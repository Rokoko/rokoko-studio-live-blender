
import bpy
import importlib
from ..core import login_manager
from ..core import library_manager
from ..core import live_data_manager


class LoginButton(bpy.types.Operator):
    bl_idname = "rsl.login_login"
    bl_label = "Sign in"
    bl_description = "Sign into your Rokoko account with your browser"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return not login_manager.user.logging_in

    def execute(self, context):
        login = login_manager.Login()
        login.start()
        self.report({'INFO'}, 'Opened Rokoko ID website in your browser.')
        return {'FINISHED'}


class LogoutButton(bpy.types.Operator):
    bl_idname = "rsl.login_logout"
    bl_label = "Sign out"
    bl_description = "Sign out of your Rokoko account"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        login_manager.user.logout()
        self.report({'INFO'}, 'Logout successful.')
        return {'FINISHED'}


class InstallLibsButton(bpy.types.Operator):
    bl_idname = 'rsl.login_install_libs'
    bl_label = 'Install Required Libraries'
    bl_description = 'Installs the required libraries for this plugin to work'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        # Install the libraries
        try:
            self.install_libs()
        except ImportError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        # Save login manager data
        classes_logged_in = login_manager.user.classes_logged_in
        classes_logged_out = login_manager.user.classes_logged_out
        version_str = login_manager.user.version_str

        # Reload files to load the libraries
        importlib.reload(login_manager)
        importlib.reload(live_data_manager)

        # Load the login manager data
        login_manager.user.classes_logged_in = classes_logged_in
        login_manager.user.classes_logged_out = classes_logged_out
        login_manager.user.version_str = version_str

        # Attempt to auto login the user
        login_manager.user.auto_login()

        self.report({'INFO'}, 'Installed libraries successfully!')
        return {'FINISHED'}

    def install_libs(self):
        missing = library_manager.lib_manager.install_libraries(["websockets", "gql", "cryptography", "boto3"])
        if missing:
            raise ImportError("The following libraries could not be installed: "
                              "\n- " + " \n- ".join(missing) +
                              "  \n\nPlease see console for more information.")
        library_manager.lib_manager.install_libraries(["lz46"])
