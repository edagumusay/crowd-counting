import sys
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QWidget, QLabel, QGroupBox, QFormLayout, QLineEdit, 
                               QSpinBox, QPushButton, QSlider)
from PySide6.QtGui import QImage, QPixmap, QGuiApplication, QIcon
from PySide6.QtCore import Qt, QRunnable, Slot, QThreadPool, QSize

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
model = YOLO('trained_models/best.pt')
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
        self._is_running = False
        self._is_paused = False

        self.cap = None

        if self.main_window_instance.stream_mode == 'file' and self.main_window_instance.video_path:
            self.cap = cv2.VideoCapture(self.main_window_instance.video_path)
        elif self.main_window_instance.stream_mode == 'camera':
            if self.cap is not None: # realease any previously opened camera
                self.cap.release()
            self.cap = cv2.VideoCapture(self.main_window_instance.camera_index)
        self.frame = None


        # For the slider
        if self.main_window_instance.stream_mode == 'file':
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        else:
            self.total_frames = 0


    @Slot()
    def run(self):
        """
        Counts the number of people and draws rectangles around them.
        """
        start_time = time.time()
        
        fps = 0
        totalFrames = 0

        self._is_running = True
        while self._is_running:
            ret, self.frame = self.cap.read()
            if not ret:
                break

            self.frame = cv2.resize(self.frame, (500, 280))
            person_coords = get_person_coordinates(self.frame)

            # Draw rectangles and count people
            for bbox in person_coords:
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(self.frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
            
            # Display the count on the frame
            people_count = len(person_coords)
            cv2.putText(self.frame, f"Total People: {people_count}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

            # GUI update
            self.main_window_instance.current_count_label.setText("%d" % people_count)

            # Display the frame
            self.display_frame(self.frame)

            totalFrames += 1
            num_seconds_till_now = time.time() - start_time
            fps = totalFrames / num_seconds_till_now
            self.main_window_instance.fps_label.setText("%.2f" % fps)

            while(self._is_paused):
                pass

        self.cap.release()
        cv2.destroyAllWindows()
    
    def stop(self):
        self._is_running = False

    def pause(self):
        self._is_paused = True

    def resume(self):
        self._is_paused = False


    def display_frame(self, frame):
        # Convert frame to QImage and display it
        label_size = self.main_window_instance.stream_display.size()
        label_width, label_height = label_size.width(), label_size.height()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame, (label_width, label_height))
        h, w, ch = frame_resized.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_resized.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.main_window_instance.stream_display.setPixmap(QPixmap.fromImage(qt_image))

        # Update the slider position
        current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.update_slider(current_frame)

    def slider_released(self):
        self.seek_video(self.main_window_instance.slider.value())

    
    def seek_video(self, frame_number):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, self.frame = self.cap.read()
        if ret:
            self.display_frame(self.frame)
    
    def display_first_frame(self):
        # Capture the first frame
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, self.frame = self.cap.read()
        if ret:
            self.display_frame(self.frame)
        # Reset the frames again
        if self.main_window_instance.stream_mode == 'file': # when reading from a file, readjust the frame progress
            self.cap.release()  # Release the current capture
            self.cap = cv2.VideoCapture(self.main_window_instance.video_path)
    
    def update_slider(self, frame_number):
        self.main_window_instance.slider.setValue(frame_number)


class CrowdCountingWindow(QWidget):
    def __init__(self, stream_mode = 'file', video_path = None, camera_index = 0):
        super().__init__()

        self.setWindowTitle("Crowd Counting")

        # For video counter
        self.video_path = video_path
        self.threadpool = QThreadPool()
        self.stream_mode = stream_mode # 'file' for image/video files or 'camera' for camera stream
        self.camera_index = camera_index


        # Init the handle for VideoCountWorker thread
        self.video_counter_thread = VideoCountWorker(self)
        
        main_layout = QGridLayout(self)
        
        # Main stream Display Area
        stream_layout = QVBoxLayout()
        self.stream_display = QLabel()
        self.stream_display.setStyleSheet("background-color: black;")
        self.stream_display.setMinimumSize(800, 600)
        stream_layout.addWidget(self.stream_display)

        
        # stream Controls
        stream_control_layout = QVBoxLayout()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, self.video_counter_thread.total_frames - 1)
        print(self.video_counter_thread.total_frames)
        stream_control_layout.addWidget(self.slider)

        
        self.slider.sliderReleased.connect(self.video_counter_thread.slider_released)

        play_pause_stop_layout = QHBoxLayout()
        self.start_button = QPushButton()
        self.start_button.setIcon(QIcon('gui/icons/play.png'))
        self.start_button.setIconSize(QSize(15, 15))
        self.start_button.setSizePolicy(self.start_button.sizePolicy().horizontalPolicy(), self.start_button.sizePolicy().horizontalPolicy())
        self.start_button.setMaximumSize(30, 30)
        self.start_button.setStyleSheet("""
            QPushButton {
                    background-color: #3498db;
                    border-radius: 8px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1c5980;
                }
            """)
        self.start_button.clicked.connect(self.play_clicked)


        self.pause_button = QPushButton()
        self.pause_button.setIcon(QIcon('gui/icons/pause.png'))
        self.pause_button.setIconSize(QSize(15, 15))
        self.pause_button.setSizePolicy(self.pause_button.sizePolicy().horizontalPolicy(), self.pause_button.sizePolicy().horizontalPolicy())
        self.pause_button.setMaximumSize(30, 30)
        self.pause_button.setStyleSheet("""
            QPushButton {
                    background-color: #3498db;
                    border-radius: 8px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1c5980;
                }
            """)
        self.pause_button.clicked.connect(self.pause_clicked)


        self.reset_button = QPushButton()
        self.reset_button.setIcon(QIcon('gui/icons/reset.png'))
        self.reset_button.setIconSize(QSize(15, 15))
        self.reset_button.setSizePolicy(self.reset_button.sizePolicy().horizontalPolicy(), self.reset_button.sizePolicy().horizontalPolicy())
        self.reset_button.setMaximumSize(30, 30)
        self.reset_button.setStyleSheet("""
            QPushButton {
                    background-color: #3498db;
                    border-radius: 8px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1c5980;
                }
            """)
        self.reset_button.clicked.connect(self.reset_clicked)

        
        play_pause_stop_layout.addWidget(self.start_button)
        play_pause_stop_layout.addWidget(self.pause_button)
        play_pause_stop_layout.addWidget(self.reset_button)

        stream_control_layout.addLayout(play_pause_stop_layout)
        
        stream_layout.addLayout(stream_control_layout)
        
        side_panel_layout = QVBoxLayout()
        
        # Results
        results_group = QGroupBox("Results")
        results_group.setMinimumWidth(200)
        results_layout = QFormLayout(results_group)
        
        self.current_count_label = QLabel("0")
        self.fps_label = QLabel("0")
        self.result3_label = QLabel("0")
        
        results_layout.addRow("Current Count:", self.current_count_label)
        results_layout.addRow("Approx. FPS:", self.fps_label)
        
        side_panel_layout.addWidget(results_group)
        
        main_layout.addLayout(side_panel_layout, 0, 0)
        main_layout.addLayout(stream_layout, 0, 1)

        self.resize(1200, 600)  # Set an initial size for the window

        # Display the first frame
        self.video_counter_thread.display_first_frame()
    
    def showEvent(self, event):
        super().showEvent(event)
        self.center()

    def center(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            window_geometry = self.geometry()
            x = (screen_geometry.width() - window_geometry.width()) // 2
            y = (screen_geometry.height() - window_geometry.height()) // 2
            self.move(x, y)

        

    def play_clicked(self):
        if self.video_counter_thread._is_paused: # When there is an active thread already and paused
            self.video_counter_thread.resume()
        elif self.video_counter_thread._is_running is not True:
            self.threadpool.start(self.video_counter_thread)

    def pause_clicked(self):
        if self.video_counter_thread is not None:
            self.video_counter_thread.pause()
    
    def reset_clicked(self):
        if self.video_counter_thread is not None:
            self.video_counter_thread.display_first_frame()

    def closeEvent(self, event):
        if self.video_counter_thread is not None:
            self.video_counter_thread.stop()