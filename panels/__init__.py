if "bpy" not in locals():
    import bpy
    from . import main
    from . import objects
    from . import command_api
    from . import retargeting
    from . import updater
    from . import info
else:
    import importlib

    importlib.reload(main)
    importlib.reload(objects)
    importlib.reload(command_api)
    importlib.reload(retargeting)
    importlib.reload(updater)
    importlib.reload(info)
