"""This module contains the Team class."""


class Team:
    """A team at the competition."""
    
    def __init__(self, team_id):
        """Initialize a Team object."""
        self.team_id = team_id
        self.scheduled_round_types = {'judging': 0, 'practice': 0, 'table': 0}
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