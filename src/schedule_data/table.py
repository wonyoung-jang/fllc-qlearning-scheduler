"""This module contains the Table class."""
from config import Config

class Table:
    """A table at the competition venue for Practice and Table rounds."""
    
    def __init__(self, table_id, side):
        """Initialize a Table object."""
        self.location_type = Config.LOCATION_TYPE_TABLE
        self.location_id = table_id
        self.table_side = side
        self.scheduled_teams = []
        self.scheduled_times = []

    def __str__(self):
        """Return a string representation of a Table object."""
        return f'Table(location_id={self.location_id}, table_side={self.table_side})'

    def __repr__(self):
        """Return a string representation of a Table object."""
        return self.__str__()
