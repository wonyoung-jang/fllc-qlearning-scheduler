from datetime import datetime, timedelta
from config import KeysConfig, ValuesConfig, TimeDataDefaultConfig, FormatsConfig
from utilities_time import *

KEY = KeysConfig()
VALUE = ValuesConfig()
FORMAT = FormatsConfig()
TIME = TimeDataDefaultConfig()


##########################################################################################
def update_round_type_durations(
    practice_rounds_stop_time,
    practice_rounds_start_time,
    table_rounds_stop_time,
    table_rounds_start_time,
    minimum_slots_required,
):
    """
    Update the duration for each round type.

    """
    available_practice_duration = time_to_minutes(
        practice_rounds_stop_time
    ) - time_to_minutes(practice_rounds_start_time)
    available_table_duration = time_to_minutes(
        table_rounds_stop_time
    ) - time_to_minutes(table_rounds_start_time)
    round_type_durations = {
        KEY.JUDGING: VALUE.ROUND_DURATION_JUDGING,  # Fixed duration
        KEY.PRACTICE: round(
            available_practice_duration / minimum_slots_required[KEY.PRACTICE]
        ),
        KEY.TABLE: round(available_table_duration / minimum_slots_required[KEY.TABLE]),
    }

    return available_practice_duration, available_table_duration, round_type_durations


def update_minimum_slots_required(
    num_teams, num_rooms, num_tables_and_sides, round_types_per_team
):
    """
    Update the minimum number of slots required for each round type.

    """
    minimum_slots_required = {
        KEY.JUDGING: calculate_minimum_slots_required(
            num_teams, num_rooms, round_types_per_team
        ),
        KEY.PRACTICE: calculate_minimum_slots_required(
            num_teams,
            num_tables_and_sides,
            round_types_per_team,
            KEY.PRACTICE,
        ),
        KEY.TABLE: calculate_minimum_slots_required(
            num_teams,
            num_tables_and_sides,
            round_types_per_team,
            KEY.TABLE,
        ),
    }
    return minimum_slots_required


