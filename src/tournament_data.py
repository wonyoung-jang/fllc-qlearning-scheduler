from config import KeysConfig, ValuesConfig, TournamentDataDefaultConfig

KEY = KeysConfig()
VALUE = ValuesConfig()
TOURNAMENT = TournamentDataDefaultConfig()

# OBJECT
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
        self.teams, self.rooms, self.tables
 