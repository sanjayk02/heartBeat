import os
from PySide2.QtWidgets import (
    QFrame, QVBoxLayout, QPushButton, QWidget, QLineEdit
)
from PySide2.QtCore import QFile, QIODevice
from PySide2.QtUiTools import QUiLoader


class CollapsibleTab(QFrame):
    def __init__(self, title, ui_path, start_collapsed=False, parent=None):
        super().__init__(parent)

        self.title = title
        self._loaded_widget = None  # strong reference

        # Frame style
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(1)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)

        # Header toggle button
        self.header_btn = QPushButton(f"{'►' if start_collapsed else '▼'} {title}")
        self.header_btn.setCheckable(True)
        self.header_btn.setChecked(not start_collapsed)
        self.header_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                text-align: left;
                padding: 6px;
                font-size: 12px;
                color: #f0b429;
                border: none;
            }
        """)
        self.header_btn.clicked.connect(self.toggle)

        # Placeholder in case loading fails
        self.content_area = QWidget()

        # Load the actual content from .ui
        loaded_widget = self.load_ui(ui_path)
        if loaded_widget:
            self.content_area = loaded_widget
            self._loaded_widget = loaded_widget  # Strong reference

        self.main_layout.addWidget(self.header_btn)
        self.main_layout.addWidget(self.content_area)

        # Apply initial collapsed state
        self.content_area.setVisible(not start_collapsed)

    def load_ui(self, ui_path):
        loader = QUiLoader()
        file = QFile(ui_path)

        if not file.open(QIODevice.ReadOnly):
            print(f"[ERROR] Could not open UI file: {ui_path}")
            return QWidget()

        ui_widget = loader.load(file, None)
        file.close()

        if not ui_widget:
            print("[ERROR] UI loader returned None.")
            return QWidget()

        # Wrap UI in a container for better layout control
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(ui_widget)

        # Keep references to avoid garbage collection
        self._loaded_widget = ui_widget
        self._container = container

        return container

    def toggle(self):
        is_open = self.header_btn.isChecked()
        self.content_area.setVisible(is_open)
        icon = "▼" if is_open else "►"
        self.header_btn.setText(f"{icon} {self.title}")
        print(f"CollapsibleTab: '{self.title}' {'opened' if is_open else 'collapsed'}")

    def get_field(self, object_name, widget_type=QLineEdit):
        """Finds and returns a child widget by object name and type."""
        if not self.content_area:
            print("content_area is None or deleted")
            return None
        return self.content_area.findChild(widget_type, object_name)

    def set_value(self, object_name, text):
        """Set the text of a QLineEdit (or similar) and make it read-only."""
        field = self.get_field(object_name)
        if field:
            field.setText(text)
            field.setReadOnly(True)
        else:
            print(f"[WARN] Field '{object_name}' not found.")

    def set_values(self, values: dict):
        """Set multiple fields by object name using a dictionary."""
        for object_name, value in values.items():
            self.set_value(object_name, value)
