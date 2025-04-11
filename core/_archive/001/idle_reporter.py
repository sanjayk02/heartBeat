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
import yaml
import sys


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
        self.load_settings()
    # -------------------------------------------------------------------------------------------------------------
    # # load_settings 
    # -------------------------------------------------------------------------------------------------------------
    def load_settings(self):
        """
        Load application settings from a YAML file.

        This method attempts to load user-defined settings from a YAML file
        specified by the `SETTINGS_FILE` constant. If the file exists and is
        successfully read, the user-defined settings are merged with the default
        settings. If the file does not exist or an error occurs during loading,
        the default settings are used.

        Default settings:
            - timeout: 60 (seconds)
            - log_level: "DEBUG"

        Exceptions during file reading or parsing are logged as errors.

        Attributes:
            self.settings (dict): A dictionary containing the merged settings.
        """
        """Load settings from YAML file."""
        default_settings = {'timeout': 60, 'log_level': "DEBUG"}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    user_settings = yaml.safe_load(f)
                    self.settings = {**default_settings, **user_settings.get('settings', {})}
                    logging.info(f"Settings loaded: {self.settings}")
                    
            except Exception as e:
                logging.error(f"Failed to load settings: {e}")
                self.settings = default_settings

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

    def monitor(self):
        """Continuously monitors idle time and logs status."""
        
        idle_threshold = self.settings.get('timeout', 300)  # Default to 5 minutes
        check_interval = self.settings.get('check_interval', 10)
        
        logging.info(f"Idle threshold set to {idle_threshold} seconds.")
        logging.info(f"Check interval set to {check_interval} seconds.")
              
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
