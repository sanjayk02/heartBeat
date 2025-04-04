"""
    InactivityTracker.py
    ---------------------

    This script is a user-space agent that monitors keyboard and mouse activity for the currently logged-in user.
    Its main purpose is to track user presence and log both real-time activity and full session summaries into a MongoDB database.

    Features:
    - Detects periods of user inactivity based on configurable timeout (default: 5 minutes).
    - Continuously tracks active and inactive time.
    - Logs real-time "activity pulses" to MongoDB with timestamps and user status.
    - At the end of each day or on shutdown, logs a complete session summary:
        - Total active and inactive durations
        - Session start and end times
    - Writes a status file for service-level visibility:
        - `C:\\ProgramData\\InactivityMonitor\\statuses\\<username>_status.txt`
        - Status values: "Active" or "Inactive"
    - Maintains daily logs in the user's folder:
        - `C:\\Users\\<username>\\InactivityLogs\\activity_monitor.log`

    Integration:
    - This agent complements the system-level `inactivity_service.py`, which logs login/logout events.
    - One-way communication: Agent updates status files that the service can read.

    Deployment:
    - Should be configured to start on user login (e.g., via Startup folder or Group Policy).
    - Requires `pynput`, `pyyaml`, `pymongo`, and `pywin32` Python packages.

    Configuration:
    - Settings are loaded from: `../config/config.yml`
        - timeout: idle threshold in seconds
        - check_interval: activity check frequency in seconds

    Author: [Your Name or Team]
    Date: [Date]
"""
# =================================================================================================
# === Imports ===
# =================================================================================================
import os
import time
import logging
import getpass
import socket
import yaml
import signal
from datetime import datetime, timedelta
from pynput import mouse, keyboard
from connect_to_db import MongoDatabase

# === Paths ===
username = getpass.getuser()

LOG_DIR = os.path.join(os.path.expanduser("~"), "InactivityLogs")
STATUS_DIR_USER = os.path.join(LOG_DIR, "statuses")
STATUS_DIR_SHARED = r"C:\ProgramData\InactivityMonitor\statuses"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STATUS_DIR_USER, exist_ok=True)
os.makedirs(STATUS_DIR_SHARED, exist_ok=True)

def get_daily_log_file():
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"monitor_{today}.log")

LOG_FILE = get_daily_log_file()

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === Configuration ===
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yml")
    try:
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f) or {}
        return cfg.get("settings", {})
    except Exception as e:
        logging.error(f"Config load error: {e}")
        return {}

settings        = load_config()
TIMEOUT         = settings.get("timeout", 300)
CHECK_INTERVAL  = settings.get("check_interval", 60)

# === Helper Functions ===
def format_hms(seconds):
    return str(timedelta(seconds=int(seconds)))

def update_status(status):
    try:
        # User-local status
        user_status_file = os.path.join(STATUS_DIR_USER, f"{username}_status.txt")
        with open(user_status_file, "w") as f:
            f.write(status)

        # Shared system-wide status
        shared_status_file = os.path.join(STATUS_DIR_SHARED, f"{username}_status.txt")
        with open(shared_status_file, "w") as f:
            f.write(status)

        logging.info(f"Status updated to '{status}' in both paths.")
    except Exception as e:
        logging.error(f"Failed to update status files: {e}")

