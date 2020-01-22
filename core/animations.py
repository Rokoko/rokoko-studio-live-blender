import bpy
from mathutils import Quaternion, Matrix

from . import animation_lists

# version = None
# timestamp = None
# playbacktimestamp = None
props = []
trackers = []
faces = []
actors = []


def clear_animations():
    global props, trackers, faces, actors
    props = []
    trackers = []
    faces = []
    actors = []


def animate():
    for obj in bpy.data.objects:
        # Animate all trackers and props
        if props or trackers:
            animate_tracker_prop(obj)

        # Animate all faces
        if faces and obj.type == 'MESH':
            animate_face(obj)

        # Animate all actors
        elif actors and obj.type == 'ARMATURE':
            animate_actor(obj)


def animate_tracker_prop(obj):
    if not obj.rsl_animations_props_trackers or obj.rsl_animations_props_trackers == 'None':
        return

    # Get obj id from selected item
    obj_id = obj.rsl_animations_props_trackers.split('|')
    obj_type = obj_id[0]
    obj_name = obj_id[1]

    def set_obj_data(data):
        obj.rotation_mode = 'QUATERNION'
        obj.location = pos_studio_to_blender(
            data['position']['x'] * 1,
            data['position']['y'] * 1,
            data['position']['z'] * 1,
        )
        obj.rotation_quaternion = rot_studio_to_blender(
            data['rotation']['w'],
            data['rotation']['x'],
            data['rotation']['y'],
            data['rotation']['z'],
        )

    # If object is a prop, get the live data
    if obj_type == 'PR':
        prop = [prop for prop in props if prop['id'] == obj_name]
        if prop:
            set_obj_data(prop[0])

    # If object is a tracker, get the live data
    elif obj_type == 'TR':
        tracker = [tracker for tracker in trackers if tracker['name'] == obj_name]
        if tracker:
            set_obj_data(tracker[0])

    # Record data
    if bpy.context.scene.rsl_recording:
        obj.keyframe_insert(data_path='location', group=obj.name)
        obj.keyframe_insert(data_path='rotation_quaternion', group=obj.name)


def animate_face(obj):
    if not hasattr(obj.data, 'shape_keys') or not hasattr(obj.data.shape_keys, 'key_blocks'):
        return
    if not obj.rsl_animations_faces or obj.rsl_animations_faces == 'None':
        return

    # Get the face live data
    face = [face for face in faces if face['faceId'] == obj.rsl_animations_faces]
    if not face:
        return
    face = face[0]

    # Set each assigned shapekey to the value of it's according live data value
    for shape in animation_lists.face_shapes:
        # Get assigned shapekey
        shapekey = obj.data.shape_keys.key_blocks.get(getattr(obj, 'rsl_face_' + shape))
        if shapekey:
            shapekey.slider_min = -1
            shapekey.value = face[shape] / 100

            if bpy.context.scene.rsl_recording:
                shapekey.keyframe_insert(data_path='value', group=obj.name)


def animate_actor(obj):
    # Return if no actor is assigned to this object
    if not obj.rsl_animations_actors or obj.rsl_animations_actors == 'None':
        return

    # Get the actor data assigned to the object
    actor = [actor for actor in actors if actor['id'] == obj.rsl_animations_actors]
    if not actor:
        return
    actor = actor[0]

    # Get current custom data from this object
    # The models t-pose bone rotations and locations, which are set by the user, are stored inside this custom data
    custom_data = obj.get('CUSTOM')
    if not custom_data:
        print('NO CUSTOM DATA')
        return

    # Get tpose data from custom data
    tpose_loc = custom_data.get('rsl_tpose_location_object')
    tpose_rot_glob = custom_data.get('rsl_tpose_rotation_global')
    if not tpose_rot_glob:
        print('NO TPOSE DATA')
        return

    # Go over every mapped bone and animate it
    # bone_name:                    Name if the bone
    # studio_reference_tpose_rot:   Studios reference t-pose rotation (still in Studio space)
    for bone_name, studio_reference_tpose_rot in animation_lists.actor_bones.items():

        # Gets the name of the bone assigned to this bone live data
        bone_name_assigned = getattr(obj, 'rsl_actor_' + bone_name)

        # Gets the assigned pose bone and it's global t-pose rotations
        bone = obj.pose.bones.get(bone_name_assigned)
        bone_data = obj.data.bones.get(bone_name_assigned)
        rot_global = tpose_rot_glob.get(bone_name_assigned)

        # Skip if there is no bone assigned to this live data or if there is no tpose data for this bone
        if not bone or not rot_global:
            continue

        # Set the bones quaternion mode and disable inherit rotation
        bone.rotation_mode = 'QUATERNION'
        bone_data.use_inherit_rotation = False

        # The global rotation of the models t-pose, which was set by the user
        bone_tpose_rot_global = Quaternion(rot_global)

        # The new pose in which the bone should be (still in Studio space)
        studio_new_pose = Quaternion((
            actor[bone_name]['rotation']['w'],
            actor[bone_name]['rotation']['x'],
            actor[bone_name]['rotation']['y'],
            actor[bone_name]['rotation']['z'],
        ))

        # Function to convert from Studio to Blender space
        def rot_to_blender(rota):
            return Quaternion((
                rota.w,
                rota.x,
                -rota.y,
                -rota.z,
            )) @ Quaternion((0, 0, 0, 1))

        # Calculate bone offset from tpose and add it to live data rotation
        rot_offset_ref = rot_to_blender(studio_reference_tpose_rot).inverted() @ bone_tpose_rot_global
        final_rot = rot_to_blender(studio_new_pose) @ rot_offset_ref

        # Set new bone rotation
        orig_loc, _, _ = bone.matrix.decompose()
        orig_loc_mat = Matrix.Translation(orig_loc)
        rotation_mat = final_rot.to_matrix().to_4x4()

        bone.matrix = orig_loc_mat @ rotation_mat

        # If hips bone, set its position
        if bone_name == 'hip':
            if tpose_loc:
                tpose_hip_location_y = tpose_loc.get(bone_name_assigned)[1]

                location_new = pos_hips_studio_to_blender(
                    actor[bone_name]['position']['x'] * tpose_hip_location_y,
                    actor[bone_name]['position']['y'] * tpose_hip_location_y - tpose_hip_location_y,
                    actor[bone_name]['position']['z'] * tpose_hip_location_y)

                bone.location = location_new
                # print(bone.location, obj.matrix_world @ bone.matrix @ bone.location)
            else:
                print('Location missing from tpose data, please set tpose of this armature again!')

        # Record the data
        if bpy.context.scene.rsl_recording:
            bone.keyframe_insert(data_path='rotation_quaternion', group=obj.name)
            if bone_name == 'hip':
                bone.keyframe_insert(data_path='location', group=obj.name)


def pos_hips_studio_to_blender(x, y, z):
    return -x, y, z


def pos_studio_to_blender(x, y, z):
    return -x, -z, y


def rot_studio_to_blender(w, x, y, z):
    return w, x, z, -y
