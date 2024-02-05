class NodeItem:
    def __init__(self, name, in_out:str):
        if in_out not in ["INPUT", "OUTPUT"]:
            raise ValueError("in_out must be either 'INPUT' or 'OUTPUT'")
        self._name = name
        self._in_out = in_out
    def __repr__(self) -> str:
        return self._name
    @property
    def name(self):
        return self._name
    @property
    def in_out(self):
        return self._in_out

class Interface:
    def __init__(self, items_tree:list[NodeItem]):
        self._items_tree = items_tree
    def __repr__(self) -> str:
        return '\n'.join(str(item) for item in self.items_tree)
    @property
    def items_tree(self):
        return self._items_tree
    def add_item(self, item:NodeItem):
        self._items_tree.append(item)

class NodeTree:
    def __init__(self, interface):
        self._interface = interface
    @property
    def interface(self):
        return self._interface


item1 = NodeItem("GeoIn", "INPUT")
item2 = NodeItem("Value", "INPUT")
item5 = NodeItem("GeoOut", "OUTPUT")
item6 = NodeItem("UV", "OUTPUT")

nodetree = NodeTree(Interface([item1, item2, item5, item6]))
NodeTree.inputs = property(lambda self: [item for item in self.interface.items_tree if item.in_out == "INPUT"])
NodeTree.outputs = property(lambda self: [item for item in self.interface.items_tree if item.in_out == "OUTPUT"])

item3 = NodeItem("FloatX", "INPUT")
item4 = NodeItem("FloatY", "INPUT")
nodetree.interface.add_item(item3)
nodetree.interface.add_item(item4)
print(nodetree.inputs)
print(nodetree.outputs)

def main():
    import bpy
    # Old Way of getting inputs (bpy <= 3.5.0)
    nodetree_inputs = bpy.types.GeometryNodeTree.inputs
    nodetree_outputs = bpy.types.GeometryNodeTree.outputs
    
    # New way (bpy >= 4.0.0)
    nodetree_inputs = [item for item in bpy.types.GeometryNodeTree.interface.items_tree if item.in_out == "INPUT"]
    nodetree_outputs = [item for item in bpy.types.GeometryNodeTree.interface.items_tree if item.in_out == "OUTPUT"]
    
    # Injecting the new way into the old property definition (bpy >= 4.0.0)
    bpy.types.GeometryNodeTree.inputs = property(lambda self: [item for item in self.interface.items_tree if item.in_out == "INPUT"])
    bpy.types.GeometryNodeTree.outputs = property(lambda self: [item for item in self.interface.items_tree if item.in_out == "OUTPUT"])
    nodetree_inputs = bpy.types.GeometryNodeTree.inputs
    nodetree_outputs = bpy.types.GeometryNodeTree.outputs