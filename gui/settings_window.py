from PySide6.QtWidgets import (QWidget)


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Settings")