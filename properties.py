from bpy.types import Scene, Object, Mesh
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty, FloatProperty

from .core import animation_lists, state_manager


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
    Scene.rsl_recording = BoolProperty(
        name='Toggle Recording',
        description='Start and stop recording of the data from Rokoko Studio',
        default=False
    )
    Scene.rsl_reset_scene_on_stop = BoolProperty(
        name='Reset Scene on Stop',
        description='This will reset the location and position of animated objects to the state of before starting the receiver',
        default=True
    )
    Scene.rsl_hide_mesh_during_play = BoolProperty(
        name='Hide Armature Meshes during Play',
        description='This will hide all meshes on armatures during their animation to greatly reduce lag and increase performance',
        default=False,
        update=state_manager.update_hidden_meshes
    )

    # Objects
    Object.rsl_animations_props_trackers = EnumProperty(
        name='Tracker or Prop',
        description='Select the prop or tracker that you want to attach this object to',
        items=animation_lists.get_props_trackers,
        update=state_manager.update_object
    )
    Object.rsl_animations_faces = EnumProperty(
        name='Face',
        description='Select the face that you want to attach this mesh to',
        items=animation_lists.get_faces,
        update=state_manager.update_face
    )
    Object.rsl_animations_actors = EnumProperty(
        name='Actor',
        description='Select the actor that you want to attach this armature to',
        items=animation_lists.get_actors,
        update=state_manager.update_armature
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
