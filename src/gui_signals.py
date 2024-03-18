"""This module contains the GUISignals class, which is a QObject that contains signals for updating the GUI."""
from PySide6.QtCore import QObject, Signal


class GUISignals(QObject):
    """Class to contain signals for updating the GUI."""
    update_gui_signal = Signal(int)
    gui_updated_signal = Signal()