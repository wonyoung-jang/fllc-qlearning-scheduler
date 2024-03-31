from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSpinBox, QLabel, QGroupBox, QGridLayout, QWidget, Qt
from src.config import Config
from src.schedule_data._schedule_data import ScheduleData

JUDGING     = Config.JUDGING
PRACTICE    = Config.PRACTICE
TABLE       = Config.TABLE

FONT_SPINBOX    = Config.FONT_SPINBOX

NUM_TEAMS  = Config.NUM_TEAMS
NUM_ROOMS  = Config.NUM_ROOMS
NUM_TABLES = Config.NUM_TABLES

ROUND_TYPE_PER_TEAM = Config.ROUND_TYPE_PER_TEAM

ROUND_TYPES_PER_TEAM_LABEL = Config.ROUND_TYPES_PER_TEAM_LABEL

SCHEDULE_DATA_INPUTS_GROUPBOX_LABEL = Config.SCHEDULE_DATA_INPUTS_GROUPBOX_LABEL

NUM_TEAMS_LABEL             = QLabel(Config.NUM_TEAMS_LABEL)
NUM_ROOMS_LABEL             = QLabel(Config.NUM_ROOMS_LABEL)
NUM_TABLES_LABEL            = QLabel(Config.NUM_TABLES_LABEL)
NUM_TABLES_AND_SIDES_LABEL  = QLabel(Config.NUM_TABLES_AND_SIDES_LABEL)

class ScheduleDataInputs(QWidget):
    def __init__(self):
        """
        Initialize the ScheduleDataInputs object.
        
        """
        super().__init__()
        self.schedule_data = ScheduleData
        self.create_schedule_data_inputs()
        self.initialize_schedule_data_inputs()
        self.setup_schedule_data_inputs()
    
    def create_schedule_data_inputs(self): 
        """
        Creates the schedule data inputs for the application.
        
        """
        self.num_teams_spinbox  = QSpinBox(self)
        self.num_rooms_spinbox  = QSpinBox(self)
        self.num_tables_spinbox = QSpinBox(self)
        
        self.num_tables_and_sides_count = QLabel(str(self.schedule_data.num_tables_and_sides))
        
        self.round_type_groupbox    = QGroupBox(ROUND_TYPES_PER_TEAM_LABEL)
        self.round_type_layout      = QGridLayout(self.round_type_groupbox)

        self.round_type_spinboxes = {
            JUDGING     : QLabel('1'),
            PRACTICE    : QSpinBox(self),
            TABLE       : QSpinBox(self),
        }

        self.round_type_labels = {}

        for name, spinbox in self.round_type_spinboxes.items():
            rount_type_result = self.schedule_data.NUM_TEAMS * self.schedule_data.ROUND_TYPE_PER_TEAM[name]
            self.round_type_labels[name] = QLabel(f"{round_type_result} Rounds")

        self.round_type_spinboxes[JUDGING].setFont(FONT_SPINBOX)
        
    def initialize_schedule_data_inputs(self): 
        """
        Initializes the schedule data inputs based on the values stored in the `schedule_data` object.
        
        """
        self.num_teams_spinbox.setValue(self.schedule_data.NUM_TEAMS)
        self.num_rooms_spinbox.setValue(self.schedule_data.NUM_ROOMS)
        self.num_tables_spinbox.setValue(self.schedule_data.NUM_TABLES)
        for name, spinbox in self.round_type_spinboxes.items():
            if name == JUDGING:
                continue
            spinbox.setValue(self.schedule_data.ROUND_TYPE_PER_TEAM[name])

    def setup_schedule_data_inputs(self): 
        """
        Sets up the schedule data inputs in the GUI.
        
        """
        self.schedule_data_inputs_groupbox = QGroupBox(SCHEDULE_DATA_INPUTS_GROUPBOX_LABEL)
        self.schedule_data_layout = QGridLayout(self.schedule_data_inputs_groupbox)
        
        self.schedule_data_layout.addWidget(NUM_TEAMS_LABEL, 0, 0)
        self.schedule_data_layout.addWidget(NUM_ROOMS_LABEL, 1, 0)
        self.schedule_data_layout.addWidget(NUM_TABLES_LABEL, 2, 0)
        self.schedule_data_layout.addWidget(NUM_TABLES_AND_SIDES_LABEL, 3, 0)
        
        self.schedule_data_layout.addWidget(self.num_teams_spinbox, 0, 1)
        self.schedule_data_layout.addWidget(self.num_rooms_spinbox, 1, 1)
        self.schedule_data_layout.addWidget(self.num_tables_spinbox, 2, 1)
        self.schedule_data_layout.addWidget(self.num_tables_and_sides_count, 3, 1, Qt.AlignRight)
        
        # Round Types per Team Inputs Widgets
        count = 0
        for name, spinbox in self.round_type_spinboxes.items():
            if name == JUDGING:
                judging_label = QLabel(JUDGING)
                judging_label.setFont(FONT_SPINBOX)
                self.round_type_layout.addWidget(judging_label, count, 0)
            else:
                self.round_type_layout.addWidget(QLabel(name.capitalize()), count, 0)
            self.round_type_layout.addWidget(spinbox, count, 1)
            self.round_type_layout.addWidget(self.round_type_labels[name], count, 2, Qt.AlignRight)
            count += 1
