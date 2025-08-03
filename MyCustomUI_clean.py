import os
import sys
import json
import importlib
import glob

import maya.OpenMayaUI as omui
import maya.cmds as cmds

# -------------------------------------------------------------------------------------------------
# Qt imports (module-style for PySide2/6 compatibility)
# -------------------------------------------------------------------------------------------------
try:
    from PySide6 import QtWidgets, QtCore, QtGui, QtUiTools
    from PySide6.QtCore import QFile
    from shiboken6 import wrapInstance
    using_pyside_version = 6
except ImportError:
    try:
        from PySide2 import QtWidgets, QtCore, QtGui, QtUiTools
        from PySide2.QtCore import QFile
        from shiboken2 import wrapInstance
        using_pyside_version = 2
    except ImportError:
        cmds.error("Neither PySide6 nor PySide2 could be imported. Please check your Maya version and Python environment.")

# -------------------------------------------------------------------------------------------------
# Custom Imports / Paths
# -------------------------------------------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
_root = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.insert(0, script_dir)
sys.path.insert(0, _root)

ui_path = os.path.join(os.path.dirname(script_dir), "gui/ui/mainUI.ui")
config_path = os.path.join(_root, "config/config.json").replace("\", "/")
icon_path = os.path.join(os.path.dirname(_root), "resources/icons/user_icon.png").replace("\", "/")

from gui import utils
importlib.reload(utils)

# Optional project root (unused here but kept if needed elsewhere)
PROJECTSET = os.environ.get("PPI_PROJECT_ROOT")

# -------------------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------------------

def read_config_values():
    """Load config.json and return a dict. Supports either a dict or list-of-dicts file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, 'r') as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data
    merged = {}
    if isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict):
                merged.update(entry)
    return merged


def get_project_path(cfg):
    """Return project path with backward-compatible key fallback."""
    return cfg.get("PROJECT_PATH") or cfg.get("PROIJECT_PATH", "")


def _revision_sort_key(s):
    """Sort by numeric value if possible, otherwise fall back to string."""
    try:
        return int(s)
    except Exception:
        return s


# =================================================================================================
# Main UI
# =================================================================================================
class MyCustomUI(QtWidgets.QDialog):
    WINDOW_NAME = "MyCustomUIWindow"

    # ---------------------------------------------------------------------------------------------
    def __init__(self, ui_file_path, parent=None):
        super(MyCustomUI, self).__init__(parent or self.get_maya_main_window())

        self.setObjectName(self.WINDOW_NAME)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("My Custom UI")
        self.resize(1200, 600)
        self.setWindowFlags(
            QtCore.Qt.Window
            | QtCore.Qt.WindowMinimizeButtonHint
            | QtCore.Qt.WindowMaximizeButtonHint
            | QtCore.Qt.WindowCloseButtonHint
        )

        # Load .ui file
        self.ui = self.load_ui(ui_file_path, self)
        self.ui.listWidget_asset.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # Layout and embed
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        table = self.ui.table
        table.setAcceptDrops(True)
        table.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
        table.dragEnterEvent = self._handle_drag_enter
        table.dropEvent = self._handle_drop_event
        table.setWordWrap(False)

        # Apply StyleSheet
        self.setStyleSheet(
            """
            QDialog {
                background-color: #2e2e2e;
                color: white;
                font-family: Arial;
                font-size: 12px;
            }

            QPushButton {
                background-color: #444;
                color: white;
                padding: 6px 10px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #555; }

            QLineEdit, QComboBox {
                background-color: #3a3a3a;
                border: 1px solid #666;
                padding: 4px;
                color: white;
            }

            QLabel { color: #dddddd; }

            QTableView {
                background-color: #3b3b3b;
                gridline-color: #666;
            }
            """
        )

        # Optional UI adjustments
        if hasattr(self.ui, "splitterMain"):
            self.ui.splitterMain.setSizes([150, 1050])

        self.add_menu_bar()
        self._add_type()
        self.connection()

    # ---------------------------------------------------------------------------------------------
    @classmethod
    def get_maya_main_window(cls):
        ptr = omui.MQtUtil.mainWindow()
        if ptr is not None:
            return wrapInstance(int(ptr), QtWidgets.QWidget)

    # ---------------------------------------------------------------------------------------------
    @classmethod
    def load_ui(cls, ui_file_path, parent=None):
        loader = QtUiTools.QUiLoader()
        ui_file = QFile(ui_file_path)
        if not ui_file.open(QFile.ReadOnly):
            raise IOError("Failed to open .ui file: " + ui_file_path)
        ui = loader.load(ui_file, parent)
        ui_file.close()
        return ui

    # ---------------------------------------------------------------------------------------------
    @classmethod
    def delete_existing(cls):
        for widget in QtWidgets.QApplication.allWidgets():
            if widget.objectName() == cls.WINDOW_NAME:
                widget.close()
                widget.deleteLater()

    # ---------------------------------------------------------------------------------------------
    def add_menu_bar(self):
        menu_bar = QtWidgets.QMenuBar(self)

        file_menu = menu_bar.addMenu("File")
        export_action = file_menu.addAction("Export to CSV")
        export_action.setShortcut("Ctrl+E")
        # export_action.triggered.connect(self.export_to_csv)

        print_action = file_menu.addAction("Print")
        print_action.setShortcut("Ctrl+P")
        # print_action.triggered.connect(self.print_table)

        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        view_menu = menu_bar.addMenu("View")
        refresh_action = view_menu.addAction("Refresh Logs")
        refresh_action.setShortcut("Ctrl+R")
        # refresh_action.triggered.connect(self.on_search_clicked)

        toggle_filters_action = view_menu.addAction("Toggle Filters")
        toggle_filters_action.setShortcut("Ctrl+F")
        # toggle_filters_action.triggered.connect(self.date_toggle_btn.click)

        help_menu = menu_bar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about_dialog)

        self.layout().setMenuBar(menu_bar)

    # ---------------------------------------------------------------------------------------------
    def show_about_dialog(self):
        QtWidgets.QMessageBox.information(
            self,
            "About Heart Beat",
            "Heart Beat

A productivity tracking tool.
Version 1.0

Created by You",
        )

    # ---------------------------------------------------------------------------------------------
    def show_ui(self):
        self.show()

    # ---------------------------------------------------------------------------------------------
    def on_my_button_clicked(self):
        print("Button clicked!")

    # ---------------------------------------------------------------------------------------------
    def connection(self):
        self.ui.listWidget_type.itemClicked.connect(self._add_name)
        self.ui.listWidget_name.itemClicked.connect(self._add_asset)
        self.ui.listWidget_asset.itemSelectionChanged.connect(self._get_reversion_selected_item)
        self.ui.Add_list_btn.clicked.connect(self._add_selectItem_tableWidget)

    # ---------------------------------------------------------------------------------------------
    def _add_type(self):
        try:
            config_data = read_config_values()
            project_path = get_project_path(config_data)
            if not project_path:
                print("'PROJECT_PATH' missing in config (or legacy 'PROIJECT_PATH').")
                return

            folders = utils.get_all_folders(project_path)
            self.ui.listWidget_type.clear()
            for folder_name in folders:
                self.ui.listWidget_type.addItem(folder_name)
        except Exception as e:
            print("Error in _add_type:", str(e))

    # ---------------------------------------------------------------------------------------------
    def _add_name(self):
        selected_items = self.ui.listWidget_type.selectedItems()
        if not selected_items:
            print("No folder selected.")
            return

        config_data = read_config_values()
        project_path = get_project_path(config_data)

        _name = []
        for item in selected_items:
            folder_name = item.text()
            full_path = os.path.join(project_path, folder_name)
            subfolders = utils.get_all_folders(full_path)
            _name.extend(subfolders)

        self.ui.listWidget_name.clear()
        for folder_name in _name:
            self.ui.listWidget_name.addItem(folder_name)

    # ---------------------------------------------------------------------------------------------
    def _add_asset(self):
        selected_type_items = self.ui.listWidget_type.selectedItems()
        if not selected_type_items:
            print("No type folder selected.")
            return

        selected_name_items = self.ui.listWidget_name.selectedItems()
        if not selected_name_items:
            print("No name folder selected.")
            return

        config_data = read_config_values()
        project_path = get_project_path(config_data)

        _asset = []
        for type_item in selected_type_items:
            type_name = type_item.text()
            for name_item in selected_name_items:
                asset_name = name_item.text()
                full_path = os.path.join(project_path, type_name, asset_name)
                subfolders = utils.get_all_folders(full_path)
                _asset.extend(subfolders)

        self.ui.listWidget_asset.clear()
        for folder_name in _asset:
            self.ui.listWidget_asset.addItem(folder_name)

        if self.ui.listWidget_asset.count() > 0:
            self.ui.listWidget_asset.setCurrentRow(0)

        self._add_phase()
        self._add_variation()

    # ---------------------------------------------------------------------------------------------
    def _add_phase(self):
        config_data = read_config_values()
        phase = config_data.get("PHASE", [])
        self.ui.listWidget_phase.clear()
        for phas in phase:
            self.ui.listWidget_phase.addItem(phas)
        if self.ui.listWidget_phase.count() > 0:
            self.ui.listWidget_phase.setCurrentRow(0)

    # ---------------------------------------------------------------------------------------------
    def _add_variation(self):
        config_data = read_config_values()
        variation = config_data.get("VARIATION", [])
        self.ui.listWidget_variation.clear()
        for vari in variation:
            self.ui.listWidget_variation.addItem(vari)
        if self.ui.listWidget_variation.count() > 0:
            self.ui.listWidget_variation.setCurrentRow(0)

    # ---------------------------------------------------------------------------------------------
    def _get_selected_all_item(self):
        selected_type_items = self.ui.listWidget_type.selectedItems()
        selected_name_items = self.ui.listWidget_name.selectedItems()
        selected_asset_items = self.ui.listWidget_asset.selectedItems()
        selected_phase_items = self.ui.listWidget_phase.selectedItems()
        selected_varaition_items = self.ui.listWidget_variation.selectedItems()

        if not all([selected_type_items, selected_name_items, selected_asset_items, selected_phase_items, selected_varaition_items]):
            print(" Please select all required fields: type, name, asset, phase, and variation.")
            return

        selected_data = {
            "type": [i.text() for i in selected_type_items],
            "name": [i.text() for i in selected_name_items],
            "asset": [i.text() for i in selected_asset_items],
            "phase": [i.text() for i in selected_phase_items],
            "variation": [i.text() for i in selected_varaition_items],
        }
        return selected_data

    # ---------------------------------------------------------------------------------------------
    def _get_reversion_selected_item(self):
        _selected_data = self._get_selected_all_item()
        if not _selected_data:
            return

        _sel_type = _selected_data.get("type", [])
        _sel_name = _selected_data.get("name", [])
        _sel_asset = _selected_data.get("asset", [])
        _sel_phase = _selected_data.get("phase", [])
        _sel_variation = _selected_data.get("variation", [])

        config_data = read_config_values()
        project_path = get_project_path(config_data)

        if not (_sel_type and _sel_name and _sel_asset and _sel_phase and _sel_variation):
            print("One or more required selections are missing.")
            return

        if len(_sel_asset) == 1:
            full_path = os.path.join(
                project_path,
                _sel_type[0],
                _sel_name[0],
                _sel_asset[0],
                _sel_phase[0],
                _sel_variation[0],
                "r",
            )
            rev_folders = utils.get_all_folders(full_path)
            rev_folders.sort(key=_revision_sort_key, reverse=True)

            if hasattr(self.ui, "comboBox_reversion"):
                self.ui.comboBox_reversion.clear()
                self.ui.comboBox_reversion.addItems(rev_folders)

    # ---------------------------------------------------------------------------------------------
    def find_maya_file(self, mamdl_path):
        """Find the most relevant maya file in MAMDL: newest, preferring .ma."""
        if not os.path.exists(mamdl_path):
            return None
        candidates = []
        for pattern in ("*.ma", "*.mb"):
            candidates.extend(glob.glob(os.path.join(mamdl_path, pattern)))
        if not candidates:
            return None
        # newest first
        try:
            candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        except Exception:
            pass
        # prefer .ma
        candidates.sort(key=lambda p: (os.path.splitext(p)[1].lower() != ".ma"))
        return candidates[0]

    # ---------------------------------------------------------------------------------------------
    def update_row_asset_path(self, row):
        base_item = self.ui.table.item(row, 0)
        if not base_item:
            return

        base_path = base_item.data(QtCore.Qt.UserRole)
        if not base_path:
            print("No original base path stored.")
            return

        combo = self.ui.table.cellWidget(row, 4)
        revision = combo.currentText() if combo else ""
        mamdl_path = os.path.normpath(os.path.join(base_path, "r", revision, "MAMDL"))

        maya_file = self.find_maya_file(mamdl_path)

        # Set ASSET_PATH column (keep base path in UserRole for dedupe)
        new_text = maya_file if maya_file else base_path
        new_item = QtWidgets.QTableWidgetItem(new_text)
        new_item.setData(QtCore.Qt.UserRole, base_path)
        new_item.setTextAlignment(QtCore.Qt.AlignLeft)
        new_item.setToolTip(new_text)
        self.ui.table.setItem(row, 0, new_item)

        if maya_file:
            print(f"[✓] Found asset: {maya_file}")
            for col in range(self.ui.table.columnCount()):
                item = self.ui.table.item(row, col)
                if item:
                    item.setBackground(QtGui.QBrush())  # reset to default
                    item.setForeground(QtGui.QBrush())
            result_item = self.ui.table.item(row, 5)
            if result_item:
                result_item.setText("Ready")
                result_item.setForeground(QtGui.QBrush(QtGui.QColor("orange")))
                result_item.setBackground(QtGui.QBrush(QtGui.QColor("transparent")))
        else:
            print(f"[✗] No .ma/.mb in: {mamdl_path}")
            for col in range(self.ui.table.columnCount()):
                item = self.ui.table.item(row, col)
                if item is None:
                    item = QtWidgets.QTableWidgetItem("")
                    self.ui.table.setItem(row, col, item)
                item.setBackground(QtGui.QColor("#661111"))
                item.setForeground(QtGui.QColor("white"))
            result_item = self.ui.table.item(row, 5)
            if result_item:
                result_item.setText("Asset Not Found")
                result_item.setForeground(QtGui.QBrush(QtGui.QColor("white")))
                result_item.setBackground(QtGui.QBrush(QtGui.QColor("#661111")))

    # ---------------------------------------------------------------------------------------------
    def add_row_to_table(self, reference_path, type_, name, asset, revision, result):
        """Add a row; dedupe by stored base path in column 0 (UserRole)."""
        for r in range(self.ui.table.rowCount()):
            existing = self.ui.table.item(r, 0)
            if existing and existing.data(QtCore.Qt.UserRole) == reference_path:
                print(f"[!] Row for {reference_path} already exists. Skipping.")
                return

        row = self.ui.table.rowCount()
        self.ui.table.setColumnCount(6)
        self.ui.table.setHorizontalHeaderLabels(["ASSET_PATH", "TYPE", "NAME", "ASSET", "REVISION", "RESULT"])
        self.ui.table.insertRow(row)

        asset_item = QtWidgets.QTableWidgetItem(reference_path)
        asset_item.setData(QtCore.Qt.UserRole, reference_path)  # Store base path
        self.ui.table.setItem(row, 0, asset_item)

        self.ui.table.setItem(row, 1, QtWidgets.QTableWidgetItem(type_))
        self.ui.table.setItem(row, 2, QtWidgets.QTableWidgetItem(name))
        self.ui.table.setItem(row, 3, QtWidgets.QTableWidgetItem(asset))

        rev_dir = os.path.join(reference_path, "r")
        rev_folders = utils.get_all_folders(rev_dir) if os.path.exists(rev_dir) else []
        rev_folders.sort(key=_revision_sort_key, reverse=True)
        asset_missing = not rev_folders

        combo = QtWidgets.QComboBox()
        combo.setEditable(True)
        combo.addItems(rev_folders)
        combo.setCurrentText(revision if revision in rev_folders else (rev_folders[0] if rev_folders else ""))
        combo.setStyleSheet("QComboBox { qproperty-alignment: AlignCenter; }")
        combo.currentTextChanged.connect(lambda _, r=row: self.update_row_asset_path(r))
        self.ui.table.setCellWidget(row, 4, combo)

        result_text = "Asset Not Found" if asset_missing else result
        result_item = QtWidgets.QTableWidgetItem(result_text)
        result_item.setFont(QtGui.QFont("Arial", 10))
        result_item.setForeground(QtGui.QBrush(QtGui.QColor("white" if asset_missing else "orange")))
        result_item.setBackground(QtGui.QBrush(QtGui.QColor("#4d0000") if asset_missing else QtGui.QColor("transparent")))
        result_item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.ui.table.setItem(row, 5, result_item)

        if asset_missing:
            for col in range(6):
                item = self.ui.table.item(row, col)
                if item is None:
                    item = QtWidgets.QTableWidgetItem("")
                    self.ui.table.setItem(row, col, item)
                item.setBackground(QtGui.QColor("#4d0000"))
                item.setForeground(QtGui.QColor("white"))

        # Align NAME/TYPE/ASSET center; leave path left-aligned
        for col in [1, 2, 3]:
            item = self.ui.table.item(row, col)
            if item:
                item.setTextAlignment(QtCore.Qt.AlignCenter)

        # Column sizing
        header = self.ui.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.ui.table.setColumnWidth(0, 750)
        for i in range(1, self.ui.table.columnCount()):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        self.update_row_asset_path(row)

    # ---------------------------------------------------------------------------------------------
    def _is_duplicate_row(self, reference_path, asset_name, revision):
        for row in range(self.ui.table.rowCount()):
            base_item = self.ui.table.item(row, 0)
            if not base_item:
                continue
            base_path = base_item.data(QtCore.Qt.UserRole)
            asset_item = self.ui.table.item(row, 3)  # column 3 is ASSET
            combo = self.ui.table.cellWidget(row, 4)
            current_rev = combo.currentText() if combo else ""
            if base_path == reference_path and asset_item and asset_item.text() == asset_name and current_rev == revision:
                return True
        return False

    # ---------------------------------------------------------------------------------------------
    def _add_selectItem_tableWidget(self):
        _selected_data = self._get_selected_all_item()
        if not _selected_data:
            return

        _sel_type = _selected_data.get("type", [])
        _sel_name = _selected_data.get("name", [])
        _sel_asset = _selected_data.get("asset", [])
        _sel_phase = _selected_data.get("phase", [])
        _sel_variation = _selected_data.get("variation", [])

        config_data = read_config_values()
        project_path = get_project_path(config_data)

        if not (_sel_type and _sel_name and _sel_asset and _sel_phase and _sel_variation):
            print("Missing required selection.")
            return

        for asset in _sel_asset:
            full_path = os.path.join(
                project_path, _sel_type[0], _sel_name[0], asset, _sel_phase[0], _sel_variation[0]
            )
            self.add_row_to_table(
                reference_path=full_path,
                type_=_sel_type[0],
                name=_sel_name[0],
                asset=asset,
                revision="000",
                result="Pending",
            )

    # ---------------------------------------------------------------------------------------------
    # Drag & Drop
    # ---------------------------------------------------------------------------------------------
    def _handle_drag_enter(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def _handle_drop_event(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            if os.path.isdir(path):
                self._handle_folder_drop(path)
            elif path.lower().endswith((".ma", ".mb")):
                parent = os.path.dirname(path)
                self._handle_folder_drop(parent)
        event.acceptProposedAction()

    def _handle_folder_drop(self, folder_path):
        # Expect: .../TYPE/NAME/ASSET/PHASE/VARIATION
        parts = os.path.normpath(folder_path).split(os.sep)
        if len(parts) < 5:
            print(f"[!] Folder structure too shallow: {folder_path}")
            return
        variation = parts[-1]
        phase = parts[-2]
        asset = parts[-3]
        name = parts[-4]
        type_ = parts[-5]
        self.add_row_to_table(
            reference_path=folder_path,
            type_=type_,
            name=name,
            asset=asset,
            revision="000",
            result="Dropped",
        )


# -------------------------------------------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------------------------------------------

def main():
    ui_file_path = ui_path
    if not os.path.exists(ui_file_path):
        raise IOError(f"UI file not found: {ui_file_path}")
    MyCustomUI.delete_existing()
    win = MyCustomUI(ui_file_path)
    win.show_ui()


# if __name__ == "__main__":
#     main()
