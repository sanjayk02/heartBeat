import time
import numpy as np
import cv2
import pyautogui
from pynput import mouse, keyboard
from PIL import ImageChops

class InactivityDetector:
    def __init__(self, timeout=10, screenshot_interval=2, region=(100, 100, 500, 400)):
        """
        timeout: Inactivity time threshold in seconds.
        screenshot_interval: Time interval between screenshots.
        region: The screen area to capture (left, top, width, height).
        """
        self.timeout = timeout
        self.screenshot_interval = screenshot_interval
        self.region = region
        self.last_activity_time = time.time()
        self.active = True
        self.last_screenshot = None

        # Start input listeners
        self.mouse_listener = mouse.Listener(on_move=self.on_activity, on_click=self.on_activity, on_scroll=self.on_activity)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_activity)

    def on_activity(self, *args):
        """Resets the inactivity timer on user interaction."""
        self.last_activity_time = time.time()
        if not self.active:
            print("User is active again.")
            self.active = True

    def take_screenshot(self):
        """Captures a portion of the screen."""
        left, top, width, height = self.region
        return pyautogui.screenshot(region=(left, top, width, height))

    def compare_screenshots(self, img1, img2):
        """Compares two images and returns True if they are different."""
        if img1 is None or img2 is None:
            return True  # If any image is missing, assume a difference

        # Convert images to grayscale for better comparison
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
            while True:
                time_since_last_activity = time.time() - self.last_activity_time

                # Take a new screenshot
                new_screenshot = self.take_screenshot()
                if self.compare_screenshots(self.last_screenshot, new_screenshot):
                    self.on_activity()  # Reset activity timer if change is detected
                self.last_screenshot = new_screenshot  # Store latest screenshot

                # Check inactivity
                if time_since_last_activity > self.timeout and self.active:
                    print("User is inactive!")
                    self.active = False

                time.sleep(self.screenshot_interval)
        except KeyboardInterrupt:
            print("Stopping inactivity detector.")
        finally:
            self.mouse_listener.stop()
            self.keyboard_listener.stop()

if __name__ == "__main__":
    detector = InactivityDetector(timeout=10, screenshot_interval=2, region=(100, 100, 500, 400))
    detector.monitor()
