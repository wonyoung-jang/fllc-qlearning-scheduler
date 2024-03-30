"""This module contains the TrainingWorker class, which is a QThread that handles the training process."""
import csv
import ast
import pandas as pd
from collections import defaultdict
from PySide6.QtCore import QObject, QThread, Signal, Slot, QWaitCondition, QMutex, Qt
from gui_signals import GUISignals
from config import Config

EVAL_RESULTS_CSV_PATH = Config.EVAL_RESULTS_CSV_PATH
EVAL_TYPES = Config.EVAL_TYPES
EVAL_TYPE = Config.EVAL_TYPE
SCORES = Config.SCORES
COMPLETION_PERCENTAGES = Config.COMPLETION_PERCENTAGES
AVERAGE_SCORE = Config.AVERAGE_SCORE
AVERAGE_COMPLETION_PERCENTAGE = Config.AVERAGE_COMPLETION_PERCENTAGE

class TrainingWorker(QObject):
    """
    Class to handle the training process as a QThread.
    
    """
    finished = Signal()

    def __init__(self, q_learning): 
        """
        Initialize TrainingWorker object.
        
        """
        super().__init__()

        self.q_learning = q_learning
        self.signals = GUISignals()
        
        self.wait_condition = QWaitCondition()  # Add a wait condition
        self.mutex = QMutex()  # Add a mutex
        
        self.signals.gui_updated_signal.connect(self.gui_updated, Qt.DirectConnection)

    def parse_scores(self, evaluation_data):
        """
        Parse the evaluation data into a list.
        
        """
        if isinstance(evaluation_data, list):  # Check if it's already a list
            return evaluation_data
        elif isinstance(evaluation_data, float):  # Handle single float cases
            return [evaluation_data]
        else:
            raise ValueError(f"Unexpected evaluation_data type in scores: {type(evaluation_data)}")

    def write_evaluation_results_to_csv(self, evaluation_data):
        """
        Write the evaluation results to a CSV file.
        
        """
        max_length = max(len(x) for x in evaluation_data.values() if isinstance(x, list))
        with open(EVAL_RESULTS_CSV_PATH, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=evaluation_data.keys())
            writer.writeheader()
            for i in range(max_length):
                evaluation_row = {
                    EVAL_TYPE: evaluation_data[EVAL_TYPE][i] if i < len(evaluation_data[EVAL_TYPE]) else "",
                    SCORES: evaluation_data[SCORES][i] if i < len(evaluation_data[SCORES]) else "",
                    COMPLETION_PERCENTAGES: evaluation_data[COMPLETION_PERCENTAGES][i] if i < len(evaluation_data[COMPLETION_PERCENTAGES]) else "",
                    AVERAGE_SCORE: evaluation_data[AVERAGE_SCORE][i] if i < len(evaluation_data[AVERAGE_SCORE]) else "",
                    AVERAGE_COMPLETION_PERCENTAGE: evaluation_data[AVERAGE_COMPLETION_PERCENTAGE][i] if i < len(evaluation_data[AVERAGE_COMPLETION_PERCENTAGE]) else "",
                }
                
                writer.writerow(evaluation_row)

    @Slot()
    def run(self):
        """Run the training process."""
        # Benchmarks
        for episode in range(1, 11):
            self.q_learning.train_benchmark_episodes()
            self.signals.update_gui_signal.emit(-1)
            self.mutex.lock()
            self.wait_condition.wait(self.mutex)  # Wait on the condition
            self.mutex.unlock()

        # Training
        for episode in range(1, self.q_learning.training_episodes + 1):
            self.q_learning.train_one_episode(episode)
            self.signals.update_gui_signal.emit(episode)
            self.mutex.lock()
            self.wait_condition.wait(self.mutex)  # Wait on the condition
            self.mutex.unlock()

        # Optimal Schedule
        self.q_learning.generate_optimal_schedule()
        self.signals.update_gui_signal.emit(-2)
        self.mutex.lock()
        self.wait_condition.wait(self.mutex)  # Wait on the condition
        self.mutex.unlock()

        average_scores = defaultdict(float)
        average_completions = defaultdict(float)

        for eval_type, scores in self.q_learning.scores.items():
            average_score = sum(scores) / len(scores)
            average_scores[eval_type] = average_score

        for eval_type, completion_percentage in self.q_learning.completion_percentage.items():
            average_completion_percentage = sum(completion_percentage) / len(completion_percentage)
            average_completions[eval_type] = average_completion_percentage

        evaluation_data = {
            EVAL_TYPE: [],
            SCORES: [],
            COMPLETION_PERCENTAGES: [],
            AVERAGE_SCORE: [],
            AVERAGE_COMPLETION_PERCENTAGE: [],
        }

        for eval_type in EVAL_TYPES:
            evaluation_data[EVAL_TYPE].append(eval_type)
            evaluation_data[SCORES].append(self.q_learning.scores[eval_type])
            evaluation_data[COMPLETION_PERCENTAGES].append(self.q_learning.completion_percentage[eval_type])
            evaluation_data[AVERAGE_SCORE].append(average_scores[eval_type])
            evaluation_data[AVERAGE_COMPLETION_PERCENTAGE].append(average_completions[eval_type])

        # Determine longest list
        max_length = max(len(x) for x in evaluation_data.values() if isinstance(x, list))

        self.write_evaluation_results_to_csv(evaluation_data)
        
        self.finished.emit()

    @Slot()
    def gui_updated(self):
        """Slot to handle the GUI updated signal."""
        self.mutex.lock()
        self.wait_condition.wakeOne()  # Wake up the waiting thread
        self.mutex.unlock()
