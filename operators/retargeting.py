import bpy

from . import detector


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
        self.report({'INFO'}, 'Retargeted animation.')
        return {'FINISHED'}
