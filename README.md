"""
    InactivityTracker.py
    ---------------------

    This script is a user-space agent that monitors keyboard and mouse activity for the currently logged-in user.
    Its main purpose is to track user presence and log both real-time activity and full session summaries into a MongoDB database.

    Features:
    - Detects periods of user inactivity based on configurable timeout (default: 5 minutes).
    - Continuously tracks active and inactive time.
    - Logs real-time "activity pulses" to MongoDB with timestamps and user status.
    - At the end of each day or on shutdown, logs a complete session summary:
        - Total active and inactive durations
        - Session start and end times
    - Writes a status file for service-level visibility:
        - `C:\\ProgramData\\InactivityMonitor\\statuses\\<username>_status.txt`
        - Status values: "Active" or "Inactive"
    - Maintains daily logs in the user's folder:
        - `C:\\Users\\<username>\\InactivityLogs\\activity_monitor.log`

    Integration:
    - This agent complements the system-level `inactivity_service.py`, which logs login/logout events.
    - One-way communication: Agent updates status files that the service can read.

    Deployment:
    - Should be configured to start on user login (e.g., via Startup folder or Group Policy).
    - Requires `pynput`, `pyyaml`, `pymongo`, and `pywin32` Python packages.

    Configuration:
    - Settings are loaded from: `../config/config.yml`
        - timeout: idle threshold in seconds
        - check_interval: activity check frequency in seconds

    Author: [Your Name or Team]
    Date: [Date]
"""
