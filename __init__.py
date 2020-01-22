# Important plugin info for Blender
from mathutils import Quaternion

bl_info = {
    'name': 'Rokoko Studio Live for Blender',
    'author': 'Rokoko',
    'category': 'Animation',
    'location': 'View 3D > Tool Shelf > Rokoko',
    'description': 'Stream your Rokoko Studio animations directly into Blender',
    'version': (0, 1),
    'blender': (2, 80, 0),
}

# If first startup of this plugin, load all modules normally
# If reloading the plugin, use importlib to reload modules
# This lets you do adjustments to the plugin on the fly without having to restart Blender
if "bpy" not in locals():
    import bpy
    from . import core
    from . import panels
    from . import operators
    from . import properties
else:
    import importlib
    importlib.reload(core)
    importlib.reload(panels)
    importlib.reload(operators)
    importlib.reload(properties)


# List of all buttons and panels
classes = [
    panels.main.ReceiverPanel,
    panels.objects.ObjectsPanel,
    panels.command_api.CommandPanel,
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
]


# register and unregister all classes
def register():
    print("\n### Loading Rokoko Studio Live...")

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
