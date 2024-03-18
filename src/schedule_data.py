"""This module is responsible for generating the time slots for each round type based on the number of teams and rooms/tables/sides."""

class ScheduleData:
    """Class to store data for scheduling rounds and tables."""

    def __init__(self, num_teams=42, num_rooms=7, num_tables=4):
        """Initialize ScheduleData object."""
        self.num_teams = num_teams
        self.num_rooms = num_rooms
        self.num_tables = num_tables
        self.round_types_per_team = {"judging": 1, "practice": 2, "table": 3}
        self.num_tables_and_sides = self.num_tables * 2
        self.teams, self.rooms, self.tables = self.initialize_teams_rooms_tables()

    def __str__(self):
        """Return string representation of ScheduleData object."""
        return f"ScheduleData(num_teams={self.num_teams}, num_rooms={self.num_rooms}, num_tables={self.num_tables})"

    def __repr__(self):
        """Return string representation of ScheduleData object."""
        return self.__str__()

    def initialize_teams_rooms_tables(self):
        """Initialize teams, rooms, and tables."""
        self.teams = {
            team_id: {
                "team_id": team_id,
                "scheduled_round_types": {"judging": 0, "practice": 0, "table": 0},
                "scheduled_times": [],
                "scheduled_tables": [],
                "scheduled_opponents": [],
                "scheduled_time_table_pairs": [],
            }
            for team_id in range(1, self.num_teams + 1)
        }

        self.rooms = {
            room_id: {
                "location_type": "room",
                "location_id": room_id,
                "table_side": None,
                "scheduled_teams": [],
            } for room_id in range(1, self.num_rooms + 1)
        }

        table_ids = [chr(65 + i) for i in range(self.num_tables)]
        self.tables = {
            (table_id, side): {
                "location_type": "table",
                "location_id": table_id,
                "table_side": side,
                "scheduled_teams": [],
                "scheduled_times": [],
            } for table_id in table_ids for side in [1, 2]
        }

        return self.teams, self.rooms, self.tables
    