# shader_swap_tool.py

from PySide2 import QtWidgets, QtCore
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import os
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

# -------------------------------------------------------------------------------------
# BACKEND: Shader Mapping Manager
# -------------------------------------------------------------------------------------
class ShaderMappingManager(object):
    def __init__(self):
        self.mapping_node = self.get_or_create_mapping_node()

    def get_or_create_mapping_node(self):
        node = "ShaderMappingNode"
        if not cmds.objExists(node):
            node = cmds.createNode("transform", name=node)
            cmds.setAttr(node + ".visibility", 0)
            cmds.lockNode(node, lock=True)
        return node

    def store_mapping(self, obj, old_shader, new_shader):
        attr_name = obj.replace("|", "_")
        full_attr = self.mapping_node + "." + attr_name
        if not cmds.attributeQuery(attr_name, node=self.mapping_node, exists=True):
            cmds.lockNode(self.mapping_node, lock=False)
            cmds.addAttr(self.mapping_node, longName=attr_name, dataType="string")
            cmds.lockNode(self.mapping_node, lock=True)
        value = "{}:{}".format(old_shader, new_shader)
        cmds.setAttr(full_attr, value, type="string")

    def read_mapping(self, obj):
        attr_name = obj.replace("|", "_")
        if not cmds.objExists(self.mapping_node):
            return None, None
        if not cmds.attributeQuery(attr_name, node=self.mapping_node, exists=True):
            return None, None
        value = cmds.getAttr(self.mapping_node + "." + attr_name)
        if ":" in value:
            return value.split(":")
        return None, None

    def get_texture_and_shader(self, obj):
        shading_grps = cmds.listConnections(obj, type='shadingEngine') or []
        for sg in shading_grps:
            shader = cmds.ls(cmds.listConnections(sg + ".surfaceShader"), materials=True)
            if shader:
                file_nodes = cmds.listConnections(shader[0], type='file')
                if file_nodes:
                    file_path = cmds.getAttr(file_nodes[0] + ".fileTextureName")
                    return file_path, shader[0]
        return None, None

    def get_dominant_color(self, image_path, k=3):
        if not os.path.exists(image_path):
            return None
        img = Image.open(image_path)
        img = img.resize((64, 64)).convert("RGB")
        pixels = np.array(img).reshape((-1, 3))
        kmeans = KMeans(n_clusters=k, random_state=42).fit(pixels)
        counts = np.bincount(kmeans.labels_)
        dominant_color = kmeans.cluster_centers_[np.argmax(counts)]
        return tuple([c / 255.0 for c in dominant_color])

    def create_lambert_shader(self, base_shader_name, rgb_color):
        new_shader = "Lambert_" + base_shader_name
        if not cmds.objExists(new_shader):
            shader = cmds.shadingNode("lambert", asShader=True, name=new_shader)
            sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=new_shader + "SG")
            cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader", force=True)
            cmds.setAttr(shader + ".color", rgb_color[0], rgb_color[1], rgb_color[2], type="double3")
        return new_shader, new_shader + "SG"

    def assign_color_shader(self, obj):
        image_path, old_shader = self.get_texture_and_shader(obj)
        if not image_path or not old_shader:
            return
        dom_color = self.get_dominant_color(image_path)
        if not dom_color:
            return
        new_shader, sg = self.create_lambert_shader(old_shader, dom_color)
        cmds.sets(obj, e=True, forceElement=sg)
        self.store_mapping(obj, old_shader, new_shader)

    def reassign_old_shader(self, obj):
        old_shader, _ = self.read_mapping(obj)
        if not old_shader:
            return
        sg = old_shader + "_SG"
        if not cmds.objExists(sg):
            sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
            cmds.connectAttr(old_shader + ".outColor", sg + ".surfaceShader", force=True)
        cmds.sets(obj, e=True, forceElement=sg)

# -------------------------------------------------------------------------------------
# UI: Shader Swap Tool
# -------------------------------------------------------------------------------------
class ShaderSwapTool(QtWidgets.QWidget):
    def __init__(self):
        super(ShaderSwapTool, self).__init__()
        self.setWindowTitle("Shader Swap Manager")
        self.setMinimumSize(400, 300)
        self.setObjectName("ShaderSwapTool")
        self.shader_mgr = ShaderMappingManager()

        self.build_ui()
        self.connect_signals()
        self.refresh_object_list()

    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.object_list = QtWidgets.QListWidget()
        layout.addWidget(self.object_list)
        self.old_shader_label = QtWidgets.QLabel("Old Shader: ")
        self.new_shader_label = QtWidgets.QLabel("New Shader: ")
        layout.addWidget(self.old_shader_label)
        layout.addWidget(self.new_shader_label)
        button_layout = QtWidgets.QHBoxLayout()
        self.restore_btn = QtWidgets.QPushButton("\u23ea Reassign Old Shader")
        self.reassign_btn = QtWidgets.QPushButton("\U0001f3a8 Reassign New Shader")
        button_layout.addWidget(self.restore_btn)
        button_layout.addWidget(self.reassign_btn)
        layout.addLayout(button_layout)

    def connect_signals(self):
        self.object_list.itemSelectionChanged.connect(self.update_shader_labels)
        self.restore_btn.clicked.connect(self.reassign_old_shader)
        self.reassign_btn.clicked.connect(self.assign_new_shader)

    def get_mapped_objects(self):
        if not cmds.objExists("ShaderMappingNode"):
            return []
        return cmds.listAttr("ShaderMappingNode", userDefined=True) or []

    def refresh_object_list(self):
        self.object_list.clear()
        for obj in self.get_mapped_objects():
            self.object_list.addItem(obj)

    def update_shader_labels(self):
        items = self.object_list.selectedItems()
        if not items:
            return
        obj = items[0].text()
        old, new = self.shader_mgr.read_mapping(obj)
        self.old_shader_label.setText("Old Shader: " + (old or ""))
        self.new_shader_label.setText("New Shader: " + (new or ""))

    def reassign_old_shader(self):
        items = self.object_list.selectedItems()
        if not items:
            return
        obj = items[0].text()
        self.shader_mgr.reassign_old_shader(obj)

    def assign_new_shader(self):
        items = self.object_list.selectedItems()
        if not items:
            return
        obj = items[0].text()
        self.shader_mgr.assign_color_shader(obj)

# -------------------------------------------------------------------------------------
# Launch Function
# -------------------------------------------------------------------------------------
def get_maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QMainWindow)

def launch_shader_swap_tool():
    parent = get_maya_main_window()
    for widget in parent.findChildren(QtWidgets.QWidget):
        if widget.objectName() == "ShaderSwapTool":
            widget.close()
            widget.deleteLater()
    ui = ShaderSwapTool()
    ui.setParent(parent)
    ui.setWindowFlags(QtCore.Qt.Window)
    ui.show()

# To launch:
# launch_shader_swap_tool()
