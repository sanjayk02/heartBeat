import win32serviceutil
import win32service
import win32event
import servicemanager
import subprocess
import os

class SystemEventService(win32serviceutil.ServiceFramework):
    _svc_name_          = "SystemEventMonitor"
    _svc_display_name_  = "System Event Monitor"
    _svc_description_   = "Detects Windows logon, logoff, and startup events."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.script_path = r"C:\stuff\source\PulseWork\core\systemEven.py"

    def SvcStop(self):
        servicemanager.LogInfoMsg("SystemEventMonitor service is stopping...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("SystemEventMonitor service started.")
        subprocess.call(["python", self.script_path])

if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(SystemEventService)
