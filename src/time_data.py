from datetime import datetime, timedelta

class TimeData:
    def __init__(self, schedule_data):
        self.scheduleData = schedule_data

        self.start_time_judging_rounds = "08:00"
        self.start_time_practice_rounds = "09:00"
        self.start_time_break = "12:00"
        self.start_time_table_rounds = "13:30"
        self.stop_time_table_rounds = "16:21"
        self.min_slots_required = {
            "judging": 0,
            "practice": 0,
            "table": 0,
        }
        self.practice_duration_available = 0
        self.table_duration_available = 0
        self.round_durations = {
            "judging": 45,
            "practice": 0,
            "table": 0,
        }
        self.judging_start_times = []
        self.practice_start_times = []
        self.table_start_times = []
        self.time_slots = {
            "judging": [],
            "practice": [],
            "table": [],
        }
        self.update_time_data()

    def calculate_min_slots_required(self, num_teams, divisor, round_type=None):
        if round_type:
            num_teams *= self.scheduleData.round_types_per_team[round_type]
        slots_check = num_teams % divisor
        if slots_check == 0:
            return num_teams // divisor
        return (num_teams // divisor) + 1

    def time_to_minutes(self, time_str):
        time = datetime.strptime(time_str, "%H:%M")
        return time.hour * 60 + time.minute

    def generate_start_times(self, start_time, num_slots, slot_length):
        start_times = []
        current_time = start_time
        for _ in range(num_slots):
            start_times.append(current_time)
            current_time = self.add_minutes_to_time(current_time, slot_length)
        return start_times

    def add_minutes_to_time(self, time_str, minutes):
        start_time = datetime.strptime(time_str, "%H:%M")
        end_time = start_time + timedelta(minutes=minutes)
        return end_time.strftime("%H:%M")

    def calculate_end_times(self, start_times, duration):
        end_times = []
        for start_time in start_times:
            end_time = self.add_minutes_to_time(start_time, duration)
            end_times.append((start_time, end_time))
        return end_times

    def adjust_rounds_time_slots(self, round_type):
        # Calculate initial end times for table rounds
        if round_type == "practice":
            start_time = self.start_time_practice_rounds
            start_times = self.practice_start_times
            current_time = start_time
            end_time = self.start_time_break
            time_length = self.round_durations["practice"]
            available_duration = self.practice_duration_available

        if round_type == "table":
            start_time = self.start_time_table_rounds
            start_times = self.table_start_times
            current_time = start_time
            end_time = self.stop_time_table_rounds
            time_length = self.round_durations["table"]
            available_duration = self.table_duration_available

        time_slots_round = self.calculate_end_times(start_times, time_length)
        # Loop to adjust the time length for table rounds
        while time_slots_round[-1][-1] > end_time:
            self.min_slots_required[round_type] += 1
            time_length = round(available_duration / self.min_slots_required[round_type], 0)  # Ensure rounding to nearest whole number
            # Recalculate start times based on the new duration
            start_times = [start_time]
            current_time = start_time
            for _ in range(self.min_slots_required[round_type] - 1):
                current_time = self.add_minutes_to_time(current_time, time_length)
                start_times.append(current_time)
            # Recalculate the end times with the updated duration
            time_slots_round = self.calculate_end_times(start_times, time_length)
        return time_slots_round

    def time_overlaps(self, slot1, slot2):
        format_str = "%H:%M"  # Time format
        start1, end1 = map(lambda x: datetime.strptime(x, format_str), slot1)
        start2, end2 = map(lambda x: datetime.strptime(x, format_str), slot2)
        return max(start1, start2) < min(end1, end2)

    def update_time_data(self):
        # Calculate Minimum Time Slots Required
        self.min_slots_required = {
            "judging": self.calculate_min_slots_required(self.scheduleData.num_teams, self.scheduleData.num_rooms),
            "practice": self.calculate_min_slots_required(self.scheduleData.num_teams, self.scheduleData.num_tables_and_sides, "practice"),
            "table": self.calculate_min_slots_required(self.scheduleData.num_teams, self.scheduleData.num_tables_and_sides, "table"),
        }

        # Calculate the duration available for practice and table rounds in
        self.practice_duration_available = self.time_to_minutes(self.start_time_break) - self.time_to_minutes(self.start_time_practice_rounds)
        self.table_duration_available = self.time_to_minutes(self.stop_time_table_rounds) - self.time_to_minutes(self.start_time_table_rounds)

        # Initialize the round_durations dictionary
        self.round_durations = {
            "judging": 45,  # Fixed duration
            "practice": round(self.practice_duration_available / self.min_slots_required["practice"]),
            "table": round(self.table_duration_available / self.min_slots_required["table"]),
        }

        # Generate Start Times
        self.judging_start_times = self.generate_start_times(self.start_time_judging_rounds, self.min_slots_required["judging"], self.round_durations["judging"])
        self.practice_start_times = self.generate_start_times(self.start_time_practice_rounds, self.min_slots_required["practice"], self.round_durations["practice"])
        self.table_start_times = self.generate_start_times(self.start_time_table_rounds, self.min_slots_required["table"], self.round_durations["table"])

        # Create the TIME_SLOTS dictionary with (start_time, end_time) tuples
        self.time_slots = {
            "judging": self.calculate_end_times(self.judging_start_times, self.round_durations["judging"]),
            "practice": self.adjust_rounds_time_slots("practice"),
            "table": self.adjust_rounds_time_slots("table"),
        }
