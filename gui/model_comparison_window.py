from PySide6.QtWidgets import (QWidget)


class ModelComparisonWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Model Comparison")