from PySide6.QtCore import QObject, Signal


# GUI SIGNALS OBJECT
class GUISignals(QObject):
    """
    Class to contain signals for updating the GUI.

    """

    # Signals (class attributes)
    update_gui_signal = Signal(int)
    gui_updated_signal = Signal()
