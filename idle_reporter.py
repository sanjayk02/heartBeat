import os
import time
import logging
import getpass
import socket
import yaml
import ctypes
from datetime import datetime
from pynput import mouse, keyboard
from connect_to_db import MongoDatabase

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(os.path.expanduser("~"), "InactivityLogs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "idle_reporter.log")
STATUS_FILE = os.path.join(LOG_DIR, "status.txt")
SUMMARY_FILE = os.path.join(LOG_DIR, "session_summary.log")
SHUTDOWN_FLAG = os.path.join(LOG_DIR, "shutdown.flag")
CONFIG_PATH = os.path.join(BASE_DIR, "config.yml")

# === Load Configuration ===
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    return {}

config = load_config()
settings = config.get("settings", {})

# === Logging Setup ===
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class IdleReporter:
    def __init__(self):
        self.timeout = settings.get("timeout", 60)
        self.check_interval = settings.get("check_interval", 10)
        self.total_runtime = settings.get("total_runtime", 300)

        self.last_activity_time = time.time()
        self.status = None
        self.last_status_time = datetime.now()
        self.running = True

        self.active_seconds = 0
        self.inactive_seconds = 0

        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.start_time = datetime.now()

        self.db = MongoDatabase()

    def on_activity(self, *args):
        self.last_activity_time = time.time()

    def start_listeners(self):
        mouse.Listener(on_move=self.on_activity, on_click=self.on_activity, on_scroll=self.on_activity).start()
        keyboard.Listener(on_press=self.on_activity, on_release=self.on_activity).start()

    def is_session_active(self):
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            return hwnd != 0
        except Exception as e:
            logging.warning(f"Session check failed: {e}")
            return True  # fail-safe: assume active

    def write_status(self, status):
        now = datetime.now()
        if status != self.status:
            duration = (now - self.last_status_time).total_seconds() / 60.0
            logging.info(f"Status changed: {self.status} -> {status} | Duration: {duration:.2f} min")
            self.last_status_time = now
        self.status = status
        with open(STATUS_FILE, "w") as f:
            f.write(f"{now.isoformat()} - {status}")

    def log_session_summary(self):
        end_time = datetime.now()
        summary = {
            "username": self.username,
            "hostname": self.hostname,
            "timestamp": end_time,
            "status": self.status,
            "active_time": round(self.active_seconds / 60, 2),
            "inactive_time": round(self.inactive_seconds / 60, 2),
            "start_time": self.start_time,
            "end_time": end_time
        }

        with open(SUMMARY_FILE, "a") as f:
            f.write(str(summary) + "\n")

        try:
            self.db.insert_summary(summary)
            logging.info(f"✅ Summary logged to DB: {summary}")
        except Exception as e:
            logging.error(f"❌ DB summary logging failed: {e}")

    def monitor(self):
        self.start_listeners()
        start_time = time.time()

        while self.running:
            if time.time() - start_time > self.total_runtime:
                logging.info("🛑 IdleReporter finished due to total_runtime limit.")
                with open(SHUTDOWN_FLAG, "w") as f:
                    f.write("done")
                break

            if not self.is_session_active():
                logging.debug("🕶️ Session not active - skipping check")
                time.sleep(self.check_interval)
                continue

            idle_duration = time.time() - self.last_activity_time
            current_status = "Inactive" if idle_duration > self.timeout else "Active"

            if current_status == "Active":
                self.active_seconds += self.check_interval
            else:
                self.inactive_seconds += self.check_interval

            self.write_status(current_status)
            time.sleep(self.check_interval)

        self.log_session_summary()

if __name__ == "__main__":
    if os.path.exists(SHUTDOWN_FLAG):
        os.remove(SHUTDOWN_FLAG)

    logging.info("✅ IdleReporter started (session-aware config version).")
    IdleReporter().monitor()
