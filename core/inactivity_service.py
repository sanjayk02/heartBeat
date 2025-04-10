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
import os

from idle_reporter import IdleReporter\
    
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
    """Windows service that runs IdleReporter and monitors user sessions."""

    _svc_name_          = "InactivityDetectorService"
    _svc_display_name_  = "Inactivity Detector Service"
    _svc_description_   = "Logs user activity and session state."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop  = win32event.CreateEvent(None, 0, 0, None)
        self.running    = True
        self.reporter   = IdleReporter()

    def SvcStop(self):
        """Handle service stop request."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """Main service execution loop."""
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ""))

        # Ensure log directory exists
        log_dir = "C:\\InactivityService"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logging.basicConfig(
            filename=os.path.join(log_dir, "service.log"),
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        logging.info("Inactivity Detector Service started.")

        # Start IdleReporter monitoring
        monitor_thread = threading.Thread(target=self.reporter.monitor)
        monitor_thread.start()

        # Start session watcher
        logout_thread = threading.Thread(target=self.monitor_user_sessions, daemon=True)
        logout_thread.start()

        while self.running:
            win32event.WaitForSingleObject(self.hWaitStop, 5000)

    def monitor_user_sessions(self):
        """Monitor user sessions and update status.txt on LOCK or LOGOUT."""
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

                        # Detect logout (was active, now disconnected)
                        if prev_state == win32ts.WTSActive and state == win32ts.WTSDisconnected:
                            self.set_user_status(username, "OFFLINE")

                        # Detect screen lock (was active, now locked)
                        if prev_state == win32ts.WTSActive and state == win32ts.WTSLocked:
                            self.set_user_status(username, "LOCKED")

                        user_session_states[username] = state

                    except Exception:
                        pass  # Some sessions may fail to query

                time.sleep(10)

            except Exception as e:
                logging.exception("Error while monitoring session states")

    def set_user_status(self, username, status):
        """Write status string to status.txt under global folder."""
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



if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(InactivityService)
