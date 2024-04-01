# TODO schedule_initializer.py
from typing import List
from config import Config
from time_data.time_utilities import TimeUtilities

JUDGING = Config.JUDGING
PRACTICE = Config.PRACTICE
TABLE = Config.TABLE
LOCATION_TYPE_ROOM = Config.LOCATION_TYPE_ROOM


class ScheduleInitializer:
    def __init__(self, schedule_data, time_data) -> None:
        """
        Initialize the schedule initializer.
        
        """
        self.schedule_data = schedule_data
        self.time_data = time_data
    
    def initialize_schedule_and_states(self) -> None:
        """
        Initialize the schedule and states for training.
        
        """
        self.schedule = self.initialize_schedule()
        self.static_states = [tuple(i) for i in self.schedule]

        self.initialize_judging_rounds()
        self.states = [tuple(i) for i in self.schedule if i[2] != JUDGING]
        self.exploration_count = 0
        self.exploitation_count = 0
        self.practice_teams_available = (
            list(self.schedule_data.teams.keys()) * self.schedule_data.ROUND_TYPE_PER_TEAM[PRACTICE]
        )
        self.table_teams_available = (
            list(self.schedule_data.teams.keys()) * self.schedule_data.ROUND_TYPE_PER_TEAM[TABLE]
        )
        self.current_schedule_length = 0
        return  (self.schedule, 
                self.states, 
                self.static_states,
                self.current_schedule_length,
                self.practice_teams_available,
                self.table_teams_available,
                self.exploration_count,
                self.exploitation_count)

    def initialize_schedule(self) -> List[List]:
        """
        Initialize the schedule for training.
        
        """
        (   self.schedule_data.teams,
            self.schedule_data.rooms,
            self.schedule_data.tables,
        ) = self.schedule_data.initialize_teams_rooms_tables()
        schedule = []
        for round_type, slots in self.time_data.round_type_time_slots.items():
            for time_start, time_end in slots:
                if round_type == JUDGING:
                    for room_id in range(1, self.schedule_data.NUM_ROOMS + 1):
                        schedule.append([time_start, time_end, round_type, LOCATION_TYPE_ROOM, room_id, None])
                else:
                    for table, details in self.schedule_data.tables.items():
                        table_id, side = table
                        schedule.append(
                            [
                                time_start,
                                time_end,
                                round_type,
                                TABLE,
                                f"{table_id}{side}",
                                None,
                            ]
                        )
        return schedule

    def initialize_judging_rounds(self) -> None:
        """
        Initialize the judging rounds for training.
        
        """
        current_team_id = list(self.schedule_data.teams.keys())[0]

        for i, schedule in enumerate(self.schedule):
            if schedule[2] == JUDGING and current_team_id <= len(list(self.schedule_data.teams.keys())):
                self.schedule[i][5] = current_team_id
                self.schedule_data.teams[current_team_id].scheduled_round_types[JUDGING] += 1
                self.schedule_data.teams[current_team_id].scheduled_times.append((schedule[0], schedule[1]))
                self.schedule_data.rooms[schedule[4]].scheduled_teams.append(current_team_id)
                current_team_id += 1

