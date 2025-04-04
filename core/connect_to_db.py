import os
import sys
import yaml
import logging
from pymongo import MongoClient, errors
from datetime import datetime
from datetime import timedelta
import getpass
# === Paths ===
script_path = os.path.dirname(os.path.abspath(__file__))
_root       = os.path.abspath(os.path.join(script_path, ".."))  # Adjusted to point to the root of the project
_get_config = os.path.join(_root, "config/config.yml").replace("\\", "/")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MongoDatabase:
    def __init__(self):
        """Initializes MongoDB connection using a YAML configuration file."""
        self.config_file            = _get_config
        self.client                 = None
        self.db_name                = None
        self.db                     = None
        self.activity_collection    = None
        self.summary_collection     = None
        self.username               = getpass.getuser()  # Get current logged-in user

        self.load_config()
        self.connect()

    def load_config(self):
        """Loads MongoDB credentials from the YAML file."""
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_path, self.config_file)

            with open(config_path, "r") as file:
                config = yaml.safe_load(file)

            self.host       = config["mongodb"]["host"]
            self.port       = config["mongodb"]["port"]
            self.username   = config["mongodb"].get("username")
            self.password   = config["mongodb"].get("password")
            self.auth_db    = config["mongodb"]["auth_db"]
            self.db_name    = config["mongodb"]["db_name"]

            logging.info("Configuration loaded successfully.")

        except FileNotFoundError:
            raise RuntimeError("Configuration file not found. Ensure 'config.yml' exists.")
        except KeyError as e:
            raise RuntimeError(f"Missing key in config file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading YAML configuration: {e}")

    def connect(self):
        """Connects to MongoDB using the loaded configuration."""
        try:
            if self.username and self.password:
                uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.auth_db}"
            else:
                uri = f"mongodb://{self.host}:{self.port}/{self.auth_db}"

            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")  # Test connection

            self.db = self.client[self.db_name]
            self.activity_collection = self.db["activity_pulse"]
            self.summary_collection = self.db["session_summaries"]

            logging.info(f"Connected to MongoDB successfully. Database: {self.db_name}")

        except errors.ServerSelectionTimeoutError:
            raise RuntimeError("MongoDB connection timeout! Please check your connection.")
        except Exception as e:
            raise RuntimeError(f"Error connecting to MongoDB: {e}")

    def insert_pulse(self, data):
        """Inserts a log entry into the MongoDB collection."""
        try:
            self.activity_collection.insert_one(data)
            logging.info("Log inserted successfully.")
        except Exception as e:
            logging.error(f"Database Error (insert_pulse): {e}")

    def insert_summary(self, data):
        """Inserts a session summary into the MongoDB collection."""
        try:
            self.summary_collection.insert_one(data)
            logging.info("Summary inserted successfully.")
        except Exception as e:
            logging.error(f"Database Error (summary_collections): {e}")

    def get_logs(self, query=None):
        """
        Fetch logs from 'activity_logs' collection based on an optional query.
        Args:
            query (dict, optional): MongoDB query filter. Defaults to {}.
        Returns:
            list: A list of log documents.
        """
        if query is None:
            query = {}

        # Fetch data from 'activity_logs' collection
        logs = list(self.activity_collection.find(query))

        # Convert BSON datetime to Python datetime if necessary
        for log in logs:
            if 'timestamp' in log and not isinstance(log['timestamp'], datetime):
                log['timestamp'] = log['timestamp'].to_datetime()

        return logs

    def get_summaries(self, query=None):
        """
        Fetch session summaries from 'session_summaries' collection based on an optional query.
        Args:
            query (dict, optional): MongoDB query filter. Defaults to {}.
        Returns:
            list: A list of summary documents.
        """
        if query is None:
            query = {}

        # Fetch data from 'session_summaries' collection
        summaries = list(self.summary_collection.find(query))

        # Convert BSON datetime to Python datetime if necessary
        for summary in summaries:
            if 'start_time' in summary and not isinstance(summary['start_time'], datetime):
                summary['start_time'] = summary['start_time'].to_datetime()
            if 'end_time' in summary and not isinstance(summary['end_time'], datetime):
                summary['end_time'] = summary['end_time'].to_datetime()

        return summaries

    def close(self):
        """Closes the MongoDB connection."""
        if self.client:
            self.client.close()
            logging.info("MongoDB connection closed successfully.")

    def __enter__(self):
        """Allows usage with `with` statements for automatic connection handling."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Closes the connection when exiting `with` statement."""
        self.close()
