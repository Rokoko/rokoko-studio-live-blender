import bpy
from .main import ToolPanel, separator
from ..operators.login import LoginButton
from ..core.icon_manager import Icons
from .. import updater, updater_ops
from ..core.login_manager import user


class LoginPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rsl_login_v2'
    bl_label = 'Rokoko ID'

    def draw(self, context):
        layout = self.layout

        updater.check_for_update_background(check_on_startup=True)
        updater_ops.draw_update_notification_panel(layout)

        row = layout.row(align=True)
        row.scale_y = 2
        row.operator(LoginButton.bl_idname, text="Sign in to Rokoko" if not user.logging_in else "Waiting for sign in..", icon_value=Icons.STUDIO_LIVE_LOGO.get_icon())

        row = layout.row(align=True)
        row.scale_y = 0.5
        row.label(text='*Opens your browser')

        errors = user.display_error
        if not errors:
            return

        separator(layout, scale=0.2)
        for i, error in enumerate(errors):
            row = layout.row(align=True)
            row.scale_y = 0.5
            row.label(text=error, icon="ERROR" if i == 0 else "BLANK1")
