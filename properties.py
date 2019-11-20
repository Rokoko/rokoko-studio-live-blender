from bpy.types import Scene, Object
from bpy.props import IntProperty, StringProperty, EnumProperty
from .core import animations


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
    Object.ssp_animations_props_trackers = EnumProperty(
        name='Tracker or Prop',
        description='Select the prop or tracker that you want to attach this object to',
        items=animations.get_props_trackers
    )
    Object.ssp_animations_faces = EnumProperty(
        name='Face',
        description='Select the prop that you want to attach this object to',
        items=animations.get_faces
    )
    Object.ssp_animations_actors = EnumProperty(
        name='Actor',
        description='Select the prop that you want to attach this object to',
        items=animations.get_actors
    )