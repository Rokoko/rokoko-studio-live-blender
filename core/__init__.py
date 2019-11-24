if "bpy" not in locals():
    import bpy
    from . import receiver
    from . import animations
    from . import animation_lists
else:
    import importlib
    importlib.reload(receiver)
    importlib.reload(animations)
    importlib.reload(animation_lists)