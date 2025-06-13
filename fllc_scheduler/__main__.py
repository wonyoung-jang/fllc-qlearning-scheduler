"""Main module for FLLC Q-Learning Tournament Scheduler."""

import logging

from PySide6.QtWidgets import QApplication

from .ui.gui import FLLCSchedulerGUI

logger = logging.getLogger(__name__)


def main() -> None:
    """Main function to run the FLLC Q-Learning Tournament Scheduler application."""
    logging.basicConfig(
        filename="fllc_scheduler.log",
        filemode="w",
        format="%(levelname)s[%(asctime)s] (%(name)s) %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
    )

    logger.info("Starting FLLC Q-Learning Tournament Scheduler application.")

    app = QApplication()
    gui = FLLCSchedulerGUI()
    gui.show()
    app.exec()

    logger.info("Stopping FLLC Q-Learning Tournament Scheduler application.")


if __name__ == "__main__":
    main()
