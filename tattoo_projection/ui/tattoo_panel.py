import bpy
from bpy_extras.io_utils import ImportHelper
# from bpy_extras.asset_utils import AssetBrowserPanel
from bpy.props import StringProperty, BoolProperty
from bpy.types import Context, Panel, Operator
from ops.nodegroups import *

C = bpy.context
D = bpy.data

class CT_PT_TattooPanel(Panel):
    bl_label = "Tattoo Panel"
    bl_idname = "CT_PT_TATTOO_PANEL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = ''
    bl_category = "CTools"
    bl_order = 1
        
    def draw(self, context):
        scene = C.scene
        layout = self.layout
        col = layout.column(align=True)
        col.scale_y = 1.3
        col.scale_x = 1.3
        proj_obj = D.objects.get(TATTOO_MESH)
        bake_obj = D.objects.get(SOURCE_MESH)
        setup = bake_obj and proj_obj
        setup_text = "Setup" if not setup else "Re-Setup"
        setup_icon = "PLAY" if not setup else "FILE_REFRESH"
        row = col.row(align=True)
        row.operator("ct.setup", text=setup_text, icon=setup_icon)
        row.operator("ct.remove", text="Remove", icon="X")
        col.operator("ct.setup", text="Bake Texture", icon="FILE_REFRESH")
        
        if not bake_obj and not proj_obj: 
            return
          
        
class CT_PT_SubPanel(Panel):
    bl_idname = "CT_PT_TATTOO_SUBPANEL"
    bl_parent_id = "CT_PT_TATTOO_PANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_options = {'DEFAULT_CLOSED'}
    # bl_order = 0

    
class CT_SubPanel_Inputs(CT_PT_SubPanel, Panel):
    bl_label = "Inputs"
    bl_idname = CT_PT_SubPanel.bl_idname + "_INPUTS"
    # bl_options = {'HIDE_HEADER'}
        
    def draw(self, context):
        scene = C.scene
        obj = scene.obj_ptr
        source_ptr = scene.source_ptr
        tattoo_ptr = scene.tattoo_ptr
        bake_obj = D.objects.get("_tattoo_baker")
        proj_obj = D.objects.get("_tattoo_projector")
        if not bake_obj or not proj_obj:
            return self.layout.label(text="Run Setup")
        if not bake_obj.modifiers or not proj_obj.modifiers:
            return self.layout.label(text="Run Setup")
        
        bake_mod = bake_obj.modifiers.get(MODIFIER_NAME)
        proj_mod = proj_obj.modifiers.get(MODIFIER_NAME)
        
        layout = self.layout
        row = layout.row(align=True)
        col_labels = row.column(align=True)
        col_props = row.column(align=True)
        row.scale_y = 1.3
        row.scale_x = 1.1
        col_labels.alignment = 'LEFT'
        
        col_labels.label(text="Source Object")
        col_labels.label(text="Source Image")
        col_labels.label(text="Tattoo Image")
        
        col_props.prop(scene, "obj_ptr", text="")
        
        row_source = col_props.row(align=True)
        row_source.prop(scene, "source_ptr", text="")
        source_op = row_source.operator("ct.open_image", text="", icon="FILE_FOLDER")
        source_op.image_ptr = "source_ptr"
        
        row_tattoo = col_props.row(align=True)
        row_tattoo.prop(scene, "tattoo_ptr", text="")
        tattoo_op = row_tattoo.operator("ct.open_image", text="", icon="FILE_FOLDER")
        tattoo_op.image_ptr = "tattoo_ptr"

    
class CT_SubPanel_Projector(CT_PT_SubPanel, Panel):
    bl_label = "Projector"
    bl_idname = CT_PT_SubPanel.bl_idname + "_PROJECTOR"
    # bl_options = {'HIDE_HEADER'}
    def draw_header_preset(self, context):
        row = self.layout.row(align=True)
        row.scale_x = 1.1
        proj_mod = get_GeometryNodes_modifier(TATTOO_MESH)
        proj_obj = D.objects.get(TATTOO_MESH)
        if not proj_mod:
            return
        
        button = row.row(align=False)
        op = button.operator("ct.select_object", text="", icon='RESTRICT_SELECT_OFF', emboss=False)
        op.pattern = TATTOO_MESH
        row.prop(proj_mod, '["Socket_26"]', text="", icon='IMAGE_ALPHA' if proj_mod["Socket_26"] else 'IMAGE_ALPHA', emboss=True)
        row.prop(proj_obj, "show_wire", text="", toggle=True, icon='SHADING_WIRE') if proj_obj else None
        row.prop(proj_mod, 'show_viewport', text="", emboss=True)
            
    def draw(self, context):
        scene = C.scene
        bake_obj = D.objects.get("_tattoo_baker")
        proj_obj = D.objects.get("_tattoo_projector")
        if not bake_obj or not proj_obj:
            return self.layout.label(text="Run Setup")
        if not bake_obj.modifiers or not proj_obj.modifiers:
            return self.layout.label(text="Run Setup")
        bake_mod = bake_obj.modifiers.get(MODIFIER_NAME)
        proj_mod = proj_obj.modifiers.get(MODIFIER_NAME)
        if not proj_mod:
            return self.layout.label(text="No Tattoo Projector found")
        
        layout = self.layout
        col = layout.column(align=True)
        col.scale_y = 1.3
        
        if proj_obj.hide_get():
            col.label(text="Object is hidden")
            col.operator("ct.unhide_object", text="Unhide Object").pattern = "_tattoo_projector"
            return
        # Projector
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(proj_mod, '["Socket_6"]', text="Resolution", icon='MESH_GRID')
        col.prop(proj_mod, '["Socket_14"]', text="Wrap Iterations")
        col.prop(proj_mod, '["Socket_15"]', text="Wrap Offset")
        col.prop(proj_mod, '["Socket_18"]', text="Ignore Backfaces")
        col.prop(proj_mod, '["Socket_27"]', text="Width")
        col.prop(proj_mod, '["Socket_28"]', text="Height")
        
        
        
