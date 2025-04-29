import sys
from PySide2.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QDateEdit, QRadioButton, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QFrame, QAction, QMessageBox, QHeaderView, QLineEdit
)
from PySide2.QtCore import Qt, QDate
from PySide2.QtGui import QPixmap, QIcon


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login Page")
        self.setFixedSize(400, 300)
        self.setWindowIcon(QIcon("resources/login.png"))
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Welcome Back!")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)

        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(35)

        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setFixedHeight(35)

        login_button = QPushButton("Login")
        login_button.setFixedHeight(35)
        login_button.clicked.connect(self.handle_login)

        layout.addWidget(title_label)
        layout.addSpacing(15)
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addSpacing(10)
        layout.addWidget(login_button)

        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial;
                font-size: 14px;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding-left: 10px;
                background-color: white;
            }
            QPushButton {
                background-color: #5cb85c;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
        """)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "password123":
            self.open_dashboard()
        else:
            QMessageBox.warning(self, "Failed", "Incorrect username or password.")

    def open_dashboard(self):
        self.admin_dashboard = AdminDashboard()
        self.admin_dashboard.show()
        self.close()


class AdminDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Dashboard - Inactivity Monitor")
        self.resize(1250, 700)
        self.setup_ui()
        self.setup_menu()

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignTop)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #1c1c1c;
                color: white;
                font-family: Arial;
            }
        """)

        profile_layout = QHBoxLayout()
        profile_pic = QLabel()
        pixmap = QPixmap("admin_profile.png").scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        profile_pic.setPixmap(pixmap)
        profile_details = QLabel("Admin\n🟢 online")
        profile_details.setStyleSheet("color: white; font-size: 13px; margin-left: 5px;")
        profile_layout.addWidget(profile_pic)
        profile_layout.addWidget(profile_details)
        sidebar_layout.addLayout(profile_layout)

        sidebar_layout.addSpacing(25)
        sidebar_layout.addWidget(QLabel("Select User:"))
        self.user_filter = QComboBox()
        self.user_filter.addItems(["All Users", "User1", "User2", "User3"])
        self.user_filter.setFixedHeight(35)
        self.user_filter.setStyleSheet("""
            QComboBox {
                color: #00FF7F;
                font-size: 12px;
                font-weight: bold;
                padding: 6px;
                border-radius: 6px;
                background-color: #2c2c2c;
            }
        """)
        self.user_filter.currentIndexChanged.connect(self.update_artiste_role)
        sidebar_layout.addWidget(self.user_filter)

        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(QLabel("Artist Role:"))
        self.artiste_role_label = QLabel("All Roles")
        self.artiste_role_label.setFixedHeight(35)
        self.artiste_role_label.setStyleSheet("""
            QLabel {
                color: #00FF7F;
                font-size: 12px;
                font-weight: bold;
                padding: 8px;
                border-radius: 6px;
                background-color: #2c2c2c;
            }
        """)
        sidebar_layout.addWidget(self.artiste_role_label)

        sidebar_layout.addSpacing(50)
        sidebar_layout.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setFixedHeight(30)
        sidebar_layout.addWidget(self.start_date)

        sidebar_layout.addWidget(QLabel("End Date:"))
        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setFixedHeight(30)
        sidebar_layout.addWidget(self.end_date)

        frame = QFrame()
        frame_layout = QVBoxLayout(frame)
        frame.setFrameShape(QFrame.Panel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setStyleSheet("""
            QFrame {
                border: 2px solid #00FF7F;
                border-radius: 8px;
                background-color: #2c2c2c;
            }
        """)
        self.pulse_radio = QRadioButton("Pulse")
        self.pulse_radio.setChecked(True)
        self.pulse_radio.setStyleSheet("QRadioButton { color: white; font-size: 12px; }")
        self.summary_radio = QRadioButton("Summaries")
        self.summary_radio.setStyleSheet("QRadioButton { color: white; font-size: 12px; }")

        search_button = QPushButton("Search Logs")
        search_button.setFixedHeight(35)
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #00FF7F;
                color: black;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00cc66;
            }
        """)
        search_button.clicked.connect(self.mock_fetch_logs)

        frame_layout.addWidget(self.pulse_radio)
        frame_layout.addWidget(self.summary_radio)
        frame_layout.addSpacing(10)
        frame_layout.addWidget(search_button)

        sidebar_layout.addSpacing(20)
        sidebar_layout.addWidget(frame)
        sidebar_layout.addStretch()

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)

        summary_frame = QFrame()
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setSpacing(10)

        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #1c1c1c;
            }
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        def create_tile(text):
            frame = QFrame()
            frame.setFixedSize(250, 40)
            frame.setStyleSheet("""
                QFrame {
                    background-color: #2c2c2c;
                }
                QLabel {
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
            layout = QVBoxLayout(frame)
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            return frame

        def create_row(*texts):
            row = QHBoxLayout()
            row.setSpacing(10)
            for text in texts:
                row.addWidget(create_tile(text))
            return row

        summary_layout.addLayout(create_row("Month :- April", "Holidays Month :- 2", "Total Workdays :- 20"))
        summary_layout.addSpacing(10)
        summary_layout.addLayout(create_row("Active Hours", "Inactive Hours"))
        summary_layout.addSpacing(10)
        summary_layout.addLayout(create_row(
            "Today :- " + QDate.currentDate().toString("dd/MM/yyyy"),
            "Today's Active Hours",
            "Today's Inactive Hours"
        ))

        content_layout.addWidget(summary_frame)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Username", "Timestamp", "Event Type", "Details"])
        self.table.setRowCount(0)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1c1c1c;
                color: white;
                font-family: Arial;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
                border: 1px solid #2c2c2c;
            }
            QTableWidget::item:selected {
                background-color: #00FF7F;
                color: black;
            }
            QHeaderView::section {
                background-color: #2c2c2c;
                color: white;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #2c2c2c;
            }
            QHeaderView::section:horizontal {
                border-top: 2px solid #00FF7F;
            }
            QHeaderView::section:vertical {
                border-left: 2px solid #00FF7F;
            }
        """)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        header = self.table.horizontalHeader()
        for col in range(4):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        content_layout.addWidget(self.table)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_widget)
        self.setCentralWidget(main_widget)

        self.user_roles = {
            "User1": "Singer",
            "User2": "Dancer",
            "User3": "Guitarist",
        }

    def setup_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #1c1c1c;
                color: white;
                font-family: Arial;
            }
            QMenuBar::item {
                background-color: #1c1c1c;
                padding: 2px;
            }
            QMenuBar::item:selected {
                background-color: #2c2c2c;
            }
            QMenu {
                background-color: #1c1c1c;
                color: white;
            }
            QMenu::item:selected {
                background-color: #2c2c2c;
            }
        """)
        file_menu = menubar.addMenu("File")
        file_menu.addAction(QAction("Exit", self, triggered=self.close))

        view_menu = menubar.addMenu("View")
        view_menu.addAction(QAction("Refresh", self, triggered=self.mock_fetch_logs))

        help_menu = menubar.addMenu("Help")
        help_menu.addAction(QAction("About", self, triggered=self.show_about))

    def update_artiste_role(self):
        selected_user = self.user_filter.currentText()
        self.artiste_role_label.setText(
            "All Roles" if selected_user == "All Users" else self.user_roles.get(selected_user, "Unknown Role")
        )

    def mock_fetch_logs(self):
        logs = [
            ("User1", "2025-04-25 10:00:00", "Pulse", "Active 3h 10m"),
            ("User2", "2025-04-25 10:05:00", "Summary", "Idle 15m"),
            ("User3", "2025-04-25 10:10:00", "Pulse", "Active 45m"),
        ]
        self.table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            for col, item in enumerate(log):
                self.table.setItem(row, col, QTableWidgetItem(item))

    def show_about(self):
        QMessageBox.information(self, "About", "Inactivity Monitor Admin Panel\nVersion 1.0\nDeveloped by Sanjay.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
