from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QFormLayout, QComboBox, 
                               QRadioButton, QPushButton, QFileDialog, QLineEdit, QMessageBox
                               )
import sys
from crowd_counting_window import CrowdCountingWindow
class InitialWindow(QWidget):
    def __init__(self):
        super().__init__()

        # To be passed to the MainWindow
        self.video_path = None
        
        self.setWindowTitle("Dashboard - Crowd Counting")

        self.crowd_counting_window = None
        
        # Main layout
        layout = QVBoxLayout()

        # Parameter Settings
        form_layout = QFormLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["YOLO", "CSRNet", "OpenPose"])
        form_layout.addRow("Model:", self.model_combo)

        
        self.parameters = QLineEdit("<Coming soon!>")
        self.parameters.setDisabled(True)

        form_layout.addRow("Parameters:", self.parameters)
        
        layout.addLayout(form_layout)
        
        # Input Source Selection
        self.camera_radio = QRadioButton("Camera Stream")
        self.camera_radio.toggled.connect(self.toggle_camera_radio)
        self.video_radio = QRadioButton("Video Input")
        self.video_radio.toggled.connect(self.toggle_video_radio)
        layout.addWidget(self.camera_radio)
        layout.addWidget(self.video_radio)

        
        self.upload_button = QPushButton("Select Video File")
        self.upload_button.hide()
        self.upload_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.upload_button)
        
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["0", "1", "2"])
        self.camera_combo.hide()
        layout.addWidget(self.camera_combo)
        
        # Start Button
        self.start_button = QPushButton("Start Counting")
        self.start_button.clicked.connect(self.start_main_gui)
        layout.addWidget(self.start_button)
        
        self.setLayout(layout)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.avi)")
        if file_path:
            self.video_path = file_path

    def toggle_camera_radio(self):
        if self.camera_radio.isChecked():
            self.camera_combo.show()
        else:
            self.camera_combo.hide()
    
    def toggle_video_radio(self):
        if self.video_radio.isChecked():
            self.upload_button.show()
        else:
            self.upload_button.hide()
    
    def start_main_gui(self):
        if self.video_path:
            self.crowd_counting_window = CrowdCountingWindow(self.video_path)
            # self.close()
            self.crowd_counting_window.show()
        else:
            QMessageBox.warning(self, 'Warning', 'Video source not selected!')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    initial_window = InitialWindow()
    initial_window.show()
    app.exec()