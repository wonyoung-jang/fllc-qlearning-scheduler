from PySide6.QtCore import QTime
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTimeEdit, QLabel, QGroupBox, QGridLayout, QWidget
from config import Config

JUDGING     = Config.JUDGING
PRACTICE    = Config.PRACTICE
TABLE       = Config.TABLE

FONT_WEIGHT_BOLD = Config.FONT_WEIGHT_BOLD


class TimeDataInputs:
    def __init__(self, schedule_data, time_data): 
        """
        Initializes the time data inputs for the application.
        
        """
        self.schedule_data = schedule_data
        self.time_data = time_data
        
        # Create time edit widgets for start time and stop time of judging rounds, practice rounds, and table rounds
        self.start_time_judging_rounds = QTimeEdit()
        self.start_time_practice_rounds = QTimeEdit()
        self.stop_time_practice_rounds = QTimeEdit()
        self.start_time_table_rounds = QTimeEdit()
        self.stop_time_table_rounds = QTimeEdit()

        # Set the duration labels for judging rounds, practice rounds, and table rounds
        self.judging_round_duration = QLabel(f'{45} minutes')
        self.judging_round_duration.setFont(QFont("Sans", 8, FONT_WEIGHT_BOLD))
        self.practice_round_duration = QLabel(f'{self.time_data.ROUND_TYPE_DURATIONS[PRACTICE]} minutes')
        self.table_round_duration = QLabel(f'{self.time_data.ROUND_TYPE_DURATIONS[TABLE]} minutes')

        # Create time edit widgets for minimum practice duration and minimum table duration
        self.minimum_practice_duration = QTimeEdit()
        self.minimum_practice_duration.setDisplayFormat('mm')
        self.minimum_table_duration = QTimeEdit()
        self.minimum_table_duration.setDisplayFormat('mm')

        # Create labels for minimum practice duration and minimum table duration
        self.minimum_practice_duration_label = QLabel('Minimum Practice Duration: ')
        self.minimum_table_duration_label = QLabel('Minimum Table Duration:')

        # Display the available practice time and available table time labels
        self.practice_time_available = QLabel(f'{self.time_data.available_practice_duration} minutes')
        self.table_time_available = QLabel(f'{self.time_data.available_table_duration} minutes')
        
        self.minimum_practice_duration.setTime(QTime.fromString(str(self.time_data.ROUND_TYPE_DURATIONS[PRACTICE]), 'mm'))
        self.minimum_table_duration.setTime(QTime.fromString(str(self.time_data.ROUND_TYPE_DURATIONS[TABLE]), 'mm'))
        self.start_time_judging_rounds.setTime(QTime.fromString(self.time_data.JUDGING_ROUNDS_START_TIME, 'HH:mm'))
        self.start_time_practice_rounds.setTime(QTime.fromString(self.time_data.PRACTICE_ROUNDS_START_TIME, 'HH:mm'))
        self.stop_time_practice_rounds.setTime(QTime.fromString(self.time_data.PRACTICE_ROUNDS_STOP_TIME, 'HH:mm'))
        self.start_time_table_rounds.setTime(QTime.fromString(self.time_data.TABLE_ROUNDS_START_TIME, 'HH:mm'))
        self.stop_time_table_rounds.setTime(QTime.fromString(self.time_data.TABLE_ROUNDS_STOP_TIME, 'HH:mm'))
        
        self.judging_stop_time_label = QLabel(f'Judging Rounds-Stop')
        self.judging_round_duration_label = QLabel("Judging Round Duration")
        self.judging_round_duration_label.setFont(QFont("Sans", 8, FONT_WEIGHT_BOLD))

        self.time_data_inputs_groupbox = self.setup_time_data_inputs()
    
    def setup_time_data_inputs(self): 
        """
        Sets up the time data inputs in the GUI.
        
        """
        time_data_inputs_groupbox = QGroupBox("Time Data Inputs")
        self.time_data_layout = QGridLayout(time_data_inputs_groupbox)
        
        self.time_data_layout.addWidget(self.judging_round_duration_label, 0, 0)
        self.time_data_layout.addWidget(self.judging_round_duration, 0, 1)
        
        self.time_data_layout.addWidget(QLabel("Practice Round Duration"), 1, 0)
        self.time_data_layout.addWidget(self.practice_round_duration, 1, 1)
        
        self.time_data_layout.addWidget(self.minimum_practice_duration_label, 2, 0)
        self.time_data_layout.addWidget(self.minimum_practice_duration, 2, 1)
        
        self.time_data_layout.addWidget(QLabel("Table Round Duration"), 3, 0)
        self.time_data_layout.addWidget(self.table_round_duration, 3, 1)
        
        self.time_data_layout.addWidget(self.minimum_table_duration_label, 4, 0)
        self.time_data_layout.addWidget(self.minimum_table_duration, 4, 1)
        
        self.time_data_layout.addWidget(QLabel("Judging Rounds-Start"), 5, 0)
        self.time_data_layout.addWidget(self.start_time_judging_rounds, 5, 1)
        
        self.judging_stop_time = self.start_time_judging_rounds.time().addSecs(self.time_data.ROUND_TYPE_DURATIONS[JUDGING] * 60 * self.time_data.MINIMUM_SLOTS_REQUIRED[JUDGING])
        self.judging_stop_time = QLabel(self.judging_stop_time.toString("HH:mm"))
        
        self.time_data_layout.addWidget(self.judging_stop_time_label, 6, 0)
        self.time_data_layout.addWidget(self.judging_stop_time, 6, 1)
        
        self.time_data_layout.addWidget(QLabel("Practice Rounds-Start"), 7, 0)
        self.time_data_layout.addWidget(self.start_time_practice_rounds, 7, 1)
        
        self.time_data_layout.addWidget(QLabel("Practice Rounds-Stop"), 8, 0)
        self.time_data_layout.addWidget(self.stop_time_practice_rounds, 8, 1)
        
        self.time_data_layout.addWidget(QLabel("Table Rounds-Start"), 9, 0)
        self.time_data_layout.addWidget(self.start_time_table_rounds, 9, 1)
        
        self.time_data_layout.addWidget(QLabel("Table Rounds-Stop"), 10, 0)
        self.time_data_layout.addWidget(self.stop_time_table_rounds, 10, 1)
        
        self.time_data_layout.addWidget(QLabel("Practice Time Available"), 11, 0)
        self.time_data_layout.addWidget(self.practice_time_available, 11, 1)
        
        self.time_data_layout.addWidget(QLabel("Table Time Available"), 12, 0)
        self.time_data_layout.addWidget(self.table_time_available, 12, 1)
        
        return time_data_inputs_groupbox
    