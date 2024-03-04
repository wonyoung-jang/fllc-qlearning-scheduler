class ScheduleData:
    def __init__(self):
        self.num_teams = 42
        self.num_rooms = 7
        self.num_tables = 4
        self.round_types_per_team = {"judging": 1, "practice": 2, "table": 3}
        self.num_tables_and_sides = self.num_tables * 2
        self.teams, self.rooms, self.tables = self.initialize_teams_rooms_tables()

    def initialize_teams_rooms_tables(self):
        # Teams Dictionary
        self.teams = {}
        for team_id in range(1, self.num_teams + 1):
            self.teams[team_id] = {
                "team_id": team_id,
                "scheduled_round_types": {"judging": 0, "practice": 0, "table": 0},
                "scheduled_times": [],
                "scheduled_tables": [],
                "scheduled_opponents": [],
                "scheduled_time_table_pairs": []
            }
        # Rooms Dictionary
        self.rooms = {}
        for room_id in range(1, self.num_rooms + 1):
            self.rooms[room_id] = {
                "location_type": "room",
                "location_id": room_id,
                "table_side": None,
                "scheduled_teams": [],
            }
        # Tables Dictionary
        self.tables = {}
        table_ids = [chr(65 + i) for i in range(self.num_tables)]  # ASCII value of 'A' is 65
        for table_id in table_ids:
            for side in [1, 2]:  # Each table has 2 sides
                self.tables[(table_id, side)] = {
                    "location_type": "table",
                    "location_id": table_id,
                    "table_side": side,
                    "scheduled_teams": [],
                    "scheduled_times": []
                }
        return self.teams, self.rooms, self.tables
