"""
This module contains the ScheduleDataInputs class, which is a QWidget that contains the schedule data inputs for the GUI. 

"""
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSpinBox, QLabel, QGroupBox, QGridLayout, QWidget
from config import Config

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

class ScheduleDataInputs:
    def __init__(self, schedule_data):
        """
        Initialize the ScheduleDataInputs object.
        
        """
        self.schedule_data = schedule_data
        self.num_teams_spinbox  = QSpinBox()
        self.num_rooms_spinbox  = QSpinBox()
        self.num_tables_spinbox = QSpinBox()
        
        self.num_tables_and_sides_count = QLabel(str(self.schedule_data.num_tables_and_sides))
                
        self.round_type_spinboxes = {
            JUDGING     : QLabel('1'),
            PRACTICE    : QSpinBox(),
            TABLE       : QSpinBox(),
        }
        self.round_type_spinboxes[JUDGING].setFont(FONT_SPINBOX)
        
        self.round_type_labels = {}
        for name, spinbox in self.round_type_spinboxes.items():
            round_type_result = self.schedule_data.NUM_TEAMS * self.schedule_data.ROUND_TYPE_PER_TEAM[name]
            self.round_type_labels[name] = QLabel(f"{round_type_result} Rounds")
        
        # Initialize Schedule Data Inputs
        self.num_teams_spinbox.setValue(self.schedule_data.NUM_TEAMS)
        self.num_rooms_spinbox.setValue(self.schedule_data.NUM_ROOMS)
        self.num_tables_spinbox.setValue(self.schedule_data.NUM_TABLES)
        for name, spinbox in self.round_type_spinboxes.items():
            if name == JUDGING:  # Skip the judging round type
                continue
            spinbox.setValue(self.schedule_data.ROUND_TYPE_PER_TEAM[name])
            
        self.inputs_groupbox        = self.setup_schedule_data_inputs()
        self.round_type_groupbox    = self.setup_round_type_inputs()
        
    def setup_schedule_data_inputs(self): 
        """
        Sets up the schedule data inputs in the GUI.
        
        """
        NUM_TEAMS_LABEL             = QLabel(Config.NUM_TEAMS_LABEL)
        NUM_ROOMS_LABEL             = QLabel(Config.NUM_ROOMS_LABEL)
        NUM_TABLES_LABEL            = QLabel(Config.NUM_TABLES_LABEL)
        NUM_TABLES_AND_SIDES_LABEL  = QLabel(Config.NUM_TABLES_AND_SIDES_LABEL)

        schedule_data_groupbox  = QGroupBox(SCHEDULE_DATA_INPUTS_GROUPBOX_LABEL)
        schedule_data_layout    = QGridLayout(schedule_data_groupbox)
        
        schedule_data_layout.addWidget(NUM_TEAMS_LABEL,             0, 0)
        schedule_data_layout.addWidget(NUM_ROOMS_LABEL,             1, 0)
        schedule_data_layout.addWidget(NUM_TABLES_LABEL,            2, 0)
        schedule_data_layout.addWidget(NUM_TABLES_AND_SIDES_LABEL,  3, 0)
        
        schedule_data_layout.addWidget(self.num_teams_spinbox,          0, 1)
        schedule_data_layout.addWidget(self.num_rooms_spinbox,          1, 1)
        schedule_data_layout.addWidget(self.num_tables_spinbox,         2, 1)
        schedule_data_layout.addWidget(self.num_tables_and_sides_count, 3, 1, Qt.AlignRight)
        
        return schedule_data_groupbox
        
    def setup_round_type_inputs(self):
        """
        Sets up the round type inputs in the GUI.
        
        """
        round_type_groupbox =  QGroupBox(ROUND_TYPES_PER_TEAM_LABEL)
        round_type_layout = QGridLayout(round_type_groupbox)
        
        count = 0
        for name, spinbox in self.round_type_spinboxes.items():
            if name == JUDGING:
                judging_label = QLabel(JUDGING)
                judging_label.setFont(FONT_SPINBOX)
                round_type_layout.addWidget(judging_label, count, 0)
            else:
                round_type_layout.addWidget(QLabel(name.capitalize()), count, 0)
            round_type_layout.addWidget(spinbox, count, 1)
            round_type_layout.addWidget(self.round_type_labels[name], count, 2, Qt.AlignRight)
            count += 1
        
        return round_type_groupbox
