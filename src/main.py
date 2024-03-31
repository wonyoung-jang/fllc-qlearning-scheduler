"""This module contains the main window class for the scheduler application."""
import os
import sys
import pandas as pd
from datetime import datetime
from openpyxl import Workbook
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QSpinBox,
    QTimeEdit,
    QComboBox,
    QGroupBox,
    QGridLayout,
    QHBoxLayout,
    QDoubleSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QProgressBar,
    QSlider,
    QSizePolicy,
    QSplitter
)
import colorsys
from PySide6.QtCore import QTime, Qt, QThread, QMetaObject, Q_ARG, Slot, QTranslator, QCoreApplication, QLocale, QEvent, QKeyCombination
from PySide6.QtGui import QFont, QShortcut, QKeySequence, QBrush, QColor
from schedule_data._schedule_data import ScheduleData
from time_data._time_data import TimeData
from q_learning import QLearning
from training_thread import TrainingWorker
from config import Config
from gui.schedule_data_inputs import ScheduleDataInputs
from gui.time_data_inputs import TimeDataInputs
from gui.q_learning_inputs import QLearningInputs
from gui.soft_constraint_weights_inputs import SoftConstraintWeightsInputs
from gui.statistics_and_progress_inputs import StatisticsAndProgressInputs
# TODO Refactor this code

FONT_SIZE_HEADER = Config.FONT_SIZE_HEADER
FONT_SIZE_SUBHEADER = Config.FONT_SIZE_SUBHEADER
FONT_WEIGHT_BOLD = Config.FONT_WEIGHT_BOLD
FONT_SPINBOX = Config.FONT_SPINBOX

JUDGING = Config.JUDGING
PRACTICE = Config.PRACTICE
TABLE = Config.TABLE

EXPORTS_DIRECTORY = Config.EXPORTS_DIRECTORY


