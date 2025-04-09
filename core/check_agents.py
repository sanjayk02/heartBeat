import os
import psutil
import logging
import getpass
from datetime import datetime

# === CONFIG ===
AGENT_NAME = "InactivityTracker.py"
AGENT_PATH = r"C:\stuff\source\heartBeat\core\InactivityTracker.py"
PYTHONW = r"C:\Program Files\Python39\pythonw.exe"
LOG_FILE = os.path.join(os.environ["USERPROFILE"], "InactivityLogs", "agent_check.log")

# === Logging Setup ===
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def is_agent_running():
    """Check if the agent script is currently running for this user."""
    username = getpass.getuser()
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline']):
        try:
            if proc.info['username'] == username:
                cmdline = ' '.join(proc.info['cmdline']).lower()
                if AGENT_NAME.lower() in cmdline:
                    logging.info(f"✅ Agent found running (PID: {proc.info['pid']})")
                    return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    return False

def restart_agent():
    """Attempt to restart the agent silently."""
    if os.path.exists(PYTHONW) and os.path.exists(AGENT_PATH):
        logging.info("🔄 Attempting to restart agent...")
        os.system(f'start "" "{PYTHONW}" "{AGENT_PATH}"')
        logging.info("✅ Agent restart command issued.")
    else:
        logging.error("❌ Agent or pythonw.exe not found. Cannot restart.")

def main():
    logging.info("🛡️ Agent status check started.")
    if is_agent_running():
        logging.info("✅ Agent is running normally.")
    else:
        logging.warning("❌ Agent is NOT running for this user!")
        restart_agent()

    logging.info("🛡️ Agent status check completed.\n")

if __name__ == "__main__":
    main()
