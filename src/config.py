from PySide6.QtGui import QFont


class BaseConfig:
    """
    Base class for configuration settings.
    
    """
    # Common configuration settings go here

class FormatsConfig(BaseConfig):
    """
    Class to store logging configuration settings.
    
    """
    LOGGING_FORMAT     = '%(asctime)s - %(levelname)s - %(message)s'
    TIME_FORMAT        = '%H:%M'

class FontsConfig(BaseConfig):
    """
    Class to store font configuration settings.
    
    """
    FONT_SIZE_HEADER    = 12
    FONT_SIZE_SUBHEADER = 10
    FONT_SIZE_BODY      = 8
    FONT_STYLE          = 'Sans'
    FONT_WEIGHT_BOLD    = QFont.Bold
    FONT_SPINBOX        = QFont(FONT_STYLE, FONT_SIZE_BODY, FONT_WEIGHT_BOLD)

class KeysConfig(BaseConfig):
    """
    Class to store configuration settings for keys.
    
    """
    # Dictionary Keys
    JUDGING             = 'judging'
    PRACTICE            = 'practice'
    TABLE               = 'table'
    
    # Teams
    TEAM_ID                     = 'team_id'
    SCHEDULED_ROUND_TYPES       = 'scheduled_round_types'
    SCHEDULED_TIMES             = 'scheduled_times'
    SCHEDULED_TABLES            = 'scheduled_tables'
    SCHEDULED_OPPONENTS         = 'scheduled_opponents'
    SCHEDULED_TIME_TABLE_PAIRS  = 'scheduled_time_table_pairs'

    # Locations
    LOCATION_TYPE               = 'location_type'
    LOCATION_ID                 = 'location_id'
    TABLE_SIDE                  = 'table_side'
    SCHEDULED_TEAMS             = 'scheduled_teams'
    
    # Soft Constraints
    TABLE_CONSISTENCY   = 'Table Consistency'
    OPPONENT_VARIETY    = 'Opponent Variety'
    BACK_TO_BACK_PENALTY= 'Back to Back Penalty'
    BREAK_TIME          = 'Break Time'
    
    COLOR              = 'color'

class ValuesConfig(BaseConfig):
    """
    Class to store configuration settings for values.
    
    """
    LOCATION_TYPE_ROOM  = 'room'
    LOCATION_TYPE_TABLE = 'table'
    
    ROUND_DURATION_JUDGING  = 45

class TournamentDataDefaultConfig(BaseConfig):
    """
    Class to store schedule data configuration settings.
    
    """
    NUM_TEAMS                           = 42
    NUM_ROOMS                           = 6
    NUM_TABLES                          = 4
    ROUND_TYPES_PER_TEAM                = {
        KeysConfig.JUDGING            : 1,
        KeysConfig.PRACTICE           : 2,
        KeysConfig.TABLE              : 3
    }
    TABLE_SIDE_1                        = '1'
    TABLE_SIDE_2                        = '2'
    ROUND_TYPES_PER_TEAM_LABEL          = 'Round Types per Team'

class TimeDataDefaultConfig(BaseConfig):
    """
    Class to store time data configuration settings.
    
    """
    JUDGING_ROUNDS_START_TIME           = '08:00'
    PRACTICE_ROUNDS_START_TIME          = '09:00'
    PRACTICE_ROUNDS_STOP_TIME           = '12:00'
    TABLE_ROUNDS_START_TIME             = '13:30'
    TABLE_ROUNDS_STOP_TIME              = '16:21'
    MINIMUM_SLOTS_REQUIRED              = {
        KeysConfig.JUDGING              : 1,
        KeysConfig.PRACTICE             : 2,
        KeysConfig.TABLE                : 3
    }
    ROUND_TYPE_DURATIONS                = {
        KeysConfig.JUDGING              : 45,
        KeysConfig.PRACTICE             : 0,
        KeysConfig.TABLE                : 0
    }
    ROUND_TYPE_TIME_SLOTS               = {
        KeysConfig.JUDGING              : [],
        KeysConfig.PRACTICE             : [],
        KeysConfig.TABLE                : []
    }
    MINUTES_PER_HOUR                    = 60
    SECS_IN_MINUTE                      = 60

class QLearningDefaultConfig(BaseConfig):
    """
    Class to store Q-Learning hyperparameter configuration settings.
    
    """
    LEARNING_RATE       = 0.20
    DISCOUNT_FACTOR     = 0.80
    EPSILON_START       = 1.00
    EPSILON_END         = 0.01
    EPSILON_DECAY       = 0.995
    TRAINING_EPISODES   = 25

class SoftConstraintDefaultConfig(BaseConfig):
    """
    Class to store soft constraint weight configuration settings.
    
    """
    TABLE_CONSISTENCY_WEIGHT    = 1.0
    OPPONENT_VARIETY_WEIGHT     = 1.0
    BACK_TO_BACK_PENALTY_WEIGHT = 1.0
    BREAK_TIME_WEIGHT           = 1.0
    SOFT_CONSTRAINTS_WEIGHT     = {
        KeysConfig.TABLE_CONSISTENCY    : TABLE_CONSISTENCY_WEIGHT,
        KeysConfig.OPPONENT_VARIETY     : OPPONENT_VARIETY_WEIGHT,
        KeysConfig.BACK_TO_BACK_PENALTY : BACK_TO_BACK_PENALTY_WEIGHT,
        KeysConfig.BREAK_TIME           : BREAK_TIME_WEIGHT
    }
      
class GUIConfig(BaseConfig):
    """
    Class to store GUI configuration settings.
    
    """
    REFRESH_INTERVAL    = 1
    WINDOW_TITLE        = 'FIRST LEGO League Challenge Q-Learning Tournament Scheduler'

class ExportConfig(BaseConfig):
    """
    Class to store export configuration settings.
    
    """
    CSV_EXT                             = '.csv'
    TXT_EXT                             = '.txt'
    XLSX_EXT                            = '.xlsx'
    
    LOGGING_DIRECTORY                   = 'logs'
    LOGGING_FILE_NAME                   = '/FLLC-Q_Log'
    
    EXPORTS_DIRECTORY                   = 'exports'
    Q_TABLE_CSV_FILENAME                = '/q_table'
    OPTIMAL_SCHEDULE_CSV_FILENAME       = '/optimal_schedule'
    OPTIMAL_SCHEDULE_EXCEL_FILENAME     = '/grid_optimal_schedule'
    
    TRAINING_SCHEDULES_DIRECTORY        = '/training_schedules_output'
    TRAINING_SCHEDULE_CSV_FILENAME      = '/schedule_episode_'

    # Column names
    COL_TIME                            = 'Time'
    COL_ROUND                           = 'Round'
    COL_LOCATION                        = 'Location'
    COL_TEAM                            = 'Team'
    COL_QVALUE                          = 'Q-Value'
