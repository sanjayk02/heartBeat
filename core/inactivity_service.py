# -*- coding: utf-8 -*-
# Inactivity Detector Service (NSSM-compatible)
# Author: Sanja
# Refactored: 2025-04-17

import logging
import threading
import time
from datetime import datetime
import os
import sys

from idle_reporter import IdleReporter
from event_detector import EventDetector
from connect_to_db import MongoDatabase

# Setup logging
log_dir = "C:\\Users\\Public\\InactivityService"
os.makedirs(log_dir, exist_ok=True)
service_log_path = os.path.join(log_dir, "service.log")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
while logger.hasHandlers():
    logger.removeHandler(logger.handlers[0])
file_handler = logging.FileHandler(service_log_path)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logging.info("[STARTUP] Inactivity Detector Service initialized.")


class InactivityService:
    def __init__(self):
        self.running = True
        self.reporter = IdleReporter()
        self.event_detector = EventDetector()
        self.db = MongoDatabase()
        self.last_event_signature = None
        self.blocker = threading.Event()

    def run(self):
        logging.info("Inactivity Detector Service started (NSSM mode).")
        logging.info(f"Args passed: {sys.argv}")

        threading.Thread(target=self.reporter.monitor, daemon=True).start()
        threading.Thread(target=self.monitor_user_sessions, daemon=True).start()
        threading.Thread(target=self.log_events_loop, daemon=True).start()

        try:
            self.blocker.wait()  # Keep main thread alive
        except KeyboardInterrupt:
            logging.info("[SHUTDOWN] Service interrupted by user (Ctrl+C).")
        except Exception as e:
            logging.exception("[ERROR] Unexpected error in main loop: %s", e)

    def monitor_user_sessions(self):
        try:
            import win32ts
        except ImportError:
            logging.error("win32ts module not found. Make sure pywin32 is installed.")
            return

        user_session_states = {}

        while self.running:
            try:
                sessions = win32ts.WTSEnumerateSessions(None, 1, 0)

                for session_id, _, _ in sessions:
                    try:
                        username = win32ts.WTSQuerySessionInformation(None, session_id, win32ts.WTSUserName)
                        state = win32ts.WTSQuerySessionInformation(None, session_id, win32ts.WTSConnectState)

                        if not username:
                            continue

                        prev_state = user_session_states.get(username)

                        if prev_state == win32ts.WTSActive and state == win32ts.WTSDisconnected:
                            self.set_user_status(username, "OFFLINE")
                        if prev_state == win32ts.WTSActive and state == win32ts.WTSLocked:
                            self.set_user_status(username, "LOCKED")

                        user_session_states[username] = state

                    except Exception:
                        pass

                time.sleep(10)

            except Exception as e:
                logging.exception("Error while monitoring session states")

    def set_user_status(self, username, status):
        try:
            base_dir = os.path.join("C:\\Users\\Public\\InactivityService", "users", username)
            os.makedirs(base_dir, exist_ok=True)
            status_file = os.path.join(base_dir, "status.txt")

            with open(status_file, 'w') as f:
                f.write(status.upper())

            logging.info(f"User {username} status set to {status.upper()}.")

        except Exception as e:
            logging.error(f"Error setting status '{status}' for {username}: {e}")

    def log_events_loop(self):
        while self.running:
            try:
                events = self.event_detector.get_latest_user_events(count=1)
                event = events[0] if events else None

                if not event:
                    continue

                if event['username'].upper().startswith("UMFD-") or event['username'].upper().startswith("DWM-"):
                    continue

                sig = (event['event_type'], event['username'], event['timestamp'])
                if sig != self.last_event_signature:
                    logging.info("Status updated: %s", event['event_type'])

                    self.set_user_status(event['username'], event['event_type'].upper())
                    self.last_event_signature = sig

                    try:
                        entry = {
                            "username": event['username'],
                            "hostname": event['hostname'],
                            "event_type": event['event_type'].upper(),
                            "timestamp": datetime.now(),
                            "source": "event_detector"
                        }
                        self.db.insert_pulse(entry)
                        logging.info("Event pushed to DB.")
                    except Exception as db_err:
                        logging.warning(f"DB write failed: {db_err}")

                    try:
                        user_profile = os.path.join("C:\\Users", event['username'])
                        user_log_dir = os.path.join(user_profile, "InactivityDetector")
                        os.makedirs(user_log_dir, exist_ok=True)
                        user_log_path = os.path.join(user_log_dir, "idle_reporter.log")

                        with open(user_log_path, "a") as f:
                            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} - INFO - Status updated: {event['event_type'].capitalize()}\n")

                    except Exception as e:
                        logging.warning(f"Could not write per-user event log: {e}")

            except Exception as e:
                logging.error("Event logging error: %s", e)

            time.sleep(10)


if __name__ == '__main__':
    service = InactivityService()
    service.run()
