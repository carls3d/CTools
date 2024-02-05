import bpy
import os,sys

sourcedir = os.path.abspath("C:/Users/Carl/Documents/GitHub/CTools/tattoo_projection")
if sourcedir in sys.path:
    sys.path.remove(sourcedir)
sys.path.append(sourcedir)

startswith_in = lambda s, l: any([s.startswith(x) for x in l])
for mod in list(sys.modules.keys())[::-1]:
    if startswith_in(mod, ["ops", "ui"]):
        del sys.modules[mod]


from ops.place_tattoo_plane import CT_PlaceTattooPlane
from ops.bake_texture import CT_BakeTexture
# from ui.tattoo_panel import CT_PT_TattooPanel, OperatorWithFileSelect, CT_SubPanel_Inputs, CT_SubPanel_Source
from ui.tattoo_panel import panel_classes
from ops.asset_setup import setup_classes
from ops.nodegroups import *
# from ..scripts.link_blendfile import AppendFromFile

C = bpy.context
D = bpy.data


def tex_size_enum_update(self, context):
    enum_prop = self.texture_size
    match enum_prop:
        case "UseSource":
            if not self.source_ptr: return
            self.size_custom_x = self.source_ptr.size[0]
            self.size_custom_y = self.source_ptr.size[1]
        case "Custom":
            return
        case _:
            size = int(enum_prop)
            self.size_custom_x = size
            self.size_custom_y = size

def tattoo_ptr_update(self, context):
    # _tatoo_projector
    #    MAT_TattooMesh
    #       node = GET_NODE["TattooImage"](MAT_TattooMesh)
    #       node.image = self.tattoo_ptr
    #    GN_TattooMesh 
    #       mod["Socket_8"] = MAT_TattooMesh
    #       mod["Socket_10"] = node.image.size[0]
    #       mod["Socket_11"] = node.image.size[1]
    # 
    # _tattoo_baker
    #    MAT_TattooBaker
    #       node = GET_NODE["TattooImage"](MAT_TattooBaker)
    #       node.image = self.tattoo_ptr
    # print("\n---- tattoo_ptr_update ----")
    assert self.obj_ptr, "No object found"
    assert self.tattoo_ptr, "No tattoo image found"
    proj_obj = get_tattoo_projector()
    proj_mat = get_Material(TATTOO_MAT)
    proj_mat_labeled_nodes = get_labeled_nodes(proj_mat)
    proj_mat_labeled_nodes[TATTOO_IMAGE].image = self.tattoo_ptr
    
    proj_modifier = proj_obj.modifiers.get(MODIFIER_NAME)
    print(proj_modifier["Socket_25"])
    proj_modifier["Input_7"] = self.obj_ptr
    proj_modifier["Socket_8"] = proj_mat
    proj_modifier["Socket_25"] = self.tattoo_ptr
    
    bake_obj = get_tattoo_baker()
    bake_mod = bake_obj.modifiers.get(MODIFIER_NAME)
    bake_mat = get_Material(SOURCE_MAT)
    bake_mod["Socket_2"] = self.obj_ptr
    bake_mod["Socket_4"] = proj_obj
    bake_mod["Socket_5"] = bake_mat
    
    bake_mat_labeled_nodes = get_labeled_nodes(bake_mat)
    bake_mat_labeled_nodes[TATTOO_IMAGE].image = self.tattoo_ptr
    

def source_ptr_update(self, context):
    tex_size_enum_update(self, context)
    assert self.obj_ptr, "No object found"
    assert self.source_ptr, "No source image found"
    bake_obj = get_tattoo_baker()
    bake_mat = get_Material(SOURCE_MAT)
    bake_mat_labeled_nodes = get_labeled_nodes(bake_mat)
    bake_mat_labeled_nodes[SOURCE_IMAGE].image = self.source_ptr
    # print(bake_mat_labeled_nodes[SOURCE_IMAGE].image)
    
    bake_mod = bake_obj.modifiers.get(MODIFIER_NAME)
    bake_mod["Socket_5"] = bake_mat  # SOCKET_TYPES[SOURCE_GN]
    
    # _tattoo_baker
    #    MAT_TattooBaker
    #       node["SourceImage"].image = self.source_ptr

