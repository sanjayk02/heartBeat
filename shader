from PySide2 import QtWidgets, QtCore
import maya.cmds as cmds

class ShaderSwapUI(QtWidgets.QWidget):
    def __init__(self):
        super(ShaderSwapUI, self).__init__()
        self.setWindowTitle("Shader Swap Manager")
        self.setMinimumSize(400, 300)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.object_list = QtWidgets.QListWidget()
        self.layout.addWidget(self.object_list)

        self.old_shader_label = QtWidgets.QLabel("Old Shader: ")
        self.new_shader_label = QtWidgets.QLabel("New Shader: ")
        self.layout.addWidget(self.old_shader_label)
        self.layout.addWidget(self.new_shader_label)

        btn_layout = QtWidgets.QHBoxLayout()
        self.restore_btn = QtWidgets.QPushButton("⏪ Reassign Old Shader")
        self.reassign_btn = QtWidgets.QPushButton("🎨 Reassign New Shader")
        btn_layout.addWidget(self.restore_btn)
        btn_layout.addWidget(self.reassign_btn)
        self.layout.addLayout(btn_layout)

        self.restore_btn.clicked.connect(self.restore_old)
        self.reassign_btn.clicked.connect(self.assign_new)
        self.object_list.itemSelectionChanged.connect(self.update_labels)

        self.refresh_objects()

    def get_mapped_objects(self):
        if not cmds.objExists("ShaderMappingNode"):
            return []
        attrs = cmds.listAttr("ShaderMappingNode", userDefined=True) or []
        return attrs

    def get_shader_mapping(self, obj_name):
        attr = "ShaderMappingNode." + obj_name
        if cmds.objExists(attr):
            value = cmds.getAttr(attr)
            if ":" in value:
                return value.split(":")
        return None, None

    def refresh_objects(self):
        self.object_list.clear()
        objs = self.get_mapped_objects()
        for obj in objs:
            self.object_list.addItem(obj)

    def update_labels(self):
        items = self.object_list.selectedItems()
        if not items:
            return
        obj = items[0].text()
        old, new = self.get_shader_mapping(obj)
        self.old_shader_label.setText("Old Shader: " + (old or ""))
        self.new_shader_label.setText("New Shader: " + (new or ""))

    def restore_old(self):
        items = self.object_list.selectedItems()
        if not items:
            return
        obj = items[0].text()
        old, _ = self.get_shader_mapping(obj)
        if old:
            sg = old + "_SG"
            if not cmds.objExists(sg):
                sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
                cmds.connectAttr(old + ".outColor", sg + ".surfaceShader", force=True)
            cmds.sets(obj, e=True, forceElement=sg)
            cmds.inViewMessage(amg='Reassigned <hl>{}</hl> to <hl>{}</hl>'.format(obj, old), pos='botCenter', fade=True)

    def assign_new(self):
        items = self.object_list.selectedItems()
        if not items:
            return
        obj = items[0].text()
        _, new = self.get_shader_mapping(obj)
        if new:
            sg = new + "_SG"
            if cmds.objExists(sg):
                cmds.sets(obj, e=True, forceElement=sg)
                cmds.inViewMessage(amg='Reassigned <hl>{}</hl> to <hl>{}</hl>'.format(obj, new), pos='botCenter', fade=True)

# ---- LAUNCH FUNCTION ----
def launch_shader_swap_ui():
    global shader_swap_ui
    try:
        shader_swap_ui.close()
    except:
        pass
    shader_swap_ui = ShaderSwapUI()
    shader_swap_ui.show()

# Example:
# launch_shader_swap_ui()
