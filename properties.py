from bpy.types import Scene, Object, Mesh
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty, FloatProperty

from .core import animation_lists, state_manager, recorder


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
    Scene.rsl_scene_scaling = FloatProperty(
        name='Scene Scaling',
        description="This defines how much the scene get's scaled."
                    "\nThis only effects props and trackers",
        default=1,
        precision=3,
        step=1
    )
    Scene.rsl_reset_scene_on_stop = BoolProperty(
        name='Reset Scene on Stop',
        description='This will reset the location and position of animated objects to the state of before starting the receiver',
        default=True
    )
    Scene.rsl_hide_mesh_during_play = BoolProperty(
        name='Hide Meshes during Play',
        description='This will hide all meshes that are animated by armatures during their animation '
                    '\nto greatly reduce lag and increase performance.'
                    '\nThis will not hide animated faces',
        default=False,
        update=state_manager.update_hidden_meshes
    )
    Scene.rsl_recording = BoolProperty(
        name='Toggle Recording',
        description='Start and stop recording of the data from Rokoko Studio',
        default=False,
        update=recorder.toggle_recording
    )
    Scene.rsl_command_ip_address = StringProperty(
        name='IP Address',
        description='Input the IP address of Rokoko Studio',
        default='127.0.0.1',
        maxlen=15
    )
    Scene.rsl_command_ip_port = IntProperty(
        name='Command API Port',
        description="The port defined in Rokoko Studio",
        default=14053,
        min=1,
        max=65535
    )
    Scene.rsl_command_api_key = StringProperty(
        name='API Key',
        description='Input the API key displayed in Rokoko Studio',
        default='1234',
        maxlen=15
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
