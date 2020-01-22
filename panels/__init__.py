if "bpy" not in locals():
    import bpy
    from . import main
    from . import objects
    from . import command_api
else:
    import importlib
    importlib.reload(main)
    importlib.reload(objects)
    importlib.reload(command_api)