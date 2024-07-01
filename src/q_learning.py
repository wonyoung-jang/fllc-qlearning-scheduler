import os
import random
from typing import List, Tuple, Dict, Optional, Any, Set
import logging
from datetime import datetime
from data_to_csv import QLearningExporter
from collections import defaultdict

from config import (
    KeysConfig,
    ValuesConfig,
    FormatsConfig,
    ExportConfig,
    TournamentDataDefaultConfig,
    QLearningDefaultConfig,
    SoftConstraintDefaultConfig,
)

from tournament_data import *
from utilities_time import *
from utilities_qlearning import *

KEY = KeysConfig()
VALUE = ValuesConfig()
TOURNAMENT = TournamentDataDefaultConfig()
FORMAT = FormatsConfig()
EXPORT = ExportConfig()
QLEARNING = QLearningDefaultConfig()
SOFT_CONSTRAINT = SoftConstraintDefaultConfig()

LOG_FILE = EXPORT.LOGGING_DIRECTORY + EXPORT.LOGGING_FILE_NAME + EXPORT.TXT_EXT

if not os.path.exists(EXPORT.LOGGING_DIRECTORY):
    try:
        os.makedirs(EXPORT.LOGGING_DIRECTORY)
    except OSError as e:
        print(f"Failed to create directory {EXPORT.LOGGING_DIRECTORY}. Reason: {e}")

with open(LOG_FILE, "w", encoding="utf-8") as file:
    file.write(f"Log file created at {datetime.now()}\n")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format=FORMAT.LOGGING_FORMAT)





