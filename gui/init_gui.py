from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QFormLayout, QComboBox, 
                               QRadioButton, QPushButton, QFileDialog, QLineEdit, 
                               )
import sys

class InitialWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Crowd Counting")
        
        # Main layout
        layout = QVBoxLayout()

        # Parameter Settings
        form_layout = QFormLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["YOLO", "CSRNet", "OpenPose"])
        form_layout.addRow("Model:", self.model_combo)

        
        self.other_setting = QLineEdit()
        form_layout.addRow("Other Settings:", self.other_setting)
        
        layout.addLayout(form_layout)
        
        # Input Source Selection
        self.camera_radio = QRadioButton("Camera Stream")
        self.video_radio = QRadioButton("Video Input")
        layout.addWidget(self.camera_radio)
        layout.addWidget(self.video_radio)

        
        self.upload_button = QPushButton("Select Video File")
        self.upload_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.upload_button)
        
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["0", "1", "2"])
        layout.addWidget(self.camera_combo)
        
        # Start Button
        self.start_button = QPushButton("Start Counting")
        self.start_button.clicked.connect(self.start_main_gui)
        layout.addWidget(self.start_button)
        
        self.setLayout(layout)

    def open_file_dialog(self):
        file_dialog = QFileDialog()
        file_dialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.avi)")
    
    def start_main_gui(self):
        pass

if __name__ == "__main__":
    app = QApplication([])
    initial_window = InitialWindow()
    initial_window.show()
    app.exec()