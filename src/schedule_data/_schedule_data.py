"""This module contains the ScheduleData class, which is used to store the data for the schedule."""
from .team import Team
from .table import Table
from .room import Room
from config import Config


class ScheduleData:
    """A class to store the data for the schedule."""
    
    def __init__(self):
        """Initialize a ScheduleData object."""
        self.NUM_TEAMS  = Config.NUM_TEAMS
        self.NUM_ROOMS  = Config.NUM_ROOMS
        self.NUM_TABLES = Config.NUM_TABLES
        self.ROUND_TYPE_PER_TEAM = Config.ROUND_TYPE_PER_TEAM
        
        self.num_tables_and_sides = self.NUM_TABLES * 2
        self.teams, self.rooms, self.tables = self.initialize_teams_rooms_tables()

    def __str__(self):
        """Return a string representation of a ScheduleData object."""
        return f'ScheduleData(NUM_TEAMS={self.NUM_TEAMS}, NUM_ROOMS={self.NUM_ROOMS}, NUM_TABLES={self.NUM_TABLES})'

    def __repr__(self):
        """Return a string representation of a ScheduleData object."""
        return self.__str__()

    def initialize_teams_rooms_tables(self):
        """Initialize the teams, rooms, and tables for the competition."""
        self.teams = {team_id: Team(team_id) for team_id in range(1, self.NUM_TEAMS + 1)}
        self.rooms = {room_id: Room(room_id) for room_id in range(1, self.NUM_ROOMS + 1)}
        
        table_ids = [chr(65 + i) for i in range(self.NUM_TABLES)]
        self.tables = {(table_id, side): Table(table_id, side) for table_id in table_ids for side in [1, 2]}

        return self.teams, self.rooms, self.tables