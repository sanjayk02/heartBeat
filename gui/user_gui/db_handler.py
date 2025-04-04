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
_root       = os.path.abspath(os.path.join(script_path, "..", "..", "..")) # Adjusted to point to the root of the project
sys.path.append(_root)

from core import connect_to_db


class GetPulseData:
    def __init__(self):
        self.client             = connect_to_db.MongoDatabase()
        self.pulse_logs_data    = self.client.get_logs()
        self.pulse_summary_data = self.client.get_summaries()

    @staticmethod
    def parse_time_to_seconds(value):
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                h, m, s = map(int, value.split(":"))
                return h * 3600 + m * 60 + s
            except Exception:
                return 0
        return 0

    def get_pulse_data(self, start_date: datetime = None, end_date: datetime = None):
        current_user = getpass.getuser()
        filtered_logs = []

        # Normalize dates to cover full days
        if start_date:
            start_date = datetime.combine(start_date.date(), datetime.min.time())
        if end_date:
            end_date = datetime.combine(end_date.date(), datetime.max.time())

        for log in self.pulse_logs_data:
            if log.get("username") != current_user:
                continue

            timestamp = log.get("timestamp")
            if not timestamp:
                continue

            # Filter by date (ignore time)
            if start_date and timestamp < start_date:
                continue
            if end_date and timestamp > end_date:
                continue

            active_seconds      = self.parse_time_to_seconds(log.get('active_time', 0))
            inactive_seconds    = self.parse_time_to_seconds(log.get('inactive_time', 0))

            log_data = {
                "username": log.get("username"),
                "hostname": log.get("hostname"),
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "status": log.get("status", ""),
                "active_time": str(timedelta(seconds=active_seconds)),
                "active_seconds": active_seconds,
                "inactive_time": str(timedelta(seconds=inactive_seconds)),
                "inactive_seconds": inactive_seconds
            }

            filtered_logs.append(log_data)

        return filtered_logs

    def get_summary_logs(self, start_date: datetime = None, end_date: datetime = None):
        current_user = getpass.getuser()
        filtered_summaries = []

        # Normalize dates
        if start_date:
            start_date = datetime.combine(start_date.date(), datetime.min.time())
        if end_date:
            end_date = datetime.combine(end_date.date(), datetime.max.time())

        for summary in self.pulse_summary_data:
            if summary.get("username") != current_user:
                continue

            timestamp = summary.get("timestamp")
            if not timestamp:
                continue

            if start_date and timestamp < start_date:
                continue
            if end_date and timestamp > end_date:
                continue

            log_data = {
                "username": summary.get("username"),
                "hostname": summary.get("hostname"),
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Summary",
                "active_time": summary.get("active_time", "00:00:00"),
                "inactive_time": summary.get("inactive_time", "00:00:00")
            }

            filtered_summaries.append(log_data)

        print(f"Filtered summaries: {filtered_summaries}")  # Debugging line
        # Sort summaries by timestamp
        return filtered_summaries


