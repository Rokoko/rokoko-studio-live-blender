if "bpy" not in locals():
    import bpy
    from . import receiver
else:
    import importlib
    importlib.reload(receiver)