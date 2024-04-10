from datetime import datetime, timedelta
import config

TIME = config.TimeDataDefaultConfig()
FORMAT = config.FormatsConfig()


# General Time Functions
def time_to_minutes(time_str):
    """
    Convert time string to minutes.

    Args:
        time_str (str): Time string in the format HH:MM.

    Returns:
        int: Time in minutes.

    """
    # Convert time string to datetime object
    try:
        time = datetime.strptime(time_str, FORMAT.TIME_FORMAT)
        return time.hour * TIME.MINUTES_PER_HOUR + time.minute
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str}. Expected format: HH:MM")


def add_minutes_to_time(time_str, minutes):
    """
    Add minutes to a time string.

    Args:
        time_str (str): Time string in the format HH:MM.
        minutes (int): Number of minutes to add.

    Returns:
        str: Time string in the format HH:MM.

    """
    try:
        start_time = datetime.strptime(time_str, FORMAT.TIME_FORMAT)
        end_time = start_time + timedelta(minutes=minutes)
        return end_time.strftime(FORMAT.TIME_FORMAT)
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str}. Expected format: HH:MM")


def is_time_overlaps(slot1, slot2):
    """
    Check if two time slots overlap.

    Args:
        slot1 (list): List of two time strings in the format HH:MM.
        slot2 (list): List of two time strings in the format HH:MM.

    Returns:
        bool: True if the time slots overlap, False otherwise.

    """
    format_str = FORMAT.TIME_FORMAT  # Time format
    start1, end1 = map(lambda x: datetime.strptime(x, format_str), slot1)
    start2, end2 = map(lambda x: datetime.strptime(x, format_str), slot2)
    return max(start1, start2) < min(end1, end2)


# Schedule Specific
def generate_start_times_for_round(start_time, num_slots, slot_length):
    """
    Generate start times for a given round type.

    Args:
        start_time (str): Start time in the format HH:MM.
        num_slots (int): Number of slots to generate.
        slot_length (int): Length of each slot in minutes.

    Returns:
        list: List of start times in the format HH:MM.

    """
    start_times = []
    current_time = start_time

    for _ in range(num_slots):
        start_times.append(current_time)
        current_time = add_minutes_to_time(current_time, slot_length)

    return start_times


def generate_end_times_for_round(start_times, duration):
    """
    Calculate the end times for a given list of start times and duration.

    Args:
        start_times (list): List of start times in the format HH:MM.
        duration (int): Duration of each slot in minutes.

    Returns:
        list: List of tuples containing the start and end times in the format (HH:MM, HH:MM).

    """
    end_times = []

    for start_time in start_times:
        end_time = add_minutes_to_time(start_time, duration)
        end_times.append((start_time, end_time))

    return end_times
