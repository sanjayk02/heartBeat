from PySide2.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QLabel
)

class SummaryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        form = QFormLayout()

        self.username = QLineEdit("Sanja")
        self.hostname = QLineEdit("PIPe")

        self.start_date = QLineEdit("2025-03-01")
        self.end_date = QLineEdit("2025-03-30")

        self.active_hours = QLineEdit("0h 0m")
        self.inactive_hours = QLineEdit("0h 0m")
        self.total_hours = QLineEdit("0h 0m")

        # Make all fields read-only
        for field in [
            self.username, self.hostname,
            self.start_date, self.end_date,
            self.active_hours, self.inactive_hours,
            self.total_hours
        ]:
            field.setReadOnly(True)

        form.addRow("Username:", self.username)
        form.addRow("Hostname:", self.hostname)
        form.addRow("Start Date:", self.start_date)
        form.addRow("End Date:", self.end_date)
        form.addRow("Active Hours:", self.active_hours)
        form.addRow("Inactive Hours:", self.inactive_hours)
        form.addRow("Total Work:", self.total_hours)

        self.setLayout(form)

# Example usage in UserGUI
# In your UserGUI.__init__ or setup method:

# self.summary_panel = SummaryPanel()
# some_layout.addWidget(self.summary_panel)

# Then in your on_search_clicked after summary is calculated:
# summary = TimeSummary.summarize(table_data)
# self.summary_panel.active_hours.setText(summary["active"])
# self.summary_panel.inactive_hours.setText(summary["inactive"])
# self.summary_panel.total_hours.setText(summary["total"])