# OBJECT
class QLearning:
    """
    Q-Learning algorithm for scheduling.

    """

    def __init__(self, tournament_data, time_data):  
        """
        Initialize the Q-Learning algorithm for scheduling.

        """
        self.learning_rate = QLEARNING.LEARNING_RATE
        self.discount_factor = QLEARNING.DISCOUNT_FACTOR
        self.epsilon_start = QLEARNING.EPSILON_START
        self.epsilon_end = QLEARNING.EPSILON_END
        self.epsilon_decay = QLEARNING.EPSILON_DECAY
        self.epsilon = self.epsilon_start
        self.training_episodes = QLEARNING.TRAINING_EPISODES

        self.q_table: Dict[Tuple[Tuple, Any], float] = {}

        self.soft_constraints_weight = SOFT_CONSTRAINT.SOFT_CONSTRAINTS_WEIGHT

        self.tournament_data = tournament_data
        self.num_teams = TOURNAMENT.NUM_TEAMS
        self.num_rooms = TOURNAMENT.NUM_ROOMS
        self.num_tables = TOURNAMENT.NUM_TABLES
        self.round_types_per_team = TOURNAMENT.ROUND_TYPES_PER_TEAM
        self.num_tables_and_sides = self.num_tables * 2
        self.teams = init_teams(self.num_teams)
        self.rooms = init_rooms(self.num_rooms)
        self.tables = init_tables(self.num_tables)
        self.color_map = init_color_map(self.teams, self.num_teams)

        self.time_data = time_data

        self.required_schedule_slots = self.tournament_data.num_teams * sum(
            self.tournament_data.round_types_per_team.values()
        )

        self.possible_schedule_slots = (
            self.tournament_data.num_rooms
            * self.time_data.minimum_slots_required[KEY.JUDGING]
            + self.tournament_data.num_tables_and_sides
            * (
                self.time_data.minimum_slots_required[KEY.PRACTICE]
                + self.time_data.minimum_slots_required[KEY.TABLE]
            )
        )

        self.initialize_schedule_and_states()
        self.completion_percentage = defaultdict(list)
        self.scores = defaultdict(list)

        self.q_table_size_limit = len(self.states) * len(self.teams)
        self.max_num_rounds_per_team = sum(
            self.tournament_data.round_types_per_team.values()
        )

        self.exporter = QLearningExporter()

    def initialize_schedule_and_states(self) -> None:  
        """
        Initialize the schedule and states for training.

        """
        self.schedule = self.initialize_schedule()
        self.staticStates = [tuple(i) for i in self.schedule]

        self.initialize_judging_rounds()
        self.states = [tuple(i) for i in self.schedule if i[5] is None]

        self.practice_teams_available = (
            list(self.teams.keys())
            * self.tournament_data.round_types_per_team[KEY.PRACTICE]
        )
        self.table_teams_available = (
            list(self.teams.keys())
            * self.tournament_data.round_types_per_team[KEY.TABLE]
        )
        self.current_schedule_length = 0

    # TODO PURE
    def initialize_schedule(self) -> List[List]:  
        """
        Initialize the schedule for training.

        """
        self.num_teams = TOURNAMENT.NUM_TEAMS
        self.num_rooms = TOURNAMENT.NUM_ROOMS
        self.num_tables = TOURNAMENT.NUM_TABLES
        self.round_types_per_team = TOURNAMENT.ROUND_TYPES_PER_TEAM
        self.num_tables_and_sides = self.num_tables * 2
        self.teams = init_teams(self.num_teams)
        self.rooms = init_rooms(self.num_rooms)
        self.tables = init_tables(self.num_tables)
        self.color_map = init_color_map(self.teams, self.num_teams)

        schedule = []
        for round_type, slots in self.time_data.round_type_time_slots.items():
            for time_start, time_end in slots:
                if round_type == KEY.JUDGING:
                    for room_id in range(1, self.tournament_data.num_rooms + 1):
                        schedule.append(
                            [
                                time_start,
                                time_end,
                                round_type,
                                VALUE.LOCATION_TYPE_ROOM,
                                room_id,
                                None,
                            ]
                        )
                else:
                    for table, details in self.tables.items():
                        table_id, side = table
                        schedule.append(
                            [
                                time_start,
                                time_end,
                                round_type,
                                KEY.TABLE,
                                f"{table_id}{side}",
                                None,
                            ]
                        )
        return schedule

    # TODO PURE
    def initialize_judging_rounds(self) -> List[List]:  
        """
        Initialize the judging rounds for training.

        """
        current_team_id = list(self.teams.keys())[0]

        for i, schedule in enumerate(self.schedule):
            if schedule[2] == KEY.JUDGING and current_team_id <= len(
                list(self.teams.keys())
            ):
                self.schedule[i][5] = current_team_id
                self.teams[current_team_id][KEY.SCHEDULED_ROUND_TYPES][KEY.JUDGING] += 1
                self.teams[current_team_id][KEY.SCHEDULED_TIMES].append(
                    (schedule[0], schedule[1])
                )
                self.rooms[schedule[4]][KEY.SCHEDULED_TEAMS].append(current_team_id)
                current_team_id += 1

        return self.schedule

    # Scheduling, Training, Optimizing
    def train_one_episode(self, episode) -> None:
        """
        Train the Q-Learning algorithm for one episode.

        """
        logging.info(f"Starting training episode {episode}")

        self.initialize_schedule_and_states()
        self.current_schedule_length = 0

        actions = tuple(self.teams.keys())
        episode_reward = 0

        while self.states:
            current_state = self.states[0]

            logging.debug(f"Current state: {current_state}")

            current_start_time = current_state[0]
            current_end_time = current_state[1]
            current_round_type = current_state[2]
            current_location_type = current_state[3]
            current_location_id = current_state[4]
            current_location_letter = current_location_id[0]
            current_location_side = current_location_id[1]

            if is_terminal_state(
                self.practice_teams_available, self.table_teams_available
            ):
                break

            actions = self.update_available_actions(current_state)
            if actions:
                selected_action = select_action(
                    current_state, actions, self.q_table, self.epsilon
                )  # Select an action using the epsilon-greedy policy
                if selected_action is not None:
                    self.update_team_availability(
                        selected_action,
                        current_round_type,
                        (current_start_time, current_end_time),
                        current_location_letter,
                        current_location_side,
                    )
                    self.update_table_availability(
                        current_location_id,
                        selected_action,
                        (current_start_time, current_end_time),
                    )
                    self.update_schedule(current_state, selected_action)
                    reward = self.get_reward(current_state, selected_action)
                    episode_reward += reward

                    self.states.remove(current_state)
                    self.staticStates[self.staticStates.index(current_state)] = (
                        current_start_time,
                        current_end_time,
                        current_round_type,
                        current_location_type,
                        current_location_id,
                        selected_action,
                    )

                    next_state = self.states[0] if self.states else None

                    if next_state is not None:
                        self.update_q_value(
                            current_state, selected_action, reward, next_state, actions
                        )
                    else:
                        self.q_table[(current_state, selected_action)] = (
                            1 - self.learning_rate
                        ) * self.q_table.get(
                            (current_state, selected_action), 0
                        ) + self.learning_rate * reward
                else:
                    self.states.remove(
                        current_state
                    )  # Optionally, remove the state and continue
            else:
                self.states.remove(current_state)

            if not self.states:
                break

        logging.info(f"Finished training episode {episode}")

        self.epsilon = max(
            self.epsilon_end, self.epsilon_decay * self.epsilon
        )  # Decays each episode

        # Export the schedule for evaluation
        scheduleCSVFileName = f"{EXPORT.EXPORTS_DIRECTORY}{EXPORT.TRAINING_SCHEDULES_DIRECTORY}{EXPORT.TRAINING_SCHEDULE_CSV_FILENAME}{episode}{EXPORT.CSV_EXT}"
        self.exporter.export_schedule_to_csv(scheduleCSVFileName, self.schedule)

    def generate_optimal_schedule(self) -> None:
        """
        Generate the optimal schedule using the Q-Learning algorithm.

        """
        self.initialize_schedule_and_states()
        self.current_schedule_length = 0

        while self.states:
            current_state = self.states[0]
            available_actions = self.update_available_actions(current_state)

            if available_actions:
                best_action = max(
                    available_actions,
                    key=lambda action: self.q_table.get(
                        (current_state, action), float("-inf")
                    ),
                )
                if best_action:
                    self.update_team_availability(
                        best_action,
                        current_state[2],
                        (current_state[0], current_state[1]),
                        current_state[4][0],
                        current_state[4][1],
                    )
                    self.update_table_availability(
                        current_state[4],
                        best_action,
                        (current_state[0], current_state[1]),
                    )
                    self.update_schedule(current_state, best_action)

                    self.staticStates[self.staticStates.index(current_state)] = (
                        current_state[0],
                        current_state[1],
                        current_state[2],
                        current_state[3],
                        current_state[4],
                        best_action,
                    )

            self.states.remove(current_state)
        q_table_filename = (
            EXPORT.EXPORTS_DIRECTORY + EXPORT.Q_TABLE_CSV_FILENAME + EXPORT.CSV_EXT
        )
        self.exporter.export_q_table_to_csv(q_table_filename, self.q_table)
        optimal_filename = (
            EXPORT.EXPORTS_DIRECTORY
            + EXPORT.OPTIMAL_SCHEDULE_CSV_FILENAME
            + EXPORT.CSV_EXT
        )
        self.exporter.export_optimal_schedule_to_excel(optimal_filename, self.schedule)

    # Updaters
    # TODO PURE
    def update_team_availability(  
        self, team_id, round_type, time_slot, location_id, side
    ) -> None:
        """
        Update the team availability for the current state.

        """
        if team_id in self.teams:
            team_info = self.teams[team_id]

            team_info[KEY.SCHEDULED_ROUND_TYPES][round_type] += 1
            team_info[KEY.SCHEDULED_TIMES].append(time_slot)
            team_info[KEY.SCHEDULED_TABLES].append((location_id, int(side)))
            team_info[KEY.SCHEDULED_TIME_TABLE_PAIRS].append(
                (time_slot, (location_id, int(side)))
            )

            if round_type == KEY.PRACTICE:
                self.practice_teams_available.remove(team_id)
            elif round_type == KEY.TABLE:
                self.table_teams_available.remove(team_id)

            # Table side and opponent logic
            table_id = location_id[0]

            if (
                side == TOURNAMENT.TABLE_SIDE_2
            ):  # Assuming side 2 indicates both are scheduled
                other_side = TOURNAMENT.TABLE_SIDE_1
                # Find the team assigned to the other side, if any
                for other_team_id, other_team_info in self.teams.items():
                    if (
                        other_team_id != team_id
                        and (time_slot, (table_id, other_side))
                        in other_team_info[KEY.SCHEDULED_TIME_TABLE_PAIRS]
                    ):
                        # Update opponents for both teams
                        other_team_info[KEY.SCHEDULED_OPPONENTS].append(team_id)
                        team_info[KEY.SCHEDULED_OPPONENTS].append(other_team_id)

                        break  # Found the other team, no need to continue the loop
        else:
            print(f"Team {team_id} does not exist.")

    # TODO PURE
    def update_table_availability(
        self, location_id, team_id, time_slot
    ) -> None:  
        """
        Update the table availability for the current state.

        """
        table_id = location_id[0]  # Extract table ID (e.g., 'A1' from 'A11')
        side = int(location_id[-1])  # Extract side (e.g., 1 from 'A11')

        if (table_id, side) in self.tables:
            self.tables[(table_id, side)][KEY.SCHEDULED_TEAMS].append(team_id)
            self.tables[(table_id, side)][KEY.SCHEDULED_TIMES].append(time_slot)
        else:
            print(f"Table {table_id} side {side} does not exist.")

    # TODO PURE
    def update_schedule(self, current_state, selected_action) -> None:  
        """
        Update the schedule for the current state.

        """
        for i, schedule_row in enumerate(self.schedule):
            sched_row = tuple(schedule_row[:5])
            if sched_row == current_state[:5] and schedule_row[5] is None:
                self.schedule[i][5] = selected_action
                break
        self.current_schedule_length += 1

    # TODO PURE
    def update_q_value(
        self, state, action, reward, next_state, actions
    ) -> None:  
        """
        Update the Q-value for the current state-action pair.

        """
        current_q = self.q_table.get((state, action), 0)

        if not actions:
            max_future_q = 0
        else:
            max_future_q = max(self.q_table.get((next_state, a), 0) for a in actions)

        new_q = (1 - self.learning_rate) * current_q + self.learning_rate * (
            reward + self.discount_factor * max_future_q
        )
        self.q_table[(state, action)] = new_q

    # State and Actions
    # TODO PURE
    def update_available_actions(self, state) -> List[int]:  
        """
        Update the available actions for the current state.

        """
        time_start, time_end, round_type, location_type, location_id, team_id = state
        time_slot = (time_start, time_end)

        if round_type == KEY.PRACTICE:
            potential_actions = [
                team for team in self.teams if team in self.practice_teams_available
            ]
        elif round_type == KEY.TABLE:
            potential_actions = [
                team for team in self.teams if team in self.table_teams_available
            ]

        remove_actions = []
        available_actions = []

        # 1. "Is the team already scheduled for the current round type for rounds_per_type number of times?"
        for team_id in potential_actions:
            if (
                self.teams[team_id][KEY.SCHEDULED_ROUND_TYPES][round_type]
                >= self.tournament_data.round_types_per_team[round_type]
            ):
                remove_actions.append(team_id)

        # 2. "Is the current state's time slot overlapping with any time slot scheduled for the team?"
        for team_id in potential_actions:
            for existing_start, existing_end in self.teams[team_id][
                KEY.SCHEDULED_TIMES
            ]:
                if (time_start < existing_end) and (time_end > existing_start):
                    remove_actions.append(team_id)
                    break  # No need to check further slots for this team

        # 3. "Is the current state's table side == 2?"
        if location_id[-1] == TOURNAMENT.TABLE_SIDE_2:  # Check if table side is 2
            previous_state = self.find_previous_state(state)
            # 3a. "Is the table side 1 of the previous state scheduled?"
            if previous_state is not None:
                available_actions = [
                    team for team in potential_actions if team not in remove_actions
                ]
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
            available_actions = [
                team for team in potential_actions if team not in remove_actions
            ]
            return available_actions

    # TODO PURE
    def find_previous_state(self, state) -> Optional[Tuple]:  
        """
        Find the previous state for the current state.

        """
        index = self.staticStates.index(state)
        prev_state = self.staticStates[index - 1]
        if prev_state[5] is None:
            return None
        else:
            return prev_state

    # TODO PURE
    def update_previous_state(self, prev_state) -> None:  
        """
        Update the previous state for the current state.

        """
        (
            prev_time_start,
            prev_time_end,
            prev_round_type,
            prev_location_type,
            prev_location_id,
            prev_team_id,
        ) = prev_state
        prev_time_slot = (prev_time_start, prev_time_end)
        prev_table_key = (prev_location_id[0], int(prev_location_id[1]))
        self.teams[prev_team_id][KEY.SCHEDULED_ROUND_TYPES][prev_round_type] -= 1
        self.teams[prev_team_id][KEY.SCHEDULED_TIMES].remove(prev_time_slot)
        self.teams[prev_team_id][KEY.SCHEDULED_TABLES].remove(prev_table_key)
        self.teams[prev_team_id][KEY.SCHEDULED_TIME_TABLE_PAIRS].remove(
            (prev_time_slot, prev_table_key)
        )
        self.tables[prev_table_key][KEY.SCHEDULED_TEAMS].remove(prev_team_id)
        self.tables[prev_table_key][KEY.SCHEDULED_TIMES].remove(prev_time_slot)
        self.schedule[self.staticStates.index(prev_state)][5] = None
        self.current_schedule_length -= 1
        if prev_round_type == KEY.PRACTICE:
            self.practice_teams_available.append(prev_team_id)
        elif prev_round_type == KEY.TABLE:
            self.table_teams_available.append(prev_team_id)

    # Reward Calculations
    def get_reward(self, state, action) -> float:  
        """
        Get the reward for the current state-action pair.

        """
        time_start, time_end, round_type, location_type, location_id, team_id = state
        (
            team_id,
            scheduled_round_types,
            scheduled_times,
            scheduled_tables,
            scheduled_opponents,
            scheduled_time_table_pairs,
        ) = self.teams[action].values()

        table_key = (location_id[0], int(location_id[1]))

        start_time_minutes = time_to_minutes(time_start)
        end_time_minutes = time_to_minutes(time_end)

        reward = 0

        # Calculate table consistency reward
        reward += self.calculate_table_consistency_reward(scheduled_tables)

        # Calculate opponent variety reward
        reward += self.calculate_opponent_variety_reward(scheduled_opponents)

        # Calculate back-to-back penalty
        reward += self.calculate_back_to_back_penalty(
            scheduled_times, start_time_minutes, end_time_minutes
        )

        # Calculate break time reward
        reward += self.calculate_break_time_reward(
            scheduled_times, start_time_minutes, end_time_minutes
        )

        # Apply completion reward multiplier
        completion_reward = self.current_schedule_length / (
            self.required_schedule_slots
            - (
                self.tournament_data.num_teams
                * self.tournament_data.round_types_per_team[KEY.JUDGING]
            )
        )
        reward += reward * completion_reward

        return reward

    # TODO PURE
    def calculate_table_consistency_reward(
        self, scheduled_tables
    ) -> float:  
        """
        Calculate the table consistency reward.

        """
        reward = 0
        length_of_tables_scheduled = len(scheduled_tables)
        if length_of_tables_scheduled > 1:
            unique_to_tables = len(set(scheduled_tables)) / len(scheduled_tables)
            reward_table = (
                unique_to_tables / self.max_num_rounds_per_team
            )  # Original reward calculation
            # Normalize this reward
            min_reward_table = 0
            max_reward_table = 1
            reward_table_normalized = normalize_reward(
                reward_table, min_reward_table, max_reward_table
            )
            reward += (
                reward_table_normalized
                * self.soft_constraints_weight[KEY.TABLE_CONSISTENCY]
            )
        return reward

    # TODO PURE
    def calculate_opponent_variety_reward(
        self, scheduled_opponents
    ) -> float:  
        """
        Calculate the opponent variety reward.

        """
        reward = 0
        length_of_opponents_scheduled = len(scheduled_opponents)
        if length_of_opponents_scheduled > 1:
            unique = []
            for opponent in scheduled_opponents:
                if opponent not in unique:
                    unique.append(opponent)
            length_of_unique_opponents = len(unique)
            unique_to_opponents = (
                length_of_unique_opponents / length_of_opponents_scheduled
            )
            reward_opponent = (
                unique_to_opponents
                * self.max_num_rounds_per_team
                * self.soft_constraints_weight[KEY.OPPONENT_VARIETY]
            )
            min_reward_opponent = 0
            max_reward_opponent = 1
            reward_opponent_normalized = normalize_reward(
                reward_opponent, min_reward_opponent, max_reward_opponent
            )
            reward += reward_opponent_normalized
        return reward

    # TODO PURE
    def calculate_back_to_back_penalty(  
        self, scheduled_times, start_time_minutes, end_time_minutes
    ) -> float:
        """
        Calculate the back-to-back penalty.

        """
        reward = 0
        for i in range(len(scheduled_times)):
            time_action_start = time_to_minutes(scheduled_times[i][0])
            time_action_end = time_to_minutes(scheduled_times[i][1])
            reward_back_to_back = 0
            if (
                time_action_start - end_time_minutes <= 0
                or time_action_end - start_time_minutes <= 0
            ):
                reward_back_to_back -= 1
            else:
                reward_back_to_back += 1

            if (
                start_time_minutes - time_action_end <= 0
                or end_time_minutes - time_action_start <= 0
            ):
                reward_back_to_back -= 1
            else:
                reward_back_to_back += 1

            min_reward_back_to_back = -1  # Define based on expected range
            max_reward_back_to_back = 1
            reward_back_to_back_normalized = normalize_reward(
                reward_back_to_back, min_reward_back_to_back, max_reward_back_to_back
            )
            reward += (
                reward_back_to_back_normalized
                * self.soft_constraints_weight[KEY.BACK_TO_BACK_PENALTY]
            )
        return reward

    # TODO PURE
    def calculate_break_time_reward(  
        self, scheduled_times, start_time_minutes, end_time_minutes
    ) -> float:
        """
        Calculate the break time reward.

        """
        reward = 0
        break_time = 30
        for i in range(1, len(scheduled_times)):
            time_action_start = time_to_minutes(scheduled_times[i][0])
            time_action_end = time_to_minutes(scheduled_times[i][1])
            reward_break_time = 0
            if (
                time_action_start - end_time_minutes >= break_time
                or time_action_end - start_time_minutes >= break_time
            ):
                reward_break_time += 1
            else:
                reward_break_time -= 1

            if (
                start_time_minutes - time_action_end >= break_time
                or end_time_minutes - time_action_start >= break_time
            ):
                reward_break_time += 1
            else:
                reward_break_time -= 1

            min_reward_break_time = -1  # Define based on expected range
            max_reward_break_time = 1
            reward_break_time_normalized = normalize_reward(
                reward_break_time, min_reward_break_time, max_reward_break_time
            )
            reward += (
                reward_break_time_normalized
                * self.soft_constraints_weight[KEY.BREAK_TIME]
            )
        return reward
