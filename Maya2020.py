import json
import os
import maya.cmds as cmds

json_path = "C:/path/to/textures/shader_texture_colors.json"

if os.path.exists(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)

    for shader, info in data.iteritems():  # .iteritems() for Python 2.7
        tex_file = info.get("file")
        color = info.get("dominant_color", [0, 0, 0])
        print("Shader: {}, Texture: {}, Dominant Color: {}".format(shader, tex_file, color))

        # Example: Store as attribute on shader
        if cmds.objExists(shader):
            attr_name = "dominantColor"
            if not cmds.attributeQuery(attr_name, node=shader, exists=True):
                cmds.addAttr(shader, ln=attr_name, usedAsColor=True, at='float3')
                cmds.addAttr(shader, ln=attr_name+"R", at='float', p=attr_name)
                cmds.addAttr(shader, ln=attr_name+"G", at='float', p=attr_name)
                cmds.addAttr(shader, ln=attr_name+"B", at='float', p=attr_name)

            cmds.setAttr("{}.{}".format(shader, attr_name), color[0]/255.0, color[1]/255.0, color[2]/255.0, type="float3")
else:
    print("❌ JSON not found:", json_path)
