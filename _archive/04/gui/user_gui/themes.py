# themes.py

light_theme = """
QMainWindow {
    background-color: #f5f5f5;
}
QWidget {
    background-color: #f5f5f5;
    color: #222;
    font-family: 'Segoe UI';
    font-size: 14px;
}
QPushButton {
    background-color: #3498db;
    color: white;
    border-radius: 6px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #2980b9;
}
QPushButton:pressed {
    background-color: #1c4ca0;
}
QDateEdit {
    background-color: #ffffff;
    border: 1px solid #3498db;
    color: #222;
    padding: 2px 6px;
}
QLineEdit {
    background-color: #ffffff;
    color: #222;
    border: 1px solid #3498db;
    border-radius: 4px;
    padding: 4px 6px;
    font-weight: 600;
}
QTableWidget {
    background-color: #ffffff;
    color: #222;
    border: 1px solid #3498db;
    gridline-color: #ccc;
}
QTableWidget::item:alternate {
    background-color: #f0f0f0;
}
QHeaderView::section {
    background-color: #ddd;
    color: #222;
    font-weight: bold;
}
QLabel {
    background-color: #e0e0e0;
    padding: 4px 8px;
    border-radius: 4px;
}
"""

dark_theme = """
QMainWindow {
    background-color: #2b2b2b;
}
QWidget {
    background-color: #2b2b2b;
    color: #f0f0f0;
    font-family: 'Segoe UI', Arial;
    font-size: 14px;
}
QPushButton {
    background-color: #3a86ff;
    color: white;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #265dd8;
}
QPushButton:pressed {
    background-color: #1c4ca0;
}
QDateEdit {
    background-color: #292929;
    color: #f0f0f0;
    border: 1px solid #444;
    padding: 2px 6px;
}
QLineEdit {
    background-color: #3b3b3b;
    color: #f0f0f0;
    border: 1px solid #666;
    border-radius: 4px;
    padding: 4px 6px;
    font-weight: 600;
}
QTableWidget {
    background-color: #292929;
    color: #f0f0f0;
    border: 1px solid #444;
    gridline-color: #666;
}
QTableWidget::item:alternate {
    background-color: #3a3a3a;
}
QHeaderView::section {
    background-color: #393939;
    color: #dddddd;
    font-weight: bold;
}
QLabel {
    background-color: #333;
    padding: 4px 8px;
    border-radius: 4px;
}
"""

neon_theme = """
QMainWindow {
    background-color: #0f0f0f;
}
QWidget {
    background-color: #0f0f0f;
    color: #39ff14;
    font-family: 'Courier New', monospace;
    font-size: 14px;
}
QPushButton {
    background-color: #39ff14;
    color: #000;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #2be10d;
}
QPushButton:pressed {
    background-color: #20c70a;
}
QDateEdit {
    background-color: #111;
    border: 1px solid #39ff14;
    color: #39ff14;
    padding: 2px 6px;
}
QLineEdit {
    background-color: #111;
    color: #39ff14;
    border: 1px solid #39ff14;
    border-radius: 4px;
    padding: 4px 6px;
    font-weight: 600;
}
QTableWidget {
    background-color: #111;
    border: 1px solid #39ff14;
    color: #39ff14;
    gridline-color: #39ff14;
}
QTableWidget::item:alternate {
    background-color: #1a1a1a;
}
QHeaderView::section {
    background-color: #1f1f1f;
    color: #39ff14;
    font-weight: bold;
}
QLabel {
    background-color: #1f1f1f;
    padding: 4px 8px;
    border-radius: 4px;
}
"""

solarized_theme = """
QMainWindow {
    background-color: #fdf6e3;
}
QWidget {
    background-color: #fdf6e3;
    color: #657b83;
    font-family: 'Segoe UI';
    font-size: 14px;
}
QPushButton {
    background-color: #268bd2;
    color: white;
    border-radius: 6px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #007acc;
}
QPushButton:pressed {
    background-color: #005eaa;
}
QDateEdit {
    background-color: #eee8d5;
    border: 1px solid #93a1a1;
    color: #586e75;
    padding: 2px 6px;
}
QLineEdit {
    background-color: #eee8d5;
    color: #586e75;
    border: 1px solid #93a1a1;
    border-radius: 4px;
    padding: 4px 6px;
    font-weight: 600;
}
QTableWidget {
    background-color: #eee8d5;
    color: #586e75;
    border: 1px solid #93a1a1;
    gridline-color: #ccc;
}
QTableWidget::item:alternate {
    background-color: #e3dac9;
}
QHeaderView::section {
    background-color: #93a1a1;
    color: #002b36;
    font-weight: bold;
}
QLabel {
    background-color: #e0dbcd;
    padding: 4px 8px;
    border-radius: 4px;
}
"""

