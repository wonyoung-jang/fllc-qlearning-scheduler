from PySide6.QtCore import QObject, Signal, Slot, QWaitCondition, QMutex, Qt
from gui_signals import GUISignals


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

    @Slot()
    def run(self):
        """
        Run the training process.
        
        """
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
        
        self.finished.emit()

    @Slot()
    def gui_updated(self):
        """
        Slot to handle the GUI updated signal.
        
        """
        self.mutex.lock()
        self.wait_condition.wakeOne()  # Wake up the waiting thread
        self.mutex.unlock()
