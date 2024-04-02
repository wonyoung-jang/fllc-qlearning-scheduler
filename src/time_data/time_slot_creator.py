"""This module contains the TimeSlotCreator class."""
from utility.time_utilities import TimeUtilities
from config import Config

JUDGING = Config.JUDGING
PRACTICE = Config.PRACTICE
TABLE = Config.TABLE


class TimeSlotCreator:
    """
    Class for creating time slots for rounds.
    
    """

    @staticmethod
    def calculate_end_times(start_times, duration):
        """
        Calculate the end times for a given list of start times and duration.
        
        Inputs:
            start_times (list): List of start times.
            duration (int): Duration of each time slot.
            
        Returns:
            list: List of tuples containing the start and end times for each time slot.
            
        """
        end_times = []
        for start_time in start_times:
            end_time = TimeUtilities.add_minutes_to_time(start_time, duration)
            end_times.append((start_time, end_time))
        return end_times

    def adjust_rounds_round_type_time_slots(self, round_type, time_data):
        """Adjust the time slots for the given round type."""
        if round_type not in [PRACTICE, TABLE]:
            raise ValueError(f"Invalid round type: {round_type}. Expected 'practice' or 'table'")
        
        if round_type == PRACTICE:
            start_time = time_data.PRACTICE_ROUNDS_START_TIME
            start_times = time_data.practice_round_start_times
            current_time = start_time
            end_time = time_data.PRACTICE_ROUNDS_STOP_TIME
            time_length = time_data.ROUND_TYPE_DURATIONS[PRACTICE]
            available_duration = time_data.available_practice_duration
        
        if round_type == TABLE:
            start_time = time_data.TABLE_ROUNDS_START_TIME
            start_times = time_data.table_round_start_times
            current_time = start_time
            end_time = time_data.TABLE_ROUNDS_STOP_TIME
            time_length = time_data.ROUND_TYPE_DURATIONS[TABLE]
            available_duration = time_data.available_table_duration
        
        round_type_time_slots_round = self.calculate_end_times(start_times, time_length)
        
        while round_type_time_slots_round[-1][-1] > end_time:
            time_data.MINIMUM_SLOTS_REQUIRED[round_type] += 1
            time_length = round(available_duration / time_data.MINIMUM_SLOTS_REQUIRED[round_type], 0)
            start_times = [start_time]
            current_time = start_time
        
            for _ in range(time_data.MINIMUM_SLOTS_REQUIRED[round_type] - 1):
                current_time = TimeUtilities.add_minutes_to_time(current_time, time_length)
                start_times.append(current_time)
        
            round_type_time_slots_round = self.calculate_end_times(start_times, time_length)
        
        return round_type_time_slots_round

    def create_round_type_time_slots(self, time_data):
        """Create time slots for each round type."""
        time_data.round_type_time_slots = {
            JUDGING: self.calculate_end_times(time_data.judging_round_start_times, time_data.ROUND_TYPE_DURATIONS["judging"]),
            PRACTICE: self.adjust_rounds_round_type_time_slots(PRACTICE, time_data),
            TABLE: self.adjust_rounds_round_type_time_slots(TABLE, time_data),
        }
