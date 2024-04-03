import bpy
from bpy.types import Operator
import addon_utils

class SCRIPT_OT_reload_addon(Operator):
    bl_idname = "script.reload_addon_module"
    bl_label = "Reload Addon Module"

    module: bpy.props.StringProperty(default="") # type: ignore

    def execute(self, context):
        default, state = addon_utils.check(self.module)
        if default and state:
            modules = bpy.utils._sys.modules.copy()
            m = modules.get(self.module)

            if m is not None:
                from importlib import reload
                m.unregister()
                m = modules[self.module] = reload(m)

                for n, sub in modules.items():
                    if n.startswith("%s." % self.module):
                        modules[n] = reload(sub)
                m.register()
        return {'CANCELLED'}