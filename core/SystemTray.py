import os
import getpass
from datetime import datetime, timedelta
from PySide2.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PySide2.QtGui import QIcon
from PySide2.QtCore import QTimer


def hms_to_seconds(hms_str):
    """Convert 'hh:mm:ss' to total seconds."""
    try:
        h, m, s = map(int, hms_str.split(":"))
        return h * 3600 + m * 60 + s
    except:
        return 0

def format_seconds(sec):
    return str(timedelta(seconds=int(sec)))


class HeartBeatTray(QSystemTrayIcon):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.collection = self.db.get_collection()
        self.username = getpass.getuser()

        # === Tray Icon ===
        icon_path = os.path.join(os.path.dirname(__file__), "user_icon.png")
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            self.setIcon(QIcon.fromTheme("application-exit"))

        # === Menu ===
        self.menu = QMenu()

        self.status_action = QAction("Status: Unknown")
        self.session_action = QAction("Active: 00:00:00 / Inactive: 00:00:00")
        self.last_updated_action = QAction("Last Updated: N/A")
        self.refresh_action = QAction("↻ Refresh")

        self.refresh_action.triggered.connect(self.refresh)

        self.menu.addAction(self.status_action)
        self.menu.addAction(self.session_action)
        self.menu.addAction(self.last_updated_action)
        self.menu.addSeparator()
        self.menu.addAction(self.refresh_action)

        self.setContextMenu(self.menu)

        # === Auto-Refresh Timer ===
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(30000)  # Refresh every 30 seconds

        self.refresh()  # Initial load

    def refresh(self):
        doc = self.collection.find_one(
            {"username": self.username},
            sort=[("timestamp", -1)]
        )

        if doc:
            status = doc.get("status", "Unknown")
            timestamp = doc.get("timestamp", datetime.now())
            active_logged = doc.get("active_time", "00:00:00")
            inactive_logged = doc.get("inactive_time", "00:00:00")

            now = datetime.now()
            time_in_status = (now - timestamp).total_seconds()

            active_sec = hms_to_seconds(active_logged)
            inactive_sec = hms_to_seconds(inactive_logged)

            if status == "Active":
                active_total = format_seconds(active_sec + time_in_status)
                inactive_total = format_seconds(inactive_sec)
                emoji = "🟢"
            else:
                active_total = format_seconds(active_sec)
                inactive_total = format_seconds(inactive_sec + time_in_status)
                emoji = "🔴"

            self.status_action.setText(f"Status: {emoji} {status} ({self.username})")
            self.session_action.setText(f"Active: {active_total} / Inactive: {inactive_total}")
            self.last_updated_action.setText(f"Last Updated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

            self.setToolTip(
                f"{emoji} {status} - {self.username}\n"
                f"Active: {active_total} / Inactive: {inactive_total}\n"
                f"Last Updated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        else:
            self.status_action.setText("Status: N/A")
            self.session_action.setText("Active: 00:00:00 / Inactive: 00:00:00")
            self.last_updated_action.setText("Last Updated: N/A")
            self.setToolTip("No activity data found.")

