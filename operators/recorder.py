import bpy


class RecorderStart(bpy.types.Operator):
    bl_idname = "rsl.recorder_start"
    bl_label = "Start Recording"
    bl_description = "Start recording data from Rokoko Studio"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        if context.scene.rsl_recording:
            self.report({'ERROR'}, 'Already recording')
            return {'CANCELLED'}

        context.scene.rsl_recording = True
        return {'FINISHED'}


class RecorderStop(bpy.types.Operator):
    bl_idname = "rsl.recorder_stop"
    bl_label = "Stop Recording"
    bl_description = "Stop recording data from Rokoko Studio" \
                     "\nThe processing of the recording can take a couple minutes, depending on the length of the recording"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        if not context.scene.rsl_recording:
            self.report({'ERROR'}, 'Not recording')
            return {'CANCELLED'}

        context.scene.rsl_recording = False
        return {'FINISHED'}
