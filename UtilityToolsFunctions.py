import bpy
import bmesh
import timeit

def island_indices():
    C = bpy.context
    if C.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
        
    bm = bmesh.new()
    bm.from_mesh(C.object.data)
    bm.verts.ensure_lookup_table()
    
    islands:list = []
    copy_verts:set = {*bm.verts}
    while copy_verts:
        island = {copy_verts.pop()}
        island_linked = set()
        
        while island != island_linked:
            if island_linked: island = island_linked
            
            island_linked = island.copy()
            island_linked.update(edge.other_vert(vertex) for vertex in island for edge in vertex.link_edges)
            
            if not island_linked: break # If no new vertices are found
            
        # Remove island from copy_verts
        copy_verts.difference_update(island)
        # Add island verts to islands
        islands.append(island)
    
    # Get mesh and create/replace attribute
    mesh:bpy.types.Mesh = C.object.data
    attribute = mesh.attributes.get("IslandIndex")
    if attribute:
        mesh.attributes.remove(attribute)
    attribute = mesh.attributes.new(name="IslandIndex", type="INT", domain="POINT")
    
    # Set island index for each vertex
    attribute_values = [0 for i, island in enumerate(islands) for _ in range(len(island))]
    for island_index, island in enumerate(islands):
        for v in island:
            attribute_values[v.index] = island_index
    
    # Set attribute values
    attribute.data.foreach_set("value", attribute_values)
    bm.free()
    

def baking_stuff():
    ...
    C = bpy.context
    D = bpy.data
    # Active image
    [area for area in C.screen.areas if area.type == 'IMAGE_EDITOR'][0].spaces.active.image
    [a for a in D.screens['UV Editing'].areas if a.type == 'IMAGE_EDITOR'].pop()
    
def set_shapekey_as_basis(new_basis):
    bpy.context.object.active_shape_key
    ...
    # Select basis
    # Edit mode
    # Select all
    # Blend from shape -> new_basis (1.0)
    # Rename new_basis -> old_basis
    # Select old_basis
    # Edit mode
    # Select all
    # Blend from shape -> basis (2.0)
    
    
def set_shapekey_intensity(shapekey, intensity):
    basis = bpy.context.object.data.shape_keys.key_blocks[0]
    active_key = bpy.context.object.active_shape_key
    
    

    ...
    # Select shapekey
    # Edit mode
    # Select all
    # Blend from shape -> shapekey(add=true, )
    # x0        =   -1.0
    # x0.5      =   -0.5
    # x1        =   0.0
    # x1.5      =   0.5
    # x2        =   1.0
    # x5        =   4.0  
    
def main():
    island_indices()
    # timer = timeit.default_timer()
    # print("Time: ",timeit.default_timer()-timer)
    
if __name__ == "__main__":
    main()