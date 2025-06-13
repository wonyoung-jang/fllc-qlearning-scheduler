"""Module for GUI refresh inputs in the FLLC Q-Learning Tournament Scheduler."""

from dataclasses import dataclass

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QProgressBar, QPushButton, QSpinBox, QVBoxLayout

from ..q_learning.q_learning import QLearning


@dataclass(slots=True)
class GuiRefreshInputLabels:
    """Data class to hold labels for GUI refresh inputs in the FLLC Q-Learning Tournament Scheduler."""

    avg_reward: QLabel
    curr_sched_len: QLabel
    status: QLabel
    qlearning: QLabel
    qtable_size: QLabel


@dataclass(slots=True)
class GuiRefreshInputs(QGroupBox):
    """Data class to hold GUI refresh inputs for the FLLC Q-Learning Tournament Scheduler."""

    progressbar: QProgressBar
    spinbox_gui_refresh_rate: QSpinBox
    gui_refresh_layout: QHBoxLayout
    run: QPushButton
    exit: QPushButton
    label: GuiRefreshInputLabels

    def __post_init__(self) -> None:
        """Initialize the GUI refresh inputs with default values."""
        super(GuiRefreshInputs, self).__init__("Training Statistics")
        self.run.setShortcut("Ctrl+R")
        self.run.setToolTip("Ctrl + R to run analysis")
        self.exit.setShortcut("Ctrl+W")
        self.exit.setToolTip("Ctrl + W to exit")

    def initialize(self, q_learning: QLearning) -> None:
        """Initialize the GUI refresh inputs with default values."""
        self.gui_refresh_layout.addWidget(QLabel("Refresh GUI every: "))
        self.gui_refresh_layout.addWidget(self.spinbox_gui_refresh_rate)
        self.gui_refresh_layout.addWidget(QLabel("Episodes"))
        self.progressbar.setMaximum(q_learning.config.episodes)
        self.spinbox_gui_refresh_rate.setValue(1)
        self.update_labels(q_learning)
        self.set_layout()

    def update_labels(self, q_learning: QLearning) -> None:
        """Update the labels for the GUI refresh inputs."""
        self.label.qlearning.setText(
            f"Epsilon: {q_learning.param.epsilon:.2f} \n"
            f"Alpha: {q_learning.param.alpha:.2f} \n"
            f"Gamma: {q_learning.param.gamma:.2f} \n"
            f"Episodes: {q_learning.config.episodes}"
        )
        self.label.curr_sched_len.setText(
            f"Required Schedule Slots: {q_learning.data.config.get_required_schedule_slots()} "
            f"({q_learning.data.get_possible_schedule_slots()} Possible)"
        )
        self.label.qtable_size.setText(
            f"Q-Table Size: {len(q_learning.state.q_table)}/{q_learning.get_q_table_size_limit()}"
        )
        self.label.status.setText("Waiting for User to Complete Initialization")

    def set_layout(self) -> None:
        """Set the layout for the GUI refresh inputs."""
        layout = QVBoxLayout()
        layout.addWidget(self.label.status)
        layout.addWidget(self.label.avg_reward)
        layout.addWidget(self.label.curr_sched_len)
        layout.addWidget(self.label.qtable_size)
        layout.addWidget(self.label.qlearning)
        layout.addWidget(self.progressbar)
        layout.addLayout(self.gui_refresh_layout)
        layout.addWidget(self.run)
        layout.addWidget(self.exit)
        self.setLayout(layout)
