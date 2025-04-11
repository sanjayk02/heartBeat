from event_detector import EventDetector
from connect_to_db import MongoDatabase
import logging
from datetime import datetime
import os

# Setup optional logging to mimic service.log
log_path = r"C:\InactivityService\service.log"
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize detector and DB
detector = EventDetector()
db = MongoDatabase()

# Get and show latest user event
event = detector.get_latest_user_event()
if event:
    print(f"Event: {event}")
    logging.info(f"[TEST] Event detected: {event['event_type']} by {event['username']}")

    # Prepare DB entry
    db_entry = {
        "username": event['username'],
        "hostname": event['hostname'],
        "event_type": event['event_type'].upper(),
        "timestamp": datetime.now(),
        "source": "test_event_logger"
    }

    # Push to MongoDB
    db.insert_pulse(db_entry)
    print("Inserted into MongoDB.")
else:
    print("No recent user event found.")

