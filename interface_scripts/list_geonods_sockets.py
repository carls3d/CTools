import bpy

def list_gn_input_sockets(layout_function:bpy.types.UILayout, obj, property_split=True, property_decorate=False):
    col = layout_function.column(align=False)
    col.scale_y = 1.1
    col.use_property_split = property_split
    col.use_property_decorate = property_decorate
    modifier = obj.modifiers.get("GeometryNodes")
    items_tree = modifier.node_group.interface.items_tree
    inputs = [var for var in items_tree if all([var.in_out == 'INPUT', hasattr(var, 'default_value')])]
    for inp in inputs:
        if inp.socket_type == 'NodeSocketMaterial':
            col.prop_search(modifier, f"""["{inp.identifier}"]""", bpy.data, "materials", text=inp.name, icon='MATERIAL_DATA')
        else:
            col.prop(modifier, f"""["{inp.identifier}"]""", text=inp.name)