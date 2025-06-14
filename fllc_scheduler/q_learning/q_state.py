"""Module for defining the ScheduleState dataclass used in Q-learning scheduling."""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np

from ..utils.config import RoundType
from ..data_model.schedule_data import Location, ScheduleData
from ..utils.stat_utils import average

if TYPE_CHECKING:
    from .q_data import QLearningSchedulerData


@dataclass(slots=True, unsafe_hash=True)
class ScheduleState:
    """Dataclass for representing the state of the scheduling process."""

    time_slot: tuple[str, str]
    round_type: RoundType
    location: Location
    team_id: int | None = None

    def __eq__(self, other: "ScheduleState") -> bool:
        """
        Check if two ScheduleState instances are equal.

        Args:
            other (ScheduleState): The other ScheduleState instance to compare with.
        Returns:
            bool: True if all attributes are equal, False otherwise.
        """
        return (
            self.time_slot == other.time_slot
            and self.round_type == other.round_type
            and self.location == other.location
        )


@dataclass(slots=True)
class QLearningStates:
    """Dataclass for Q-Learning states."""

    states: list[ScheduleState] = field(default_factory=list)
    static: list[ScheduleState] = field(default_factory=list)
    schedule: list[ScheduleState] = field(default_factory=list)
    practice_teams_available: list[int] = field(default_factory=list)
    table_teams_available: list[int] = field(default_factory=list)
    current_schedule_length: int = 0
    q_table: dict[tuple[ScheduleState, int], float] = field(default_factory=dict)

    def is_terminal(self) -> bool:
        """
        Check if the scheduling is complete.

        Returns
            bool: True if all teams have been scheduled for all rounds, False otherwise.
        """
        if not (self.practice_teams_available or self.table_teams_available):
            return True
        return False

    def find_previous(self, state: ScheduleState) -> ScheduleState | None:
        """
        Find the previous state in the static states list.

        Args:
            state (ScheduleState): The current state represented as a tuple.
        Returns:
            ScheduleState | None: The previous state if found, otherwise None.
        """
        prev_index = self.static.index(state) - 1
        prev_state = self.static[prev_index]
        if prev_state.team_id is None:
            return None
        return prev_state

    def update_schedule(self, state: ScheduleState, team_id: int) -> None:
        """
        Update the schedule with the selected action for the current state.

        Args:
            current_state (ScheduleState): The current state represented as a ScheduleState object.
            selected_action (Any): The action selected for the current state.
        """
        self.remove_availability(state.round_type, team_id)
        for sched_state in self.schedule:
            if state == sched_state and state.team_id is None:
                state.team_id = team_id
                break
        curr_index = self.static.index(state)
        self.static[curr_index].team_id = team_id
        self.current_schedule_length += 1

    def to_heatmap(self) -> tuple[np.ndarray, list[str], list[str]]:
        """
        Transform the Q-table for heatmap display.

        Returns:
            tuple: A tuple containing:
                - A 2D numpy array representing the heatmap data.
                - A list of action labels for the columns.
                - A list of detailed state labels for the rows.
        """
        data = defaultdict(list)
        for (state, action), value in self.q_table.items():
            start_time, round_type = state.time_slot[0], state.round_type
            detailed_state = (start_time, round_type)
            data[(detailed_state, action)].append(value)
        aggregated_data = {k: average(values) for k, values in data.items()}
        detailed_states = sorted(set(k[0] for k in aggregated_data), key=lambda x: (x[1], x[0]))
        actions = sorted(set(k[1] for k in aggregated_data))
        heatmap_data = np.zeros((len(detailed_states), len(actions)))
        for (detailed_state, action), value in aggregated_data.items():
            row = detailed_states.index(detailed_state)
            col = actions.index(action)
            heatmap_data[row, col] = value
        state_labels = [f"{state[0]} {state[1][0].capitalize()}" for state in detailed_states]
        return heatmap_data, actions, state_labels

    def add_availability(self, round_type: RoundType, team_id: int) -> None:
        """
        Update the availability of teams based on the current round type and team ID.

        Args:
            round_type (RoundType): The type of round (Practice or Table).
            team_id (int): The ID of the team to update.
        """
        add_team = {
            RoundType.PRACTICE: self.practice_teams_available.append,
            RoundType.TABLE: self.table_teams_available.append,
        }.get(round_type, None)
        if add_team is not None:
            add_team(team_id)

    def remove_availability(self, round_type: RoundType, team_id: int) -> None:
        """
        Remove the availability of teams based on the current round type and team ID.

        Args:
            round_type (RoundType): The type of round (Practice or Table).
            team_id (int): The ID of the team to update.
        """
        remove_team = {
            RoundType.PRACTICE: self.practice_teams_available.remove,
            RoundType.TABLE: self.table_teams_available.remove,
        }.get(round_type, None)
        if remove_team is not None:
            remove_team(team_id)

    def update_previous_state(self, prev: ScheduleState) -> None:
        """
        Update the previous state by removing the scheduled team, time slot, and table from the schedule.

        Args:
            prev_state (ScheduleState): The previous state represented as a ScheduleState object.
        """
        prev_index = self.static.index(prev)
        self.schedule[prev_index].team_id = None
        self.current_schedule_length -= 1
        self.add_availability(prev.round_type, prev.team_id)

    def initialize_schedule_and_states(self, data: "QLearningSchedulerData") -> None:
        """
        Initialize the schedule and states based on the provided data.

        Args:
            data (QLearningSchedulerData): The data object containing schedule and time information.
        """
        self.schedule = data.initialize_schedule()
        self.static = self.schedule.copy()
        self.initialize_judging_rounds(data.schedule)
        self.states = [s for s in self.schedule if s.team_id is None]
        self.practice_teams_available = data.get_practice_teams_available()
        self.table_teams_available = data.get_table_teams_available()

    def initialize_judging_rounds(self, schedule_data: ScheduleData) -> None:
        """
        Initialize the judging rounds in the schedule by assigning teams to rounds.

        Args:
            schedule_data (ScheduleData): The schedule data containing team information.
        """
        team_keys = list(schedule_data.teams.keys())
        book = schedule_data.book_team_for_slot
        judging_schedule_only = (s for s in self.schedule if s.round_type == RoundType.JUDGING)
        for i, state in enumerate(judging_schedule_only, 1):
            if i <= len(team_keys):
                state.team_id = i
                book(i, RoundType.JUDGING, state.time_slot, state.location)

    def update_available_actions(self, state: ScheduleState, data: "QLearningSchedulerData") -> list:
        """
        Update the available actions based on the current state and hard constraints.

        Args:
            state (ScheduleState): The current state of the scheduling process.
            data (QLearningSchedulerData): The data object containing schedule and time information.
        Returns:
            list: A list of available actions (teams) for the current state.
        """
        available_potentials = {
            RoundType.PRACTICE: self.practice_teams_available,
            RoundType.TABLE: self.table_teams_available,
        }.get(state.round_type, [])

        potential_actions = [team for team in data.schedule.teams if team in available_potentials]
        remove_actions = list(
            data.check_is_team_scheduled_or_overlapping(potential_actions, state.round_type, state.time_slot)
        )
        available_actions = [team for team in potential_actions if team not in remove_actions]
        if state.location.side == 2:
            if previous_state := self.find_previous(state):
                if not available_actions:
                    self.update_previous_state(previous_state)
                return available_actions
            return []
        return available_actions

    def get_best_action(self, actions: list[int], s: ScheduleState) -> int | None:
        """
        Get a possible action from the list of actions based on the current state.

        Args:
            actions (list[int]): The list of available actions (team IDs).
            s (ScheduleState): The current state of the scheduling process.
        Returns:
            int | None: A possible action (team ID) or None if no action is available.
        """
        best_actions = {}
        for a in actions:
            state_action = (s, a)
            value = self.q_table.get(state_action, float("-inf"))
            best_actions[a] = value
        best_action = max(best_actions, key=best_actions.get, default=None)
        return best_action
