import bpy, os
from ops.material_utils import get_labeled_nodes

C = bpy.context
D = bpy.data

SOURCE_MESH = "_tattoo_baker"
SOURCE_GN = "GN_UVMapProjector"
SOURCE_MAT = "MAT_TattooBaker"
SOURCE_IMAGE = "SourceImage"

TATTOO_MESH = "_tattoo_projector"
TATTOO_GN = "GN_TattooMesh"
TATTOO_MAT = "MAT_TattooMesh"
TATTOO_IMAGE = "TattooImage"

MODIFIER_NAME = "GeometryNodes"

ANY_ASSETS = lambda: any([
    D.objects.get(SOURCE_MESH), 
    D.objects.get(TATTOO_MESH), 
    D.node_groups.get(SOURCE_GN), 
    D.node_groups.get(TATTOO_GN), 
    D.materials.get(SOURCE_MAT), 
    D.materials.get(TATTOO_MAT)])

GET_OBJECT = {
    SOURCE_MESH: lambda : get_tattoo_baker,
    TATTOO_MESH: lambda : get_tattoo_projector,
}

SOCKET_TYPES = {
    SOURCE_GN: {
        'Socket_2': 'NodeSocketObject', # Target
        'Socket_4': 'NodeSocketObject', # Projector
        'Socket_5': 'NodeSocketMaterial', # Material
    },
    TATTOO_GN: {
        'Input_7': 'NodeSocketObject', # Target
        'Socket_8': 'NodeSocketMaterial', # Material
        'Socket_25': 'NodeSocketImage', # Image
    },
    SOURCE_MAT: {
        'SourceImage': 'TEX_IMAGE',
        'TattooImage': 'TEX_IMAGE',
        'CombinedImage': 'MIX',
        'Output': 'OUTPUT_MATERIAL',
    },
    TATTOO_MAT: {
        'TattooImage': 'TEX_IMAGE',
        'Output': 'OUTPUT_MATERIAL',
    },
}

ASSET_PATH = os.path.join(os.path.abspath('D:\Dropbox\Freehand\_BlenderNodes'), "TattooProjector.blend")

class AppendFromFile:
    types_attr = {
        "Material": "materials", 
        "NodeTree": "node_groups", 
        "Object": "objects"
        }
    def __init__(self, append_type, filepath, link=True):
        self.append_type = append_type
        self.filepath = filepath
        # self.asset_name = asset_name
        self.link = link

    @property
    def data(self):
        if self.append_type not in list(self.types_attr):
            return None
        return getattr(bpy.data, self.types_attr[self.append_type])

    def append(self, asset_name):
        assert self.append_type in list(self.types_attr), f"Invalid type '{self.append_type}'"
        
        # Use existing
        if asset_name in bpy.data.node_groups: 
            return self.data[asset_name]
        
        # Append / Link
        before_data = self.data[:]
        bpy.ops.wm.append(directory=os.path.join(self.filepath, self.append_type), filename=asset_name, link=self.link)
        new_data = [d for d in self.data if d not in before_data]
        return new_data[0].name if new_data else None



def get_GeoNodeTree(GN_name:str, link:bool = False) -> bpy.types.GeometryNodeTree:
    modifier = D.node_groups.get(GN_name)
    if modifier and validate_nodesmodifer(modifier, GN_name):
        return modifier
    
    filepath = os.path.join(os.path.abspath('D:\Dropbox\Freehand\_BlenderNodes'), "TattooProjector.blend")
    AppendFromFile(
        "NodeTree", 
        filepath, 
        link=link
        ).append(GN_name)
    return D.node_groups.get(GN_name)

def get_Material(MAT_name:str, link:bool = False) -> bpy.types.Material:
    material = D.materials.get(MAT_name)
    if material and validate_material(material, MAT_name):
        return material
    
    filepath = os.path.join(os.path.abspath('D:\Dropbox\Freehand\_BlenderNodes'), "TattooProjector.blend")
    AppendFromFile(
        "Material", 
        filepath, 
        link=link
        ).append(MAT_name)
    return D.materials.get(MAT_name)
   


