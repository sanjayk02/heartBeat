# -*- coding: utf-8 -*-
# inactivity_monitor.py - Logs user activity and inactivity
# Author: Sanja

import os
import sys
import time
import socket
import signal
import logging
import yaml
import getpass
from datetime import datetime, timedelta
import connect_to_db

# === Constants ===
BASE_DIR = os.path.join(os.environ.get("USERPROFILE", os.getcwd()), "InactivityDetector")
LOG_FILE = os.path.join(BASE_DIR, "inactivity_monitor.log")
STATUS_FILE = os.path.join(BASE_DIR, "status.txt")
DEFAULT_SETTINGS = {'timeout': 300, 'log_level': "DEBUG"}

# Ensure base directory exists
os.makedirs(BASE_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize log file with a message
try:
    with open(LOG_FILE, "w") as f:
        f.write("status")
    logging.info("Inactivity monitor log initialized.")
except Exception as e:
    logging.error(f"Failed to initialize log file: {e}")

# Path to config.yml (relative to project root)
script_path = os.path.dirname(os.path.abspath(__file__))
_root = os.path.abspath(os.path.join(script_path, ".."))
SETTINGS_FILE = os.path.join(_root, "config/config.yml").replace("\\", "/")


class InactivityMonitor:
    def __init__(self):
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_exit)
        logging.info("Signal handlers registered for graceful shutdown.")

        self.username   = os.getlogin() or getpass.getuser()
        self.hostname   = socket.gethostname()
        self.db         = self.connect_to_db()

        if self.db:
            logging.info("Database connection is active.")
        else:
            logging.warning("Database connection failed. Monitor will still run, but no data will be saved.")

        self.status_file = STATUS_FILE
        self.load_settings()

    def handle_exit(self, signum, frame):
        logging.info("Shutdown signal received. Exiting monitor...")
        sys.exit(0)

    def connect_to_db(self):
        try:
            db = connect_to_db.MongoDatabase()
            logging.info("Connected to MongoDB.")
            return db
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return None

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    user_settings = yaml.safe_load(f)
                    self.settings = {**DEFAULT_SETTINGS, **user_settings.get('settings', {})}
                    logging.info(f"Settings loaded: {self.settings}")
            except Exception as e:
                logging.error(f"Failed to load settings: {e}")
                self.settings = DEFAULT_SETTINGS
        else:
            self.settings = DEFAULT_SETTINGS

    def log_activity(self, status, duration):
        entry = {
            "username": self.username,
            "hostname": self.hostname,
            "timestamp": datetime.now(),
            "status": status,
            "active_time": round(duration, 2) if status == "Inactive" else 0,
            "inactive_time": round(duration, 2) if status == "Active" else 0
        }

        try:
            if self.db:
                self.db.insert_pulse(entry)
                logging.info(f"Logged {status} to database: {entry}")
            else:
                logging.warning("No DB connection available.")
        except Exception as e:
            logging.exception(f"Failed to log activity: {e}")

    def log_day_start_status(self, last_status, day_start_time):
        try:
            self.log_activity(last_status, 0)
            logging.info(f"Day start log: {last_status} at {datetime.fromtimestamp(day_start_time)}")
        except Exception as e:
            logging.exception("Failed to log day start status")

    def log_day_end_status(self, last_status, last_change_time, day_end_time):
        try:
            duration = day_end_time - last_change_time
            if duration > 0:
                self.log_activity(last_status, duration)
                logging.info(f"Day end log: {last_status} for {duration:.2f} sec at {datetime.fromtimestamp(day_end_time)}")

            day = datetime.fromtimestamp(day_end_time).date()
            start = datetime.combine(day, datetime.min.time())
            end = start + timedelta(days=1)

            result = self.db.activity_collection.aggregate([
                {"$match": {"timestamp": {"$gte": start, "$lt": end}}},
                {"$group": {
                    "_id": None,
                    "total_active_time": {"$sum": "$active_time"}
                }}
            ])

            total_active = round(next(result, {}).get("total_active_time", 0), 2)

            summary_entry = {
                "username": self.username,
                "hostname": self.hostname,
                "date": str(day),
                "status": "Summary",
                "total_active_time": total_active,
                "timestamp": datetime.now(),
                "type": "daily_summary"
            }

            self.db.insert_pulse(summary_entry)
            logging.info(f"Daily summary inserted for {day}: {total_active} seconds active")

            return day_end_time

        except Exception as e:
            logging.exception("Failed during day end logging or summary")
            return last_change_time

    def monitor(self):
        last_status = "Active"
        last_change_time = time.time()
        last_date = datetime.now().date()
        start_time = time.time()
        total_runtime = self.settings.get("total_runtime", 0)
        check_interval = self.settings.get("check_interval", 5)

        while True:
            try:
                if total_runtime > 0 and (time.time() - start_time) > total_runtime:
                    logging.info("Total runtime reached. Exiting monitor loop.")
                    break

                current_time = time.time()
                current_date = datetime.now().date()

                if current_date != last_date:
                    day_end = datetime.combine(last_date, datetime.max.time()).replace(microsecond=0)
                    last_change_time = self.log_day_end_status(last_status, last_change_time, day_end.timestamp())

                    day_start = datetime.combine(current_date, datetime.min.time())
                    self.log_day_start_status(last_status, day_start.timestamp())
                    last_date = current_date

                if os.path.exists(self.status_file):
                    with open(self.status_file, "r") as f:
                        status = f.read().strip()

                    if status != last_status:
                        duration = current_time - last_change_time
                        self.log_activity(status, duration)
                        logging.info(f"Status updated: {status}")

                        last_status = status
                        last_change_time = current_time
                else:
                    logging.warning("Status file not found.")

                time.sleep(check_interval)

            except Exception as e:
                logging.exception("Error in monitor loop")


# # Uncomment to run directly for testing
# if __name__ == "__main__":
#     monitor = InactivityMonitor()
#     monitor.monitor()
