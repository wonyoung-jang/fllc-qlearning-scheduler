"""This module contains the StartTimeGenerator class."""
from .time_utilities import TimeUtilities


class StartTimeGenerator:
    """Class for generating start times for rounds."""

    @staticmethod
    def generate_start_times_for_round(start_time, num_slots, slot_length):
        """Generate start times for a given round type."""
        start_times = []
        current_time = start_time
        for _ in range(num_slots):
            start_times.append(current_time)
            current_time = TimeUtilities.add_minutes_to_time(current_time, slot_length)
        return start_times

    def generate_start_times(self, time_data):
        """Generate start times for each round type."""
        time_data.judging_round_start_times = self.generate_start_times_for_round(
            time_data.judging_rounds_start_time,
            time_data.minimum_slots_required["judging"],
            time_data.round_type_durations["judging"],
        )
        time_data.practice_round_start_times = self.generate_start_times_for_round(
            time_data.practice_rounds_start_time,
            time_data.minimum_slots_required["practice"],
            time_data.round_type_durations["practice"],
        )
        time_data.table_round_start_times = self.generate_start_times_for_round(
            time_data.table_rounds_start_time,
            time_data.minimum_slots_required["table"],
            time_data.round_type_durations["table"],
        )