lavender_theme = """
QMainWindow {
    background-color: #f3f0ff;
}
QWidget {
    background-color: #f3f0ff;
    color: #3e3e3e;
    font-family: 'Segoe UI';
    font-size: 14px;
}
QPushButton {
    background-color: #b39ddb;
    color: white;
    border-radius: 6px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #9575cd;
}
QPushButton:pressed {
    background-color: #7e57c2;
}
QDateEdit {
    background-color: #e0d7f5;
    border: 1px solid #b39ddb;
    color: #3e3e3e;
    padding: 2px 6px;
}
QLineEdit {
    background-color: #e0d7f5;
    color: #3e3e3e;
    border: 1px solid #b39ddb;
    border-radius: 4px;
    padding: 4px 6px;
    font-weight: 600;
}
QTableWidget {
    background-color: #e0d7f5;
    border: 1px solid #b39ddb;
    color: #3e3e3e;
    gridline-color: #aaa;
}
QTableWidget::item:alternate {
    background-color: #d8ccf0;
}
QHeaderView::section {
    background-color: #c9bdf5;
    color: #3e3e3e;
    font-weight: bold;
}
QLabel {
    background-color: #d8ccf0;
    padding: 4px 8px;
    border-radius: 4px;
}
"""

strawberry_theme = """
QMainWindow {
    background-color: #fff0f5;
}
QWidget {
    background-color: #fff0f5;
    color: #4b2e2e;
    font-family: 'Segoe UI';
    font-size: 14px;
}
QPushButton {
    background-color: #ff6f91;
    color: white;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #ff4f73;
}
QPushButton:pressed {
    background-color: #e63b61;
}
QDateEdit {
    background-color: #ffe4ec;
    border: 1px solid #ff6f91;
    color: #4b2e2e;
    padding: 2px 6px;
}
QLineEdit {
    background-color: #ffe4ec;
    color: #4b2e2e;
    border: 1px solid #ff6f91;
    border-radius: 4px;
    padding: 4px 6px;
    font-weight: 600;
}
QTableWidget {
    background-color: #ffe4ec;
    border: 1px solid #ff6f91;
    color: #4b2e2e;
    gridline-color: #fcbad3;
}
QTableWidget::item:alternate {
    background-color: #fddde6;
}
QHeaderView::section {
    background-color: #ffc1d1;
    color: #4b2e2e;
    font-weight: bold;
}
QLabel {
    background-color: #ffd6e3;
    padding: 4px 8px;
    border-radius: 4px;
}
"""
blue_theme = """
QMainWindow {
    background-color: #eaf6ff;
}
QWidget {
    background-color: #eaf6ff;
    color: #1b1f3b;
    font-family: 'Segoe UI';
    font-size: 14px;
}
QPushButton {
    background-color: #3498db;
    color: white;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #2c80b4;
}
QPushButton:pressed {
    background-color: #256894;
}
QDateEdit {
    background-color: #ffffff;
    color: #1b1f3b;
    border: 1px solid #3498db;
    padding: 2px 6px;
}
QLineEdit {
    background-color: #ffffff;
    color: #1b1f3b;
    border: 1px solid #3498db;
    border-radius: 4px;
    padding: 4px 6px;
    font-weight: 600;
}
QComboBox {
    background-color: #ffffff;
    color: #1b1f3b;
    border: 1px solid #3498db;
    border-radius: 4px;
    padding: 2px 6px;
    min-height: 24px;
    font-size: 12px;
}
QRadioButton {
    spacing: 6px;
    padding: 4px;
    font-weight: 500;
    font-size: 13px;
    color: #1b1f3b;
}
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 1px solid #3498db;
    background-color: transparent;
}
QRadioButton::indicator:checked {
    background-color: #3498db;
    border: 1px solid #1d6fa5;
}
QTableWidget {
    background-color: #ffffff;
    color: #1b1f3b;
    border: 1px solid #3498db;
    gridline-color: #aacde8;
}
QTableWidget::item:alternate {
    background-color: #f0faff;
}
QHeaderView::section {
    background-color: #d1ecff;
    color: #1b1f3b;
    font-weight: bold;
}
QLabel {
    background-color: #c6e5ff;
    padding: 4px 8px;
    border-radius: 4px;
}
"""

themes = {
    "Light": light_theme,
    "Dark": dark_theme,
    "Neon": neon_theme,
    "Solarized": solarized_theme,
    "Lavender": lavender_theme,
    "Strawberry Milk": strawberry_theme,
    "Blue": blue_theme  # ✅ Add this line
}

