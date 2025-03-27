import subprocess
import ctypes
import sys  # <-- Needed for exit()

class SetupChecker:
    def __init__(self, service_name="InactivityMonitorService", task_name="InactivityMonitorLauncher"):
        self.service_name = service_name
        self.task_name = task_name

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def check_service_status(self):
        try:
            output = subprocess.check_output(f'sc query "{self.service_name}"', shell=True, text=True)
            exists = True
            running = "RUNNING" in output
        except subprocess.CalledProcessError:
            exists = False
            running = False
        return exists, running

    def check_task_exists(self):
        try:
            subprocess.check_output(f'schtasks /Query /TN "{self.task_name}"', shell=True, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    def should_install(self):
        svc_exists, _ = self.check_service_status()
        task_exists = self.check_task_exists()
        return not (svc_exists and task_exists)

# === Entry Point ===
if __name__ == "__main__":
    checker = SetupChecker()
    if checker.should_install():
        sys.exit(0)  # Proceed with install
    else:
        sys.exit(1)  # Already installed – skip
