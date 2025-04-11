# -*- coding: utf-8 -*-
# author: Sanja
# date: 2025-03-01

# Heart Beat Application - Idle Reporter
# This script monitors user inactivity and logs the status to a file.
# It uses the ctypes library to access Windows API functions to get the last input time.
# The script creates a directory in the user's profile to store the status file and logs.
# It continuously checks the idle time and updates the status file accordingly.

import os
import time
import ctypes
import logging

script_path     = os.path.dirname(os.path.abspath(__file__))
_root           = os.path.abspath(os.path.join(script_path, ".."))
SETTINGS_FILE   = os.path.join(_root, "config/config.yml").replace("\\", "/")

class IdleReporter:
    """Detects user inactivity and logs it."""

    def __init__(self):
        """Initialize paths, logging, and ensure necessary files exist."""
        self.base_dir = os.path.join(os.environ["USERPROFILE"], "InactivityDetector")
        self.status_file = os.path.join(self.base_dir, "status.txt")
        self.log_file = os.path.join(self.base_dir, "idle_reporter.log")

        os.makedirs(self.base_dir, exist_ok=True)

        logging.basicConfig(
            filename=self.log_file,
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        self.ensure_status_file()

    def get_idle_duration(self):
        """Get the duration in seconds since the last user input."""
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

        li = LASTINPUTINFO()
        li.cbSize = ctypes.sizeof(li)

        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(li)):
            millis = ctypes.windll.kernel32.GetTickCount() - li.dwTime
            return millis / 1000.0  # Convert to seconds
        return 0

    def ensure_status_file(self):
        """Ensure status.txt exists before writing."""
        if not os.path.exists(self.status_file):
            with open(self.status_file, "w") as f:
                f.write("Active")  # Default to Active
            logging.info("Created status.txt and initialized with Active.")

    def write_status(self, status):
        """Write activity status to status.txt."""
        self.ensure_status_file()
        try:
            with open(self.status_file, "w") as f:
                f.write(status)
            logging.info(f"Status updated: {status}")
        except Exception as e:
            logging.error(f"Failed to write status: {e}")

    def monitor(self, idle_threshold=300, check_interval=10):
        """Continuously monitors idle time and logs status."""
        last_status = "Active"
        logging.info("Idle Reporter Started.")

        while True:
            idle_time = self.get_idle_duration()
            status = "Inactive" if idle_time > idle_threshold else "Active"

            if status != last_status:
                self.write_status(status)
                last_status = status

            time.sleep(check_interval)

if __name__ == "__main__":
    reporter = IdleReporter()
    reporter.monitor()
