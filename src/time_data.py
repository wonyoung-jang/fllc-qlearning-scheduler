from config import KeysConfig, ValuesConfig, TimeDataDefaultConfig, FormatsConfig
from utilities_time import *

KEY = KeysConfig()
VALUE = ValuesConfig()
FORMAT = FormatsConfig()
TIME = TimeDataDefaultConfig()

# PURE



# OBJECT
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
        self.round_type_durations = TIME.ROUND_TYPE_DURATIONS
        self.round_type_time_slots = TIME.ROUND_TYPE_TIME_SLOTS

        self.available_practice_duration = 0
        self.available_table_duration = 0

        self.judging_round_start_times = []
        self.practice_round_start_times = []
        self.table_round_start_times = []


        self.update_time_data()


    def update_time_data(self):
        """
        Update the time data.

        """
        self.update_minimum_slots_required()
        self.update_round_type_durations()
        self.generate_start_times()
        self.create_round_type_time_slots()


    # TODO DEL
    def calculate_minimum_slots_required(
        self, num_teams, divisor, round_type=None
    ):
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

    # TODO DEL
    def adjust_rounds_round_type_time_slots(self, round_type):
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

    # TODO DEL
    def update_minimum_slots_required(self): 
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

    # TODO DEL
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

    # TODO DEL
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

    # TODO DEL
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
