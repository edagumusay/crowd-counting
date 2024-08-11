import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QMenuBar, QToolBar, 
                               QWidget, QLabel, QGroupBox, QFormLayout, QLineEdit, 
                               QSpinBox, QPushButton)
from PySide6.QtGui import QAction, QImage, QPixmap
from PySide6.QtCore import QRunnable, Slot, QThreadPool
import os
import cv2
import time
import pandas as pd
from ultralytics import YOLO

# Add the parent directory to sys.path
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

# Load the YOLO model and COCO labels
model = YOLO('yolov8x.pt')
with open("coco.txt", "r") as my_file:
    class_list = my_file.read().split("\n")

def get_person_coordinates(frame):
    results = model.predict(frame, verbose=False)
    a = results[0].boxes.data.detach().cpu()
    px = pd.DataFrame(a).astype("float")

    person_coords = []
    for _, row in px.iterrows():
        x1, y1, x2, y2 = row[0], row[1], row[2], row[3]
        class_id = int(row[5])
        if class_list[class_id] == 'person':
            person_coords.append([x1, y1, x2, y2])
    return person_coords

class VideoCountWorker(QRunnable):
    def __init__(self, main_window_instance):
        super().__init__()
        self.main_window_instance = main_window_instance
        self._is_running = True

    @Slot()
    def run(self):
        """
        Counts the number of people and draws rectangles around them.
        """
        start_time = time.time()
        if self.main_window_instance.video_path:
            cap = cv2.VideoCapture(self.main_window_instance.video_path)
        else:
            cap = cv2.VideoCapture("Input/input.mp4")
        
        fps = 0
        totalFrames = 0

        while self._is_running:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (500, 280))
            person_coords = get_person_coordinates(frame)

            # Draw rectangles and count people
            for bbox in person_coords:
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
            
            # Display the count on the frame
            people_count = len(person_coords)
            cv2.putText(frame, f"Total People: {people_count}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

            # GUI update
            self.main_window_instance.current_count_label.setText("%d" % people_count)

            # Convert frame to QImage and display it
            label_size = self.main_window_instance.stream_display.size()
            label_width, label_height = label_size.width(), label_size.height()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame, (label_width, label_height))
            h, w, ch = frame_resized.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame_resized.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.main_window_instance.stream_display.setPixmap(QPixmap.fromImage(qt_image))

            totalFrames += 1
            num_seconds_till_now = time.time() - start_time
            fps = totalFrames / num_seconds_till_now
            self.main_window_instance.fps_label.setText("%.2f" % fps)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        self._is_running = False

class CrowdCountingWindow(QMainWindow):
    def __init__(self, video_path):
        super().__init__()

        # For video counter
        self.video_path = video_path

        self.threadpool = QThreadPool()
        
        self.setWindowTitle("Crowd Counting")
        
        # Menu Bar
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        # Menubar actions
        file_menu_action = QAction("File", self)
        preference_menu_action = QAction("Preference", self)
        exit_menu_action = QAction("Exit", self)
        
        file_menu = menu_bar.addMenu("File")
        preference_menu = menu_bar.addMenu("Preference")
        exit_menu = menu_bar.addMenu("Exit")

        file_menu.addAction(file_menu_action)
        preference_menu.addAction(preference_menu_action)
        exit_menu.addAction(preference_menu_action)

        # Toolbar actions
        generate_report_action = QAction("Generate Report", self)
        access_data_action = QAction("Access Historical Data", self)

        # Toolbar
        tool_bar = QToolBar()
        self.addToolBar(tool_bar)
        
        tool_bar.addAction(generate_report_action)
        tool_bar.addAction(access_data_action)
        
        # Central Widget
        central_widget = QWidget()
        main_layout = QGridLayout(central_widget)
        
        # Main stream Display Area
        stream_layout = QVBoxLayout()
        self.stream_display = QLabel()
        self.stream_display.setStyleSheet("background-color: black;")
        self.stream_display.setMinimumSize(800, 600)
        stream_layout.addWidget(self.stream_display)
        
        # stream Controls
        stream_controls_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_clicked)
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_clicked)
        
        stream_controls_layout.addWidget(self.play_button)
        stream_controls_layout.addWidget(self.pause_button)
        stream_controls_layout.addWidget(self.stop_button)
        
        stream_layout.addLayout(stream_controls_layout)
        
        # Side Panel
        side_panel = QGroupBox("Results and Parameters")
        side_panel.setMaximumWidth(250)
        side_panel_layout = QVBoxLayout(side_panel)
        
        # Results
        results_group = QGroupBox("Results")
        results_layout = QFormLayout(results_group)
        
        self.current_count_label = QLabel("0")
        self.fps_label = QLabel("0")
        self.result3_label = QLabel("0")
        
        results_layout.addRow("Current Count:", self.current_count_label)
        results_layout.addRow("Approx. FPS:", self.fps_label)
        results_layout.addRow("Result 3:", self.result3_label)
        
        side_panel_layout.addWidget(results_group)
        
        # Parameters
        parameters_group = QGroupBox("Parameters")
        settings_layout = QFormLayout(parameters_group)
        
        self.parameter0_label = QLineEdit()
        self.parameter0_label.setDisabled(True)
        self.parameter1_label = QSpinBox()
        self.parameter2_label = QSpinBox()
        self.parameter3_label = QSpinBox()
        self.parameter4_label = QSpinBox()
        
        settings_layout.addRow("Parameter 0:", self.parameter0_label)
        settings_layout.addRow("Parameter 1:", self.parameter1_label)
        settings_layout.addRow("Parameter 2:", self.parameter2_label)
        settings_layout.addRow("Parameter 3:", self.parameter3_label)
        settings_layout.addRow("Parameter 4:", self.parameter4_label)
        
        side_panel_layout.addWidget(parameters_group)
        
        main_layout.addWidget(side_panel, 0, 0)
        main_layout.addLayout(stream_layout, 0, 1)
        
        self.setCentralWidget(central_widget)

    def play_clicked(self):
        self.video_counter_thread = VideoCountWorker(self)
        self.threadpool.start(self.video_counter_thread)
    
    def stop_clicked(self):
        if self.video_counter_thread is not None:
            print("stopping")
            self.video_counter_thread.stop()

    def closeEvent(self, event):
        if self.video_counter_thread is not None:
            print("stopping")
            self.video_counter_thread.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CrowdCountingWindow("path_to_your_video.mp4")
    window.show()
    sys.exit(app.exec())
