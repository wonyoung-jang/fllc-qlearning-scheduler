from PySide6.QtWidgets import QGroupBox, QGridLayout, QSlider, QLabel
from PySide6.QtCore import Qt
from q_learning import QLearning
from schedule_data._schedule_data import ScheduleData
from time_data._time_data import TimeData
from config import Config


class SoftConstraintWeightsInputs:
    def __init__(self):
        self.schedule_data = ScheduleData()
        self.time_data = TimeData(self.schedule_data)
        self.q_learning = QLearning(self.schedule_data, self.time_data)
        
        """Creates the soft constraint weights for the Q-learning scheduler."""
        # Create the group box and layout for the soft constraint weights
        self.soft_constraint_weights_groupbox = QGroupBox("Soft Constraint Weights")
        self.soft_constraint_weights_layout = QGridLayout(self.soft_constraint_weights_groupbox)

        # Initialize dictionaries to store the sliders and labels for each constraint
        self.soft_constraint_weights = {}
        self.constraint_labels = {}

        # Set the scale factor for the slider positions
        scale_factor = 100.0  # Adjust this value based on the precision you need

        # Initialize the row counter
        row = 0

        # Iterate over each constraint and create a slider and label for it
        for constraint in ['Table Consistency', 'Opponent Variety', 'Back to Back Penalty', 'Break Time']:
            # Create the slider for the constraint
            self.soft_constraint_weights[constraint] = QSlider(Qt.Horizontal)
            self.soft_constraint_weights[constraint].setRange(0, 100)  # Adjust this based on the range you need
            self.soft_constraint_weights[constraint].setSingleStep(1)
            self.soft_constraint_weights[constraint].setTickInterval(10)
            self.soft_constraint_weights[constraint].setSliderPosition(self.q_learning.soft_constraints_weight[constraint] * scale_factor)

            # Connect the valueChanged signal of the slider to the on_update method
            #self.soft_constraint_weights[constraint].valueChanged.connect(self.on_update)

            # Create the label for the constraint
            self.constraint_labels[constraint] = QLabel(f'{constraint}: {self.q_learning.soft_constraints_weight[constraint] * scale_factor:.2f}%')

            # Add the label and slider to the layout
            self.soft_constraint_weights_layout.addWidget(self.constraint_labels[constraint], row, 0, Qt.AlignLeft)
            self.soft_constraint_weights_layout.addWidget(self.soft_constraint_weights[constraint], row, 1, Qt.AlignRight)

            # Increment the row counter
            row += 1
    