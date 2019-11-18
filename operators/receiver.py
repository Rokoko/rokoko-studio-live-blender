import bpy

receiver_enabled = False


def test():
    for obj in bpy.data.objects:
        obj.location.x += 0.01


class ReceiverStart(bpy.types.Operator):
    bl_idname = "ssp.receiver_start"
    bl_label = "Start Receiver"
    bl_description = "Start receiving data from Rokoko Studio"
    bl_options = {'REGISTER'}

    timer = None

    def modal(self, context, event):
        if event.type == 'ESC' or not receiver_enabled:
            return self.cancel(context)

        # This gets run every frame
        if event.type == 'TIMER':
            test()

        return {'PASS_THROUGH'}

    def execute(self, context):
        print('Starting receiver')

        global receiver_enabled
        if receiver_enabled:
            print('ALREADY RUNNING')
            return {'CANCELLED'}

        receiver_enabled = True

        context.window_manager.modal_handler_add(self)
        self.timer = context.window_manager.event_timer_add( 1 / 60, window=bpy.context.window)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        print('Stopping receiver')

        global receiver_enabled
        receiver_enabled = False
        context.window_manager.event_timer_remove(self.timer)

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