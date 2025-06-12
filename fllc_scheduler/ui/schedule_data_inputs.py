"""Data classes for the FLLC Q-Learning Tournament Scheduler inputs."""

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFormLayout, QGridLayout, QGroupBox, QLabel, QSpinBox

from ..config import RoundType
from ..schedule_data import ScheduleData


@dataclass(slots=True)
class ScheduleDataInputs(QGroupBox):
    """Data class to hold schedule data for the FLLC Q-Learning Tournament Scheduler."""

    spinbox_num_teams: QSpinBox
    spinbox_num_rooms: QSpinBox
    spinbox_num_tables: QSpinBox
    label_num_tables_and_sides: QLabel

    def __post_init__(self) -> None:
        """Initialize the schedule data inputs with default values."""
        super(ScheduleDataInputs, self).__init__("Schedule Data Inputs")

    def initialize(self, schedule_data: ScheduleData) -> None:
        """Create the input fields for schedule data."""
        self.spinbox_num_teams.setValue(schedule_data.config.num_teams)
        self.spinbox_num_rooms.setValue(schedule_data.config.num_rooms)
        self.spinbox_num_tables.setValue(schedule_data.config.num_tables)
        self.update_labels(schedule_data)
        self.set_layout()

    def update_labels(self, schedule_data: ScheduleData) -> None:
        """Update the labels for the schedule data inputs."""
        self.label_num_tables_and_sides.setText(str(schedule_data.config.num_tables * 2))

    def set_layout(self) -> None:
        """Set the layout for the schedule data inputs."""
        layout = QFormLayout(self)
        layout.addRow(QLabel("Number of Teams"), self.spinbox_num_teams)
        layout.addRow(QLabel("Number of Rooms"), self.spinbox_num_rooms)
        layout.addRow(QLabel("Number of Tables"), self.spinbox_num_tables)
        layout.addRow(QLabel("Number of Tables and Sides: "), self.label_num_tables_and_sides)


@dataclass(slots=True)
class RoundTypeInputs(QGroupBox):
    """Data class to hold round type inputs for the FLLC Q-Learning Tournament Scheduler."""

    spinboxes: dict[str, QSpinBox]
    labels: dict[str, QLabel]

    def __post_init__(self) -> None:
        """Initialize the round type inputs with default values."""
        super(RoundTypeInputs, self).__init__("Round Type Inputs")

    def initialize(self, schedule_data: ScheduleData) -> None:
        """Create the input fields for round types."""
        self.spinboxes[RoundType.JUDGING].setFont(QFont("Sans", 8, QFont.Weight.Bold))
        for name, spinbox in self.spinboxes.items():
            if name == RoundType.JUDGING:
                continue
            spinbox.setValue(schedule_data.config.round_types_per_team[name])
        self.update_labels(schedule_data)
        self.set_layout()

    def update_labels(self, schedule_data: ScheduleData) -> None:
        """Update the labels for the schedule data inputs."""
        for name in (RoundType.JUDGING, RoundType.PRACTICE, RoundType.TABLE):
            self.labels[name].setText(
                f"{schedule_data.config.num_teams * schedule_data.config.round_types_per_team[name]} Rounds"
            )

    def set_layout(self) -> None:
        """Set the layout for the round type inputs."""
        layout = QGridLayout(self)
        count = 0
        for name, spinbox in self.spinboxes.items():
            if name == RoundType.JUDGING:
                judging_label = QLabel("Judging")
                judging_label.setFont(QFont("Sans", 8, QFont.Weight.Bold))
                layout.addWidget(judging_label, count, 0)
            else:
                layout.addWidget(QLabel(name.capitalize()), count, 0)
            layout.addWidget(spinbox, count, 1)
            layout.addWidget(self.labels[name], count, 2, Qt.AlignmentFlag.AlignRight)
            count += 1
