"""This module contains the Room class."""
from config import Config


class Room:
    """A (judging) room at the competition venue."""
    
    def __init__(self, room_id):
        """Initialize a Room object."""
        self.location_type = Config.LOCATION_TYPE_ROOM
        self.location_id = room_id
        self.table_side = None
        self.scheduled_teams = []

    def __str__(self):
        """Return a string representation of a Room object."""
        return f'Room(location_id={self.location_id})'

    def __repr__(self):
        """Return a string representation of a Room object."""
        return self.__str__()