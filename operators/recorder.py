import bpy

recording = False


class RecorderStart(bpy.types.Operator):
    bl_idname = "rsl.recorder_start"
    bl_label = "Start Recorder"
    bl_description = "Start recording data from Rokoko Studio"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global recording
        if recording:
            self.report({'ERROR'}, 'Already recording')
            return {'CANCELLED'}

        recording = True
        return {'FINISHED'}


class RecorderStop(bpy.types.Operator):
    bl_idname = "rsl.recorder_stop"
    bl_label = "Stop Recorder"
    bl_description = "Stop recording data from Rokoko Studio"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global recording
        if not recording:
            self.report({'ERROR'}, 'Not recording')
            return {'CANCELLED'}

        recording = False
        return {'FINISHED'}