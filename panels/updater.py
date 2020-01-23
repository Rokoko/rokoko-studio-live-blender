import bpy

from .main import ToolPanel
from .. import updater_ops


class UpdaterPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rsl_updater'
    bl_label = 'Updater'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        updater_ops.draw_updater_panel(context, self.layout)
