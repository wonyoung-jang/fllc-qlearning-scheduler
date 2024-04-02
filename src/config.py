"""This module contains the configuration settings for the Q-Learning algorithm and the GUI."""
import sys
from PySide6.QtGui import QFont

class Config:
    """Class to store configuration settings for the Q-Learning algorithm and the GUI."""
    ###########
    # Logging #
    ###########
    
    # Logging settings
    LOGGING_FILE_NAME = 'FLLC-Q_Log.txt'
    LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    
    #############
    # Constants #
    #############
    
    # Round Type Constants
    JUDGING     = 'judging'
    PRACTICE    = 'practice'
    TABLE       = 'table'
    
    # Location Type Constants
    LOCATION_TYPE_ROOM  = 'room'
    LOCATION_TYPE_TABLE = 'table'
    
    # GUI Constants
    FONT_SIZE_HEADER    = 12
    FONT_SIZE_SUBHEADER = 10
    FONT_SIZE_BODY      = 8
    
    FONT_STYLE          = 'Sans'
    FONT_WEIGHT_BOLD    = QFont.Bold
    
    FONT_SPINBOX        = QFont(FONT_STYLE, FONT_SIZE_BODY, FONT_WEIGHT_BOLD)
    
    
    # Soft Constraint Constants
    TABLE_CONSISTENCY       = 'Table Consistency'
    OPPONENT_VARIETY        = 'Opponent Variety'
    BACK_TO_BACK_PENALTY    = 'Back to Back Penalty'
    BREAK_TIME              = 'Break Time'
    
    
    ##########################
    # Data Inputs (Defaults) #
    ##########################
    
    # Schedule Data settings
    NUM_TEAMS   = 8
    NUM_ROOMS   = 2
    NUM_TABLES  = 2
    
    ROUND_TYPE_PER_TEAM = {
        JUDGING   : 1, 
        PRACTICE  : 2, 
        TABLE     : 3
    }
    
    TABLE_SIDE_1 = '1'
    TABLE_SIDE_2 = '2'
    
    ROUND_TYPES_PER_TEAM_LABEL = 'Round Types per Team'
    
    SCHEDULE_DATA_INPUTS_GROUPBOX_LABEL = 'Schedule Data Inputs'
    
    NUM_TEAMS_LABEL             = 'Number of Teams'
    NUM_ROOMS_LABEL             = 'Number of Rooms'
    NUM_TABLES_LABEL            = 'Number of Tables'
    NUM_TABLES_AND_SIDES_LABEL  = 'Number of Tables and Sides: '
    
    # Time Data settings
    JUDGING_ROUNDS_START_TIME   = '08:00'
    PRACTICE_ROUNDS_START_TIME  = '09:00'
    PRACTICE_ROUNDS_STOP_TIME   = '12:00'
    TABLE_ROUNDS_START_TIME     = '13:30'
    TABLE_ROUNDS_STOP_TIME      = '16:21'
    
    MINIMUM_SLOTS_REQUIRED = {
        JUDGING   : 1,
        PRACTICE  : 2,
        TABLE     : 3
    }
    
    ROUND_TYPE_DURATIONS = {
        JUDGING : 45,
        PRACTICE: 0,
        TABLE   : 0
    }
    
    TIME_FORMAT = '%H:%M'
    
    # Q-Learning hyperparameters
    LEARNING_RATE       = 0.20
    DISCOUNT_FACTOR     = 0.80
    EPSILON_START       = 1.00
    EPSILON_END         = 0.01
    EPSILON_DECAY       = 0.995
    TRAINING_EPISODES   = 25
    
    # Soft Constraint weights
    TABLE_CONSISTENCY_WEIGHT    = 1.0
    OPPONENT_VARIETY_WEIGHT     = 1.0
    BACK_TO_BACK_PENALTY_WEIGHT = 1.0
    BREAK_TIME_WEIGHT           = 1.0

    
    ###########################
    # GUI Settings (Defaults) #
    ###########################
    
    # GUI settings
    GUI_REFRESH_INTERVAL = 1

    
    ################
    # Data Exports #
    ################
    
    # Export settings
    CSV_EXT                  = '.csv'
    XLSX_EXT                 = '.xlsx'
    EXPORTS_DIRECTORY                   = './exports'
    TRAINING_SCHEDULE_CSV_FILENAME      = '/training_schedules_output/schedule_episode_'
    OPTIMAL_SCHEDULE_CSV_FILENAME       = '/optimal_schedule'
    OPTIMAL_SCHEDULE_EXCEL_FILENAME     = '/grid_optimal_schedule'
    Q_TABLE_CSV_FILENAME                = '/q_table'
    
    # Column names
    COL_TIME        = 'Time'
    COL_ROUND       = 'Round'
    COL_LOCATION    = 'Location'
    COL_TEAM        = 'Team'
    COL_QVALUE      = 'Q-Value'
