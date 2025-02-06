import time
import numpy as np
import cv2
import pyautogui
from pynput import mouse, keyboard
from datetime import datetime, timedelta
import threading
import pystray
from PIL import Image, ImageDraw


class InactivityDetector:
    def __init__(self, total_runtime=3600, timeout=5, check_interval=2, region=(100, 100, 500, 400)):
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

        self.icon = None
        self.running = True

        self.mouse_listener = mouse.Listener(on_move=self.on_activity, 
                                             on_click=self.on_activity, 
                                             on_scroll=self.on_activity)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_activity)

    def on_activity(self, *args):
        """Resets the inactivity timer on user interaction."""
        if not self.active:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - User is active again.")

        if not self.active:
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
            return True  

        img1 = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2GRAY)
        img2 = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2GRAY)

        diff = cv2.absdiff(img1, img2)
        non_zero_count = np.count_nonzero(diff)

        return non_zero_count > 500  

    def monitor(self):
        """Monitors user activity based on keyboard, mouse, and screen changes."""
        self.mouse_listener.start()
        self.keyboard_listener.start()

        try:
            while time.time() - self.start_time < self.total_runtime and self.running:
                time_since_last_activity = time.time() - self.last_activity_time

                new_screenshot = self.take_screenshot()
                if self.compare_screenshots(self.last_screenshot, new_screenshot):
                    self.on_activity()
                self.last_screenshot = new_screenshot

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

        if total_time > self.total_runtime:
            self.active_time = (self.active_time / total_time) * self.total_runtime
            self.inactive_time = self.total_runtime - self.active_time
        elif total_time < self.total_runtime:
            self.inactive_time += self.total_runtime - total_time

        active_percent = (self.active_time / self.total_runtime) * 100
        inactive_percent = (self.inactive_time / self.total_runtime) * 100

        print(f"\nSummary (Final):\n"
              f"Total Time Tracked: {timedelta(seconds=int(self.total_runtime))}\n"
              f"Active Time: {timedelta(seconds=int(self.active_time))} ({active_percent:.2f}%)\n"
              f"Inactive Time: {timedelta(seconds=int(self.inactive_time))} ({inactive_percent:.2f}%)\n")

    def create_icon(self):
        """Creates a system tray icon with real-time elapsed time."""
        self.icon = pystray.Icon("inactivity_detector", self.create_icon_image(), menu=self.create_menu())
        threading.Thread(target=self.update_tray_time, daemon=True).start()
        self.icon.run()

    def create_icon_image(self):
        """Creates a simple icon image."""
        image = Image.new("RGB", (64, 64), (0, 128, 255))  # Blue icon
        draw = ImageDraw.Draw(image)
        draw.rectangle((10, 10, 54, 54), fill=(255, 255, 255))
        return image

    def create_menu(self):
        """Creates menu options for the system tray icon."""
        return pystray.Menu(pystray.MenuItem("Exit", self.exit_program))

    def update_tray_time(self):
        """Updates the system tray icon title with elapsed time."""
        while self.running:
            elapsed_time = int(time.time() - self.start_time)
            self.icon.title = f"Time: {timedelta(seconds=elapsed_time)}"
            time.sleep(1)

    def exit_program(self, icon, item):
        """Stops monitoring and exits the program."""
        print("Exiting program...")
        self.running = False
        self.icon.stop()


if __name__ == "__main__":
    detector = InactivityDetector(
        total_runtime=3600,  
        timeout=5,  
        check_interval=2,  
        region=(100, 100, 500, 400)
    )

    monitor_thread = threading.Thread(target=detector.monitor)
    monitor_thread.start()

    detector.create_icon()
