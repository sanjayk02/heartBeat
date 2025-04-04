from PySide2.QtWidgets import QApplication
from connect_to_db import MongoDatabase
from SystemTray import HeartBeatTray

def main():
    # Connect to MongoDB
    db = MongoDatabase()

    # Create and launch the Qt Tray App
    app = QApplication([])
    tray = HeartBeatTray(db)
    tray.show()
    app.exec_()

if __name__ == "__main__":
    main()
        