import bpy

obj = bpy.context.active_object
attributes = obj.data.attributes

attr_uvs = [i for i, attr in enumerate(attributes) if attr.data_type == 'FLOAT_VECTOR' and attr.domain == 'CORNER' and 'UV' in attr.name]
obj_uvs = obj.data.uv_layers

if len(attr_uvs) == 1 and len(obj_uvs) == 0:
    attributes.active_index = attr_uvs[0]
    bpy.ops.geometry.attribute_convert(mode='UV_MAP')
    
hasattr()
_locals = locals()
def is_local(var_name:str, default_var) -> any:
    return _locals[var_name] if var_name in _locals else default_var

attr_index = is_local('attr_index', 0)
replace = is_local('replace', True)
replace_index = is_local('replace_index', 0)
button = is_local('popup', True)

def convert_getUV():
    # uv_attr_list: corner vector if 'uv' in attr.name.lower()
    # On convert -> check if object has a UVMap with conflicting name in uv_attr_list
    # If one or more exists, popup:
    # - for each attribute that exists:
    #     UVMap exists, replace? [REPLACE]
    ...


def button_getUV():
    # UI for each corner vector attribute:
    #     Convert to UVMap? [Convert]
    #     Replace UVMap? [Replace]
    bpy.context.active_object.data.uv_layers.active_index
    
    if replace:                                 # Replace
        obj_uvs.active_index = replace_index
        bpy.ops.mesh.uv_texture_remove()
    
    attributes.active_index = attr_index       # Set active index
    bpy.ops.geometry.attribute_convert(mode='UV_MAP')   # Convert
    
if button: button_getUV()