from datetime import datetime, timedelta
import config

TIME = config.TimeDataDefaultConfig()
FORMAT = config.FormatsConfig()
KEY = config.KeysConfig()
VALUE = config.ValuesConfig()


# General Time Functions
def time_to_minutes(time_str):
    """
    Convert time string to minutes.

    Args:
        time_str (str)  : Time string in the format HH:MM.

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
        time_str (str)  : Time string in the format HH:MM.
        minutes (int)   : Number of minutes to add.

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


# Tournament 
def calculate_minimum_slots_required(num_teams, divisor, round_types_per_team, round_type=None):
    """
    Calculate the minimum number of slots required for a given number of teams and divisor.

    Args:
        num_teams (int): Number of teams.
        divisor (int): Divisor for the number of slots.
        round_types_per_team (dict): Number of rounds for each team, per type.

    Returns:
        int: Minimum number of slots required.
        
    """
    # Check for division by zero
    if divisor == 0:
        raise ValueError("Divisor cannot be zero.")

    # Adjust the number of teams based on the round type
    if round_type:
        num_teams *= round_types_per_team[round_type]

    # Calculate the number of slots required
    slots_check = num_teams % divisor

    # Return the number of slots required
    if slots_check == 0:
        return num_teams // divisor
    else:
        return (num_teams // divisor) + 1


def adjust_rounds_round_type_time_slots(
    round_type,
    practice_rounds_start_time,
    practice_round_start_times,
    practice_rounds_stop_time,
    available_practice_duration,
    round_type_durations,
    table_rounds_start_time,
    table_round_start_times,
    table_rounds_stop_time,
    available_table_duration,
    minimum_slots_required):
    """
    Adjust the time slots for the given round type.
    
    Args:
        round_type (str): Round type to adjust.
        

    Returns:
        tuple: Tuple containing the adjusted start times and end times for the given round type.

    """
    if round_type not in [KEY.PRACTICE, KEY.TABLE]:
        raise ValueError(
            f"Invalid round type: {round_type}. Expected 'practice' or 'table'"
        )

    # Calculate initial end times for table rounds
    if round_type == KEY.PRACTICE:
        start_time = practice_rounds_start_time
        start_times = practice_round_start_times
        current_time = start_time
        end_time = practice_rounds_stop_time
        time_length = round_type_durations[KEY.PRACTICE]
        available_duration = available_practice_duration

    if round_type == KEY.TABLE:
        start_time = table_rounds_start_time
        start_times = table_round_start_times
        current_time = start_time
        end_time = table_rounds_stop_time
        time_length = round_type_durations[KEY.TABLE]
        available_duration = available_table_duration

    round_type_time_slots_round = generate_end_times_for_round(
        start_times, time_length
    )

    # Loop to adjust the time length for table rounds
    while round_type_time_slots_round[-1][-1] > end_time:
        minimum_slots_required[round_type] += 1
        # Ensure rounding to nearest whole number
        time_length = round(
            available_duration / minimum_slots_required[round_type], 0
        )
        # Recalculate start times based on the new duration
        start_times = [start_time]
        current_time = start_time

        for _ in range(minimum_slots_required[round_type] - 1):
            current_time = add_minutes_to_time(current_time, time_length)
            start_times.append(current_time)

        # Recalculate the end times with the updated duration
        round_type_time_slots_round = generate_end_times_for_round(
            start_times, time_length
        )

    return round_type_time_slots_round


# Data structures that were functions 
"""minimum_slots_required = {
        KEY.JUDGING: calculate_minimum_slots_required(
            num_teams, num_rooms
        ),
        KEY.PRACTICE: calculate_minimum_slots_required(
            num_teams,
            num_tables_and_sides,
            KEY.PRACTICE,
        ),
        KEY.TABLE: calculate_minimum_slots_required(
            num_teams,
            num_tables_and_sides,
            KEY.TABLE,
        ),
    }
"""
"""judging_round_start_times = generate_start_times_for_round(
        judging_rounds_start_time,
        minimum_slots_required[KEY.JUDGING],
        round_type_durations[KEY.JUDGING],
    )
    practice_round_start_times = generate_start_times_for_round(
        practice_rounds_start_time,
        minimum_slots_required[KEY.PRACTICE],
        round_type_durations[KEY.PRACTICE],
    )
    table_round_start_times = generate_start_times_for_round(
        table_rounds_start_time,
        minimum_slots_required[KEY.TABLE],
        round_type_durations[KEY.TABLE],
    )
"""
"""round_type_time_slots = {
        KEY.JUDGING: generate_end_times_for_round(
            judging_round_start_times, 
            round_type_durations[KEY.JUDGING]
        ),
        KEY.PRACTICE: adjust_rounds_round_type_time_slots(KEY.PRACTICE),
        KEY.TABLE: adjust_rounds_round_type_time_slots(KEY.TABLE),
    }
"""
"""available_practice_duration = time_to_minutes(
        practice_rounds_stop_time
    ) - time_to_minutes(practice_rounds_start_time)
    
    available_table_duration = time_to_minutes(
        table_rounds_stop_time
    ) - time_to_minutes(table_rounds_start_time)
    
    round_type_durations = {
        KEY.JUDGING: VALUE.ROUND_DURATION_JUDGING,  # Fixed duration
        KEY.PRACTICE: round(
            available_practice_duration
            / minimum_slots_required[KEY.PRACTICE]
        ),
        KEY.TABLE: round(
            available_table_duration / minimum_slots_required[KEY.TABLE]
        ),
    }
"""
