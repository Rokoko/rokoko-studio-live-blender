import bpy
import webbrowser
from ..core import login_manager


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
        return {'FINISHED'}


class LogoutButton(bpy.types.Operator):
    bl_idname = "rsl.login_logout"
    bl_label = "Sign out"
    bl_description = "Sign ouf of your Rokoko account"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        login_manager.user.logout()
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
