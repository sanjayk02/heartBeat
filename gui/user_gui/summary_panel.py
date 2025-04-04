# db_handler.py

import yaml
from pymongo import MongoClient
from datetime import datetime
import os
import sys
import getpass
import logging
from typing import List, Dict
from datetime import timedelta
import getpass

# === Paths ===
script_path = os.path.abspath(__file__)
_root       = os.path.abspath(os.path.join(script_path, "..", "..", ".."))
sys.path.append(_root)

_holidays_path = os.path.join(_root, "config/holidaysList.yml")
if not os.path.exists(_holidays_path):
    raise FileNotFoundError(f"Holidays file not found at {_holidays_path}")

from core import connect_to_db

# === Logging === 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === Constants ===
def load_config():
    try:
        if os.path.exists(_holidays_path):
            with open(_holidays_path, 'r') as f:
                cfg = yaml.safe_load(f) or {}
                current_month = datetime.now().strftime("%B")

                # Safely get holidays for the current month
                holidays = cfg.get(current_month, [])
                return holidays  # Return list of holidays this month

    except Exception as e:
        logging.error(f"[CONFIG] Failed to load holiday config: {e}")

    return []

# =====================================================================================
# SummaryPanel Class
# =====================================================================================
class SummaryPanel:
    
    def __init__(self):
        
        self.client             = connect_to_db.MongoDatabase()
        self.pulse_logs_data    = self.client.get_logs()
        self.pulse_summary_data = self.client.get_summaries()

    # -------------------------------------------------------------------------
    # get number_of_holidays in the month
    # -------------------------------------------------------------------------
    def get_number_of_holidays(self) -> int:
        """
        Returns the number of sessions in the pulse summary data.
        """
        
        self.holidays_in_month  = load_config()
        return len(self.holidays_in_month) 

    # -------------------------------------------------------------------------
    # get total Active time in this month
    # -------------------------------------------------------------------------
    def get_total_active_time(self) -> timedelta:
        """
        Returns the total active time in this month from pulse_summary_data.
        Parses string durations into timedelta objects if needed.
        """
        total_active_time = timedelta(0)

        for summary in self.pulse_logs_data:
            active_time = summary.get('active_time')
            
            if isinstance(active_time, timedelta):
                total_active_time += active_time
            elif isinstance(active_time, str):
                try:
                    # Example format: "2:30:00" => 2h 30m
                    (h, m, s) = map(int, active_time.split(":"))
                    total_active_time += timedelta(hours=h, minutes=m, seconds=s)
                except Exception as e:
                    logging.warning(f"Could not parse active_time '{active_time}': {e}")
            else:
                logging.warning(f"Ignored invalid active_time type: {type(active_time)}")

        return total_active_time

    # -------------------------------------------------------------------------
    # get total Inactive time in this month
    # -------------------------------------------------------------------------
    def get_total_inactive_time(self) -> timedelta:
        """
        Returns the total inactive time in this month from pulse_summary_data.
        Parses string durations into timedelta objects if needed.
        """
        total_inactive_time = timedelta(0)

        for summary in self.pulse_logs_data:
            inactive_time = summary.get('inactive_time')
            
            if isinstance(inactive_time, timedelta):
                total_inactive_time += inactive_time
            elif isinstance(inactive_time, str):
                try:
                    # Example format: "2:30:00" => 2h 30m
                    (h, m, s) = map(int, inactive_time.split(":"))
                    total_inactive_time += timedelta(hours=h, minutes=m, seconds=s)
                except Exception as e:
                    logging.warning(f"Could not parse inactive_time '{inactive_time}': {e}")
            else:
                logging.warning(f"Ignored invalid inactive_time type: {type(inactive_time)}")

        return total_inactive_time
    
    # -------------------------------------------------------------------------
    # get total active time off today in this month
    # -------------------------------------------------------------------------
    def get_total_active_time_off_today(self) -> timedelta:
        """
        first check today day  and get data from pulse_summary_data today
        and then return the total active time off today.
        Parses string durations into timedelta objects if needed.
        
        """
        today = datetime.now().strftime("%Y-%m-%d")
        total_active_time_today = timedelta(0)
        
        for summary in self.pulse_logs_data:
            
            timeStamp = (summary.get('timestamp'))
            if isinstance(timeStamp, datetime):
                timeStamp = timeStamp.strftime("%Y-%m-%d")
                
                if timeStamp == today:
                    active_time = summary.get('active_time')
                    
                    if isinstance(active_time, timedelta):
                        total_active_time_today += active_time
                    elif isinstance(active_time, str):
                        try:
                            # Example format: "2:30:00" => 2h 30m
                            (h, m, s) = map(int, active_time.split(":"))
                            total_active_time_today += timedelta(hours=h, minutes=m, seconds=s)
                            
                        except Exception as e:
                            logging.warning(f"Could not parse active_time '{active_time}': {e}")
                    else:
                        logging.warning(f"Ignored invalid active_time type: {type(active_time)}")
            else:
                logging.warning(f"Ignored invalid timestamp type: {type(timeStamp)}")
                        
        return total_active_time_today

    # -------------------------------------------------------------------------
    # get total inactive time off today in this month
    # -------------------------------------------------------------------------
    def get_total_inactive_time_off_today(self) -> timedelta:
        """
        first check today day  and get data from pulse_summary_data today
        and then return the total inactive time off today.
        Parses string durations into timedelta objects if needed.
        
        """
        today = datetime.now().strftime("%Y-%m-%d")
        total_inactive_time_today = timedelta(0)
        
        for summary in self.pulse_logs_data:
            
            timeStamp = (summary.get('timestamp'))
            if isinstance(timeStamp, datetime):
                timeStamp = timeStamp.strftime("%Y-%m-%d")
                
                if timeStamp == today:
                    inactive_time = summary.get('inactive_time')
                    
                    if isinstance(inactive_time, timedelta):
                        total_inactive_time_today += inactive_time
                    elif isinstance(inactive_time, str):
                        try:
                            # Example format: "2:30:00" => 2h 30m
                            (h, m, s) = map(int, inactive_time.split(":"))
                            total_inactive_time_today += timedelta(hours=h, minutes=m, seconds=s)
                            
                        except Exception as e:
                            logging.warning(f"Could not parse inactive_time '{inactive_time}': {e}")
                    else:
                        logging.warning(f"Ignored invalid inactive_time type: {type(inactive_time)}")
            else:
                logging.warning(f"Ignored invalid timestamp type: {type(timeStamp)}")
                        
        return total_inactive_time_today
    
    
# SP = SummaryPanel()
# hd = SP.get_number_of_holidays()
# print(f"Number of holidays this month: {hd}")
# print(f"Total active time this month: {SP.get_total_active_time()}")
# print(f"Total inactive time this month: {SP.get_total_inactive_time()}")
# print(f"Total active time off today this month: {SP.get_total_active_time_off_today()}")
# print(f"Total Inactive time off today this month: {SP.get_total_inactive_time_off_today()}")
