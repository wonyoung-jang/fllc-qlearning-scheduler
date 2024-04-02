"""This module contains utility functions for time operations."""
from datetime import datetime, timedelta
from config import Config 

TIME_FORMAT = Config.TIME_FORMAT


class TimeUtilities:
    """Utility class for time-related operations."""

    @staticmethod
    def time_to_minutes(time_str):
        """Convert time string to minutes."""
        try:
            time = datetime.strptime(time_str, TIME_FORMAT)
            return time.hour * 60 + time.minute
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}. Expected format: HH:MM")

    @staticmethod
    def add_minutes_to_time(time_str, minutes):
        """Add minutes to a time string."""
        try:
            start_time = datetime.strptime(time_str, TIME_FORMAT)
            end_time = start_time + timedelta(minutes=minutes)
            return end_time.strftime(TIME_FORMAT)
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}. Expected format: HH:MM")

    @staticmethod
    def time_overlaps(slot1, slot2):
        """Check if two time slots overlap."""
        format_str = TIME_FORMAT  # Time format
        start1, end1 = map(lambda x: datetime.strptime(x, format_str), slot1)
        start2, end2 = map(lambda x: datetime.strptime(x, format_str), slot2)
        return max(start1, start2) < min(end1, end2)
