from datetime import datetime, timedelta
import config

FORMAT = config.FormatsConfig()
TIME = config.TimeDataDefaultConfig()

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

def time_overlaps(slot1, slot2):
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
