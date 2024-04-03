import bpy

class CT_OT_Toggle_Pin(bpy.types.Operator):
    bl_idname = "ct.toggle_pin"
    bl_label = "Toggle Pin"
    bl_description = "Toggle Pin"
    bl_options = {"REGISTER", "UNDO"}
    
    id: bpy.props.StringProperty(name='id', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0) # type: ignore
    
    def execute(self, context):
        context.scene.braids_pin_id = self.id if context.scene.braids_pin_id != self.id else ''
        return {"FINISHED"}
    def invoke(self, context, event):
        return self.execute(context)
    
class SNA_PT_BRAIDS_GENERATOR_A87B8(bpy.types.Panel):
    bl_label = 'Braids Generator X3'
    bl_idname = 'SNA_PT_BRAIDS_GENERATOR_A87B8'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CTools'

    pin_id = None
    
    def draw_header_preset(self, context):
        layout = self.layout
        pin_id = context.scene.braids_pin_id
        op = layout.operator('ct.toggle_pin', text='', icon='PINNED' if pin_id == self.bl_idname else 'UNPINNED', emboss=False)
        op.id = self.bl_idname
        
    def draw(self, context):
        col = self.layout.column(align=True)
        ob = bpy.context.active_object
        nodegrp_name = ''
        modifier = ob.modifiers.get('GeometryNodes')
        if not modifier or not modifier.node_group: return
        if modifier.node_group.name != nodegrp_name: return

        col_props = col.column(align=True)
        col_props.use_property_split = True
        col_props.use_property_decorate = False
        
        valid_input = lambda x: all([
            x.in_out == 'INPUT',
            hasattr(x, 'default_value')
        ])
        inputs = [var for var in modifier.node_group.interface.items_tree if valid_input(var)]
        for inp in inputs:
            col_props.prop(modifier, f"""["{inp.identifier}"]""", text=inp.name)
        
def register():
    bpy.types.Scene.braids_pin_id = bpy.props.StringProperty(name='pin_id', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    bpy.utils.register_class(CT_OT_Toggle_Pin)
    
def unregister():
    del bpy.types.Scene.braids_pin_id
    bpy.utils.unregister_class(CT_OT_Toggle_Pin)