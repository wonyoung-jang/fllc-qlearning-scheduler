from PySide6.QtCore import QObject, Signal


class GUISignals(QObject):
    """
    Class to contain signals for updating the GUI.

    """

    # Signals
    update_gui_signal = Signal(int)
    gui_updated_signal = Signal()
