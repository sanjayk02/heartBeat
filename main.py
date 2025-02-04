import time
import numpy as np
import cv2
import pyautogui
from pynput import mouse, keyboard
from datetime import datetime, timedelta

class InactivityDetector:
    def __init__(self, total_runtime=60, timeout=10, check_interval=10, region=(100, 100, 500, 400)):
        self.total_runtime = total_runtime
        self.timeout = timeout
        self.check_interval = check_interval
        self.region = region
        self.last_activity_time = time.time()
        self.active = True

        self.start_time = time.time()
        self.active_time = 0
        self.inactive_time = 0
        self.last_check_time = self.start_time

        self.last_screenshot = None

        # Start input listeners
        self.mouse_listener = mouse.Listener(on_move=self.on_activity, 
                                             on_click=self.on_activity, 
                                             on_scroll=self.on_activity)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_activity)

    def on_activity(self, *args):
        """Resets the inactivity timer on user interaction and immediately records active time."""
        if not self.active:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - User is active again.")
        
        # Ensure active time is only counted once per cycle
        if self.active is False:
            self.active_time += time.time() - self.last_check_time
            self.active = True
        
        self.last_activity_time = time.time()

    def take_screenshot(self):
        """Captures a portion of the screen."""
        left, top, width, height = self.region
        return pyautogui.screenshot(region=(left, top, width, height))

    def compare_screenshots(self, img1, img2):
        """Compares two images and returns True if they are different."""
        if img1 is None or img2 is None:
            return True  # Assume change if no previous image

        img1 = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2GRAY)
        img2 = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2GRAY)

        diff = cv2.absdiff(img1, img2)
        non_zero_count = np.count_nonzero(diff)

        return non_zero_count > 500  # Adjust threshold dynamically

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
                    self.on_activity()
                self.last_screenshot = new_screenshot

                # Check inactivity and update active/inactive time
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

                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - User is {status}")

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("Stopping inactivity detector.")
        finally:
            self.mouse_listener.stop()
            self.keyboard_listener.stop()
            self.print_final_summary()

    def print_final_summary(self):
        """Prints the final summary of active and inactive time."""
        total_time = self.active_time + self.inactive_time

        # Ensure values do not exceed total_runtime
        if total_time > self.total_runtime:
            self.active_time = (self.active_time / total_time) * self.total_runtime
            self.inactive_time = self.total_runtime - self.active_time
        elif total_time < self.total_runtime:  # Fix undercounting
            self.inactive_time += self.total_runtime - total_time

        active_percent = (self.active_time / self.total_runtime) * 100
        inactive_percent = (self.inactive_time / self.total_runtime) * 100

        print(f"\nSummary (Final):\n"
              f"Total Time Tracked: {timedelta(seconds=int(self.total_runtime))}\n"
              f"Active Time: {timedelta(seconds=int(self.active_time))} ({active_percent:.2f}%)\n"
              f"Inactive Time: {timedelta(seconds=int(self.inactive_time))} ({inactive_percent:.2f}%)\n")

if __name__ == "__main__":
    detector = InactivityDetector(
                                    total_runtime   = 360,  
                                    timeout         = 1,  
                                    check_interval  = 1,  
                                    region          = (100, 100, 500, 400)  
                                    )
    detector.monitor()
