import time
from threading import Thread

import bpy
from ..core.receiver import Receiver
from ..core.animations import clear_animations
from ..core.utils import ui_refresh_all
from ..core import state_manager

timer = None
receiver = None
receiver_enabled = False


class ReceiverStart(bpy.types.Operator):
    bl_idname = "rsl.receiver_start"
    bl_label = "Start Receiver"
    bl_description = "Start receiving data from Rokoko Studio"
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        # If ECS or F8 is pressed, cancel
        if event.type == 'ESC' or event.type == 'F8' or not receiver_enabled:
            return self.cancel(context)

        # This gets run every frame
        if event.type == 'TIMER':
            if bpy.context.screen.is_animation_playing:
                return self.cancel(context)

            receiver.run()

        return {'PASS_THROUGH'}

    def execute(self, context):
        global receiver_enabled, receiver, timer

        # If animation is currently playing, stop it
        if context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()

        receiver_enabled = True

        # Clear current live data
        clear_animations()

        # Set up and start the receiver
        if not receiver:
            receiver = Receiver()
        receiver.start(context.scene.rsl_receiver_port)

        # Save the scene
        state_manager.save_scene()

        # Register this classes modal operator in Blenders event handling system and execute it at the specified fps
        context.window_manager.modal_handler_add(self)
        timer = context.window_manager.event_timer_add(1 / context.scene.rsl_receiver_fps, window=bpy.context.window)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        ReceiverStart.force_disable()
        ui_refresh_all()
        return {'CANCELLED'}

    @classmethod
    def disable(cls):
        global receiver_enabled
        receiver_enabled = False

    @classmethod
    def force_disable(cls):
        global receiver_enabled, receiver, timer

        receiver_enabled = False
        receiver.stop()

        bpy.context.window_manager.event_timer_remove(timer)

        # If the recording is still running, let it load the scene afterwards with a delay
        if bpy.context.scene.rsl_recording:
            bpy.context.scene.rsl_recording = False
            thread = Thread(target=load_scene_later, args=[])
            thread.start()
        else:
            state_manager.load_scene()


def load_scene_later():
    time.sleep(0.04)
    state_manager.load_scene()


class ReceiverStop(bpy.types.Operator):
    bl_idname = "rsl.receiver_stop"
    bl_label = "Stop Receiver"
    bl_description = "Stop receiving data from Rokoko Studio"
    bl_options = {'REGISTER'}

    def execute(self, context):
        ReceiverStart.disable()
        return {'FINISHED'}