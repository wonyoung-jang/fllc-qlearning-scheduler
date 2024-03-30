"""This module contains the Team class."""
from config import Config

class Team:
    """A team at the competition."""
    
    def __init__(self, team_id):
        """Initialize a Team object."""
        self.team_id = team_id
        self.scheduled_round_types = {
            Config.JUDGING  : 0, 
            Config.PRACTICE : 0, 
            Config.TABLE    : 0
        }
        self.scheduled_times = []
        self.scheduled_tables = []
        self.scheduled_opponents = []
        self.scheduled_time_table_pairs = []

    def __str__(self):
        """Return a string representation of a Team object."""
        return f'Team(team_id={self.team_id})'

    def __repr__(self):
        """Return a string representation of a Team object."""
        return self.__str__()