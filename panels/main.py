import bpy
from ..operators import receiver
from ..operators.receiver import ReceiverStart, ReceiverStop


# Initializes the Rokoko panel in the toolbar
class ToolPanel(object):
    bl_label = 'Rokoko'
    bl_idname = 'VIEW3D_TS_rokoko'
    bl_category = 'Rokoko'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'


# Main panel of the Rokoko panel
class ReceiverPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rsl_receiver'
    bl_label = 'Rokoko Studio Live'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False

        col = layout.column()

        col.enabled = not receiver.receiver_enabled

        row = col.row(align=True)
        row.label(text='Port:')
        row.prop(context.scene, 'rsl_receiver_port', text='')

        row = col.row(align=True)
        row.label(text='FPS:')
        row.prop(context.scene, 'rsl_receiver_fps', text='')

        layout.separator()

        row = layout.row(align=True)
        row.scale_y = 1.3
        if receiver.receiver_enabled:
            row.operator(ReceiverStop.bl_idname, icon='PAUSE')
        else:
            row.operator(ReceiverStart.bl_idname, icon='PLAY')

        # # Show a list of all assigned objects, not yet working correctly
        # for obj in bpy.data.objects:
        #     if obj.rsl_animations_props_trackers and obj.rsl_animations_props_trackers.startswith('PR|'):
        #         row = layout.row(align=True)
        #         row.label(text='Prop: ' + obj.name + ' - ' + obj.rsl_animations_props_trackers.split('|')[2])
        #     if obj.rsl_animations_props_trackers and obj.rsl_animations_props_trackers.startswith('TR|'):
        #         row = layout.row(align=True)
        #         row.label(text='Tracker: ' + obj.name + ' - ' + obj.rsl_animations_props_trackers.split('|')[1])
        #     if obj.rsl_animations_faces:
        #         row = layout.row(align=True)
        #         row.label(text='Face: ' + obj.name + ' - ' + obj.rsl_animations_faces)
        #     if obj.rsl_animations_actors:
        #         row = layout.row(align=True)
        #         row.label(text='Actor: ' + obj.name + ' - ' + obj.rsl_animations_actors.split('|')[1])
