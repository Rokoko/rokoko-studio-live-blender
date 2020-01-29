import bpy

from .main import ToolPanel
from .. import updater
from ..operators import info
from ..core.icon_manager import Icons


class InfoPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rsl_info'
    bl_label = 'Info'
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.label(text='Rokoko Studio Live (' + updater.current_version_str + ')', icon_value=Icons.ROKOKO.get_icon())

        # Separator
        row = layout.row(align=True)
        row.scale_y = 0.1

        row = layout.row(align=True)
        row.scale_y = 0.65
        row.label(text='Need help, found a bug or')
        row = layout.row(align=True)
        row.scale_y = 0.65
        row.label(text='want to share a suggestion?')

        # Separator
        row = layout.row(align=True)
        row.scale_y = 0.1

        row = layout.row(align=True)
        row.operator(info.ForumButton.bl_idname, icon='URL')
