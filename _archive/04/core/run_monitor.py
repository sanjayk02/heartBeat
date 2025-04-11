# -*- coding: utf-8 -*-
# author: Sanja
# date: 2025-03-01

# Heart Beat Application - Inactivity Monitor
# This script is part of the Heart Beat Application.
# It monitors user inactivity and performs actions based on it.
# This script is designed to be run manually for debugging purposes.
# It is not intended for production use.
# This script is part of the Heart Beat Application.
# It monitors user inactivity and performs actions based on it.
# This script is designed to be run manually for debugging purposes.
# It is not intended for production use.
# This script is part of the Heart Beat Application.
# It monitors user inactivity and performs actions based on it.
# This script is designed to be run manually for debugging purposes.
# It is not intended for production use.
# This script is part of the Heart Beat Application.
# It monitors user inactivity and performs actions based on it.
# This script is designed to be run manually for debugging purposes.

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
