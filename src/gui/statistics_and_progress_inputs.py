from PySide6.QtWidgets import QProgressBar, QLabel, QHBoxLayout, QSpinBox, QGroupBox, QVBoxLayout
from config import Config

class StatisticsAndProgressInputs:
    def __init__(self, schedule_data, time_data, q_learning): 
        """Creates the statistics and progress for the Q-learning scheduler."""
        self.schedule_data = schedule_data
        self.time_data = time_data
        self.q_learning = q_learning
        
        self.progress_bar = QProgressBar()
        self.avg_reward_label = QLabel("Average Reward: ")
        self.current_schedule_length_label = QLabel(f"Required Schedule Slots: {self.q_learning.required_schedule_slots} ({self.q_learning.possible_schedule_slots} Possible)")
        
        self.status_label = QLabel("Waiting for User to Complete Initialization")
        self.q_learning_label = QLabel(f"Epsilon: {self.q_learning.epsilon:.2f}\nAlpha: {self.q_learning.learning_rate:.2f}\nGamma: {self.q_learning.discount_factor:.2f}\nEpisodes: {self.q_learning.training_episodes}")
        self.q_table_size_label = QLabel(f"Q-Table Size: {len(self.q_learning.q_table)}/{self.q_learning.q_table_size_limit}")
        
        self.gui_refresh_layout = QHBoxLayout()
        
        self.gui_refresh_label = QLabel("Refresh GUI every: ")
        self.gui_refresh_rate = QSpinBox()
        
        self.gui_refresh_layout.addWidget(self.gui_refresh_label)
        self.gui_refresh_layout.addWidget(self.gui_refresh_rate)
        self.gui_refresh_layout.addWidget(QLabel("Episodes"))
        
        self.initialize_statistics_and_progress()
        self.setup_statistics()
        
    def initialize_statistics_and_progress(self):
        """Initializes the statistics and progress for the Q-learning scheduler."""
        self.progress_bar.setMaximum(self.q_learning.training_episodes)
        self.current_schedule_length_label.setText(f"Required Schedule Slots: {self.q_learning.required_schedule_slots} ({self.q_learning.possible_schedule_slots} Possible)")
        self.gui_refresh_rate.setValue(self.q_learning.gui_refresh_interval)
    
    def setup_statistics(self): 
        """Sets up the statistics and progress for the Q-learning scheduler."""
        self.statistics_groupbox = QGroupBox("Training Statistics")
        self.statistics_layout = QVBoxLayout(self.statistics_groupbox)
        self.statistics_layout.addWidget(self.status_label)
        self.statistics_layout.addWidget(self.avg_reward_label)
        self.statistics_layout.addWidget(self.current_schedule_length_label)
        self.statistics_layout.addWidget(self.q_table_size_label)
        self.statistics_layout.addWidget(self.q_learning_label)
        
        self.statistics_layout.addWidget(self.progress_bar)
        
        self.statistics_layout.addLayout(self.gui_refresh_layout)
        