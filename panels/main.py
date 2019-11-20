import bpy
from ..operators import receiver
from ..operators.receiver import ReceiverStart, ReceiverStop


# Initializes the SmartsuitPro panel in the toolbar
class ToolPanel(object):
    bl_label = 'SmartsuitPro'
    bl_idname = 'VIEW3D_TS_smartsuitpro'
    bl_category = 'SmartsuitPro'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'


# Main panel of the SmartsuitPro panel
class ReceiverPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_ssp_receiver'
    bl_label = 'SmartsuitPro Receiver'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False

        col = layout.column()

        col.enabled = not receiver.receiver_enabled

        row = col.row(align=True)
        row.label(text='Port:')
        row.prop(context.scene, 'ssp_receiver_port', text='')

        row = col.row(align=True)
        row.label(text='FPS:')
        row.prop(context.scene, 'ssp_receiver_fps', text='')

        layout.separator()

        row = layout.row(align=True)
        row.scale_y = 1.3
        if receiver.receiver_enabled:
            row.operator(ReceiverStop.bl_idname, icon='PAUSE')
        else:
            row.operator(ReceiverStart.bl_idname, icon='PLAY')
