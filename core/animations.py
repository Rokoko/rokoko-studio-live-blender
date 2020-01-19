import time

import bpy
from bpy_extras.io_utils import axis_conversion
from mathutils import Quaternion, Euler, Vector, Matrix
import math

from . import animation_lists
from . import utils

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
            animate_trackers_props(obj)

        # Animate all faces
        if faces and obj.type == 'MESH':
            animate_faces(obj)

        # Animate all actors
        elif actors and obj.type == 'ARMATURE':
            animate_actors(obj)


def animate_trackers_props(obj):
    if obj.rsl_animations_props_trackers and obj.rsl_animations_props_trackers != 'None':
        obj_id = obj.rsl_animations_props_trackers.split('|')

        # If object is a prop
        if obj_id[0] == 'PR':
            prop = [prop for prop in props if prop['id'] == obj_id[1]]
            if prop:
                obj.rotation_mode = 'QUATERNION'
                obj.location = pos_studio_to_blender(
                    prop[0]['position']['x'] * 10,
                    prop[0]['position']['y'] * 10,
                    prop[0]['position']['z'] * 10,
                )
                obj.rotation_quaternion = rot_studio_to_blender(
                    prop[0]['rotation']['w'],
                    prop[0]['rotation']['x'],
                    prop[0]['rotation']['y'],
                    prop[0]['rotation']['z'],
                )

        # If object is a tracker
        elif obj_id[0] == 'TR':
            tracker = [tracker for tracker in trackers if tracker['name'] == obj_id[1]]
            if tracker:
                obj.rotation_mode = 'QUATERNION'
                obj.location = pos_studio_to_blender(
                    tracker[0]['position']['x'] * 10,
                    tracker[0]['position']['y'] * 10,
                    tracker[0]['position']['z'] * 10,
                )
                obj.rotation_quaternion = rot_studio_to_blender(
                    tracker[0]['rotation']['w'],
                    tracker[0]['rotation']['x'],
                    tracker[0]['rotation']['y'],
                    tracker[0]['rotation']['z'],
                )

        if bpy.context.scene.rsl_recording:
            obj.keyframe_insert(data_path='location', group=obj.name)
            obj.keyframe_insert(data_path='rotation_quaternion', group=obj.name)


def animate_faces(obj):
    if not hasattr(obj.data, 'shape_keys') or not hasattr(obj.data.shape_keys, 'key_blocks'):
        return
    if not obj.rsl_animations_faces or obj.rsl_animations_faces == 'None':
        return

    face = [face for face in faces if face['faceId'] == obj.rsl_animations_faces]
    if not face:
        return

    for shape in animation_lists.face_shapes:
        shapekey = obj.data.shape_keys.key_blocks.get(getattr(obj, 'rsl_face_' + shape))
        if shapekey:
            shapekey.slider_min = -1
            shapekey.value = face[0][shape] / 100

            if bpy.context.scene.rsl_recording:
                shapekey.keyframe_insert(data_path='value', group=obj.name)


