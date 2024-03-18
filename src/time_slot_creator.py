"""This module contains the TimeSlotCreator class."""
from time_utilities import TimeUtilities


class TimeSlotCreator:
    """Class for creating time slots for rounds."""

    @staticmethod
    def calculate_end_times(start_times, duration):
        """Calculate the end times for a given list of start times and duration."""
        end_times = []
        for start_time in start_times:
            end_time = TimeUtilities.add_minutes_to_time(start_time, duration)
            end_times.append((start_time, end_time))
        return end_times

    def adjust_rounds_round_type_time_slots(self, round_type, time_data):
        """Adjust the time slots for the given round type."""
        if round_type not in ["practice", "table"]:
            raise ValueError(f"Invalid round type: {round_type}. Expected 'practice' or 'table'")
        if round_type == "practice":
            start_time = time_data.practice_rounds_start_time
            start_times = time_data.practice_round_start_times
            current_time = start_time
            end_time = time_data.practice_rounds_stop_time
            time_length = time_data.round_type_durations["practice"]
            available_duration = time_data.available_practice_duration
        if round_type == "table":
            start_time = time_data.table_rounds_start_time
            start_times = time_data.table_round_start_times
            current_time = start_time
            end_time = time_data.table_rounds_stop_time
            time_length = time_data.round_type_durations["table"]
            available_duration = time_data.available_table_duration
        round_type_time_slots_round = self.calculate_end_times(start_times, time_length)
        while round_type_time_slots_round[-1][-1] > end_time:
            time_data.minimum_slots_required[round_type] += 1
            time_length = round(available_duration / time_data.minimum_slots_required[round_type], 0)
            start_times = [start_time]
            current_time = start_time
            for _ in range(time_data.minimum_slots_required[round_type] - 1):
                current_time = TimeUtilities.add_minutes_to_time(current_time, time_length)
                start_times.append(current_time)
            round_type_time_slots_round = self.calculate_end_times(start_times, time_length)
        return round_type_time_slots_round

    def create_round_type_time_slots(self, time_data):
        """Create time slots for each round type."""
        time_data.round_type_time_slots = {
            "judging": self.calculate_end_times(time_data.judging_round_start_times, time_data.round_type_durations["judging"]),
            "practice": self.adjust_rounds_round_type_time_slots("practice", time_data),
            "table": self.adjust_rounds_round_type_time_slots("table", time_data),
        }
