# -*- coding: utf-8 -*-
# run_monitor.py - Extended with EventDetector integration
# Author: Sanja
# Project: PulseWork
# Updated: 2025-04-11

import logging
import signal
import sys
import os
import getpass
import time
from datetime import datetime
from inactivity_monitor import InactivityMonitor
from event_detector import EventDetector

class RunMonitor:
    def __init__(self):
        self.monitor = InactivityMonitor()
        self.event_detector = EventDetector()
        self.username = getpass.getuser()
        self.user_dir = os.path.join(os.environ.get("USERPROFILE", os.getcwd()), "InactivityDetector")
        os.makedirs(self.user_dir, exist_ok=True)

        self.status_file = os.path.join(self.user_dir, "status.txt")
        self.log_file = os.path.join(self.user_dir, "idle_reporter.log")
        self.last_event_signature = None  # For deduplication

        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        self.fix_crashed_status()

        # Signal handlers
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

        if sys.platform == "win32":
            try:
                import win32api
                win32api.SetConsoleCtrlHandler(lambda event: self.handle_exit(None, None), True)
            except Exception as e:
                logging.warning("win32api handler not attached: %s", e)

        logging.info("[RUN_MONITOR] Initialized for user: %s", self.username)

    def fix_crashed_status(self):
        if os.path.exists(self.status_file):
            with open(self.status_file, "r") as f:
                last_status = f.read().strip()
            if last_status in ["ACTIVE", "IDLE"]:
                self.update_status("OFFLINE", source="reboot-corrector")

    def update_status(self, status, source="run_monitor"):
        with open(self.status_file, "w") as f:
            f.write(status.upper())
        logging.info("Status updated: %s (%s)", status.capitalize(), source)

    def handle_exit(self, signum, frame):
        self.update_status("OFFLINE", source="shutdown")
        logging.info("RunMonitor received shutdown signal (%s). Exiting.", signum)
        sys.exit(0)

    def log_event_if_new(self):
        event = self.event_detector.get_latest_user_event()
        if event:
            event_signature = (event['event_type'], event['username'], event['timestamp'])
            if event_signature != self.last_event_signature:
                logging.info("[EVENT_DETECTOR] %s by %s on %s at %s", 
                             event['event_type'], event['username'], event['hostname'], event['timestamp'])
                self.last_event_signature = event_signature

    def start_monitoring(self):
        logging.info("[RUN_MONITOR] Starting InactivityMonitor...")
        self.monitor.monitor()  # handles IDLE/ACTIVE monitoring


if __name__ == "__main__":
    runner = RunMonitor()
    runner.start_monitoring()
    logging.info("[RUN_MONITOR] Monitoring started.")

    try:
        while True:
            time.sleep(60)  # Idle check interval
            runner.log_event_if_new()
    except KeyboardInterrupt:
        runner.handle_exit(None, None)
    except Exception as e:
        logging.error("Unexpected error: %s", e)
        runner.handle_exit(None, None)