def animate_actors(obj):
    # Return if no actor is assigned to this object
    if not obj.rsl_animations_actors or obj.rsl_animations_actors == 'None':
        return

    # Get the actor data assigned to the object
    actor = [actor for actor in actors if actor['id'] == obj.rsl_animations_actors]
    if not actor:
        return

    # Get current custom data from this object
    # The models t-pose bone rotations, which are set by the user, are stored inside this custom data
    custom_data = obj.get('CUSTOM')
    if not custom_data:
        print('NO CUSTOM DATA')
        return

    # Get tpose data from custom data
    tpose_rot = custom_data.get('rsl_tpose_rotation')
    tpose_rot_glob = custom_data.get('rsl_tpose_rotation_global')
    # target_pose_rot = custom_data.get('rsl_target_pose_rotation')
    # if not tpose_rot or not tpose_rot_glob or not target_pose_rot:
    if not tpose_rot or not tpose_rot_glob:
        print('NO TPOSE DATA')
        return

    # print()
    # Go over every mapped bone and animate it
    for bone_name, ref_rot in animation_lists.actor_bones.items():

        # Gets the name of the bone assigned to this bone data
        bone_name_assigned = getattr(obj, 'rsl_actor_' + bone_name)

        # Gets the assigned pose bone and it's local and global t-pose rotations
        bone = obj.pose.bones.get(bone_name_assigned)
        bone_data = obj.data.bones.get(bone_name_assigned)
        rot = tpose_rot.get(bone_name_assigned)
        rot_glob = tpose_rot_glob.get(bone_name_assigned)
        # target_glob = target_pose_rot.get(bone_name_assigned)

        # if not bone or not rot or not rot_glob or not target_glob:
        if not bone or not rot or not rot_glob:
            continue

        '''
            Animation starts here
        '''

        # # If bone is top parent, set its position
        # if bone_name == 'hip':
        #     bone.location = pos_actor_studio_to_blender(
        #         actor[0][bone_name]['position']['x'],
        #         actor[0][bone_name]['position']['y'],
        #         actor[0][bone_name]['position']['z'],
        #     )

        # Set the bones quaternion mode
        bone.rotation_mode = 'QUATERNION'
        bone_data.use_inherit_rotation = False

        # The local and global rotation of the models t-pose, which was set by the user
        bone_tpose_rot = Quaternion(rot)
        bone_tpose_rot_glob = Quaternion(rot_glob)
        # bone_target_pose_rot = Quaternion(target_glob)

        # The current global rotation of this bone
        # INFO: Find a way to calculate the offset without using this to eliminate weird jiggling!
        # Edit: Found it, disabling use_inherit_rotation fixes it
        bone_current_pose = Quaternion(bone.matrix.to_euler().to_quaternion())
        bone_current_pose2 = obj.matrix_world @ bone.matrix

        # The new pose in which the bone should be (still in Studio space)
        bone_new_pose_raw = Quaternion((
            actor[0][bone_name]['rotation']['w'],
            actor[0][bone_name]['rotation']['x'],
            actor[0][bone_name]['rotation']['y'],
            actor[0][bone_name]['rotation']['z'],
        ))

        # Studios reference t-pose rotation (still in Studio space)
        bone_reference_raw = Quaternion((
            ref_rot.w,
            ref_rot.x,
            ref_rot.y,
            ref_rot.z,
        ))

        # Studios reference t-pose rotation imported into blender
        bone_reference_imported = animation_lists.actor_bones_ref[bone_name]

        converter = utils.BoneConverterPoseMode(bone)

        # Function to convert from Studio to Blender space
        # This does not work and has to be figured out
        # Converting from (w,x,y,z) to (w,z,y,-x) almost works
        def rot_to_blender_best(rota):
            return Quaternion((
                rota.w,
                rota.x,
                -rota.y,
                -rota.z,
            )) @ Quaternion((0, 0, 0, 1))

        '''
            Offset and pose calculations start here
        '''

        rot_offset_ref =  rot_to_blender_best(bone_reference_raw).inverted() @ bone_tpose_rot_glob
        final_rot = rot_to_blender_best(bone_new_pose_raw) @ rot_offset_ref

        orig_loc, orig_rot, orig_scale = bone.matrix.decompose()
        orig_loc_mat = Matrix.Translation(orig_loc)
        rotation_mat = final_rot.to_matrix().to_4x4()
        orig_scale_mat = Matrix.Scale(orig_scale[0],4,(1,0,0)) @ Matrix.Scale(orig_scale[1],4,(0,1,0)) @ Matrix.Scale(orig_scale[2],4,(0,0,1))
        
        bone.matrix = orig_loc_mat @ rotation_mat# @ orig_scale_mat

        if bpy.context.scene.rsl_recording:
            bone.keyframe_insert(data_path='rotation_quaternion', group=obj.name)
            # TODO: Add recording of hip position


'''
    Some Studio to Blender conversation test functions
'''


def pos_studio_to_blender(x, y, z):
    return -x, -z, y


def pos_actor_studio_to_blender(x, y, z):
    return -x, y, z


def rot_studio_to_blender(w, x, y, z):
    return w, x, z, -y


def rot_actor_studio_to_blender(w, x, y, z):
    return -w, x, y, z


def rot_quat_studio_to_blender(quat):
    return Quaternion((quat.w, quat.x, quat.z, -quat.y))

