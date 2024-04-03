import bpy
from addon_utils import enable, disable

class BeforeAfterDecoratorFactory:
    def __init__(self, before = None, after = None):
        self.before = before
        self.after = after
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            self.after() if self.after else None
            result = func(*args, **kwargs)
            self.before() if self.before else None
            return result
        return wrapper
    
def tmp_serpens_register():
    if __name__ == "tmp_serpens":
        import sys
        serpens_addon = bpy.context.scene.sn.addon_name
        addon_identifier = serpens_addon.lower().replace(" ", "_")
        # Disable addon
        if addon_identifier in sys.modules:
            print(f" → Workfile for '{serpens_addon}' detected, unregistering '{serpens_addon}'...")
            disable(addon_identifier)

def tmp_serpens_unregister():
    if __name__ == "tmp_serpens":
        import sys
        serpens_addon = bpy.context.scene.sn.addon_name
        addon_identifier = serpens_addon.lower().replace(" ", "_")
        # Enable addon
        if addon_identifier in sys.modules:
            print(f" → '{addon_identifier}' module detected, registering '{serpens_addon}'...")
            enable(addon_identifier)

register_decorators:list[BeforeAfterDecoratorFactory] = [
    BeforeAfterDecoratorFactory(after=tmp_serpens_register)
]

unregister_decorators:list[BeforeAfterDecoratorFactory] = [
    BeforeAfterDecoratorFactory(before=tmp_serpens_unregister)
]


