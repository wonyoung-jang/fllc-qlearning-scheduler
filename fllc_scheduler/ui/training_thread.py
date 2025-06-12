"""Module for managing training threads in the FLLC Scheduler."""

import csv
from collections import defaultdict
from dataclasses import dataclass

from PySide6.QtCore import QMutex, QObject, Qt, QThread, QWaitCondition, Signal, Slot

from ..config import EXPORT_RESULTS, Training
from ..q_learning.q_learning import QLearning
from ..utils.stat_utils import average


class GUISignals(QObject):
    """Signals for GUI updates during training."""

    update_gui_signal = Signal(str, int)
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
            for _ in range(10):
                if not self._should_continue():
                    return

                self.q_learning.train_benchmark_episodes()
                self.signals.update_gui_signal.emit(Training.BENCHMARK, -1)

                if not self._wait_for_gui_update() and not self._should_continue():
                    return

            for episode in range(1, self.q_learning.config.episodes + 1):
                if not self._should_continue():
                    return

                self.q_learning.train_one_episode(episode)
                self.signals.update_gui_signal.emit(Training.TRAINING, episode)

                if not self._wait_for_gui_update() and not self._should_continue():
                    return

            if not self._should_continue():
                return

            self.q_learning.generate_optimal_schedule()
            self.signals.update_gui_signal.emit(Training.OPTIMAL, -1)

            if not self._wait_for_gui_update() and not self._should_continue():
                return

            self._export_results()
        except Exception as e:
            print(f"Training error: {e}")
            raise e
        finally:
            self.signals.finished.emit()

    def _export_results(self) -> None:
        """Export training results to a CSV file."""
        try:
            average_scores = defaultdict(float)
            for eval_type, scores in self.q_learning.metrics.scores.items():
                average_scores[eval_type] = average(scores) if scores else 0.0

            average_completions = defaultdict(float)
            for eval_type, completion_percentage in self.q_learning.metrics.completion_percentage.items():
                average_completions[eval_type] = average(completion_percentage) if completion_percentage else 0.0

            d = defaultdict(list)
            for eval_type in ("Benchmarks", "Training", "Optimal"):
                d["Eval Type"].append(eval_type)
                d["Scores"].append(self.q_learning.metrics.scores[eval_type])
                d["Completion Percentages"].append(self.q_learning.metrics.completion_percentage[eval_type])
                d["Average Score"].append(average_scores[eval_type])
                d["Average Completion Percentage"].append(average_completions[eval_type])

            max_length = max(len(x) for x in d.values() if isinstance(x, list))

            with EXPORT_RESULTS.open("w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=d.keys())
                writer.writeheader()
                for i in range(max_length):
                    row = {}
                    row["Eval Type"] = d["Eval Type"][i] if i < len(d["Eval Type"]) else ""
                    row["Scores"] = d["Scores"][i] if i < len(d["Scores"]) else ""
                    row["Completion Percentages"] = (
                        d["Completion Percentages"][i] if i < len(d["Completion Percentages"]) else ""
                    )
                    row["Average Score"] = d["Average Score"][i] if i < len(d["Average Score"]) else ""
                    row["Average Completion Percentage"] = (
                        d["Average Completion Percentage"][i] if i < len(d["Average Completion Percentage"]) else ""
                    )
                    writer.writerow(row)
        except Exception as e:
            print(f"Error exporting results: {e}")
            raise e

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
        self.wait_condition.wakeAll()  # Wake up if waiting
