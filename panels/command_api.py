import bpy

from .main import ToolPanel
from ..operators import command_api
from ..core.icon_manager import get_icon


# Main panel of the Rokoko panel
class CommandPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rsl_command_api'
    bl_label = 'Command API'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False

        col = layout.column()

        # Command API
        row = col.row(align=True)
        row.label(text='Address:')
        row.prop(context.scene, 'rsl_command_ip_address', text='')

        row = col.row(align=True)
        row.label(text='Port:')
        row.prop(context.scene, 'rsl_command_ip_port', text='')

        row = col.row(align=True)
        row.label(text='Key:')
        row.prop(context.scene, 'rsl_command_api_key', text='')

        row = layout.row(align=True)
        row.operator(command_api.StartCalibration.bl_idname, icon_value=get_icon('SUIT'))
        row = layout.row(align=True)
        row.operator(command_api.Restart.bl_idname, icon='FILE_REFRESH')
        row = layout.row(align=True)
        row.operator(command_api.StartRecording.bl_idname, icon='PLAY')
        row = layout.row(align=True)
        row.operator(command_api.StopRecording.bl_idname, icon='PAUSE')
