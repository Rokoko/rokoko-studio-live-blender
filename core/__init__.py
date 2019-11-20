if "bpy" not in locals():
    import bpy
    from . import receiver
    from . import animations
else:
    import importlib
    importlib.reload(receiver)
    importlib.reload(animations)