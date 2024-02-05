import bpy
from bpy_extras import view3d_utils
from mathutils import Vector
from bpy.types import Context


class CT_PlaceTattooPlane(bpy.types.Operator):
    bl_idname = "ct.place_tattoo_plane"
    bl_label = "Place Tattoo Plane"
    bl_description = ""
    bl_options = {'REGISTER'}

    obj:bpy.types.Object
    raycast_hit:bool = False

    @classmethod
    def poll(cls, context):
        return True

    def set_cursor(self, context:Context, cursor:str):
        cursor_event = {
            "Start": "CROSSHAIR",
            "Hit": "SCROLL_XY",
            "Finish": "DEFAULT",
        }
        context.window.cursor_modal_set(cursor_event[cursor])

    def invoke(self, context, event):
        self.obj = context.active_object
        context.window_manager.modal_handler_add(self)
        self.set_cursor(context, "Start")
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        # self.obj
        # Raycast from mouse position
        # Get hit position
        # Get hit normal
        
        # print(event.type, event.value)
        if self.raycast_hit:
            # Do thing
            ...
        
        if event.type == "LEFTMOUSE":
            if context.area.type != "VIEW_3D":
                self.report({"ERROR"}, "Active area is not a 3D View")
                return {"CANCELLED"}

            if event.value == "PRESS":
                dephsgraph = context.evaluated_depsgraph_get()
                region3D = context.space_data.region_3d
                mouse_coords = Vector((event.mouse_region_x, event.mouse_region_y))
                origin = view3d_utils.region_2d_to_origin_3d(context.region, region3D, mouse_coords)
                vec = view3d_utils.region_2d_to_vector_3d(context.region, region3D, mouse_coords)
                hit, loc, normal, index, object, matrix = context.scene.ray_cast(dephsgraph, origin, vec)
                self.raycast_hit = hit
                
                if self.raycast_hit:
                    self.set_cursor(context, "Hit")
                    # Prepare to do things
                    ...
                return {"RUNNING_MODAL"}
            
            elif event.value == "RELEASE":
                if not self.raycast_hit:
                    print("No press")
                    return {"RUNNING_MODAL"}
                # Finish doing things
                # ...
                self.set_cursor(context, "Finish")
                return {"FINISHED"}
        
        if event.type in {"RIGHTMOUSE", "ESC"}:
            print("Cancel")
            self.set_cursor(context, "Finish")
            return {"CANCELLED"}
        
        return {"RUNNING_MODAL"}