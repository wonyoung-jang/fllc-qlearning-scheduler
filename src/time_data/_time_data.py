"""This module is responsible for generating the time slots for each round type based on the number of teams and rooms/tables/sides."""
from datetime import datetime, timedelta
from .time_utilities import TimeUtilities
from .start_time_generator import StartTimeGenerator
from .time_slot_creator import TimeSlotCreator
from config import Config

JUDGING = Config.JUDGING
PRACTICE = Config.PRACTICE
TABLE = Config.TABLE

JUDGING_ROUNDS_START_TIME = Config.JUDGING_ROUNDS_START_TIME
PRACTICE_ROUNDS_START_TIME = Config.PRACTICE_ROUNDS_START_TIME
PRACTICE_ROUNDS_STOP_TIME = Config.PRACTICE_ROUNDS_STOP_TIME
TABLE_ROUNDS_START_TIME = Config.TABLE_ROUNDS_START_TIME
TABLE_ROUNDS_STOP_TIME = Config.TABLE_ROUNDS_STOP_TIME
MINIMUM_SLOTS_REQUIRED = Config.MINIMUM_SLOTS_REQUIRED

ROUND_TYPE_DURATIONS = Config.ROUND_TYPE_DURATIONS


class TimeData:
    """
    Class to store data for scheduling rounds and tables.
    
    """

    def __init__(self, schedule_data):
        """
        Initialize TimeData object.
        
        """
        self.schedule_data = schedule_data
        
        self.JUDGING_ROUNDS_START_TIME = JUDGING_ROUNDS_START_TIME
        self.PRACTICE_ROUNDS_START_TIME = PRACTICE_ROUNDS_START_TIME
        self.PRACTICE_ROUNDS_STOP_TIME = PRACTICE_ROUNDS_STOP_TIME
        self.TABLE_ROUNDS_START_TIME = TABLE_ROUNDS_START_TIME
        self.TABLE_ROUNDS_STOP_TIME = TABLE_ROUNDS_STOP_TIME
        self.MINIMUM_SLOTS_REQUIRED = MINIMUM_SLOTS_REQUIRED
            
            
        self.available_practice_duration = 0
        self.available_table_duration = 0
        
        self.ROUND_TYPE_DURATIONS = ROUND_TYPE_DURATIONS
        
        self.judging_round_start_times = []
        self.practice_round_start_times = []
        self.table_round_start_times = []
        self.round_type_time_slots = {
            JUDGING: [],
            PRACTICE: [],
            TABLE: [],
        }
        
        self.update_time_data()

    def __str__(self):
        """
        Return string representation of TimeData object.
        
        """
        return f"TimeData(JUDGING_ROUNDS_START_TIME={self.JUDGING_ROUNDS_START_TIME}, PRACTICE_ROUNDS_START_TIME={self.PRACTICE_ROUNDS_START_TIME}, PRACTICE_ROUNDS_STOP_TIME={self.PRACTICE_ROUNDS_STOP_TIME}, TABLE_ROUNDS_START_TIME={self.TABLE_ROUNDS_START_TIME}, TABLE_ROUNDS_STOP_TIME={self.TABLE_ROUNDS_STOP_TIME}, MINIMUM_SLOTS_REQUIRED={self.MINIMUM_SLOTS_REQUIRED}, available_practice_duration={self.available_practice_duration}, available_table_duration={self.available_table_duration}, ROUND_TYPE_DURATIONS={self.ROUND_TYPE_DURATIONS}, judging_round_start_times={self.judging_round_start_times}, practice_round_start_times={self.practice_round_start_times}, table_round_start_times={self.table_round_start_times}, round_type_time_slots={self.round_type_time_slots})"

    def __repr__(self):
        """
        Return string representation of TimeData object.
        
        """
        return self.__str__()

    def calculate_minimum_slots_required(self, NUM_TEAMS, divisor, round_type=None):
        """
        Calculate the minimum number of slots required for a given number of teams and divisor.
        
        """
        if divisor == 0:
            raise ValueError("Divisor cannot be zero.")
        if round_type:
            NUM_TEAMS *= self.schedule_data.ROUND_TYPE_PER_TEAM[round_type]
        slots_check = NUM_TEAMS % divisor
        if slots_check == 0:
            return NUM_TEAMS // divisor
        else:
            return (NUM_TEAMS // divisor) + 1

    def update_time_data(self):
        """
        Update the time data.
        
        """
        self.update_minimum_slots_required()
        self.update_round_type_durations()
        start_time_generator = StartTimeGenerator()
        start_time_generator.generate_start_times(self)
        time_slot_creator = TimeSlotCreator()
        time_slot_creator.create_round_type_time_slots(self)

    def update_minimum_slots_required(self):
        """
        Update the minimum number of slots required for each round type.
        
        """
        self.MINIMUM_SLOTS_REQUIRED = {
            JUDGING: self.calculate_minimum_slots_required(self.schedule_data.NUM_TEAMS, self.schedule_data.NUM_ROOMS),
            PRACTICE: self.calculate_minimum_slots_required(
                self.schedule_data.NUM_TEAMS,
                self.schedule_data.num_tables_and_sides,
                PRACTICE,
            ),
            TABLE: self.calculate_minimum_slots_required(
                self.schedule_data.NUM_TEAMS,
                self.schedule_data.num_tables_and_sides,
                TABLE,
            ),
        }

    def update_round_type_durations(self):
        """
        Update the duration for each round type.
        
        """
        self.available_practice_duration = TimeUtilities.time_to_minutes(self.PRACTICE_ROUNDS_STOP_TIME) - TimeUtilities.time_to_minutes(
            self.PRACTICE_ROUNDS_START_TIME
        )
        self.available_table_duration = TimeUtilities.time_to_minutes(self.TABLE_ROUNDS_STOP_TIME) - TimeUtilities.time_to_minutes(
            self.TABLE_ROUNDS_START_TIME
        )
        self.ROUND_TYPE_DURATIONS = {
            JUDGING     : 45,  # Fixed duration for judging rounds TODO
            PRACTICE    : round(self.available_practice_duration / self.MINIMUM_SLOTS_REQUIRED[PRACTICE]),
            TABLE       : round(self.available_table_duration    / self.MINIMUM_SLOTS_REQUIRED[TABLE]),
        }
