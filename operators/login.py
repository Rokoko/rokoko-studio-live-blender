import bpy
import platform
import webbrowser
from ..core import login


class LoginButton(bpy.types.Operator):
    bl_idname = "rsl.login_login"
    bl_label = "Sign in"
    bl_description = "Sign into your Rokoko account"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        password = context.scene.rsl_login_password
        if login.show_password:
            password = context.scene.rsl_login_password_shown

        if login.login(context.scene.rsl_login_email, password):
            self.report({'INFO'}, 'Signed in successfully!')
        return {'FINISHED'}


class LogoutButton(bpy.types.Operator):
    bl_idname = "rsl.login_logout"
    bl_label = "Sign out"
    bl_description = "Sign ouf of your Rokoko account"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        login.logout()
        return {'FINISHED'}


class RegisterButton(bpy.types.Operator):
    bl_idname = 'rsl.login_register'
    bl_label = 'Sign up in Browser'
    bl_description = 'Opens the Rokoko ID website in your browser'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open('https://www.rokoko.com/en/rmp/account/sign-up')
        self.report({'INFO'}, 'Opened Rokoko ID website.')
        return {'FINISHED'}


class ShowPassword(bpy.types.Operator):
    bl_idname = "rsl.login_show_password"
    bl_label = "Show Password"
    bl_description = "Shows or hides the entered password"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        if login.show_password:
            login.show_password = False
            context.scene.rsl_login_password = context.scene.rsl_login_password_shown
            context.scene.rsl_login_password_shown = ''
        else:
            login.show_password = True
            context.scene.rsl_login_password_shown = context.scene.rsl_login_password
            context.scene.rsl_login_password = ''
        return {'FINISHED'}


class InstallMissingLibsPopup(bpy.types.Operator):
    bl_idname = "rsl.login_popup_install_missing_libs"
    bl_label = "Missing Library detected!"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value * 4.5)

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        if platform.system() == "Windows":
            row = col.row(align=True)
            row.label(text="A necessary Windows library is not installed on your system.")
            col.separator()
            row = col.row(align=True)
            row.label(text="Please download and install it via the following link:", icon="INFO")
            col.separator()
            row = col.row(align=True)
            row.operator(InstallLibsButtonButton.bl_idname, icon="URL")
            return

        row = col.row(align=True)
        row.label(text="Login failed, you are missing necessary libraries.")
        row = col.row(align=True)
        row.label(text="You might be using a currently unsupported operating system.")
        row = col.row(align=True)
        row.label(text="Please let us know about this issue with your current specs!")


class InstallLibsButtonButton(bpy.types.Operator):
    bl_idname = 'rsl.login_install_libs'
    bl_label = 'Open Windows Download Site'
    bl_description = 'Opens the Windows download website in your browser'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open('https://support.microsoft.com/en-us/topic/update-for-visual-c-2013-redistributable-package-d8ccd6a5-4e26-c290-517b-8da6cfdf4f10')
        self.report({'INFO'}, 'Opened Windows download website.')
        return {'FINISHED'}
