import bpy

obj = bpy.context.view_layer.objects
source = obj.active
parent = obj.active.parent

bpy.ops.object.data_transfer(
    data_type='VGROUP_WEIGHTS', 
    vert_mapping='POLYINTERP_NEAREST', 
    layers_select_src='ALL', 
    layers_select_dst='NAME', 
    mix_mode='REPLACE', 
    mix_factor=1
    )

if parent:
    if parent.type == 'ARMATURE':
        obj.active = parent
        bpy.ops.object.parent_set(
            type='ARMATURE', 
            keep_transform=True
            )
        obj.active = source
