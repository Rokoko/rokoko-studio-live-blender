# Important plugin info for Blender
bl_info = {
    'name': 'Rokoko Studio Live for Blender',
    'author': 'Rokoko Electronics ApS',
    'category': 'Animation',
    'location': 'View 3D > Tool Shelf > Rokoko',
    'description': 'Stream your Rokoko Studio animations directly into Blender',
    'version': (1, 4, 1),
    'blender': (2, 80, 0),
    'wiki_url': 'https://github.com/Rokoko/rokoko-studio-live-blender#readme',
}

beta_branch = True

first_startup = "bpy" not in locals()
import bpy
import sys

# Load the updater. Important to do early, so it is always loaded even in case of an error
from . import updater_ops
from . import updater
if not first_startup:
    import importlib
    importlib.reload(updater_ops)
    importlib.reload(updater)
# Register the updater
updater_ops.register()

# If first startup of this plugin, load all modules normally
# If reloading the plugin, use importlib to reload modules
# This lets you do adjustments to the plugin on the fly without having to restart Blender
from . import core
from . import panels
from . import operators
from . import properties

if first_startup:
    pass
else:
    import importlib
    importlib.reload(core)
    importlib.reload(panels)
    importlib.reload(operators)
    importlib.reload(properties)


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


# List of all buttons and panels
classes_logged_in = [  # These panels will only be loaded when the user is logged in
    panels.main.ReceiverPanel,
    panels.objects.ObjectsPanel,
    panels.command_api.CommandPanel,
    panels.retargeting.RetargetingPanel,
    panels.updater.UpdaterPanel,
    panels.info.InfoPanel,
]
classes_logged_out = [  # These panels will only be loaded when the user is logged out
    panels.login.LoginPanel,
    panels.updater.UpdaterPanel,
    panels.info.InfoPanel,
]
classes_always_enable = [  # These non-panels will always be loaded, all non-panel ui should go in here
    operators.login.LoginButton,
    operators.login.LogoutButton,
    operators.login.InstallLibsButton,
    operators.receiver.ReceiverStart,
    operators.receiver.ReceiverStop,
    operators.recorder.RecorderStart,
    operators.recorder.RecorderStop,
    operators.detector.DetectFaceShapes,
    operators.detector.DetectActorBones,
    operators.detector.SaveCustomShapes,
    operators.detector.SaveCustomBones,
    operators.detector.SaveCustomBonesRetargeting,
    operators.detector.ImportCustomBones,
    operators.detector.ExportCustomBones,
    operators.detector.ClearCustomBones,
    operators.detector.ClearCustomShapes,
    operators.actor.InitTPose,
    operators.actor.ResetTPose,
    operators.actor.PrintCurrentPose,
    operators.command_api.CommandTest,
    operators.command_api.StartCalibration,
    operators.command_api.Restart,
    operators.command_api.StartRecording,
    operators.command_api.StopRecording,
    operators.retargeting.BuildBoneList,
    operators.retargeting.AddBoneListItem,
    operators.retargeting.ClearBoneList,
    operators.retargeting.RetargetAnimation,
    panels.retargeting.RSL_UL_BoneList,
    panels.retargeting.BoneListItem,
    operators.info.LicenseButton,
    operators.info.RokokoButton,
    operators.info.DocumentationButton,
    operators.info.ForumButton,
    operators.info.ToggleRokokoIDButton,
]


def register_classes(classes, unregister_classes=[]):
    # Unregister classes_logged_in first
    for cls in reversed(unregister_classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            print("Error: Failed to unregister class", cls)
            pass

    register_count = 0
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
            register_count += 1
        except ValueError:
            print("Error: Failed to register class", cls)
            pass
    if register_count < len(classes):
        print('Skipped', len(classes) - register_count, 'ROKOKO classes_logged_in.')


def register():
    print("\n### Loading Rokoko Studio Live for Blender...")

    # Check for unsupported Blender versions
    check_unsupported_blender_versions()

    # Register logged out classes
    register_classes(classes_logged_out + classes_always_enable)

    # Register all custom properties
    properties.register()

    # Load custom icons
    core.icon_manager.load_icons()

    # Load bone detection list
    core.detection_manager.load_detection_lists()

    # Init fbx patcher
    core.fbx_patcher.start_fbx_patch_timer()

    # Add info to the login user and then login if all libraries are loaded
    core.login_manager.user.set_info(classes_logged_in, classes_logged_out, bl_info)
    if core.login_manager.loaded_all_libs:
        core.login_manager.user.auto_login()

    # Update updater info as late as possible, to ensure that errors are shown instead of being overwritten
    updater_ops.update_info(bl_info, beta_branch)

    print("### Loaded Rokoko Studio Live for Blender successfully!\n")


def unregister():
    print("### Unloading Rokoko Studio Live for Blender...")
    from . import updater_ops
    from . import operators
    from . import core

    # Unregister updater
    updater_ops.unregister()

    # Shut down receiver if the plugin is disabled while it is running
    if operators.receiver.receiver_enabled:
        operators.receiver.ReceiverStart.force_disable()

    # Unregister all classes
    for cls in reversed(classes_logged_out + classes_logged_in + classes_always_enable):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass

    # Unload all custom icons
    core.icon_manager.unload_icons()

    # Exit the logged-in user
    core.login_manager.user.quit()

    print("### Unloaded Rokoko Studio Live for Blender successfully!\n")


if __name__ == '__main__':
    register()
