"""Soft constraint panel for the FLLC Scheduler UI."""

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QSlider

from ..utils.config import Constraint
from ..q_learning.q_learning import QLearning


@dataclass(slots=True)
class SoftConstraintInputSliders:
    """Class to represent the sliders for soft constraints in the UI."""

    table_consistency: QSlider = None
    opponent_variety: QSlider = None
    back_to_back_penalty: QSlider = None
    break_time: QSlider = None

    def initialize(self, q_learning: QLearning) -> None:
        """Initialize the sliders with the QLearning instance."""
        self.table_consistency = self.init_slider(q_learning, Constraint.TABLE_CONSISTENCY)
        self.opponent_variety = self.init_slider(q_learning, Constraint.OPP_VARIETY)
        self.back_to_back_penalty = self.init_slider(q_learning, Constraint.BTB_PENALTY)
        self.break_time = self.init_slider(q_learning, Constraint.BREAK_TIME)

    def init_slider(self, q_learning: QLearning, constraint: Constraint) -> QSlider:
        """
        Create a slider for a specific soft constraint weight.

        Args:
            constraint (Constraint): The soft constraint for which to create the slider.
        Returns:
            QSlider: The created slider widget.
        """
        weight = q_learning.config.constraint_weights[constraint]
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setSingleStep(1)
        slider.setTickInterval(10)
        slider.setSliderPosition(weight * 100.0)
        return slider


@dataclass(slots=True)
class SoftConstraintInputLabels:
    """Class to represent the labels for soft constraints in the UI."""

    table_consistency: QLabel
    opponent_variety: QLabel
    back_to_back_penalty: QLabel
    break_time: QLabel

    def initialize(self, q_learning: QLearning) -> None:
        """Initialize the labels for the soft constraints."""
        self.update_labels(q_learning)

    def update_labels(self, q_learning: QLearning) -> None:
        """Update the labels for the soft constraints."""
        self.table_consistency.setText(self._label(q_learning, Constraint.TABLE_CONSISTENCY))
        self.opponent_variety.setText(self._label(q_learning, Constraint.OPP_VARIETY))
        self.back_to_back_penalty.setText(self._label(q_learning, Constraint.BTB_PENALTY))
        self.break_time.setText(self._label(q_learning, Constraint.BREAK_TIME))

    def _label(self, q_learning: QLearning, constraint: Constraint) -> str:
        """
        Create a label for a specific soft constraint weight.

        Args:
            constraint (Constraint): The soft constraint for which to create the label.
        Returns:
            str: The label text for the soft constraint.
        """
        weight = q_learning.config.constraint_weights[constraint]
        return f"{constraint}: {weight * 100:.2f}%"


@dataclass(slots=True)
class SoftConstraintInputs(QGroupBox):
    """Class to represent a soft constraint with its weight and label."""

    label: SoftConstraintInputLabels
    slider: SoftConstraintInputSliders = None

    def __post_init__(self) -> None:
        """Initialize the soft constraint inputs with default values."""
        super(SoftConstraintInputs, self).__init__("Soft Constraints Weights")
        self.slider = SoftConstraintInputSliders()

    def initialize(self, q_learning: QLearning) -> None:
        """Initialize the soft constraints with the QLearning instance."""
        self.slider.initialize(q_learning)
        self.label.initialize(q_learning)
        self.initialize_layout()

    def initialize_layout(self) -> None:
        """Initialize the layout for the soft constraints."""
        layout = QFormLayout(self)
        layout.addRow(self.label.table_consistency, self.slider.table_consistency)
        layout.addRow(self.label.opponent_variety, self.slider.opponent_variety)
        layout.addRow(self.label.back_to_back_penalty, self.slider.back_to_back_penalty)
        layout.addRow(self.label.break_time, self.slider.break_time)
