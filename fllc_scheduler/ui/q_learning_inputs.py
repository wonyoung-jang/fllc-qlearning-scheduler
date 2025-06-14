"""Module for Q-Learning input fields in the FLLC Q-Learning Tournament Scheduler."""

from dataclasses import dataclass

from PySide6.QtWidgets import QDoubleSpinBox, QFormLayout, QGroupBox, QLabel, QSpinBox

from ..q_learning.q_learning import QLearning


@dataclass(slots=True)
class QLearningInputDoubleSpinBoxes:
    """Data class to hold Q-Learning input double spin boxes."""

    alpha: QDoubleSpinBox
    gamma: QDoubleSpinBox
    epsilon_start: QDoubleSpinBox
    epsilon_end: QDoubleSpinBox
    epsilon_decay: QDoubleSpinBox


@dataclass(slots=True)
class QLearningInputs(QGroupBox):
    """Data class to hold Q-Learning inputs for the FLLC Q-Learning Tournament Scheduler."""

    decays: list[int]
    spinbox_episodes: QSpinBox
    label_epsilon_halfway: QLabel
    label_epsilon_total: QLabel
    dblspin: QLearningInputDoubleSpinBoxes = None

    def __post_init__(self) -> None:
        """Initialize the Q-Learning input fields with default values."""
        super(QLearningInputs, self).__init__("Q-Learning Inputs")
        self.set_layout()

    def initialize(self, q_learning: QLearning) -> None:
        """Initialize the Q-Learning input fields with default values."""
        self.dblspin.alpha.setValue(q_learning.param.alpha)
        self.dblspin.gamma.setValue(q_learning.param.gamma)
        self.dblspin.epsilon_start.setValue(q_learning.param.epsilon_start)
        self.dblspin.epsilon_end.setValue(q_learning.param.epsilon_end)
        self.dblspin.epsilon_decay.setValue(q_learning.param.epsilon_decay)
        self.dblspin.epsilon_decay.setRange(0.001, 1.000)
        self.dblspin.epsilon_decay.setSingleStep(0.001)
        self.spinbox_episodes.setValue(q_learning.config.episodes)
        self.spinbox_episodes.setRange(1, 100000)
        self.update_labels()

    def update_labels(self) -> None:
        """Update the labels for epsilon decay episodes."""
        halfway_decay, total_decay = self.calc_epsilon_decays()
        self.label_epsilon_halfway.setText(f"{halfway_decay} episodes")
        self.label_epsilon_total.setText(f"{total_decay} episodes")

    def calc_epsilon_decays(self) -> tuple[int, int, list]:
        """
        Calculate the number of episodes until epsilon reaches 0.5 and the total number of episodes
        until epsilon reaches the end value.
        Returns:
            tuple: A tuple containing the number of episodes until epsilon reaches 0.5,
                   the total number of episodes, and a list of epsilon values at each step.
        """
        e_start = self.dblspin.epsilon_start.value()
        e_end = self.dblspin.epsilon_end.value()
        e_decay = self.dblspin.epsilon_decay.value()
        epsilon_halfway = 0.5
        ep_count = 0
        ep_count_half = 0
        epsilon_decay_list = self.decays.append
        while e_start > e_end:
            e_start *= e_decay
            ep_count += 1
            if e_start > epsilon_halfway:
                ep_count_half += 1
            epsilon_decay_list(e_start)
        return ep_count_half, ep_count

    def set_layout(self) -> None:
        """Set the layout for the Q-Learning inputs."""

        layout = QFormLayout()
        layout.addRow("Learning Rate (α): ", self.dblspin.alpha)
        layout.addRow("Discount Factor (γ): ", self.dblspin.gamma)
        layout.addRow("Epsilon Start (Ɛ): ", self.dblspin.epsilon_start)
        layout.addRow("Epsilon End (Ɛ): ", self.dblspin.epsilon_end)
        layout.addRow("Epsilon Decay (Ɛ): ", self.dblspin.epsilon_decay)
        layout.addRow("Max Training Episodes: ", self.spinbox_episodes)
        layout.addRow(r"Epsilon 50% at: ", self.label_epsilon_halfway)
        layout.addRow("Epsilon End at:", self.label_epsilon_total)
        self.setLayout(layout)
