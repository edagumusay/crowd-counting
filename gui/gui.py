import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, 
                               QRadioButton, QPushButton, QFileDialog, QMessageBox, QLabel, QGroupBox, QToolBar, QSizePolicy,
                               QTabWidget, QToolButton, QMenu, QWidgetAction)
from PySide6.QtGui import QIcon, QAction, QFont
from PySide6.QtCore import QSize, Qt

from crowd_counting_window import CrowdCountingWindow
from model_comparison_window import ModelComparisonWindow
from data_insights_window import DataInsightsWindow
from settings_window import SettingsWindow
import qdarktheme

class FixedWidthSpacer(QWidget):
    def __init__(self, width=5):
        super().__init__()
        self.setFixedWidth(width)

class ExpandingSpacer(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class RecentRunsGBox(QGroupBox):
    def __init__(self, data):
        super().__init__(parent=None)
        self.setTitle("Recent")
        # self.setStyleSheet("font-size: 14px;")
        self.setStyleSheet("""
            QGroupBox {
                border: 3px solid gray;
                border-radius: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-position: top center;
                padding: 0 10px;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        for time, action, user in data:
            item_layout = QHBoxLayout()
            time_label = QLabel(time)
            time_label.setFixedWidth(150)
            time_label.setAlignment(Qt.AlignCenter)

            action_label = QLabel(action)
            action_label.setFixedWidth(120)
            action_label.setAlignment(Qt.AlignCenter)

            user_label = QLabel(user)
            user_label.setFixedWidth(50)
            user_label.setAlignment(Qt.AlignCenter)

            item_layout.addWidget(time_label)
            item_layout.addWidget(action_label)
            item_layout.addWidget(user_label)

            layout.addLayout(item_layout)

        self.setLayout(layout)

class CustomPushButton(QWidget):
    def __init__(self, icon_path, label_text):
        super().__init__(parent=None)

        layout = QVBoxLayout(self)

        self.button = QPushButton()
        self.button.setIcon(QIcon(icon_path))
        self.button.setIconSize(QSize(30, 30))
        self.button.setSizePolicy(self.button.sizePolicy().horizontalPolicy(), self.button.sizePolicy().horizontalPolicy())
        self.button.setMaximumSize(90, 90)  # Adjust the button size if necessary
        self.button.setStyleSheet("""
            QPushButton {
                    background-color: #3498db;
                    border-radius: 30px;
                    padding: 30px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1c5980;
                }
            """)
        # Create a QLabel
        self.label = QLabel(label_text)
        self.label.setAlignment(Qt.AlignCenter)  # Center the label text
        self.label.setStyleSheet("font-size: 14px;")

        # Add the button and label to the layout
        layout.addWidget(self.button, alignment=Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

class CrowdCountingPushButton(QWidget):
    def __init__(self, icon_path, label_text):
        super().__init__(parent=None)

        # To be passed to the CrowdCountingWindow
        self.video_path = None
        self.crowd_counting_window = None

        layout = QVBoxLayout(self)

        self.button = QPushButton()
        self.button.setIcon(QIcon(icon_path))
        self.button.setIconSize(QSize(30, 30))
        self.button.setSizePolicy(self.button.sizePolicy().horizontalPolicy(), self.button.sizePolicy().horizontalPolicy())
        self.button.setMaximumSize(90, 90)  # Adjust the button size if necessary
        self.button.setStyleSheet("""
            QPushButton {
                    background-color: #f26d21;
                    border-radius: 30px;
                    padding: 30px;
                }
                QPushButton:hover {
                    background-color: #e75500;
                }
                QPushButton:pressed {
                    background-color: #da2e00;
                }
            """)

        # Create a QLabel
        self.label = QLabel(label_text)
        self.label.setAlignment(Qt.AlignCenter)  # Center the label text
        self.label.setStyleSheet("font-size: 14px;")

        # Dropdown button
        self.tool_button = QToolButton(self)
        self.tool_button.setStyleSheet("border: none; background: none; padding: 0px; margin: 0px;")
        self.tool_button.setMaximumSize(QSize(15, 15))
        self.tool_button.setPopupMode(QToolButton.InstantPopup)  # To show the menu on click

        # Create a menu to be used as dropdown
        menu = QMenu(self)

        # Create a widget container
        dropdown_widget = QWidget()
        dropdown_widget.setFixedHeight(140)
        dropdown_widget_layout = QVBoxLayout(dropdown_widget)

        # Input Source Selection
        self.camera_radio = QRadioButton("Camera Stream")
        self.camera_radio.toggled.connect(self.toggle_camera_radio)
        dropdown_widget_layout.addWidget(self.camera_radio)

        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["0", "1", "2"])
        self.camera_combo.hide()
        dropdown_widget_layout.addWidget(self.camera_combo)


        self.video_radio = QRadioButton("Video/Image Input")
        self.video_radio.toggled.connect(self.toggle_video_radio)
        dropdown_widget_layout.addWidget(self.video_radio)

        self.upload_button = QPushButton("Select File")
        self.upload_button.hide()
        self.upload_button.clicked.connect(self.open_file_dialog)
        dropdown_widget_layout.addWidget(self.upload_button)

        # Model selection
        self.model_combo = QComboBox()
        self.model_combo.addItems(["YOLO", "CSRNet", "OpenPose"])
        dropdown_widget_layout.addWidget(self.model_combo)

        # Add the widget to the menu
        dropdown_widget_action = QWidgetAction(menu)
        dropdown_widget_action.setDefaultWidget(dropdown_widget)
        menu.addAction(dropdown_widget_action)

        # Assign the menu to the tool button
        self.tool_button.setMenu(menu)

        # Layout container for label and tool button
        self.label_tool_button_layout = QHBoxLayout()
        self.label_tool_button_layout.setSpacing(0)
        self.label_tool_button_layout.addWidget(self.label)
        self.label_tool_button_layout.addWidget(self.tool_button)

        # Add the button and the label_tool_button_layout to the layout
        layout.addWidget(self.button, alignment=Qt.AlignCenter)
        layout.addLayout(self.label_tool_button_layout)

        self.button.clicked.connect(self.start_crowd_counting)

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

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self,"Select Video/Image File", "", "Video Files (*.mp4 *.avi);;Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)")
        if file_path:
            self.video_path = file_path
    
    def start_crowd_counting(self):
        if self.video_path:
            self.crowd_counting_window = CrowdCountingWindow(self.video_path)
            self.crowd_counting_window.show()
        else:
            QMessageBox.warning(self, 'Warning', 'Video source not selected!')

class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window size
        self.resize(950, 650)
        self.setStyleSheet("color: #B0B0B0;")
        self.setWindowTitle("Dashboard")

        # Initialize and set central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # ------------------ TabWidget -------------------------------
        # Create a QTabWidget
        self.tab_widget = QTabWidget()
        # Sytle to hide the pane and tabs
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                width: 0px;
                height: 0px;
                margin: 0px;
                padding: 0px;
            }
        """)
        main_layout.addWidget(self.tab_widget)

        # Add tabs to the QTabWidget
        self.home_tab = QWidget()
        self.overview_tab = QWidget()

        # Tabs layout
        self.home_layout = QHBoxLayout(self.home_tab)
        self.home_layout.setAlignment(Qt.AlignCenter)

        self.overview_layout = QVBoxLayout(self.overview_tab)

        # Add tabs to QTabWidget
        self.tab_widget.addTab(self.home_tab, "Home")
        self.tab_widget.addTab(self.overview_tab, "Overview")

        # ------------ The main toolbar -----------------------------
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setStyleSheet("QToolBar { padding: 10px; }")

        # App Logo
        app_name = QLabel("CrowdCountingApp")
        font = QFont("Courier New", 25, QFont.Bold) 
        app_name.setFont(font)
        app_name.setContentsMargins(10, 0, 0, 0)

        app_name.setStyleSheet(
            "QLabel {color: #3498db; margin-right: 80px  }"
        )
        
        toolbar.addWidget(app_name)

        # Home toolbar icon
        home_action = QAction(QIcon("gui/icons/home.png"), "Home", self)
        toolbar.addAction(home_action)
        home_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))

        toolbar.addWidget(FixedWidthSpacer(30))

        # Overview toolbar icon
        overview_action = QAction(QIcon("gui/icons/overview.png"), "Overview", self)
        toolbar.addAction(overview_action)
        overview_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))

        toolbar.addWidget(ExpandingSpacer())

        # More toolbar icon
        more_action = QAction(QIcon("gui/icons/more.png"), "More", self)
        toolbar.addAction(more_action)
        toolbar.addWidget(FixedWidthSpacer())

        # Info toolbar icon
        info_action = QAction(QIcon("gui/icons/info.png"), "Info", self)
        toolbar.addAction(info_action)
        toolbar.addWidget(FixedWidthSpacer())

        # Notification toolbar icon
        notification_action = QAction(QIcon("gui/icons/notification.png"), "Notification", self)
        toolbar.addAction(notification_action)
        toolbar.addWidget(FixedWidthSpacer())

        # Account toolbar icon
        account_action = QAction(QIcon("gui/icons/account.png"), "Account", self)
        toolbar.addAction(account_action)

        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # ------------ The homepage -----------------------------
        # Functional features -----
        functional_layout = QGridLayout()

        self.crowd_counting_button = CrowdCountingPushButton('gui/icons/crowd.png', 'Crowd counting') # Click event handled in CrowdCountingPushButton class
        
        self.model_comparison_button = CustomPushButton('gui/icons/compare.png', 'Model comparison')
        self.model_comparison_button.button.clicked.connect(self.start_model_comparison)

        self.data_insights_button = CustomPushButton('gui/icons/data.png', 'Data insights')
        self.data_insights_button.button.clicked.connect(self.start_data_insights)

        self.settings_button = CustomPushButton('gui/icons/settings.png', "Settings")
        self.settings_button.button.clicked.connect(self.start_settings)

        functional_layout.addWidget(self.crowd_counting_button, 0, 0)
        functional_layout.addWidget(self.model_comparison_button, 0, 1)
        functional_layout.addWidget(self.data_insights_button, 1, 0)
        functional_layout.addWidget(self.settings_button, 1, 1)

        # Recent runs ------
        # Some example recent run data
        recent_run_data = [
            ("2024-08-11 10:23:45", "Crowd counting", "Nijat"),
            ("2024-08-11 09:12:34", "Model Comparison", "Eda"),
            ("2024-08-11 08:45:12", "Model Comparison", "Daniel"),
            ("2024-08-11 09:12:34", "Model Comparison", "Daniel"), 
        ]
        recent_groupbox = RecentRunsGBox(recent_run_data)


        self.home_layout.addLayout(functional_layout)
        self.home_layout.addWidget(FixedWidthSpacer(80))
        self.home_layout.addWidget(recent_groupbox)

    
    def start_model_comparison(self):
        self.model_comparison_window = ModelComparisonWindow()
        self.model_comparison_window.show()

    def start_data_insights(self):
        self.data_insights_window = DataInsightsWindow()
        self.data_insights_window.show()

    def start_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()
    dashboard_window = DashboardWindow()
    dashboard_window.show()
    app.exec()