class CT_SubPanel_Baker(CT_PT_SubPanel, Panel):
    bl_label = "Baker"
    bl_idname = CT_PT_SubPanel.bl_idname + "_BAKER"
    
    def draw_header_preset(self, context):
        row = self.layout.row(align=True)
        row.scale_x = 1.1
        bake_mod = get_GeometryNodes_modifier(SOURCE_MESH)
        bake_obj = D.objects.get(SOURCE_MESH)
        if bake_mod:
            row.prop(bake_mod, '["Socket_7"]', text="", toggle=False, icon='UV')
            row.prop(bake_obj, "show_wire", text="", toggle=True, icon='SHADING_WIRE') if bake_obj else None
            row.prop(bake_mod, 'show_viewport', text="", emboss=True)
            
        
    def draw(self, context):
        bake_obj = D.objects.get("_tattoo_baker")
        proj_obj = D.objects.get("_tattoo_projector")
        if not bake_obj or not proj_obj:
            return self.layout.label(text="Run Setup")
        if not bake_obj.modifiers or not proj_obj.modifiers:
            return self.layout.label(text="Run Setup")
        bake_mod = bake_obj.modifiers.get(MODIFIER_NAME)
        proj_mod = proj_obj.modifiers.get(MODIFIER_NAME)
        if not proj_mod:
            return self.layout.label(text="No Tattoo Projector found")
        
        layout = self.layout
        col = layout.column(align=True)
        col.scale_y = 1.3
        
        if bake_obj.hide_get():
            col.label(text="Object is hidden")
            col.operator("ct.unhide_object", text="Unhide Object").pattern = "_tattoo_baker"
            return
        
        # Shaders
        section_shader = col.split(align=True, factor=0.3)
        shader_labels = section_shader.column(align=True)
        shader_props = section_shader.column(align=True)
        shader_labels.label(text="Shader")
        
        shader_props.prop(proj_mod, '["Socket_20"]', text="Use Alpha Channel", toggle=True, icon='IMAGE_RGB_ALPHA')
        shader_props.prop(proj_mod, '["Socket_21"]', text="Invert Alpha", toggle=True, icon='IMAGE_ALPHA')
        
        color_row = shader_props.split(align=True, factor=0.75)
        color_row.prop(proj_mod, '["Socket_22"]', text="Custom Color", toggle=True, icon='IMAGE_DATA' if proj_mod["Socket_22"] else 'COLOR')
        color_prop = color_row.row(align=True)
        color_prop.enabled = proj_mod["Socket_22"]
        color_prop.prop(proj_mod, '["Socket_23"]', text="")
        
        shader_props.prop(get_Material(SOURCE_MAT).node_tree.nodes['Mix'], 'blend_type', text="", icon='NODE_MATERIAL')
        shader_props.separator(factor=0.5)
        
        
class OperatorWithFileSelect(Operator, ImportHelper):
    bl_idname = "ct.open_image"
    bl_label = "Open Image"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    filter_glob: StringProperty(default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp', options={'HIDDEN'})
    image_ptr: StringProperty(name="Image", options={'HIDDEN'})
    
    def execute(self, context):
        fp = self.properties.filepath
        if not getattr(C.scene, self.image_ptr):
            return {"CANCELLED"}
        img = bpy.data.images.load(fp, check_existing=True)
        setattr(C.scene, self.image_ptr, img)
        return {"FINISHED"}


class ColorPicker(Operator):
    bl_idname = "ct.color_picker"
    bl_label = "Color Picker"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    color_ptr: StringProperty(name="Color", options={'HIDDEN'})
    
    def execute(self, context):
        return {"FINISHED"}
        
class CT_Select_Object(Operator):
    bl_label = "Select Object"
    bl_idname = "ct.select_object"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    pattern: StringProperty(name="Pattern", options={'HIDDEN'})
    def execute(self, context):
        obj = bpy.data.objects.get(self.pattern)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        return {"FINISHED"}

class CT_Unhide_Object(Operator):
    bl_label = "Unhide Object"
    bl_idname = "ct.unhide_object"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    pattern: StringProperty(name="Pattern", options={'HIDDEN'})
    def execute(self, context):
        obj = bpy.data.objects.get(self.pattern)
        obj.hide_set(False)
        obj.select_set(True)
        return {"FINISHED"}

panel_classes = (
    CT_PT_TattooPanel,
    CT_SubPanel_Inputs,
    CT_SubPanel_Projector,
    OperatorWithFileSelect,
    CT_SubPanel_Baker,
    CT_Select_Object,
    CT_Unhide_Object
)