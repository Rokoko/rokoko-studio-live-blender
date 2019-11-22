from bpy.types import Scene, Object
from bpy.props import IntProperty, StringProperty, EnumProperty
from .core import animations


def register():
    Scene.rsl_receiver_port = IntProperty(
        name='Streaming Port',
        description="The port defined in Rokoko Studio",
        default=14043,
        min=1,
        max=65535
    )
    Scene.rsl_receiver_fps = IntProperty(
        name='FPS',
        description="How often is the data received",
        default=60,
        min=1,
        max=100
    )
    Object.rsl_animations_props_trackers = EnumProperty(
        name='Tracker or Prop',
        description='Select the prop or tracker that you want to attach this object to',
        items=animations.get_props_trackers
    )
    Object.rsl_animations_faces = EnumProperty(
        name='Face',
        description='Select the prop that you want to attach this object to',
        items=animations.get_faces
    )
    Object.rsl_animations_actors = EnumProperty(
        name='Actor',
        description='Select the prop that you want to attach this object to',
        items=animations.get_actors
    )