def calculate_minimum_slots_required(
    num_teams, divisor, round_types_per_team, round_type=None
):  # TODO fll
    """
    Calculate the minimum number of slots required for a given number of teams and divisor.

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


def generate_start_times(
    judging_rounds_start_time,
    practice_rounds_start_time,
    table_rounds_start_time,
    minimum_slots_required,
    round_type_durations,
):
    """
    Generate start times for each round type.

    """
    judging_round_start_times = generate_start_times_for_round(
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

    return (
        judging_round_start_times,
        practice_round_start_times,
        table_round_start_times,
    )


def create_round_type_time_slots(
    judging_round_start_times,
    practice_round_start_times,
    table_round_start_times,
    practice_rounds_start_time,
    practice_rounds_stop_time,
    available_practice_duration,
    table_rounds_start_time,
    table_rounds_stop_time,
    available_table_duration,
    minimum_slots_required,
    round_type_durations,
):
    """
    Create time slots for each round type.

    """
    round_type_time_slots = {
        KEY.JUDGING: generate_end_times_for_round(
            judging_round_start_times, round_type_durations[KEY.JUDGING]
        ),
        KEY.PRACTICE: adjust_rounds_round_type_time_slots(
            practice_round_start_times,
            practice_rounds_start_time,
            practice_rounds_stop_time,
            round_type_durations[KEY.PRACTICE],
            available_practice_duration,
            minimum_slots_required[KEY.PRACTICE],
        ),
        KEY.TABLE: adjust_rounds_round_type_time_slots(
            table_round_start_times,
            table_rounds_start_time,
            table_rounds_stop_time,
            round_type_durations[KEY.TABLE],
            available_table_duration,
            minimum_slots_required[KEY.TABLE],
        ),
    }

    return round_type_time_slots


def adjust_rounds_round_type_time_slots(*args):
    """
    Adjust the time slots for the given round type.

    """
    # Calculate initial end times for table rounds
    start_times = args[0]
    start_time = args[1]
    current_time = start_time
    end_time = args[2]
    time_length = args[3]
    available_duration = args[4]
    minimum_slots_required = args[5]

    round_type_time_slots_round = generate_end_times_for_round(start_times, time_length)

    # Loop to adjust the time length for table rounds
    while round_type_time_slots_round[-1][-1] > end_time:
        minimum_slots_required += 1
        # Ensure rounding to nearest whole number
        time_length = round(available_duration / minimum_slots_required, 0)
        # Recalculate start times based on the new duration
        start_times = [start_time]
        current_time = start_time

        for _ in range(minimum_slots_required - 1):
            current_time = add_minutes_to_time(current_time, time_length)
            start_times.append(current_time)

        # Recalculate the end times with the updated duration
        round_type_time_slots_round = generate_end_times_for_round(
            start_times, time_length
        )

    return round_type_time_slots_round


##########################################################################################
class TimeData:
    """
    Class to store data for scheduling rounds and tables.

    """

    def __init__(self, tournament_data):
        """
        Initialize TimeData object.

        """
        self.tournament_data = tournament_data

        self.judging_rounds_start_time = TIME.JUDGING_ROUNDS_START_TIME
        self.practice_rounds_start_time = TIME.PRACTICE_ROUNDS_START_TIME
        self.practice_rounds_stop_time = TIME.PRACTICE_ROUNDS_STOP_TIME
        self.table_rounds_start_time = TIME.TABLE_ROUNDS_START_TIME
        self.table_rounds_stop_time = TIME.TABLE_ROUNDS_STOP_TIME

        self.minimum_slots_required = TIME.MINIMUM_SLOTS_REQUIRED

        self.available_practice_duration = 0
        self.available_table_duration = 0

        self.round_type_durations = TIME.ROUND_TYPE_DURATIONS

        self.judging_round_start_times = []
        self.practice_round_start_times = []
        self.table_round_start_times = []

        self.round_type_time_slots = TIME.ROUND_TYPE_TIME_SLOTS

        self.update_time_data()

    def calculate_minimum_slots_required(
        self, num_teams, divisor, round_type=None
    ):  # TODO fll
        """
        Calculate the minimum number of slots required for a given number of teams and divisor.

        """
        # Check for division by zero
        if divisor == 0:
            raise ValueError("Divisor cannot be zero.")

        # Adjust the number of teams based on the round type
        if round_type:
            num_teams *= self.tournament_data.round_types_per_team[round_type]

        # Calculate the number of slots required
        slots_check = num_teams % divisor

        # Return the number of slots required
        if slots_check == 0:
            return num_teams // divisor
        else:
            return (num_teams // divisor) + 1

    def adjust_rounds_round_type_time_slots(self, round_type):  # TODO fll
        """
        Adjust the time slots for the given round type.

        """
        if round_type not in [KEY.PRACTICE, KEY.TABLE]:
            raise ValueError(
                f"Invalid round type: {round_type}. Expected 'practice' or 'table'"
            )

        # Calculate initial end times for table rounds
        if round_type == KEY.PRACTICE:
            start_time = self.practice_rounds_start_time
            start_times = self.practice_round_start_times
            current_time = start_time
            end_time = self.practice_rounds_stop_time
            time_length = self.round_type_durations[KEY.PRACTICE]
            available_duration = self.available_practice_duration

        if round_type == KEY.TABLE:
            start_time = self.table_rounds_start_time
            start_times = self.table_round_start_times
            current_time = start_time
            end_time = self.table_rounds_stop_time
            time_length = self.round_type_durations[KEY.TABLE]
            available_duration = self.available_table_duration

        round_type_time_slots_round = generate_end_times_for_round(
            start_times, time_length
        )

        # Loop to adjust the time length for table rounds
        while round_type_time_slots_round[-1][-1] > end_time:
            self.minimum_slots_required[round_type] += 1
            # Ensure rounding to nearest whole number
            time_length = round(
                available_duration / self.minimum_slots_required[round_type], 0
            )
            # Recalculate start times based on the new duration
            start_times = [start_time]
            current_time = start_time

            for _ in range(self.minimum_slots_required[round_type] - 1):
                current_time = add_minutes_to_time(current_time, time_length)
                start_times.append(current_time)

            # Recalculate the end times with the updated duration
            round_type_time_slots_round = generate_end_times_for_round(
                start_times, time_length
            )

        return round_type_time_slots_round

    # TODO Updates
    def update_time_data(self):
        """
        Update the time data.

        """
        self.update_minimum_slots_required()
        self.update_round_type_durations()
        self.generate_start_times()
        self.create_round_type_time_slots()

    def update_minimum_slots_required(self):  # TODO minimum_slots_required
        """
        Update the minimum number of slots required for each round type.

        """
        self.minimum_slots_required = {
            KEY.JUDGING: self.calculate_minimum_slots_required(
                self.tournament_data.num_teams, self.tournament_data.num_rooms
            ),
            KEY.PRACTICE: self.calculate_minimum_slots_required(
                self.tournament_data.num_teams,
                self.tournament_data.num_tables_and_sides,
                KEY.PRACTICE,
            ),
            KEY.TABLE: self.calculate_minimum_slots_required(
                self.tournament_data.num_teams,
                self.tournament_data.num_tables_and_sides,
                KEY.TABLE,
            ),
        }

    def update_round_type_durations(self):
        """
        Update the duration for each round type.

        """
        self.available_practice_duration = time_to_minutes(
            self.practice_rounds_stop_time
        ) - time_to_minutes(self.practice_rounds_start_time)
        self.available_table_duration = time_to_minutes(
            self.table_rounds_stop_time
        ) - time_to_minutes(self.table_rounds_start_time)
        self.round_type_durations = {
            KEY.JUDGING: VALUE.ROUND_DURATION_JUDGING,  # Fixed duration
            KEY.PRACTICE: round(
                self.available_practice_duration
                / self.minimum_slots_required[KEY.PRACTICE]
            ),
            KEY.TABLE: round(
                self.available_table_duration / self.minimum_slots_required[KEY.TABLE]
            ),
        }

    def generate_start_times(self):
        """
        Generate start times for each round type.

        """
        self.judging_round_start_times = generate_start_times_for_round(
            self.judging_rounds_start_time,
            self.minimum_slots_required[KEY.JUDGING],
            self.round_type_durations[KEY.JUDGING],
        )
        self.practice_round_start_times = generate_start_times_for_round(
            self.practice_rounds_start_time,
            self.minimum_slots_required[KEY.PRACTICE],
            self.round_type_durations[KEY.PRACTICE],
        )
        self.table_round_start_times = generate_start_times_for_round(
            self.table_rounds_start_time,
            self.minimum_slots_required[KEY.TABLE],
            self.round_type_durations[KEY.TABLE],
        )

    def create_round_type_time_slots(self):
        """
        Create time slots for each round type.

        """
        self.round_type_time_slots = {
            KEY.JUDGING: generate_end_times_for_round(
                self.judging_round_start_times, self.round_type_durations[KEY.JUDGING]
            ),
            KEY.PRACTICE: self.adjust_rounds_round_type_time_slots(KEY.PRACTICE),
            KEY.TABLE: self.adjust_rounds_round_type_time_slots(KEY.TABLE),
        }