def get_GeometryNodes_modifier(obj_name:str) -> bpy.types.NodesModifier | None:
    obj = D.objects.get(obj_name)
    if obj: 
        modifier = obj.modifiers.get(MODIFIER_NAME)
        return modifier
    return None


def get_tattoo_projector() -> bpy.types.Object:
    """Mesh"""
    proj_obj = D.objects.get(TATTOO_MESH)
    if not proj_obj:
        getmesh = lambda: D.meshes.get(TATTOO_MESH) or D.meshes.new(TATTOO_MESH)
        proj_obj = D.objects.new(TATTOO_MESH, getmesh())
        modifier = proj_obj.modifiers.new(MODIFIER_NAME, 'NODES')
        modifier.node_group = get_GeoNodeTree(TATTOO_GN, link=True)
        bpy.context.collection.objects.link(proj_obj)
    
    if not validate_nodesmodifer(proj_obj.modifiers[MODIFIER_NAME], TATTOO_GN):
        proj_obj.modifiers.clear()
        modifier = proj_obj.modifiers.new(MODIFIER_NAME, 'NODES')
        modifier.node_group = get_GeoNodeTree(TATTOO_GN, link=True)
    return proj_obj

def get_tattoo_baker() -> bpy.types.Object:
    """Mesh"""
    bake_obj = D.objects.get(SOURCE_MESH) or None
    if not bake_obj:
        getmesh = lambda: D.meshes.get(SOURCE_MESH) or D.meshes.new(SOURCE_MESH)
        bake_obj = D.objects.new(SOURCE_MESH, getmesh())
        modifier = bake_obj.modifiers.new(MODIFIER_NAME, 'NODES')
        modifier.node_group = get_GeoNodeTree(SOURCE_GN, link=True)
        bpy.context.collection.objects.link(bake_obj)
    
    elif not validate_nodesmodifer(bake_obj.modifiers[MODIFIER_NAME], SOURCE_GN):
        bake_obj.modifiers.clear()
        modifier = bake_obj.modifiers.new(MODIFIER_NAME, 'NODES')
        modifier.node_group = get_GeoNodeTree(SOURCE_GN, link=True)
        
    bake_obj.lock_location = [True]*3
    bake_obj.lock_rotation = [True]*3
    bake_obj.lock_scale = [True]*3
    return bake_obj


def validate_nodesmodifer(modifier:bpy.types.NodesModifier, modifier_name:str) -> bool: 
    """Asserts modifier socket types"""
    if not modifier.node_group:
        return False
    if modifier.node_group.name != modifier_name:
        print(f"Modifier node group is not '{modifier_name}'")
        return False
    modifier.show_viewport = True
    modifier.show_render = True
    
    # Modifier input sockets
    items_tree = modifier.node_group.interface.items_tree
    socket_types = {i.identifier:i.socket_type for i in items_tree if i.item_type == 'SOCKET' and i.in_out == 'INPUT'}
    for socket, socket_type in SOCKET_TYPES[modifier_name].items():
        if socket_types.get(socket) != socket_type:
            print(f"Socket '{socket}' is not of type '{socket_type}', found '{socket_types.get(socket)}'")
            return False
    return True

def validate_material(material:bpy.types.Material, material_name:str) -> bool:
    """Asserts material socket types"""
    if material.name != material_name:
        print(f"Material is not '{material_name}'")
        return False
    node_types_filter = SOCKET_TYPES[material_name]
    
    # Material nodes with labels
    nodes = material.node_tree.nodes
    node_types = {n.label:n.type for n in nodes if n.label}
    for node, node_type in node_types_filter.items():
        if node_types.get(node) != node_type:
            print(f"Node '{node}' is not of type '{node_type}', found '{node_types.get(node)}'")
            return False
    return True


def remove_asset(path, name) -> None:
    collection = getattr(D, path)
    asset = collection.get(name)
    if asset: collection.remove(asset, do_unlink=True) 