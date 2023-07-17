import bpy

# By Carlsu https://github.com/carls3d
# Made to be injected as a script in a serpens class

def applyModifiers(modifierName:str = None):
    def select_object(ob:bpy.types.Object, select:bool):
        if bpy.app.version < (3, 5, 0):
            ob.select = True
        else:
            ob.select_set(True)
    obj = bpy.context.active_object
    shapekeys = obj.data.shape_keys.key_blocks
    # Use active when ran on it's own as a script
    if not modifierName and obj.modifiers.active:
        if obj.modifiers.active:
            
            modifierName = obj.modifiers.active.name
        else: return
    
    objects = []
    for i, k in enumerate(shapekeys[1:]):
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.select_all(action='DESELECT')
        select_object(obj, True)
        bpy.ops.object.duplicate()
        
        bpy.context.active_object.show_only_shape_key = True        # Only use a single shapekey value
        bpy.context.active_object.active_shape_key_index = i+1      # Set active shapekey index
        bpy.ops.object.shape_key_remove(all=True, apply_mix=True)   # Apply shapekey
        bpy.ops.object.modifier_apply(modifier=modifierName)        # Apply modifier
        bpy.context.active_object.name = k.name                     # Set name
        objects.append(bpy.context.active_object)                  # Add to list

    for ob in objects: 
        select_object(ob, True)
    bpy.context.view_layer.objects.active = obj             # Set active object
    bpy.context.active_object.shape_key_clear()             # Remove shapekeys
    bpy.ops.object.modifier_apply(modifier=modifierName)    # Apply modifier
    bpy.ops.object.join_shapes()                            # Add shapekeys
    for k in objects:                                       # Delete placeholders
        bpy.data.meshes.remove(k.data)
    select_object(obj, True)

# if __name__ == '__main__':  
    # Use active modifier when ran as a script
    # applyModifiers()
    
    