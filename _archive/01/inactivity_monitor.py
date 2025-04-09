import os
import time
import socket
import logging
from datetime import datetime
import connect_to_db
import yaml

BASE_DIR = os.path.join(os.environ["USERPROFILE"], "InactivityDetector")
SETTINGS_FILE = os.path.join("C:\\stuff\\source\\heartBeat", "settings.yaml")
LOG_FILE = os.path.join(BASE_DIR, "inactivity_monitor.log")

os.makedirs(BASE_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class InactivityMonitor:
    """Monitors inactivity and logs to MongoDB."""

    def __init__(self):
        self.username = os.getlogin()
        self.hostname = socket.gethostname()
        self.db = self.connect_to_db()
        self.status_file = os.path.join(BASE_DIR, "status.txt")
        self.load_settings()

    def load_settings(self):
        """Load settings from YAML file."""
        default_settings = {'timeout': 60, 'log_level': "DEBUG"}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    user_settings = yaml.safe_load(f)
                    self.settings = {**default_settings, **user_settings.get('settings', {})}
            except Exception as e:
                logging.error(f"Failed to load settings: {e}")
                self.settings = default_settings

    def connect_to_db(self):
        """Connect to MongoDB."""
        try:
            db = connect_to_db.MongoDatabase()
            logging.info("Connected to MongoDB.")
            return db
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return None

    def log_activity(self, status):
        """Log activity status to MongoDB."""
        entry = {"username": self.username, "hostname": self.hostname, "timestamp": datetime.now(), "status": status}
        if self.db:
            self.db.insert_pulse(entry)
            logging.info(f"Logged {status} to database.")

    def monitor(self):
        """Monitor inactivity based on status.txt."""
        last_status = "Active"
        while True:
            if os.path.exists(self.status_file):
                with open(self.status_file, "r") as f:
                    status = f.read().strip()
                if status != last_status:
                    self.log_activity(status)
                    last_status = status
            time.sleep(5)

if __name__ == "__main__":
    monitor = InactivityMonitor()
    monitor.monitor()
