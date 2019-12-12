if "bpy" not in locals():
    import bpy
    from . import receiver
    from . import detector
    from . import recorder
    from . import actor
else:
    import importlib
    importlib.reload(receiver)
    importlib.reload(detector)
    importlib.reload(recorder)
    importlib.reload(actor)