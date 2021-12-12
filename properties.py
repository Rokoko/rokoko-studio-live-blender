from bpy.types import Scene, Object
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty, FloatProperty, CollectionProperty, PointerProperty

from .core import animation_lists, state_manager, recorder, retargeting, login
from .panels import retargeting as retargeting_ui


def register():
    # Login
    Scene.rsl_login_email = StringProperty(
        name='Email',
        description='Input the email address of your Rokoko account',
        update=login.credentials_update
    )
    Scene.rsl_login_password = StringProperty(
        name='Password',
        description='Input the password of your Rokoko account',
        subtype='PASSWORD',
        update=login.credentials_update
    )
    Scene.rsl_login_password_shown = StringProperty(
        name='Password',
        description='Input the password of your Rokoko account',
        update=login.credentials_update
    )

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
        description="This allows you to scale the position of props and trackers."
                    "\nUseful to align their positions with armatures",
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
        description='This will hide all meshes that are animated by armatures'
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

    # Command API
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

    # Retargeting
    Scene.rsl_retargeting_armature_source = PointerProperty(
        name='Source',
        description='Select the armature with the animation that you want to retarget',
        type=Object,
        poll=retargeting.poll_source_armatures,
        update=retargeting.clear_bone_list
    )
    Scene.rsl_retargeting_armature_target = PointerProperty(
        name='Target',
        description='Select the armature that should receive the animation',
        type=Object,
        poll=retargeting.poll_target_armatures,
        update=retargeting.clear_bone_list
    )
    Scene.rsl_retargeting_auto_scaling = BoolProperty(
        name='Auto Scale',
        description='This will scale the source armature to fit the height of the target armature.'
                    '\nBoth armatures have to be in T-pose for this to work correctly',
        default=True
    )
    Scene.rsl_retargeting_use_pose = EnumProperty(
        name="Use Pose",
        description='Select which pose of the source and target armature to use to retarget the animation.'
                    '\nBoth armatures should be in the same pose before retargeting',
        items=[
            ("REST", "Rest", "Select this to use the rest pose during retargeting."),
            ("CURRENT", "Current", "Select this to use the current pose during retargeting.")
        ]
    )
    Scene.rsl_retargeting_bone_list = CollectionProperty(
        type=retargeting_ui.BoneListItem
    )
    Scene.rsl_retargeting_bone_list_index = IntProperty(
        name="Index for the retargeting bone list",
        default=0
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
        update=state_manager.update_actor
    )
    Object.rsl_use_custom_scale = BoolProperty(
        name='Use Custom Scale',
        description='Select this if the objects scene scaling should be overwritten',
        default=False,
    )
    Object.rsl_custom_scene_scale = FloatProperty(
        name='Custom Scene Scaling',
        description="This allows you to scale the position independently from the scene scale.",
        default=1,
        precision=3,
        step=1
    )

    # Face shapekeys
    for shape in animation_lists.face_shapes:
        setattr(Object, 'rsl_face_' + shape, StringProperty(
            name=shape,
            description='Select the shapekey that should be animated by this shape'
        ))

    # Actor bones
    for bone in animation_lists.get_bones().keys():
        setattr(Object, 'rsl_actor_' + bone, StringProperty(
            name=bone,
            description='Select the bone that corresponds to the actors bone'
        ))
