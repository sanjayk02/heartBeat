# -*- coding: utf-8 -*-
# author: Sanja
# date: 2025-03-01

# Heart Beat Application - Inactivity Monitor
# This script monitors user inactivity and logs the status to a MongoDB database.
# It reads the user's activity status from a file and logs the duration of active/inactive periods.
# The script also handles daily summaries and logs the status at the start and end of each day.
# The script is designed to run continuously, checking the status file at regular intervals.
# It uses the `connect_to_db` module to handle database connections and operations.
# The script is intended to be run as a standalone application.
# The script is part of the Heart Beat Application, which is designed to monitor user activity and inactivity.
# The application is intended for use in environments where user activity needs to be monitored for security or productivity reasons.
# The script is designed to be run on Windows operating systems, as indicated by the use of `os.getlogin()` and `os.environ["USERPROFILE"]`.
# The script is written in Python and uses the `logging` module for logging messages to a file.
# The script uses the `yaml` module to load user-defined settings from a YAML file.
# The script uses the `datetime` module to handle date and time operations.
# The script uses the `socket` module to get the hostname of the machine where it is running.
# The script uses the `os` module to handle file and directory operations.

import os
import time
import socket
import logging
from datetime import datetime
import connect_to_db
import yaml

BASE_DIR        = os.path.join(os.environ["USERPROFILE"], "InactivityDetector")
LOG_FILE        = os.path.join(BASE_DIR, "inactivity_monitor.log")

script_path     = os.path.dirname(os.path.abspath(__file__))
_root           = os.path.abspath(os.path.join(script_path, ".."))
SETTINGS_FILE   = os.path.join(_root, "config/config.yml").replace("\\", "/")


