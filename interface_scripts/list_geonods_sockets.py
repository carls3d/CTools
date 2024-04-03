import bpy

def list_gn_input_sockets(layout_function:bpy.types.UILayout, obj, property_split=True, property_decorate=False):
    
    def get_inputs(modifier):
        if bpy.app.version >= (4,0,0):
            items_tree = modifier.node_group.interface.items_tree
            inputs = [var for var in items_tree if all([var.in_out == 'INPUT', hasattr(var, 'default_value')])]
            is_material = lambda inp: inp.socket_type == 'NodeSocketMaterial'
            return inputs, is_material
        
        elif bpy.app.version >= (3,3,0):
            inputs = [var for var in filter(lambda x: hasattr(x, 'default_value'), modifier.node_group.inputs)]
            is_material = lambda inp: inp.type == 'MATERIAL'
            return inputs, is_material
        
        return None, None
    
    col = layout_function.column(align=False)
    col.scale_y = 1.1
    col.use_property_split = property_split
    col.use_property_decorate = property_decorate
    modifier = obj.modifiers.get("GeometryNodes")
    
    inputs, is_material = get_inputs(modifier)
    
    if not inputs:
        return col.label(text="No inputs found")
    
    for inp in inputs:
        if is_material(inp):
            col.prop_search(modifier, f"""["{inp.identifier}"]""", bpy.data, "materials", text=inp.name, icon='MATERIAL_DATA')
        else:
            col.prop(modifier, f"""["{inp.identifier}"]""", text=inp.name)