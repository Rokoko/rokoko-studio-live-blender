import time

import bpy
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
    # start_time = time.clock()
    for obj in bpy.data.objects:
        # Animate all trackers and props
        if props or trackers:
            if obj.rsl_animations_props_trackers and obj.rsl_animations_props_trackers != 'None':
                obj_id = obj.rsl_animations_props_trackers.split('|')

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

        # Animate all faces
        if faces and obj.type == 'MESH':
            if not hasattr(obj.data, 'shape_keys') or not hasattr(obj.data.shape_keys, 'key_blocks'):
                continue
            if not obj.rsl_animations_faces or obj.rsl_animations_faces == 'None':
                continue

            face = [face for face in faces if face['faceId'] == obj.rsl_animations_faces]
            if not face:
                continue

            for shape in animation_lists.face_shapes:
                if obj.data.shape_keys.key_blocks.get(getattr(obj, 'rsl_face_' + shape)):
                    obj.data.shape_keys.key_blocks[getattr(obj, 'rsl_face_' + shape)].slider_min = -1
                    obj.data.shape_keys.key_blocks[getattr(obj, 'rsl_face_' + shape)].value = face[0][shape] / 100

        # Animate all actors
        elif actors and obj.type == 'ARMATURE':
            if not obj.rsl_animations_actors or obj.rsl_animations_actors == 'None':
                continue

            actor = [actor for actor in actors if actor['id'] == obj.rsl_animations_actors]
            if not actor:
                continue

            # print(actor)
            # print()
            # i = 0
            # rounder = 5
            # for key, value in actor[0].items():
            #     i += 1
            #     if i <= 6:
            #         continue
            #
            #     # print(key, value)
            #     print('actor_bones[\'' + key + '\'] = Quaternion(('
            #           + str(round(value['rotation']['w'], rounder)) + ', '
            #           + str(round(value['rotation']['x'], rounder)) + ', '
            #           + str(round(value['rotation']['y'], rounder)) + ', '
            #           + str(round(value['rotation']['z'], rounder))
            #           + '))')

            # Get current custom data
            custom_data = obj.get('CUSTOM')
            if not custom_data:
                print('NO CUSTOM DATA')
                continue

            # Get tpose data from custom data
            tpose_rot = custom_data.get('rsl_tpose_rotation_global')
            if not tpose_rot:
                print('NO TPOSE DATA')
                continue

            # print()
            for bone_name, ref_rot in animation_lists.actor_bones.items():
                bone = obj.pose.bones.get(getattr(obj, 'rsl_actor_' + bone_name))
                # bone_edit = obj.data.bones.get(getattr(obj, 'rsl_actor_' + bone_name))
                rot = tpose_rot.get(getattr(obj, 'rsl_actor_' + bone_name))
                if bone and rot:



                    # If bone is top parent, set it's position
                    # if bone_name == 'hip':
                    #     bone.location = pos_actor_studio_to_blender(
                    #         actor[0][bone_name]['position']['x'] * 100,
                    #         actor[0][bone_name]['position']['y'] * 100,
                    #         actor[0][bone_name]['position']['z'] * 100,
                    #     )

                    bone.rotation_mode = 'QUATERNION'

                    if 1 == 2:
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

                        return

                    bone_tpose_rot = Quaternion(rot)
                    bone_current_pose = Quaternion(bone.matrix.to_euler().to_quaternion())
                    bone_new_pose_raw = Quaternion((
                        actor[0][bone_name]['rotation']['w'],
                        actor[0][bone_name]['rotation']['x'],
                        actor[0][bone_name]['rotation']['y'],
                        actor[0][bone_name]['rotation']['z'],
                    ))
                    ref_rot_new = Quaternion((
                        ref_rot.w,
                        ref_rot.x,
                        ref_rot.y,
                        ref_rot.z,
                    ))

                    up = Vector((0, 1, 1))
                    dest = Vector((1, 1, 1))
                    r = up.rotation_difference(dest).to_matrix().to_4x4().to_quaternion()

                    bone_offset_ref = bone_tpose_rot.inverted() @ ref_rot_new

                    # bone_offset = bone_current_pose.inverted() @ ref_rot_new
                    bone_offset = bone_current_pose.inverted() @ bone_new_pose_raw

                    bone_offset_diff = bone_offset_ref.inverted() @ bone_offset

                    bone_result = bone.rotation_quaternion @ bone_offset @ bone_offset_ref.inverted()  # @ Quaternion((0, 0, 0, 1))  # @ bone_offset_ref # @ Quaternion((0, 0, 0, 1))

                    if bone_name == 'spine':
                        # print(bone_current_pose, ref_rot_new, bone_offset)
                        # print(bone_offset, bone.rotation_quaternion, bone_result)
                        print(bone_name, bone_offset_diff, bone_tpose_rot, ref_rot_new)
                        print(bone_name, bone_tpose_rot.rotation_difference(ref_rot_new))
                        print(bone_name, bone_tpose_rot.inverted() @ ref_rot_new)

                        pass

                    bone.rotation_quaternion = bone_result
                    

                    # Test the old and new animation files in Unity

                    continue




                    # Debug stuff

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

    # end_time = time.clock()
    # delta = end_time - start_time
    # print()
    # print(start_time)
    # print(end_time)
    # print(time.clock(), delta, 60 / delta)


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

