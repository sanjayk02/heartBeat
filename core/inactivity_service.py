import win32serviceutil
import win32service
import win32event
import servicemanager
import win32ts
import win32con
import win32gui
import win32api
import logging
import os
import time
from datetime import datetime

# === Configuration ===
SERVICE_NAME    = "InactivityMonitorService"
STATUS_DIR      = r"C:\ProgramData\InactivityMonitor\statuses"
LOG_DIR         = r"C:\ProgramData\InactivityMonitor"
LOG_FILE        = os.path.join(LOG_DIR, "service_log.txt")

# Ensure log directory exists
os.makedirs(STATUS_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class InactivityService(win32serviceutil.ServiceFramework):
    _svc_name_ = SERVICE_NAME
    _svc_display_name_ = "Inactivity Monitor Service"
    _svc_description_ = "Tracks login/logout events and reads user activity status."

    def __init__(self, args):
        super().__init__(args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        logging.info("Stopping service...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        logging.info("Inactivity Monitor Service started.")
        servicemanager.LogInfoMsg("Inactivity Monitor Service is running...")

        # Setup message handler for session change events
        message_map = {
            win32con.WM_WTSSESSION_CHANGE: self.on_session_change,
        }

        wc = win32gui.WNDCLASS()
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "InactivityMonitorWindow"
        wc.lpfnWndProc = message_map
        win32gui.RegisterClass(wc)

        hwnd = win32gui.CreateWindow(
            wc.lpszClassName, "InactivityMonitorWindow",
            0, 0, 0, 0, 0, 0, 0, wc.hInstance, None
        )

        win32ts.WTSRegisterSessionNotification(hwnd, win32ts.NOTIFY_FOR_ALL_SESSIONS)

        # Main loop
        while self.running:
            win32gui.PumpWaitingMessages()
            self.check_user_statuses()
            time.sleep(30)

        win32ts.WTSUnRegisterSessionNotification(hwnd)
        win32gui.DestroyWindow(hwnd)
        logging.info("Inactivity Monitor Service stopped.")

    def on_session_change(self, hwnd, msg, wparam, lparam):
        session_id = lparam
        try:
            username = win32ts.WTSQuerySessionInformation(None, session_id, win32ts.WTSUserName)
        except Exception:
            username = f"Session{session_id}"

        event = {
            win32con.WTS_SESSION_LOGON: "LOGIN",
            win32con.WTS_SESSION_LOGOFF: "LOGOUT",
            win32con.WTS_SESSION_LOCK: "LOCK",
            win32con.WTS_SESSION_UNLOCK: "UNLOCK"
        }.get(wparam, "UNKNOWN")

        logging.info(f"[Session Event] {event}: {username} (Session {session_id})")
        return 0

    def check_user_statuses(self):
        try:
            for filename in os.listdir(STATUS_DIR):
                if filename.endswith("_status.txt"):
                    user = filename.replace("_status.txt", "")
                    path = os.path.join(STATUS_DIR, filename)
                    with open(path, "r") as f:
                        status = f.read().strip()
                    logging.info(f"[User Status] {user}: {status}")
        except Exception as e:
            logging.error(f"Failed to check user statuses: {e}")

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(InactivityService)