class MainWindow(QWidget):
    """The main window class for the scheduler application."""
    
    def __init__(self): 
        """Initializes the main class of the scheduler application."""
        super().__init__()
        self.setWindowTitle("FIRST LEGO League Challenge Q-Learning Tournament Scheduler")
        
        # Create the schedule data inputs
        self.schedule_data_inputs = ScheduleDataInputs()
        
        self.num_teams_spinbox = self.schedule_data_inputs.num_teams_spinbox
        self.num_rooms_spinbox = self.schedule_data_inputs.num_rooms_spinbox
        self.num_tables_spinbox = self.schedule_data_inputs.num_tables_spinbox
        self.round_type_spinboxes = self.schedule_data_inputs.round_type_spinboxes
        self.round_type_labels = self.schedule_data_inputs.round_type_labels
        
        self.inputs_groupbox = self.schedule_data_inputs.inputs_groupbox
        self.round_type_groupbox = self.schedule_data_inputs.round_type_groupbox
        
        # Create the time data inputs
        self.time_data_inputs = TimeDataInputs()
        
        self.start_time_judging_rounds = self.time_data_inputs.start_time_judging_rounds
        self.start_time_practice_rounds = self.time_data_inputs.start_time_practice_rounds
        self.stop_time_practice_rounds = self.time_data_inputs.stop_time_practice_rounds
        self.minimum_practice_duration = self.time_data_inputs.minimum_practice_duration
        self.minimum_table_duration = self.time_data_inputs.minimum_table_duration
        self.start_time_table_rounds = self.time_data_inputs.start_time_table_rounds
        self.stop_time_table_rounds = self.time_data_inputs.stop_time_table_rounds
        
        self.time_data_inputs_groupbox = self.time_data_inputs.time_data_inputs_groupbox
        
        # Create the Q-learning inputs
        self.q_learning_inputs = QLearningInputs()
        
        self.alpha_spinbox = self.q_learning_inputs.alpha_spinbox
        self.gamma_spinbox = self.q_learning_inputs.gamma_spinbox
        self.epsilon_start_spinbox = self.q_learning_inputs.epsilon_start_spinbox
        self.epsilon_end_spinbox = self.q_learning_inputs.epsilon_end_spinbox
        self.epsilon_decay_spinbox = self.q_learning_inputs.epsilon_decay_spinbox
        self.training_episodes_spinbox = self.q_learning_inputs.training_episodes_spinbox
        
        self.q_learning_inputs_groupbox = self.q_learning_inputs.q_learning_inputs_groupbox
        
        # Create the soft constraint weights inputs
        self.soft_constraint_weights_inputs = SoftConstraintWeightsInputs()
        
        self.soft_constraint_weights = self.soft_constraint_weights_inputs.soft_constraint_weights
        self.soft_constraint_weights_groupbox = self.soft_constraint_weights_inputs.soft_constraint_weights_groupbox
        
        for constraint, slider in self.soft_constraint_weights.items():
            slider.valueChanged.connect(self.on_update)
            
        # Create the statistics and progress inputs
        self.statistics_and_progress_inputs = StatisticsAndProgressInputs()
        
        self.progress_bar = self.statistics_and_progress_inputs.progress_bar
        self.avg_reward_label = self.statistics_and_progress_inputs.avg_reward_label
        self.current_schedule_length_label = self.statistics_and_progress_inputs.current_schedule_length_label
        self.status_label = self.statistics_and_progress_inputs.status_label
        self.q_learning_label = self.statistics_and_progress_inputs.q_learning_label
        self.q_table_size_label = self.statistics_and_progress_inputs.q_table_size_label
        self.gui_refresh_rate = self.statistics_and_progress_inputs.gui_refresh_rate
        self.gui_refresh_layout = self.statistics_and_progress_inputs.gui_refresh_layout
        
        self.statistics_groupbox = self.statistics_and_progress_inputs.statistics_groupbox
            
        
        
        ############################
        self.create_exports_directory()
        self.schedule_data = ScheduleData()
        self.time_data = TimeData(self.schedule_data)
        self.q_learning = QLearning(self.schedule_data, self.time_data)
        
        self.create_gui_components()
        self.initialize_gui_components()
        self.setup_gui_components()
        self.connect_signals_and_slots()
            
        self.initialize_main_gui()
        
        # Create a custom shortcut for the "Ctrl+G" key combination
        self.generate_shortcut = QShortcut(QKeySequence(Qt.CTRL | Qt.Key_G), self)
        self.generate_shortcut.activated.connect(self.start_training_thread)
        
        
    def create_exports_directory(self):
        """Creates the exports directory if it does not exist.
        
        Structure for ./exports directory:
            ./exports
            ├── /training_schedules_output
                ├── schedule_episode_{int}.csv
                ├── schedule_episode_benchmark.csv
            ├── grid_optimal_schedule.xlsx
            ├── optimal_schedule.csv
            ├── q_table.csv
            
        """
        if not os.path.exists(EXPORTS_DIRECTORY):
            os.makedirs(EXPORTS_DIRECTORY)
            os.makedirs(f'{EXPORTS_DIRECTORY}/training_schedules_output')
    
    def create_gui_components(self): 
        """Creates the GUI components for the scheduler application."""
        self.create_schedule_display() # TODO
        self.create_submission_buttons()

    def initialize_gui_components(self):
        """Initializes the GUI components of the scheduler."""        
        self.initialize_schedule_display() # TODO

    def setup_gui_components(self):
        """Sets up the GUI components for the scheduler."""        
        self.setup_schedule_display() # TODO
        
    def initialize_main_gui(self):
        """
        Initializes the main GUI for the scheduler application.
        
        """
        main_layout = QGridLayout(self)
        
        input_panel = QSplitter(Qt.Vertical)
                
        # Add widgets to the left panel
        input_panel.addWidget(self.train_button)

        input_panel.addWidget(self.inputs_groupbox)
        input_panel.addWidget(self.round_type_groupbox)
        input_panel.addWidget(self.time_data_inputs_groupbox)
        input_panel.addWidget(self.q_learning_inputs_groupbox)
        input_panel.addWidget(self.soft_constraint_weights_groupbox)
        input_panel.addWidget(self.statistics_groupbox)
        
        # Add panels to the column splitter
        column_splitter = QSplitter(Qt.Horizontal)
        column_splitter.addWidget(input_panel)
        column_splitter.addWidget(self.schedule_display_groupbox) # TODO
        
        # Add the column splitter to the main layout
        main_layout.addWidget(column_splitter, 0, 0)

    def create_schedule_display(self): 
        """Creates the schedule display for the Q-learning scheduler."""
        # Judging Rounds Table
        self.judging_table = QTableWidget()
        self.judging_table.setColumnCount(self.schedule_data.NUM_ROOMS + 1)  # Time + Room columns
        self.judging_table.setHorizontalHeaderLabels(['Time'] + [f'Room {i+1}' for i in range(self.schedule_data.NUM_ROOMS)])

        # Practice Rounds Table
        self.practice_table = QTableWidget()
        self.practice_table.setColumnCount(self.schedule_data.NUM_TABLES * 2 + 1)  # Time + Table columns
        practice_headers = ['Time'] + [f'Table {chr(65 + i // 2)}{i % 2 + 1}' for i in range(self.schedule_data.NUM_TABLES * 2)]
        self.practice_table.setHorizontalHeaderLabels(practice_headers)

        # Table Rounds Table
        self.table_round_table = QTableWidget()
        self.table_round_table.setColumnCount(self.schedule_data.NUM_TABLES * 2 + 1)  # Time + Table columns
        table_round_headers = ['Time'] + [f'Table {chr(65 + i // 2)}{i % 2 + 1}' for i in range(self.schedule_data.NUM_TABLES * 2)]
        self.table_round_table.setHorizontalHeaderLabels(table_round_headers)
    
    def initialize_schedule_display(self):
        """Initializes the schedule display for the Q-learning scheduler."""

        # Ensure tables are clear and set up before populating
        self.clear_and_setup_tables()

        # Initialize a dictionary to track the last row used for each time in each table
        last_row = {'judging': {}, 'practice': {}, 'table': {}}

        # Create a color map to store unique colors for each team
        color_map = {}

        # Iterate over each entry in the sorted schedule
        for entry in sorted(self.q_learning.schedule, key=lambda x: (x[0], x[2], x[4])):
            time_start, _, round_type, _, location_id, team_id = entry

            table_widget = self.get_table_widget(round_type)

            # If this time_start has not been used in this table, add a new row for it
            if time_start not in last_row[round_type]:
                newRow = table_widget.rowCount()
                table_widget.insertRow(newRow)
                table_widget.setItem(newRow, 0, QTableWidgetItem(time_start))  # Set the time in the first column
                last_row[round_type][time_start] = newRow

            row = last_row[round_type][time_start]

            # Calculate the column for this entry. Adjust get_col_index to fit your logic
            col = self.get_col_index(round_type, location_id)

            item = QTableWidgetItem(str(team_id))
            table_widget.setItem(row, col, item)

            # Generate a unique color for each team if not already in the color map
            if team_id not in color_map:
                hue = (len(color_map) * 0.618033988749895) % 1.0  # Golden ratio
                saturation = 0.5
                value = 0.85
                r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
                color = QColor.fromRgb(int(r * 255), int(g * 255), int(b * 255))
                color_map[team_id] = color
                                
            # Set the cell background color using QBrush
            item.setBackground(QBrush(color_map[team_id]))

    def setup_schedule_display(self): 
        """Sets up the schedule display for the Q-learning scheduler."""
        # Create a vertical splitter for arranging the schedule display
        schedule_splitter = QSplitter(Qt.Vertical)

        # Create the group box for the schedule display
        self.schedule_display_groupbox = QGroupBox("Schedule Display")
        self.schedule_layout = QVBoxLayout(self.schedule_display_groupbox)

        # Create the group box for the judging rounds display
        self.judging_display_groupbox = QGroupBox("Judging Rounds")
        self.judging_layout = QVBoxLayout(self.judging_display_groupbox)

        # Create the group box for the practice rounds display
        self.pracice_display_groupbox = QGroupBox("Practice Rounds")
        self.practice_layout = QVBoxLayout(self.pracice_display_groupbox)

        # Create the group box for the table rounds display
        self.table_display_groupbox = QGroupBox("Table Rounds")
        self.table_layout = QVBoxLayout(self.table_display_groupbox)

        # Add the judging table widget to the judging layout
        self.judging_layout.addWidget(self.judging_table)

        # Add the practice table widget to the practice layout
        self.practice_layout.addWidget(self.practice_table)

        # Add the table round table widget to the table layout
        self.table_layout.addWidget(self.table_round_table)

        # Add the judging display group box to the splitter
        schedule_splitter.addWidget(self.judging_display_groupbox)

        # Add the practice display group box to the splitter
        schedule_splitter.addWidget(self.pracice_display_groupbox)

        # Add the table display group box to the splitter
        schedule_splitter.addWidget(self.table_display_groupbox)

        # Add the splitter to the schedule layout
        self.schedule_layout.addWidget(schedule_splitter)
            
            
    def clear_and_setup_tables(self):
        """Clears and sets up the judging, practice, and table round tables."""

        for table in [self.judging_table, self.practice_table, self.table_round_table]:
            table.clearContents()  # Clear the contents of the table
            table.setColumnCount(0)  # Clear the columns
            table.setRowCount(0)  # Clear the rows
            table.setAlternatingRowColors(True)  # Enable alternating row colors
            table.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable editing

            if table is self.judging_table:
                # Set column count and header labels for judging table
                table.setColumnCount(self.schedule_data.NUM_ROOMS + 1)
                table.setHorizontalHeaderLabels(['Time'] + [f'Room {i+1}' for i in range(self.schedule_data.NUM_ROOMS)])
            else:
                # Set column count and header labels for practice and table round tables
                table.setColumnCount((self.schedule_data.NUM_TABLES * 2) + 1)
                table.setHorizontalHeaderLabels(['Time'] + [f'Table {chr(65 + i // 2)}{i % 2 + 1}' for i in range(self.schedule_data.NUM_TABLES * 2)])

    def get_table_widget(self, round_type):
        """Returns the table widget based on the round type."""
        if round_type == 'judging':
            return self.judging_table
        elif round_type == 'practice':
            return self.practice_table
        else:  # 'table'
            return self.table_round_table

    def get_col_index(self, round_type, location_id):
        """Returns the column index based on the round type and location ID."""
        if round_type == 'judging':
            return int(location_id)
        else:
            col_base = ord(location_id[0]) - ord('A') + 1
            col_offset = int(location_id[1])
            return (col_base - 1) * 2 + col_offset


    def create_submission_buttons(self):
        """Creates submission buttons for training and generating optimal schedule."""
        # Submit(Train) Button
        self.train_button = QPushButton("Train then Generate Optimal Schedule (Ctrl + G)", self)
        self.train_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        
    def connect_signals_and_slots(self):
        """Connects the signals and slots for the scheduler application."""
        # Time Data Inputs
        self.start_time_judging_rounds.timeChanged.connect(self.on_update)  # Connects the timeChanged signal of start_time_judging_rounds to the on_update slot function
        
        self.start_time_practice_rounds.timeChanged.connect(self.on_update)  # Connects the timeChanged signal of start_time_practice_rounds to the on_update slot function
        self.stop_time_practice_rounds.timeChanged.connect(self.on_update)  # Connects the timeChanged signal of stop_time_practice_rounds to the on_update slot function
        
        self.minimum_practice_duration.timeChanged.connect(self.on_update)  # Connects the timeChanged signal of minimum_practice_duration to the on_update slot function
        self.minimum_table_duration.timeChanged.connect(self.on_update)  # Connects the timeChanged signal of minimum_table_duration to the on_update slot function
        
        self.start_time_table_rounds.timeChanged.connect(self.on_update)  # Connects the timeChanged signal of start_time_table_rounds to the on_update slot function
        self.stop_time_table_rounds.timeChanged.connect(self.on_update)  # Connects the timeChanged signal of stop_time_table_rounds to the on_update slot function
        
        self.start_time_practice_rounds.timeChanged.connect(self.validate_practice_times)  # Connects the timeChanged signal of start_time_practice_rounds to the validate_practice_times slot function
        self.stop_time_practice_rounds.timeChanged.connect(self.validate_practice_times)  # Connects the timeChanged signal of stop_time_practice_rounds to the validate_practice_times slot function
        self.minimum_practice_duration.timeChanged.connect(self.validate_practice_times)  # Connects the timeChanged signal of minimum_practice_duration to the validate_practice_times slot function
        
        self.start_time_table_rounds.timeChanged.connect(self.validate_table_times)  # Connects the timeChanged signal of start_time_table_rounds to the validate_table_times slot function
        self.stop_time_table_rounds.timeChanged.connect(self.validate_table_times)  # Connects the timeChanged signal of stop_time_table_rounds to the validate_table_times slot function
        self.minimum_table_duration.timeChanged.connect(self.validate_table_times)  # Connects the timeChanged signal of minimum_table_duration to the validate_table_times slot function
        
        # Schedule Data Inputs        
        self.num_teams_spinbox.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of num_teams_spinbox to the on_update slot function
        self.num_rooms_spinbox.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of num_rooms_spinbox to the on_update slot function
        self.num_tables_spinbox.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of num_tables_spinbox to the on_update slot function
        self.round_type_spinboxes[PRACTICE].valueChanged.connect(self.on_update)  # Connects the valueChanged signal of round_type_spinboxes[PRACTICE] to the on_update slot function
        self.round_type_spinboxes[TABLE].valueChanged.connect(self.on_update)  # Connects the valueChanged signal of round_type_spinboxes[TABLE] to the on_update slot function
        
        # Q-Learning Inputs
        self.alpha_spinbox.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of alpha_spinbox to the on_update slot function
        self.gamma_spinbox.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of gamma_spinbox to the on_update slot function
        self.epsilon_start_spinbox.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of epsilon_start_spinbox to the on_update slot function
        self.epsilon_end_spinbox.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of epsilon_end_spinbox to the on_update slot function
        self.epsilon_decay_spinbox.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of epsilon_decay_spinbox to the on_update slot function
        self.training_episodes_spinbox.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of training_episodes_spinbox to the on_update slot function
        
        # Statistics and Progress
        self.gui_refresh_rate.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of gui_refresh_rate to the on_update slot function
        self.soft_constraint_weights['Table Consistency'].valueChanged.connect(self.on_update)  # Connects the valueChanged signal of soft_constraint_weights['Table Consistency'] to the on_update slot function
        self.soft_constraint_weights['Opponent Variety'].valueChanged.connect(self.on_update)  # Connects the valueChanged signal of soft_constraint_weights['Opponent Variety'] to the on_update slot function
        self.soft_constraint_weights['Back to Back Penalty'].valueChanged.connect(self.on_update)  # Connects the valueChanged signal of soft_constraint_weights['Back to Back Penalty'] to the on_update slot function
        self.soft_constraint_weights['Break Time'].valueChanged.connect(self.on_update)  # Connects the valueChanged signal of soft_constraint_weights['Break Time'] to the on_update slot function
        
        # Buttons
        self.train_button.clicked.connect(self.start_training_thread)  # Connects the clicked signal of train_button to the start_training_thread slot function
    
    def start_training_thread(self):
        """Starts the training thread for the Q-learning scheduler."""
        training_episodes = int(self.training_episodes_spinbox.value())  # Assuming you have an input field for training_episodes
        self.q_learning.training_episodes = training_episodes
        self.initialize_schedule_display()

        self.thread = QThread()
        self.worker = TrainingWorker(self.q_learning)  # Assuming q_learning is your QLearning instance
        self.worker.moveToThread(self.thread)

        self.worker.signals.update_gui_signal.connect(self.update_gui_total, Qt.QueuedConnection)

        self.thread.started.connect(self.worker.run, Qt.QueuedConnection)

        self.thread.start()

    @Slot()
    def validate_practice_times(self):
        """Validates the practice times based on the minimum duration and the round type duration."""
        # Get the start and end practice times, minimum duration, and default duration
        start_practice = self.start_time_practice_rounds.time()
        end_practice = self.stop_time_practice_rounds.time()
        min_duration = self.minimum_practice_duration.time()
        duration = self.time_data.ROUND_TYPE_DURATIONS[PRACTICE]
        duration = QTime(0, duration, 0)
        
        # Compare the duration with the minimum duration
        if duration < min_duration:
            # Adjust the end practice time based on the difference in minutes
            end_practice = end_practice.addSecs((min_duration.minute() - duration.minute()) * 60)
            self.stop_time_practice_rounds.setTime(end_practice)
    
    @Slot()
    def validate_table_times(self):
        """Validates the table times based on the minimum duration and the round type duration."""
        start_table = self.start_time_table_rounds.time()
        end_table = self.stop_time_table_rounds.time()
        min_duration = self.minimum_table_duration.time()
        duration = self.time_data.ROUND_TYPE_DURATIONS[TABLE]
        duration = QTime(0, duration, 0)

        if duration < min_duration:
            end_table = end_table.addSecs((min_duration.minute() - duration.minute()) * 60)
            self.stop_time_table_rounds.setTime(end_table)

    @Slot()
    def update_schedule_data(self):
        """Updates the GUI based on the current inputs."""
        self.schedule_data.NUM_TEAMS = self.num_teams_spinbox.value()
        self.schedule_data.NUM_ROOMS = self.num_rooms_spinbox.value()
        self.schedule_data.NUM_TABLES = self.num_tables_spinbox.value()
        self.schedule_data.ROUND_TYPE_PER_TEAM['practice'] = self.round_type_spinboxes['practice'].value()
        self.schedule_data.ROUND_TYPE_PER_TEAM['table'] = self.round_type_spinboxes['table'].value()
        self.schedule_data.num_tables_and_sides = self.schedule_data.NUM_TABLES * 2
        self.num_tables_and_sides_label.setText(str(self.schedule_data.num_tables_and_sides))
        for name in [JUDGING, PRACTICE, TABLE]:
            self.round_type_labels[name].setText(f"{self.schedule_data.NUM_TEAMS * self.schedule_data.ROUND_TYPE_PER_TEAM[name]} Rounds")

    @Slot()
    def update_time_data(self):
        """Updates the TimeData with current GUI inputs."""
        jStop = self.start_time_judging_rounds.time().addSecs(self.time_data.ROUND_TYPE_DURATIONS[JUDGING] * 60 * self.time_data.MINIMUM_SLOTS_REQUIRED[JUDGING])
        self.judging_stop_time.setText(jStop.toString("HH:mm"))

        self.time_data.JUDGING_ROUNDS_START_TIME = self.start_time_judging_rounds.time().toString("hh:mm")
        self.time_data.PRACTICE_ROUNDS_START_TIME = self.start_time_practice_rounds.time().toString("hh:mm")
        self.time_data.PRACTICE_ROUNDS_STOP_TIME = self.stop_time_practice_rounds.time().toString("hh:mm")
        self.time_data.TABLE_ROUNDS_START_TIME = self.start_time_table_rounds.time().toString("hh:mm")
        self.time_data.TABLE_ROUNDS_STOP_TIME = self.stop_time_table_rounds.time().toString("hh:mm")
        self.time_data.update_time_data()

    @Slot()
    def on_update(self):
        self.update_schedule_data()
        self.update_time_data()
        
        # Update soft constraint weights
        for constraint in self.soft_constraint_weights:
            self.q_learning.soft_constraints_weight[constraint] = self.soft_constraint_weights[constraint].value() / 100.0
            self.constraint_labels[constraint].setText(f'{constraint}: {self.q_learning.soft_constraints_weight[constraint] * 100:.2f}%')

        self.q_learning.gui_refresh_interval = self.gui_refresh_rate.value()

        # Update Q-Learning parameters
        self.q_learning.learning_rate = self.alpha_spinbox.value()
        self.q_learning.discount_factor = self.gamma_spinbox.value()
        self.q_learning.epsilon_start = self.epsilon_start_spinbox.value()
        self.q_learning.epsilon_end = self.epsilon_end_spinbox.value()
        self.q_learning.epsilon_decay = self.epsilon_decay_spinbox.value()
        self.q_learning.training_episodes = self.training_episodes_spinbox.value()
        self.q_learning.initialize_schedule_and_states()

        halfway_decay, total_decay, self.decays = self.calculate_epsilon_decay_episodes()
        self.epsilon_halfway_label.setText(f'{halfway_decay} Episodes')
        self.epsilon_total_label.setText(f'{total_decay} Episodes')

        self.progress_bar.setMaximum(self.q_learning.training_episodes)
        self.q_learning.required_schedule_slots = sum(self.schedule_data.ROUND_TYPE_PER_TEAM.values()) * self.schedule_data.NUM_TEAMS
        self.q_learning.possible_schedule_slots = self.schedule_data.NUM_ROOMS * self.time_data.MINIMUM_SLOTS_REQUIRED[JUDGING] + self.schedule_data.num_tables_and_sides * (self.time_data.MINIMUM_SLOTS_REQUIRED[PRACTICE] + self.time_data.MINIMUM_SLOTS_REQUIRED[TABLE])
        self.q_learning.q_table_size_limit = len(self.q_learning.states) * self.schedule_data.NUM_TEAMS

        # Update current stats
        self.q_learning_label.setText(f"Epsilon: {self.q_learning.epsilon:.2f} \nAlpha: {self.q_learning.learning_rate:.2f} \nGamma: {self.q_learning.discount_factor:.2f} \nEpisodes: {self.q_learning.training_episodes}")
        self.current_schedule_length_label.setText(f"Required Schedule Slots: {self.q_learning.required_schedule_slots} ({self.q_learning.possible_schedule_slots} Possible)")
        self.q_table_size_label.setText(f"Q-Table Size: {len(self.q_learning.q_table)}/{self.q_learning.q_table_size_limit}")

        self.q_learning.practice_teams_available = list(self.schedule_data.teams.keys()) * self.schedule_data.ROUND_TYPE_PER_TEAM[PRACTICE]
        self.q_learning.table_teams_available = list(self.schedule_data.teams.keys()) * self.schedule_data.ROUND_TYPE_PER_TEAM[TABLE]

        # Update TimeData with current GUI inputs
        self.practice_round_duration.setText(f'{self.time_data.ROUND_TYPE_DURATIONS[PRACTICE]} minutes')
        self.table_round_duration.setText(f'{self.time_data.ROUND_TYPE_DURATIONS[TABLE]} minutes')
        self.practice_time_available.setText(f'{self.time_data.available_practice_duration} minutes')
        self.table_time_available.setText(f'{self.time_data.available_table_duration} minutes')

        self.status_label.setText(f"Waiting for User to Complete Initialization")
        self.initialize_schedule_display()

        self.validate_practice_times()
        self.validate_table_times()

    @Slot(int)
    def update_gui_total(self, episode):
        """Updates the GUI based on the current episode."""
        if episode == -1: # Benchmarks
            self.progress_bar.setValue(0)
            self.status_label.setText(f"Generating Benchmarks...")
            self.train_button.setText("Generating Benchmarks...")
            self.train_button.setDisabled(True)
            # self.scheduleScoresPlot.plot_schedule_scores('benchmark', 10, self.q_learning.scores, self.q_learning.completion_percentage)
            
            self.worker.signals.gui_updated_signal.emit()
        else:
            if episode == -2: # Optimal
                self.avg_reward_label.setText(f"Average Reward: Optimized")
                self.status_label.setText(f"Optimal Scheduling: Scheduling complete!\nOptimal Schedule Generated at exports/grid_optimal_schedule.xlsx")
                self.q_learning_label.setText(f"Epsilon: {self.q_learning.epsilon:.2f} (Final)\nAlpha: {self.q_learning.learning_rate:.2f}\nGamma: {self.q_learning.discount_factor:.2f}\nEpisodes: {self.q_learning.training_episodes}")
                self.q_table_size_label.setText(f"Q-Table Size: {len(self.q_learning.q_table)}/{self.q_learning.q_table_size_limit} (Final)")

                # self.scheduleScoresPlot.plot_schedule_scores('optimal', episode, self.q_learning.scores, self.q_learning.completion_percentage)
                
                # Update the schedule display
                self.initialize_schedule_display()
                self.progress_bar.setValue(self.q_learning.training_episodes)
                self.train_button.setDisabled(False)
                self.train_button.setText("Close Window")
                self.worker.signals.gui_updated_signal.emit()
                
            elif episode > 0 and episode % self.gui_refresh_rate.value() == 0:
                # Basic Stats
                self.avg_reward_label.setText(f"Average Reward: {self.q_learning.average_rewards[-1]:.2f}")
                self.status_label.setText(f"Episode {episode} : Scheduling in progress...")

                self.q_learning_label.setText(f"Epsilon: {self.q_learning.epsilon:.2f}\nAlpha: {self.q_learning.learning_rate:.2f}\nGamma: {self.q_learning.discount_factor:.2f}\nEpisodes: {self.q_learning.training_episodes}")
                self.q_table_size_label.setText(f"Q-Table Size: {len(self.q_learning.q_table)}/{self.q_learning.q_table_size_limit}")
                
                # Update the schedule display
                self.initialize_schedule_display()
                self.progress_bar.setValue(episode)
                self.train_button.setText(f'Training in Progress...{episode}/{self.q_learning.training_episodes}')
                self.worker.signals.gui_updated_signal.emit()
        
        self.worker.signals.gui_updated_signal.emit()

        if not self.thread.isRunning():
            print(f"Thread {self.thread} Stopped")
            return

if __name__ == "__main__":
    """Run the main application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Centering the window
    screen_geometry = QApplication.primaryScreen().availableGeometry()  # Get screen dimensions
    window_geometry = window.frameGeometry()
    center_point = screen_geometry.center()  
    window_geometry.moveCenter(center_point)  
    window.move(window_geometry.topLeft())  
    
    # Focus window
    window.activateWindow()  
    window.raise_()  

    app.exec()
