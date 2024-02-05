import bpy

C = bpy.context
D = bpy.data

def get_labeled_nodes(mat:bpy.types.Material) -> dict | None:
    """Get dictionary of labeled nodes in material"""
    return {n.label:n for n in mat.node_tree.nodes if n.label} or None

def get_material_node(material:bpy.types.Material, label:str) -> bpy.types.ShaderNode:
    """Get labeled node from material"""
    return get_labeled_nodes(material).get(label)


def tattoo_thing():
    obj = C.object
    assert obj.active_material, "No active material found"
    
    tattoo_node_label = "TattooImage"
    source_node_label = "SourceImage"

    nodes_with_labels = {n.label:n for n in C.object.active_material.node_tree.nodes if n.label}
    assert nodes_with_labels, "No nodes with labels found"

    tattoo_node = nodes_with_labels[tattoo_node_label]
    source_node = nodes_with_labels[source_node_label]
