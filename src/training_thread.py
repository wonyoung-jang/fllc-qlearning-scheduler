from PySide6.QtCore import QObject, QThread, Signal, Slot, QWaitCondition, QMutex, Qt
import pandas as pd
from collections import defaultdict
import csv
import ast

class GUISignals(QObject):
    update_gui_signal = Signal(int)  # episode, total_episodes, avg_reward, q_value_changes, q_table, exploration_count, exploitation_count
    gui_updated_signal = Signal()
    
class TrainingWorker(QObject):
    finished = Signal()

    def __init__(self, q_learning_instance):
        super().__init__()
        self.q_learning = q_learning_instance
        self.signals = GUISignals()
        self.wait_condition = QWaitCondition()  # Add a wait condition
        self.mutex = QMutex()                  # Add a mutex
        self.signals.gui_updated_signal.connect(self.gui_updated, Qt.DirectConnection)         
    
    def parse_scores(self, data): 
        if isinstance(data, list):  # Check if it's already a list
            return data
        elif isinstance(data, float):  # Handle single float cases 
            return [data] 
        else: 
            raise ValueError(f"Unexpected data type in scores: {type(data)}")
        
    @Slot()        
    def run(self):
        # Benchmarks
        for episode in range(1, 11):
            self.q_learning.train_benchmark_episodes()
            self.signals.update_gui_signal.emit(-1)
            self.mutex.lock()
            self.wait_condition.wait(self.mutex)  # Wait on the condition
            self.mutex.unlock()            

        # Training
        for episode in range(1, self.q_learning.episodes + 1):
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

        data = {
            'Eval Type': [],
            'Scores': [],
            'Completion Percentages': [],
            'Average Score': [],
            'Average Completion Percentage': [], 
        }

        for eval_type in ['Benchmarks', 'Training', 'Optimal']:  
            data['Eval Type'].append(eval_type) 
            data['Scores'].append(self.q_learning.scores[eval_type])
            data['Completion Percentages'].append(self.q_learning.completion_percentage[eval_type])
            data['Average Score'].append(average_scores[eval_type])
            data['Average Completion Percentage'].append(average_completions[eval_type]) 

        max_length = max(len(x) for x in data.values() if isinstance(x, list))  # Determine longest list
        
        with open('./exports/schedule_evaluation/evaluation_results.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())
            writer.writeheader()
            for i in range(max_length): 
                row = {
                    'Eval Type': data['Eval Type'][i] if i < len(data['Eval Type']) else '',
                    'Scores': data['Scores'][i] if i < len(data['Scores']) else '',
                    'Completion Percentages': data['Completion Percentages'][i] if i < len(data['Completion Percentages']) else '',
                    'Average Score': data['Average Score'][i] if i < len(data['Average Score']) else '',    
                    'Average Completion Percentage': data['Average Completion Percentage'][i] if i < len(data['Average Completion Percentage']) else ''
                }
                writer.writerow(row)
        self.finished.emit()
          
    @Slot()
    def gui_updated(self):
        self.mutex.lock()
        self.wait_condition.wakeOne()  # Wake up the waiting thread
        self.mutex.unlock()