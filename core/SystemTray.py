import pystray
from PIL import Image, ImageDraw
import threading
import time
from datetime import timedelta

class ActivityTrayIcon:
    def __init__(self, detector):
        """Initializes the system tray icon for activity status."""
        self.detector = detector
        self.icon = pystray.Icon("activity_tracker", self.create_icon_image())
        self.running = True

    def create_icon_image(self):
        """Generates a simple system tray icon."""
        image = Image.new("RGB", (64, 64), (0, 128, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle((10, 10, 54, 54), fill=(255, 255, 255))
        return image

    def update_tray_time(self):
        """Updates system tray tooltip with active/inactive time."""
        while self.running:
            elapsed_active = timedelta(seconds=int(self.detector.active_time))
            elapsed_inactive = timedelta(seconds=int(self.detector.inactive_time))
            self.icon.title = f"Active: {elapsed_active} | Inactive: {elapsed_inactive}"
            time.sleep(5)

    def run(self):
        """Runs the system tray icon and updates it in a separate thread."""
        threading.Thread(target=self.update_tray_time, daemon=True).start()
        self.icon.run()

    def stop(self):
        """Stops the tray icon gracefully."""
        self.running = False
        self.icon.stop()
