import bpy
from ..operators import receiver
from ..operators.receiver import ReceiverStart, ReceiverStop

class ToolPanel(object):
    bl_label = 'SmartsuitPro'
    bl_idname = '3D_VIEW_TS_smartsuitpro'
    bl_category = 'SmartsuitPro'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'


class ReceiverPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rokoko_receiver'
    bl_label = 'SmartsuitPro Receiver'

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        layout.use_property_split = True

        col = layout.column()

        col.enabled = not receiver.receiver_enabled
        row = col.row(align=True)
        row.prop(context.scene, 'ssp_receiver_port', text = "Port:")

        if receiver.receiver_enabled:
            layout.operator(ReceiverStop.bl_idname, icon='ARMATURE_DATA')
        else:
            layout.operator(ReceiverStart.bl_idname, icon='ARMATURE_DATA')
