if "bpy" not in locals():
    import bpy
    from . import main
else:
    import importlib
    importlib.reload(main)