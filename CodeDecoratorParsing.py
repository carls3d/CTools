# This is injected into the serpens code and is required for "SerpensRegisterInjetion" to function
# → "AppData\Roaming\Blender Foundation\Blender\4.0\scripts\addons\blender_visual_scripting_addon\nodes\compiler.py"

DECORATOR_FACTORY = """
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
"""
def format_decorator_factory(_code:str) -> tuple[str, str, str]:
    import ast
    tree = ast.parse(_code)
    
    def find_variables(node, variable_name):
        for child in ast.iter_child_nodes(node):
            # Check for both Assign and AnnAssign nodes
            if isinstance(child, (ast.Assign, ast.AnnAssign)) and hasattr(child, 'targets'):
                # Assign nodes
                for target in child.targets:
                    if isinstance(target, ast.Name) and target.id == variable_name:
                        return child.value
            elif isinstance(child, ast.AnnAssign):
                # AnnAssign nodes
                if isinstance(child.target, ast.Name) and child.target.id == variable_name:
                    return child.value
            result = find_variables(child, variable_name)
            if result is not None:
                return result
        return None
    def code_factory_decorators(decorators_node:ast.List) -> list:
        code_decorators = []
        if decorators_node and isinstance(decorators_node, ast.List):
            for element in decorators_node.elts:
                if isinstance(element, ast.Call) and isinstance(element.func, ast.Name):
                    decorator_name = element.func.id
                    parameters = ", ".join([f"{keyword.arg}={keyword.value.id}" for keyword in element.keywords])
                    code_decorators.append(f"{decorator_name}({parameters})")
        return code_decorators
    def class_exists(node, class_name):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef) and child.name == class_name:
                return True
            elif class_exists(child, class_name):
                return True
        return False
    

    register_decorators_node = find_variables(tree, "register_decorators")
    unregister_decorators_node = find_variables(tree, "unregister_decorators")

    code_register_decorators = code_factory_decorators(register_decorators_node)
    code_unregister_decorators = code_factory_decorators(unregister_decorators_node)

    # Generate the injection string
    reg_injection_string = "\n".join([f"@{decorator}" for decorator in code_register_decorators])
    unreg_injection_string = "\n".join([f"@{decorator}" for decorator in code_unregister_decorators])
    
    # Add decorator factory if it doesn't exist
    decorator_factory = ""
    if not class_exists(tree, "BeforeAfterDecoratorFactory"):
        if code_register_decorators or code_unregister_decorators:
            decorator_factory = DECORATOR_FACTORY
    
    return reg_injection_string, unreg_injection_string, decorator_factory

code = """
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
def my_func1():
    print("before")
def my_func2():
    print("after")
def my_func3():
    print("after")

register_decorators:list[BeforeAfterDecoratorFactory] = [
# register_decorators:list = [
    BeforeAfterDecoratorFactory(before=my_func1),
    BeforeAfterDecoratorFactory(after=my_func2)
]
unregister_decorators = [
# unregister_decorators:list = [
    BeforeAfterDecoratorFactory(before=my_func1, after=my_func3)
]
"""
def format_single_file():
    ...
    sn:...
    imports:str
    imperative:str
    main:str
    register:str
    unregister:str
    indent_code:str

    if sn.is_exporting:
        code = f"{imports}\n{imperative}\n\n{main}\n\ndef register():\n{indent_code(register, 1, 0)}\n\ndef unregister():\n{indent_code(unregister, 1, 0)}\n\n"
    else:
        reg_decos, unreg_decos, decorator_factory = "", "", ""
        try:
            reg_decos, unreg_decos, decorator_factory = format_decorator_factory(main)
            # print("! → ",reg_decos, unreg_decos, decorator_factory)
        except Exception as e:
            print("? →", e)
        
        code = f"{imports}\n{imperative}\n{decorator_factory}\n\n{main}\n{reg_decos}\ndef register():\n{indent_code(register, 1, 0)}\n{unreg_decos}\ndef unregister():\n{indent_code(unregister, 1, 0)}\n\n"
    ...