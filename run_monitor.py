import os
import time
import logging
from datetime import datetime
import getpass
import socket
from inactivity_monitor import InactivityMonitor
from connect_to_db import MongoDatabase

# Paths
LOG_DIR = os.path.join(os.path.expanduser("~"), "InactivityLogs")
STATUS_FILE = os.path.join(LOG_DIR, "status.txt")
SHUTDOWN_FLAG = os.path.join(LOG_DIR, "shutdown.flag")
MONITOR_LOG = os.path.join(LOG_DIR, "monitor_log.txt")

# Logging setup
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=MONITOR_LOG,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class MonitorRunner:
    def __init__(self):
        self.monitor = InactivityMonitor()
        self.db = MongoDatabase()

        self.running = True
        self.last_status = None
        self.check_interval = 10  # seconds

        self.active_time = 0
        self.inactive_time = 0

        self.username = getpass.getuser()
        self.hostname = socket.gethostname()

    def read_status(self):
        if not os.path.exists(STATUS_FILE):
            return "Unknown"
        try:
            with open(STATUS_FILE, "r") as f:
                return f.read().strip().split(" - ")[-1]
        except Exception as e:
            logging.warning(f" Could not read status.txt: {e}")
            return "Unknown"

    def should_stop(self):
        return os.path.exists(SHUTDOWN_FLAG)

    def start_monitoring(self):
        logging.info(" MonitorRunner started.")
        while self.running:
            if self.should_stop():
                logging.info(" Detected shutdown.flag — stopping MonitorRunner.")
                break

            status = self.read_status()

            # Track time regardless of transition
            if self.last_status == "Active":
                self.active_time += self.check_interval
            elif self.last_status == "Inactive":
                self.inactive_time += self.check_interval

            if status != self.last_status:
                now = datetime.now()
                pulse = {
                    "username": self.username,
                    "hostname": self.hostname,
                    "timestamp": now,
                    "status": status,
                    "active_time": round(self.active_time / 60, 2),
                    "inactive_time": round(self.inactive_time / 60, 2)
                }

                try:
                    self.db.insert_pulse(pulse)
                    logging.info(f" Logged pulse to DB: {pulse}")
                except Exception as e:
                    logging.error(f" DB pulse logging failed: {e}")

                self.monitor.log_external_status(status)
                self.last_status = status

            time.sleep(self.check_interval)

if __name__ == "__main__":
    MonitorRunner().start_monitoring()
