from typing import Dict
from config import Config
from utility.time_utilities import TimeUtilities

TABLE_CONSISTENCY = Config.TABLE_CONSISTENCY
OPPONENT_VARIETY = Config.OPPONENT_VARIETY
BACK_TO_BACK_PENALTY = Config.BACK_TO_BACK_PENALTY
BREAK_TIME = Config.BREAK_TIME
JUDGING = Config.JUDGING

class RewardCalculator:
    def __init__(self, schedule_data, required_schedule_slots, current_schedule_length, soft_constraints_weight, max_num_rounds_per_team):
        self.schedule_data = schedule_data
        self.required_schedule_slots = required_schedule_slots
        self.current_schedule_length = current_schedule_length
        self.soft_constraints_weight = soft_constraints_weight
        self.max_num_rounds_per_team = max_num_rounds_per_team

    def normalize_reward(self, reward, min_reward, max_reward) -> float:
        """
        Normalize the reward for the current state-action pair.
        
        Args:
            reward (float): The reward to be normalized.
            min_reward (float): The minimum possible reward.
            max_reward (float): The maximum possible reward.
            
        Returns:
            float: The normalized reward.
        
        """
        if max_reward - min_reward == 0:
            return 0
        else:
            return (reward - min_reward) / (max_reward - min_reward)

    def calculate_table_consistency_reward(self, scheduled_tables) -> float:
        """
        Calculate the table consistency reward.
        
        """
        reward = 0
        length_of_tables_scheduled = len(scheduled_tables)
        if length_of_tables_scheduled > 1:
            unique_to_tables = len(set(scheduled_tables)) / len(scheduled_tables)
            reward_table = unique_to_tables / self.max_num_rounds_per_team  # Original reward calculation
            # Normalize this reward
            min_reward_table = 0
            max_reward_table = 1
            reward_table_normalized = self.normalize_reward(reward_table, min_reward_table, max_reward_table)
            reward += reward_table_normalized * self.soft_constraints_weight[TABLE_CONSISTENCY]
        return reward

    def calculate_opponent_variety_reward(self, scheduled_opponents) -> float:
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
            unique_to_opponents = length_of_unique_opponents / length_of_opponents_scheduled
            reward_opponent = (
                unique_to_opponents * self.max_num_rounds_per_team * self.soft_constraints_weight[OPPONENT_VARIETY]
            )
            min_reward_opponent = 0
            max_reward_opponent = 1
            reward_opponent_normalized = self.normalize_reward(
                reward_opponent, min_reward_opponent, max_reward_opponent
            )
            reward += reward_opponent_normalized
        return reward

    def calculate_back_to_back_penalty(self, scheduled_times, start_time_minutes, end_time_minutes) -> float:
        """
        Calculate the back-to-back penalty.
        
        """
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
            reward += reward_back_to_back_normalized * self.soft_constraints_weight[BACK_TO_BACK_PENALTY]
        return reward

    def calculate_break_time_reward(self, scheduled_times, start_time_minutes, end_time_minutes) -> float:
        """
        Calculate the break time reward.
        
        """
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
            reward += reward_break_time_normalized * self.soft_constraints_weight[BREAK_TIME]
        return reward
    
    def get_reward(self, state, action) -> float:
        """
        Get the reward for the current state-action pair.
        
        """
        
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
            - (self.schedule_data.NUM_TEAMS * self.schedule_data.ROUND_TYPE_PER_TEAM[JUDGING])
        )
        reward += reward * completion_reward

        return reward
