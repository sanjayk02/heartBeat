import os
import logging
from inactivity_monitor import InactivityMonitor

class RunMonitor:
    """Runs InactivityMonitor manually for debugging."""

    def __init__(self):
        self.monitor = InactivityMonitor()

    def start_monitoring(self):
        """Starts monitoring activity."""
        logging.info("[MANUAL] Starting InactivityMonitor...")
        self.monitor.monitor()

if __name__ == "__main__":
    runner = RunMonitor()
    runner.start_monitoring()
