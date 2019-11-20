if "bpy" not in locals():
    import bpy
    from . import main
    from . import objects
else:
    import importlib
    importlib.reload(main)
    importlib.reload(objects)