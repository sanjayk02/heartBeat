from datetime import datetime
import logging
import os

LOG_DIR = os.path.join(os.path.expanduser("~"), "InactivityLogs")
LOG_FILE = os.path.join(LOG_DIR, "monitor_log.txt")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class InactivityMonitor:
    def __init__(self):
        logging.info("📡 InactivityMonitor initialized")

    def log_external_status(self, status):
        now = datetime.now().isoformat()
        entry = {
            "timestamp": now,
            "status": status,
            "source": "status.txt"
        }
        logging.info(f"✅ Logged external status: {entry}")
        # If using MongoDB: self.db.insert_pulse(entry)
