# -*- coding: utf-8 -*-
# Heart Beat Application - Inactivity Detector Service
# This service monitors user inactivity and logs it to a shared file.
# It uses the IdleReporter class from the idle_reporter module to perform the monitoring.
# The service is designed to run on Windows and can be installed, started, stopped, and uninstalled using the command line.
# The service will log its status and any errors to the Windows Event Log.
# The service will run indefinitely until stopped, checking for user inactivity at regular intervals.
# The IdleReporter class is responsible for the actual monitoring of user activity and logging.
# The service will check for user inactivity every 5 seconds and log the status to a shared file.
# The service will also handle any exceptions that occur during the monitoring process and log them to the Windows Event Log.
# The service will run as a Windows service and can be controlled using the Windows Service Control Manager.
# The service will be installed using the pywin32 library and can be controlled using the command line.
# The service will be installed using the following command:
# python inactivity_service.py install
# The service can be started using the following command:
# python inactivity_service.py start
# The service can be stopped using the following command:

# author: Sanja
# date: 2025-03-01

import win32serviceutil
import win32service
import win32event
import servicemanager
import os
import logging
from idle_reporter import IdleReporter

class InactivityService(win32serviceutil.ServiceFramework):
    """Windows service that runs IdleReporter for inactivity detection."""

    _svc_name_          = "InactivityDetectorService"
    _svc_display_name_  = "Inactivity Detector Service"
    _svc_description_   = "Logs user activity by reading status from a shared file."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop  = win32event.CreateEvent(None, 0, 0, None)
        self.running    = True
        self.reporter   = IdleReporter()

    def SvcStop(self):
        """Handle service stop request."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """Main service execution loop."""
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ""))

        logging.info("Inactivity Detector Service started.")
        self.reporter.monitor()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(InactivityService)
