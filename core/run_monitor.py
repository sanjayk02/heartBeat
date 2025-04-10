# -*- coding: utf-8 -*-
# Heart Beat Application - Inactivity Monitor (Manual Runner)
# author: Sanja
# date: 2025-03-01

import logging
import signal
import sys
from inactivity_monitor import InactivityMonitor

class RunMonitor:
    """Runs InactivityMonitor manually for debugging."""

    def __init__(self):
        self.monitor = InactivityMonitor()

        # Setup basic logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        # Signal handlers for clean exit
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

    def handle_exit(self, signum, frame):
        logging.info("Received termination signal. Exiting RunMonitor.")
        sys.exit(0)

    def start_monitoring(self):
        """Starts monitoring activity."""
        logging.info("[MANUAL] Starting InactivityMonitor...")
        self.monitor.monitor()

if __name__ == "__main__":
    runner = RunMonitor()
    runner.start_monitoring()
