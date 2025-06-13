"""Module for the main GUI of the FLLC Scheduler."""

from dataclasses import dataclass, field

from PySide6.QtCore import Qt, QThread, QTime, Slot
from PySide6.QtWidgets import QHBoxLayout, QSplitter, QWidget

from ..utils.config import EXPORT_DIR, EXPORT_OPTIMAL_GRID, RoundType, Training
from ..data_model.data import FLLCSchedulerData
from ..utils.export_utils import clear_exports_dir
from .input_panel import FLLCSchedulerInputPanel
from .mpl_widgets import MplWidgets
from .schedule_display import ScheduleDisplay
from .training_thread import TrainingWorker


@dataclass(slots=True)
class FLLCSchedulerProcessor:
    """Data class to hold the thread and worker for the FLLC Q-Learning Tournament Scheduler."""

    thread: QThread
    worker: TrainingWorker

    def emit(self) -> None:
        """Emit the GUI updated signal from the worker."""
        self.worker.signals.gui_updated_signal.emit()


@dataclass(slots=True)
class FLLCSchedulerGUI(QWidget):
    """FLLCSchedulerGUI main window for the FLLC Q-Learning Tournament Scheduler GUI."""

    data: FLLCSchedulerData = field(default_factory=FLLCSchedulerData)
    inputs: FLLCSchedulerInputPanel = None
    sched_display: ScheduleDisplay = None
    mpl: MplWidgets = None
    process: FLLCSchedulerProcessor = None

    def __post_init__(self) -> None:
        """Initialize the main window and its components."""
        super(FLLCSchedulerGUI, self).__init__()
        self.setWindowTitle("FIRST LEGO League Challenge Q-Learning Tournament Scheduler")
        self.resize(1500, 600)
        self.inputs = FLLCSchedulerInputPanel(self.data)
        self.sched_display = ScheduleDisplay(self.data)
        self.mpl = MplWidgets(self)
        self.mpl.set_q_learning(self.data.q_learning)
        self.connect_signals_and_slots()
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the main GUI layout and components."""
        col_splitter = QSplitter(Qt.Orientation.Horizontal)
        col_splitter.addWidget(self.inputs)
        col_splitter.addWidget(self.sched_display)
        col_splitter.addWidget(self.mpl)
        layout = QHBoxLayout()
        layout.addWidget(col_splitter)
        self.setLayout(layout)

    def connect_signals_and_slots(self) -> None:
        """Connect signals and slots for the GUI components."""
        self.connect_time_inputs_signals()
        self.connect_schedule_inputs_signals()
        self.connect_q_inputs_signals()
        self.connect_soft_constraint_signals()
        self.connect_gui_inputs_signals()

    def connect_time_inputs_signals(self) -> None:
        """Connect signals for time input changes."""
        t = self.inputs.comp.time_inputs.timeedit
        t.judging_start.timeChanged.connect(self.on_update)

        t.practice_start.timeChanged.connect(self.on_update)
        t.practice_start.timeChanged.connect(self.validate_practice_times)
        t.practice_stop.timeChanged.connect(self.on_update)
        t.practice_stop.timeChanged.connect(self.validate_practice_times)
        t.practice_minimum.timeChanged.connect(self.on_update)
        t.practice_minimum.timeChanged.connect(self.validate_practice_times)

        t.table_minimum.timeChanged.connect(self.on_update)
        t.table_minimum.timeChanged.connect(self.validate_table_times)
        t.table_start.timeChanged.connect(self.on_update)
        t.table_start.timeChanged.connect(self.validate_table_times)
        t.table_stop.timeChanged.connect(self.on_update)
        t.table_stop.timeChanged.connect(self.validate_table_times)

    def connect_schedule_inputs_signals(self) -> None:
        """Connect signals for schedule input changes."""
        s = self.inputs.comp.sched_inputs
        s.spinbox_num_teams.valueChanged.connect(self.on_update)
        s.spinbox_num_rooms.valueChanged.connect(self.on_update)
        s.spinbox_num_tables.valueChanged.connect(self.on_update)
        r = self.inputs.comp.round_inputs.spinboxes
        r[RoundType.PRACTICE].valueChanged.connect(self.on_update)
        r[RoundType.TABLE].valueChanged.connect(self.on_update)

    def connect_q_inputs_signals(self) -> None:
        """Connect signals for Q-Learning input changes."""
        q = self.inputs.comp.q_inputs
        q.dblspin.alpha.valueChanged.connect(self.on_update)
        q.dblspin.gamma.valueChanged.connect(self.on_update)
        q.dblspin.epsilon_start.valueChanged.connect(self.on_update)
        q.dblspin.epsilon_end.valueChanged.connect(self.on_update)
        q.dblspin.epsilon_decay.valueChanged.connect(self.on_update)
        q.spinbox_episodes.valueChanged.connect(self.on_update_constraints)

    def connect_soft_constraint_signals(self) -> None:
        """Connect signals for soft constraint input changes."""
        s = self.inputs.comp.soft_constraint.slider
        s.table_consistency.valueChanged.connect(self.on_update_constraints)
        s.opponent_variety.valueChanged.connect(self.on_update_constraints)
        s.back_to_back_penalty.valueChanged.connect(self.on_update_constraints)
        s.break_time.valueChanged.connect(self.on_update_constraints)

    def connect_gui_inputs_signals(self) -> None:
        """Connect signals for GUI input changes."""
        g = self.inputs.comp.gui_inputs
        g.spinbox_gui_refresh_rate.valueChanged.connect(self.on_update)
        g.run.clicked.connect(self.start_training_thread)
        g.exit.clicked.connect(self.close)

    def _training_benchmark(self) -> None:
        """Run the benchmark training process."""
        _mpl = self.mpl
        _inputs = self.inputs.comp
        _gui_inputs = _inputs.gui_inputs
        _gui_labels = _gui_inputs.label
        _mpl.schedule_scores.plot(Training.BENCHMARK)
        _gui_inputs.progressbar.setValue(0)
        _gui_labels.status.setText("Generating Benchmarks...")
        self.process.emit()

    def _training_training(self, episode: int) -> None:
        """Run the training process."""
        _mpl = self.mpl
        _inputs = self.inputs.comp
        _gui_inputs = _inputs.gui_inputs
        _gui_labels = _gui_inputs.label
        _mpl.heatmap.plot()
        _mpl.schedule_scores.plot(Training.TRAINING)
        _mpl.convergence.plot(list(range(1, episode + 1)))
        _mpl.explore_exploit.plot(_inputs.q_inputs.decays)
        _gui_labels.avg_reward.setText(f"Average Reward: {self.data.q_learning.metrics.avg_rewards[-1]:.2f}")
        _gui_labels.qlearning.setText(
            f"Epsilon: {self.data.q_learning.param.epsilon:.2f}\n"
            f"Alpha: {self.data.q_learning.param.alpha:.2f}\n"
            f"Gamma: {self.data.q_learning.param.gamma:.2f}\n"
            f"Episodes: {self.data.q_learning.config.episodes}"
        )
        _gui_labels.qtable_size.setText(
            f"Q-Table Size: {len(self.data.q_learning.state.q_table)}/{self.data.q_learning.q_table_size_limit}"
        )
        prog_fraction = f"{episode}/{self.data.q_learning.config.episodes}"
        _gui_inputs.progressbar.setValue(episode)
        _gui_labels.status.setText(f"Episode {prog_fraction}: Scheduling in progress...")
        self.process.emit()

    def _training_optimal(self) -> None:
        """Run the optimal training process."""
        _mpl = self.mpl
        _inputs = self.inputs.comp
        _gui_inputs = _inputs.gui_inputs
        _gui_labels = _gui_inputs.label
        _mpl.schedule_scores.plot(Training.OPTIMAL)
        _gui_labels.avg_reward.setText("Average Reward: Optimized")
        _gui_labels.qlearning.setText(
            f"Epsilon: {self.data.q_learning.param.epsilon:.2f} (Final)\n"
            f"Alpha: {self.data.q_learning.param.alpha:.2f}\n"
            f"Gamma: {self.data.q_learning.param.gamma:.2f}\n"
            f"Episodes: {self.data.q_learning.config.episodes}"
        )
        _gui_labels.qtable_size.setText(
            f"Q-Table Size: {len(self.data.q_learning.state.q_table)}/{self.data.q_learning.q_table_size_limit} (Final)"
        )
        _gui_labels.status.setText(
            f"Optimal Scheduling: Scheduling complete!\nOptimal Schedule Generated at {str(EXPORT_OPTIMAL_GRID)}"
        )
        _gui_inputs.progressbar.setValue(self.data.q_learning.config.episodes)
        _gui_inputs.run.setEnabled(True)
        self.process.emit()

    @Slot()
    def start_training_thread(self) -> None:
        """Start the training thread for Q-Learning."""
        clear_exports_dir(EXPORT_DIR)
        self.on_update()
        self.process = FLLCSchedulerProcessor(
            thread=QThread(),
            worker=TrainingWorker(self.data.q_learning),
        )
        self.process.worker.moveToThread(self.process.thread)
        self.process.worker.signals.update_gui_signal.connect(self.update_gui_total, Qt.ConnectionType.QueuedConnection)
        self.process.thread.started.connect(self.process.worker.run, Qt.ConnectionType.DirectConnection)
        self.process.thread.start()
        self.inputs.comp.gui_inputs.run.setText("Stop Training")
        self.inputs.comp.gui_inputs.run.clicked.disconnect()
        self.inputs.comp.gui_inputs.run.clicked.connect(self.stop_training_thread)

    @Slot()
    def validate_practice_times(self) -> None:
        """Validate the practice round times to ensure they meet minimum duration requirements."""
        timeedit_practice_stop = self.inputs.comp.time_inputs.timeedit.practice_stop
        min_duration = self.inputs.comp.time_inputs.timeedit.practice_minimum.time()
        duration = QTime(0, self.data.time.round_durations[RoundType.PRACTICE], 0)

        end_practice = timeedit_practice_stop.time()
        if duration < min_duration:
            end_practice = end_practice.addSecs((min_duration.minute() - duration.minute()) * 60)
            timeedit_practice_stop.setTime(end_practice)

    @Slot()
    def validate_table_times(self) -> None:
        """Validate the table round times to ensure they meet minimum duration requirements."""
        timeedit_table_stop = self.inputs.comp.time_inputs.timeedit.table_stop
        min_duration = self.inputs.comp.time_inputs.timeedit.table_minimum.time()
        duration = QTime(0, self.data.time.round_durations[RoundType.TABLE], 0)

        end_table = timeedit_table_stop.time()
        if duration < min_duration:
            end_table = end_table.addSecs((min_duration.minute() - duration.minute()) * 60)
            timeedit_table_stop.setTime(end_table)

    @Slot()
    def on_update(self) -> None:
        """Update the GUI components based on user inputs."""
        settings_from_ui = self.inputs.comp.collect_settings_from_ui()
        self.data.config.update_from_settings(settings_from_ui)
        self.data.time.update_from_settings(settings_from_ui)
        self.data.q_learning.param.update_from_settings(settings_from_ui)
        self.sched_display.init_schedule_display()
        self.inputs.comp.update_dependent_displays()
        self.validate_practice_times()
        self.validate_table_times()

    @Slot()
    def on_update_constraints(self) -> None:
        """Update the soft constraints based on user inputs."""
        settings_from_ui = self.inputs.comp.collect_settings_from_ui()
        self.data.q_learning.config.update_from_settings(settings_from_ui)
        self.inputs.comp.soft_constraint.label.update_labels(self.data.q_learning)
        self.inputs.comp.gui_inputs.progressbar.setMaximum(self.data.q_learning.config.episodes)

    @Slot(str, int)
    def update_gui_total(self, training_type: Training, episode: int) -> None:
        """
        Update the GUI with the current training status and results.

        Args:
            training_type (Training): The type of training being performed, which can be:
            episode (int): The current episode number in the training process.
        """
        to_refresh = episode % self.inputs.comp.gui_inputs.spinbox_gui_refresh_rate.value() == 0
        if training_type == Training.BENCHMARK:
            self.sched_display.init_schedule_display()
            self._training_benchmark()
        elif training_type == Training.TRAINING and to_refresh:
            self.sched_display.init_schedule_display()
            self._training_training(episode)
        elif training_type == Training.OPTIMAL:
            self._training_optimal()

        self.process.worker.signals.gui_updated_signal.emit()
        if not self.process.thread.isRunning():
            print(f"Thread {self.process.thread} Stopped")

    @Slot()
    def stop_training_thread(self) -> None:
        """Stop the training thread if it is running."""

        if self.process and self.process.thread.isRunning():
            self.process.worker.request_stop()
            self.inputs.comp.gui_inputs.run.setText("Stopping...")
            self.inputs.comp.gui_inputs.run.setDisabled(True)

    def closeEvent(self, event) -> None:
        """Handle the close event to stop the training thread if it is running."""
        if self.process and self.process.thread.isRunning():
            self.stop_training_thread()
            self.process.thread.quit()
            self.process.thread.wait(5000)
        event.accept()
