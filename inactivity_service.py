import win32serviceutil
import win32service
import win32event
import servicemanager
import time
import os
import logging
from datetime import datetime

STATUS_FILE = os.path.join(os.path.expanduser("~"), "InactivityLogs", "status.txt")
LOG_FILE = os.path.join(os.path.expanduser("~"), "InactivityLogs", "service_log.txt")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class InactivityService(win32serviceutil.ServiceFramework):
    _svc_name_ = "InactivityMonitorService"
    _svc_display_name_ = "Inactivity Monitor Service"
    _svc_description_ = "Reads idle status written by user agent and logs it."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        logging.info("🛑 Service is stopping.")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        logging.info("🚀 Inactivity Service started.")
        servicemanager.LogInfoMsg("Inactivity Service running...")

        try:
            self.run()
        except Exception as e:
            logging.exception("💥 Error in service run loop:")

    def run(self):
        last_status = None
        while self.running:
            try:
                if os.path.exists(STATUS_FILE):
                    with open(STATUS_FILE, "r") as f:
                        content = f.read().strip()

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if content != last_status:
                        logging.info(f"📌 User Status: {content} at {timestamp}")
                        last_status = content
                else:
                    logging.warning("⚠️ status.txt not found.")
            except Exception as e:
                logging.error(f"❌ Error reading status file: {e}")

            time.sleep(30)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(InactivityService)
