import bpy
import os

APPEND_TYPES = ["Action", "Brush", "Camera", "Collection", "FreestyleLineStyle", "Image", "Light", "Material", "Mesh", "NodeTree", "Object", "Palette", "Scene", "Text", "Texture", "WorkSpace", "World"]
serpens_assets_path = os.path.join(os.path.dirname(__file__), 'assets')

class AppendFromFile:
    types_attr = {
        "Material": "materials", 
        "NodeTree": "node_groups", 
        "Object": "objects"
        }
    
    def __init__(self, append_type, filepath, asset_name, link=True):
        self.append_type = append_type
        self.filepath = filepath
        self.asset_name = asset_name
        self.link = link

    @property
    def data(self):
        if self.append_type not in list(self.types_attr):
            return None
        return getattr(bpy.data, self.types_attr[self.append_type])

    def append(self):
        assert self.append_type in list(self.types_attr), f"Invalid type '{self.append_type}'"
        
        # Use existing
        if self.asset_name in bpy.data.node_groups: 
            return self.data[self.asset_name]
        
        # Append / Link
        before_data = self.data[:]
        bpy.ops.wm.append(directory=os.path.join(self.filepath, self.append_type), filename=self.asset_name, link=self.link)
        new_data = [d for d in self.data if d not in before_data]
        return new_data[0].name if new_data else None


def main():
    append_type = "NodeTree"

    
if __name__ == "__main__":
    main()

# def append_nodetree(node_name, link=True, filepath=None, filename=None):
#     if node_name in D.node_groups:
#         # Use existing
#         return D.node_groups[node_name]
#     else:
#         # Append / Link
#         before_data = D.node_groups[:]
#         bpy.ops.wm.append(directory=os.path.join(filepath, filename) + r'\NodeTree', filename=node_name, link=link)
#         new_data = [d for d in new_data if d not in before_data]
#         return new_data[0].name if new_data else None

# convert = {'sna_braids_node': None, 'sna_braidsnodename': '_Hair Braids Generator', 'sna_realize_node': None, 'sna_realizenodename': 'RealizeObject', 'sna_active_node': None, 'sna_obj': None, }
# def sna_getrealizeobject_1C864():
#     node = None
#     nodegrp_name = 'NodeGroupName'
#     if nodegrp_name in D.node_groups:
#         node = D.node_groups[nodegrp_name]
#     else:
#         before_data = D.node_groups[:]
#         bpy.ops.wm.append(directory=os.path.join(os.path.dirname(__file__), 'assets', 'Realize.blend') + r'\NodeTree', filename=nodegrp_name, link=True)
#         new_data = [d for d in new_data if d not in before_data]
        
#         added = None if not new_data else new_data[0]
#         node = added
#     return node.name

