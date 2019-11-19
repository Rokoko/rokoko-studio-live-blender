import bpy
from ..core.receiver import Receiver

receiver_enabled = False


def test():
    for obj in bpy.data.objects:
        obj.location.x += 0.01


class ReceiverStart(bpy.types.Operator):
    bl_idname = "ssp.receiver_start"
    bl_label = "Start Receiver"
    bl_description = "Start receiving data from Rokoko Studio"
    bl_options = {'REGISTER'}

    receiver = None
    timer = None

    def modal(self, context, event):
        if event.type == 'ESC' or not receiver_enabled:
            return self.cancel(context)

        # This gets run every frame
        if event.type == 'TIMER':
            self.receiver.run()

        return {'PASS_THROUGH'}

    def execute(self, context):
        global receiver_enabled
        if receiver_enabled or self.receiver:
            raise RuntimeError('Receiver is already enabled.')

        receiver_enabled = True

        self.receiver = Receiver(context.scene.ssp_receiver_port)

        context.window_manager.modal_handler_add(self)
        self.timer = context.window_manager.event_timer_add(1 / context.scene.ssp_receiver_fps, window=bpy.context.window)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        global receiver_enabled
        receiver_enabled = False
        context.window_manager.event_timer_remove(self.timer)

        del self.receiver

        return {'CANCELLED'}

    @classmethod
    def disable(cls):
        global receiver_enabled
        if receiver_enabled:
            receiver_enabled = False


class ReceiverStop(bpy.types.Operator):
    bl_idname = "ssp.receiver_stop"
    bl_label = "Stop Receiver"
    bl_description = "Stop receiving data from Rokoko Studio"
    bl_options = {'REGISTER'}

    def execute(self, context):
        ReceiverStart.disable()
        return {'FINISHED'}