import bpy

# By Carlsu https://github.com/carls3d
# Made to be injected as a script in a class

def realizeobject():
    # Created thanks to: https://github.com/BrendanParmer/NodeToPython 
    realizeobject = bpy.data.node_groups.new(type = "GeometryNodeTree", name = "_RealizeObject")
    realizeobject.outputs.new("NodeSocketGeometry", "Geometry")
    realizeobject.inputs.new("NodeSocketGeometry", "Geometry")
    realizeobject.inputs.new("NodeSocketObject", "Object")

    group_input = realizeobject.nodes.new("NodeGroupInput")
    group_input.location = (-340.0, 0.0)
    group_input.width, group_input.height = 140.0, 100.0

    object_info = realizeobject.nodes.new("GeometryNodeObjectInfo")
    object_info.location = (-120.77420043945312, 0.0)
    object_info.width, object_info.height = 140.0, 100.0
    object_info.transform_space = 'ORIGINAL'
    object_info.inputs[1].default_value = False

    realize_instances = realizeobject.nodes.new("GeometryNodeRealizeInstances")
    realize_instances.location = (60.38710021972656, 0.0)
    realize_instances.width, realize_instances.height = 140.0, 100.0

    group_output = realizeobject.nodes.new("NodeGroupOutput")
    group_output.location = (241.54840087890625, 0.0)
    group_output.width, group_output.height = 140.0, 100.0

    realizeobject.links.new(group_input.outputs["Object"], object_info.inputs["Object"])
    realizeobject.links.new(realize_instances.outputs["Geometry"], group_output.inputs["Geometry"])
    realizeobject.links.new(object_info.outputs["Geometry"], realize_instances.inputs["Geometry"])

    return realizeobject.name


modifier = realizeobject()

obj = bpy.context.view_layer.objects.active
mesh = bpy.data.meshes.new(obj.name+"_mesh")
new_obj = bpy.data.objects.new(obj.name+"_mesh", mesh)

bpy.context.collection.objects.link(new_obj)
bpy.context.view_layer.objects.active = new_obj

bpy.ops.object.modifier_add(type='NODES')
bpy.context.active_object.modifiers[-1].node_group = bpy.data.node_groups[modifier]
bpy.context.active_object.modifiers[-1]['Input_2'] = bpy.data.objects[obj.name]
bpy.ops.object.modifier_apply(modifier="GeometryNodes")

new_obj.select_set(True)
