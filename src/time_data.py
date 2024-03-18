"""This module is responsible for generating the time slots for each round type based on the number of teams and rooms/tables/sides."""
from datetime import datetime, timedelta


class TimeData:
    """Class to store data for scheduling rounds and tables."""

    def __str__(self):
        """Return string representation of TimeData object."""
        return f"TimeData(judging_rounds_start_time={self.judging_rounds_start_time}, practice_rounds_start_time={self.practice_rounds_start_time}, practice_rounds_stop_time={self.practice_rounds_stop_time}, table_rounds_start_time={self.table_rounds_start_time}, table_rounds_stop_time={self.table_rounds_stop_time}, minimum_slots_required={self.minimum_slots_required}, available_practice_duration={self.available_practice_duration}, available_table_duration={self.available_table_duration}, round_type_durations={self.round_type_durations}, judging_round_start_times={self.judging_round_start_times}, practice_round_start_times={self.practice_round_start_times}, table_round_start_times={self.table_round_start_times}, round_type_time_slots={self.round_type_time_slots})"

    def __repr__(self):
        """Return string representation of TimeData object."""
        return self.__str__()

    def __init__(self, schedule_data):
        """Initialize TimeData object."""
        self.schedule_data = schedule_data

        self.judging_rounds_start_time = "08:00"
        self.practice_rounds_start_time = "09:00"
        self.practice_rounds_stop_time = "12:00"
        self.table_rounds_start_time = "13:30"
        self.table_rounds_stop_time = "16:21"

        self.minimum_slots_required = {
            "judging": 0,
            "practice": 0,
            "table": 0,
        }

        self.available_practice_duration = 0
        self.available_table_duration = 0

        self.round_type_durations = {
            "judging": 45,
            "practice": 0,
            "table": 0,
        }

        self.judging_round_start_times = []
        self.practice_round_start_times = []
        self.table_round_start_times = []

        self.round_type_time_slots = {
            "judging": [],
            "practice": [],
            "table": [],
        }

        self.update_time_data()

    def calculate_minimum_slots_required(self, num_teams, divisor, round_type=None):
        """Calculate the minimum number of slots required for a given number of teams and divisor."""
        
        # Check for division by zero
        if divisor == 0:
            raise ValueError("Divisor cannot be zero.")

        # Adjust the number of teams based on the round type
        if round_type:
            num_teams *= self.schedule_data.round_types_per_team[round_type]
        
        # Calculate the number of slots required
        slots_check = num_teams % divisor

        # Return the number of slots required
        if slots_check == 0:
            return num_teams // divisor
        else:
            return (num_teams // divisor) + 1

    def time_to_minutes(self, time_str): 
        """Convert time string to minutes."""
        
        # Convert time string to datetime object
        try:
            time = datetime.strptime(time_str, "%H:%M")
            return time.hour * 60 + time.minute
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}. Expected format: HH:MM")
        
    def generate_start_times_for_round(self, start_time, num_slots, slot_length): 
        """Generate start times for a given round type."""
        start_times = []
        current_time = start_time

        for _ in range(num_slots):
            start_times.append(current_time)
            current_time = self.add_minutes_to_time(current_time, slot_length)

        return start_times

    def add_minutes_to_time(self, time_str, minutes):
        """Add minutes to a time string."""
        try:
            start_time = datetime.strptime(time_str, "%H:%M")
            end_time = start_time + timedelta(minutes=minutes)
            return end_time.strftime("%H:%M")
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}. Expected format: HH:MM")
        
    def calculate_end_times(self, start_times, duration):
        """Calculate the end times for a given list of start times and duration."""
        end_times = []

        for start_time in start_times:
            end_time = self.add_minutes_to_time(start_time, duration)
            end_times.append((start_time, end_time))

        return end_times

    def adjust_rounds_round_type_time_slots(self, round_type):
        """Adjust the time slots for the given round type."""
        if round_type not in ["practice", "table"]:
            raise ValueError(f"Invalid round type: {round_type}. Expected 'practice' or 'table'")
        
        # Calculate initial end times for table rounds
        if round_type == "practice":
            start_time = self.practice_rounds_start_time
            start_times = self.practice_round_start_times
            current_time = start_time
            end_time = self.practice_rounds_stop_time
            time_length = self.round_type_durations["practice"]
            available_duration = self.available_practice_duration

        if round_type == "table":
            start_time = self.table_rounds_start_time
            start_times = self.table_round_start_times
            current_time = start_time
            end_time = self.table_rounds_stop_time
            time_length = self.round_type_durations["table"]
            available_duration = self.available_table_duration

        round_type_time_slots_round = self.calculate_end_times(start_times, time_length)

        # Loop to adjust the time length for table rounds
        while round_type_time_slots_round[-1][-1] > end_time:
            self.minimum_slots_required[round_type] += 1
            # Ensure rounding to nearest whole number
            time_length = round(available_duration / self.minimum_slots_required[round_type], 0)
            # Recalculate start times based on the new duration
            start_times = [start_time]
            current_time = start_time

            for _ in range(self.minimum_slots_required[round_type] - 1):
                current_time = self.add_minutes_to_time(current_time, time_length)
                start_times.append(current_time)

            # Recalculate the end times with the updated duration
            round_type_time_slots_round = self.calculate_end_times(start_times, time_length)

        return round_type_time_slots_round

    def time_overlaps(self, slot1, slot2): 
        """Check if two time slots overlap."""
        format_str = "%H:%M"  # Time format
        start1, end1 = map(lambda x: datetime.strptime(x, format_str), slot1)
        start2, end2 = map(lambda x: datetime.strptime(x, format_str), slot2)
        return max(start1, start2) < min(end1, end2)

    def update_time_data(self): 
        """Update the time data."""
        self.update_minimum_slots_required()
        self.update_round_type_durations()
        self.generate_start_times()
        self.create_round_type_time_slots()

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
        self.available_practice_duration = self.time_to_minutes(self.practice_rounds_stop_time) - self.time_to_minutes(
            self.practice_rounds_start_time
        )
        self.available_table_duration = self.time_to_minutes(self.table_rounds_stop_time) - self.time_to_minutes(
            self.table_rounds_start_time
        )

        self.round_type_durations = {
            "judging": 45,  # Fixed duration
            "practice": round(self.available_practice_duration / self.minimum_slots_required["practice"]),
            "table": round(self.available_table_duration / self.minimum_slots_required["table"]),
        }

    def generate_start_times(self): 
        """Generate start times for each round type."""
        self.judging_round_start_times = self.generate_start_times_for_round(
            self.judging_rounds_start_time,
            self.minimum_slots_required["judging"],
            self.round_type_durations["judging"],
        )
        self.practice_round_start_times = self.generate_start_times_for_round(
            self.practice_rounds_start_time,
            self.minimum_slots_required["practice"],
            self.round_type_durations["practice"],
        )
        self.table_round_start_times = self.generate_start_times_for_round(
            self.table_rounds_start_time,
            self.minimum_slots_required["table"],
            self.round_type_durations["table"],
        )

    def create_round_type_time_slots(self): 
        """Create time slots for each round type."""
        self.round_type_time_slots = {
            "judging": self.calculate_end_times(self.judging_round_start_times, self.round_type_durations["judging"]),
            "practice": self.adjust_rounds_round_type_time_slots("practice"),
            "table": self.adjust_rounds_round_type_time_slots("table"),
        }