os.makedirs(BASE_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# =================================================================================================================
# Main InactivityMonitor class
# =================================================================================================================
class InactivityMonitor:
    """Monitors inactivity and logs to MongoDB."""
    # -------------------------------------------------------------------------------------------------------------
    #  # Define class variables here if needed
    # -------------------------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Initializes the InactivityMonitor class.

        This constructor sets up the necessary attributes for the inactivity monitor,
        including the username, hostname, database connection, status file path, 
        and loads the application settings.

        Attributes:
            username (str): The username of the currently logged-in user.
            hostname (str): The hostname of the machine where the code is running.
            db: The database connection object.
            status_file (str): The file path to the status file.
        """
        self.username       = os.getlogin()
        self.hostname       = socket.gethostname()
        self.db             = self.connect_to_db()
        self.status_file    = os.path.join(BASE_DIR, "status.txt")
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

    # -------------------------------------------------------------------------------------------------------------
    # connect_to_db
    # -------------------------------------------------------------------------------------------------------------
    def connect_to_db(self):
        """
        Establish a connection to the MongoDB database.

        This method attempts to create a connection to the MongoDB database
        using the `MongoDatabase` class. If the connection is successful, 
        it logs a success message and returns the database object. If the 
        connection fails, it logs an error message and returns `None`.

        Returns:
            MongoDatabase: An instance of the connected MongoDB database if successful.
            None: If the connection to the database fails.
        """
        """Connect to MongoDB."""
        try:
            db = connect_to_db.MongoDatabase()
            logging.info("Connected to MongoDB.")
            return db
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return None

    # -------------------------------------------------------------------------------------------------------------
    # log_activity
    # -------------------------------------------------------------------------------------------------------------
    def log_activity(self, status, duration):
        """
        Logs the user's activity status to a MongoDB database.
        Args:
            status (str): The activity status, either "Active" or "Inactive".
            duration (float): The duration of the activity in seconds.
        The method creates a log entry containing the username, hostname, 
        timestamp, activity status, and the duration of active or inactive time. 
        If the database connection is available, the entry is inserted into the 
        database. Otherwise, a warning is logged. In case of an error during 
        the logging process, an exception is logged.
        Raises:
            Exception: If an error occurs while inserting the log entry into the database.
        """
        """Log activity status to MongoDB."""
        entry = {
            "username"      : self.username,
            "hostname"      : self.hostname,
            "timestamp"     : datetime.now(),
            "status"        : status,
            "active_time"   : round(duration, 2) if status == "Inactive" else 0,
            "inactive_time" : round(duration, 2) if status == "Active" else 0
        }

        try:
            if self.db:
                self.db.insert_pulse(entry)
                logging.info(f"Logged {status} to database: {entry}")
            else:
                logging.warning("No DB connection available.")
        except Exception as e:
            logging.exception(f"Failed to log activity: {e}")

    # -------------------------------------------------------------------------------------------------------------
    # log_day_start_status
    # -------------------------------------------------------------------------------------------------------------
    def log_day_start_status(self, last_status, day_start_time):
        """
        Log a status snapshot at the beginning of a new day (00:00:00).
        
        Args:
            last_status (str): Current status at day start.
            day_start_time (float): Timestamp of midnight.
        """
        try:
            self.log_activity(last_status, 0)  # Zero duration snapshot
            logging.info(f"Day start log: {last_status} at {datetime.fromtimestamp(day_start_time)}")
        except Exception as e:
            logging.exception("Failed to log day start status")

    # -------------------------------------------------------------------------------------------------------------
    # log_day_end_status
    # -------------------------------------------------------------------------------------------------------------
    def log_day_end_status(self, last_status, last_change_time, day_end_time):
        """
        1. Log the final status duration up to 23:59:59.
        2. Calculate and insert daily active time summary into the DB.
        
        Args:
            last_status (str): Last known status ("Active"/"Inactive")
            last_change_time (float): Timestamp when status last changed
            day_end_time (float): Timestamp for 23:59:59 of the current day
            
        Returns:
            float: New last_change_time (at 23:59:59)
        """
        try:
            # 1. Log status duration from last change to end of day
            duration = day_end_time - last_change_time
            if duration > 0:
                self.log_activity(last_status, duration)
                logging.info(f"Day end log: {last_status} for {duration:.2f} sec at {datetime.fromtimestamp(day_end_time)}")

            # 2. Calculate and insert daily summary
            day     = datetime.fromtimestamp(day_end_time).date()
            start   = datetime.combine(day, datetime.min.time())
            end     = start + timedelta(days=1)

            result = self.db.collection.aggregate([
                {"$match": {
                    "timestamp": {"$gte": start, "$lt": end}
                }},
                {"$group": {
                    "_id": None,
                    "total_active_time": {"$sum": "$active_time"}
                }}
            ])

            total_active = round(next(result, {}).get("total_active_time", 0), 2)

            summary_entry = {
                "username"          : self.username,
                "hostname"          : self.hostname,
                "date"              : str(day),
                "status"            : "Summary",
                "total_active_time" : total_active,
                "timestamp"         : datetime.now(),
                "type"              : "daily_summary"
            }

            self.db.insert_pulse(summary_entry)
            logging.info(f"Daily summary inserted for {day}: {total_active} seconds active")

            return day_end_time  # Reset last_change_time

        except Exception as e:
            logging.exception("Failed during day end logging or summary")
            return last_change_time

    # -------------------------------------------------------------------------------------------------------------
    # monitor
    # -------------------------------------------------------------------------------------------------------------
    def monitor(self):
        """
        Monitors inactivity by periodically checking the status from a file, logging status transitions,
        and generating daily summaries. The monitoring process includes handling day rollovers and 
        ensuring proper logging of activity durations.
        The method operates in a loop, checking the status file at regular intervals, and exits 
        when the specified total runtime is exceeded (if configured).
        Attributes:
            last_status (str): Tracks the last known status (e.g., "Active").
            last_change_time (float): Timestamp of the last status change.
            last_date (datetime.date): Tracks the last processed date for day rollover handling.
            start_time (float): Timestamp when the monitoring started.
            total_runtime (int): Maximum runtime for the monitor in seconds (0 for unlimited).
            check_interval (int): Interval in seconds between status checks.
        Behavior:
            - Reads the status from a file (`self.status_file`) and logs transitions.
            - Handles day rollovers by logging end-of-day and start-of-day statuses.
            - Logs warnings if the status file is not found.
            - Catches and logs exceptions during the monitoring process.
        Raises:
            Exception: Logs any unexpected errors encountered during the monitoring loop.
        """
        """Monitor inactivity based on status.txt, log transitions and daily summary."""
        last_status         = "Active"
        last_change_time    = time.time()
        last_date           = datetime.now().date()
        start_time          = time.time()
        total_runtime       = self.settings.get("total_runtime", 0)
        check_interval      = self.settings.get("check_interval", 5)

        while True:
            try:
                # Exit if total_runtime is > 0 and time's up
                if total_runtime > 0 and (time.time() - start_time) > total_runtime:
                    logging.info("Total runtime reached. Exiting monitor loop.")
                    break

                current_time = time.time()
                current_date = datetime.now().date()

                # Day rollover logic
                if current_date != last_date:
                    day_end = datetime.combine(last_date, datetime.max.time()).replace(microsecond=0)
                    last_change_time = self.log_day_end_status(last_status, last_change_time, day_end.timestamp())

                    day_start = datetime.combine(current_date, datetime.min.time())
                    self.log_day_start_status(last_status, day_start.timestamp())
                    last_date = current_date

                # Status file read
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

            
# ==============================================================================================================
# Main function to run the InactivityMonitor
# ==============================================================================================================            
if __name__ == "__main__":
    monitor = InactivityMonitor()
    monitor.monitor()