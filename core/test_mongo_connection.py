from connect_to_db import MongoDatabase
from datetime import datetime

db = MongoDatabase()
db.insert_pulse({
    "username": "test_user",
    "event_type": "TestInsert",
    "hostname": "manual_test",
    "timestamp": datetime.now(),
    "source": "test_script"
})
print("✅ Inserted test log into MongoDB.")
