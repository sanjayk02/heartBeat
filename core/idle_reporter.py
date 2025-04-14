# -*- coding: utf-8 -*-
# author: Sanja
# date: 2025-03-01

# Heart Beat Application - Idle Reporter
# Patched to route 'Logoff (session end)' to service.log only.

import os
import time
import ctypes
import logging
import yaml
import sys

script_path     = os.path.dirname(os.path.abspath(__file__))
_root           = os.path.abspath(os.path.join(script_path, ".."))
SETTINGS_FILE   = os.path.join(_root, "config/config.yml").replace("\\", "/")

# --- Patched Logging Handler ---
def log_status_update(status: str):
    base_dir = os.path.join(os.environ["USERPROFILE"], "InactivityDetector")
    service_log = os.path.join(base_dir, "service.log")
    idle_log = os.path.join(base_dir, "idle_reporter.log")

    main_logger = logging.getLogger("main_logger")
    service_logger = logging.getLogger("service_logger")

    if not main_logger.handlers:
        main_handler = logging.FileHandler(idle_log)
        main_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        main_logger.addHandler(main_handler)
        main_logger.setLevel(logging.INFO)

    if not service_logger.handlers:
        service_handler = logging.FileHandler(service_log)
        service_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        service_logger.addHandler(service_handler)
        service_logger.setLevel(logging.INFO)

    if status == "Logoff (session end)":
        service_logger.info(f"Status updated: {status}")
    else:
        main_logger.info(f"Status updated: {status}")

class IdleReporter:
    """Detects user inactivity and logs it."""

    def __init__(self):
        self.base_dir = os.path.join(os.environ["USERPROFILE"], "InactivityDetector")
        self.status_file = os.path.join(self.base_dir, "status.txt")
        self.log_file = os.path.join(self.base_dir, "idle_reporter.log")

        os.makedirs(self.base_dir, exist_ok=True)

        self.ensure_status_file()
        self.load_settings()

    def load_settings(self):
        default_settings = {'timeout': 60, 'log_level': "DEBUG"}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    user_settings = yaml.safe_load(f)
                    self.settings = {**default_settings, **user_settings.get('settings', {})}
                    log_status_update(f"Settings loaded: {self.settings}")
            except Exception as e:
                log_status_update(f"Failed to load settings: {e}")
                self.settings = default_settings

    def get_idle_duration(self):
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

        li = LASTINPUTINFO()
        li.cbSize = ctypes.sizeof(li)

        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(li)):
            millis = ctypes.windll.kernel32.GetTickCount() - li.dwTime
            return millis / 1000.0
        return 0

    def ensure_status_file(self):
        if not os.path.exists(self.status_file):
            with open(self.status_file, "w") as f:
                f.write("Active")
            log_status_update("Created status.txt and initialized with Active.")

    def write_status(self, status):
        self.ensure_status_file()
        try:
            with open(self.status_file, "w") as f:
                f.write(status)
            log_status_update(status)
        except Exception as e:
            log_status_update(f"Failed to write status: {e}")

    def monitor(self):
        idle_threshold = self.settings.get('timeout', 300)
        check_interval = self.settings.get('check_interval', 10)

        log_status_update(f"Idle threshold set to {idle_threshold} seconds.")
        log_status_update(f"Check interval set to {check_interval} seconds.")
        log_status_update("Idle Reporter Started.")

        last_status = "Active"

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
