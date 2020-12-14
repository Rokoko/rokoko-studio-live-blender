if "bpy" not in locals():
    import bpy
    from . import receiver
    from . import animations
    from . import animation_lists
    from . import utils
    from . import state_manager
    from . import icon_manager
    from . import recorder
    from . import retargeting
    from . import detection_manager
    from . import fbx_patcher
    from . import login
    from . import live_data_manager
else:
    import importlib

    importlib.reload(receiver)
    importlib.reload(animations)
    importlib.reload(animation_lists)
    importlib.reload(utils)
    importlib.reload(state_manager)
    importlib.reload(icon_manager)
    importlib.reload(recorder)
    importlib.reload(retargeting)
    importlib.reload(detection_manager)
    importlib.reload(fbx_patcher)
    importlib.reload(login)
    importlib.reload(live_data_manager)
