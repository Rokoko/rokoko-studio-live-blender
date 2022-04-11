# Important plugin info for Blender
bl_info = {
    'name': 'Rokoko Studio Live for Blender',
    'author': 'Rokoko Electronics ApS',
    'category': 'Animation',
    'location': 'View 3D > Tool Shelf > Rokoko',
    'description': 'Stream your Rokoko Studio animations directly into Blender',
    'version': (1, 3, 0),
    'blender': (2, 80, 0),
    'wiki_url': 'https://rokoko.freshdesk.com/support/solutions/folders/47000761699',
}

beta_branch = True

import os
import sys
import pathlib
import pkgutil
import subprocess

# Install missing libraries
required = ["lz4", "websockets", "gql", "cryptography", "boto3"]
missing = [mod for mod in required if not pkgutil.find_loader(mod)]

if missing:
    print("Missing libaries:", missing)
    python = sys.executable

    # Get lib directory
    lib = os.path.join(pathlib.Path(python).parent.parent, "lib")
    print(lib)

    print("Ensuring pip")
    subprocess.call([python, "-m", "ensurepip", "--user"])

    print("Updating pip")
    subprocess.call([python, "-m", "pip", "install", "--upgrade", "pip"])

    print("Installing missing libaries:", missing)
    command = [python, '-m', 'pip', 'install', f"--target={str(lib)}", *missing]
    subprocess.check_call(command, stdout=subprocess.DEVNULL)
    print("Successfully installed missing libraries:", missing)

    # Reset console color
    print('\033[39m')

# If first startup of this plugin, load all modules normally
# If reloading the plugin, use importlib to reload modules
# This lets you do adjustments to the plugin on the fly without having to restart Blender
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
classes = [  # These panels will only be loaded when the user is logged in
    panels.main.ReceiverPanel,
    panels.objects.ObjectsPanel,
    panels.command_api.CommandPanel,
    panels.retargeting.RetargetingPanel,
    panels.updater.UpdaterPanel,
    panels.info.InfoPanel,
]
classes_login = [  # These panels will only be loaded when the user is logged out
    panels.login.LoginPanel,
    panels.updater.UpdaterPanel,
    panels.info.InfoPanel,
]
classes_always_enable = [  # These non-panels will always be loaded, all non-panel ui should go in here
    operators.login.LoginButton,
    operators.login.RegisterButton,
    operators.login.LogoutButton,
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
    print("\n### Loading Rokoko Studio Live for Blender...")

    # Check for unsupported Blender versions
    check_unsupported_blender_versions()

    # Register updater and check for Rokoko Studio Live updates
    updater_ops.register(bl_info, beta_branch)

    # Check if the user is logged in, show the login panel if not
    # logged_in = core.login.login_from_cache(classes, classes_login)
    logged_in = core.login_manager.user.auto_login(classes, classes_login)

    # Register classes
    if logged_in:
        for cls in classes:
            bpy.utils.register_class(cls)
    else:
        for cls in classes_login:
            bpy.utils.register_class(cls)
    for cls in classes_always_enable:
        bpy.utils.register_class(cls)

    # Register all custom properties
    properties.register()

    # Load custom icons
    core.icon_manager.load_icons()

    # Load bone detection list
    core.detection_manager.load_detection_lists()

    # Init fbx patcher
    core.fbx_patcher.start_fbx_patch_timer()

    print("### Loaded Rokoko Studio Live for Blender successfully!\n")


def unregister():
    print("### Unloading Rokoko Studio Live for Blender...")

    # Unregister updater
    updater_ops.unregister()

    # Shut down receiver if the plugin is disabled while it is running
    if operators.receiver.receiver_enabled:
        operators.receiver.ReceiverStart.force_disable()

    # Unregister all classes
    for cls in reversed(classes_login + classes + classes_always_enable):
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
