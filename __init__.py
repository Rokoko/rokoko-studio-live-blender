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
import traceback
import subprocess

first_startup = "bpy" not in locals()
import bpy

# Get library directory
main_dir = pathlib.Path(os.path.dirname(__file__)).resolve()
resources_dir = os.path.join(main_dir, "resources")
lib_dir = os.path.join(resources_dir, "libraries")
if not os.path.isdir(lib_dir):
    os.mkdir(lib_dir)

# Add the library path to the modules, so they can be loaded from the plugin
if lib_dir not in sys.path:
    sys.path.append(lib_dir)

# Install missing libraries
required = ["lz4", "websockets", "gql", "cryptography", "boto3"]
missing = [mod for mod in required if not pkgutil.find_loader(mod)]

if missing:
    print("Missing libaries:", missing)
    python = sys.executable

    # Ensure and update pip
    print("Ensuring pip")
    subprocess.call([python, "-m", "ensurepip", "--user"])

    print("Updating pip")
    subprocess.call([python, "-m", "pip", "install", "--upgrade", "pip"])

    # Install the missing libraries into the library path
    print("Installing missing libaries:", missing)
    command = [python, '-m', 'pip', 'install', f"--target={str(lib_dir)}", *missing]
    subprocess.check_call(command, stdout=subprocess.DEVNULL)
    print("Successfully installed missing libraries:", missing)

    # Reset console color
    print('\033[39m')


def show_error(message="", title="Unable to load Rokoko plugin!"):
    def draw(self, context):
        layout = self.layout
        msg_list = message.split("\n")

        for i, msg in enumerate(msg_list):
            row = layout.row(align=True)
            row.scale_y = 0.85
            row.label(text=msg)

    # Only show popup if the preferences window is open
    if len(bpy.context.window_manager.windows) > 1:
        bpy.context.window_manager.popup_menu(draw, title=title, icon="ERROR")


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


classes = []
classes_login = []
classes_always_enable = []


# register and unregister all classes
def register():
    print("\n### Loading Rokoko Studio Live for Blender...")

    # Check for unsupported Blender versions
    check_unsupported_blender_versions()

    # If first startup of this plugin, load all modules normally
    # If reloading the plugin, use importlib to reload modules
    # This lets you do adjustments to the plugin on the fly without having to restart Blender
    try:
        from . import updater_ops
        from . import updater

        # Always register the updater
        updater_ops.register()

        from . import core
        from . import panels
        from . import operators
        from . import properties
        if first_startup:
            pass
            # print("\nFirst STARTUP!")
        else:
            # print("\nRELOAD!")
            import importlib
            importlib.reload(updater_ops)
            importlib.reload(updater)
            importlib.reload(core)
            importlib.reload(panels)
            importlib.reload(operators)
            importlib.reload(properties)
    except Exception as e:
        print("\nERROR: Rokoko plugin failed to load:")
        trace = traceback.format_exc()
        print(trace)
        show_error("Expand the plugin module to access the updater to check for a newer version.\n\n" + trace)
        return

    global classes, classes_login, classes_always_enable

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

    # Register updater and check for Rokoko Studio Live updates
    updater_ops.update_info(bl_info, beta_branch)

    # Check if the user is logged in, show the login panel if not
    # logged_in = core.login.login_from_cache(classes, classes_login)
    logged_in = core.login_manager.user.auto_login(classes, classes_login)

    # Register classes
    # The classes need to be assigned as list() to create a duplicate
    classes_to_register = list(classes)
    if not logged_in:
        classes_to_register = list(classes_login)
    classes_to_register += classes_always_enable

    register_count = 0
    for cls in classes_to_register:
        try:
            bpy.utils.register_class(cls)
            register_count += 1
        except ValueError:
            print("Error: Failed to register class", cls)
            pass
    if register_count < len(classes_to_register):
        print('Skipped', len(classes_to_register) - register_count, 'ROKOKO classes.')

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
    from . import updater_ops
    from . import operators
    from . import core

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
