"""Time utilities for the FLLC Scheduler."""

from datetime import datetime, timedelta
from typing import Generator


def time_to_minutes(time_str: str) -> int:
    """
    Convert a time string in "HH:MM" format to the total number of minutes.

    Args:
        time_str (str): The time string in "HH:MM" format.
    Returns:
        int: The total number of minutes represented by the time string.
    """
    t = datetime.strptime(time_str, "%H:%M")
    return t.hour * 60 + t.minute


def add_minutes_to_time(time_str: str, minutes: int) -> str:
    """
    Add a specified number of minutes to a given time string.

    Args:
        time_str (str): The starting time in "HH:MM" format.
        minutes (int): The number of minutes to add.
    Returns:
        str: The resulting time in "HH:MM" format after adding the specified minutes.
    """
    start = datetime.strptime(time_str, "%H:%M")
    end = start + timedelta(minutes=minutes)
    return end.strftime("%H:%M")


def calculate_end_times(start_times: list[str], duration: int) -> Generator[tuple[str, str], None, None]:
    """
    Calculate end times for a list of start times given a fixed duration.

    Args:
        start_times (list[str]): A list of start times in "HH:MM" format.
        duration (int): The duration in minutes for each time slot.
    Returns:
        Generator[tuple[str, str], None, None]: A generator yielding tuples of start and end times.
    """
    for start in start_times:
        end = add_minutes_to_time(start, duration)
        yield (start, end)


def generate_start_times(start_time: str, num_slots: int, slot_length: int) -> list[str]:
    """
    Generate a list of start times for a given number of time slots.

    Args:
        start_time (str): The starting time in "HH:MM" format.
        num_slots (int): The number of time slots to generate.
        slot_length (int): The length of each time slot in minutes.
    Returns:
        list[str]: A list of start times in "HH:MM" format.
    """
    start_times = []
    current_time = start_time
    for _ in range(num_slots):
        start_times.append(current_time)
        current_time = add_minutes_to_time(current_time, slot_length)
    return start_times
