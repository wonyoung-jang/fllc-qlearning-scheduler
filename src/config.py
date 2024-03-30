"""This module contains the configuration settings for the Q-Learning algorithm and the GUI."""
from PySide6.QtGui import QFont

class Config:
    """Class to store configuration settings for the Q-Learning algorithm and the GUI."""
    
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
    FONT_WEIGHT_BOLD    = QFont.Bold
    
    # Soft Constraint Constants
    TABLE_CONSISTENCY       = 'Table Consistency'
    OPPONENT_VARIETY        = 'Opponent Variety'
    BACK_TO_BACK_PENALTY    = 'Back to Back Penalty'
    BREAK_TIME              = 'Break Time'
    
    
    ##########################
    # Data Inputs (Defaults) #
    ##########################
    
    # Schedule Data settings
    num_teams   = 42
    num_rooms   = 7
    num_tables  = 4
    round_types_per_team = {
        JUDGING   : 1, 
        PRACTICE  : 2, 
        TABLE     : 3
    }
    
    # Time Data settings
    judging_rounds_start_time   = '08:00'
    practice_rounds_start_time  = '09:00'
    practice_rounds_stop_time   = '12:00'
    table_rounds_start_time     = '13:30'
    table_rounds_stop_time      = '16:21'
    minimum_slots_required = {
        JUDGING   : 1,
        PRACTICE  : 2,
        TABLE     : 3
    }
    
    round_type_durations = {
        JUDGING : 45,
        PRACTICE: 0,
        TABLE   : 0
    }
    
    TIME_FORMAT = '%H:%M'
    
    # Q-Learning hyperparameters
    learning_rate       = 0.20
    discount_factor     = 0.80
    epsilon_start       = 1.00
    epsilon_end         = 0.01
    epsilon_decay       = 0.995
    training_episodes   = 5
    
    # Soft Constraint weights
    TABLE_CONSISTENCY_WEIGHT    = 1.0
    OPPONENT_VARIETY_WEIGHT     = 1.0
    BACK_TO_BACK_PENALTY_WEIGHT = 1.0
    BREAK_TIME_WEIGHT           = 1.0

    
    ###########################
    # GUI Settings (Defaults) #
    ###########################
    
    # GUI settings
    gui_refresh_interval = 1

    
    ################
    # Data Exports #
    ################
    
    # Export settings
    EXPORTS_DIRECTORY                   = './exports'
    OPTIMAL_SCHEDULE_GRID_EXCEL_PATH    = './exports/grid_optimal_schedule.xlsx'
    EVAL_RESULTS_CSV_PATH               = './exports/schedule_evaluation/evaluation_results.csv'
    
    # Column names
    COL_TIME        = 'Time'
    COL_ROUND       = 'Round'
    COL_LOCATION    = 'Location'
    COL_TEAM        = 'Team'
    COL_QVALUE      = 'Q-Value'
    
    # Evaluation data
    EVAL_TYPES                      = ['Benchmarks', 'Training', 'Optimal']
    EVAL_TYPE                       = 'Eval Type'
    SCORES                          = 'Scores'
    COMPLETION_PERCENTAGES          = 'Completion Percentages'
    AVERAGE_SCORE                   = 'Average Score'
    AVERAGE_COMPLETION_PERCENTAGE   = 'Average Completion Percentage'