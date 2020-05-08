import bpy
import copy

from . import detector
from ..core import utils
from ..core.auto_detect_lists import bones
from ..core.retargeting import get_source_armature, get_target_armature

RETARGET_ID = '_RSL_RETARGET'


class BuildBoneList(bpy.types.Operator):
    bl_idname = "rsl.build_bone_list"
    bl_label = "Build Bone List"
    bl_description = "Builds the bone list from the animation and tries to automatically detect and match bones"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        bone_list = []
        bone_detection_list = detector.get_bone_list()
        armature_source = get_source_armature()
        armature_target = get_target_armature()

        if not armature_source.animation_data or not armature_source.animation_data.action:
            self.report({'ERROR'}, 'No animation on the source armature found!'
                                   '\nSelect an armature with an animation as source.')
            return {'CANCELLED'}

        if armature_source.name == armature_target.name:
            self.report({'ERROR'}, 'Source and target armature are the same!'
                                   '\nPlease select different armatures.')
            return {'CANCELLED'}

        # Get all bones from the animation
        for fc in armature_source.animation_data.action.fcurves:
            bone_name = fc.data_path.split('"')
            if len(bone_name) == 3 and bone_name[1] not in bone_list:
                bone_list.append(bone_name[1])

        # Check if this animation is from Rokoko Studio. Ignore certain bones in that case
        is_rokoko_animation = False
        if 'newton' in bone_list and 'RightFinger1Tip' in bone_list and 'HeadVertex' in bone_list and 'LeftFinger2Metacarpal' in bone_list:
            is_rokoko_animation = True
            # print('Rokoko animation detected')

        # Clear the bone retargeting list
        context.scene.rsl_retargeting_bone_list.clear()

        spines_source = []
        spines_target = []

        # Then add all the bones to the list
        for bone_name in bone_list:
            if is_rokoko_animation and bone_name in bones.ignore_rokoko_retargeting_bones:
                continue

            bone_item = context.scene.rsl_retargeting_bone_list.add()
            bone_item.bone_name_source = bone_name

            main_bone_name = ''
            standardized_bone_name_source = detector.standardize_bone_name(bone_name)

            # Find the main bone name of the source bone
            for bone_main, bone_values in bone_detection_list.items():
                if standardized_bone_name_source in bone_values or standardized_bone_name_source == bone_main.lower():
                    main_bone_name = bone_main
                    break

            # If no main bone name was found, continue
            if not main_bone_name:
                continue

            # If it's a spine bone, it to the list for later fixing
            if main_bone_name == 'spine':
                spines_source.append(bone_name)
                continue

            # Go through the target armature and search for bones that fit the main source bone
            for bone in armature_target.pose.bones:
                bone_name_standardized = detector.standardize_bone_name(bone.name)

                if bone_name_standardized in bone_detection_list[main_bone_name]:
                    bone_item.bone_name_target = bone.name
                    break

        # Add target spines to list for later fixing
        for bone in armature_target.pose.bones:
            bone_name_standardized = detector.standardize_bone_name(bone.name)
            if bone_name_standardized in bone_detection_list['spine']:
                spines_target.append(bone.name)

        # Fix spine auto detection
        if spines_target and spines_source:
            spine_dict = {}

            i = 0
            for spine in reversed(spines_source):
                i += 1
                if i == len(spines_target):
                    break
                spine_dict[spine] = spines_target[-i]

            spine_dict[spines_source[0]] = spines_target[0]

            # Fill in fixed spines
            for spine_source, spine_target in spine_dict.items():
                for item in context.scene.rsl_retargeting_bone_list:
                    if item.bone_name_source == spine_source:
                        item.bone_name_target = spine_target

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
        armature_source = get_source_armature()
        armature_target = get_target_armature()

        if not armature_source.animation_data or not armature_source.animation_data.action:
            self.report({'ERROR'}, 'No animation on the source armature found!'
                                   '\nSelect an armature with an animation as source.')
            return {'CANCELLED'}

        if armature_source.name == armature_target.name:
            self.report({'ERROR'}, 'Source and target armature are the same!'
                                   '\nPlease select different armatures.')
            return {'CANCELLED'}

        # Find root bones
        root_bones = []
        for bone in armature_target.pose.bones:
            if not bone.parent:
                root_bones.append(bone)

        # Find animated root bones
        root_bones_animated = []
        target_bones = [item.bone_name_target for item in context.scene.rsl_retargeting_bone_list if
                        armature_target.pose.bones.get(item.bone_name_target) and armature_source.pose.bones.get(item.bone_name_source)]
        while root_bones:
            for bone in copy.copy(root_bones):
                root_bones.remove(bone)
                if bone.name in target_bones:
                    root_bones_animated.append(bone.name)
                else:
                    for bone_child in bone.children:
                        root_bones.append(bone_child)

        # Cancel if no root bones are found
        if not root_bones_animated:
            self.report({'ERROR'}, 'No root bone found!'
                                   '\nCheck if the bones are mapped correctly or try rebuilding the bone list.')
            return {'CANCELLED'}

        # Prepare armatures
        utils.set_active(armature_target)
        bpy.ops.object.mode_set(mode='OBJECT')
        utils.set_active(armature_source)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Save transforms of target armature
        rotation_mode = armature_target.rotation_mode
        armature_target.rotation_mode = 'QUATERNION'
        rotation = copy.deepcopy(armature_target.rotation_quaternion)
        location = copy.deepcopy(armature_target.location)

        # Apply transforms of the target armature
        bpy.ops.object.select_all(action='DESELECT')
        utils.set_active(armature_target)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        if context.scene.rsl_retargeting_auto_scaling:
            # Clean source animation
            self.clean_animation(armature_source)

            # Scale the source armature to fit the target armature
            self.scale_armature(context, armature_source, armature_target)

        bpy.ops.object.mode_set(mode='EDIT')

        # Create a transformation dict of all bones of the target armature and unselect all bones
        bone_transforms = {}
        for bone in context.object.data.edit_bones:
            bone.select = False
            bone_transforms[bone.name] = armature_source.matrix_world.inverted() @ bone.head.copy(), \
                                         armature_source.matrix_world.inverted() @ bone.tail.copy(), \
                                         utils.mat3_to_vec_roll(armature_source.matrix_world.inverted().to_3x3() @ bone.matrix.to_3x3())  # Head loc, tail loc, bone roll

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        utils.set_active(armature_source)
        bpy.ops.object.mode_set(mode='EDIT')

        # Recreate bones from target armature in source armature
        for item in context.scene.rsl_retargeting_bone_list:
            if not item.bone_name_source or not item.bone_name_target or item.bone_name_target not in bone_transforms:
                continue

            bone_source = armature_source.data.edit_bones.get(item.bone_name_source)
            if not bone_source:
                print('Skipped:', item.bone_name_source, item.bone_name_target)
                continue

            # Recreate target bone
            bone_new = armature_source.data.edit_bones.new(item.bone_name_target + RETARGET_ID)
            bone_new.head, bone_new.tail, bone_new.roll = bone_transforms[item.bone_name_target]
            bone_new.parent = bone_source

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        # Add constraints to target armature and select the bones for animation
        for item in context.scene.rsl_retargeting_bone_list:
            if not item.bone_name_source or not item.bone_name_target:
                continue

            bone_source = armature_source.pose.bones.get(item.bone_name_source)
            bone_target = armature_target.pose.bones.get(item.bone_name_target)
            bone_target_data = armature_target.data.bones.get(item.bone_name_target)

            if not bone_source or not bone_target or not bone_target_data:
                print('Bone mapping not found:', item.bone_name_source, item.bone_name_target)
                continue

            # Add constraints
            constraint = bone_target.constraints.new('COPY_ROTATION')
            constraint.name += RETARGET_ID
            constraint.target = armature_source
            constraint.subtarget = item.bone_name_target + RETARGET_ID

            if bone_target.name in root_bones_animated:
                constraint = bone_target.constraints.new('COPY_LOCATION')
                constraint.name += RETARGET_ID
                constraint.target = armature_source
                constraint.subtarget = item.bone_name_source

            # Select the bone for animation
            armature_target.data.bones.get(item.bone_name_target).select = True

        # Read the animation length from the animation
        frame_start = None
        frame_end = None
        for fcurve in armature_source.animation_data.action.fcurves:
            for key in fcurve.keyframe_points:
                keyframe = key.co.x
                if frame_start is None:
                    frame_start = keyframe
                if frame_end is None:
                    frame_end = keyframe

                if keyframe < frame_start:
                    frame_start = keyframe
                if keyframe > frame_end:
                    frame_end = keyframe

        # Bake the animation to the target armature
        utils.set_active(armature_target)
        bpy.ops.nla.bake(frame_start=frame_start, frame_end=frame_end, visual_keying=True, only_selected=True, bake_types={'POSE'})

        # Change action name
        armature_target.animation_data.action.name = armature_source.animation_data.action.name + ' Retarget'

        # Remove constraints from target armature
        for bone in armature_target.pose.bones:
            for constraint in bone.constraints:
                if RETARGET_ID in constraint.name:
                    bone.constraints.remove(constraint)

        bpy.ops.object.select_all(action='DESELECT')
        utils.set_active(armature_source)
        bpy.ops.object.mode_set(mode='EDIT')

        # Delete helper bones
        for bone in armature_source.data.edit_bones:
            if RETARGET_ID in bone.name:
                armature_source.data.edit_bones.remove(bone)

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        utils.set_active(armature_target)

        # Reset target armature transforms to old state
        armature_target.rotation_quaternion = rotation
        armature_target.location = location

        armature_target.rotation_quaternion.w = -armature_target.rotation_quaternion.w
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        armature_target.rotation_quaternion = rotation
        armature_target.rotation_mode = rotation_mode

        bpy.ops.object.select_all(action='DESELECT')

        self.report({'INFO'}, 'Retargeted animation.')
        return {'FINISHED'}

    def clean_animation(self, armature_source):
        deletable_fcurves = ['location', 'rotation_euler', 'rotation_quaternion', 'scale']
        for fcurve in armature_source.animation_data.action.fcurves:
            if fcurve.data_path in deletable_fcurves:
                armature_source.animation_data.action.fcurves.remove(fcurve)

    def scale_armature(self, context, armature_source, armature_target):
        source_max = None
        source_min = None
        target_max = None
        target_min = None

        for item in context.scene.rsl_retargeting_bone_list:
            if not item.bone_name_source or not item.bone_name_target:
                continue

            bone_source = armature_source.pose.bones.get(item.bone_name_source)
            bone_target = armature_target.pose.bones.get(item.bone_name_target)
            if not bone_source or not bone_target:
                continue

            bone_source_z = (armature_source.matrix_world @ bone_source.head)[2]
            bone_target_z = (armature_target.matrix_world @ bone_target.head)[2]

            if source_max is None or source_max < bone_source_z:
                source_max = bone_source_z
            if source_min is None or source_min > bone_source_z:
                source_min = bone_source_z

            if target_max is None or target_max < bone_target_z:
                target_max = bone_target_z
            if target_min is None or target_min > bone_target_z:
                target_min = bone_target_z#

        source_height = source_max - source_min
        target_height = target_max - target_min
        scale_factor = target_height / source_height

        armature_source.scale *= scale_factor