def try_except(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
            return True
        except Exception as e:
            print(e)
            return False
    return wrapper


class Updater:
    def __init__(self, scene, context):
        self.scene = scene
        self.context = context
    
    def parser(self, prop:str):
        socket, *index = prop.split("[")
        vars = prop.split("[")
        socket = vars[0]
        if len(vars) == 1:
            return [socket, None]
        index = eval(vars[1].split("]")[0])
        assert type(index) == int, "Invalid index"
        return [socket, index]
    
    @try_except
    def set_direct(self, obj_name:str, socket:str, prop:str):
        modifier = D.objects[obj_name].modifiers[MODIFIER_NAME]
        s, i = self.parser(socket)
        p, j = self.parser(prop)
        prop_attr = getattr(self.scene, p)[j] if j is not None else getattr(self.scene, p)
        if i is not None:
            modifier[s][i] = prop_attr
        else:
            modifier[s] = prop_attr
    
    @try_except
    def create_then_set(self, func, socket:str, prop:str):
        modifier = func().modifiers.get(MODIFIER_NAME)
        s, i = self.parser(socket)
        p, j = self.parser(prop)
        prop_attr = getattr(self.scene, p)[j] if j is not None else getattr(self.scene, p)
        if i is not None:
            modifier[s][i] = prop_attr
        else:
            modifier[s] = prop_attr
    
    def proj(self, socket:str, prop:str):
        x = self.set_direct(TATTOO_MESH, socket, prop)
        
        if x: return
        assert self.create_then_set(get_tattoo_projector, socket, prop), "Failed to set projector property"
    
    def bake(self, socket:str, prop:str):
        x = self.set_direct(SOURCE_MESH, socket, prop)
        if x: return
        assert self.create_then_set(get_tattoo_baker, socket, prop), "Failed to set baker property"


def update_baker_prop(self, context, socket:str, prop:str):
    try:
        modifier = D.objects[SOURCE_MESH].modifiers[MODIFIER_NAME]
        modifier[socket] = getattr(self, prop)
    except:
        obj = get_tattoo_baker()
        obj.modifiers.get(MODIFIER_NAME)[socket] = getattr(self, prop)
        
def update_projector_prop(self, context, socket:str, prop:str):
    try:
        modifier = D.objects[TATTOO_MESH].modifiers[MODIFIER_NAME]
        modifier[socket] = getattr(self, prop)
    except:
        obj = get_tattoo_projector()
        obj.modifiers.get(MODIFIER_NAME)[socket] = getattr(self, prop)
    

def obj_ptr_update(self, context):
    # print("----obj_ptr_update")
    # Check for valid modifier
    #    Create modifier if not found
    # Get or set image socket
    # Get or set material
    proj_obj = get_tattoo_projector()
    bake_obj = get_tattoo_baker()
    proj_obj.modifiers.get(MODIFIER_NAME)["Input_7"] = self.obj_ptr
    bake_obj.modifiers.get(MODIFIER_NAME)["Socket_2"] = self.obj_ptr
    ...

def update_modifiers(self, context):
    # Source obj modifier
    # Tattoo modifier
    obj:bpy.types.Object
    modifier:bpy.types.Modifier
    
    obj = bpy.context.scene.obj_ptr
    if not obj: return
    
    tattoo_socket = "Socket_7"
    
    modifier = obj.modifiers.get("GeometryNodes")
    assert tattoo_socket in modifier, "No tattoo image socket found"
    img_ptr = C.scene.tattoo_ptr
    modifier[tattoo_socket] = img_ptr
    
        
classes = (
    CT_PlaceTattooPlane,
    CT_BakeTexture,
)
classes += panel_classes
classes += setup_classes

properties = {
    "texture_size": bpy.props.EnumProperty(name="Output Size", items=[
        ("UseSource", "Source", ""),
        ("Custom", "Custom", ""),
        ("512", "512 x 512", ""),
        ("1024", "1024 x 1024", ""),
        ("2048", "2048 x 2048", ""),
        ("4096", "4096 x 4096", ""),
        ("8192", "8192 x 8192", ""),
    ], default="UseSource", update=tex_size_enum_update),
    "size_custom_x": bpy.props.IntProperty(name="X", default=1024, min=1, max=4096),
    "size_custom_y": bpy.props.IntProperty(name="Y", default=1024, min=1, max=4096),
    "tattoo_ptr": bpy.props.PointerProperty(name="Tattoo",type=bpy.types.Image, update=tattoo_ptr_update),
    "source_ptr": bpy.props.PointerProperty(name="Source",type=bpy.types.Image, update=source_ptr_update),
    "obj_ptr": bpy.props.PointerProperty(name="Object",type=bpy.types.Object, update=obj_ptr_update),
}
# from nodeitems_utils import NodeCategory, NodeItem

# classes += (,)
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    for prop in properties:
        exec(f"bpy.types.Scene.{prop} = properties[prop]")
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    for prop in properties:
        exec(f"del bpy.types.Scene.{prop}")
    

if __name__ == "__main__":
    try: unregister()
    except: pass
    register()