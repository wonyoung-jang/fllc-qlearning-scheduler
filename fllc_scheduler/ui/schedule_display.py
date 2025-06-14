"""Schedule display for the FLLC Q-Learning Tournament Scheduler."""

from dataclasses import dataclass
from typing import ClassVar

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QSplitter, QTableWidget, QTableWidgetItem, QVBoxLayout

from ..data_model.schedule_data import Location
from ..q_learning.q_state import ScheduleState
from ..utils.config import LocationType, RoundType
from .helpers import WidgetHelper


@dataclass(slots=True)
class ScheduleDisplay(QGroupBox):
    """Data class to hold the schedule display for the FLLC Q-Learning Tournament Scheduler."""

    judging_headers: list[str]
    table_headers: list[str]
    table_judging: QTableWidget = None
    table_practice: QTableWidget = None
    table_round: QTableWidget = None

    tables: ClassVar[dict[RoundType, QTableWidget]] = {}
    col_index: ClassVar[dict[LocationType, int]] = {}

    def __post_init__(self) -> None:
        """Initialize the schedule display with default values."""
        super(ScheduleDisplay, self).__init__()
        self.setTitle("Schedule Display")

    def create_schedule_display(self, num_rooms: int, num_tables: int) -> None:
        """Create the widgets for displaying the schedule."""
        ScheduleDisplay.col_index = {}
        for i in range(1, num_rooms + 1):
            loc = Location(
                location_type=LocationType.ROOM,
                location_id=str(i),
            )
            ScheduleDisplay.col_index[loc] = i
        for c in range(num_tables):
            for side in (1, 2):
                char = chr(65 + c)
                loc = Location(
                    location_type=LocationType.TABLE,
                    location_id=char,
                    side=side,
                )
                ScheduleDisplay.col_index[loc] = (c * 2) + side

        self.table_judging = WidgetHelper.schedule_table(self.judging_headers)
        self.table_practice = WidgetHelper.schedule_table(self.table_headers)
        self.table_round = WidgetHelper.schedule_table(self.table_headers)
        ScheduleDisplay.tables = {
            RoundType.JUDGING: self.table_judging,
            RoundType.PRACTICE: self.table_practice,
            RoundType.TABLE: self.table_round,
        }
        groupbox_judging = WidgetHelper.table_to_groupbox("Judging Rounds", self.table_judging)
        groupbox_practice = WidgetHelper.table_to_groupbox("Practice Rounds", self.table_practice)
        groupbox_table = WidgetHelper.table_to_groupbox("Table Rounds", self.table_round)
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(groupbox_judging)
        splitter.addWidget(groupbox_practice)
        splitter.addWidget(groupbox_table)
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

    def init_schedule_display(self, schedule: list[ScheduleState]) -> None:
        """Initialize the schedule display tables with default values."""
        self._clear_and_setup_tables()
        last_row = {RoundType.JUDGING: {}, RoundType.PRACTICE: {}, RoundType.TABLE: {}}
        col_index = ScheduleDisplay.col_index
        for entry in sorted(schedule, key=lambda x: (x.time_slot, x.round_type, x.location.location_id)):
            time_start = entry.time_slot[0]
            round_type = entry.round_type
            location = entry.location
            team_id = entry.team_id

            table = ScheduleDisplay.tables[round_type]
            if time_start not in last_row[round_type]:
                new_row = table.rowCount()
                table.insertRow(new_row)
                table.setItem(new_row, 0, QTableWidgetItem(time_start))
                last_row[round_type][time_start] = new_row

            row = last_row[round_type][time_start]
            col = col_index[location]
            table.setItem(row, col, QTableWidgetItem(str(team_id)))

    def _setup_table(self, table: QTableWidget, headers: list[str]) -> None:
        """Set up a table with the given headers."""
        table.clearContents()
        table.setRowCount(0)
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

    def _clear_and_setup_tables(self) -> None:
        """Clear the schedule display tables and set them up with default properties."""
        for table, headers in (
            (self.table_judging, self.judging_headers),
            (self.table_practice, self.table_headers),
            (self.table_round, self.table_headers),
        ):
            self._setup_table(table, headers)
