import bpy

def popup_window(title:str = "Error", text:str|list = "Error message", icon:str = 'ERROR'):
    """Each element in text is a line in the popup window"""
    def popup(self, context):
        lines = text if type(text) == list else text.split("\n") 
        for line in lines:
            row = self.layout.row()
            row.label(text=line)
    bpy.context.window_manager.popup_menu(popup, title=title, icon=icon) 

def _vertex_colors_to_materials():
    """Use case?"""
    # Get the active object and its vertex colors
    obj = bpy.context.active_object
    vertex_colors = obj.data.vertex_colors.active.data

    # Create a dictionary to store faces with the same vertex color
    face_dict = {}

    # Loop through all the polygons in the object
    for i, poly in enumerate(obj.data.polygons):
        
        # Get the vertex colors for each vertex in the polygon
        vertex_colors_poly = [(vertex_colors[poly.loop_indices[i]].color[0],
                            vertex_colors[poly.loop_indices[i]].color[1],
                            vertex_colors[poly.loop_indices[i]].color[2],
                            vertex_colors[poly.loop_indices[i]].color[3]) for i in range(len(poly.vertices))]
        
        # vertex_colors_poly[0] is first vertex of polygon
        if all(color == vertex_colors_poly[0] for color in vertex_colors_poly):
            face_dict.setdefault(vertex_colors_poly[0], []).append(poly.index)
        
    # Assign the material to the faces with the same vertex color
    for i, (color, face_indices) in enumerate(face_dict.items()):
        material_name = f"vertex_colors.{i}"
        material = bpy.data.materials.get(material_name)
        if material is None:
            material = bpy.data.materials.new(material_name)
        obj.data.materials.append(material)
        bpy.data.materials.new(material_name)
        polys = obj.data.polygons
        for poly_index in face_indices:
            polys[poly_index].material_index = i

def convert_curve_haircurve():
    def hair_curves_to_poly_spline(obj):
        # Get the curves, modifiers and name of the hair object.
        hair_curves = obj.data.curves
        attributes = obj.data.attributes
        modifiers = obj.modifiers
        name = obj.name
        collections = [col for col in obj.users_collection]
        #todo? matr = obj.matrix_world

        #TODO bezier curve attributes
        # bpy.context.active_object.data.attributes['curve_type']
        # bpy.context.active_object.data.attributes['handle_type_left']
        # bpy.context.active_object.data.attributes['handle_type_right']
        # bpy.context.active_object.data.attributes['resolution']
        # bpy.context.active_object.data.attributes['handle_left']
        # bpy.context.active_object.data.attributes['handle_right']
        
        #TODO nurbs curve attributes
        # bpy.context.active_object.data.attributes['nurbs_order']
        # bpy.context.active_object.data.attributes['knots_mode']
        # bpy.context.active_object.data.attributes['normal_mode']
        
            
        # Create new curve object
        spline_data = bpy.data.curves.new("_temp", type='CURVE')
        spline_data.dimensions = '3D'
        spline_obj = bpy.data.objects.new("_temp", spline_data)
        for col in collections:
            col.objects.link(spline_obj)

        # Get all the curve coordinates, tilt and radius.
        tilt = 'tilt' in attributes
        radius = 'radius' in attributes
        curve_coords = [[point.position for point in curve.points] for curve in hair_curves]
        point_tilt = [tilt.value for tilt in attributes['tilt'].data] if tilt else None
        point_radius = [radius.value for radius in attributes['radius'].data] if radius else None
        
        # Create a new spline for each curve and add the coordinates, tilt and radius
        indx = 0
        for coords in curve_coords:
            spline = spline_obj.data.splines.new('POLY')
            points = spline.points
            points.add(len(coords)-1)
            for j, point in enumerate(points):
                point.co = coords[j].to_4d()
                if point_tilt: # Set tilt if not None
                    point.tilt = point_tilt[indx]
                if point_radius: # Set radius if not None
                    point.radius = point_radius[indx]
                indx += 1
        
        # Copy the modifiers to the new hair object
        spline_obj.select_set(True)
        for modifier in modifiers:
            bpy.ops.object.modifier_copy_to_selected(modifier=modifier.name)

        # Delete the old hair object
        bpy.data.hair_curves.remove(obj.data)
        # Rename the new hair object
        spline_obj.name, spline_obj.data.name = name, name

        # Convert the new hair object to a poly spline 
        bpy.context.view_layer.objects.active = spline_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.spline_type_set(type='POLY')
        bpy.ops.object.mode_set(mode='OBJECT')

    def spline_to_hair_curves(obj):
        # Get spline name
        name = obj.name
        obj.select_set(False)
        collections = [col for col in obj.users_collection]
        
        #TODO --------------------
        if False in [spline.type == 'POLY' for spline in obj.data.splines]:
            return popup_window(text="Only 'poly' splines are supported for now")
        
        # Create new curve object
        spline_obj = bpy.data.objects.new("_temp", obj.data)
        for col in collections:
            col.objects.link(spline_obj)
        
        # Convert to hair curves
        bpy.context.view_layer.objects.active = spline_obj
        spline_obj.select_set(True)
        bpy.ops.object.convert(target='CURVES')

        # Copy modifiers to new hair object
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        for modifier in obj.modifiers:
            bpy.ops.object.modifier_copy_to_selected(modifier=modifier.name)
            
        # Remove old spline object and rename new hair object
        bpy.data.curves.remove(obj.data)
        spline_obj.name, spline_obj.data.name = name, name
        bpy.context.view_layer.objects.active = spline_obj

    #TODO --------------------
    #todo - Support for bezier and nurbs curves

    obj = bpy.context.active_object
    assert obj.type in ('CURVES', 'CURVE'), "Select a curve or hair curve object"
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    if obj.type == 'CURVES':
        hair_curves_to_poly_spline(obj)
    elif obj.type == 'CURVE':
        spline_to_hair_curves(obj)