# =================================================================================================
# === ActivityMonitor Class ===
# =================================================================================================
class ActivityMonitor:
    # ---------------------------------------------------------------------------------------------
    # Constants
    # ---------------------------------------------------------------------------------------------
    def __init__(self):

        self.username           = getpass.getuser()
        self.hostname           = socket.gethostname()
        self.db                 = MongoDatabase()
        self.active_seconds     = 0
        self.inactive_seconds   = 0
        self.last_activity_time = time.time()
        self.status             = "Active"
        self.running            = True
        self.start_time         = datetime.now()
        self.current_day        = self.start_time.date()
        self.last_check_time    = time.time()

    # ---------------------------------------------------------------------------------------------
    # on_activity callback
    # ---------------------------------------------------------------------------------------------
    def on_activity(self, *args):

        self.last_activity_time = time.time()

    # ---------------------------------------------------------------------------------------------
    # Listener methods
    # ---------------------------------------------------------------------------------------------
    def start_listeners(self):

        mouse.Listener(on_move=self.on_activity, on_click=self.on_activity, on_scroll=self.on_activity).start()
        keyboard.Listener(on_press=self.on_activity, on_release=self.on_activity).start()

    # ---------------------------------------------------------------------------------------------
    # Logging methods
    # ---------------------------------------------------------------------------------------------
    def log_pulse(self):
        """
        Logs a MongoDB pulse with the time spent in the previous status.
        Also writes a human-readable entry to monitor.log.
        """
        now = datetime.now()
        total_runtime = (now - self.start_time).total_seconds()

        pulse = {
            "username"      : self.username,
            "hostname"      : self.hostname,
            "timestamp"     : now,
            "status"        : self.status,
            "active_time"   : format_hms(self.active_seconds),
            "inactive_time" : format_hms(self.inactive_seconds),
            "total_runtime" : format_hms(total_runtime),
            "tag"           : "Activity"
        }

        try:
            # Insert into MongoDB
            self.db.insert_pulse(pulse)
            logging.info(f"Pulse logged to DB: {pulse}")

            # Log to monitor.log in clean format
            log_msg = (
                f"[Pulse] User: {self.username} | Status: {self.status} | "
                f"Active: {format_hms(self.active_seconds)} | "
                f"Inactive: {format_hms(self.inactive_seconds)} | "
                f"Total Runtime: {format_hms(total_runtime)}"
            )
            logging.info(log_msg)

        except Exception as e:
            logging.error(f"Pulse logging error: {e}")

    # ---------------------------------------------------------------------------------------------
    # Session summary methods
    # ---------------------------------------------------------------------------------------------
    def log_session_summary(self):
        """
        Logs a session summary to MongoDB and writes a readable version to monitor.log.
        """
        end_time = datetime.now()
        total_time = self.active_seconds + self.inactive_seconds

        summary = {
            "username"      : self.username,
            "hostname"      : self.hostname,
            "timestamp"     : end_time,
            "active_time"   : format_hms(self.active_seconds),
            "inactive_time" : format_hms(self.inactive_seconds),
            "start_time"    : self.start_time,
            "end_time"      : end_time,
            "total_duration": format_hms(total_time),
            "tag"           : "SessionSummary"
        }

        try:
            # Save to MongoDB
            self.db.insert_summary(summary)
            logging.info(f"Session summary logged to DB: {summary}")

            # Log to monitor.log in clean format
            log_msg = (
                f"[Session Summary] User: {self.username} | "
                f"Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} | "
                f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S')} | "
                f"Active: {format_hms(self.active_seconds)} | "
                f"Inactive: {format_hms(self.inactive_seconds)} | "
                f"Total: {format_hms(total_time)}"
            )
            logging.info(log_msg)

        except Exception as e:
            logging.error(f"Session summary logging error: {e}")

        # Reset counters for next session
        self.active_seconds = 0
        self.inactive_seconds = 0
        self.start_time = datetime.now()

    # ---------------------------------------------------------------------------------------------
    # Main run method
    # ---------------------------------------------------------------------------------------------
    def run(self):
        """
        Monitors user activity and tracks active/inactive periods.

        Logs a pulse each time the user switches between Active and Inactive.
        Each pulse only includes the duration spent in the previous state.
        """
        logging.info("Activity Monitor started.")
        self.start_listeners()
        update_status("Active")

        self.last_check_time = time.time()
        self.last_status_time = self.last_check_time

        while self.running:
            now = datetime.now()
            current_time = time.time()

            # Detect new status based on idle time
            idle_duration = current_time - self.last_activity_time
            new_status = "Inactive" if idle_duration >= TIMEOUT else "Active"

            # Detect status change
            if new_status != self.status:
                # Time spent in previous status
                duration = current_time - self.last_status_time

                if self.status == "Active":
                    self.active_seconds = duration
                    self.inactive_seconds = 0
                else:
                    self.inactive_seconds = duration
                    self.active_seconds = 0

                self.log_pulse()

                # Update to new status
                self.status = new_status
                update_status(self.status)

                # Reset timers
                self.last_status_time = current_time
                self.active_seconds = 0
                self.inactive_seconds = 0

            time.sleep(CHECK_INTERVAL)

        # Graceful shutdown — log final pulse
        final_duration = time.time() - self.last_status_time
        if self.status == "Active":
            self.active_seconds = final_duration
            self.inactive_seconds = 0
        else:
            self.inactive_seconds = final_duration
            self.active_seconds = 0

        self.log_pulse()
        self.log_session_summary()
        logging.info("Activity Monitor stopped.")

    # ---------------------------------------------------------------------------------------------
    # Stop method
    # ---------------------------------------------------------------------------------------------
    def stop(self):
        """
        Stops the activity monitor by setting the running flag to False.

        This method is used to halt the monitoring process, ensuring that
        the tracker is no longer active.
        """
        self.running = False
        update_status("Stopped")
        logging.info("Activity Monitor stopped.")
        self.db.close()
        logging.info("Database connection closed.")
        
        logging.info("Status file closed.")
        try:
            with open(STATUS_FILE, "a") as f:
                f.write("Stopped")
        except Exception as e:
            logging.error(f"Failed to close status file: {e}")
            
            
monitor = ActivityMonitor()

# =================================================================================================
# === Signal Handling ===
# =================================================================================================
def handle_exit(signum, frame):

    logging.info(f"Signal {signum} received. Shutting down...")
    monitor.stop()

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

if __name__ == "__main__":
    monitor.run()
