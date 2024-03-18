"""This module contains the main window class for the scheduler application."""
import os
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
from PySide6.QtCore import QTime, Qt, QThread, QMetaObject, Q_ARG, Slot, QTranslator, QCoreApplication, QLocale, QEvent
from PySide6.QtGui import QFont
from schedule_data import ScheduleData
from time_data import TimeData
from q_learning import QLearning
from descriptive_stats import MplWidget
from training_thread import TrainingWorker

# TASKS
# TODO implement: translation feature
# TODO maybe: using a dependency injection framework or design pattern

FONT_SIZE_HEADER = 12
FONT_SIZE_SUBHEADER = 10
FONT_WEIGHT_BOLD = QFont.Bold


class MainWindow(QWidget):
    """The main window class for the scheduler application."""
    
    def __init__(self): 
        """Initializes the main class of the scheduler application."""
        super().__init__()
        self.setWindowTitle("FIRST LEGO League Challenge Q-Learning Tournament Scheduler")
        
        self.create_exports_directory()
        self.scheduleData = ScheduleData()
        self.timeData = TimeData(self.scheduleData)
        self.qLearning = QLearning(self.scheduleData, self.timeData)
        
        self.create_gui_components()
        self.initialize_gui_components()
        self.setup_gui_components()
        self.connect_signals_and_slots()
        self.initialize_main_gui()
        
        self.translator = QTranslator() # TODO
        self.current_language = "en"  # Default language
    
    def create_exports_directory(self):
        """Creates the exports directory if it does not exist.
        
        Structure for ./exports directory:
            ./exports
            ├── /aggregate_stats
                ├── aggregate_statistics_Benchmarks.csv
                ├── aggregate_statistics_Optimal.csv
                ├── aggregate_statistics_Training.csv
            ├── /schedule_evaluation
                ├── evaluation_results.csv
            ├── /training_schedules_output
                ├── schedule_episode_{int}.csv
                ├── schedule_episode_benchmark.csv
            ├── grid_optimal_schedule.xlsx
            ├── optimal_schedule.csv
            ├── q_table.csv
            
        """
        exports_directory = "./exports"
        if not os.path.exists(exports_directory):
            os.makedirs(exports_directory)
            os.makedirs(f'{exports_directory}/aggregate_stats')
            os.makedirs(f'{exports_directory}/schedule_evaluation')
            os.makedirs(f'{exports_directory}/training_schedules_output')
    
    def create_gui_components(self): 
        """Creates the GUI components for the scheduler application."""
        self.create_schedule_data_inputs()
        self.create_time_data_inputs()
        self.create_q_learning_inputs()
        self.create_statistics_and_progress()
        self.create_visualizations()
        self.create_schedule_display()
        self.create_submission_buttons()
        self.create_soft_constraint_weights()

    def initialize_gui_components(self):
        """Initializes the GUI components of the scheduler."""
        self.initialize_schedule_data_inputs()
        self.initialize_time_data_inputs()
        self.initialize_q_learning_inputs()
        self.initialize_statistics_and_progress()
        self.initialize_schedule_display()

    def setup_gui_components(self):
        """Sets up the GUI components for the scheduler."""
        self.setup_schedule_data_inputs()
        self.setup_time_data_inputs()
        self.setup_q_learning_inputs()
        self.setup_statistics()
        self.setup_schedule_display()
    
    def create_schedule_data_inputs(self): 
        """Creates the schedule data inputs for the application."""
        self.numTeamsSpinbox = QSpinBox(self)
        self.numRoomsSpinbox = QSpinBox(self)
        self.numTablesSpinbox = QSpinBox(self)
        self.numTablesAndSidesLabel = QLabel(str(self.scheduleData.num_tables_and_sides))
        self.roundTypeGroupBox = QGroupBox("Round Types Per Team")
        self.roundTypeLayout = QGridLayout(self.roundTypeGroupBox)

        self.roundTypeSpinboxes = {
            "judging": QLabel(f'{1}'),
            "practice": QSpinBox(self),
            "table": QSpinBox(self),
        }

        self.roundTypeLabels = {}

        for name, spinbox in self.roundTypeSpinboxes.items():
            self.roundTypeLabels[name] = QLabel(f"{self.scheduleData.num_teams * self.scheduleData.round_types_per_team[name]} Rounds")

        self.roundTypeSpinboxes["judging"].setFont(QFont("Sans", 8, FONT_WEIGHT_BOLD))
        
    def initialize_schedule_data_inputs(self): 
        """Initializes the schedule data inputs based on the values stored in the `scheduleData` object."""
        self.numTeamsSpinbox.setValue(self.scheduleData.num_teams)
        self.numRoomsSpinbox.setValue(self.scheduleData.num_rooms)
        self.numTablesSpinbox.setValue(self.scheduleData.num_tables)
        for name, spinbox in self.roundTypeSpinboxes.items():
            if name == "judging":
                continue
            spinbox.setValue(self.scheduleData.round_types_per_team[name])

    def setup_schedule_data_inputs(self): 
        """Sets up the schedule data inputs in the GUI."""
        # ScheduleData Inputs Widgets
        self.scheduleDataInputsGroupBox = QGroupBox("Schedule Data Inputs")
        self.scheduleDataLayout = QGridLayout(self.scheduleDataInputsGroupBox)
        self.scheduleDataLayout.addWidget(QLabel("Number of Teams"), 0, 0)
        self.scheduleDataLayout.addWidget(self.numTeamsSpinbox, 0, 1)
        self.scheduleDataLayout.addWidget(QLabel("Number of Rooms"), 1, 0)
        self.scheduleDataLayout.addWidget(self.numRoomsSpinbox, 1, 1)
        self.scheduleDataLayout.addWidget(QLabel("Number of Tables"), 2, 0)
        self.scheduleDataLayout.addWidget(self.numTablesSpinbox, 2, 1)
        self.scheduleDataLayout.addWidget(QLabel("Number of Tables and Sides: "), 3, 0)
        self.scheduleDataLayout.addWidget(self.numTablesAndSidesLabel, 3, 1, Qt.AlignRight)
        
        # Round Types per Team Inputs Widgets
        count = 0
        for name, spinbox in self.roundTypeSpinboxes.items():
            if name == 'judging':
                jlabel = QLabel(f'Judging')
                jlabel.setFont(QFont('Sans', 8, FONT_WEIGHT_BOLD))
                self.roundTypeLayout.addWidget(jlabel, count, 0)
            else:
                self.roundTypeLayout.addWidget(QLabel(name.capitalize()), count, 0)
            self.roundTypeLayout.addWidget(spinbox, count, 1)
            self.roundTypeLayout.addWidget(self.roundTypeLabels[name], count, 2, Qt.AlignRight)
            count += 1
        
    def create_time_data_inputs(self): 
        """Creates the time data inputs for the application."""
        # Create time edit widgets for start time and stop time of judging rounds, practice rounds, and table rounds
        self.startTimeJudgingRounds = QTimeEdit(self)
        self.startTimePracticeRounds = QTimeEdit(self)
        self.stopTimePractice = QTimeEdit(self)
        self.startTimeTableRounds = QTimeEdit(self)
        self.stopTimeTableRounds = QTimeEdit(self)

        # Set the duration labels for judging rounds, practice rounds, and table rounds
        self.judgingRoundDuration = QLabel(f'{45} minutes')
        self.judgingRoundDuration.setFont(QFont("Sans", 8, FONT_WEIGHT_BOLD))
        self.practiceRoundDuration = QLabel(f'{self.timeData.round_type_durations["practice"]} minutes')
        self.tableRoundDuration = QLabel(f'{self.timeData.round_type_durations["table"]} minutes')

        # Create time edit widgets for minimum practice duration and minimum table duration
        self.minimumPracticeDuration = QTimeEdit(self)
        self.minimumPracticeDuration.setDisplayFormat('mm')
        self.minimumTableDuration = QTimeEdit(self)
        self.minimumTableDuration.setDisplayFormat('mm')

        # Create labels for minimum practice duration and minimum table duration
        self.minimumPracticeDurationLabel = QLabel('Minimum Practice Duration: ')
        self.minimumTableDurationLabel = QLabel('Minimum Table Duration:')

        # Display the available practice time and available table time labels
        self.practiceTimeAvailable = QLabel(f'{self.timeData.available_practice_duration} minutes')
        self.tableTimeAvailable = QLabel(f'{self.timeData.available_table_duration} minutes')
    
    def initialize_time_data_inputs(self): 
        """Initializes the time data inputs based on the values stored in the `timeData` object."""
        self.minimumPracticeDuration.setTime(QTime.fromString(str(self.timeData.round_type_durations["practice"]), 'mm'))
        self.minimumTableDuration.setTime(QTime.fromString(str(self.timeData.round_type_durations["table"]), 'mm'))
        self.startTimeJudgingRounds.setTime(QTime.fromString(self.timeData.judging_rounds_start_time, 'HH:mm'))
        self.startTimePracticeRounds.setTime(QTime.fromString(self.timeData.practice_rounds_start_time, 'HH:mm'))
        self.stopTimePractice.setTime(QTime.fromString(self.timeData.practice_rounds_stop_time, 'HH:mm'))
        self.startTimeTableRounds.setTime(QTime.fromString(self.timeData.table_rounds_start_time, 'HH:mm'))
        self.stopTimeTableRounds.setTime(QTime.fromString(self.timeData.table_rounds_stop_time, 'HH:mm'))
    
    def setup_time_data_inputs(self): 
        """Sets up the time data inputs in the GUI."""
        self.timeDataInputsGroupBox = QGroupBox("Time Data Inputs")
        self.timeDataLayout = QGridLayout(self.timeDataInputsGroupBox)
        
        self.judgingRoundDurationLabelConstant = QLabel("Judging Round Duration")
        self.judgingRoundDurationLabelConstant.setFont(QFont("Sans", 8, FONT_WEIGHT_BOLD))
        self.timeDataLayout.addWidget(self.judgingRoundDurationLabelConstant, 0, 0)
        self.timeDataLayout.addWidget(self.judgingRoundDuration, 0, 1)
        
        self.timeDataLayout.addWidget(QLabel("Practice Round Duration"), 1, 0)
        self.timeDataLayout.addWidget(self.practiceRoundDuration, 1, 1)
        
        self.timeDataLayout.addWidget(self.minimumPracticeDurationLabel, 2, 0)
        self.timeDataLayout.addWidget(self.minimumPracticeDuration, 2, 1)
        
        self.timeDataLayout.addWidget(QLabel("Table Round Duration"), 3, 0)
        self.timeDataLayout.addWidget(self.tableRoundDuration, 3, 1)
        
        self.timeDataLayout.addWidget(self.minimumTableDurationLabel, 4, 0)
        self.timeDataLayout.addWidget(self.minimumTableDuration, 4, 1)
        
        self.timeDataLayout.addWidget(QLabel("Judging Rounds-Start"), 5, 0)
        self.timeDataLayout.addWidget(self.startTimeJudgingRounds, 5, 1)
        
        self.judgingStopTimeProjectionLabel = QLabel(f'Judging Rounds-Stop')
        self.judgingStopTime = self.startTimeJudgingRounds.time().addSecs(self.timeData.round_type_durations["judging"] * 60 * self.timeData.minimum_slots_required["judging"])
        self.judgingStopTime = QLabel(self.judgingStopTime.toString("HH:mm"))
        self.timeDataLayout.addWidget(self.judgingStopTimeProjectionLabel, 6, 0)
        self.timeDataLayout.addWidget(self.judgingStopTime, 6, 1)
        
        self.timeDataLayout.addWidget(QLabel("Practice Rounds-Start"), 7, 0)
        self.timeDataLayout.addWidget(self.startTimePracticeRounds, 7, 1)
        
        self.timeDataLayout.addWidget(QLabel("Practice Rounds-Stop"), 8, 0)
        self.timeDataLayout.addWidget(self.stopTimePractice, 8, 1)
        
        self.timeDataLayout.addWidget(QLabel("Table Rounds-Start"), 9, 0)
        self.timeDataLayout.addWidget(self.startTimeTableRounds, 9, 1)
        
        self.timeDataLayout.addWidget(QLabel("Table Rounds-Stop"), 10, 0)
        self.timeDataLayout.addWidget(self.stopTimeTableRounds, 10, 1)
        
        self.timeDataLayout.addWidget(QLabel("Practice Time Available"), 11, 0)
        self.timeDataLayout.addWidget(self.practiceTimeAvailable, 11, 1)
        
        self.timeDataLayout.addWidget(QLabel("Table Time Available"), 12, 0)
        self.timeDataLayout.addWidget(self.tableTimeAvailable, 12, 1)
    
    def create_q_learning_inputs(self):
        """Creates the Q-learning inputs for the application."""
        self.alphaInput = QDoubleSpinBox(self)
        self.gammaInput = QDoubleSpinBox(self)
        self.epsilonStartInput = QDoubleSpinBox(self)
        self.epsilonEndInput = QDoubleSpinBox(self)
        self.epsilonDecayInput = QDoubleSpinBox(self, decimals=3)
        self.episodesInput = QSpinBox(self)
    
    def initialize_q_learning_inputs(self):
        """Initializes the Q-learning inputs based on the values stored in the `qLearning` object."""
        self.alphaInput.setValue(self.qLearning.learning_rate)
        self.alphaInput.setRange(0.01, 1.00)
        self.alphaInput.setSingleStep(0.01)
        
        self.gammaInput.setValue(self.qLearning.discount_factor)
        self.gammaInput.setRange(0.01, 1.00)
        self.gammaInput.setSingleStep(0.01)
        
        self.epsilonStartInput.setValue(self.qLearning.epsilon_start)
        self.epsilonStartInput.setRange(0.01, 1.00)
        self.epsilonStartInput.setSingleStep(0.01)
        
        self.epsilonEndInput.setValue(self.qLearning.epsilon_end)
        self.epsilonEndInput.setRange(0.01, 1.00) 
        self.epsilonEndInput.setSingleStep(0.01)     
          
        self.epsilonDecayInput.setValue(self.qLearning.epsilon_decay)
        self.epsilonDecayInput.setRange(0.001, 1.000)
        self.epsilonDecayInput.setSingleStep(0.001)
        
        self.episodesInput.setValue(self.qLearning.training_episodes)
        self.episodesInput.setRange(1, 100000)
              
    def setup_q_learning_inputs(self):
        """Sets up the Q-learning inputs in the GUI."""
        halfway_decay, total_decay, self.decays = self.calculate_epsilon_decay_episodes()
        self.epsilonHalfwayLabel = QLabel(f'{halfway_decay} Episodes')
        self.epsilonTotalLabel = QLabel(f'{total_decay} Episodes')
        
        self.qLearningInputsGroupBox = QGroupBox("Q-Learning Inputs")
        self.qLearningLayout = QGridLayout(self.qLearningInputsGroupBox)
        self.qLearningLayout.addWidget(QLabel("Learning Rate (α)"), 0, 0)
        self.qLearningLayout.addWidget(self.alphaInput, 0, 1)
        self.qLearningLayout.addWidget(QLabel("Discount Factor (γ)"), 1, 0)
        self.qLearningLayout.addWidget(self.gammaInput, 1, 1)
        self.qLearningLayout.addWidget(QLabel("Epsilon Start (Ɛ)"), 2, 0)
        self.qLearningLayout.addWidget(self.epsilonStartInput, 2, 1)
        self.qLearningLayout.addWidget(QLabel("Epsilon End (Ɛ)"), 3, 0)
        self.qLearningLayout.addWidget(self.epsilonEndInput, 3, 1)
        self.qLearningLayout.addWidget(QLabel("Epsilon Decay (Ɛ)"), 4, 0)
        self.qLearningLayout.addWidget(self.epsilonDecayInput, 4, 1)
        self.qLearningLayout.addWidget(QLabel("Max Training Episodes"), 5, 0)
        self.qLearningLayout.addWidget(self.episodesInput, 5, 1)
        self.qLearningLayout.addWidget(QLabel(f'Epsilon 50% at: '), 6, 0)
        self.qLearningLayout.addWidget(self.epsilonHalfwayLabel, 6, 1)
        self.qLearningLayout.addWidget(QLabel(f'Epsilon End at:'), 7, 0)
        self.qLearningLayout.addWidget(self.epsilonTotalLabel, 7, 1)
        
    def create_statistics_and_progress(self): 
        """Creates the statistics and progress for the Q-learning scheduler."""
        self.progressBar = QProgressBar(self)
        self.avgRewardLabel = QLabel("Average Reward: ")
        self.CurrentScheduleLengthLabel = QLabel(f"Required Schedule Slots: {self.qLearning.required_schedule_slots} ({self.qLearning.possible_schedule_slots} Possible)")
        
        self.statusLabel = QLabel("Waiting for User to Complete Initialization")
        self.q_learningLabel = QLabel(f"Epsilon: {self.qLearning.epsilon:.2f}\nAlpha: {self.qLearning.learning_rate:.2f}\nGamma: {self.qLearning.discount_factor:.2f}\nEpisodes: {self.qLearning.training_episodes}")
        self.q_tableSizeLabel = QLabel(f"Q-Table Size: {len(self.qLearning.q_table)}/{self.qLearning.q_table_size_limit}")
        
        self.guiRefreshLayout = QHBoxLayout()
        
        self.guiRefreshLabel = QLabel("Refresh GUI every: ")
        self.guiRefreshRate = QSpinBox(self)
        
        self.guiRefreshLayout.addWidget(self.guiRefreshLabel)
        self.guiRefreshLayout.addWidget(self.guiRefreshRate)
        self.guiRefreshLayout.addWidget(QLabel("Episodes"))
        
    def initialize_statistics_and_progress(self):
        """Initializes the statistics and progress for the Q-learning scheduler."""
        self.progressBar.setMaximum(self.qLearning.training_episodes)
        self.CurrentScheduleLengthLabel.setText(f"Required Schedule Slots: {self.qLearning.required_schedule_slots} ({self.qLearning.possible_schedule_slots} Possible)")
        self.guiRefreshRate.setValue(self.qLearning.gui_refresh_interval)
    
    def setup_statistics(self): 
        """Sets up the statistics and progress for the Q-learning scheduler."""
        self.statisticsGroupBox = QGroupBox("Training Statistics")
        self.statisticsLayout = QVBoxLayout(self.statisticsGroupBox)
        self.statisticsLayout.addWidget(self.statusLabel)
        self.statisticsLayout.addWidget(self.avgRewardLabel)
        self.statisticsLayout.addWidget(self.CurrentScheduleLengthLabel)
        self.statisticsLayout.addWidget(self.q_tableSizeLabel)
        self.statisticsLayout.addWidget(self.q_learningLabel)
        
        self.statisticsLayout.addWidget(self.progressBar)
        
        self.statisticsLayout.addLayout(self.guiRefreshLayout)
        
    def create_soft_constraint_weights(self):
        """Creates the soft constraint weights for the Q-learning scheduler."""
        # Create the group box and layout for the soft constraint weights
        self.softConstraintWeightsGroupBox = QGroupBox("Soft Constraint Weights")
        self.softConstraintWeightsLayout = QGridLayout(self.softConstraintWeightsGroupBox)

        # Initialize dictionaries to store the sliders and labels for each constraint
        self.softConstraintWeights = {}
        self.constraintLabel = {}

        # Set the scale factor for the slider positions
        scale_factor = 100.0  # Adjust this value based on the precision you need

        # Initialize the row counter
        row = 0

        # Iterate over each constraint and create a slider and label for it
        for constraint in ['Table Consistency', 'Opponent Variety', 'Back to Back Penalty', 'Break Time']:
            # Create the slider for the constraint
            self.softConstraintWeights[constraint] = QSlider(Qt.Horizontal, self)
            self.softConstraintWeights[constraint].setRange(0, 100)  # Adjust this based on the range you need
            self.softConstraintWeights[constraint].setSingleStep(1)
            self.softConstraintWeights[constraint].setTickInterval(10)
            self.softConstraintWeights[constraint].setSliderPosition(self.qLearning.soft_constraints_weight[constraint] * scale_factor)

            # Connect the valueChanged signal of the slider to the on_update method
            self.softConstraintWeights[constraint].valueChanged.connect(self.on_update)

            # Create the label for the constraint
            self.constraintLabel[constraint] = QLabel(f'{constraint}: {self.qLearning.soft_constraints_weight[constraint] * scale_factor:.2f}%')

            # Add the label and slider to the layout
            self.softConstraintWeightsLayout.addWidget(self.constraintLabel[constraint], row, 0, Qt.AlignLeft)
            self.softConstraintWeightsLayout.addWidget(self.softConstraintWeights[constraint], row, 1, Qt.AlignRight)

            # Increment the row counter
            row += 1
            
    def create_visualizations(self): 
        """Creates the visualizations for the Q-learning scheduler."""
        # Initialize the visualizationsLayout
        self.visualizationsLayout = QVBoxLayout()

        # Create MplWidget objects for different plots
        self.qValueConvergencePlot = MplWidget(self)
        self.qValueHeatmapPlot = MplWidget(self)
        self.exploreExploitPlot = MplWidget(self)
        self.scheduleScoresPlot = MplWidget(self)
    
    def create_schedule_display(self): 
        """Creates the schedule display for the Q-learning scheduler."""
        # Judging Rounds Table
        self.judgingTable = QTableWidget()
        self.judgingTable.setColumnCount(self.scheduleData.num_rooms + 1)  # Time + Room columns
        self.judgingTable.setHorizontalHeaderLabels(['Time'] + [f'Room {i+1}' for i in range(self.scheduleData.num_rooms)])

        # Practice Rounds Table
        self.practiceTable = QTableWidget()
        self.practiceTable.setColumnCount(self.scheduleData.num_tables * 2 + 1)  # Time + Table columns
        practice_headers = ['Time'] + [f'Table {chr(65 + i // 2)}{i % 2 + 1}' for i in range(self.scheduleData.num_tables * 2)]
        self.practiceTable.setHorizontalHeaderLabels(practice_headers)

        # Table Rounds Table
        self.tableRoundTable = QTableWidget()
        self.tableRoundTable.setColumnCount(self.scheduleData.num_tables * 2 + 1)  # Time + Table columns
        table_round_headers = ['Time'] + [f'Table {chr(65 + i // 2)}{i % 2 + 1}' for i in range(self.scheduleData.num_tables * 2)]
        self.tableRoundTable.setHorizontalHeaderLabels(table_round_headers)
    
    def initialize_schedule_display(self):
        """Initializes the schedule display for the Q-learning scheduler."""
        # Ensure tables are clear and set up before populating
        self.clearAndSetupTables()

        # Initialize a dictionary to track the last row used for each time in each table
        lastRow = {'judging': {}, 'practice': {}, 'table': {}}

        # Iterate over each entry in the sorted schedule
        for entry in sorted(self.qLearning.schedule, key=lambda x: (x[0], x[2], x[4])):
            time_start, _, round_type, _, location_id, team_id = entry
            tableWidget = self.getTableWidget(round_type)

            # If this time_start has not been used in this table, add a new row for it
            if time_start not in lastRow[round_type]:
                newRow = tableWidget.rowCount()
                tableWidget.insertRow(newRow)
                tableWidget.setItem(newRow, 0, QTableWidgetItem(time_start))  # Set the time in the first column
                lastRow[round_type][time_start] = newRow
            row = lastRow[round_type][time_start]

            # Calculate the column for this entry. Adjust getColIndex to fit your logic
            col = self.getColIndex(round_type, location_id)
            tableWidget.setItem(row, col, QTableWidgetItem(str(team_id)))

    def setup_schedule_display(self): 
        """Sets up the schedule display for the Q-learning scheduler."""
        # Create a vertical splitter for arranging the schedule display
        schedule_splitter = QSplitter(Qt.Vertical)

        # Create the group box for the schedule display
        self.scheduleDisplayGroupBox = QGroupBox("Schedule Display")
        self.scheduleLayout = QVBoxLayout(self.scheduleDisplayGroupBox)

        # Create the group box for the judging rounds display
        self.judgingDisplayGroupBox = QGroupBox("Judging Rounds")
        self.judgingLayout = QVBoxLayout(self.judgingDisplayGroupBox)

        # Create the group box for the practice rounds display
        self.practiceDisplayGroupBox = QGroupBox("Practice Rounds")
        self.practiceLayout = QVBoxLayout(self.practiceDisplayGroupBox)

        # Create the group box for the table rounds display
        self.tableDisplayGroupBox = QGroupBox("Table Rounds")
        self.tableLayout = QVBoxLayout(self.tableDisplayGroupBox)

        # Add the judging table widget to the judging layout
        self.judgingLayout.addWidget(self.judgingTable)

        # Add the practice table widget to the practice layout
        self.practiceLayout.addWidget(self.practiceTable)

        # Add the table round table widget to the table layout
        self.tableLayout.addWidget(self.tableRoundTable)

        # Add the judging display group box to the splitter
        schedule_splitter.addWidget(self.judgingDisplayGroupBox)

        # Add the practice display group box to the splitter
        schedule_splitter.addWidget(self.practiceDisplayGroupBox)

        # Add the table display group box to the splitter
        schedule_splitter.addWidget(self.tableDisplayGroupBox)

        # Add the splitter to the schedule layout
        self.scheduleLayout.addWidget(schedule_splitter)
        
    def clearAndSetupTables(self):
        """Clears and sets up the judging, practice, and table round tables."""
        for table in [self.judgingTable, self.practiceTable, self.tableRoundTable]:
            table.clearContents()  # Clear the contents of the table
            table.setColumnCount(0)  # Clear the columns
            table.setRowCount(0)  # Clear the rows
            table.setAlternatingRowColors(True)  # Enable alternating row colors
            table.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable editing

            if table is self.judgingTable:
                # Set column count and header labels for judging table
                table.setColumnCount(self.scheduleData.num_rooms + 1)
                table.setHorizontalHeaderLabels(['Time'] + [f'Room {i+1}' for i in range(self.scheduleData.num_rooms)])
            else:
                # Set column count and header labels for practice and table round tables
                table.setColumnCount((self.scheduleData.num_tables * 2) + 1)
                table.setHorizontalHeaderLabels(['Time'] + [f'Table {chr(65 + i // 2)}{i % 2 + 1}' for i in range(self.scheduleData.num_tables * 2)])
        
    def getTableWidget(self, round_type):
        """Returns the table widget based on the round type."""
        if round_type == 'judging':
            return self.judgingTable
        elif round_type == 'practice':
            return self.practiceTable
        else:  # 'table'
            return self.tableRoundTable

    def getColIndex(self, round_type, location_id):
        """Returns the column index based on the round type and location ID."""
        if round_type == 'judging':
            return int(location_id)
        else:
            columnBase = ord(location_id[0]) - ord('A') + 1
            columnOffset = int(location_id[1])
            return (columnBase - 1) * 2 + columnOffset

    def create_submission_buttons(self):
        """Creates submission buttons for training and generating optimal schedule."""
        # Submit(Train) Button
        self.trainButton = QPushButton("Train then Generate Optimal Schedule", self)
        self.trainButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
    def connect_signals_and_slots(self):
        """Connects the signals and slots for the scheduler application."""
        # Time Data Inputs
        self.startTimeJudgingRounds.timeChanged.connect(self.on_update)  # Connects the timeChanged signal of startTimeJudgingRounds to the on_update slot function
        
        self.startTimePracticeRounds.timeChanged.connect(self.on_update)  # Connects the timeChanged signal of startTimePracticeRounds to the on_update slot function
        self.stopTimePractice.timeChanged.connect(self.on_update)  # Connects the timeChanged signal of stopTimePractice to the on_update slot function
        
        self.minimumPracticeDuration.timeChanged.connect(self.on_update)  # Connects the timeChanged signal of minimumPracticeDuration to the on_update slot function
        self.minimumTableDuration.timeChanged.connect(self.on_update)  # Connects the timeChanged signal of minimumTableDuration to the on_update slot function
        
        self.startTimeTableRounds.timeChanged.connect(self.on_update)  # Connects the timeChanged signal of startTimeTableRounds to the on_update slot function
        self.stopTimeTableRounds.timeChanged.connect(self.on_update)  # Connects the timeChanged signal of stopTimeTableRounds to the on_update slot function
        
        self.startTimePracticeRounds.timeChanged.connect(self.validate_practice_times)  # Connects the timeChanged signal of startTimePracticeRounds to the validate_practice_times slot function
        self.stopTimePractice.timeChanged.connect(self.validate_practice_times)  # Connects the timeChanged signal of stopTimePractice to the validate_practice_times slot function
        self.minimumPracticeDuration.timeChanged.connect(self.validate_practice_times)  # Connects the timeChanged signal of minimumPracticeDuration to the validate_practice_times slot function
        
        self.startTimeTableRounds.timeChanged.connect(self.validate_table_times)  # Connects the timeChanged signal of startTimeTableRounds to the validate_table_times slot function
        self.stopTimeTableRounds.timeChanged.connect(self.validate_table_times)  # Connects the timeChanged signal of stopTimeTableRounds to the validate_table_times slot function
        self.minimumTableDuration.timeChanged.connect(self.validate_table_times)  # Connects the timeChanged signal of minimumTableDuration to the validate_table_times slot function
        
        # Schedule Data Inputs        
        self.numTeamsSpinbox.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of numTeamsSpinbox to the on_update slot function
        self.numRoomsSpinbox.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of numRoomsSpinbox to the on_update slot function
        self.numTablesSpinbox.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of numTablesSpinbox to the on_update slot function
        self.roundTypeSpinboxes["practice"].valueChanged.connect(self.on_update)  # Connects the valueChanged signal of roundTypeSpinboxes["practice"] to the on_update slot function
        self.roundTypeSpinboxes["table"].valueChanged.connect(self.on_update)  # Connects the valueChanged signal of roundTypeSpinboxes["table"] to the on_update slot function
        
        # Q-Learning Inputs
        self.alphaInput.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of alphaInput to the on_update slot function
        self.gammaInput.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of gammaInput to the on_update slot function
        self.epsilonStartInput.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of epsilonStartInput to the on_update slot function
        self.epsilonEndInput.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of epsilonEndInput to the on_update slot function
        self.epsilonDecayInput.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of epsilonDecayInput to the on_update slot function
        self.episodesInput.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of episodesInput to the on_update slot function
        
        # Statistics and Progress
        self.guiRefreshRate.valueChanged.connect(self.on_update)  # Connects the valueChanged signal of guiRefreshRate to the on_update slot function
        self.softConstraintWeights['Table Consistency'].valueChanged.connect(self.on_update)  # Connects the valueChanged signal of softConstraintWeights['Table Consistency'] to the on_update slot function
        self.softConstraintWeights['Opponent Variety'].valueChanged.connect(self.on_update)  # Connects the valueChanged signal of softConstraintWeights['Opponent Variety'] to the on_update slot function
        self.softConstraintWeights['Back to Back Penalty'].valueChanged.connect(self.on_update)  # Connects the valueChanged signal of softConstraintWeights['Back to Back Penalty'] to the on_update slot function
        self.softConstraintWeights['Break Time'].valueChanged.connect(self.on_update)  # Connects the valueChanged signal of softConstraintWeights['Break Time'] to the on_update slot function
        
        # Buttons
        self.trainButton.clicked.connect(self.start_training_thread)  # Connects the clicked signal of trainButton to the start_training_thread slot function

    def initialize_main_gui(self):
        """Initializes the main GUI for the scheduler application."""
        # self.translate_button = QPushButton("Translate")
        # self.translate_button.clicked.connect(self.translate)

        main_layout = QGridLayout(self)
        column_splitter = QSplitter(Qt.Horizontal)
        left_panel = QSplitter(Qt.Vertical)
        right_panel = QSplitter(Qt.Vertical)
        
        # Add widgets to the left panel
        # left_panel.addWidget(self.translate_button)
        left_panel.addWidget(self.scheduleDataInputsGroupBox)
        left_panel.addWidget(self.roundTypeGroupBox)
        left_panel.addWidget(self.timeDataInputsGroupBox)
        left_panel.addWidget(self.qLearningInputsGroupBox)
        left_panel.addWidget(self.softConstraintWeightsGroupBox)
        left_panel.addWidget(self.statisticsGroupBox)
        left_panel.addWidget(self.trainButton)
        
        # Add widgets to the right panel
        right_panel.addWidget(QLabel("Visualizations", font=QFont("Times", FONT_SIZE_HEADER, FONT_WEIGHT_BOLD)))
        right_panel.addWidget(QLabel("Q-Value Convergence Plot", font=QFont("Times", FONT_SIZE_SUBHEADER, FONT_WEIGHT_BOLD)))
        right_panel.addWidget(self.qValueConvergencePlot)
        right_panel.addWidget(QLabel("Q-Table Heatmap", font=QFont("Times", FONT_SIZE_SUBHEADER, FONT_WEIGHT_BOLD)))
        right_panel.addWidget(self.qValueHeatmapPlot)
        right_panel.addWidget(QLabel("Exploration vs. Exploitation Ratios", font=QFont("Times", FONT_SIZE_SUBHEADER, FONT_WEIGHT_BOLD)))
        right_panel.addWidget(self.exploreExploitPlot)
        right_panel.addWidget(QLabel("Schedule Scores", font=QFont("Times", FONT_SIZE_SUBHEADER, FONT_WEIGHT_BOLD)))
        right_panel.addWidget(self.scheduleScoresPlot)
        
        # Add panels to the column splitter
        column_splitter.addWidget(left_panel)
        column_splitter.addWidget(self.scheduleDisplayGroupBox)
        column_splitter.addWidget(right_panel)
        
        # Add the column splitter to the main layout
        main_layout.addWidget(column_splitter, 0, 0)
    
    def start_training_thread(self):
        """Starts the training thread for the Q-learning scheduler."""
        training_episodes = int(self.episodesInput.value())  # Assuming you have an input field for training_episodes
        self.qLearning.training_episodes = training_episodes
        self.initialize_schedule_display()

        self.thread = QThread()
        self.worker = TrainingWorker(self.qLearning)  # Assuming qLearning is your QLearning instance
        self.worker.moveToThread(self.thread)

        self.worker.signals.update_gui_signal.connect(self.update_gui_total, Qt.QueuedConnection)

        self.thread.started.connect(self.worker.run, Qt.QueuedConnection)

        self.thread.start()

    def calculate_epsilon_decay_episodes(self):
        """Calculates the epsilon decay episodes for the Q-learning scheduler."""
        # Get the initial epsilon, epsilon end, and epsilon decay values
        epsilon_start = self.epsilonStartInput.value()
        epsilon_end = self.epsilonEndInput.value()
        epsilon_decay = self.epsilonDecayInput.value()

        epsilon_halfway = 0.5
        ep_count = 0
        ep_count_half = 0
        epsilon_decay_list = []

        # Calculate epsilon decay until it reaches the end value
        while epsilon_start > epsilon_end:
            epsilon_start *= epsilon_decay
            ep_count += 1

            # Check if epsilon is greater than halfway
            if epsilon_start > epsilon_halfway:
                ep_count_half += 1

            epsilon_decay_list.append(epsilon_start)
            
        return ep_count_half, ep_count, epsilon_decay_list
    
    '''
    # TODO Implement a translation feature
    def changeEvent(self, event): # TODO
        """Handles the change event for the application."""
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def retranslateUi(self): # TODO
        """Retranslates the UI components based on the current language."""
        self.setWindowTitle(QCoreApplication.translate("MainWindow", "FIRST LEGO League Challenge Q-Learning Tournament Scheduler"))
        self.translate_button.setText(QCoreApplication.translate("MainWindow", "Translate"))

    @Slot()
    def translate(self): # TODO
        """Slot to handle the translation of the application."""
        if self.current_language == "en":
            self.current_language = "es"  # Switch to Spanish
            self.translator.load("../translations/es.qm")
        else:
            self.current_language = "en"  # Switch back to English
            self.translator.load("")  # Empty string to remove translations

        QCoreApplication.installTranslator(self.translator)
        self.retranslateUi()
    '''
    
    @Slot()
    def validate_practice_times(self):
        """Validates the practice times based on the minimum duration and the round type duration."""
        # Get the start and end practice times, minimum duration, and default duration
        start_practice = self.startTimePracticeRounds.time()
        end_practice = self.stopTimePractice.time()
        min_duration = self.minimumPracticeDuration.time()
        duration = self.timeData.round_type_durations["practice"]
        duration = QTime(0, duration, 0)
        
        # Compare the duration with the minimum duration
        if duration < min_duration:
            # Adjust the end practice time based on the difference in minutes
            end_practice = end_practice.addSecs((min_duration.minute() - duration.minute()) * 60)
            self.stopTimePractice.setTime(end_practice)
    
    @Slot()
    def validate_table_times(self):
        """Validates the table times based on the minimum duration and the round type duration."""
        start_table = self.startTimeTableRounds.time()
        end_table = self.stopTimeTableRounds.time()
        min_duration = self.minimumTableDuration.time()
        duration = self.timeData.round_type_durations["table"]
        duration = QTime(0, duration, 0)

        if duration < min_duration:
            end_table = end_table.addSecs((min_duration.minute() - duration.minute()) * 60)
            self.stopTimeTableRounds.setTime(end_table)

    def update_schedule_data(self):
        """Updates the GUI based on the current inputs."""
        self.scheduleData.num_teams = self.numTeamsSpinbox.value()
        self.scheduleData.num_rooms = self.numRoomsSpinbox.value()
        self.scheduleData.num_tables = self.numTablesSpinbox.value()
        self.scheduleData.round_types_per_team['practice'] = self.roundTypeSpinboxes['practice'].value()
        self.scheduleData.round_types_per_team['table'] = self.roundTypeSpinboxes['table'].value()
        self.scheduleData.num_tables_and_sides = self.scheduleData.num_tables * 2
        self.numTablesAndSidesLabel.setText(str(self.scheduleData.num_tables_and_sides))
        for name in ["judging", "practice", "table"]:
            self.roundTypeLabels[name].setText(f"{self.scheduleData.num_teams * self.scheduleData.round_types_per_team[name]} Rounds")

    def update_time_data(self):
        """Updates the TimeData with current GUI inputs."""
        jStop = self.startTimeJudgingRounds.time().addSecs(self.timeData.round_type_durations["judging"] * 60 * self.timeData.minimum_slots_required["judging"])
        self.judgingStopTime.setText(jStop.toString("HH:mm"))

        self.timeData.judging_rounds_start_time = self.startTimeJudgingRounds.time().toString("hh:mm")
        self.timeData.practice_rounds_start_time = self.startTimePracticeRounds.time().toString("hh:mm")
        self.timeData.practice_rounds_stop_time = self.stopTimePractice.time().toString("hh:mm")
        self.timeData.table_rounds_start_time = self.startTimeTableRounds.time().toString("hh:mm")
        self.timeData.table_rounds_stop_time = self.stopTimeTableRounds.time().toString("hh:mm")
        self.timeData.update_time_data()

    @Slot()
    def on_update(self):
        self.update_schedule_data()
        self.update_time_data()
        
        # Update soft constraint weights
        for constraint in self.softConstraintWeights:
            self.qLearning.soft_constraints_weight[constraint] = self.softConstraintWeights[constraint].value() / 100.0
            self.constraintLabel[constraint].setText(f'{constraint}: {self.qLearning.soft_constraints_weight[constraint] * 100:.2f}%')

        self.qLearning.gui_refresh_interval = self.guiRefreshRate.value()

        # Update Q-Learning parameters
        self.qLearning.learning_rate = self.alphaInput.value()
        self.qLearning.discount_factor = self.gammaInput.value()
        self.qLearning.epsilon_start = self.epsilonStartInput.value()
        self.qLearning.epsilon_end = self.epsilonEndInput.value()
        self.qLearning.epsilon_decay = self.epsilonDecayInput.value()
        self.qLearning.training_episodes = self.episodesInput.value()
        self.qLearning.initialize_schedule_and_states()

        halfway_decay, total_decay, self.decays = self.calculate_epsilon_decay_episodes()
        self.epsilonHalfwayLabel.setText(f'{halfway_decay} Episodes')
        self.epsilonTotalLabel.setText(f'{total_decay} Episodes')

        self.progressBar.setMaximum(self.qLearning.training_episodes)
        self.qLearning.required_schedule_slots = sum(self.scheduleData.round_types_per_team.values()) * self.scheduleData.num_teams
        self.qLearning.possible_schedule_slots = self.scheduleData.num_rooms * self.timeData.minimum_slots_required["judging"] + self.scheduleData.num_tables_and_sides * (self.timeData.minimum_slots_required["practice"] + self.timeData.minimum_slots_required["table"])
        self.qLearning.q_table_size_limit = len(self.qLearning.states) * self.scheduleData.num_teams

        # Update current stats
        self.q_learningLabel.setText(f"Epsilon: {self.qLearning.epsilon:.2f} \nAlpha: {self.qLearning.learning_rate:.2f} \nGamma: {self.qLearning.discount_factor:.2f} \nEpisodes: {self.qLearning.training_episodes}")
        self.CurrentScheduleLengthLabel.setText(f"Required Schedule Slots: {self.qLearning.required_schedule_slots} ({self.qLearning.possible_schedule_slots} Possible)")
        self.q_tableSizeLabel.setText(f"Q-Table Size: {len(self.qLearning.q_table)}/{self.qLearning.q_table_size_limit}")

        self.qLearning.practice_teams_available = list(self.scheduleData.teams.keys()) * self.scheduleData.round_types_per_team["practice"]
        self.qLearning.table_teams_available = list(self.scheduleData.teams.keys()) * self.scheduleData.round_types_per_team["table"]

        # Update TimeData with current GUI inputs
        self.practiceRoundDuration.setText(f'{self.timeData.round_type_durations["practice"]} minutes')
        self.tableRoundDuration.setText(f'{self.timeData.round_type_durations["table"]} minutes')
        self.practiceTimeAvailable.setText(f'{self.timeData.available_practice_duration} minutes')
        self.tableTimeAvailable.setText(f'{self.timeData.available_table_duration} minutes')

        self.statusLabel.setText(f"Waiting for User to Complete Initialization")
        self.initialize_schedule_display()

        self.validate_practice_times()
        self.validate_table_times()

    @Slot(int)
    def update_gui_total(self, episode):
        """Updates the GUI based on the current episode."""
        if episode == -1: # Benchmarks
            self.progressBar.setValue(0)
            self.statusLabel.setText(f"Generating Benchmarks...")
            self.trainButton.setText("Generating Benchmarks...")
            self.trainButton.setDisabled(True)
            self.scheduleScoresPlot.plot_schedule_scores('benchmark', 10, self.qLearning.scores, self.qLearning.completion_percentage)
            
            self.worker.signals.gui_updated_signal.emit()
        else:
            if episode == -2: # Optimal
                self.avgRewardLabel.setText(f"Average Reward: Optimized")
                self.statusLabel.setText(f"Optimal Scheduling: Scheduling complete!\nOptimal Schedule Generated at exports/grid_optimal_schedule.xlsx")
                self.q_learningLabel.setText(f"Epsilon: {self.qLearning.epsilon:.2f} (Final)\nAlpha: {self.qLearning.learning_rate:.2f}\nGamma: {self.qLearning.discount_factor:.2f}\nEpisodes: {self.qLearning.training_episodes}")
                self.q_tableSizeLabel.setText(f"Q-Table Size: {len(self.qLearning.q_table)}/{self.qLearning.q_table_size_limit} (Final)")

                self.scheduleScoresPlot.plot_schedule_scores('optimal', episode, self.qLearning.scores, self.qLearning.completion_percentage)
                
                # Update the schedule display
                self.initialize_schedule_display()
                self.progressBar.setValue(self.qLearning.training_episodes)
                self.trainButton.setDisabled(False)
                self.trainButton.setText("Close Window")
                self.worker.signals.gui_updated_signal.emit()
                
            elif episode > 0 and episode % self.guiRefreshRate.value() == 0:
                # Basic Stats
                self.avgRewardLabel.setText(f"Average Reward: {self.qLearning.average_rewards[-1]:.2f}")
                self.statusLabel.setText(f"Episode {episode} : Scheduling in progress...")

                self.q_learningLabel.setText(f"Epsilon: {self.qLearning.epsilon:.2f}\nAlpha: {self.qLearning.learning_rate:.2f}\nGamma: {self.qLearning.discount_factor:.2f}\nEpisodes: {self.qLearning.training_episodes}")
                self.q_tableSizeLabel.setText(f"Q-Table Size: {len(self.qLearning.q_table)}/{self.qLearning.q_table_size_limit}")
                
                # Update the Q-value heatmap                  
                aggregated_data = self.qLearning.transform_for_heatmap()
                heatmap_data, round_types, team_ids = self.qLearning.aggregated_data_to_2d_array(aggregated_data)
                self.qValueHeatmapPlot.plot_heatmap(heatmap_data, xticklabels=team_ids, yticklabels=round_types)

                # Update the Q-value convergence plot
                self.qValueConvergencePlot.plot_convergence(list(range(1,episode+1)), self.qLearning.q_value_changes, self.qLearning.average_reward_changes, self.qLearning.training_episodes)

                # Update the exploration vs. exploitation plot
                self.exploreExploitPlot.plot_exploration_exploitation_balance(self.qLearning.num_exploration_counts, self.qLearning.num_exploitation_counts, self.qLearning.training_episodes, self.qLearning.epsilon_start, self.qLearning.epsilon_end, self.decays)

                # Update score plot
                self.scheduleScoresPlot.plot_schedule_scores('training', episode, self.qLearning.scores, self.qLearning.completion_percentage)    
                
                # Update the schedule display
                self.initialize_schedule_display()
                self.progressBar.setValue(episode)
                self.trainButton.setText(f'Training in Progress...{episode}/{self.qLearning.training_episodes}')
                self.worker.signals.gui_updated_signal.emit()
        
        self.worker.signals.gui_updated_signal.emit()

        if not self.thread.isRunning():
            print(f"Thread {self.thread} Stopped")
            return
        
if __name__ == "__main__":
    """Run the main application."""
    app = QApplication([])
    window = MainWindow()
    window.resize(1500, 600)

    # Show window
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
