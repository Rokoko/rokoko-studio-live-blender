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
    target_pose_rot = custom_data.get('rsl_target_pose_rotation')
    if not tpose_rot or not tpose_rot_glob or not target_pose_rot:
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
        target_glob = target_pose_rot.get(bone_name_assigned)

        if not bone or not rot or not rot_glob or not target_glob:
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
        bone_target_pose_rot = Quaternion(target_glob)

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
        def rot_to_blender(rota):
            return Quaternion((
                rota.w,
                rota.x,
                -rota.y,
                -rota.z,
            )) @ Quaternion((0, 0, 0, 1))

        def rot_to_blender_best(rota):
            return Quaternion((
                rota.w,
                rota.x,
                rota.y,
                -rota.z,
            )) @ Quaternion((0, 0, 0, 1))

        def rot_to_blender_after(rota):
            return Quaternion((
                rota.w,
                rota.x,
                -rota.y,
                rota.z,
            )) # @ Quaternion((0, 0, 0, 1))

        def rot_to_blender2(rota):
            m = axis_conversion(from_forward='Z',
                                from_up='Y',
                                to_forward='Y',
                                to_up='-Z').to_4x4()

            rot = m.to_euler().to_quaternion()

            return rota @ rot

        def rot_to_blender3(rota):
            mat = bone.matrix.to_3x3()
            mat[1], mat[2] = mat[2].copy(), mat[1].copy()
            __mat = mat.transposed()
            __mat_rot = bone.matrix_basis.to_3x3()

            rot = Quaternion((rota.w, rota.x, rota.y, rota.z))
            rot = Quaternion((__mat @ rot.axis) * -1, rot.angle)
            return (__mat_rot @ rot.to_matrix()).to_quaternion()

        def rot_to_blender0(rota):
            return Quaternion((
                rota.w,
                -rota.z,
                -rota.y,
                rota.x,
            ))  # @ Quaternion((0, 0, 0, 1))

        def rot_to_blender2(rota):
            m = axis_conversion(from_forward='Z',
                                from_up='Y',
                                to_forward='-Y',
                                to_up='Z').to_4x4()

            rot = m.to_euler().to_quaternion()

            return rota @ rot

        def rotate_around_center(mat_rot, center):
            return (Matrix.Translation(center) *
                    mat_rot *
                    Matrix.Translation(-center))

        def rotation_90(rot_old):
            q = Quaternion((1, 0, 0), math.radians(90))
            rot_new = q @ rot_old
            return rot_new

        '''
            Offset and pose calculations start here
        '''

        rot_offset_ref = bone_tpose_rot_glob.inverted() @ rot_to_blender_best(bone_reference_raw)
        rot_offset_target = bone_tpose_rot_glob.inverted() @ rot_to_blender_best(bone_new_pose_raw)

        rot_ref = bone_tpose_rot @ rot_offset_ref
        rot_target = bone_tpose_rot @ rot_offset_target

        rot_offset_new = rot_ref.inverted() @ rot_target
        bone.rotation_quaternion = bone_tpose_rot @ rot_offset_new

        # Record animation
        if bpy.context.scene.rsl_recording:
            bone.keyframe_insert(data_path='rotation_quaternion', group=obj.name)
            # obj.keyframe_insert(data_path='pose.bones["' + bone.name + '"].rotation_quaternion', group=obj.name)
            # TODO: Add recording of hip position

        '''
            Below are previous calculation tests
        '''

        continue

        # bone.rotation_quaternion = bone_reference_raw

        # eu = Euler(map(math.radians, (0.0, 0.0, 90.0)), 'XYZ').to_matrix().to_4x4()
        # newRotMat = rotate_around_center(eu, bone.matrix.location) * bone.matrix

        # q = Quaternion((0, 1, 0), math.radians(90))
        # print(q)
        # print(Quaternion((0, -0.707107, 0, -0.707107)).inverted() @ Quaternion((-0.707107, 0, -0.707107, 0)))
        #
        # bone.rotation_quaternion = q @ bone_reference_raw @ Quaternion((0, 0, 0, -1))

        # print(bone_name, bone.rotation_quaternion, bone.matrix_local.rotation_quaternion)

        # continue

        # Get offset between studio reference tpose and new bone rotation
        # rot_offset_new = bone_tpose_rot_glob.inverted() @ bone_target_pose_rot
        # rot_offset_new_2 = bone_tpose_rot_glob.inverted() @ rot_to_blender(bone_new_pose_raw)
        # rot_offset_new = rot_to_blender(bone_reference_raw).inverted() @ rot_to_blender(bone_new_pose_raw)
        # rot_offset_new = rot_to_blender(bone_reference_raw.inverted() @ bone_new_pose_raw)

        rot_offset_ref = bone_tpose_rot_glob.inverted() @ rot_to_blender_best(bone_reference_raw)
        # rot_offset_ref = bone_tpose_rot_glob.inverted() @ bone_reference_imported
        rot_offset_target = bone_tpose_rot_glob.inverted() @ rot_to_blender_best(bone_new_pose_raw)

        rot_ref = bone_tpose_rot @ rot_offset_ref
        rot_target = bone_tpose_rot @ rot_offset_target

        rot_offset_new = rot_ref.inverted() @ rot_target

        # if bone_name in ['leftUpperArm']:
        #     print()
        #     print(bone_name, rot_ref, rot_target, rot_offset_new)
        #     print(bone_name, bone.rotation_quaternion, bone_tpose_rot @ rot_offset_new)
        #     # print(bone_name, rot_ref, rot_target, rot_offset_new, rot_ref.axis, rot_target.axis)

        q = Quaternion((0, 1, 0), math.radians(90))

        # bone.rotation_quaternion = rot_ref
        bone.rotation_quaternion = rot_target
        # bone.rotation_quaternion = bone_tpose_rot @ rot_offset_new
        # bone.rotation_quaternion = bone_tpose_rot  @ rot_offset_new.inverted()@ q
        # bone.rotation_quaternion @= rot_offset_new.inverted()
        # bone.rotation_quaternion = bone_tpose_rot @ rot_to_blender_after(rot_offset_new)
        # bone.rotation_quaternion = bone_tpose_rot @ rot_offset_new_2




        # # Calculate rotation on the reference armature to get from the its tpose to its new pose
        # offset_to_new_pose = reference_tpose.inverted() @ reference_new_pose
        #
        # # Add this rotation to the target tpose
        # bone.rotation_quaternion = target_tpose @ offset_to_new_pose

        continue

        ###### This is the best I currently have
        def rot_to_blender_best(rota):
            return Quaternion((
                rota.w,
                rota.x,
                rota.y,
                -rota.z,
            )) @ Quaternion((0, 0, 0, 1))

        rot_offset_ref = bone_tpose_rot_glob.inverted() @ rot_to_blender_best(bone_reference_raw)
        rot_offset_target = bone_tpose_rot_glob.inverted() @ rot_to_blender_best(bone_new_pose_raw)

        rot_ref = bone_tpose_rot @ rot_offset_ref
        rot_target = bone_tpose_rot @ rot_offset_target

        rot_offset_new = rot_ref.inverted() @ rot_target
        bone.rotation_quaternion = bone_tpose_rot @ rot_offset_new

        continue

        # Get offset between studio reference tpose and new bone rotation

        rot_offset_new = bone_tpose_rot_glob.inverted() @ bone_target_pose_rot
        # rot_offset_new = bone_tpose_rot_glob.inverted() @ bone_current_pose
        # rot_offset_new = bone_tpose_rot_glob.inverted() @ rot_to_blender(bone_new_pose_raw)
        # rot_offset_new = rot_to_blender(bone_reference_raw).inverted() @ rot_to_blender(bone_new_pose_raw)
        # rot_offset_new = (bone_reference_raw @ Quaternion((0, 1, 0, 0))).inverted() @ rot_to_blender(bone_new_pose_raw)
        # rot_offset_new = bone_reference_raw.inverted() @ bone_new_pose_raw

        # print(rot_offset_new, rot_to_blender(bone_reference_raw), rot_to_blender2(bone_reference_raw), converter.convert_rotation(bone_reference_raw))

        # Add this offset to the global tpose to get the new global rotation of the bone
        rot_tpose_new = bone_tpose_rot @ rot_offset_new
        rot_tpose_new_glob = bone_tpose_rot_glob @ rot_offset_new
        # rot_tpose_new = bone_tpose_rot @ rot_to_blender2(rot_offset_new)


        rot_offset_to_new = bone_current_pose.inverted() @ rot_tpose_new_glob

        bone.rotation_quaternion = bone.rotation_quaternion @ rot_offset_to_new  #  @ Quaternion((0, 0, 0, 1))

        if bone_name in ['hip']:
            print(bone_name, rot_offset_new, rot_tpose_new, rot_offset_to_new)

        def get_parent_offset(bone, rot_tpose):
            if not bone.parent:
                return rot_tpose

            parent_current_rot = Quaternion(bone.parent.matrix.to_euler().to_quaternion())

            # offset_from_parent = parent_current_rot.inverted() @ rot_tpose
            offset_from_parent = bone.parent.rotation_quaternion.inverted() @ rot_tpose

            tpose_new = bone_tpose_rot @ offset_from_parent

            return get_parent_offset(bone.parent, tpose_new)

        continue


        offset_from_parent = Quaternion((1, 0, 0, 0))
        if bone.parent:
            parent_current_rot = Quaternion(bone.parent.matrix.to_euler().to_quaternion())

            offset_from_parent = parent_current_rot.inverted() @ rot_tpose_new

            # rot_tpose_new = bone_tpose_rot @ offset_from_parent

        # Add this offset to the current local bone rotation
        bone.rotation_quaternion = bone.rotation_quaternion @ offset_from_parent

        continue

        rot_offset_to_new = bone_current_pose.inverted() @ rot_offset_new

        # Add this offset to the current local bone rotation
        bone.rotation_quaternion = bone.rotation_quaternion @ rot_offset_to_new

        continue

        # Inverse kinematics
        rot_tpose_new_2 = get_parent_offset(bone, rot_tpose_new)

        # Get offset between current local bone rotation and new global bone rotation
        rot_offset_from_current = bone.rotation_quaternion.inverted() @ rot_tpose_new_2
        if bone_name in ['leftHand']:
            print(bone_name, rot_offset_new, rot_tpose_new, rot_tpose_new_2, rot_offset_from_current)

        # if bone_name == 'hips':
        #     rot_offset_from_current = rot_offset_from_current @ Quaternion((0, 0, 0, 1))

        # Add this offset to the current local bone rotation
        bone.rotation_quaternion = bone.rotation_quaternion @ rot_offset_from_current

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

        # rot_parent_current = Quaternion((1, 0, 0, 0))
        # if pose.bones[bonename].parent:
        #
        #     # the matrix from file
        #     matrix = frames[frame][bonenumber]
        #
        #     # Calculate bone vector(armature space).
        #     pos = matrix.to_translation()
        #     vector = matrix.to_3x3().col[1]
        #
        #     # Calculate rotation from parent bone vector to bone vector
        #     parent_vector = mathutils.Vector((0.0, 0.0, 1.0))
        #     rotation = parent_vector.rotation_difference(vector)
        #
        #     # Calculate bone head(armature space)
        #     head = pos
        #
        #     # Assign rotation and location to your Posebone.matrix.
        #     newmatrix = rotation.to_matrix()
        #     newmatrix.resize_4x4()
        #     newmatrix[0][3] = head.x
        #     newmatrix[1][3] = head.y
        #     newmatrix[2][3] = head.z
        #
        #     bs_mat = mathutils.Quaternion(mathutils.Vector((1.0, 0.0, 0.0)), .5 * 3.14159).normalized().to_matrix().to_4x4()
        #
        #     newmatrix = newmatrix * bs_mat
        #
        #     pose.bones[bonename].matrix = newmatrix

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

