# Import / create -> Materials, GeometryNodeTrees, Objects

import bpy
from ops.nodegroups import *
from bpy.types import Operator

C = bpy.context
D = bpy.data

class CT_Setup(Operator):
    bl_idname = "ct.setup"
    bl_label = "Setup assets"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        print("\n Execute")
        if ANY_ASSETS():
            self.report({"WARNING"}, "Re-Setup")
            remove_asset("objects", SOURCE_MESH)
            remove_asset("objects", TATTOO_MESH)
            remove_asset("node_groups", SOURCE_GN)
            remove_asset("node_groups", TATTOO_GN)
            remove_asset("materials", SOURCE_MAT)
            remove_asset("materials", TATTOO_MAT)
            print("Removed assets")
        else:
            self.report({"INFO"}, "Setup")
        get_tattoo_baker()
        get_tattoo_projector()
        
        # Trigger update functions
        scene = bpy.context.scene
        scene.tattoo_ptr = scene.tattoo_ptr
        scene.source_ptr = scene.source_ptr
        return {"FINISHED"}

    # def invoke(self, context, event):
    #     return self.execute(context)

class CT_Remove(Operator):
    bl_idname = "ct.remove"
    bl_label = "Remove assets"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        if ANY_ASSETS():
            self.report({"INFO"}, "Removed assets")
            remove_asset("objects", SOURCE_MESH)
            remove_asset("objects", TATTOO_MESH)
            remove_asset("node_groups", SOURCE_GN)
            remove_asset("node_groups", TATTOO_GN)
            remove_asset("materials", SOURCE_MAT)
            remove_asset("materials", TATTOO_MAT)
        else:
            self.report({"WARNING"}, "No assets to remove")
        return {"FINISHED"}

    # def invoke(self, context, event):
    #     return self.execute(context)

setup_classes = (
    CT_Setup,
    CT_Remove
)