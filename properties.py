from bpy.types import Scene
from bpy.props import IntProperty


def register():
    Scene.ssp_receiver_port = IntProperty(
        name='Streaming Port',
        description="The port defined in Rokoko Stuio",
        default=14043,
        min=1,
        max=65535
    )