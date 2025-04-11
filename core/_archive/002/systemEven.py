import os
import time
import logging
import win32evtlog
import socket
import win32security

LOG_PATH = r"C:\InactivityService\latest_event.log"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

EXCLUDED_USERS = {"SYSTEM", "LOCAL SERVICE", "NETWORK SERVICE", "PIPE$", "-", "DWM-1", "DWM-2", "DWM-10"}

def resolve_sid_to_username(sid_str):
    try:
        sid = win32security.ConvertStringSidToSid(sid_str)
        name, domain, _ = win32security.LookupAccountSid(None, sid)
        return name
    except Exception:
        return sid_str  # fallback: return the SID itself

def parse_username_from_event(event):
    try:
        inserts = event.StringInserts
        logging.info(f"Event ID {event.EventID} - String Inserts: {inserts}")

        if not inserts:
            return None

        if event.EventID == 4624 and len(inserts) > 5:
            return inserts[5].strip()

        elif event.EventID == 4647 and len(inserts) > 1:
            username = inserts[1].strip()
            if username.startswith("S-1-5"):
                return resolve_sid_to_username(username)
            return username

        elif event.EventID == 4634 and len(inserts) > 0:
            username = inserts[0].strip()
            if username.startswith("S-1-5"):
                return resolve_sid_to_username(username)
            return username

        elif event.EventID == 6005:
            return "SYSTEM"

        for s in inserts:
            if s and s.upper() not in EXCLUDED_USERS:
                return s.strip()

        return None
    except Exception as e:
        logging.warning(f"Username parsing failed for Event ID {event.EventID}: {e}")
        return None

def detect_latest_event():
    server = 'localhost'
    log_type = 'Security'
    event_ids_to_watch = [4624, 4647, 4634, 6005]

    try:
        hand = win32evtlog.OpenEventLog(server, log_type)
    except Exception as e:
        logging.error(f"Failed to open event log: {e}")
        print(f"[ERROR] {e}")
        return

    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    events = []
    max_records = 500

    try:
        while len(events) < max_records:
            chunk = win32evtlog.ReadEventLog(hand, flags, 0)
            if not chunk:
                break
            events.extend(chunk)

        for event in events:
            if event.EventID in event_ids_to_watch:
                raw_user = parse_username_from_event(event)

                if not raw_user or raw_user.upper() in EXCLUDED_USERS:
                    logging.info(f"Skipped user/event: {raw_user} - ID {event.EventID}")
                    continue

                hostname = socket.gethostname()

                if event.EventID == 4624:
                    event_type = "User Logon"
                elif event.EventID == 4647:
                    event_type = "User Logoff"
                elif event.EventID == 4634:
                    event_type = "User Logoff (Session Ended)"
                elif event.EventID == 6005:
                    event_type = "System Startup"
                else:
                    event_type = "Other"

                message = f"{event_type} detected - User: {raw_user}, Host: {hostname}"
                print(message)
                logging.info(message)
                break
        else:
            logging.info("No matching user event found.")
    except Exception as e:
        logging.error(f"Error while reading event log: {e}")
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    while True:
        detect_latest_event()
        time.sleep(30)
