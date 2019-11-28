from bpy.types import Scene, Object, Mesh
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty, FloatProperty
from .core import animation_lists


def register():
    # Receiver
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

    Scene.rsl_ui_refresher = BoolProperty()

    # Objects
    Object.rsl_animations_props_trackers = EnumProperty(
        name='Tracker or Prop',
        description='Select the prop or tracker that you want to attach this object to',
        items=animation_lists.get_props_trackers
    )
    Object.rsl_animations_faces = EnumProperty(
        name='Face',
        description='Select the prop that you want to attach this object to',
        items=animation_lists.get_faces
    )
    Object.rsl_animations_actors = EnumProperty(
        name='Actor',
        description='Select the prop that you want to attach this object to',
        items=animation_lists.get_actors
    )

    Object.rsl_euler_0 = FloatProperty(
        name='Euler W',
        description='testing',
        default=0,
        min=-1,
        max=1
    )

    Object.rsl_euler_1 = FloatProperty(
        name='Euler X',
        description='testing',
        default=0,
        min=-1,
        max=1
    )

    Object.rsl_euler_2 = FloatProperty(
        name='Euler Y',
        description='testing',
        default=0,
        min=-1,
        max=1
    )

    Object.rsl_euler_3 = FloatProperty(
        name='Euler Z',
        description='testing',
        default=0,
        min=-1,
        max=1
    )

    # Face shapekeys
    for shape in animation_lists.face_shapes:
        setattr(Object, 'rsl_face_' + shape, StringProperty(
            name=shape,
            description='Select the shapekey that should be animated by this shape'
        ))

    # Actor bones
    for bone in animation_lists.actor_bones.keys():
        setattr(Object, 'rsl_actor_' + bone, StringProperty(
            name=bone,
            description='Select the bone that corresponds to the actors bone'
        ))
