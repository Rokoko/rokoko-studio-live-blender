if "bpy" not in locals():
    import bpy
    from . import receiver
    from . import detector
    from . import recorder
else:
    import importlib
    importlib.reload(receiver)
    importlib.reload(detector)
    importlib.reload(recorder)