import win32evtlog
import win32security
import socket
import logging

class EventDetector:
    EXCLUDED_USERS = {"SYSTEM", "LOCAL SERVICE", "NETWORK SERVICE", "PIPE$", "-", "DWM-1", "DWM-2", "DWM-10"}
    EVENT_IDS = [4624, 4647, 4634, 6005]

    def __init__(self, log_path=r"C:\InactivityService\event_detector.log", max_records=500):
        self.hostname = socket.gethostname()
        self.server = 'localhost'
        self.log_type = 'Security'
        self.max_records = max_records

        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def resolve_sid_to_username(self, sid_str):
        try:
            sid = win32security.ConvertStringSidToSid(sid_str)
            name, domain, _ = win32security.LookupAccountSid(None, sid)
            return name
        except Exception:
            return sid_str

    def parse_username(self, event):
        inserts = event.StringInserts
        if not inserts:
            return None

        try:
            username = None

            if event.EventID == 4624 and len(inserts) > 5:
                username = inserts[5].strip()
            elif event.EventID == 4647 and len(inserts) > 1:
                username = self.resolve_sid_to_username(inserts[1].strip())
            elif event.EventID == 4634 and len(inserts) > 0:
                username = self.resolve_sid_to_username(inserts[0].strip())
            elif event.EventID == 6005:
                username = "SYSTEM"

            if username:
                uname_upper = username.upper()
                # Exclude common system-generated usernames
                if (uname_upper in self.EXCLUDED_USERS or
                    uname_upper.startswith("UMFD-") or
                    uname_upper.startswith("DWM-")):
                    return None
                return username.strip()

        except Exception as e:
            logging.warning(f"Failed to parse username: {e}")
        return None

    def get_latest_user_event(self):
        try:
            handle = win32evtlog.OpenEventLog(self.server, self.log_type)
        except Exception as e:
            logging.error(f"Failed to open event log: {e}")
            return None

        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        events = []

        try:
            while len(events) < self.max_records:
                chunk = win32evtlog.ReadEventLog(handle, flags, 0)
                if not chunk:
                    break
                events.extend(chunk)

            for event in events:
                if event.EventID not in self.EVENT_IDS:
                    continue

                username = self.parse_username(event)
                if not username or username.upper() in self.EXCLUDED_USERS:
                    continue

                if event.EventID == 4624:
                    event_type = "Logon"
                elif event.EventID == 4647:
                    event_type = "Logoff"
                elif event.EventID == 4634:
                    event_type = "Logoff (Session End)"
                elif event.EventID == 6005:
                    event_type = "Startup"
                else:
                    event_type = "Other"

                return {
                    "event_type": event_type,
                    "username": username,
                    "hostname": self.hostname,
                    "timestamp": event.TimeGenerated.Format()
                }

        except Exception as e:
            logging.error(f"Error while scanning event log: {e}")

        return None


# from event_detector import EventDetector
# detector = EventDetector()
# event = detector.get_latest_user_event()
# if event:
#     print(f"{event['timestamp']} - {event['event_type']} by {event['username']} on {event['hostname']}")
