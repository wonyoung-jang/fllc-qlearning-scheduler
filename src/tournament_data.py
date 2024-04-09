"""
This module is responsible for generating the time slots for each round type based on the number of teams and rooms/tables/sides.

"""
import colorsys
from PySide6.QtGui import QColor
from config import KeysConfig, ValuesConfig, TournamentDataDefaultConfig

KEY         = KeysConfig()
VALUE       = ValuesConfig()
TOURNAMENT  = TournamentDataDefaultConfig()

def init_teams() -> dict:
    """
    Initialize teams.
    
    """
    teams = {
        team_id: {
            KEY.TEAM_ID: team_id,
            KEY.SCHEDULED_ROUND_TYPES: {
                                        KEY.JUDGING   : 0, 
                                        KEY.PRACTICE  : 0, 
                                        KEY.TABLE     : 0,
                                        },
            KEY.SCHEDULED_TIMES: [],
            KEY.SCHEDULED_TABLES: [],
            KEY.SCHEDULED_OPPONENTS: [],
            KEY.SCHEDULED_TIME_TABLE_PAIRS: [],
        }
        for team_id in range(1, TOURNAMENT.NUM_TEAMS + 1)
    }
    
    return teams

def init_rooms() -> dict:
    """
    Initialize rooms.
    
    """
    rooms = {
        room_id: {
            KEY.LOCATION_TYPE: VALUE.LOCATION_TYPE_ROOM,
            KEY.LOCATION_ID: room_id,
            KEY.TABLE_SIDE: None,
            KEY.SCHEDULED_TEAMS: [],
        } for room_id in range(1, TOURNAMENT.NUM_ROOMS + 1)
    }
    
    return rooms

def init_tables() -> dict:
    """
    Initialize tables.
    
    """
    table_ids = [chr(65 + i) for i in range(TOURNAMENT.NUM_TABLES)]
    tables = {
        (table_id, side): {
            KEY.LOCATION_TYPE: VALUE.LOCATION_TYPE_TABLE,
            KEY.LOCATION_ID: table_id,
            KEY.TABLE_SIDE: side,
            KEY.SCHEDULED_TEAMS: [],
            KEY.SCHEDULED_TIMES: [],
        } for table_id in table_ids for side in [1, 2]
    }
    
    return tables

def init_color_map(teams) -> dict:
    """
    Initialize color map for teams.
    
    """
    color_map = {}
    for i, team_id in enumerate(teams):
        hue = ((i / TOURNAMENT.NUM_TEAMS) * 0.618033988749895) % 1.0  # Golden ratio
        saturation = 0.5
        value = 0.85
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        color = QColor.fromRgb(int(r * 255), int(g * 255), int(b * 255))
        color_map[team_id] = color
    
    return color_map


class TournamentData:
    """
    Class to store data for scheduling rounds and tables.
    
    """
    def __init__(self):
        """
        Initialize TournamentData object.
        
        """
        self.num_teams = TOURNAMENT.NUM_TEAMS
        self.num_rooms = TOURNAMENT.NUM_ROOMS
        self.num_tables = TOURNAMENT.NUM_TABLES
        self.round_types_per_team = TOURNAMENT.ROUND_TYPES_PER_TEAM
        self.num_tables_and_sides = self.num_tables * 2
        self.teams, self.rooms, self.tables = self.initialize_teams_rooms_tables()
        
    def initialize_teams_rooms_tables(self):
        """
        Initialize teams, rooms, and tables.
        
        """        
        self.teams = {
            team_id: {
                KEY.TEAM_ID: team_id,
                KEY.SCHEDULED_ROUND_TYPES: {
                                            KEY.JUDGING   : 0, 
                                            KEY.PRACTICE  : 0, 
                                            KEY.TABLE     : 0,
                                            },
                KEY.SCHEDULED_TIMES: [],
                KEY.SCHEDULED_TABLES: [],
                KEY.SCHEDULED_OPPONENTS: [],
                KEY.SCHEDULED_TIME_TABLE_PAIRS: [],
            }
            for team_id in range(1, self.num_teams + 1)
        }
        
        self.color_map = self.initialize_color_map()

        self.rooms = {
            room_id: {
                KEY.LOCATION_TYPE: VALUE.LOCATION_TYPE_ROOM,
                KEY.LOCATION_ID: room_id,
                KEY.TABLE_SIDE: None,
                KEY.SCHEDULED_TEAMS: [],
            } for room_id in range(1, self.num_rooms + 1)
        }

        table_ids = [chr(65 + i) for i in range(self.num_tables)]
        self.tables = {
            (table_id, side): {
                KEY.LOCATION_TYPE: VALUE.LOCATION_TYPE_TABLE,
                KEY.LOCATION_ID: table_id,
                KEY.TABLE_SIDE: side,
                KEY.SCHEDULED_TEAMS: [],
                KEY.SCHEDULED_TIMES: [],
            } for table_id in table_ids for side in [1, 2]
        }

        return self.teams, self.rooms, self.tables
    
    def initialize_color_map(self):
        """
        Initialize color map for teams.
        
        """
        color_map = {}
        for i, team_id in enumerate(self.teams):
            hue = ((i / self.num_teams) * 0.618033988749895) % 1.0  # Golden ratio
            saturation = 0.5
            value = 0.85
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
            color = QColor.fromRgb(int(r * 255), int(g * 255), int(b * 255))
            color_map[team_id] = color
        
        return color_map
                    