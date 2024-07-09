import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer

net = cv2.dnn.readNet("gui/yolo/yolov4.weights", "gui/yolo/yolov4.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

class VideoStream(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crowd Counting")
        self.video_label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        self.setLayout(layout)
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = self.detect_objects(frame)
            image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(image))

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