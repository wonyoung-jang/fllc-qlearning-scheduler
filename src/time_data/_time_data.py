"""This module is responsible for generating the time slots for each round type based on the number of teams and rooms/tables/sides."""
from datetime import datetime, timedelta
from .time_utilities import TimeUtilities
from .start_time_generator import StartTimeGenerator
from .time_slot_creator import TimeSlotCreator
from config import Config

class TimeData:
    """Class to store data for scheduling rounds and tables."""

    def __init__(self, schedule_data):
        """Initialize TimeData object."""
        self.schedule_data = schedule_data
        
        self.judging_rounds_start_time = Config.judging_rounds_start_time
        self.practice_rounds_start_time = Config.practice_rounds_start_time
        self.practice_rounds_stop_time = Config.practice_rounds_stop_time
        self.table_rounds_start_time = Config.table_rounds_start_time
        self.table_rounds_stop_time = Config.table_rounds_stop_time
        self.minimum_slots_required = Config.minimum_slots_required
            
            
        self.available_practice_duration = 0
        self.available_table_duration = 0
        
        self.round_type_durations = Config.round_type_durations
        
        self.judging_round_start_times = []
        self.practice_round_start_times = []
        self.table_round_start_times = []
        self.round_type_time_slots = {
            "judging": [],
            "practice": [],
            "table": [],
        }
        
        self.update_time_data()

    def __str__(self):
        """Return string representation of TimeData object."""
        return f"TimeData(judging_rounds_start_time={self.judging_rounds_start_time}, practice_rounds_start_time={self.practice_rounds_start_time}, practice_rounds_stop_time={self.practice_rounds_stop_time}, table_rounds_start_time={self.table_rounds_start_time}, table_rounds_stop_time={self.table_rounds_stop_time}, minimum_slots_required={self.minimum_slots_required}, available_practice_duration={self.available_practice_duration}, available_table_duration={self.available_table_duration}, round_type_durations={self.round_type_durations}, judging_round_start_times={self.judging_round_start_times}, practice_round_start_times={self.practice_round_start_times}, table_round_start_times={self.table_round_start_times}, round_type_time_slots={self.round_type_time_slots})"

    def __repr__(self):
        """Return string representation of TimeData object."""
        return self.__str__()

    def calculate_minimum_slots_required(self, num_teams, divisor, round_type=None):
        """Calculate the minimum number of slots required for a given number of teams and divisor."""
        if divisor == 0:
            raise ValueError("Divisor cannot be zero.")
        if round_type:
            num_teams *= self.schedule_data.round_types_per_team[round_type]
        slots_check = num_teams % divisor
        if slots_check == 0:
            return num_teams // divisor
        else:
            return (num_teams // divisor) + 1

    def update_time_data(self):
        """Update the time data."""
        self.update_minimum_slots_required()
        self.update_round_type_durations()
        start_time_generator = StartTimeGenerator()
        start_time_generator.generate_start_times(self)
        time_slot_creator = TimeSlotCreator()
        time_slot_creator.create_round_type_time_slots(self)

    def update_minimum_slots_required(self):
        """Update the minimum number of slots required for each round type."""
        self.minimum_slots_required = {
            "judging": self.calculate_minimum_slots_required(self.schedule_data.num_teams, self.schedule_data.num_rooms),
            "practice": self.calculate_minimum_slots_required(
                self.schedule_data.num_teams,
                self.schedule_data.num_tables_and_sides,
                "practice",
            ),
            "table": self.calculate_minimum_slots_required(
                self.schedule_data.num_teams,
                self.schedule_data.num_tables_and_sides,
                "table",
            ),
        }

    def update_round_type_durations(self):
        """Update the duration for each round type."""
        self.available_practice_duration = TimeUtilities.time_to_minutes(self.practice_rounds_stop_time) - TimeUtilities.time_to_minutes(
            self.practice_rounds_start_time
        )
        self.available_table_duration = TimeUtilities.time_to_minutes(self.table_rounds_stop_time) - TimeUtilities.time_to_minutes(
            self.table_rounds_start_time
        )
        self.round_type_durations = {
            "judging": 45,  # Fixed duration
            "practice": round(self.available_practice_duration / self.minimum_slots_required["practice"]),
            "table": round(self.available_table_duration / self.minimum_slots_required["table"]),
        }