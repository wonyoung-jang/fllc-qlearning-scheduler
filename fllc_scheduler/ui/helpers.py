"""QWidget helper functions for the FLLC Scheduler UI."""

from dataclasses import dataclass

from PySide6.QtWidgets import QDoubleSpinBox, QGroupBox, QTableWidget, QVBoxLayout


@dataclass(slots=True)
class WidgetHelper:
    """Data class to hold QWidget helper functions for the FLLC Scheduler UI."""

    @staticmethod
    def double_spin_box() -> QDoubleSpinBox:
        """Initialize a QDoubleSpinBox with common properties."""
        dblspin = QDoubleSpinBox()
        dblspin.setRange(0.01, 1.00)
        dblspin.setSingleStep(0.01)
        return dblspin

    @staticmethod
    def schedule_table(headers: list[str]) -> QTableWidget:
        """
        Create a QTableWidget with the specified headers.

        Args:
            headers (list[str]): The headers for the table.
        Returns:
            QTableWidget: The created table widget.
        """
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        return table

    @staticmethod
    def table_to_groupbox(title: str, table_widget: QTableWidget) -> QGroupBox:
        """Create a QGroupBox for the schedule display."""
        layout = QVBoxLayout()
        layout.addWidget(table_widget)
        groupbox = QGroupBox(title)
        groupbox.setLayout(layout)
        return groupbox
