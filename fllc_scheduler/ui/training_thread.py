"""Module for managing training threads in the FLLC Scheduler."""

from dataclasses import dataclass

from PySide6.QtCore import QMutex, QObject, Qt, QThread, QWaitCondition, Signal, Slot

from ..q_learning.q_learning import QLearning
from ..utils.config import NUM_BENCHMARKS, Training


class GUISignals(QObject):
    """Signals for GUI updates during training."""

    update_gui_signal = Signal(Training, int)
    gui_updated_signal = Signal()
    finished = Signal()


@dataclass(slots=True)
class TrainingWorker(QThread):
    """Worker thread for training the Q-Learning model in the FLLC Scheduler."""

    q_learning: QLearning
    signals: GUISignals = None
    mutex: QMutex = None
    wait_condition: QWaitCondition = None
    _stop_requested: bool = False

    def __post_init__(self) -> None:
        """Initialize the training worker with Q-Learning instance and signals."""
        super(TrainingWorker, self).__init__()
        self.wait_condition = QWaitCondition()
        self.mutex = QMutex()
        self.signals = GUISignals()
        self.signals.gui_updated_signal.connect(self.gui_updated, Qt.ConnectionType.DirectConnection)
        self._stop_requested = False

    def _should_continue(self) -> bool:
        """Check if training should continue."""
        self.mutex.lock()
        should_continue = not self._stop_requested
        self.mutex.unlock()
        return should_continue

    def _wait_for_gui_update(self, timeout_ms: int = 5000) -> bool:
        """Wait for GUI update with timeout. Returns True if GUI updated, False if timeout."""
        self.mutex.lock()
        result = self.wait_condition.wait(self.mutex, timeout_ms)
        self.mutex.unlock()
        return result

    @Slot()
    def run(self) -> None:
        """Run the training process for the Q-Learning model."""
        try:
            for _ in range(NUM_BENCHMARKS):
                if not self._should_continue():
                    return

                self.q_learning.benchmark()
                self.signals.update_gui_signal.emit(Training.BENCHMARK, -1)

                if not self._wait_for_gui_update() and not self._should_continue():
                    return

            for episode in range(self.q_learning.config.episodes):
                if not self._should_continue():
                    return

                self.q_learning.train(episode)
                self.signals.update_gui_signal.emit(Training.TRAINING, episode + 1)

                if not self._wait_for_gui_update() and not self._should_continue():
                    return

            if not self._should_continue():
                return

            self.q_learning.optimize()
            self.signals.update_gui_signal.emit(Training.OPTIMAL, -1)

            if not self._wait_for_gui_update() and not self._should_continue():
                return
        except Exception as e:
            print(f"Training error: {e}")
            raise e
        finally:
            self.signals.finished.emit()

    @Slot()
    def gui_updated(self) -> None:
        """Handle GUI updates after training."""
        self.mutex.lock()
        self.wait_condition.wakeOne()
        self.mutex.unlock()

    @Slot()
    def request_stop(self) -> None:
        """Request to stop the training thread."""
        self.mutex.lock()
        self._stop_requested = True
        self.mutex.unlock()
        self.wait_condition.wakeAll()


@dataclass(slots=True)
class FLLCSchedulerProcessor:
    """Data class to hold the thread and worker for the FLLC Q-Learning Tournament Scheduler."""

    thread: QThread
    worker: TrainingWorker

    def emit(self) -> None:
        """Emit the GUI updated signal from the worker."""
        self.worker.signals.gui_updated_signal.emit()
