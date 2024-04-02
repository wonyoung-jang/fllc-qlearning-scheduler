"""This module contains the QLearning class, which is responsible for the Q-Learning algorithm for scheduling."""
import random
import logging
import pickle
import numpy as np
from collections import defaultdict
from datetime import datetime
from typing import List, Tuple, Dict, Optional, Any
from PySide6.QtCore import QObject, Signal

from config import Config

from utility.time_utilities import TimeUtilities

from .exporter import QLearningExporter
from .reward_calculator import RewardCalculator
from .schedule_initializer import ScheduleInitializer
from .state_manager import StateManager
from .availability_updater import AvailabilityUpdater
from .schedule_updater import ScheduleUpdater

# Config Constants
LOGGING_FILE_NAME   = Config.LOGGING_FILE_NAME
LOGGING_FORMAT      = Config.LOGGING_FORMAT

JUDGING     = Config.JUDGING
PRACTICE    = Config.PRACTICE
TABLE       = Config.TABLE

LOCATION_TYPE_ROOM  = Config.LOCATION_TYPE_ROOM
LOCATION_TYPE_TABLE = Config.LOCATION_TYPE_TABLE

TABLE_SIDE_1 = Config.TABLE_SIDE_1
TABLE_SIDE_2 = Config.TABLE_SIDE_2

TABLE_CONSISTENCY       = Config.TABLE_CONSISTENCY
OPPONENT_VARIETY        = Config.OPPONENT_VARIETY
BACK_TO_BACK_PENALTY    = Config.BACK_TO_BACK_PENALTY
BREAK_TIME              = Config.BREAK_TIME

TABLE_CONSISTENCY_WEIGHT    = Config.TABLE_CONSISTENCY_WEIGHT
OPPONENT_VARIETY_WEIGHT     = Config.OPPONENT_VARIETY_WEIGHT
BACK_TO_BACK_PENALTY_WEIGHT = Config.BACK_TO_BACK_PENALTY_WEIGHT
BREAK_TIME_WEIGHT           = Config.BREAK_TIME_WEIGHT

LEARNING_RATE       = Config.LEARNING_RATE
DISCOUNT_FACTOR     = Config.DISCOUNT_FACTOR
EPSILON_START       = Config.EPSILON_START
EPSILON_END         = Config.EPSILON_END
EPSILON_DECAY       = Config.EPSILON_DECAY
TRAINING_EPISODES   = Config.TRAINING_EPISODES

GUI_REFRESH_INTERVAL    = Config.GUI_REFRESH_INTERVAL

EXPORTS_DIRECTORY                   = Config.EXPORTS_DIRECTORY
CSV_EXT                             = Config.CSV_EXT
TRAINING_SCHEDULE_CSV_FILENAME      = Config.TRAINING_SCHEDULE_CSV_FILENAME
Q_TABLE_CSV_FILENAME                = Config.Q_TABLE_CSV_FILENAME
OPTIMAL_SCHEDULE_CSV_FILENAME       = Config.OPTIMAL_SCHEDULE_CSV_FILENAME

logging.basicConfig(filename=LOGGING_FILE_NAME, level=logging.DEBUG, format=LOGGING_FORMAT)

