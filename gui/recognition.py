import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer

# Load YOLO model
net = cv2.dnn.readNet("gui/yolo/yolov4.weights", "gui/yolo/yolov4.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

class VideoStream(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crowd Counting")

        # Setup UI
        self.video_label = QLabel(self)
        self.camera_button = QPushButton("Use Camera", self)
        self.video_button = QPushButton("Load Video", self)
        
        # Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.camera_button)
        button_layout.addWidget(self.video_button)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.video_label)
        self.setLayout(main_layout)

        # Connections
        self.camera_button.clicked.connect(self.use_camera)
        self.video_button.clicked.connect(self.load_video)

        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.cap = None

    def use_camera(self):
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(0)
        self.timer.start(20)

    def load_video(self):
        video_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.avi *.mp4 *.mov)")
        if video_path:
            if self.cap is not None:
                self.cap.release()
            self.cap = cv2.VideoCapture(video_path)
            self.timer.start(20)

    def update_frame(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                frame = self.detect_objects(frame)
                image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(image))
            else:
                self.timer.stop()

    def detect_objects(self, frame):
        height, width, channels = frame.shape
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)

        class_ids = []
        confidences = []
        boxes = []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5 and class_id == 0:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str("person")
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoStream()
    window.show()
    sys.exit(app.exec())