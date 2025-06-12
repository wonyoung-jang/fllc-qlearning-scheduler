"""Main module for FLLC Q-Learning Tournament Scheduler."""

from PySide6.QtWidgets import QApplication

from .ui.gui import FLLCSchedulerGUI


def main() -> None:
    """Main function to run the FLLC Q-Learning Tournament Scheduler application."""
    app = QApplication()
    gui = FLLCSchedulerGUI()
    gui.show()
    app.exec()


if __name__ == "__main__":
    main()
