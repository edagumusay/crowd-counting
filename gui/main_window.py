import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QMenuBar, QToolBar, 
                               QWidget, QLabel, QGroupBox, QFormLayout, QLineEdit, 
                               QSpinBox, QPushButton)
from PySide6.QtGui import QAction, QImage, QPixmap
from PySide6.QtCore import QRunnable, Slot, QThreadPool
import os

# Add the parent directory to sys.path
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

from videoCount import *

class VideoCountWorker(QRunnable):
    def __init__(self, main_window_instance):
        super().__init__()
        self.main_window_instance = main_window_instance

    @Slot()
    def run(self):
        """
        Counts the number of people entering and exiting based on object tracking.
        """
        count = 0
        if self.main_window_instance.video_path:
            cap = cv2.VideoCapture(self.main_window_instance.video_path)
        else:
            cap = cv2.VideoCapture(test_video)
        
        ct = CentroidTracker(maxDisappeared=40, maxDistance=40)
        trackers = []
        trackableObjects = {}

        # Initialize the total number of frames processed thus far, along
        # with the total number of objects that have moved either up or down
        totalFrames = 0
        totalDown = 0
        totalUp = 0

        # Initialize empty lists to store the counting data
        total = []
        move_out = []
        move_in = []

        # Initialize video writer
        W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        # writer = cv2.VideoWriter('Final_output.mp4', fourcc, 30, (W, H), True)

        fps = FPS().start()
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            count += 1
            if count % 3 != 0:
                continue

            frame = cv2.resize(frame, (500, 280))

            per_corr = get_person_coordinates(frame)

            rects = []
            if totalFrames % 30 == 0:
                trackers = []
                for bbox in per_corr:
                    x1, y1, x2, y2 = bbox
                    rects.append([x1, y1, x2, y2])
                    tracker = dlib.correlation_tracker()
                    rect = dlib.rectangle(int(x1), int(y1), int(x2), int(y2))
                    tracker.start_track(frame, rect)
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 255), 1)
                    trackers.append(tracker)
            else:
                for tracker in trackers:
                    tracker.update(frame)
                    pos = tracker.get_position()
                    startX = int(pos.left())
                    startY = int(pos.top())
                    endX = int(pos.right())
                    endY = int(pos.bottom())
                    rects.append((startX, startY, endX, endY))

            cv2.line(frame, (0, H // 2 - 10), (W, H // 2 - 10), (0, 0, 0), 2)

            objects = ct.update(rects)

            for (objectID, centroid) in objects.items():
                to = trackableObjects.get(objectID)

                if to is None:
                    to = TrackableObject(objectID, centroid)
                else:
                    y = [c[1] for c in to.centroids]
                    direction = centroid[1] - np.mean(y)
                    to.centroids.append(centroid)

                    if not to.counted:
                        if direction < 0 and centroid[1] < H // 2 - 20:
                            totalUp += 1
                            move_out.append(totalUp)
                            to.counted = True
                        elif 0 < direction < 1.1 and centroid[1] > 144:
                            totalDown += 1
                            move_in.append(totalDown)
                            to.counted = True

                            total = []
                            total.append(len(move_in) - len(move_out))

                trackableObjects[objectID] = to

                text = "ID {}".format(objectID)
                cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (255, 255, 255), 2)
                cv2.circle(frame, (centroid[0], centroid[1]), 4, (255, 255, 255), -1)

            info_status = [
                ("Enter", totalUp),
                ("Exit ", totalDown),
            ]

            
            for (i, (k, v)) in enumerate(info_status):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, H - ((i * 20) + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

            # writer.write(frame)
            # cv2.imshow("People Count", frame)

            # Convert frame to QImage and display it
            label_size = self.main_window_instance.stream_display.size()
            label_width, label_height = label_size.width(), label_size.height()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame, (label_width, label_height))
            h, w, ch = frame_resized.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame_resized.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.main_window_instance.stream_display.setPixmap(QPixmap.fromImage(qt_image))

            if cv2.waitKey(1) & 0xFF == 27:
                break

            totalFrames += 1
            fps.update()

            end_time = time.time()
            num_seconds = (end_time - start_time)
            if num_seconds > 28800:
                break

        cap.release()
        # writer.release()
        cv2.destroyAllWindows()

        fps.stop()
        logger.info("Elapsed time: {:.2f}".format(fps.elapsed()))
        logger.info("Approx. FPS: {:.2f}".format(fps.fps()))

class MainWindow(QMainWindow):
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
        self.error_label = QLabel("0")
        self.result1_label = QLabel("0")
        self.result2_label = QLabel("0")
        
        results_layout.addRow("Current Count:", self.current_count_label)
        results_layout.addRow("Error:", self.error_label)
        results_layout.addRow("Result 1:", self.result1_label)
        results_layout.addRow("Result 2:", self.result2_label)
        
        side_panel_layout.addWidget(results_group)
        
        # Parameters
        parameters_group = QGroupBox("Parameters")
        settings_layout = QFormLayout(parameters_group)
        
        self.parameter0_label = QLineEdit()
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
        video_counter_thread = VideoCountWorker(self)
        self.threadpool.start(video_counter_thread)