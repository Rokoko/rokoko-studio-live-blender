from collections import OrderedDict

import bpy

from . import detector
from mathutils import Quaternion

retargeting = False


class BuildBoneList(bpy.types.Operator):
    bl_idname = "rsl.build_bone_list"
    bl_label = "Build Bone List"
    bl_description = "Builds the bone list from the animation and tries to automatically detect and match bones"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        bone_list = []
        bone_detection_list = detector.get_bone_list()
        armature_source = bpy.data.objects.get(context.scene.rsl_retargeting_armature_source)
        armature_target = bpy.data.objects.get(context.scene.rsl_retargeting_armature_target)

        # Get all bones from the animation
        for fc in armature_source.animation_data.action.fcurves:
            bone_name = fc.data_path.split('"')
            if len(bone_name) == 3 and bone_name[1] not in bone_list:
                bone_list.append(bone_name[1])

        # Clear the bone retargeting list
        context.scene.rsl_retargeting_bone_list.clear()

        # Then add all the bones to the list
        for bone_name in bone_list:
            bone_item = context.scene.rsl_retargeting_bone_list.add()
            bone_item.bone_name_source = bone_name

            main_bone_name = ''
            standardized_bone_name_source = detector.standardize_bone_name(bone_name)

            # Find the main bone name of the source bone
            for bone_main, bone_values in bone_detection_list.items():
                if standardized_bone_name_source in bone_values or standardized_bone_name_source == bone_main.lower():
                    main_bone_name = bone_main
                    break

            # print(bone_name, standardized_bone_name_source, main_bone_name)

            # If no main bone name was found, continue
            if not main_bone_name:
                continue

            # Go through the target armature and search for bones that fit the main source bone
            for bone in armature_target.pose.bones:
                bone_name_standardized = detector.standardize_bone_name(bone.name)

                if bone_name_standardized in bone_detection_list[main_bone_name]:
                    bone_item.bone_name_target = bone.name
                    break

        return {'FINISHED'}


class ClearBoneList(bpy.types.Operator):
    bl_idname = "rsl.clear_bone_list"
    bl_label = "Clear Bone List"
    bl_description = "Clears the bone list so that you can manually fill in all bones"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        for bone_item in context.scene.rsl_retargeting_bone_list:
            bone_item.bone_name_target = ''
        return {'FINISHED'}


class RetargetAnimation(bpy.types.Operator):
    bl_idname = "rsl.retarget_animation"
    bl_label = "Retarget Animation"
    bl_description = "Retargets the animation from the source armature to the target armature"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        armature_source = bpy.data.objects.get(context.scene.rsl_retargeting_armature_source)
        armature_target = bpy.data.objects.get(context.scene.rsl_retargeting_armature_target)
        properties = [p.identifier for p in armature_source.animation_data.bl_rna.properties if not p.is_readonly and p.identifier != 'action']

        # Get rotation matrix of both armatures
        mat_source = armature_source.matrix_local.decompose()[1].to_matrix().to_4x4()
        mat_target = armature_target.matrix_local.decompose()[1].to_matrix().to_4x4()

        # Calculate the rotation from the source armature to the target armature
        rot_transform = (mat_source.inverted() @ mat_target).to_quaternion()

        print(mat_source)
        print(mat_target)
        print(rot_transform)

        # Create animation data if none is found on the target armature
        if not armature_target.animation_data:
            armature_target.animation_data_create()

        # bpy.ops.nla.bake(frame_start=0, frame_end=282, visual_keying=True, only_selected=False, bake_types={'POSE'})

        # Create a duplicate of the animation
        action_new = armature_source.animation_data.action.copy()

        # Set up dictionary to store all rotation fcurves
        fc_dict = OrderedDict()

        # Put all rotation fcurves into the dictionary
        for fc in action_new.fcurves:
            data_path = fc.data_path
            data_path_strings = fc.data_path.replace('\'', '"').split('"')
            bone_name_new = ''

            # Only process rotation curves (for now)
            if len(data_path_strings) < 2 or data_path.endswith(('location', 'scale')):
                # print('IGNORE', data_path)
                action_new.fcurves.remove(fc)
                continue

            # Extract bone name from data_path
            bone_name = data_path_strings[1]

            # Get the target bone from corresponding the source bone from the bone list
            for bone_item in context.scene.rsl_retargeting_bone_list:
                if bone_item.bone_name_source == bone_name:
                    bone_name_new = bone_item.bone_name_target

            # If there is no corresponding bone, continue
            if not bone_name_new:
                # print('NO BONE', data_path)
                action_new.fcurves.remove(fc)
                continue

            # Replace source bone with target bone in data path and put it back together
            data_path_strings[1] = bone_name_new
            fc.data_path = '"'.join(data_path_strings)

            # Add fcurves to the dict to sort them by their bone name
            if not fc_dict.get(bone_name):  # TODO: Change to bone_name_new? On next 2 lines as well.
                fc_dict[bone_name] = []
            fc_dict[bone_name].append(fc)

            # if i < 1:
            #     print(bone_name, armature_source.pose.bones.get(bone_name).matrix)
            #     print(bone_name, armature_source.pose.bones.get(bone_name).matrix.to_quaternion())
            #     print(bone_name, armature_source.pose.bones.get(bone_name).rotation_quaternion)
            #
            #     print(bone_name, armature_target.pose.bones.get(bone_name_new).matrix)
            #     print(bone_name, armature_target.pose.bones.get(bone_name_new).matrix.to_quaternion())
            #     i += 1

        # Go over all fcurves and calculate the new rotation of the bones
        for bone_name, fcurves in fc_dict.items():
            if len(fcurves) != 4:
                print(bone_name, 'Not enough fcurves! Maybe euler rotations?')

            for key0, key1, key2, key3 in zip(fcurves[0].keyframe_points, fcurves[1].keyframe_points, fcurves[2].keyframe_points, fcurves[3].keyframe_points):

                rotation = Quaternion((
                    key0.co.y,
                    key1.co.y,
                    key2.co.y,
                    key3.co.y))
                # print(rotation)

                key0.co.y = rotation.w
                key1.co.y = rotation.x
                key2.co.y = rotation.y
                key3.co.y = rotation.z

                # rotation_new = rot_transform @ rotation
                #
                # # print(rotation_new)
                #
                # key0.co.y = rotation_new.w
                # key1.co.y = rotation_new.x
                # key2.co.y = rotation_new.y
                # key3.co.y = rotation_new.z

                # if bone_name == 'Hips':
                #     print(bone_name, key0.co)
                #     print(bone_name, key1.co)
                #     print(bone_name, key2.co)
                #     print(bone_name, key3.co)

        # Add the new animation to the target armature
        armature_target.animation_data.action = action_new

        # Transfer other animation settings over as well
        for prop in properties:
            print(prop)
            try:
                setattr(armature_target.animation_data, prop, getattr(armature_source.animation_data, prop).copy())
            except AttributeError:
                setattr(armature_target.animation_data, prop, getattr(armature_source.animation_data, prop))

        # Fix source and target armatures being changed after this operation and stop the clearing of the bones list in that case
        global retargeting
        retargeting = True
        context.scene.rsl_retargeting_armature_source = armature_source.name
        context.scene.rsl_retargeting_armature_target = armature_target.name
        retargeting = False

        self.report({'INFO'}, 'Retargeted animation.')
        return {'FINISHED'}
