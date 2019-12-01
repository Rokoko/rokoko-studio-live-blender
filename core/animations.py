import time

import bpy
from bpy_extras.io_utils import axis_conversion
from mathutils import Quaternion, Euler, Vector, Matrix

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
                    prop[0]['position']['x'],
                    prop[0]['position']['y'],
                    prop[0]['position']['z'],
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
                    tracker[0]['position']['x'],
                    tracker[0]['position']['y'],
                    tracker[0]['position']['z'],
                )
                obj.rotation_quaternion = rot_studio_to_blender(
                    tracker[0]['rotation']['w'],
                    tracker[0]['rotation']['x'],
                    tracker[0]['rotation']['y'],
                    tracker[0]['rotation']['z'],
                )


def animate_faces(obj):
    if not hasattr(obj.data, 'shape_keys') or not hasattr(obj.data.shape_keys, 'key_blocks'):
        return
    if not obj.rsl_animations_faces or obj.rsl_animations_faces == 'None':
        return

    face = [face for face in faces if face['faceId'] == obj.rsl_animations_faces]
    if not face:
        return

    for shape in animation_lists.face_shapes:
        if obj.data.shape_keys.key_blocks.get(getattr(obj, 'rsl_face_' + shape)):
            obj.data.shape_keys.key_blocks[getattr(obj, 'rsl_face_' + shape)].slider_min = -1
            obj.data.shape_keys.key_blocks[getattr(obj, 'rsl_face_' + shape)].value = face[0][shape] / 100


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
    if not tpose_rot or not tpose_rot_glob:
        print('NO TPOSE DATA')
        return

    # Go over every mapped bone and animate it
    for bone_name, ref_rot in animation_lists.actor_bones.items():

        # Gets the name of the bone assigned to this bone data
        bone_name_assigned = getattr(obj, 'rsl_actor_' + bone_name)

        # Gets the assigned pose bone and it's local and global t-pose rotations
        bone = obj.pose.bones.get(bone_name_assigned)
        bone_norm = obj.data.bones.get(bone_name_assigned)
        rot = tpose_rot.get(bone_name_assigned)
        rot_glob = tpose_rot_glob.get(bone_name_assigned)

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

        # The local and global rotation of the models t-pose, which was set by the user
        bone_tpose_rot = Quaternion(rot)
        bone_tpose_rot_glob = Quaternion(rot_glob)

        # The current global rotation of this bone
        # INFO: Find a way to calculate the offset without using this to eliminate weird jiggling!
        bone_current_pose = Quaternion(bone.matrix.to_euler().to_quaternion())
        bone_current_pose2 = obj.matrix_world @ bone.matrix

        print(bone_name, bone_current_pose, bone_current_pose2)
        # , bone_norm.roll

        # The new pose in which the bone should be (still in Studio space)
        bone_new_pose_raw = Quaternion((
            actor[0][bone_name]['rotation']['w'],
            actor[0][bone_name]['rotation']['x'],
            actor[0][bone_name]['rotation']['y'],
            actor[0][bone_name]['rotation']['z'],
        ))

        # Studios reference t-pose rotation
        bone_reference_raw = Quaternion((
            ref_rot.w,
            ref_rot.x,
            ref_rot.y,
            ref_rot.z,
        ))

        # Function to convert from Studio to Blender space
        # This does not work and has to be figured out
        # Converting from (w,x,y,z) to (w,z,y,-x) almost works
        def rot_to_blender(rota):
            return Quaternion((
                rota.w,
                rota.z,
                rota.y,
                rota.x,
            ))

        def rot_to_blender2(rota):
            m = axis_conversion(from_forward='Z',
                                from_up='Y',
                                to_forward='-Y',
                                to_up='Z').to_4x4()

            rot = m.to_euler().to_quaternion()

            return rota @ rot



        '''
            Offset and pose calculations start here
        '''

        # Get offset between studio reference tpose and new bone rotation
        rot_offset_new = bone_reference_raw.inverted() @ bone_new_pose_raw

        # print(rot_offset_new, rot_to_blender(rot_offset_new), rot_to_blender2(rot_offset_new))

        # Add this offset to the global tpose to get the new global rotation of the bone
        rot_tpose_new = bone_tpose_rot @ rot_to_blender(rot_offset_new)

        # Get offset between current local bone rotation and new global bone rotation
        rot_offset_from_current = bone.rotation_quaternion.inverted() @ rot_tpose_new

        # Add this offset to the current local bone rotation
        bone.rotation_quaternion = bone.rotation_quaternion @ rot_offset_from_current









        '''
            Below are calculation tests
        '''

        continue

        # Get offset between studio reference tpose and new bone rotation
        rot_offset_new = bone_reference_raw.inverted() @ bone_new_pose_raw

        # Add this offset to the global tpose to get the new global rotation of the bone
        rot_tpose_new = bone_tpose_rot_glob @ rot_to_blender(rot_offset_new)

        # Get offset between current global bone rotation and new global bone rotation
        rot_offset_from_current = bone_current_pose.inverted() @ rot_tpose_new

        # Add this offset to the current local bone rotation
        bone.rotation_quaternion = bone.rotation_quaternion @ rot_offset_from_current

        continue

        #####

        # # if bone_name == 'rightLowerArm':
        # bone.rotation_mode = 'XYZ'
        # # bone_new_pose_raw.y = -bone_new_pose_raw.y
        # bone_new_pose_euler = bone_new_pose_raw.to_euler('XYZ')
        # # bone_new_pose_euler.y += 180
        # print(bone_new_pose_raw, bone_new_pose_euler)
        # bone.rotation_euler = bone_new_pose_euler

        continue

        #####

        bone_new_pose = rot_to_blender3(bone_new_pose_raw)
        bone_reference = rot_to_blender3(bone_reference_raw)

        bone_offset = bone_current_pose.inverted() @ bone_new_pose

        bone_offset_ref = bone_reference.inverted() @ bone_tpose_rot_glob

        bone_result = bone.rotation_quaternion @ bone_offset @ bone_offset_ref

        bone.rotation_quaternion = bone_result # @ Quaternion((0, 0, 0, 1))

        continue

        #####

        bone_tpose_offset = bone_tpose_rot_glob.inverted() @ bone_current_pose

        bone.rotation_quaternion = bone_tpose_rot @ bone_tpose_offset

        print(bone_name, bone_tpose_rot_glob, bone_current_pose, bone_tpose_offset, bone_tpose_offset)

        continue

        #####

        # print(ref_rot.inverted() @ bone_new_pose_raw)
        # print(bone_reference.inverted() @ bone_new_pose)

        rotation_ultimate = Quaternion((0.5, 0.5, -0.5, 0.5))

        bone_new_target_offset = bone_reference.inverted() @ bone_new_pose_raw @ rotation_ultimate

        bone_new_target_offset_2 = Quaternion((
            bone_new_target_offset.w,
            bone_new_target_offset.z,
            bone_new_target_offset.y,
            -bone_new_target_offset.x,
        ))

        bone_new_pose_ult = Quaternion((
            actor[0][bone_name]['rotation']['w'],
            actor[0][bone_name]['rotation']['z'],
            actor[0][bone_name]['rotation']['y'],
            -actor[0][bone_name]['rotation']['z'],
        ))

        pose_ref_target_offset = bone_reference.inverted() @ bone_new_pose_raw

        if bone_name == 'rightUpperArm' or bone_name == 'rightLowerArm':
            print(bone_name, bone_reference.inverted(), bone_new_pose_raw, pose_ref_target_offset)

        pose_ref_target_offset_trans = Quaternion((
            pose_ref_target_offset.w,
            -pose_ref_target_offset.x,
            -pose_ref_target_offset.y,
            pose_ref_target_offset.z,
        ))

        bone_offset = bone_current_pose.inverted() @ pose_ref_target_offset_trans

        bone_new_pos = bone_current_pose @ bone_offset

        # bone.rotation_quaternion = bone_offset

        # pose_ref_tpose_offset = bone_tpose_rot.inverted() @ bone_reference

        # bone.rotation_quaternion = bone.rotation_quaternion @ bone_current_pose.inverted() @ bone_reference

        # pose_ref_tpose_offset = bone_tpose_rot.inverted() @ bone_reference

        # pose_new_rot_offset = bone_current_pose.inverted() @ bone_new_pose_raw

        # bone.rotation_quaternion = bone.rotation_quaternion @ pose_new_rot_offset @ pose_ref_tpose_offset

        continue

        #####

        up = Vector((0, 1, 1))
        dest = Vector((1, 1, 1))
        r = up.rotation_difference(dest).to_matrix().to_4x4().to_quaternion()

        bone_offset_ref = bone_tpose_rot.inverted() @ bone_reference

        # bone_offset = bone_current_pose.inverted() @ bone_reference
        bone_offset = bone_current_pose.inverted() @ bone_new_pose_raw

        bone_offset_diff = bone_offset_ref.inverted() @ bone_offset

        bone_result = bone.rotation_quaternion @ bone_offset @ bone_offset_ref.inverted()  # @ Quaternion((0, 0, 0, 1))  # @ bone_offset_ref # @ Quaternion((0, 0, 0, 1))

        if bone_name == 'spine':
            # print(bone_current_pose, bone_reference, bone_offset)
            # print(bone_offset, bone.rotation_quaternion, bone_result)
            print(bone_name, bone_offset_diff, bone_tpose_rot, bone_reference)
            print(bone_name, bone_tpose_rot.rotation_difference(bone_reference))
            print(bone_name, bone_tpose_rot.inverted() @ bone_reference)

            pass

        bone.rotation_quaternion = bone_result

        # Test the old and new animation files in Unity

        continue

        #####

        # ref_rot.x = -ref_rot.x
        # print(bone_name, bone_current_pose, bone_new_pose_raw)
        if bone_name == 'hips':  # If Hips

            bone_offset_ref = bone_tpose_rot.inverted() @ ref_rot_new

            bone_offset = bone_current_pose.inverted() @ ref_rot_new
            # bone_offset = bone_current_pose.inverted() @ bone_new_pose_raw.inverted()

            bone.rotation_quaternion = bone.rotation_quaternion @ bone_offset @ bone_offset_ref#   @ Quaternion((0, 0, 0, 1))#  @ bone_offset_ref @ Quaternion((0, 0, 0, 1))

        else:
            bone_offset_ref = bone_tpose_rot.inverted() @ ref_rot_new

            # bone_offset = bone_current_pose.inverted() @ ref_rot_new
            bone_offset = bone_current_pose.inverted() @ bone_new_pose_raw

            bone_offset_diff = bone_offset_ref.inverted() @ bone_offset

            bone_result = bone.rotation_quaternion @ bone_offset @ bone_offset_ref.inverted()  # @ Quaternion((0, 0, 0, 1))  # @ bone_offset_ref # @ Quaternion((0, 0, 0, 1))

            if bone_name == 'spine':
                # print(bone_current_pose, ref_rot_new, bone_offset)
                #print(bone_offset, bone.rotation_quaternion, bone_result)
                print(bone_name, bone_offset_diff, bone_tpose_rot, ref_rot_new)
                print(bone_name, bone_tpose_rot.rotation_difference(ref_rot_new))
                print(bone_name, bone_tpose_rot.inverted() @ ref_rot_new)

                pass

            bone.rotation_quaternion = bone_result

            # bone.rotation_quaternion = bone_result
            # bone.rotation_quaternion = Quaternion((
            #     round(bone_result.w, 10),
            #     round(bone_result.x, 10),
            #     round(bone_result.y, 10),
            #     round(bone_result.z, 10),
            # ))
            # bone.rotation_quaternion = bone_new_pose_raw

        continue

        #####

        if 1 == 2:  # This was done in order to learn how Quaternions multiplications work in Blender
            # leg_tpose = Quaternion((-0, 0, 0, 1))
            leg_tpose = Quaternion(rot)
            leg_ref_pose = Quaternion((0, 0, 0, -1))
            leg_current_pose = Quaternion(bone.matrix.to_euler().to_quaternion())
            leg_new_pose = Quaternion((-0, -0, 0.0995, 0.995))

            print()
            # print(leg_current_pose.inverted() @ leg_new_pose.inverted())
            # print(leg_current_pose.inverted() @ leg_new_pose)

            leg_offset_1 = leg_ref_pose.inverted() @ leg_tpose.inverted()
            print(leg_ref_pose)
            print(leg_tpose)
            print(leg_offset_1)

            leg_offset = leg_current_pose.inverted() @ leg_new_pose.inverted()

            leg_offset_2 = leg_tpose.inverted() @ leg_offset

            print(bone.rotation_quaternion)
            print(bone.rotation_quaternion @ leg_offset)

            bone.rotation_quaternion = bone.rotation_quaternion @ leg_offset @ leg_offset_1

            # bone.rotation_quaternion = bone.rotation_quaternion @ leg_offset_1

            continue


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

