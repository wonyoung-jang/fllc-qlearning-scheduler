"""Dataclass for Q-Learning data used in FLLC scheduling."""

from dataclasses import dataclass
from typing import Any, Generator

from ..config import LocationType, RoundType
from ..schedule_data import Location, ScheduleConfig, ScheduleData
from ..time_data import TimeData
from .q_state import ScheduleState


@dataclass(slots=True)
class QLearningSchedulerData:
    """Dataclass for Q-Learning data."""

    config: ScheduleConfig
    schedule: ScheduleData
    time: TimeData

    def initialize_schedule(self) -> list:
        """
        Initialize the schedule with time slots for judging, practice, and table rounds.

        Returns:
            list: A list of schedule entries, each containing start time, end time, round type, location type,
                  location ID, and team ID (initially None).
        """
        self.schedule.initialize()
        schedule = []
        for round_type, slots in self.time.time_slots.items():
            for time_slot in slots:
                if round_type == RoundType.JUDGING:
                    for room_id in range(1, self.config.num_rooms + 1):
                        state = ScheduleState(
                            time_slot=time_slot,
                            round_type=round_type,
                            location=Location(
                                location_type=LocationType.ROOM,
                                location_id=str(room_id),
                            ),
                        )
                        schedule.append(state)
                elif round_type in (RoundType.PRACTICE, RoundType.TABLE):
                    for table_id in (chr(65 + i) for i in range(self.config.num_tables)):
                        for side in (1, 2):
                            state = ScheduleState(
                                time_slot=time_slot,
                                round_type=round_type,
                                location=Location(
                                    location_type=LocationType.TABLE,
                                    location_id=table_id,
                                    side=side,
                                ),
                            )
                            schedule.append(state)
        return schedule

    def get_possible_schedule_slots(self) -> int:
        """
        Get the number of possible schedule slots.

        Returns:
            int: The number of possible schedule slots.
        """
        sched_config = self.config
        timeslots = self.time.min_slots_required
        possible_judging = sched_config.num_rooms * timeslots[RoundType.JUDGING]
        timeslots_practice_and_table = timeslots[RoundType.PRACTICE] + timeslots[RoundType.TABLE]
        possible_practice_and_table = (sched_config.num_tables * 2) * timeslots_practice_and_table
        return possible_judging + possible_practice_and_table

    def get_practice_teams_available(self) -> list:
        """
        Get the list of available practice teams.

        Returns:
            list: A list of team IDs available for practice rounds.
        """
        return list(self.schedule.teams.keys()) * self.config.round_types_per_team[RoundType.PRACTICE]

    def get_table_teams_available(self) -> list:
        """
        Get the list of available table teams.

        Returns:
            list: A list of team IDs available for table rounds.
        """
        return list(self.schedule.teams.keys()) * self.config.round_types_per_team[RoundType.TABLE]

    def check_is_team_scheduled(self, potential_actions: list, round_type: str) -> Generator[Any, None, None]:
        """
        Check if any team in the potential actions is already scheduled.

        Args:
            potential_actions (list): List of potential actions (teams).
            round_type (str): The type of round being checked (e.g., RoundType.PRACTICE, RoundType.TABLE).
        Yields:
            Any: Team ID if it is already scheduled for the current round type.
        """
        for team_id in potential_actions:
            if self.schedule.is_team_scheduled(team_id, round_type):
                yield team_id

    def check_is_time_slot_overlapping(self, potential_actions: list, time_slot: tuple) -> Generator[Any, None, None]:
        """
        Check if the time slot overlaps with any scheduled times for the teams.

        Args:
            potential_actions (list): List of potential actions (teams).
            time_slot (tuple): The time slot to check (start_time, end_time).
        Yields:
            Any: Team ID if the time slot overlaps with any scheduled times.
        """
        for team_id in potential_actions:
            if not (team := self.schedule.get_team(team_id)):
                continue
            if team.has_time_conflict(time_slot):
                yield team_id
