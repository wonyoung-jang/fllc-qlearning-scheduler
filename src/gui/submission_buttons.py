from PySide6.QtWidgets import QPushButton, QSizePolicy
from config import Config


class SubmissionButtons:
    def __init__(self):
        """Creates submission buttons for training and generating optimal schedule."""
        # Submit(Train) Button
        self.train_button = QPushButton("Train then Generate Optimal Schedule (Ctrl + G)")
        self.train_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
