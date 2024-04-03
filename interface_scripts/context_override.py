import bpy
from bpy.types import Operator, Panel

# https://docs.blender.org/api/current/bpy.ops.html#overriding-context
# https://blender.stackexchange.com/a/291088

class A_OP_ContextOverrideOperator(Operator):
    bl_idname = "image.contextoverride_operator"
    bl_label = "Context Override Operator"
    bl_description = "Operator called with context override"
    bl_options = {'REGISTER', 'UNDO'}

    # verify appropriate context is available in current workspace and save reference in context_area variable
    context_area: bpy.types.Area = None
    @classmethod
    def poll(cls, context):
        cls.context_area = None
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                cls.context_area = area
                break

        if not cls.context_area:
            cls.poll_message_set("Need Image Editor window in workspace")
            return False

        return cls.context_area.type == 'IMAGE_EDITOR'

    def execute(self, context):
        print("Calling context override operator...")
        print(f"\tOperator called with context: {context.space_data.type}")
        with context.temp_override(area=self.context_area):
            # put Image Editor related code  here
            print(f"\tContext after override: {context.space_data.type}")

        return {'FINISHED'}

class A_PT_CustomView3D_Panel(Panel):
    # custom panel added to the 3D View Sidebar
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_label = "Custom Panel"
    bl_category = "Custom Tab"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.operator("image.contextoverride_operator")

classes = (A_OP_ContextOverrideOperator, A_PT_CustomView3D_Panel)

def register():
    for c in classes:
        bpy.utils.register_class(c)

if __name__ == "__main__":
    register()