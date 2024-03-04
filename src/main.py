###############################################################
# Step 1: Import required libraries
###############################################################
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
from PySide6.QtCore import QTime, Qt, QThread, QMetaObject, Q_ARG, Slot
from PySide6.QtGui import QFont
from schedule_data import ScheduleData
from time_data import TimeData
from q_learning import QLearning
from descriptive_stats import MplWidget
from training_thread import TrainingWorker


###############################################################
# Step 2: Define the Main Window GUI ##########################
###############################################################
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize the data objects
        self.scheduleData = ScheduleData()  # Create an instance of ScheduleData
        self.timeData = TimeData(self.scheduleData)  # Create an instance of TimeData
        
        # Initialize the Q-Learning object
        self.qLearning = QLearning(self.scheduleData, self.timeData)
        
        # Create the GUI components
        self.create_schedule_data_inputs()
        self.create_time_data_inputs()
        self.create_q_learning_inputs()
        self.create_statistics_and_progress()
        self.create_visualizations()
        self.create_schedule_display()
        self.create_submission_buttons()
        self.create_soft_constraint_weights()
        
        # Initizlize the GUI components
        self.initialize_schedule_data_inputs()
        self.initialize_time_data_inputs()
        self.initialize_q_learning_inputs()
        self.initialize_statistics_and_progress()
        self.initialize_schedule_display()
        
        # Setup the GUI components
        self.setup_schedule_data_inputs()
        self.setup_time_data_inputs()
        self.setup_q_learning_inputs()
        self.setup_statistics()
        self.setup_schedule_display()
        
        self.initialize_main_gui()
        
        # Connect signals and slots
        self.connect_signals_and_slots()
    
    # Schedule Data
    def create_schedule_data_inputs(self):
        # Basic Schedule Data Inputs
        self.numTeamsSpinbox = QSpinBox(self)
        self.numRoomsSpinbox = QSpinBox(self)
        self.numTablesSpinbox = QSpinBox(self)

        # Count for the number of tables and sides (display)
        self.numTablesAndSidesLabel = QLabel(str(self.scheduleData.num_tables_and_sides))
        
        # Round Types Per Team
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
        
        self.roundTypeSpinboxes["judging"].setFont(QFont("Sans", 8, QFont.Bold))
        
    
    def initialize_schedule_data_inputs(self):
        self.numTeamsSpinbox.setValue(self.scheduleData.num_teams)
        self.numRoomsSpinbox.setValue(self.scheduleData.num_rooms)
        self.numTablesSpinbox.setValue(self.scheduleData.num_tables)
        for name, spinbox in self.roundTypeSpinboxes.items():
            if name == "judging":
                continue
            spinbox.setValue(self.scheduleData.round_types_per_team[name]) 

    def setup_schedule_data_inputs(self):
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
                jlabel.setFont(QFont('Sans', 8, QFont.Bold))
                self.roundTypeLayout.addWidget(jlabel, count, 0)
            else:
                self.roundTypeLayout.addWidget(QLabel(name.capitalize()), count, 0)
            self.roundTypeLayout.addWidget(spinbox, count, 1)
            self.roundTypeLayout.addWidget(self.roundTypeLabels[name], count, 2, Qt.AlignRight)
            count += 1
        
    # Time Data
    def create_time_data_inputs(self):
        self.startTimeJudgingRounds = QTimeEdit(self)
        self.startTimePracticeRounds = QTimeEdit(self)
        self.stopTimePractice = QTimeEdit(self)
        self.startTimeTableRounds = QTimeEdit(self)
        self.stopTimeTableRounds = QTimeEdit(self)
        
        self.judgingRoundDuration = QLabel(f'{45} minutes')
        self.judgingRoundDuration.setFont(QFont("Sans", 8, QFont.Bold))
        
        self.practiceRoundDuration = QLabel(f'{self.timeData.round_durations["practice"]} minutes')
        self.tableRoundDuration = QLabel(f'{self.timeData.round_durations["table"]} minutes')
        
        self.minimumPracticeDuration = QTimeEdit(self)
        self.minimumPracticeDuration.setDisplayFormat('mm')
        self.minimumTableDuration = QTimeEdit(self)
        self.minimumTableDuration.setDisplayFormat('mm')
        
        self.minimumPracticeDurationLabel = QLabel('Minimum Practice Duration: ')
        self.minimumTableDurationLabel = QLabel('Minimum Table Duration:')
        
        self.practiceTimeAvailable = QLabel(f'{self.timeData.practice_duration_available} minutes')
        self.tableTimeAvailable = QLabel(f'{self.timeData.table_duration_available} minutes')
    
    
    def initialize_time_data_inputs(self):
        self.minimumPracticeDuration.setTime(QTime.fromString(str(self.timeData.round_durations["practice"]), 'mm'))
        self.minimumTableDuration.setTime(QTime.fromString(str(self.timeData.round_durations["table"]), 'mm'))
        self.startTimeJudgingRounds.setTime(QTime.fromString(self.timeData.start_time_judging_rounds, 'HH:mm'))
        self.startTimePracticeRounds.setTime(QTime.fromString(self.timeData.start_time_practice_rounds, 'HH:mm'))
        self.stopTimePractice.setTime(QTime.fromString(self.timeData.start_time_break, 'HH:mm'))
        self.startTimeTableRounds.setTime(QTime.fromString(self.timeData.start_time_table_rounds, 'HH:mm'))
        self.stopTimeTableRounds.setTime(QTime.fromString(self.timeData.stop_time_table_rounds, 'HH:mm'))
    
    def setup_time_data_inputs(self):
        self.timeDataInputsGroupBox = QGroupBox("Time Data Inputs")
        self.timeDataLayout = QGridLayout(self.timeDataInputsGroupBox)
        
        self.judgingRoundDurationLabelConstant = QLabel("Judging Round Duration")
        self.judgingRoundDurationLabelConstant.setFont(QFont("Sans", 8, QFont.Bold))
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
        self.judgingStopTime = self.startTimeJudgingRounds.time().addSecs(self.timeData.round_durations["judging"] * 60 * self.timeData.min_slots_required["judging"])
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
    
    # Q-Learning Inputs
    def create_q_learning_inputs(self):
        self.alphaInput = QDoubleSpinBox(self)
        self.gammaInput = QDoubleSpinBox(self)
        self.epsilonStartInput = QDoubleSpinBox(self)
        self.epsilonEndInput = QDoubleSpinBox(self)
        self.epsilonDecayInput = QDoubleSpinBox(self, decimals=3)
        self.episodesInput = QSpinBox(self)
    
    def initialize_q_learning_inputs(self):
        self.alphaInput.setValue(self.qLearning.alpha)
        self.alphaInput.setRange(0.01, 1.00)
        self.alphaInput.setSingleStep(0.01)
        self.gammaInput.setValue(self.qLearning.gamma)
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
        self.episodesInput.setValue(self.qLearning.episodes)
        self.episodesInput.setRange(1, 100000)
              
    def setup_q_learning_inputs(self):
        halfway_decay, total_decay, self.decays = self.calculate_epsilon_decay_episodes()
        self.epsilonHalfwayLabel = QLabel(f'{halfway_decay} episodes')
        self.epsilonTotalLabel = QLabel(f'{total_decay} episodes')
        
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
        
    # Basic Stats
    def create_statistics_and_progress(self):
        self.progressBar = QProgressBar(self)
        self.avgRewardLabel = QLabel("Average Reward: ")
        self.CurrentScheduleLengthLabel = QLabel(f"Required Schedule Slots: {self.qLearning.required_schedule_slots} ({self.qLearning.possible_schedule_slots} Possible)")
        
        self.statusLabel = QLabel("Waiting for User to Complete Initialization")
        self.q_learningLabel = QLabel(f"Epsilon: {self.qLearning.epsilon:.2f}\nAlpha: {self.qLearning.alpha:.2f}\nGamma: {self.qLearning.gamma:.2f}\nEpisodes: {self.qLearning.episodes}")
        self.q_tableSizeLabel = QLabel(f"Q-Table Size: {len(self.qLearning.q_table)}/{self.qLearning.q_table_size_limit}")
        
        self.guiRefreshLayout = QHBoxLayout()
        
        self.guiRefreshLabel = QLabel("Refresh GUI every: ")
        self.guiRefreshRate = QSpinBox(self)
        
        self.guiRefreshLayout.addWidget(self.guiRefreshLabel)
        self.guiRefreshLayout.addWidget(self.guiRefreshRate)
        self.guiRefreshLayout.addWidget(QLabel("Episodes"))
        
    def initialize_statistics_and_progress(self):
        self.progressBar.setMaximum(self.qLearning.episodes)
        self.CurrentScheduleLengthLabel.setText(f"Required Schedule Slots: {self.qLearning.required_schedule_slots} ({self.qLearning.possible_schedule_slots} Possible)")
        self.guiRefreshRate.setValue(self.qLearning.gui_refresh_rate)
    
    def setup_statistics(self):
        self.statisticsGroupBox = QGroupBox("Training Statistics")
        self.statisticsLayout = QVBoxLayout(self.statisticsGroupBox)
        self.statisticsLayout.addWidget(self.statusLabel)
        self.statisticsLayout.addWidget(self.avgRewardLabel)
        self.statisticsLayout.addWidget(self.CurrentScheduleLengthLabel)
        self.statisticsLayout.addWidget(self.q_tableSizeLabel)
        self.statisticsLayout.addWidget(self.q_learningLabel)
        
        self.statisticsLayout.addWidget(self.progressBar)
        
        self.statisticsLayout.addLayout(self.guiRefreshLayout)
        
    # Soft Constraint Weights
    def create_soft_constraint_weights(self):
        self.softConstraintWeightsGroupBox = QGroupBox("Soft Constraint Weights")
        self.softConstraintWeightsLayout = QGridLayout(self.softConstraintWeightsGroupBox)
        self.softConstraintWeights = {}
        self.constraintLabel = {}
        scale_factor = 100.0  # Adjust this value based on the precision you need
        row = 0
        for constraint in ['Table Consistency', 'Opponent Variety', 'Back to Back Penalty', 'Break Time']:
            self.softConstraintWeights[constraint] = QSlider(Qt.Horizontal, self)
            self.softConstraintWeights[constraint].setRange(0, 100)  # Adjust this based on the range you need
            self.softConstraintWeights[constraint].setSingleStep(1)
            self.softConstraintWeights[constraint].setTickInterval(10)
            self.softConstraintWeights[constraint].setSliderPosition(self.qLearning.constraint_weights[constraint] * scale_factor)
            self.softConstraintWeights[constraint].valueChanged.connect(self.on_update)
            self.constraintLabel[constraint] = QLabel(f'{constraint}: {self.qLearning.constraint_weights[constraint] * scale_factor:.2f}%')
            self.softConstraintWeightsLayout.addWidget(self.constraintLabel[constraint], row, 0, Qt.AlignLeft)
            self.softConstraintWeightsLayout.addWidget(self.softConstraintWeights[constraint], row, 1, Qt.AlignRight)
            row += 1
            
    # Visualizations
    def create_visualizations(self):
        self.visualizationsLayout = QVBoxLayout()
        self.qValueConvergencePlot = MplWidget(self)
        self.qValueHeatmapPlot = MplWidget(self)
        self.exploreExploitPlot = MplWidget(self)   
        self.scheduleScoresPlot = MplWidget(self)     
    
    # Schedule Display
    def create_schedule_display(self):
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
        # Assuming self.qLearning.schedule has been filled and is ready to use
        self.clearAndSetupTables()  # Ensure tables are clear and set up before populating

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
        schedule_splitter = QSplitter(Qt.Vertical)
        self.scheduleDisplayGroupBox = QGroupBox("Schedule Display")
        self.scheduleLayout = QVBoxLayout(self.scheduleDisplayGroupBox)
        
        self.judgingDisplayGroupBox = QGroupBox("Judging Rounds")
        self.judgingLayout = QVBoxLayout(self.judgingDisplayGroupBox)
        self.practiceDisplayGroupBox = QGroupBox("Practice Rounds")
        self.practiceLayout = QVBoxLayout(self.practiceDisplayGroupBox)
        self.tableDisplayGroupBox = QGroupBox("Table Rounds")
        self.tableLayout = QVBoxLayout(self.tableDisplayGroupBox)
        
        self.judgingLayout.addWidget(self.judgingTable)
        self.practiceLayout.addWidget(self.practiceTable)
        self.tableLayout.addWidget(self.tableRoundTable)
        
        schedule_splitter.addWidget(self.judgingDisplayGroupBox)
        schedule_splitter.addWidget(self.practiceDisplayGroupBox)
        schedule_splitter.addWidget(self.tableDisplayGroupBox)
        self.scheduleLayout.addWidget(schedule_splitter)        
        
    # Schedule Display Helper Functions
    def clearAndSetupTables(self):
        for table in [self.judgingTable, self.practiceTable, self.tableRoundTable]:
            table.clearContents()
            table.setColumnCount(0)  # Clear the columns
            table.setRowCount(0)  # Clear the rows
            table.setAlternatingRowColors(True)  # Enable alternating row colors
            table.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable editing
            if table is self.judgingTable:
                table.setColumnCount(self.scheduleData.num_rooms + 1)
                table.setHorizontalHeaderLabels(['Time'] + [f'Room {i+1}' for i in range(self.scheduleData.num_rooms)])
            else:
                table.setColumnCount((self.scheduleData.num_tables * 2) + 1)
                table.setHorizontalHeaderLabels(['Time'] + [f'Table {chr(65 + i // 2)}{i % 2 + 1}' for i in range(self.scheduleData.num_tables * 2)])
        
    def getTableWidget(self, round_type):
        if round_type == 'judging':
            return self.judgingTable
        elif round_type == 'practice':
            return self.practiceTable
        else:  # 'table'
            return self.tableRoundTable

    def getColIndex(self, round_type, location_id):
        if round_type == 'judging':
            # Assuming location_id is an integer representing the room number
            return int(location_id)
        else:
            # Convert table identifiers (e.g., "A1") into column indexes
            columnBase = ord(location_id[0]) - ord('A') + 1  # Convert 'A' to 1, 'B' to 2, etc.
            columnOffset = int(location_id[1])  # '1' or '2'
            return (columnBase - 1) * 2 + columnOffset  # Adjust based on your table's column layout

    # Training and Generate Optimal Schedule Buttons
    def create_submission_buttons(self):
        # Submit(Train) Button
        self.trainButton = QPushButton("Train then Generate Optimal Schedule", self)
        self.trainButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
    # Connect signals and slots
    def connect_signals_and_slots(self):
        # Time Data Inputs
        self.startTimeJudgingRounds.timeChanged.connect(self.on_update)
        
        self.startTimePracticeRounds.timeChanged.connect(self.on_update)
        self.stopTimePractice.timeChanged.connect(self.on_update)
        
        self.minimumPracticeDuration.timeChanged.connect(self.on_update)
        self.minimumTableDuration.timeChanged.connect(self.on_update)
        
        self.startTimeTableRounds.timeChanged.connect(self.on_update)
        self.stopTimeTableRounds.timeChanged.connect(self.on_update)
        
        self.startTimePracticeRounds.timeChanged.connect(self.validate_practice_times)
        self.stopTimePractice.timeChanged.connect(self.validate_practice_times)
        self.minimumPracticeDuration.timeChanged.connect(self.validate_practice_times)
        
        self.startTimeTableRounds.timeChanged.connect(self.validate_table_times)
        self.stopTimeTableRounds.timeChanged.connect(self.validate_table_times)
        self.minimumTableDuration.timeChanged.connect(self.validate_table_times)
        
        # Schedule Data Inputs        
        self.numTeamsSpinbox.valueChanged.connect(self.on_update)
        self.numRoomsSpinbox.valueChanged.connect(self.on_update)
        self.numTablesSpinbox.valueChanged.connect(self.on_update)
        self.roundTypeSpinboxes["practice"].valueChanged.connect(self.on_update)
        self.roundTypeSpinboxes["table"].valueChanged.connect(self.on_update)
        
        # Q-Learning Inputs
        self.alphaInput.valueChanged.connect(self.on_update)
        self.gammaInput.valueChanged.connect(self.on_update)
        self.epsilonStartInput.valueChanged.connect(self.on_update)
        self.epsilonEndInput.valueChanged.connect(self.on_update)
        self.epsilonDecayInput.valueChanged.connect(self.on_update)
        self.episodesInput.valueChanged.connect(self.on_update)
        
        # Statistics and Progress
        self.guiRefreshRate.valueChanged.connect(self.on_update)
        self.softConstraintWeights['Table Consistency'].valueChanged.connect(self.on_update)
        self.softConstraintWeights['Opponent Variety'].valueChanged.connect(self.on_update)
        self.softConstraintWeights['Back to Back Penalty'].valueChanged.connect(self.on_update)
        self.softConstraintWeights['Break Time'].valueChanged.connect(self.on_update)
        
        # Buttons
        self.trainButton.clicked.connect(self.start_training_thread)

    # Main Layout
    def initialize_main_gui(self):
        # Main Layout
        self.layout = QGridLayout(self)
        col_splitter = QSplitter(Qt.Horizontal)
        left_splitter = QSplitter(Qt.Vertical)
        right_splitter = QSplitter(Qt.Vertical)
        # Adding subgroups and widgets to the main layout
        
        left_splitter.addWidget(self.scheduleDataInputsGroupBox)
        left_splitter.addWidget(self.roundTypeGroupBox)
        left_splitter.addWidget(self.timeDataInputsGroupBox)
        left_splitter.addWidget(self.qLearningInputsGroupBox)
        left_splitter.addWidget(self.softConstraintWeightsGroupBox)
        left_splitter.addWidget(self.statisticsGroupBox)
        left_splitter.addWidget(self.trainButton)
        right_splitter.addWidget(QLabel("Visualizations", font=QFont("Times", 12, QFont.Bold)))
        right_splitter.addWidget(QLabel("Q-Value Convergence Plot", font=QFont("Times", 10, QFont.Bold)))
        right_splitter.addWidget(self.qValueConvergencePlot)
        right_splitter.addWidget(QLabel("Q-Table Heatmap", font=QFont("Times", 10, QFont.Bold)))
        right_splitter.addWidget(self.qValueHeatmapPlot)
        right_splitter.addWidget(QLabel("Exploration vs. Exploitation Ratios", font=QFont("Times", 10, QFont.Bold)))
        right_splitter.addWidget(self.exploreExploitPlot)
        right_splitter.addWidget(QLabel("Schedule Scores", font=QFont("Times", 10, QFont.Bold)))
        right_splitter.addWidget(self.scheduleScoresPlot)
        
        col_splitter.addWidget(left_splitter)
        col_splitter.addWidget(self.scheduleDisplayGroupBox)
        col_splitter.addWidget(right_splitter)
        
        self.layout.addWidget(col_splitter, 0, 0)
    
    # Thread
    def start_training_thread(self):
        episodes = int(self.episodesInput.value())  # Assuming you have an input field for episodes
        self.qLearning.episodes = episodes
        self.initialize_schedule_display()

        self.thread = QThread()
        self.worker = TrainingWorker(self.qLearning)  # Assuming qLearning is your QLearning instance
        self.worker.moveToThread(self.thread)
        
        self.worker.signals.update_gui_signal.connect(self.update_gui_total, Qt.QueuedConnection)
        
        self.thread.started.connect(self.worker.run, Qt.QueuedConnection)
        
        self.thread.start()

    # Calculate number of episodes for Epsilon to decay to 50%
    def calculate_epsilon_decay_episodes(self):
        epsilon_start = self.epsilonStartInput.value()
        epsilon_end = self.epsilonEndInput.value()
        epsilon_decay = self.epsilonDecayInput.value()
        epsilon_halfway = 0.5
        ep_count = 0
        ep_count_half = 0
        epsilon_decay_list = []
        while epsilon_start > epsilon_end:
            epsilon_start *= epsilon_decay
            ep_count += 1
            if epsilon_start > epsilon_halfway:
                ep_count_half += 1
            epsilon_decay_list.append(epsilon_start)
            
        return ep_count_half, ep_count, epsilon_decay_list

    # Slots
    @Slot()
    def validate_practice_times(self):
        start_practice = self.startTimePracticeRounds.time()
        end_practice = self.stopTimePractice.time()
        min_duration = self.minimumPracticeDuration.time()
        duration = self.timeData.round_durations["practice"]
        duration = QTime(0, duration, 0)
        
        if duration < min_duration:
            end_practice = end_practice.addSecs((min_duration.minute() - duration.minute()) * 60)
            self.stopTimePractice.setTime(end_practice)
    
    @Slot()
    def validate_table_times(self):
        start_table = self.startTimeTableRounds.time()
        end_table = self.stopTimeTableRounds.time()
        min_duration = self.minimumTableDuration.time()
        duration = self.timeData.round_durations["table"]
        duration = QTime(0, duration, 0)

        if duration < min_duration:
            end_table = end_table.addSecs((min_duration.minute() - duration.minute()) * 60)
            self.stopTimeTableRounds.setTime(end_table)
            
    @Slot()
    def on_update(self):
        # Update GUI components that depend on ScheduleData
        self.scheduleData.num_teams = self.numTeamsSpinbox.value()
        self.scheduleData.num_rooms = self.numRoomsSpinbox.value()
        self.scheduleData.num_tables = self.numTablesSpinbox.value()
        self.scheduleData.round_types_per_team['practice'] = self.roundTypeSpinboxes['practice'].value()
        self.scheduleData.round_types_per_team['table'] = self.roundTypeSpinboxes['table'].value()
        self.scheduleData.num_tables_and_sides = self.scheduleData.num_tables * 2
        self.numTablesAndSidesLabel.setText(str(self.scheduleData.num_tables_and_sides))
        for name in ["judging", "practice", "table"]:
            self.roundTypeLabels[name].setText(f"{self.scheduleData.num_teams * self.scheduleData.round_types_per_team[name]} Rounds")
        
        # Update TimeData with current GUI inputs
        jStop = self.startTimeJudgingRounds.time().addSecs(self.timeData.round_durations["judging"] * 60 * self.timeData.min_slots_required["judging"])
        self.judgingStopTime.setText(jStop.toString("HH:mm"))
        
        self.timeData.start_time_judging_rounds = self.startTimeJudgingRounds.time().toString("hh:mm")
        self.timeData.start_time_practice_rounds = self.startTimePracticeRounds.time().toString("hh:mm")
        self.timeData.start_time_break = self.stopTimePractice.time().toString("hh:mm")
        self.timeData.start_time_table_rounds = self.startTimeTableRounds.time().toString("hh:mm")
        self.timeData.stop_time_table_rounds = self.stopTimeTableRounds.time().toString("hh:mm")
        self.timeData.update_time_data()

        # Update soft constraint weights
        for constraint in self.softConstraintWeights:
            self.qLearning.constraint_weights[constraint] = self.softConstraintWeights[constraint].value() / 100.0
            self.constraintLabel[constraint].setText(f'{constraint}: {self.qLearning.constraint_weights[constraint] * 100:.2f}%')
        
        self.qLearning.gui_refresh_rate = self.guiRefreshRate.value()
        
        # Update Q-Learning parameters
        self.qLearning.alpha = self.alphaInput.value()
        self.qLearning.gamma = self.gammaInput.value()
        self.qLearning.epsilon_start = self.epsilonStartInput.value()
        self.qLearning.epsilon_end = self.epsilonEndInput.value()
        self.qLearning.epsilon_decay = self.epsilonDecayInput.value()
        self.qLearning.episodes = self.episodesInput.value()
        self.qLearning.initialize_schedule_and_states()
        
        halfway_decay, total_decay, self.decays = self.calculate_epsilon_decay_episodes()
        self.epsilonHalfwayLabel.setText(f'{halfway_decay} episodes')
        self.epsilonTotalLabel.setText(f'{total_decay} episodes')

        self.progressBar.setMaximum(self.qLearning.episodes)
        self.qLearning.required_schedule_slots = sum(self.scheduleData.round_types_per_team.values()) * self.scheduleData.num_teams
        self.qLearning.possible_schedule_slots = self.scheduleData.num_rooms * self.timeData.min_slots_required["judging"] + self.scheduleData.num_tables_and_sides * (self.timeData.min_slots_required["practice"] + self.timeData.min_slots_required["table"]) 
        self.qLearning.q_table_size_limit = len(self.qLearning.states) * self.scheduleData.num_teams

        # Update current stats
        self.q_learningLabel.setText(f"Epsilon: {self.qLearning.epsilon:.2f} \nAlpha: {self.qLearning.alpha:.2f} \nGamma: {self.qLearning.gamma:.2f} \nEpisodes: {self.qLearning.episodes}")
        self.CurrentScheduleLengthLabel.setText(f"Required Schedule Slots: {self.qLearning.required_schedule_slots} ({self.qLearning.possible_schedule_slots} Possible)")
        self.q_tableSizeLabel.setText(f"Q-Table Size: {len(self.qLearning.q_table)}/{self.qLearning.q_table_size_limit}")
        
        self.qLearning.practice_teams_available = list(self.scheduleData.teams.keys()) * self.scheduleData.round_types_per_team["practice"]
        self.qLearning.table_teams_available = list(self.scheduleData.teams.keys()) * self.scheduleData.round_types_per_team["table"]
        
        # Update TimeData with current GUI inputs
        self.practiceRoundDuration.setText(f'{self.timeData.round_durations["practice"]} minutes')
        self.tableRoundDuration.setText(f'{self.timeData.round_durations["table"]} minutes')
        self.practiceTimeAvailable.setText(f'{self.timeData.practice_duration_available} minutes')
        self.tableTimeAvailable.setText(f'{self.timeData.table_duration_available} minutes')

        self.statusLabel.setText(f"Waiting for User to Complete Initialization")
        self.initialize_schedule_display()
        
        self.validate_practice_times()
        self.validate_table_times()

    @Slot(int)
    def update_gui_total(self, episode):
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
                self.q_learningLabel.setText(f"Epsilon: {self.qLearning.epsilon:.2f} (Final)\nAlpha: {self.qLearning.alpha:.2f}\nGamma: {self.qLearning.gamma:.2f}\nEpisodes: {self.qLearning.episodes}")
                self.q_tableSizeLabel.setText(f"Q-Table Size: {len(self.qLearning.q_table)}/{self.qLearning.q_table_size_limit} (Final)")

                self.scheduleScoresPlot.plot_schedule_scores('optimal', episode, self.qLearning.scores, self.qLearning.completion_percentage)
                
                # Update the schedule display
                self.initialize_schedule_display()
                self.progressBar.setValue(self.qLearning.episodes)
                self.trainButton.setDisabled(False)
                self.trainButton.setText("Close Window")
                self.worker.signals.gui_updated_signal.emit()
                
            elif episode > 0 and episode % self.guiRefreshRate.value() == 0:
                # Basic Stats
                self.avgRewardLabel.setText(f"Average Reward: {self.qLearning.avg_rewards[-1]:.2f}")
                self.statusLabel.setText(f"Episode {episode} : Scheduling in progress...")

                self.q_learningLabel.setText(f"Epsilon: {self.qLearning.epsilon:.2f}\nAlpha: {self.qLearning.alpha:.2f}\nGamma: {self.qLearning.gamma:.2f}\nEpisodes: {self.qLearning.episodes}")
                self.q_tableSizeLabel.setText(f"Q-Table Size: {len(self.qLearning.q_table)}/{self.qLearning.q_table_size_limit}")
                
                # Update the Q-value heatmap                  
                aggregated_data = self.qLearning.transform_for_heatmap()
                heatmap_data, round_types, team_ids = self.qLearning.aggregated_data_to_2d_array(aggregated_data)
                self.qValueHeatmapPlot.plot_heatmap(heatmap_data, xticklabels=team_ids, yticklabels=round_types)

                # Update the Q-value convergence plot
                self.qValueConvergencePlot.plot_convergence(list(range(1,episode+1)), self.qLearning.q_value_changes, self.qLearning.avg_reward_changes, self.qLearning.episodes)

                # Update the exploration vs. exploitation plot
                self.exploreExploitPlot.plot_exploration_exploitation_balance(self.qLearning.exploration_counts, self.qLearning.exploitation_counts, self.qLearning.episodes, self.qLearning.epsilon_start, self.qLearning.epsilon_end, self.decays)

                # Update score plot
                self.scheduleScoresPlot.plot_schedule_scores('training', episode, self.qLearning.scores, self.qLearning.completion_percentage)    
                
                # Update the schedule display
                self.initialize_schedule_display()
                self.progressBar.setValue(episode)
                self.trainButton.setText(f'Training in Progress...{episode}/{self.qLearning.episodes}')
                self.worker.signals.gui_updated_signal.emit()
        
        self.worker.signals.gui_updated_signal.emit()

        if not self.thread.isRunning():
            print(f"Thread {self.thread} Stopped")
            return
        

###############################################################
# Step 3: Run the application #################################
###############################################################
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.setWindowTitle("FIRST LEGO League Challenge Q-Learning Tournament Scheduler")
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
