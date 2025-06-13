"""FLLC Scheduler Input Panel UI Module."""

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTimeEdit,
    QWidget,
)

from ..config import Configuration, Constraint, QParam, RoundType, Time
from ..data import FLLCSchedulerData
from .gui_refresh_inputs import GuiRefreshInputLabels, GuiRefreshInputs
from .helpers import WidgetHelper
from .q_learning_inputs import QLearningInputDoubleSpinBoxes, QLearningInputs
from .schedule_data_inputs import RoundTypeInputs, ScheduleDataInputs
from .soft_constraint_inputs import SoftConstraintInputLabels, SoftConstraintInputs
from .time_data_inputs import TimeDataInputLabels, TimeDataInputs, TimeDataInputTimeEdits


@dataclass(slots=True)
class FLLCSchedulerInputPanelComponents(QWidget):
    """Data class to hold the input panel for the FLLC Q-Learning Tournament Scheduler."""

    data: FLLCSchedulerData
    sched_inputs: ScheduleDataInputs = None
    round_inputs: RoundTypeInputs = None
    time_inputs: TimeDataInputs = None
    q_inputs: QLearningInputs = None
    gui_inputs: GuiRefreshInputs = None
    soft_constraint: SoftConstraintInputs = None

    def __post_init__(self) -> None:
        """Initialize the components of the input panel."""
        super(FLLCSchedulerInputPanelComponents, self).__init__()
        self.sched_inputs = self._init_sched_inputs()
        self.round_inputs = self._init_round_inputs()
        self.time_inputs = self._init_time_inputs()
        self.q_inputs = self._init_q_learning_inputs()
        self.gui_inputs = self._init_gui_refresh_inputs()
        self.soft_constraint = self._init_soft_constraint_inputs()

    def _init_sched_inputs(self) -> ScheduleDataInputs:
        """Initialize the ScheduleDataInputs with common properties."""
        sched_inputs = ScheduleDataInputs(
            spinbox_num_teams=QSpinBox(self),
            spinbox_num_rooms=QSpinBox(self),
            spinbox_num_tables=QSpinBox(self),
            label_num_tables_and_sides=QLabel(),
        )
        sched_inputs.initialize(self.data.schedule)
        return sched_inputs

    def _init_round_inputs(self) -> RoundTypeInputs:
        """Initialize the RoundTypeInputs with common properties."""
        round_inputs = RoundTypeInputs(
            spinboxes={
                RoundType.JUDGING: QLabel("1"),
                RoundType.PRACTICE: QSpinBox(self),
                RoundType.TABLE: QSpinBox(self),
            },
            labels={
                RoundType.JUDGING: QLabel(),
                RoundType.PRACTICE: QLabel(),
                RoundType.TABLE: QLabel(),
            },
        )
        round_inputs.initialize(self.data.schedule)
        return round_inputs

    def _init_time_inputs(self) -> TimeDataInputs:
        """Initialize the TimeDataInputs with common properties."""
        time_inputs = TimeDataInputs(
            timeedit=TimeDataInputTimeEdits(
                judging_start=QTimeEdit(self),
                practice_start=QTimeEdit(self),
                practice_stop=QTimeEdit(self),
                table_start=QTimeEdit(self),
                table_stop=QTimeEdit(self),
                practice_minimum=QTimeEdit(self),
                table_minimum=QTimeEdit(self),
            ),
            label=TimeDataInputLabels(
                duration_practice_round=QLabel(),
                duration_table_round=QLabel(),
                practice_time_available=QLabel(),
                table_time_available=QLabel(),
                judging_stop_time=QLabel(),
            ),
        )
        time_inputs.initialize(self.data.time)
        return time_inputs

    def _init_q_learning_inputs(self) -> QLearningInputs:
        """Initialize the QLearningInputs with common properties."""
        q_inputs = QLearningInputs(
            decays=[],
            spinbox_episodes=QSpinBox(self),
            label_epsilon_halfway=QLabel("0 episodes"),
            label_epsilon_total=QLabel("0 episodes"),
            dblspin=QLearningInputDoubleSpinBoxes(
                alpha=WidgetHelper.double_spin_box(),
                gamma=WidgetHelper.double_spin_box(),
                epsilon_start=WidgetHelper.double_spin_box(),
                epsilon_end=WidgetHelper.double_spin_box(),
                epsilon_decay=QDoubleSpinBox(self, decimals=3),
            ),
        )
        q_inputs.initialize(self.data.q_learning)
        return q_inputs

    def _init_gui_refresh_inputs(self) -> GuiRefreshInputs:
        """Initialize the GuiRefreshInputs with common properties."""
        gui_inputs = GuiRefreshInputs(
            progressbar=QProgressBar(self),
            spinbox_gui_refresh_rate=QSpinBox(self),
            gui_refresh_layout=QHBoxLayout(),
            run=QPushButton("Train then Generate Optimal Schedule", self),
            exit=QPushButton("Exit", self),
            label=GuiRefreshInputLabels(
                avg_reward=QLabel("Average Reward: "),
                curr_sched_len=QLabel(),
                status=QLabel(),
                qlearning=QLabel(),
                qtable_size=QLabel(),
            ),
        )
        gui_inputs.initialize(self.data.q_learning)
        return gui_inputs

    def _init_soft_constraint_inputs(self) -> SoftConstraintInputs:
        """Initialize the SoftConstraintInputs with common properties."""
        soft_constraint = SoftConstraintInputs(
            label=SoftConstraintInputLabels(
                table_consistency=QLabel(),
                opponent_variety=QLabel(),
                back_to_back_penalty=QLabel(),
                break_time=QLabel(),
            )
        )
        soft_constraint.initialize(self.data.q_learning)
        return soft_constraint

    def update_dependent_displays(self) -> None:
        """
        Update dependent displays based on the current state of the Q-Learning instance.
        This method is called to refresh the GUI elements that depend on the Q-Learning state.
        """
        self.soft_constraint.label.update_labels(self.data.q_learning)
        self.sched_inputs.update_labels(self.data.schedule)
        self.round_inputs.update_labels(self.data.schedule)
        self.time_inputs.update_labels(self.data.time)
        self.q_inputs.update_labels()
        self.gui_inputs.update_labels(self.data.q_learning)

    def collect_settings_from_ui(self) -> dict:
        """
        Collect the current settings from the GUI components and return them as a dictionary.

        Returns:
            dict: A dictionary containing the current settings from the GUI.
        """
        settings = {
            Configuration.NUM_TEAMS: self.sched_inputs.spinbox_num_teams.value(),
            Configuration.NUM_ROUNDS: self.sched_inputs.spinbox_num_rooms.value(),
            Configuration.NUM_TABLES: self.sched_inputs.spinbox_num_tables.value(),
            Configuration.ROUND_TYPES: {
                RoundType.PRACTICE: self.round_inputs.spinboxes[RoundType.PRACTICE].value(),
                RoundType.TABLE: self.round_inputs.spinboxes[RoundType.TABLE].value(),
            },
            Time.JUDGING_START: self.time_inputs.timeedit.judging_start.time().toString("hh:mm"),
            Time.PRACTICE_START: self.time_inputs.timeedit.practice_start.time().toString("hh:mm"),
            Time.PRACTICE_STOP: self.time_inputs.timeedit.practice_stop.time().toString("hh:mm"),
            Time.TABLE_START: self.time_inputs.timeedit.table_start.time().toString("hh:mm"),
            Time.TABLE_STOP: self.time_inputs.timeedit.table_stop.time().toString("hh:mm"),
            QParam.ALPHA: self.q_inputs.dblspin.alpha.value(),
            QParam.GAMMA: self.q_inputs.dblspin.gamma.value(),
            QParam.EPSILON_START: self.q_inputs.dblspin.epsilon_start.value(),
            QParam.EPSILON_END: self.q_inputs.dblspin.epsilon_end.value(),
            QParam.EPSILON_DECAY: self.q_inputs.dblspin.epsilon_decay.value(),
            QParam.EPISODES: self.q_inputs.spinbox_episodes.value(),
            Constraint.TABLE_CONSISTENCY: self.soft_constraint.slider.table_consistency.value() / 100.0,
            Constraint.OPP_VARIETY: self.soft_constraint.slider.opponent_variety.value() / 100.0,
            Constraint.BTB_PENALTY: self.soft_constraint.slider.back_to_back_penalty.value() / 100.0,
            Constraint.BREAK_TIME: self.soft_constraint.slider.break_time.value() / 100.0,
        }
        return settings


@dataclass(slots=True)
class FLLCSchedulerInputPanel(QWidget):
    """Input panel for the FLLC Q-Learning Tournament Scheduler."""

    data: FLLCSchedulerData
    comp: FLLCSchedulerInputPanelComponents = None

    def __post_init__(self) -> None:
        """Initialize the input panel with the necessary components."""
        super(FLLCSchedulerInputPanel, self).__init__()
        self.comp = FLLCSchedulerInputPanelComponents(self.data)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the UI components of the input panel."""
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.comp.sched_inputs)
        splitter.addWidget(self.comp.round_inputs)
        splitter.addWidget(self.comp.time_inputs)
        splitter.addWidget(self.comp.q_inputs)
        splitter.addWidget(self.comp.soft_constraint)
        splitter.addWidget(self.comp.gui_inputs)
        layout = QHBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)