def weight_transfer():
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

def apply_modifiers(modifierName:str = None):
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

def sharpedges_from_attributes():
    obj = bpy.context.active_object
    edges = obj.data.edges
    sharp_edge_attr = [attr for attr in obj.data.attributes if attr.data_type == 'BOOLEAN' and attr.domain == 'EDGE']
    
    if not sharp_edge_attr:
        popup_window(text=f"No valid attribute found in '{obj.data.name}'.\nThe attribute type must be 'EDGE' & 'BOOLEAN'")
    # assert sharp_edge_attr, "No attribute found. The attribute type must be 'EDGE' & 'BOOLEAN'"
    
    for attr in sharp_edge_attr:
        for i, attr_edge in enumerate(attr.data):
            edges[i].use_edge_sharp = attr_edge.value

def realize_object():
    def realize():
        # Created with: https://github.com/BrendanParmer/NodeToPython 
        if "_RealizeObject" in bpy.data.node_groups:
            realizeobject = bpy.data.node_groups['_RealizeObject']
        else:
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
        object_info.transform_space = 'RELATIVE'
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

    modifier = realize()

    obj = bpy.context.active_object
    collections = [col for col in obj.users_collection]
    
    mesh = bpy.data.meshes.new(obj.name+"_mesh")
    new_obj = bpy.data.objects.new(obj.name+"_mesh", mesh)
    for col in collections:
        col.objects.link(new_obj)

    bpy.context.view_layer.objects.active = new_obj
    bpy.ops.object.modifier_add(type='NODES')
    bpy.context.active_object.modifiers[-1].node_group = bpy.data.node_groups[modifier]
    bpy.context.active_object.modifiers[-1]['Input_2'] = bpy.data.objects[obj.name]
    bpy.ops.object.modifier_apply(modifier="GeometryNodes")

    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.active_object.select_set(True)

    obj = bpy.context.active_object
    attributes = obj.data.attributes

    if bpy.app.version >= (3, 5, 0):
        attr_uvs = [i for i, attr in enumerate(attributes) if attr.data_type == 'FLOAT2' and attr.domain == 'CORNER' and 'UV' in attr.name]
    else:
        attr_uvs = [i for i, attr in enumerate(attributes) if attr.data_type == 'FLOAT_VECTOR' and attr.domain == 'CORNER' and 'UV' in attr.name]
    obj_uvs = obj.data.uv_layers

    if len(attr_uvs) == 1 and len(obj_uvs) == 0:
        attributes.active_index = attr_uvs[0]
        bpy.ops.geometry.attribute_convert(mode='UV_MAP')