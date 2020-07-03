import bpy
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