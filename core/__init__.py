if "bpy" not in locals():
    import bpy
    from . import receiver
    from . import animations
    from . import animation_lists
    from . import utils
    from . import state_manager
else:
    import importlib
    importlib.reload(receiver)
    importlib.reload(animations)
    importlib.reload(animation_lists)
    importlib.reload(utils)
    importlib.reload(state_manager)