class QLearning:
    """
    Q-Learning algorithm for scheduling.
    
    """

    def __init__(self, schedule_data, time_data):
        """
        Initialize the Q-Learning algorithm for scheduling.
        
        """
        self.learning_rate = LEARNING_RATE
        self.discount_factor = DISCOUNT_FACTOR
        self.epsilon_start = EPSILON_START
        self.epsilon_end = EPSILON_END
        self.epsilon_decay = EPSILON_DECAY
        self.training_episodes = TRAINING_EPISODES
        
        self.gui_refresh_interval = GUI_REFRESH_INTERVAL
        
        self.epsilon = self.epsilon_start

        self.q_table: Dict[Tuple[Tuple, Any], float] = {}
        self.episode_rewards: List[float] = []
        self.num_exploration_counts: List[int] = []
        self.num_exploitation_counts: List[int] = []
        self.q_value_changes: List[float] = []
        self.average_rewards: List[float] = []
        self.average_reward_changes: List[float] = []

        self.soft_constraints_weight = {
            TABLE_CONSISTENCY: TABLE_CONSISTENCY_WEIGHT,
            OPPONENT_VARIETY: OPPONENT_VARIETY_WEIGHT,
            BACK_TO_BACK_PENALTY: BACK_TO_BACK_PENALTY_WEIGHT,
            BREAK_TIME: BREAK_TIME_WEIGHT,
        }

        self.schedule_data = schedule_data
        self.time_data = time_data

        self.required_schedule_slots = self.schedule_data.NUM_TEAMS * sum(
            self.schedule_data.ROUND_TYPE_PER_TEAM.values()
        )

        self.possible_schedule_slots = self.schedule_data.NUM_ROOMS * self.time_data.MINIMUM_SLOTS_REQUIRED[
            JUDGING
        ] + self.schedule_data.num_tables_and_sides * (
            self.time_data.MINIMUM_SLOTS_REQUIRED[PRACTICE] + self.time_data.MINIMUM_SLOTS_REQUIRED[TABLE]
        )

        self.schedule_initializer = ScheduleInitializer(self.schedule_data, self.time_data)
        (self.schedule, 
         self.states, 
         self.static_states, 
         self.current_schedule_length, 
         self.practice_teams_available, 
         self.table_teams_available, 
         self.exploration_count, 
         self.exploitation_count) = self.schedule_initializer.initialize_schedule_and_states()
        
        self.q_table_size_limit = len(self.states) * len(self.schedule_data.teams)
        self.max_num_rounds_per_team = sum(self.schedule_data.ROUND_TYPE_PER_TEAM.values())

        self.exporter = QLearningExporter()
        self.reward_calculator = RewardCalculator(
            self.schedule_data,
            self.required_schedule_slots,
            self.current_schedule_length,
            self.soft_constraints_weight,
            self.max_num_rounds_per_team
        )
        
        self.schedule_updater = ScheduleUpdater()
        
        self.availability_updater = AvailabilityUpdater(
            self.schedule_data, 
            self.practice_teams_available, 
            self.table_teams_available
        )
        
        self.state_manager = StateManager(
            self.schedule_data,
            self.static_states,
            self.current_schedule_length,
            self.practice_teams_available,
            self.table_teams_available,
            self.schedule
        )
        
    def train_one_episode(self, episode) -> None:
        """
        Train the Q-Learning algorithm for one episode.
        
        """
        logging.info(f"Starting training episode {episode}")

        (self.schedule, 
         self.states, 
         self.static_states, 
         self.current_schedule_length, 
         self.practice_teams_available, 
         self.table_teams_available, 
         self.exploration_count, 
         self.exploitation_count) = self.schedule_initializer.initialize_schedule_and_states()
        
        actions = tuple(self.schedule_data.teams.keys())
        episode_reward = 0

        while self.states:
            current_state = self.states[0]

            logging.debug(f"Current state: {current_state}")

            current_start_time      = current_state[0]
            current_end_time        = current_state[1]
            current_round_type      = current_state[2]
            current_location_type   = current_state[3]
            current_location_id     = current_state[4]
            current_location_letter = current_location_id[0]
            current_location_side   = current_location_id[1]

            if self.is_terminal_state():
                break

            actions = self.state_manager.update_available_actions(current_state)
            
            if actions:
                selected_action = self.select_action(
                    current_state, actions
                )  # Select an action using the epsilon-greedy policy
                
                if selected_action is not None:
                    self.availability_updater.update_team_availability(
                        selected_action,
                        current_round_type,
                        (current_start_time, current_end_time),
                        current_location_letter,
                        current_location_side,
                    )
                    
                    self.availability_updater.update_table_availability(
                        current_location_id,
                        selected_action,
                        (current_start_time, current_end_time),
                    )
                    
                    self.schedule, self.current_schedule_length = self.schedule_updater.update_schedule(current_state, selected_action, self.schedule, self.current_schedule_length)
                    reward = self.reward_calculator.get_reward(current_state, selected_action)                    
                    episode_reward += reward
                    self.states.remove(current_state)
                    
                    self.static_states[self.static_states.index(current_state)] = (
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
        scheduleCSVFileName = f'{EXPORTS_DIRECTORY}{TRAINING_SCHEDULE_CSV_FILENAME}{episode}{CSV_EXT}'
        self.exporter.export_schedule_to_csv(scheduleCSVFileName, self.schedule)

    def generate_optimal_schedule(self) -> None:
        """
        Generate the optimal schedule using the Q-Learning algorithm.
        
        """
        (self.schedule, 
         self.states, 
         self.static_states, 
         self.current_schedule_length, 
         self.practice_teams_available, 
         self.table_teams_available, 
         self.exploration_count, 
         self.exploitation_count) = self.schedule_initializer.initialize_schedule_and_states()
        self.current_schedule_length = 0

        while self.states:
            current_state = self.states[0]
            available_actions = self.state_manager.update_available_actions(current_state)

            if available_actions:
                best_action = max(
                    available_actions,
                    key=lambda action: self.q_table.get((current_state, action), float("-inf")),
                )
                
                if best_action:
                    self.availability_updater.update_team_availability(
                        best_action,
                        current_state[2],
                        (current_state[0], current_state[1]),
                        current_state[4][0],
                        current_state[4][1],
                    )
                    
                    self.availability_updater.update_table_availability(
                        current_state[4],
                        best_action,
                        (current_state[0], current_state[1]),
                    )
                    
                    self.schedule, self.current_schedule_length = self.schedule_updater.update_schedule(current_state, best_action, self.schedule, self.current_schedule_length)

                    self.static_states[self.static_states.index(current_state)] = (
                        current_state[0],
                        current_state[1],
                        current_state[2],
                        current_state[3],
                        current_state[4],
                        best_action,
                    )
                    
            self.states.remove(current_state)
            
        self.exporter.export_q_table_to_csv(f'{EXPORTS_DIRECTORY}{Q_TABLE_CSV_FILENAME}{CSV_EXT}', self.q_table)
        self.exporter.export_optimal_schedule_to_excel(f'{EXPORTS_DIRECTORY}{OPTIMAL_SCHEDULE_CSV_FILENAME}{CSV_EXT}', self.schedule)
    
    def update_q_value(self, state, action, reward, next_state, actions) -> None:
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

    def select_action(self, state, actions) -> Optional[int]:
        """
        Select an action using the epsilon-greedy policy.
        
        """
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

    def is_terminal_state(self) -> bool:
        """
        Check if the current state is a terminal state.
        
        """
        if len(self.practice_teams_available) == 0 and len(self.table_teams_available) == 0:
            return True
        else:
            return False
