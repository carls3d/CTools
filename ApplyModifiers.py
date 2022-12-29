import bpy
import timeit

def applyModifiers():
    obj = bpy.context.active_object
    shapekeys = obj.data.shape_keys.key_blocks
    # When ran on it's own as a script
    if 'modifierName' not in locals():
        modifierName = obj.modifiers.active.name
        
    obj_keys = []
    for i, k in enumerate(shapekeys[1:]):
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        bpy.ops.object.duplicate()
        
        bpy.context.active_object.show_only_shape_key = True        # Only use a single shapekey value
        bpy.context.active_object.active_shape_key_index = i+1      # Set active shapekey index
        bpy.ops.object.shape_key_remove(all=True, apply_mix=True)   # Apply shapekey
        bpy.ops.object.modifier_apply(modifier=modifierName)        # Apply modifier
        bpy.context.active_object.name = k.name                     # Set name
        obj_keys.append(bpy.context.active_object)                  # Add to list

    for k in obj_keys: k.select = True
    bpy.context.view_layer.objects.active = obj             # Set active object
    bpy.context.active_object.shape_key_clear()             # Remove shapekeys
    bpy.ops.object.modifier_apply(modifier=modifierName)    # Apply modifier
    bpy.ops.object.join_shapes()                            # Add shapekeys
    for k in obj_keys:                                      # Delete placeholders
        bpy.data.meshes.remove(k.data)
    obj.select = True

if __name__ == '__main__' or 'modifierName' in locals():  
    start = timeit.default_timer()
    applyModifiers()
    stop = timeit.default_timer()
    print(f'Time: {stop-start}\n')