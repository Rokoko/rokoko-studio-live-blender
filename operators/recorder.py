import bpy


class RecorderStart(bpy.types.Operator):
    bl_idname = "rsl.recorder_start"
    bl_label = "Start Recording"
    bl_description = "Start recording data from Rokoko Studio" \
                     "\nWarning: Data currently on this track will be overwritten. Choose another track to record to or set the start frame at the position you want to start recording"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if context.scene.rsl_recording:
            self.report({'ERROR'}, 'Already recording')
            return {'CANCELLED'}

        context.scene.rsl_recording = True

        context.scene.frame_current = context.scene.frame_start
        context.scene.render.fps = context.scene.rsl_receiver_fps
        return {'FINISHED'}


class RecorderStop(bpy.types.Operator):
    bl_idname = "rsl.recorder_stop"
    bl_label = "Stop Recording"
    bl_description = "Stop recording data from Rokoko Studio"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if not context.scene.rsl_recording:
            self.report({'ERROR'}, 'Not recording')
            return {'CANCELLED'}

        context.scene.rsl_recording = False
        return {'FINISHED'}