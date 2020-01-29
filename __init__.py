# Important plugin info for Blender
bl_info = {
    'name': 'Rokoko Studio Live for Blender',
    'author': 'Rokoko Electronics ApS',
    'category': 'Animation',
    'location': 'View 3D > Tool Shelf > Rokoko',
    'description': 'Stream your Rokoko Studio animations directly into Blender',
    'version': (1, 0),
    'blender': (2, 80, 0),
    'wiki_url': 'https://rokoko.freshdesk.com/support/solutions/folders/47000761699',
}

dev_branch = False

# If first startup of this plugin, load all modules normally
# If reloading the plugin, use importlib to reload modules
# This lets you do adjustments to the plugin on the fly without having to restart Blender
import sys
if "bpy" not in locals():
    import bpy
    from . import core
    from . import panels
    from . import operators
    from . import properties
    from . import updater_ops
    from . import updater
else:
    import importlib
    importlib.reload(core)
    importlib.reload(panels)
    importlib.reload(operators)
    importlib.reload(properties)
    importlib.reload(updater_ops)
    importlib.reload(updater)


# List of all buttons and panels
classes = [
    panels.main.ReceiverPanel,
    panels.objects.ObjectsPanel,
    panels.command_api.CommandPanel,
    panels.updater.UpdaterPanel,
    panels.info.InfoPanel,
    operators.receiver.ReceiverStart,
    operators.receiver.ReceiverStop,
    operators.recorder.RecorderStart,
    operators.recorder.RecorderStop,
    operators.detector.DetectFaceShapes,
    operators.detector.DetectActorBones,
    operators.actor.InitTPose,
    operators.actor.ResetTPose,
    operators.actor.PrintCurrentPose,
    operators.command_api.CommandTest,
    operators.command_api.StartCalibration,
    operators.command_api.Restart,
    operators.command_api.StartRecording,
    operators.command_api.StopRecording,
    operators.info.LicenseButton,
    operators.info.RokokoButton,
    operators.info.DocumentationButton,
    operators.info.ForumButton,

]


def check_unsupported_blender_versions():
    # Don't allow Blender versions older than 2.80
    if bpy.app.version < (2, 80):
        unregister()
        sys.tracebacklimit = 0
        raise ImportError('\n\nBlender versions older than 2.80 are not supported by Rokoko Studio Live. '
                          '\nPlease use Blender 2.80 or later.'
                          '\n')

    # Versions 2.80.0 to 2.80.74 are beta versions, stable is 2.80.75
    if (2, 80, 0) <= bpy.app.version < (2, 80, 75):
        unregister()
        sys.tracebacklimit = 0
        raise ImportError('\n\nYou are still on the beta version of Blender 2.80!'
                          '\nPlease update to the release version of Blender 2.80.'
                          '\n')


# register and unregister all classes
def register():
    print("\n### Loading Rokoko Studio Live...")

    # Check for unsupported Blender versions
    check_unsupported_blender_versions()

    # Register updater and check for Rokoko Studio Live updates
    updater_ops.register(bl_info, dev_branch)

    # Register all classes
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register all custom properties
    properties.register()

    # Load custom icons
    core.icon_manager.load_icons()

    print("### Loaded Rokoko Studio Live successfully!\n")


def unregister():
    print("### Unloading Rokoko Studio Live...")

    # Unregister updater
    updater_ops.unregister()

    # Shut down receiver if the plugin is disabled while it is running
    if operators.receiver.receiver_enabled:
        operators.receiver.ReceiverStart.force_disable()

    # Unregister all classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # Unload all custom icons
    core.icon_manager.unload_icons()

    print("### Unloaded Rokoko Studio Live successfully!\n")


if __name__ == '__main__':
    register()
