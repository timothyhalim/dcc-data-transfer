import sys
import os

# Blender addon info
bl_info = {
    "name" : "Camera Transfer",
    "author" : "Timothy Halim",
    "description" : "Camera Transfer between DCC software",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Studio"
}

if os.path.basename(sys.argv[0]).lower().startswith("blender"):
    # Blender addon import
    import bpy
    
    module_names = [ 'operator', 'properties', 'gui' ]

    import importlib

    module_full_names = [ f"{__name__}.blender.{module}" for module in module_names ]

    for module in module_full_names:
        if module in sys.modules:
            importlib.reload(sys.modules[module])
        else:
            locals()[module] = importlib.import_module(module)
            setattr(locals()[module], 'module_names', module_full_names)

    def register():
        for module in module_full_names:
            if module in sys.modules:
                if hasattr(sys.modules[module], 'register'):
                    sys.modules[module].register()

    def unregister():
        for module in module_full_names:
            if module in sys.modules:
                if hasattr(sys.modules[module], 'unregister'):
                    sys.modules[module].unregister()