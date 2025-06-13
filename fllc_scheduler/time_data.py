"""Module for managing time data in the FLLC Scheduler."""

from dataclasses import dataclass, field
from typing import Any

from .config import RoundType, Time
from .schedule_data import ScheduleConfig
from .utils.time_utils import (
    add_minutes_to_time,
    calculate_end_times,
    generate_start_times,
    time_to_minutes,
)


@dataclass(slots=True)
class TimeDataStartTimeCollections:
    """Data class to hold start times for different rounds in the FLLC Scheduler."""

    judging: list[str] = field(default_factory=list)
    practice: list[str] = field(default_factory=list)
    table: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TimeDataSettings:
    """Data class to hold settings for time data in the FLLC Scheduler."""

    start_time_judging_rounds: str = "08:00"
    start_time_practice_rounds: str = "09:00"
    start_time_break: str = "12:00"
    start_time_table_rounds: str = "13:30"
    stop_time_table_rounds: str = "16:21"


@dataclass(slots=True)
class TimeDataDurationsAvailable:
    """Data class to hold available durations for practice and table rounds in the FLLC Scheduler."""

    practice: int = 0
    table: int = 0


@dataclass(slots=True)
class TimeData:
    """Class to manage time data for scheduling rounds in FLLC events."""

    config: ScheduleConfig
    min_slots_required: dict[RoundType, int] = field(
        default_factory=lambda: {
            RoundType.JUDGING: 0,
            RoundType.PRACTICE: 0,
            RoundType.TABLE: 0,
        }
    )
    round_durations: dict[RoundType, int] = field(
        default_factory=lambda: {
            RoundType.JUDGING: 45,
            RoundType.PRACTICE: 0,
            RoundType.TABLE: 0,
        }
    )
    time_slots: dict[RoundType, list] = field(
        default_factory=lambda: {
            RoundType.JUDGING: [],
            RoundType.PRACTICE: [],
            RoundType.TABLE: [],
        }
    )
    setting: TimeDataSettings = field(default_factory=TimeDataSettings)
    start_times: TimeDataStartTimeCollections = field(default_factory=TimeDataStartTimeCollections)
    duration_available: TimeDataDurationsAvailable = field(default_factory=TimeDataDurationsAvailable)

    def __post_init__(self) -> None:
        """Initialize the TimeData with schedule data."""
        self.update_time_data()

    def update_time_data(self) -> None:
        """Update the time data based on the schedule data."""
        self.update_min_slots_required()
        self.update_duration_available()
        self.update_round_durations()
        self.update_start_times()
        self.update_time_slots()

    def update_min_slots_required(self) -> None:
        """
        Update the minimum slots required for each round type based on the current configuration.
        """
        n_teams = self.config.num_teams
        n_rooms = self.config.num_rooms
        n_tables_and_sides = self.config.num_tables * 2
        self.min_slots_required = {
            RoundType.JUDGING: self.calculate_min_slots_required(n_teams, n_rooms),
            RoundType.PRACTICE: self.calculate_min_slots_required(n_teams, n_tables_and_sides, RoundType.PRACTICE),
            RoundType.TABLE: self.calculate_min_slots_required(n_teams, n_tables_and_sides, RoundType.TABLE),
        }

    def update_duration_available(self) -> None:
        """
        Calculate the available duration for practice and table rounds based on the current settings.
        """
        start_break = time_to_minutes(self.setting.start_time_break)
        start_practice = time_to_minutes(self.setting.start_time_practice_rounds)
        start_table = time_to_minutes(self.setting.start_time_table_rounds)
        stop_table = time_to_minutes(self.setting.stop_time_table_rounds)
        self.duration_available.practice = start_break - start_practice
        self.duration_available.table = stop_table - start_table

    def update_round_durations(self) -> None:
        """
        Set up the round durations based on the current settings and minimum slots required.
        """
        min_practice = self.min_slots_required[RoundType.PRACTICE]
        min_table = self.min_slots_required[RoundType.TABLE]
        self.round_durations = {
            RoundType.JUDGING: 45,
            RoundType.PRACTICE: round(self.duration_available.practice / min_practice),
            RoundType.TABLE: round(self.duration_available.table / min_table),
        }

    def update_start_times(self) -> None:
        """Generate start times for each round type based on the current settings."""
        self.start_times.judging = generate_start_times(*self.get_start_time(RoundType.JUDGING))
        self.start_times.practice = generate_start_times(*self.get_start_time(RoundType.PRACTICE))
        self.start_times.table = generate_start_times(*self.get_start_time(RoundType.TABLE))

    def update_time_slots(self) -> None:
        """
        Set up the time slots for all round types based on the current settings.
        """
        start_times = self.start_times.judging
        duration = self.round_durations[RoundType.JUDGING]
        judging_end_times = list(calculate_end_times(start_times, duration))
        self.time_slots = {
            RoundType.JUDGING: judging_end_times,
            RoundType.PRACTICE: self.adjust_rounds_time_slots(RoundType.PRACTICE),
            RoundType.TABLE: self.adjust_rounds_time_slots(RoundType.TABLE),
        }

    def calculate_min_slots_required(self, num_teams: int, divisor: int, round_type: str = None) -> int:
        """
        Calculate the minimum number of time slots required for a given number of teams.

        Args:
            num_teams (int): The number of teams participating.
            divisor (int): The number of teams that can be accommodated in one time slot.
            round_type (str, optional): The type of round (e.g., RoundType.PRACTICE, RoundType.TABLE). Defaults to None.
        Returns:
            int: The minimum number of time slots required.
        """
        if round_type:
            num_teams *= self.config.round_types_per_team[round_type]

        if num_teams % divisor == 0:
            return num_teams // divisor
        return (num_teams // divisor) + 1

    def adjust_rounds_time_slots(self, round_type: RoundType) -> list[tuple[str, str]]:
        """
        Adjust the time slots for practice or table rounds to ensure they fit within the available time.

        Args:
            round_type (RoundType): The type of round to adjust (RoundType.PRACTICE or RoundType.TABLE).
        Returns:
            list: A list of tuples containing start and end times for the adjusted rounds.
        """
        start_times = []
        duration = 0
        end_time = ""
        available_duration = 0
        if round_type == RoundType.PRACTICE:
            start_time = self.setting.start_time_practice_rounds
            start_times = self.start_times.practice
            current_time = start_time
            end_time = self.setting.start_time_break
            duration = self.round_durations[RoundType.PRACTICE]
            available_duration = self.duration_available.practice

        if round_type == RoundType.TABLE:
            start_time = self.setting.start_time_table_rounds
            start_times = self.start_times.table
            current_time = start_time
            end_time = self.setting.stop_time_table_rounds
            duration = self.round_durations[RoundType.TABLE]
            available_duration = self.duration_available.table

        time_slots_round = list(calculate_end_times(start_times, duration))

        while time_slots_round[-1][-1] > end_time:
            self.min_slots_required[round_type] += 1
            duration = round(available_duration / self.min_slots_required[round_type], 0)
            start_times = [start_time]
            current_time = start_time
            for _ in range(self.min_slots_required[round_type] - 1):
                current_time = add_minutes_to_time(current_time, duration)
                start_times.append(current_time)
            time_slots_round = list(calculate_end_times(start_times, duration))
        return time_slots_round

    def get_start_time(self, round_type: RoundType) -> tuple[str, int, int]:
        """Get the start time, number of slots, and slot length for a given round type."""
        match round_type:
            case RoundType.JUDGING:
                start_time = self.setting.start_time_judging_rounds
                num_slots = self.min_slots_required[RoundType.JUDGING]
                slot_length = self.round_durations[RoundType.JUDGING]
            case RoundType.PRACTICE:
                start_time = self.setting.start_time_practice_rounds
                num_slots = self.min_slots_required[RoundType.PRACTICE]
                slot_length = self.round_durations[RoundType.PRACTICE]
            case RoundType.TABLE:
                start_time = self.setting.start_time_table_rounds
                num_slots = self.min_slots_required[RoundType.TABLE]
                slot_length = self.round_durations[RoundType.TABLE]
        return start_time, num_slots, slot_length

    def update_from_settings(self, settings: dict[str, Any]) -> None:
        """
        Update the time data from the provided settings.

        Args:
            settings (dict[str, Any]): The settings to update the time data.
        """
        self.setting.start_time_judging_rounds = settings.get(Time.JUDGING_START)
        self.setting.start_time_practice_rounds = settings.get(Time.PRACTICE_START)
        self.setting.start_time_break = settings.get(Time.PRACTICE_STOP)
        self.setting.start_time_table_rounds = settings.get(Time.TABLE_START)
        self.setting.stop_time_table_rounds = settings.get(Time.TABLE_STOP)
        self.update_time_data()
