import bpy

from .main import ToolPanel, separator
from .. import updater
from ..operators import info
from ..core.icon_manager import Icons
from ..core.login_manager import user
from ..operators.login import LogoutButton


class InfoPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rsl_info_v2'
    bl_label = 'Info'

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.label(text='Rokoko Studio Live', icon_value=Icons.STUDIO_LIVE_LOGO.get_icon())
        row = layout.row(align=True)
        row.scale_y = 0.1
        row.label(text='for Blender (v' + updater.current_version_str + ')', icon='BLANK1')

        separator(layout, 0.01)

        row = layout.row(align=True)
        row.label(text='Developed by ', icon='BLANK1')
        row.scale_y = 0.6
        row = layout.row(align=True)
        row.scale_y = 0.3
        row.label(text='Rokoko Electronics ApS', icon='BLANK1')

        separator(layout, 0.1)

        col = layout.column(align=True)

        row = col.row(align=True)
        row.operator(info.LicenseButton.bl_idname)
        row.operator(info.RokokoButton.bl_idname)
        row = col.row(align=True)
        row.operator(info.DocumentationButton.bl_idname)
        row = col.row(align=True)
        row.operator(info.ForumButton.bl_idname)

        # If there is no email, the user is not logged in yet
        if not user.email:
            return

        separator(layout, 0.1)

        subrow = layout.row(align=True)
        row = subrow.row(align=True)
        row.scale_y = 0.7
        row.label(text='Rokoko ID:')
        row = subrow.row(align=True)
        row.scale_y = 0.7
        row.alignment = 'RIGHT'
        row.operator(info.ToggleRokokoIDButton.bl_idname, text='', icon='HIDE_OFF' if user.display_email else 'HIDE_ON')

        row = layout.row(align=True)
        row.scale_y = 0.3
        row.label(text=user.email if user.display_email else "***********")
        row = layout.row(align=True)
        row.operator(LogoutButton.bl_idname)
