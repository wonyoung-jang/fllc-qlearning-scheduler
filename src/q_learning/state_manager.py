from typing import List, Optional, Tuple
from config import Config

PRACTICE = Config.PRACTICE
TABLE = Config.TABLE
TABLE_SIDE_1 = Config.TABLE_SIDE_1
TABLE_SIDE_2 = Config.TABLE_SIDE_2

class StateManager:
    def __init__(self, schedule_data, static_states, current_schedule_length, practice_teams_available, table_teams_available, schedule):
        self.schedule_data = schedule_data
        self.static_states = static_states
        self.current_schedule_length = current_schedule_length
        self.practice_teams_available = practice_teams_available
        self.table_teams_available = table_teams_available
        self.schedule = schedule
    
    def update_available_actions(self, state) -> List[int]:
        """
        Update the available actions for the current state.
        
        """
        time_start, time_end, round_type, location_type, location_id, team_id = state
        time_slot = (time_start, time_end)

        if round_type == PRACTICE:
            potential_actions = [
                team for team in self.schedule_data.teams if team in self.practice_teams_available
            ]
        elif round_type == TABLE:
            potential_actions = [
                team for team in self.schedule_data.teams if team in self.table_teams_available
            ]

        remove_actions = []
        available_actions = []

        # 1. "Is the team already scheduled for the current round type for rounds_per_type number of times?"
        for team_id in potential_actions:
            if (
                self.schedule_data.teams[team_id].scheduled_round_types[round_type]
                >= self.schedule_data.ROUND_TYPE_PER_TEAM[round_type]
            ):
                remove_actions.append(team_id)

        # 2. "Is the current state's time slot overlapping with any time slot scheduled for the team?"
        for team_id in potential_actions:
            for existing_start, existing_end in self.schedule_data.teams[team_id].scheduled_times:
                if (time_start < existing_end) and (time_end > existing_start):
                    remove_actions.append(team_id)
                    break  # No need to check further slots for this team

        # 3. "Is the current state's table side == 2?"
        if location_id[-1] == TABLE_SIDE_2:  # Check if table side is 2
            previous_state = self.find_previous_state(state)
            # 3a. "Is the table side 1 of the previous state scheduled?"
            if previous_state is not None:
                available_actions = [team for team in potential_actions if team not in remove_actions]
                # 3b. "Is there 1 or more available actions?"
                if not available_actions:
                    # Empty list → No available actions
                    self.update_previous_state(previous_state)
                    available_actions = []
                return available_actions
            else:
                # No previous state, no need to check for table side 1 or 2
                available_actions = []
                return available_actions

        else:  # Table side is 1
            available_actions = [team for team in potential_actions if team not in remove_actions]
            return available_actions

    def find_previous_state(self, state) -> Optional[Tuple]:
        """
        Find the previous state for the current state.
        
        """
        index = self.static_states.index(state)
        prev_state = self.static_states[index - 1]
        if prev_state[5] is None:
            return None
        else:
            return prev_state

    def update_previous_state(self, prev_state) -> None:
        """
        Update the previous state for the current state.
        
        """
        (   prev_time_start,
            prev_time_end,
            prev_round_type,
            prev_location_type,
            prev_location_id,
            prev_team_id,
        ) = prev_state
        prev_time_slot = (prev_time_start, prev_time_end)
        prev_table_key = (prev_location_id[0], int(prev_location_id[1]))

        self.schedule_data.teams[prev_team_id].scheduled_round_types[prev_round_type] -= 1
        self.schedule_data.teams[prev_team_id].scheduled_times.remove(prev_time_slot)
        self.schedule_data.teams[prev_team_id].scheduled_tables.remove(prev_table_key)
        self.schedule_data.teams[prev_team_id].scheduled_time_table_pairs.remove((prev_time_slot, prev_table_key))
        self.schedule_data.tables[prev_table_key].scheduled_teams.remove(prev_team_id)
        self.schedule_data.tables[prev_table_key].scheduled_times.remove(prev_time_slot)
        
        self.schedule[self.static_states.index(prev_state)][5] = None
        self.current_schedule_length -= 1
        if prev_round_type == PRACTICE:
            self.practice_teams_available.append(prev_team_id)
        elif prev_round_type == TABLE:
            self.table_teams_available.append(prev_team_id)
    