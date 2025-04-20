
# -*- coding: utf-8 -*-
# Heart Beat Application - User GUI
# author: Sanja
# date: 2025-03-01
# description: This module provides the main GUI for the Heart Beat application.
# It includes functionalities for displaying user data, selecting dates,
# and applying themes. The GUI is built using PySide2 and Qt Designer.
# ========================================================================================================
# Imports # Standard Libraries
# ========================================================================================================
import os
import sys
import csv
import logging
from datetime import datetime
import socket

from PySide2.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QSizePolicy,
    QWidget, QDateEdit, QPushButton, QHeaderView, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QLineEdit, QRadioButton, QFileDialog
)
from PySide2.QtCore import Qt, QFile, QIODevice, QDate, QSize
from PySide2.QtGui import QIcon, QPixmap, QFont, QPalette, QColor
from PySide2.QtUiTools import QUiLoader

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# ========================================================================================================
# Custom Imports
# ========================================================================================================
from themes import themes # Custom theme dictionary
from db_handler import GetPulseData
from time_summary import TimeSummary
from collapsible_summary import CollapsibleTab
from summary_panel import SummaryPanel

# === Paths ===
script_path = os.path.abspath(__file__)
ui_path     = os.path.join(os.path.dirname(script_path), "ui/ui_user.ui")
_root       = os.path.abspath(os.path.join(script_path, "..", ".."))
icon_path   = os.path.join(os.path.dirname(_root), "resources/icons/user_icon.png").replace("\\", "/")

# === Logging ===
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# === Stylesheet (default fallback) ===
default_stylesheet = """
    QMainWindow { background-color: #2b2b2b; }
    QWidget { background-color: #2b2b2b; color: #f0f0f0; font-family: 'Segoe UI'; font-size: 14px; }
    #sidePanel { background-color: #1c1c1c; border-right: 1px solid #444; padding: 12px; }
    QLabel { color: #e6e6e6; font-weight: 600; padding-bottom: 6px; }
    QPushButton { background-color: #3a86ff; color: white; border-radius: 6px; padding: 6px 12px; font-weight: 600; }
    QPushButton:hover { background-color: #265dd8; }
    QDateEdit, QLineEdit, QTextEdit { background-color: #3b3b3b; color: white; border: 1px solid #666; border-radius: 4px; padding: 4px 6px; }
    QTableWidget { background-color: #292929; color: #f0f0f0; border: 1px solid #444; gridline-color: #555; alternate-background-color: #333; selection-background-color: #444; selection-color: white; }
    QTableWidget::item { padding: 8px; font-weight: 500; }
"""

