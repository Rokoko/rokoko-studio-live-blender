
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
import json
import shutil
import pathlib
import pkgutil
import platform
import traceback
import ensurepip
import subprocess

first_startup = "bpy" not in locals()
import bpy


class LibraryManager:
    system_info = {
        "operating_system": platform.system(),
    }

    def __init__(self, libs, libs_main_dir):
        self.required = libs
        self.libs_main_dir = libs_main_dir
        self.libs_info_file = os.path.join(self.libs_main_dir, ".lib_info")

        python_ver_str = "".join([str(ver) for ver in sys.version_info[:2]])
        self.libs_dir = os.path.join(self.libs_main_dir, "python" + python_ver_str)

        self.check_libs_info()
        self.install_libraries()

    def install_libraries(self):
        # Create main library directory
        if not os.path.isdir(self.libs_main_dir):
            os.mkdir(self.libs_main_dir)
        # Create python specific library directory
        if not os.path.isdir(self.libs_dir):
            os.mkdir(self.libs_dir)

        # Add the library path to the modules, so they can be loaded from the plugin
        if self.libs_dir not in sys.path:
            sys.path.append(self.libs_dir)

        # Install missing libraries
        missing = [mod for mod in self.required if not pkgutil.find_loader(mod)]
        if missing:
            print("Missing libaries:", missing)
            try:
                # Set python path on older Blender versions
                python = bpy.app.binary_path_python
            except AttributeError:
                python = sys.executable
            if not python.lower().endswith("python.exe"):
                print("WARNING: Could not find correct python executable:", python)

            # Ensure and update pip
            print("Ensuring pip")
            ensurepip.bootstrap()

            print("Updating pip")
            try:
                subprocess.check_call([python, "-m", "pip", "install", "--upgrade", "pip"])
            except subprocess.CalledProcessError:
                subprocess.call(["sudo", python, "-m", "pip", "install", "--upgrade", "pip"])

            # Install the missing libraries into the library path
            print("Installing missing libraries:", missing)
            command = [python, '-m', 'pip', 'install', f"--target={str(self.libs_dir)}", *missing]
            subprocess.call(command, stdout=subprocess.DEVNULL)

            # Check if all libraries installations were successful
            still_missing = [mod for mod in self.required if not pkgutil.find_loader(mod)]
            installed_libs = [lib for lib in missing if lib not in still_missing]
            if still_missing:
                print("WARNING: Could not install the following libraries:", still_missing)
            if installed_libs:
                print("Successfully installed missing libraries:", installed_libs)

            # Reset console color, because it's still colored after running pip
            print('\033[39m')

        # Create library info file after all libraries are installed to ensure everything is installed correctly
        self.create_libs_info()

    def check_libs_info(self):
        if not os.path.isdir(self.libs_dir):
            return

        # If the library info file doesn't exist, delete the libs folder
        if not os.path.isfile(self.libs_info_file):
            print("Library info is missing, deleting library folder.")
            shutil.rmtree(self.libs_main_dir)
            return

        # Read data from info file
        current_data = self.system_info
        with open(self.libs_info_file, 'r', encoding="utf8") as file:
            loaded_data = json.load(file)

        # Compare info and delete libs folder if it doesn't match
        for key, val_current in current_data.items():
            val_loaded = loaded_data.get(key)
            if not val_loaded == val_current:
                print("Current info:", current_data)
                print("Loaded info: ", loaded_data)
                print("Library info is not matching, deleting library folder.")
                shutil.rmtree(self.libs_main_dir)
                return

    def create_libs_info(self):
        if not os.path.isdir(self.libs_dir) or os.path.isfile(self.libs_info_file):
            return

        # Write the current data to the info file
        with open(self.libs_info_file, 'w', encoding="utf8") as file:
            json.dump(self.system_info, file)


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

    # Register the updater
    # Important to do early, so it is always loaded even in case of an error
    from . import updater_ops
    from . import updater
    if not first_startup:
        import importlib
        importlib.reload(updater_ops)
        importlib.reload(updater)
    updater_ops.register()

    # Now that the updater is loaded, do the rest of the registration safely
    try:
        register_late()
    except Exception:
        print("\nERROR: Rokoko plugin failed to load:")
        trace = traceback.format_exc()
        print(trace)
        show_error("Expand the plugin module to access the updater to check for a newer version.\n\n" + trace)
        return


def register_late():
    # Install the missing libraries
    main_dir = pathlib.Path(os.path.dirname(__file__)).resolve()
    resources_dir = os.path.join(main_dir, "resources")
    libs_dir = os.path.join(resources_dir, "libraries")
    libs = ["lz4", "websockets", "gql", "cryptography", "boto3"]
    LibraryManager(libs, libs_dir)

    # If first startup of this plugin, load all modules normally
    # If reloading the plugin, use importlib to reload modules
    # This lets you do adjustments to the plugin on the fly without having to restart Blender
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
        importlib.reload(core)
        importlib.reload(panels)
        importlib.reload(operators)
        importlib.reload(properties)

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

    # Update updater info as late as possible, to ensure that errors are shown instead of being overwritten
    from . import updater_ops
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
