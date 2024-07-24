import sys
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QMenuBar, QToolBar, 
                               QWidget, QLabel, QGroupBox, QFormLayout, QLineEdit, 
                               QSpinBox, QPushButton, QListWidget)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
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
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        
        stream_controls_layout.addWidget(self.play_button)
        stream_controls_layout.addWidget(self.pause_button)
        stream_controls_layout.addWidget(self.stop_button)
        
        stream_layout.addLayout(stream_layout)
        stream_layout.addLayout(stream_controls_layout)
        
        # Side Panel
        side_panel = QGroupBox("Results and Parameters")
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


if __name__ == "__main__":
    app = QApplication([])
    initial_window = MainWindow()
    initial_window.show()
    app.exec()