import time
import numpy as np
import cv2
import pyautogui
from pynput import mouse, keyboard
from datetime import datetime, timedelta

class InactivityDetector:
    def __init__(self, total_runtime=3600, timeout=30, check_interval=10, region=(100, 100, 500, 400)):
        """
        total_runtime: Total run time in seconds (default: 1 hour).
        timeout: Time threshold (seconds) before considering the user inactive.
        check_interval: How often (seconds) to check for activity.
        region: Screen area to capture (left, top, width, height).
        """
        self.total_runtime = total_runtime
        self.timeout = timeout
        self.check_interval = check_interval
        self.region = region
        self.last_activity_time = time.time()
        self.active = True

        self.start_time = time.time()
        self.active_time = 0
        self.inactive_time = 0
        self.last_check_time = time.time()

        self.last_screenshot = None

        # Start input listeners
        self.mouse_listener = mouse.Listener(on_move=self.on_activity, on_click=self.on_activity, on_scroll=self.on_activity)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_activity)

    def on_activity(self, *args):
        """Resets the inactivity timer on user interaction."""
        if not self.active:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - User is active again.")
        self.last_activity_time = time.time()
        self.active = True

    def take_screenshot(self):
        """Captures a portion of the screen."""
        left, top, width, height = self.region
        return pyautogui.screenshot(region=(left, top, width, height))

    def compare_screenshots(self, img1, img2):
        """Compares two images and returns True if they are different."""
        if img1 is None or img2 is None:
            return True  # Assume change if no previous image

        # Convert images to grayscale
        img1 = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2GRAY)
        img2 = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2GRAY)

        # Compute absolute difference
        diff = cv2.absdiff(img1, img2)
        non_zero_count = np.count_nonzero(diff)

        return non_zero_count > 1000  # Threshold for detecting changes

    def monitor(self):
        """Monitors user activity based on keyboard, mouse, and screen changes."""
        self.mouse_listener.start()
        self.keyboard_listener.start()

        try:
            while time.time() - self.start_time < self.total_runtime:
                time_since_last_activity = time.time() - self.last_activity_time

                # Take a new screenshot every check_interval seconds
                new_screenshot = self.take_screenshot()
                if self.compare_screenshots(self.last_screenshot, new_screenshot):
                    self.on_activity()  # Reset activity timer if change is detected
                self.last_screenshot = new_screenshot  # Store latest screenshot

                # Check inactivity and update total active/inactive time
                elapsed = time.time() - self.last_check_time
                self.last_check_time = time.time()

                if time_since_last_activity <= self.timeout:
                    self.active_time += elapsed
                    status = "Active"
                else:
                    self.inactive_time += elapsed
                    status = "Inactive"

                # Print time and user status
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - User is {status}")

                # Periodically show summary
                if int(self.active_time + self.inactive_time) % 300 == 0:  # Every 5 minutes
                    self.print_summary()

                time.sleep(self.check_interval)  # Wait for the next check
        except KeyboardInterrupt:
            print("Stopping inactivity detector.")
        finally:
            self.mouse_listener.stop()
            self.keyboard_listener.stop()
            self.print_summary(final=True)

    def print_summary(self, final=False):
        """Prints a summary of active and inactive time."""
        total_time = self.active_time + self.inactive_time
        active_percent = (self.active_time / total_time) * 100 if total_time > 0 else 0
        inactive_percent = (self.inactive_time / total_time) * 100 if total_time > 0 else 0

        summary_text = f"\nSummary {'(Final)' if final else ''}:\n" \
                       f"Total Time Tracked: {timedelta(seconds=int(total_time))}\n" \
                       f"Active Time: {timedelta(seconds=int(self.active_time))} ({active_percent:.2f}%)\n" \
                       f"Inactive Time: {timedelta(seconds=int(self.inactive_time))} ({inactive_percent:.2f}%)\n"

        print(summary_text)

if __name__ == "__main__":
    detector = InactivityDetector(total_runtime=60, timeout=10, check_interval=10, region=(100, 100, 500, 400))
    detector.monitor()
