from PySide6.QtWidgets import QDoubleSpinBox, QSpinBox, QLabel, QGroupBox, QGridLayout
from q_learning import QLearning
from schedule_data._schedule_data import ScheduleData
from time_data._time_data import TimeData
from config import Config

class QLearningInputs:
    def __init__(self):
        """Creates the Q-learning inputs for the application."""
        self.schedule_data = ScheduleData()
        self.time_data = TimeData(self.schedule_data)
        self.q_learning = QLearning(self.schedule_data, self.time_data)
        
        self.alpha_spinbox = QDoubleSpinBox()
        self.gamma_spinbox = QDoubleSpinBox()
        self.epsilon_start_spinbox = QDoubleSpinBox()
        self.epsilon_end_spinbox = QDoubleSpinBox()
        self.epsilon_decay_spinbox = QDoubleSpinBox(decimals=3)
        self.training_episodes_spinbox = QSpinBox()
        
        self.initialize_q_learning_inputs()
        self.setup_q_learning_inputs()
        
    
    def initialize_q_learning_inputs(self):
        """Initializes the Q-learning inputs based on the values stored in the `q_learning` object."""
        self.alpha_spinbox.setValue(self.q_learning.learning_rate)
        self.alpha_spinbox.setRange(0.01, 1.00)
        self.alpha_spinbox.setSingleStep(0.01)
        
        self.gamma_spinbox.setValue(self.q_learning.discount_factor)
        self.gamma_spinbox.setRange(0.01, 1.00)
        self.gamma_spinbox.setSingleStep(0.01)
        
        self.epsilon_start_spinbox.setValue(self.q_learning.epsilon_start)
        self.epsilon_start_spinbox.setRange(0.01, 1.00)
        self.epsilon_start_spinbox.setSingleStep(0.01)
        
        self.epsilon_end_spinbox.setValue(self.q_learning.epsilon_end)
        self.epsilon_end_spinbox.setRange(0.01, 1.00) 
        self.epsilon_end_spinbox.setSingleStep(0.01)     
          
        self.epsilon_decay_spinbox.setValue(self.q_learning.epsilon_decay)
        self.epsilon_decay_spinbox.setRange(0.001, 1.000)
        self.epsilon_decay_spinbox.setSingleStep(0.001)
        
        self.training_episodes_spinbox.setValue(self.q_learning.training_episodes)
        self.training_episodes_spinbox.setRange(1, 100000)
              
    def setup_q_learning_inputs(self):
        """Sets up the Q-learning inputs in the GUI."""
        halfway_decay, total_decay, self.decays = self.calculate_epsilon_decay_episodes()
        self.epsilon_halfway_label  = QLabel(f'{halfway_decay} Episodes')
        self.epsilon_total_label    = QLabel(f'{total_decay} Episodes')
        
        self.q_learning_inputs_groupbox = QGroupBox("Q-Learning Inputs")
        self.q_learning_layout = QGridLayout(self.q_learning_inputs_groupbox)
        self.q_learning_layout.addWidget(QLabel("Learning Rate (α)"), 0, 0)
        self.q_learning_layout.addWidget(self.alpha_spinbox, 0, 1)
        self.q_learning_layout.addWidget(QLabel("Discount Factor (γ)"), 1, 0)
        self.q_learning_layout.addWidget(self.gamma_spinbox, 1, 1)
        self.q_learning_layout.addWidget(QLabel("Epsilon Start (Ɛ)"), 2, 0)
        self.q_learning_layout.addWidget(self.epsilon_start_spinbox, 2, 1)
        self.q_learning_layout.addWidget(QLabel("Epsilon End (Ɛ)"), 3, 0)
        self.q_learning_layout.addWidget(self.epsilon_end_spinbox, 3, 1)
        self.q_learning_layout.addWidget(QLabel("Epsilon Decay (Ɛ)"), 4, 0)
        self.q_learning_layout.addWidget(self.epsilon_decay_spinbox, 4, 1)
        self.q_learning_layout.addWidget(QLabel("Max Training Episodes"), 5, 0)
        self.q_learning_layout.addWidget(self.training_episodes_spinbox, 5, 1)
        self.q_learning_layout.addWidget(QLabel(f'Epsilon 50% at: '), 6, 0)
        self.q_learning_layout.addWidget(self.epsilon_halfway_label, 6, 1)
        self.q_learning_layout.addWidget(QLabel(f'Epsilon End at:'), 7, 0)
        self.q_learning_layout.addWidget(self.epsilon_total_label, 7, 1) 
    
    
    def calculate_epsilon_decay_episodes(self):
        """Calculates the epsilon decay episodes for the Q-learning scheduler."""
        # Get the initial epsilon, epsilon end, and epsilon decay values
        epsilon_start = self.epsilon_start_spinbox.value()
        epsilon_end = self.epsilon_end_spinbox.value()
        epsilon_decay = self.epsilon_decay_spinbox.value()

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
