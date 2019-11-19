from bpy.types import Scene
from bpy.props import IntProperty


def register():
    Scene.ssp_receiver_port = IntProperty(
        name='Streaming Port',
        description="The port defined in Rokoko Studio",
        default=14043,
        min=1,
        max=65535
    )
    Scene.ssp_receiver_fps = IntProperty(
        name='FPS',
        description="How often is the data received",
        default=30,
        min=1,
        max=100
    )