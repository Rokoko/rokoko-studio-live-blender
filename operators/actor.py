import bpy
from mathutils import Quaternion


class InitTPose(bpy.types.Operator):
    bl_idname = "rsl.init_tpose"
    bl_label = "Set as T-Pose"
    bl_description = "Press this button if you have this armature in T-Pose"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object
        if obj.type != 'ARMATURE':
            self.report({'ERROR'}, 'This is not an armature!')
            return {'CANCELLED'}

        # Get current custom data
        custom_data = obj.get('CUSTOM')
        if not custom_data:
            custom_data = {}

        # Create tpose data
        tpose_rotation = {}
        tpose_rotation_global = {}
        for bone in obj.pose.bones:
            bone.rotation_mode = 'QUATERNION'
            tpose_rotation[bone.name] = bone.rotation_quaternion
            tpose_rotation_global[bone.name] = bone.matrix.to_quaternion()
            i = 6
            print('actor_bones[\'' + bone.name + '\'] = Quaternion(('
                  + str(round(tpose_rotation_global[bone.name][0], i)) + ', '
                  + str(round(tpose_rotation_global[bone.name][1], i)) + ', '
                  + str(round(tpose_rotation_global[bone.name][2], i)) + ', '
                  + str(round(tpose_rotation_global[bone.name][3], i))
                  + '))')

        # Save data to custom data
        custom_data['rsl_tpose_rotation'] = tpose_rotation
        custom_data['rsl_tpose_rotation_global'] = tpose_rotation_global

        # Save custom data in object
        obj['CUSTOM'] = custom_data

        # print()
        # for bone, rot in obj['CUSTOM']['rsl_tpose_rotation_global'].items():
        #     print(bone, Quaternion(rot))

        return {'FINISHED'}


class ResetTPose(bpy.types.Operator):
    bl_idname = "rsl.reset_tpose"
    bl_label = "Reset to T-Pose"
    bl_description = "Use this to reset the armature to it's T-Pose"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object
        if obj.type != 'ARMATURE':
            self.report({'ERROR'}, 'This is not an armature!')
            return {'CANCELLED'}

        # Get current custom data
        custom_data = obj.get('CUSTOM')
        if not custom_data:
            self.report({'ERROR'}, 'Please set the T-Pose first. 1')
            return {'CANCELLED'}

        # Get tpose data from custom data
        tpose_rotation = custom_data.get('rsl_tpose_rotation')
        if not tpose_rotation:
            self.report({'ERROR'}, 'Please set the T-Pose first. 2')
            return {'CANCELLED'}

        # Apply rotations to armature
        for bone_name, rot in tpose_rotation.items():
            bone = obj.pose.bones.get(bone_name)
            if bone:
                bone.rotation_mode = 'QUATERNION'
                bone.rotation_quaternion = rot

        return {'FINISHED'}


class PrintCurrentPose(bpy.types.Operator):
    bl_idname = "rsl.print_current_pose"
    bl_label = "Print"
    bl_description = "Debugging. Prints world rotation of armature bones"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object
        if obj.type != 'ARMATURE':
            self.report({'ERROR'}, 'This is not an armature!')
            return {'CANCELLED'}

        for bone in obj.pose.bones:
            bone.rotation_mode = 'QUATERNION'
            rot = bone.matrix.to_euler().to_quaternion().copy()
            i = 5
            print('actor_bones[\'' + bone.name + '\'] = Quaternion(('
                  + str(round(rot[0], i)) + ', '
                  + str(round(rot[1], i)) + ', '
                  + str(round(rot[2], i)) + ', '
                  + str(round(rot[3], i))
                  + '))')

        return {'FINISHED'}


class SaveTargetPose(bpy.types.Operator):
    bl_idname = "rsl.save_target_pose"
    bl_label = "Save Target Pose"
    bl_description = "Set this pose as target pose"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object
        if obj.type != 'ARMATURE':
            self.report({'ERROR'}, 'This is not an armature!')
            return {'CANCELLED'}

        # Get current custom data
        custom_data = obj.get('CUSTOM')
        if not custom_data:
            custom_data = {}

        # Create tpose data
        target_pose_rotation = {}
        for bone in obj.pose.bones:
            bone.rotation_mode = 'QUATERNION'
            target_pose_rotation[bone.name] = bone.matrix.to_euler().to_quaternion().copy()
            i = 6
            print('actor_bones[\'' + bone.name + '\'] = Quaternion(('
                  + str(round(target_pose_rotation[bone.name][0], i)) + ', '
                  + str(round(target_pose_rotation[bone.name][1], i)) + ', '
                  + str(round(target_pose_rotation[bone.name][2], i)) + ', '
                  + str(round(target_pose_rotation[bone.name][3], i))
                  + '))')

        # Save data to custom data
        custom_data['rsl_target_pose_rotation'] = target_pose_rotation

        # Save custom data in object
        obj['CUSTOM'] = custom_data

        return {'FINISHED'}
