import bpy
from ..core import animations
from ..core import receiver as receiver_cls
from ..operators import receiver, recorder


# Initializes the Rokoko panel in the toolbar
class ToolPanel(object):
    bl_label = 'Rokoko'
    bl_idname = 'VIEW3D_TS_rokoko'
    bl_category = 'Rokoko'
    # bl_category = 'Rokoko  Studio  Live'
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
            row.operator(receiver.ReceiverStop.bl_idname, icon='PAUSE', depress=True)
        else:
            row.operator(receiver.ReceiverStart.bl_idname, icon='PLAY')

        row = layout.row(align=True)
        row.scale_y = 1.3
        row.enabled = receiver.receiver_enabled
        if context.scene.rsl_recording:
            row.operator(recorder.RecorderStop.bl_idname, icon='RADIOBUT_ON', depress=True)
        else:
            row.operator(recorder.RecorderStart.bl_idname, icon='RADIOBUT_ON')

        if receiver.receiver_enabled and receiver_cls.show_error:
            for i, error in enumerate(receiver_cls.show_error):
                if i == 0:
                    row = layout.row(align=True)
                    row.label(text=error, icon='ERROR')
                else:
                    row = layout.row(align=True)
                    row.scale_y = 0.3
                    row.label(text=error, icon='BLANK1')

        inputs = []

        # Show a list of all assigned objects
        for obj in bpy.data.objects:
            if animations.props or animations.trackers:
                if obj.rsl_animations_props_trackers and obj.rsl_animations_props_trackers != 'None':
                    if obj.rsl_animations_props_trackers.startswith('PR|'):
                        inputs.append('Prop: ' + obj.rsl_animations_props_trackers.split('|')[2] + ' --> ' + obj.name)
                    elif obj.rsl_animations_props_trackers.startswith('TR|'):
                        inputs.append('Tracker: ' + obj.rsl_animations_props_trackers.split('|')[1] + ' --> ' + obj.name)
            if animations.faces and obj.rsl_animations_faces and obj.rsl_animations_faces != 'None':
                inputs.append('Face: ' + obj.rsl_animations_faces + ' --> ' + obj.name)
            if animations.actors and obj.rsl_animations_actors and obj.rsl_animations_actors != 'None':
                inputs.append('Actor: ' + obj.rsl_animations_actors + ' --> ' + obj.name)

        if inputs:
            layout.separator()
            row = layout.row(align=True)
            row.label(text='Inputs:')

            for input_text in inputs:
                row = layout.row(align=True)
                row.scale_y = 0.75
                row.label(text='  ' + input_text)