# ========================================================================================================
# Main GUI Class
# ========================================================================================================
class UserGUI(QMainWindow):
    
    # ----------------------------------------------------------------------------------------------------
    # Constructor
    # ----------------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Initializes the main GUI window for the Heart Beat application.

        This constructor sets up the user interface, configures the main window,
        and initializes various components such as the summary panel, menu bar,
        date selectors, username display, and table. It also applies a default
        theme, connects signals and slots, and ensures the window stays on top.

        Attributes:
            ui (None): Placeholder for the user interface object.
            _summary_panel (dict): Dictionary to store summary panel components.
            _summary_month_info (SummaryPanel): Instance of the SummaryPanel class.
        """
        super().__init__()
        self.ui = None
        self._summary_panel = {}
        self._summary_month_info = SummaryPanel()
        self.load_ui()
        self.setWindowTitle("Heart Beat")
        self.add_menu_bar()
        self.add_icon_to_layout()
        self.load_summary_panel()
        self.add_date_selectors()
        self.add_username()
        self.setup_table()
        self.change_theme("Dark")
        self.connection()
        self.setStyleSheet(default_stylesheet)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    # ----------------------------------------------------------------------------------------------------
    # Load the UI file and set up the main window
    # ----------------------------------------------------------------------------------------------------
    def load_ui(self):
        """
        Loads the UI layout from a .ui file and sets it as the central widget of the main window.
        This method uses QUiLoader to dynamically load the UI file specified by `ui_path`.
        If the file cannot be opened or the UI fails to load, an error message is displayed,
        and the application exits. Upon successful loading, the method configures the main
        window's size, minimum size, and optionally sets a window icon if `icon_path` exists.
        It also adjusts the sizes and stretch factors of specific QSplitter widgets in the UI.
        Raises:
            SystemExit: If the UI file cannot be opened or the UI fails to load.
        Side Effects:
            - Displays a QMessageBox with an error message if loading fails.
            - Sets the central widget, size, and icon of the main window.
            - Configures splitter sizes and stretch factors in the UI.
        Attributes:
            self.ui: The loaded UI object, which is set as the central widget.
        """
        loader = QUiLoader()
        ui_file = QFile(ui_path)
        if not ui_file.open(QIODevice.ReadOnly):
            QMessageBox.critical(self, "Error", f"Cannot open UI file:\n{ui_path}")
            sys.exit(1)
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        if self.ui:
            self.setCentralWidget(self.ui)
            self.resize(350, 600)
            self.setMinimumSize(QSize(350, 600))
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                
            self.ui.splitterMain.setSizes([350, 0])
            self.ui.splitter_4.setSizes([50, 550])
            self.ui.splitterB.setSizes([600, 50])
            self.ui.splitterB.setStretchFactor(1, 0)
            
        else:
            QMessageBox.critical(self, "Error", "Failed to load the UI layout.")
            sys.exit(1)

    # ----------------------------------------------------------------------------------------------------
    # Add add_menu_bar to the layout
    # ----------------------------------------------------------------------------------------------------
    def add_menu_bar(self):
        """
        Creates and configures the menu bar for the GUI application.
        This method sets up the following menus and their respective actions:
        - File Menu:
            - "Export to CSV" (Shortcut: Ctrl+E): Triggers the `export_to_csv` method.
            - "Print" (Shortcut: Ctrl+P): Triggers the `print_table` method.
            - "Exit" (Shortcut: Ctrl+Q): Closes the application.
        - View Menu:
            - "Refresh Logs" (Shortcut: Ctrl+R): Triggers the `on_search_clicked` method.
            - "Toggle Filters" (Shortcut: Ctrl+F): Placeholder for toggling filters functionality.
        - Help Menu:
            - "About": Triggers the `show_about_dialog` method.
        Note:
            The "Toggle Filters" action currently does not have a connected method.
        """
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        export_action = file_menu.addAction("Export to CSV")
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_to_csv)

        print_action = file_menu.addAction("Print")
        print_action.setShortcut("Ctrl+P")
        print_action.triggered.connect(self.print_table)

        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        view_menu = menu_bar.addMenu("View")
        refresh_action = view_menu.addAction("Refresh Logs")
        refresh_action.setShortcut("Ctrl+R")
        refresh_action.triggered.connect(self.on_search_clicked)

        toggle_filters_action = view_menu.addAction("Toggle Filters")
        toggle_filters_action.setShortcut("Ctrl+F")
        # toggle_filters_action.triggered.connect(self.date_toggle_btn.click)

        help_menu = menu_bar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about_dialog)

    # ----------------------------------------------------------------------------------------------------
    # Add the show_about_dialog to the layout
    # ----------------------------------------------------------------------------------------------------
    def show_about_dialog(self):
        QMessageBox.information(self, "About Heart Beat", "Heart Beat\n\nA productivity tracking tool.\nVersion 1.0\n\nCreated by You")

    # ----------------------------------------------------------------------------------------------------
    # export_to_csv method to export the table data to a CSV file
    # ----------------------------------------------------------------------------------------------------
    def export_to_csv(self):
        """
        Exports the data from the table widget to a CSV file.

        This method checks if the table widget contains data and prompts the user
        to select a file path to save the CSV file. It writes the table's headers
        and data rows to the file. If the export is successful, a confirmation
        message is displayed. If an error occurs during the export process, an
        error message is shown.

        Raises:
            Exception: If an error occurs while writing to the CSV file.

        GUI Components:
            - QMessageBox: Used to display warnings, errors, and success messages.
            - QFileDialog: Used to prompt the user to select a file path.

        Preconditions:
            - The table widget (`self.tableWidget`) must be initialized and populated
              with data to export.

        Postconditions:
            - A CSV file is created at the specified path containing the table's data.

        """
        if not self.tableWidget or self.tableWidget.rowCount() == 0:
            QMessageBox.warning(self, "Export Failed", "No data available to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv)")
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    headers = [self.tableWidget.horizontalHeaderItem(col).text() for col in range(self.tableWidget.columnCount())]
                    writer.writerow(headers)
                    for row in range(self.tableWidget.rowCount()):
                        writer.writerow([
                            self.tableWidget.item(row, col).text()
                            for col in range(self.tableWidget.columnCount())
                        ])
                QMessageBox.information(self, "Export Successful", f"Logs exported to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export CSV:\n{e}")

    # ----------------------------------------------------------------------------------------------------
    # Add the username to the layout
    # ----------------------------------------------------------------------------------------------------
    def print_table(self):
        QMessageBox.information(self, "Print", "Print functionality is not implemented yet.")

    # ----------------------------------------------------------------------------------------------------  
    # Add the username to the layout
    # ----------------------------------------------------------------------------------------------------
    def add_username(self):
        """
        Updates the GUI to display the current user's username.

        This method retrieves the current system username using `os.getlogin()` 
        and updates a QLabel widget in the GUI with the username. The label is 
        styled with specific font, alignment, size, and appearance properties.

        If the QLabel with the object name "usernameLabel" is not found, an 
        error is logged and the method exits without making any changes.

        Styling applied to the QLabel includes:
        - Font: Arial, size 10, bold
        - Alignment: Centered
        - Size policy: Expanding horizontally, fixed vertically
        - Minimum width: 100 pixels
        - Cursor: Pointing hand cursor
        - Background color: #3a86ff (blue)
        - Text color: White
        - Border radius: 6 pixels
        - Font weight: 600

        Raises:
            None

        Logs:
            - Logs an error if the QLabel "usernameLabel" is not found.

        Returns:
            None
        """
        current_user    = os.getlogin()
        username_label  = self.ui.findChild(QLabel, "usernameLabel")
        if not username_label:
            logging.error("username_label not found")
            return
        username_label.setText(f"{current_user}")
        username_label.setFont(QFont("Arial", 10, QFont.Bold))
        username_label.setAlignment(Qt.AlignCenter)
        username_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        username_label.setMinimumWidth(100)
        username_label.setCursor(Qt.PointingHandCursor)
        username_label.setStyleSheet("background-color: #3a86ff; color: white; border-radius: 6px; font-weight: 600;")
        
    # ----------------------------------------------------------------------------------------------------
    # change_theme method to change the theme of the GUI
    # ----------------------------------------------------------------------------------------------------
    def change_theme(self, theme_name):
        """
        Changes the application's theme by applying the specified stylesheet and palette.

        Args:
            theme_name (str): The name of the theme to apply. If "Light", a light theme is used; 
                              otherwise, a dark theme is applied.

        Behavior:
            - Updates the application's stylesheet using the `themes` dictionary.
            - Sets the palette to white for the "Light" theme or black for other themes.
            - Enables auto-fill background for the application.
        """
        self.setStyleSheet(themes.get(theme_name, default_stylesheet))
        self.ui.setStyleSheet(themes.get(theme_name, default_stylesheet))
        self.setPalette(QPalette(QColor(255, 255, 255) if theme_name == "Light" else QColor(1, 1, 1)))
        self.setAutoFillBackground(True)

    # ----------------------------------------------------------------------------------------------------
    # add _icon_to_layout method to add the user icon to the layout
    # ----------------------------------------------------------------------------------------------------
    def add_icon_to_layout(self):
        """
        Adds an icon to a specified QVBoxLayout in the user interface.

        This method searches for a QVBoxLayout named "IconVLay" in the UI. If the layout
        is found, it creates a QLabel and attempts to load a QPixmap from the specified
        `icon_path`. If the pixmap is successfully loaded, it is scaled to 64x64 pixels
        while maintaining its aspect ratio, and added to the layout. If the pixmap cannot
        be loaded, a QLabel with an error message is added to the layout instead.

        The QLabel is configured with the following properties:
        - Alignment: Centered
        - Size policy: Expanding in both horizontal and vertical directions
        - Error message style: Red text with bold font (if the icon is not found)

        Attributes:
            None

        Parameters:
            None

        Returns:
            None
        """
        layout = self.ui.findChild(QVBoxLayout, "IconVLay")
        if layout:
            label = QLabel(self)
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio))
                label.setAlignment(Qt.AlignCenter)
                label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                layout.addWidget(label)
            else:
                label.setText("Icon not found")
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("color: red; font-weight: bold;")
                layout.addWidget(label)

    # ----------------------------------------------------------------------------------------------------
    # load_summary_panel method to load the summary panel
    # ----------------------------------------------------------------------------------------------------
    def load_summary_panel(self):
        """
        Loads and initializes the summary panel in the user interface.
        This method builds the path to the UI file for the collapsible tab, initializes
        the tab with the summary information, and populates it with data retrieved from
        the `_summary_month_info` object. The summary panel is added to the "InformationPanel"
        layout in the main UI.
        Raises:
            [ERROR]: Logs an error message if the "InformationPanel" layout is not found.
        Summary Fields Populated:
            - day_month_LD: Total number of workdays in the month.
            - holidays_month_LD: Number of holidays in the month.
            - total_work_days_LD: Total number of working days in the month (excluding holidays).
            - active_hours_LD: Total active time for the current month.
            - inactive_days_LD: Total inactive time for the current month.
            - Active_LD: Total active time for the current day.
            - Inactive_LD: Total inactive time for the current day.
        """
        # === Build full path to UI file ===
        collapse_ui_path = os.path.join(os.path.dirname(script_path), "ui/collapse.ui")

        # === Initialize CollapsibleTab, collapsed by default ===
        summary = CollapsibleTab("Summary", collapse_ui_path, start_collapsed=False)

        # === Find container layout in main UI ===
        layout = self.ui.findChild(QVBoxLayout, "InformationPanel")
        
        month_work_days                 = "22"
        holidays_in_month               = self._summary_month_info.get_number_of_holidays()
        _work_days_in_month             = int(month_work_days) - int(holidays_in_month)
        total_active_time_this_month    = self._summary_month_info.get_total_active_time()
        total_inactive_time_this_month  = self._summary_month_info.get_total_inactive_time()
                
        total_active_time_today         = self._summary_month_info.get_total_active_time_off_today()
        total_inactive_time_today       = self._summary_month_info.get_total_inactive_time_off_today()
        
        if layout:
            layout.addWidget(summary)

            # === Populate fields after loading ===
            summary.set_values({
                "day_month_LD"          : str(month_work_days),
                "holidays_month_LD"     : str(holidays_in_month),
                "total_work_days_LD"    : str(_work_days_in_month),
                "active_hours_LD"       : str(total_active_time_this_month),
                "inactive_days_LD"      : str(total_inactive_time_this_month),
                "Active_LD"             : str(total_active_time_today),
                "Inactive_LD"           : str(total_inactive_time_today)
            })

        else:
            print("[ERROR] Could not find 'InformationPanel' layout in UI.")

    # ----------------------------------------------------------------------------------------------------
    # add_date_selectors method to add date selectors and filter buttons
    # ----------------------------------------------------------------------------------------------------
    def add_date_selectors(self):
        """
        Adds a collapsible date filter section to the GUI, allowing users to filter logs
        by start and end dates, select log types, and change the application theme.
        The method performs the following:
        - Creates a toggle button to expand/collapse the filter section.
        - Adds date selectors (start and end dates) with calendar popups.
        - Includes radio buttons to select log types (Pulse or Summaries).
        - Provides a search button to trigger log filtering.
        - Adds a theme selector dropdown at the bottom of the layout.
        Components:
        - `date_toggle_btn`: A toggle button to show/hide the filter section.
        - `date_section_widget`: A collapsible container for the filter section.
        - `start_date_edit`: A date selector for the start date.
        - `end_date_edit`: A date selector for the end date.
        - `search_btn`: A button to initiate the log search.
        - `radio_log_pulse`: A radio button to select "Pulse" logs.
        - `radio_log_summary`: A radio button to select "Summaries" logs.
        - `theme_selector`: A dropdown to select the application theme.
        Notes:
        - The filter section starts collapsed by default.
        - The theme selector is always visible at the bottom of the layout.
        - Logs an error if the parent layout (`SeachLogVLay`) is not found.
        """
        layout = self.ui.findChild(QVBoxLayout, "SeachLogVLay")
        if not layout:
            logging.error("SeachLogVLay not found")
            return

        label_font = QFont("Arial", 10)
        label_font.setBold(True)

        # === Toggle Button ===
        self.date_toggle_btn = QPushButton("▶ Filters")
        self.date_toggle_btn.setCheckable(True)
        self.date_toggle_btn.setChecked(False)
        self.date_toggle_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                text-align: left;
                padding: 6px;
                font-size: 12px;
                color: #f0b429;
                border: none;
            }
        """)
        layout.addWidget(self.date_toggle_btn)
        self.date_toggle_btn.clicked.connect(self.toggle_date_section)

        # === Filter Section Container ===
        self.date_section_widget = QWidget()
        filter_layout = QVBoxLayout(self.date_section_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)

        # === Filter Widgets ===
        self.start_date_edit    = QDateEdit()
        self.end_date_edit      = QDateEdit()
        self.search_btn         = QPushButton("Search Logs")
        self.radio_log_pulse    = QRadioButton("Pulse")
        self.radio_log_summary  = QRadioButton("Summaries")

        self.start_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setDate(QDate.currentDate())

        self.radio_log_pulse.setChecked(True)

        for widget in [self.start_date_edit, self.end_date_edit]:
            widget.setCalendarPopup(True)
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            widget.setMinimumWidth(50)

        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.setMinimumHeight(30)

        self.start_label = QLabel("Start Date:")
        self.end_label   = QLabel("End Date:")
        for label in [self.start_label, self.end_label]:
            label.setFont(label_font)
            label.setStyleSheet("padding-top: 10px;")

        def wrap(widget):
            wrapper = QWidget()
            wrapper_layout = QVBoxLayout(wrapper)
            wrapper_layout.addWidget(widget)
            wrapper_layout.setContentsMargins(0, 0, 0, 0)
            return wrapper

        # === Add Filter Widgets to Layout ===
        filter_layout.addWidget(self.start_label)
        filter_layout.addWidget(wrap(self.start_date_edit))
        filter_layout.addWidget(self.end_label)
        filter_layout.addWidget(wrap(self.end_date_edit))

        radio_layout = QVBoxLayout()
        radio_layout.addWidget(self.radio_log_pulse)
        radio_layout.addWidget(self.radio_log_summary)
        radio_widget = QWidget()
        radio_widget.setLayout(radio_layout)
        filter_layout.addWidget(radio_widget)

        filter_layout.addWidget(wrap(self.search_btn))

        # === Add Collapsible Section to Main Layout ===
        layout.addWidget(self.date_section_widget)
        layout.addStretch(1)
        
        # === Theme selector (ALWAYS visible at bottom) ===
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(themes.keys())
        self.theme_selector.setCurrentText("Dark")
        self.theme_selector.currentTextChanged.connect(self.change_theme)
        self.theme_selector.setFixedHeight(35)
        self.theme_selector.setStyleSheet("font-size: 12px;")

        layout.addWidget(self.theme_selector)  # <- At the bottom

        # === Start Collapsed ===
        self.date_section_widget.setVisible(False)
        self.date_toggle_btn.setChecked(False)
        self.date_toggle_btn.setText("▶ Filters")

    # ----------------------------------------------------------------------------------------------------
    # toggle the visibility of the date section and adjust the button text
    # ----------------------------------------------------------------------------------------------------
    def toggle_date_section(self):
        """
        Toggles the visibility of the date section in the GUI.
        This method is triggered when the date toggle button is clicked. It updates
        the visibility of the date section widget, changes the button text to indicate
        the current state, and adjusts the size of the GUI window accordingly.
        Actions performed:
        - Checks the state of the toggle button (checked or unchecked).
        - Shows or hides the date section widget based on the button state.
        - Updates the toggle button text to reflect the current state.
        - Resizes the GUI window to fit the content.
        Prints:
            A message indicating whether the toggle button is checked or not.
        Resizes:
            - Expands the GUI to 350x900 when the date section is visible.
            - Shrinks the GUI to 350x600 when the date section is hidden.
        """
        is_checked = self.date_toggle_btn.isChecked()
        self.date_section_widget.setVisible(is_checked)
        self.date_toggle_btn.setText("▼ Filters" if is_checked else "▶ Filters")
        
        print(f"Toggle button clicked: {is_checked}")
        # Resize the GUI to fit the content
        
        if is_checked is True:
            self.resize(350, 900)
        else:
            self.resize(350, 600)
            # self.resize(350, 600)  # Reset to original size
    
    # ----------------------------------------------------------------------------------------------------
    # Connect the search button to the search function
    # ----------------------------------------------------------------------------------------------------
    def connection(self):
        self.search_btn.clicked.connect(self.on_search_clicked)

    # ----------------------------------------------------------------------------------------------------
    # Setup the table widget and its properties
    # ----------------------------------------------------------------------------------------------------
    def setup_table(self):
        """
        Sets up the QTableWidget with predefined configurations.
        This method initializes the table widget by setting its column count,
        header labels, row count, and various display properties. It also ensures
        that the table widget is configured for single-row selection and disables
        editing. Additionally, it adjusts the column widths to stretch evenly.
        If the table widget is not found in the UI, a warning is logged, and the
        method exits without making any changes.
        Attributes Configured:
            - Column count: 4
            - Header labels: ["TimeStamp", "ActiveTime", "InactiveTime", "Status"]
            - Alternating row colors: Enabled
            - Selection behavior: Row-based
            - Selection mode: Single selection
            - Edit triggers: Disabled
            - Grid display: Enabled
            - Column resize mode: Stretch for all columns
        Logs:
            - Logs a warning if the table widget is not found in the UI.
        """
        self.tableWidget = self.ui.findChild(QTableWidget, "tableWidget")
        if not self.tableWidget:
            logging.warning("Table widget not found.")
            return

        header = self.tableWidget.horizontalHeader()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels([
            "TimeStamp", "ActiveTime", "InactiveTime", "Status"
        ])
        self.tableWidget.setRowCount(0)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget.setSelectionMode(QTableWidget.SingleSelection)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setShowGrid(True)

        for col in range(4):
            header.setSectionResizeMode(col, QHeaderView.Stretch)

    # ----------------------------------------------------------------------------------------------------
    # Search button clicked event handler
    # ----------------------------------------------------------------------------------------------------
    def on_search_clicked(self):
        """
        Handles the search button click event to fetch and display logs within the specified date range.
        This method retrieves the start and end dates from the GUI date pickers, converts them to datetime
        objects, and queries the database for logs within the specified range. Depending on the selected
        radio button, it either fetches a summary of logs or detailed pulse data. The results are then
        displayed in a table and the GUI is resized to fit the content.
        Raises:
            Exception: If there is an error while querying the database, a critical message box is displayed
                       and the error is logged.
        Notes:
            - The method assumes the existence of `GetPulseData` class with `get_summary_logs` and 
              `get_pulse_data` methods.
            - The `TimeSummary.summarize` method is used to generate a summary panel from the table data.
            - The GUI is resized to specific dimensions after populating the table.
        """
        start = self.start_date_edit.date().toPython()
        end = self.end_date_edit.date().toPython()

        start_datetime = datetime.combine(start, datetime.min.time())
        end_datetime = datetime.combine(end, datetime.max.time())

        logging.info(f"Searching logs from {start_datetime} to {end_datetime}")

        try:
            ac = GetPulseData()

            if self.radio_log_summary.isChecked():
                results = ac.get_summary_logs(start_datetime, end_datetime)  #Add this method if needed
            else:
                results = ac.get_pulse_data(start_datetime, end_datetime)

            table_data = [
                (
                    doc["timestamp"],
                    doc.get("active_time", ""),
                    doc.get("inactive_time", ""),
                    doc.get("status", "")
                )
                for doc in results
            ]

            self._summary_panel = TimeSummary.summarize(table_data)
            self.populate_table(table_data)
            
            # resize Gui to fit the content
            self.resize(1100, 900)
            self.ui.splitterMain.setSizes([350, 750]) 

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to fetch logs:\n{e}")
            logging.error("MongoDB query failed: %s", e)
    
    # ----------------------------------------------------------------------------------------------------
    # Populate the table with data
    # ----------------------------------------------------------------------------------------------------        
    def populate_table(self, data):
        """
        Populates the table widget with the provided data.
        Args:
            data (list of list): A list of rows, where each row is a list of values 
                                 representing the data to be displayed in the table.
        Behavior:
            - Sets the number of rows in the table to match the length of the data.
            - Iterates through the data to populate each cell in the table.
            - Aligns the text in each cell to the center.
            - (Commented out) Optionally sets the background and foreground colors 
              of the cells based on the "status" value in the data.
            - Calls `add_summary_panel` after populating the table.
        """
        self.tableWidget.setRowCount(len(data))
        active_color    = QColor("#24ff92")
        inactive_color  = QColor("#cd6155")

        for row_idx, row_data in enumerate(data):
            status = str(row_data[3]).lower()

            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)

                # if status == "active":
                #     # item.setBackground(active_color)
                #     # item.setForeground(Qt.black)
                # elif status == "inactive":
                #     item.setBackground(inactive_color)
                #     item.setForeground(Qt.white)

                self.tableWidget.setItem(row_idx, col_idx, item)
                
        self.add_summary_panel()

    # ----------------------------------------------------------------------------------------------------
    # Add summary panel to the layout
    # ----------------------------------------------------------------------------------------------------
    def add_summary_panel(self):
        """
        Populates a summary panel in the GUI with user and session information.
        This method retrieves data such as the user's login name, hostname, 
        session start and end dates, and activity times, and populates corresponding 
        QLineEdit widgets in the GUI. The populated fields are set to read-only.
        Fields populated:
            - userName_LD: The login name of the current user.
            - hostName_LD: The hostname of the machine.
            - startDate_LD: The session start date in "YYYY-MM-DD" format.
            - endDate_LD: The session end date in "YYYY-MM-DD" format.
            - activeTime_LD: The total active time during the session.
            - inactiveTime_LD: The total inactive time during the session.
            - totalTime_LD: The total time of the session.
        Notes:
            - The method assumes that the QLineEdit widgets in the GUI are named 
              according to the keys in the `fields` dictionary.
            - If a widget corresponding to a field is not found, it is skipped.
        Raises:
            AttributeError: If `self.start_date_edit` or `self.end_date_edit` 
                            does not have a `date()` method.
            KeyError: If `self._summary_panel` does not contain the required keys.
        """
        start = self.start_date_edit.date().toPython()
        end = self.end_date_edit.date().toPython()

        fields = {
            "userName_LD"       : os.getlogin(),
            "hostName_LD"       : socket.gethostname(),
            "startDate_LD"      : start.strftime("%Y-%m-%d"),
            "endDate_LD"        : end.strftime("%Y-%m-%d"),
            "activeTime_LD"     : self._summary_panel["active"],
            "inactiveTime_LD"   : self._summary_panel["inactive"],
            "totalTime_LD"      : self._summary_panel["total"]
        }

        for obj_name, value in fields.items():
            widget = self.ui.findChild(QLineEdit, obj_name)
            if widget:
                widget.setText(value)
                widget.setReadOnly(True)
                

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = UserGUI()
    gui.show()
    sys.exit(app.exec_())
