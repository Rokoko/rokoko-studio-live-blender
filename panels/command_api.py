import bpy

from .main import ToolPanel
from ..operators import command_api
from ..core.icon_manager import get_icon


# Main panel of the Rokoko panel
class CommandPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rsl_command_api'
    bl_label = 'Studio Command API'
    bl_options = {'DEFAULT_CLOSED'}

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
        row.scale_y = 1.5
        row.scale_x = 3
        row.operator(command_api.StartCalibration.bl_idname, text='', icon_value=get_icon('SUIT'))
        row.operator(command_api.Restart.bl_idname, text='', icon='FILE_REFRESH')
        row.operator(command_api.StartRecording.bl_idname, text='', icon='PLAY')
        row.operator(command_api.StopRecording.bl_idname, text='', icon='SNAP_FACE')
