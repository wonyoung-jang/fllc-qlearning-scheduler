"""Time data inputs for the FLLC Q-Learning Tournament Scheduler."""

from dataclasses import dataclass

from PySide6.QtCore import QTime
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QTimeEdit

from ..data_model.time_data import TimeData
from ..utils.config import RoundType


@dataclass(slots=True)
class TimeDataInputLabels:
    """Data class to hold labels for time data inputs in the FLLC Q-Learning Tournament Scheduler."""

    duration_practice_round: QLabel
    duration_table_round: QLabel
    practice_time_available: QLabel
    table_time_available: QLabel
    judging_stop_time: QLabel


@dataclass(slots=True)
class TimeDataInputTimeEdits:
    """Data class to hold time edit widgets for time data inputs in the FLLC Q-Learning Tournament Scheduler."""

    judging_start: QTimeEdit
    practice_start: QTimeEdit
    practice_stop: QTimeEdit
    table_start: QTimeEdit
    table_stop: QTimeEdit
    practice_minimum: QTimeEdit
    table_minimum: QTimeEdit


@dataclass(slots=True)
class TimeDataInputs(QGroupBox):
    """Data class to hold time data for the FLLC Q-Learning Tournament Scheduler."""

    timeedit: TimeDataInputTimeEdits
    label: TimeDataInputLabels

    def __post_init__(self) -> None:
        """Initialize the time data inputs with default values."""
        super(TimeDataInputs, self).__init__("Time Data Inputs")

    def initialize(self, time_data: TimeData) -> None:
        """Create the input fields for time data."""
        self.timeedit.practice_minimum.setDisplayFormat("mm")
        self.timeedit.table_minimum.setDisplayFormat("mm")
        self.timeedit.practice_minimum.setTime(
            QTime.fromString(str(time_data.round_durations[RoundType.PRACTICE]), "mm")
        )
        self.timeedit.table_minimum.setTime(QTime.fromString(str(time_data.round_durations[RoundType.TABLE]), "mm"))
        self.timeedit.judging_start.setTime(QTime.fromString(time_data.time_setting.start_time_judging_rounds, "HH:mm"))
        self.timeedit.practice_start.setTime(
            QTime.fromString(time_data.time_setting.start_time_practice_rounds, "HH:mm")
        )
        self.timeedit.practice_stop.setTime(QTime.fromString(time_data.time_setting.start_time_break, "HH:mm"))
        self.timeedit.table_start.setTime(QTime.fromString(time_data.time_setting.start_time_table_rounds, "HH:mm"))
        self.timeedit.table_stop.setTime(QTime.fromString(time_data.time_setting.stop_time_table_rounds, "HH:mm"))
        self.update_labels(time_data)
        self.initialize_layout()

    def update_labels(self, time_data: TimeData) -> None:
        """Update the labels for the time data inputs."""
        duration = time_data.round_durations
        min_slots = time_data.min_slots
        judging_stop_time = self.timeedit.judging_start.time().addSecs(
            duration[RoundType.JUDGING] * 60 * min_slots[RoundType.JUDGING]
        )
        self.label.judging_stop_time.setText(judging_stop_time.toString("HH:mm"))
        self.label.duration_practice_round.setText(f"{duration[RoundType.PRACTICE]} minutes")
        self.label.duration_table_round.setText(f"{duration[RoundType.TABLE]} minutes")
        self.label.practice_time_available.setText(f"{time_data.duration_available.practice} minutes")
        self.label.table_time_available.setText(f"{time_data.duration_available.table} minutes")

    def initialize_layout(self) -> None:
        """Set the layout for the time data inputs."""

        label_duration_judging_round = QLabel("45 minutes")
        label_duration_judging_round.setFont(QFont("Sans", 8, QFont.Weight.Bold))
        layout = QFormLayout()
        layout.addRow("Judging Round Duration", label_duration_judging_round)
        layout.addRow("Practice Round Duration", self.label.duration_practice_round)
        layout.addRow("Minimum Practice Duration: ", self.timeedit.practice_minimum)
        layout.addRow("Table Round Duration", self.label.duration_table_round)
        layout.addRow("Minimum Table Duration:", self.timeedit.table_minimum)
        layout.addRow("Judging Rounds-Start", self.timeedit.judging_start)
        layout.addRow("Judging Rounds-Stop", self.label.judging_stop_time)
        layout.addRow("Practice Rounds-Start", self.timeedit.practice_start)
        layout.addRow("Practice Rounds-Stop", self.timeedit.practice_stop)
        layout.addRow("Table Rounds-Start", self.timeedit.table_start)
        layout.addRow("Table Rounds-Stop", self.timeedit.table_stop)
        layout.addRow("Practice Time Available", self.label.practice_time_available)
        layout.addRow("Table Time Available", self.label.table_time_available)
        self.setLayout(layout)
