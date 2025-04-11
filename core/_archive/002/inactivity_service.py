# -*- coding: utf-8 -*-
# Inactivity Detector Service
# Author: Sanja
# Date: 2025-03-01

import win32serviceutil
import win32service
import win32event
import servicemanager
import logging
import threading
import time
from datetime import datetime
import os
import win32security

from idle_reporter import IdleReporter
from event_detector import EventDetector

try:
    log_dir = "C:\\InactivityService"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        filename=os.path.join(log_dir, "service.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Logging initialized.")
except Exception as e:
    logging.error(f"Failed to initialize logging: {e}")


class InactivityService(win32serviceutil.ServiceFramework):
    _svc_name_ = "InactivityDetectorService"
    _svc_display_name_ = "Inactivity Detector Service"
    _svc_description_ = "Logs user activity and session state."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        self.reporter = IdleReporter()
        self.event_detector = EventDetector()
        self.last_event_signature = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ""))

        log_dir = "C:\\InactivityService"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logging.basicConfig(
            filename=os.path.join(log_dir, "service.log"),
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        logging.info("Inactivity Detector Service started.")

        monitor_thread = threading.Thread(target=self.reporter.monitor)
        monitor_thread.start()

        logout_thread = threading.Thread(target=self.monitor_user_sessions, daemon=True)
        logout_thread.start()

        event_thread = threading.Thread(target=self.log_events_loop, daemon=True)
        event_thread.start()

        while self.running:
            win32event.WaitForSingleObject(self.hWaitStop, 5000)

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
            base_dir = os.path.join("C:\\InactivityService", "users", username)
            status_file = os.path.join(base_dir, "status.txt")

            if not os.path.exists(base_dir):
                os.makedirs(base_dir)

            with open(status_file, 'w') as f:
                f.write(status.upper())

            logging.info(f"Wrote {status.upper()} for user {username} at {status_file}")

        except Exception as e:
            logging.error(f"Error setting status '{status}' for {username}: {e}")

    def log_events_loop(self):
        while self.running:
            try:
                event = self.event_detector.get_latest_user_event()
                # Skip system services like UMFD-*, DWM-*, etc.
                if event['username'].upper().startswith("UMFD-") or event['username'].upper().startswith("DWM-"):
                    continue
                if event:
                    sig = (event['event_type'], event['username'], event['timestamp'])
                    if sig != self.last_event_signature:
                        logging.info("Status updated: %s", event['event_type'])
                        self.set_user_status(event['username'], event['event_type'].upper())
                        self.last_event_signature = sig

                        try:
                            user_profile = os.path.join("C:\\Users", event['username'])
                            user_log_dir = os.path.join(user_profile, "InactivityDetector")
                            os.makedirs(user_log_dir, exist_ok=True)
                            user_log_path = os.path.join(user_log_dir, "idle_reporter.log")
                            with open(user_log_path, "a") as f:
                                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} - INFO - Status updated: {event['event_type'].capitalize()} \n")
                        except Exception as e:
                            logging.warning(f"Could not write per-user event log: {e}")

            except Exception as e:
                logging.error("Event logging error: %s", e)
            time.sleep(10)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(InactivityService)
