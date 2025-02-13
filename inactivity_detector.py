import time
import asyncio
import pyautogui
import numpy as np
import cv2
from pynput import mouse, keyboard
from datetime import datetime, timedelta
import os
import signal
import win32ts


class InactivityDetector:
    def __init__(self, total_runtime=3600, timeout=3, check_interval=2, region=None, log_file="activity_log.txt"):
        self.total_runtime = total_runtime
        self.timeout = timeout
        self.check_interval = check_interval
        self.log_file = log_file

        screen_width, screen_height = pyautogui.size()
        self.region = region if region else (
            int(screen_width * 0.1),
            int(screen_height * 0.1),
            int(screen_width * 0.5),
            int(screen_height * 0.5)
        )

        self.last_activity_time = time.time()
        self.active = True
        self.start_time = time.time()
        self.active_time = 0
        self.inactive_time = 0
        self.last_check_time = self.start_time
        self.last_frame = None
        self.running = True
        self.session_locked = False

        self.mouse_listener = mouse.Listener(on_move=self.on_activity, on_click=self.on_activity, on_scroll=self.on_activity)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_activity)

        # Block Ctrl+C and termination signals
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)

        with open(self.log_file, 'a') as f:
            f.write(f"\n--- Monitoring Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")

    def log(self, message):
        print(message)
        with open(self.log_file, 'a') as f:
            f.write(f"{message}\n")

    def on_activity(self, *args):
        if not self.active:
            self.log(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - User is active again.")
        self.active = True
        self.last_activity_time = time.time()

    def take_screenshot(self):
        left, top, width, height = self.region
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

    def detect_motion(self, new_frame):
        if self.last_frame is None:
            self.last_frame = new_frame
            return False

        flow = cv2.calcOpticalFlowFarneback(self.last_frame, new_frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        motion_intensity = np.linalg.norm(flow)
        self.last_frame = new_frame

        return motion_intensity > 5  # Adjust sensitivity if needed

    def check_session_state(self):
        """
        Use pywin32's win32ts module to check the current session state.
        This is the most stable approach for Active/Disconnected detection.
        """
        WTS_CURRENT_SESSION = win32ts.WTS_CURRENT_SESSION

        try:
            session_info = win32ts.WTSQuerySessionInformation(
                win32ts.WTS_CURRENT_SERVER_HANDLE,
                WTS_CURRENT_SESSION,
                win32ts.WTSConnectState
            )

            self.log(f"Session State Detected: {session_info}")

            # Active = 0, Disconnected = 1, etc.
            if session_info == win32ts.WTSActive:
                return False  # Active session
            else:
                return True  # Disconnected or other states

        except Exception as e:
            self.log(f"Failed to query session state: {e}")
            return True  # Assume disconnected if it fails

    async def monitor(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()

        while time.time() - self.start_time < self.total_runtime and self.running:
            self.session_locked = self.check_session_state()

            if self.session_locked:
                self.log(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Session Disconnected or User Switched. Pausing...")
                await asyncio.sleep(self.check_interval)
                continue

            time_since_last_activity = time.time() - self.last_activity_time
            new_frame = self.take_screenshot()
            motion_detected = self.detect_motion(new_frame)

            if motion_detected:
                self.on_activity()

            elapsed = time.time() - self.last_check_time
            self.last_check_time = time.time()

            if time_since_last_activity <= self.timeout:
                self.active_time += elapsed
                self.active = True
                status = "Active"
            else:
                self.inactive_time += elapsed
                self.active = False
                status = "Inactive"

            self.log(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - User is {status}")

            await asyncio.sleep(self.check_interval)

        self.mouse_listener.stop()
        self.keyboard_listener.stop()
        self.print_final_summary()

    def print_final_summary(self):
        total_time = self.active_time + self.inactive_time
        active_percent = (self.active_time / total_time) * 100 if total_time > 0 else 0
        inactive_percent = (self.inactive_time / total_time) * 100 if total_time > 0 else 0

        summary = (f"\nSummary:\n"
                   f"Active Time: {timedelta(seconds=int(self.active_time))} ({active_percent:.2f}%)\n"
                   f"Inactive Time: {timedelta(seconds=int(self.inactive_time))} ({inactive_percent:.2f}%)\n")

        self.log(summary)


if __name__ == "__main__":
    detector = InactivityDetector(total_runtime=60, timeout=3, check_interval=2)
    asyncio.run(detector.monitor())
