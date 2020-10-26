import bpy
from .main import ToolPanel, separator
from ..operators.login import LoginButton, RegisterButton, ShowPassword
from ..core import login
from ..core.icon_manager import Icons
from .. import updater, updater_ops


class LoginPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rsl_login_v2'
    bl_label = 'Rokoko ID'

    def draw(self, context):
        layout = self.layout

        updater.check_for_update_background(check_on_startup=True)
        updater_ops.draw_update_notification_panel(layout)

        row = layout.row(align=True)
        row.label(text='Sign in with your Rokoko ID:', icon_value=Icons.STUDIO_LIVE_LOGO.get_icon())
        separator(layout, 0.1)

        row = layout.row(align=True)
        row.scale_y = 0.5
        row.label(text='Email:')
        row = layout.row(align=True)
        row.prop(context.scene, 'rsl_login_email', text='')

        separator(layout, 0.01)

        row = layout.row(align=True)
        row.scale_y = 0.5
        row.label(text='Password:')

        split = layout.row(align=True)
        row = split.row(align=True)
        row.prop(context.scene, 'rsl_login_password_shown' if login.show_password else 'rsl_login_password', text='')
        row = split.row(align=True)
        row.alignment = 'RIGHT'
        row.operator(ShowPassword.bl_idname, text="", icon='HIDE_OFF' if login.show_password else 'HIDE_ON')

        if login.error_show_no_connection:
            row = layout.row(align=True)
            row.label(text='No internet connection!', icon='ERROR')

        elif login.error_show_wrong_auth:
            row = layout.row(align=True)
            row.label(text='Wrong email or password!', icon='ERROR')

        row = layout.row(align=True)
        row.operator(LoginButton.bl_idname, icon='KEYINGSET')

        row = layout.row(align=True)
        row.operator(RegisterButton.bl_idname, icon='URL')

        separator(layout, 0.1)
        row = layout.row(align=True)
        row.scale_y = 0.6
        row.label(text='The sign in is required once.', icon='INFO')
        row = layout.row(align=True)
        row.scale_y = 0.4
        row.label(text='It can then be used offline.', icon='BLANK1')
