"""This module contains the QLearning class, which is responsible for the Q-Learning algorithm for scheduling."""
import random
import logging
import pickle
import numpy as np
from datetime import datetime
from typing import List, Tuple, Dict, Optional, Any
from PySide6.QtCore import QObject, Signal
from schedule_evaluator import ScheduleEvaluator
from data_to_csv import QLearningExporter
from collections import defaultdict
from time_data.time_utilities import TimeUtilities

logging.basicConfig(filename='FLLC-Q_Log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class QLearning:
    """Q-Learning algorithm for scheduling."""

    def __init__(self, schedule_data, time_data):
        """Initialize the Q-Learning algorithm for scheduling."""
        self.learning_rate = 0.20  # Alpha
        self.discount_factor = 0.80  # Gamma
        self.epsilon_start = 1.00
        self.epsilon_end = 0.01
        self.epsilon_decay = 0.995
        self.epsilon = self.epsilon_start
        self.training_episodes = 5

        self.gui_refresh_interval = 1

        self.q_table: Dict[Tuple[Tuple, Any], float] = {}
        self.episode_rewards: List[float] = []
        self.num_exploration_counts: List[int] = []
        self.num_exploitation_counts: List[int] = []
        self.q_value_changes: List[float] = []
        self.average_rewards: List[float] = []
        self.average_reward_changes: List[float] = []

        self.soft_constraints_weight = {
            "Table Consistency": 1.0,
            "Opponent Variety": 1.0,
            "Back to Back Penalty": 1.0,
            "Break Time": 1.0,
        }

        self.schedule_data = schedule_data
        self.time_data = time_data

        self.required_schedule_slots = self.schedule_data.num_teams * sum(
            self.schedule_data.round_types_per_team.values()
        )

        self.possible_schedule_slots = self.schedule_data.num_rooms * self.time_data.minimum_slots_required[
            "judging"
        ] + self.schedule_data.num_tables_and_sides * (
            self.time_data.minimum_slots_required["practice"] + self.time_data.minimum_slots_required["table"]
        )

        self.initialize_schedule_and_states()
        self.completion_percentage = defaultdict(list)
        self.scores = defaultdict(list)

        self.q_table_size_limit = len(self.states) * len(self.schedule_data.teams)
        self.max_num_rounds_per_team = sum(self.schedule_data.round_types_per_team.values())

        self.exporter = QLearningExporter()

    def save_model(self, filename: str) -> None:  # TODO
        """Save the trained model to a file."""
        with open(filename, 'wb') as file:
            pickle.dump(self.q_table, file)

    def load_model(self, filename: str) -> None:  # TODO
        """Load the trained model from a file."""
        with open(filename, 'rb') as file:
            self.q_table = pickle.load(file)

    def initialize_schedule_and_states(self) -> None:
        """Initialize the schedule and states for training."""
        self.schedule = self.initialize_schedule()
        self.staticStates = [tuple(i) for i in self.schedule]

        self.initialize_judging_rounds()
        self.states = [tuple(i) for i in self.schedule if i[2] != 'judging']
        self.exploration_count = 0
        self.exploitation_count = 0
        self.practice_teams_available = (
            list(self.schedule_data.teams.keys()) * self.schedule_data.round_types_per_team["practice"]
        )
        self.table_teams_available = (
            list(self.schedule_data.teams.keys()) * self.schedule_data.round_types_per_team["table"]
        )
        self.current_schedule_length = 0

    def initialize_schedule(self) -> List[List]:
        """Initialize the schedule for training."""
        (
            self.schedule_data.teams,
            self.schedule_data.rooms,
            self.schedule_data.tables,
        ) = self.schedule_data.initialize_teams_rooms_tables()
        schedule = []
        for round_type, slots in self.time_data.round_type_time_slots.items():
            for time_start, time_end in slots:
                if round_type == "judging":
                    for room_id in range(1, self.schedule_data.num_rooms + 1):
                        schedule.append([time_start, time_end, round_type, "room", room_id, None])
                else:
                    for table, details in self.schedule_data.tables.items():
                        table_id, side = table
                        schedule.append(
                            [
                                time_start,
                                time_end,
                                round_type,
                                "table",
                                f"{table_id}{side}",
                                None,
                            ]
                        )
        return schedule

    def initialize_judging_rounds(self) -> None:
        """Initialize the judging rounds for training."""
        current_team_id = list(self.schedule_data.teams.keys())[0]

        for i, schedule in enumerate(self.schedule):
            if schedule[2] == "judging" and current_team_id <= len(list(self.schedule_data.teams.keys())):
                self.schedule[i][5] = current_team_id
                self.schedule_data.teams[current_team_id].scheduled_round_types["judging"] += 1
                self.schedule_data.teams[current_team_id].scheduled_times.append((schedule[0], schedule[1]))
                self.schedule_data.rooms[schedule[4]].scheduled_teams.append(current_team_id)
                current_team_id += 1

    def train_benchmark_episodes(self) -> None:
        """Train the Q-Learning algorithm for benchmarking."""
        self.initialize_schedule_and_states()
        self.current_schedule_length = 0
        actions = tuple(self.schedule_data.teams.keys())
        while self.states:
            current_state = random.choice(self.states)
            current_start_time = current_state[0]
            current_end_time = current_state[1]
            current_round_type = current_state[2]
            current_location_type = current_state[3]
            current_location_id = current_state[4]
            current_location_letter = current_location_id[0]
            current_location_side = current_location_id[1]

            if self.is_terminal_state():
                break

            actions = self.update_available_actions(current_state)
            if actions:
                selected_action = random.choice(actions)
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
                    self.states.remove(current_state)
                    self.staticStates[self.staticStates.index(current_state)] = (
                        current_start_time,
                        current_end_time,
                        current_round_type,
                        current_location_type,
                        f"{current_location_letter}{current_location_side}",
                        selected_action,
                    )

                else:
                    self.states.remove(current_state)
            else:
                self.states.remove(current_state)

            if not self.states:
                break

        scheduleCSVFileName = "./exports/training_schedules_output/schedule_episode_benchmark.csv"
        self.exporter.export_schedule_to_csv(scheduleCSVFileName, self.schedule)

        self.completed_percentage = self.current_schedule_length / self.required_schedule_slots
        self.evaluator = ScheduleEvaluator(scheduleCSVFileName)
        self.schedule_score = self.evaluator.calculate_schedule_score(self.completed_percentage)
        self.evaluator.generate_aggregate_statistics(name="Benchmarks")

        self.completion_percentage["Benchmarks"].append(self.completed_percentage)
        self.scores["Benchmarks"].append(self.schedule_score)

    def train_one_episode(self, episode) -> None:
        """Train the Q-Learning algorithm for one episode."""
        logging.info(f"Starting training episode {episode}")

        self.initialize_schedule_and_states()
        self.current_schedule_length = 0
        actions = tuple(self.schedule_data.teams.keys())
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

            if self.is_terminal_state():
                break

            actions = self.update_available_actions(current_state)
            if actions:
                selected_action = self.select_action(
                    current_state, actions
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
                        self.update_q_value(current_state, selected_action, reward, next_state, actions)
                    else:
                        self.q_table[(current_state, selected_action)] = (1 - self.learning_rate) * self.q_table.get(
                            (current_state, selected_action), 0
                        ) + self.learning_rate * reward
                else:
                    self.states.remove(current_state)  # Optionally, remove the state and continue
            else:
                self.states.remove(current_state)

            if not self.states:
                break

        logging.info(f"Finished training episode {episode}")

        self.episode_rewards.append(episode_reward)  # Track the reward for the current episode
        self.epsilon = max(self.epsilon_end, self.epsilon_decay * self.epsilon)  # Decays each episode

        # Q-value changes
        avg_reward = sum(self.episode_rewards) / len(self.episode_rewards)
        self.average_rewards.append(avg_reward)

        if len(self.episode_rewards) < 2:
            q_value_change = 0
        else:
            q_value_change = abs(self.episode_rewards[-1] - self.episode_rewards[-2])
        self.q_value_changes.append(q_value_change)

        if self.q_value_changes and len(self.q_value_changes) > 1:
            avg_change = sum(self.q_value_changes) / len(self.q_value_changes)
        else:
            avg_change = 0

        self.average_reward_changes.append(avg_change)

        # Explore vs. Exploit
        self.num_exploration_counts.append(self.exploration_count)
        self.num_exploitation_counts.append(self.exploitation_count)

        # Export the schedule for evaluation
        scheduleCSVFileName = f"./exports/training_schedules_output/schedule_episode_{episode}.csv"
        self.exporter.export_schedule_to_csv(scheduleCSVFileName, self.schedule)

        # Evaluate the schedule
        self.completed_percentage = self.current_schedule_length / self.required_schedule_slots
        self.evaluator = ScheduleEvaluator(scheduleCSVFileName)
        self.schedule_score = self.evaluator.calculate_schedule_score(self.completed_percentage)
        self.evaluator.generate_aggregate_statistics(name="Training")

        self.completion_percentage["Training"].append(self.completed_percentage)
        self.scores["Training"].append(self.schedule_score)

    def generate_optimal_schedule(self) -> None:
        """Generate the optimal schedule using the Q-Learning algorithm."""
        self.initialize_schedule_and_states()
        self.current_schedule_length = 0

        while self.states:
            current_state = self.states[0]
            available_actions = self.update_available_actions(current_state)

            if available_actions:
                best_action = max(
                    available_actions,
                    key=lambda action: self.q_table.get((current_state, action), float("-inf")),
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
        q_table_filename = f"./exports/q_table.csv"
        self.exporter.export_q_table_to_csv(q_table_filename, self.q_table)
        optimal_filename = f"./exports/optimal_schedule.csv"
        self.exporter.export_optimal_schedule_to_excel(optimal_filename, self.schedule)

        self.completed_percentage = self.current_schedule_length / self.required_schedule_slots
        self.evaluator = ScheduleEvaluator(optimal_filename)
        self.schedule_score = self.evaluator.calculate_schedule_score(self.completed_percentage)
        self.evaluator.generate_aggregate_statistics(name="Optimal")
        self.completion_percentage["Optimal"].append(self.completed_percentage)
        self.scores["Optimal"].append(self.schedule_score)

    def update_available_actions(self, state) -> List[int]:
        """Update the available actions for the current state."""
        time_start, time_end, round_type, location_type, location_id, team_id = state
        time_slot = (time_start, time_end)

        if round_type == "practice":
            potential_actions = [team for team in self.schedule_data.teams if team in self.practice_teams_available]
        elif round_type == "table":
            potential_actions = [team for team in self.schedule_data.teams if team in self.table_teams_available]

        remove_actions = []
        available_actions = []

        # 1. "Is the team already scheduled for the current round type for rounds_per_type number of times?"
        for team_id in potential_actions:
            if (
                self.schedule_data.teams[team_id].scheduled_round_types[round_type]
                >= self.schedule_data.round_types_per_team[round_type]
            ):
                remove_actions.append(team_id)

        # 2. "Is the current state's time slot overlapping with any time slot scheduled for the team?"
        for team_id in potential_actions:
            for existing_start, existing_end in self.schedule_data.teams[team_id].scheduled_times:
                if (time_start < existing_end) and (time_end > existing_start):
                    remove_actions.append(team_id)
                    break  # No need to check further slots for this team

        # 3. "Is the current state's table side == 2?"
        if location_id[-1] == "2":  # Check if table side is 2
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

    def update_team_availability(self, team_id, round_type, time_slot, location_id, side) -> None:
        """Update the team availability for the current state."""
        if team_id in self.schedule_data.teams:
            team_info = self.schedule_data.teams[team_id]

            team_info.scheduled_round_types[round_type] += 1
            team_info.scheduled_times.append(time_slot)
            team_info.scheduled_tables.append((location_id, int(side)))
            team_info.scheduled_time_table_pairs.append((time_slot, (location_id, int(side))))

            if round_type == "practice":
                self.practice_teams_available.remove(team_id)
            elif round_type == "table":
                self.table_teams_available.remove(team_id)

            # Table side and opponent logic
            table_id = location_id[0]

            if side == "2":  # Assuming side 2 indicates both are scheduled
                other_side = "1"
                # Find the team assigned to the other side, if any
                for other_team_id, other_team_info in self.schedule_data.teams.items():
                    if (
                        other_team_id != team_id
                        and (time_slot, (table_id, other_side)) in other_team_info.scheduled_time_table_pairs
                    ):
                        # Update opponents for both teams
                        other_team_info["scheduled_opponents"].append(team_id)
                        team_info["scheduled_opponents"].append(other_team_id)

                        break  # Found the other team, no need to continue the loop
        else:
            print(f"Team {team_id} does not exist.")

    def update_table_availability(self, location_id, team_id, time_slot) -> None:
        """Update the table availability for the current state."""
        table_id = location_id[0]  # Extract table ID (e.g., 'A1' from 'A11')
        side = int(location_id[-1])  # Extract side (e.g., 1 from 'A11')

        if (table_id, side) in self.schedule_data.tables:
            self.schedule_data.tables[(table_id, side)].scheduled_teams.append(team_id)
            self.schedule_data.tables[(table_id, side)].scheduled_times.append(time_slot)
        else:
            print(f"Table {table_id} side {side} does not exist.")

    def update_schedule(self, current_state, selected_action) -> None:
        """Update the schedule for the current state."""
        for i, schedule_row in enumerate(self.schedule):
            sched_row = tuple(schedule_row[:5])
            if sched_row == current_state[:5] and schedule_row[5] is None:
                self.schedule[i][5] = selected_action
                break
        self.current_schedule_length += 1

    def update_q_value(self, state, action, reward, next_state, actions) -> None:
        """Update the Q-value for the current state-action pair."""
        current_q = self.q_table.get((state, action), 0)

        if not actions:
            max_future_q = 0
        else:
            max_future_q = max(self.q_table.get((next_state, a), 0) for a in actions)

        new_q = (1 - self.learning_rate) * current_q + self.learning_rate * (
            reward + self.discount_factor * max_future_q
        )
        self.q_table[(state, action)] = new_q

    def find_previous_state(self, state) -> Optional[Tuple]:
        """Find the previous state for the current state."""
        index = self.staticStates.index(state)
        prev_state = self.staticStates[index - 1]
        if prev_state[5] is None:
            return None
        else:
            return prev_state

    def update_previous_state(self, prev_state) -> None:
        """Update the previous state for the current state."""
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

        self.schedule_data.teams[prev_team_id].scheduled_round_types[prev_round_type] -= 1
        self.schedule_data.teams[prev_team_id].scheduled_times.remove(prev_time_slot)
        self.schedule_data.teams[prev_team_id].scheduled_tables.remove(prev_table_key)
        self.schedule_data.teams[prev_team_id].scheduled_time_table_pairs.remove((prev_time_slot, prev_table_key))
        self.schedule_data.tables[prev_table_key].scheduled_teams.remove(prev_team_id)
        self.schedule_data.tables[prev_table_key].scheduled_times.remove(prev_time_slot)
        
        self.schedule[self.staticStates.index(prev_state)][5] = None
        self.current_schedule_length -= 1
        if prev_round_type == "practice":
            self.practice_teams_available.append(prev_team_id)
        elif prev_round_type == "table":
            self.table_teams_available.append(prev_team_id)

    def select_action(self, state, actions) -> Optional[int]:
        """Select an action using the epsilon-greedy policy."""
        if not actions:
            return None

        random_val = random.uniform(0, 1)

        if random_val < self.epsilon:  # Exploration
            self.exploration_count += 1

            return random.choice(actions)
        else:  # Exploitation
            self.exploitation_count += 1

            q_values = [self.q_table.get((state, a), 0) for a in actions]
            max_q_value = max(q_values)
            best_actions = [a for a, q in zip(actions, q_values) if q == max_q_value]
            return random.choice(best_actions)

    def normalize_reward(self, reward, min_reward, max_reward) -> float:
        """Normalize the reward for the current state-action pair."""
        if max_reward - min_reward == 0:
            return 0
        else:
            return (reward - min_reward) / (max_reward - min_reward)

    def get_reward(self, state, action) -> float:
        """Get the reward for the current state-action pair."""
        
        # Unpack state
        time_start, time_end, round_type, location_type, location_id, team_id = state

        # Get the selected team's attributes
        team = self.schedule_data.teams[action]
        scheduled_round_types = team.scheduled_round_types
        scheduled_times = team.scheduled_times
        scheduled_tables = team.scheduled_tables
        scheduled_opponents = team.scheduled_opponents
        scheduled_time_table_pairs = team.scheduled_time_table_pairs

        table_key = (location_id[0], int(location_id[1]))

        start_time_minutes = TimeUtilities.time_to_minutes(time_start)
        end_time_minutes = TimeUtilities.time_to_minutes(time_end)

        reward = 0

        # Calculate table consistency reward
        reward += self.calculate_table_consistency_reward(scheduled_tables)

        # Calculate opponent variety reward
        reward += self.calculate_opponent_variety_reward(scheduled_opponents)

        # Calculate back-to-back penalty
        reward += self.calculate_back_to_back_penalty(scheduled_times, start_time_minutes, end_time_minutes)

        # Calculate break time reward
        reward += self.calculate_break_time_reward(scheduled_times, start_time_minutes, end_time_minutes)

        # Apply completion reward multiplier
        completion_reward = self.current_schedule_length / (
            self.required_schedule_slots
            - (self.schedule_data.num_teams * self.schedule_data.round_types_per_team['judging'])
        )
        reward += reward * completion_reward

        return reward

    def calculate_table_consistency_reward(self, scheduled_tables) -> float:
        """Calculate the table consistency reward."""
        reward = 0
        length_of_tables_scheduled = len(scheduled_tables)
        if length_of_tables_scheduled > 1:
            unique_to_tables = len(set(scheduled_tables)) / len(scheduled_tables)
            reward_table = unique_to_tables / self.max_num_rounds_per_team  # Original reward calculation
            # Normalize this reward
            min_reward_table = 0
            max_reward_table = 1
            reward_table_normalized = self.normalize_reward(reward_table, min_reward_table, max_reward_table)
            reward += reward_table_normalized * self.soft_constraints_weight["Table Consistency"]
        return reward

    def calculate_opponent_variety_reward(self, scheduled_opponents) -> float:
        """Calculate the opponent variety reward."""
        reward = 0
        length_of_opponents_scheduled = len(scheduled_opponents)
        if length_of_opponents_scheduled > 1:
            unique = []
            for opponent in scheduled_opponents:
                if opponent not in unique:
                    unique.append(opponent)
            length_of_unique_opponents = len(unique)
            unique_to_opponents = length_of_unique_opponents / length_of_opponents_scheduled
            reward_opponent = (
                unique_to_opponents * self.max_num_rounds_per_team * self.soft_constraints_weight["Opponent Variety"]
            )
            min_reward_opponent = 0
            max_reward_opponent = 1
            reward_opponent_normalized = self.normalize_reward(
                reward_opponent, min_reward_opponent, max_reward_opponent
            )
            reward += reward_opponent_normalized
        return reward

    def calculate_back_to_back_penalty(self, scheduled_times, start_time_minutes, end_time_minutes) -> float:
        """Calculate the back-to-back penalty."""
        reward = 0
        for i in range(len(scheduled_times)):
            timeActionStart = TimeUtilities.time_to_minutes(scheduled_times[i][0])
            timeActionEnd = TimeUtilities.time_to_minutes(scheduled_times[i][1])
            reward_back_to_back = 0
            if timeActionStart - end_time_minutes <= 0 or timeActionEnd - start_time_minutes <= 0:
                reward_back_to_back -= 1
            else:
                reward_back_to_back += 1

            if start_time_minutes - timeActionEnd <= 0 or end_time_minutes - timeActionStart <= 0:
                reward_back_to_back -= 1
            else:
                reward_back_to_back += 1

            min_reward_back_to_back = -1  # Define based on expected range
            max_reward_back_to_back = 1
            reward_back_to_back_normalized = self.normalize_reward(
                reward_back_to_back, min_reward_back_to_back, max_reward_back_to_back
            )
            reward += reward_back_to_back_normalized * self.soft_constraints_weight["Back to Back Penalty"]
        return reward

    def calculate_break_time_reward(self, scheduled_times, start_time_minutes, end_time_minutes) -> float:
        """Calculate the break time reward."""
        reward = 0
        break_time = 30
        for i in range(1, len(scheduled_times)):
            timeActionStart = TimeUtilities.time_to_minutes(scheduled_times[i][0])
            timeActionEnd = TimeUtilities.time_to_minutes(scheduled_times[i][1])
            reward_break_time = 0
            if timeActionStart - end_time_minutes >= break_time or timeActionEnd - start_time_minutes >= break_time:
                reward_break_time += 1
            else:
                reward_break_time -= 1

            if start_time_minutes - timeActionEnd >= break_time or end_time_minutes - timeActionStart >= break_time:
                reward_break_time += 1
            else:
                reward_break_time -= 1

            min_reward_break_time = -1  # Define based on expected range
            max_reward_break_time = 1
            reward_break_time_normalized = self.normalize_reward(
                reward_break_time, min_reward_break_time, max_reward_break_time
            )
            reward += reward_break_time_normalized * self.soft_constraints_weight["Break Time"]
        return reward

    ''' TODO 
    def transform_for_heatmap(self) -> Dict[Tuple[Tuple, Any], float]:
        """Transform the Q-table data for the heatmap."""
        data = {}
        for (
            (
                start_time,
                end_time,
                round_type,
                location_type,
                location_id,
                team_in_state,
            ),
            action,
        ), value in self.q_table.items():
            # Use a more detailed state representation
            detailed_state = (
                start_time[:5],
                round_type,
            )  # Simplify start_time and combine with round_type
            if (detailed_state, action) not in data:
                data[(detailed_state, action)] = []
            data[(detailed_state, action)].append(value)

        # Aggregate values by averaging
        aggregated_data = {k: sum(values) / len(values) for k, values in data.items()}
        return aggregated_data
    '''

    ''' TODO
    def aggregated_data_to_2d_array(self, aggregated_data) -> Tuple[np.ndarray, List[str], List[str]]:
        """Convert the aggregated data to a 2D array for the heatmap."""
        detailed_states = sorted(set(k[0] for k in aggregated_data.keys()), key=lambda x: (x[1], x[0]))
        actions = sorted(set(k[1] for k in aggregated_data.keys()))  # Assuming actions are team IDs

        heatmap_data = np.zeros((len(detailed_states), len(actions)))

        for (detailed_state, action), value in aggregated_data.items():
            row = detailed_states.index(detailed_state)
            col = actions.index(action)
            heatmap_data[row, col] = value

        # Generate labels for heatmap axes
        state_labels = [f"{state[0]}-{state[1]}" for state in detailed_states]  # Combining for label
        action_labels = [str(action) for action in actions]  # Assuming actions are already meaningful

        return heatmap_data, state_labels, action_labels
    '''

    def is_terminal_state(self) -> bool:
        """Check if the current state is a terminal state."""
        if len(self.practice_teams_available) == 0 and len(self.table_teams_available) == 0:
            return True
        else:
            return False
