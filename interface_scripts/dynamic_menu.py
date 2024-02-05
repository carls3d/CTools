import bpy
import random

CONTEXT_ID = "ct_dynamic_menu_" + str(random.randint(0, 1000000))
def dyn_menu(layout_function:bpy.types.UILayout, func_name:str, args:list, label:str = "", icon_value:int = 46):
    row = layout_function.row(align=True)
    row.context_pointer_set(CONTEXT_ID, row)
    CT_MT_DynamicMenu._parents[row] = func_name, args
    row.menu(CT_MT_DynamicMenu.bl_idname, text=label, icon_value=icon_value)



class CT_MT_DynamicMenu(bpy.types.Menu):
    bl_idname = "CT_MT_dynamic_menu"
    bl_label = "Dynamic Menu"
    
    _parents = {}
    
    def draw(self, context):
        parent_id = getattr(context, CONTEXT_ID, None)
        func_name, args = self._parents[parent_id]
        
        dyn_menu = self.layout
        eval(f"{func_name}(dyn_menu, *args)")
        
            
def register():
    bpy.utils.register_class(CT_MT_DynamicMenu)

def unregister():
    bpy.utils.unregister_class(CT_MT_DynamicMenu)