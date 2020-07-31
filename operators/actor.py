import bpy
import copy

from . import receiver


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

        bones = {}

        # Save local and global space rotations and local and object space locations for each bone
        for bone in obj.pose.bones:
            # Save rotation mode
            rotation_mode = bone.rotation_mode
            if rotation_mode == 'QUATERNION':
                rotation_mode = 'XYZ'

            bone.rotation_mode = 'QUATERNION'
            bones[bone.name] = {
                'location_local': bone.location,
                'location_object': bone.matrix @ bone.location,
                'rotation_local': bone.rotation_quaternion,
                'rotation_global': bone.matrix.to_quaternion(),
                'inherit_rotation': obj.data.bones.get(bone.name).use_inherit_rotation,
            }
            # Load rotation mode
            bone.rotation_mode = rotation_mode

        # Save tpose data to custom data
        custom_data['rsl_tpose_bones'] = copy.deepcopy(bones)
        obj['CUSTOM'] = custom_data

        self.report({'INFO'}, 'T-Pose successfully saved!')
        return {'FINISHED'}


class ResetTPose(bpy.types.Operator):
    bl_idname = "rsl.reset_tpose"
    bl_label = "Reset to T-Pose"
    bl_description = "Use this to reset the armature to it's T-Pose"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if receiver.receiver_enabled:
            self.report({'ERROR'}, 'Receiver is currently running. Please stop it first.')
            return {'CANCELLED'}

        obj = context.object
        if obj.type != 'ARMATURE':
            self.report({'ERROR'}, 'This is not an armature!')
            return {'CANCELLED'}

        # Get current custom data
        custom_data = obj.get('CUSTOM')
        if not custom_data:
            self.report({'ERROR'}, 'Please set the T-Pose first.')
            return {'CANCELLED'}

        # Get tpose data from custom data
        tpose_bones = custom_data.get('rsl_tpose_bones')
        if not tpose_bones:
            self.report({'ERROR'}, 'Please set the T-Pose first.')
            return {'CANCELLED'}

        # Apply locations and rotations to bones
        for bone_name, data in tpose_bones.items():
            bone = obj.pose.bones.get(bone_name)
            if bone:
                # Save rotation mode
                rotation_mode = bone.rotation_mode
                if rotation_mode == 'QUATERNION':
                    rotation_mode = 'XYZ'

                bone.rotation_mode = 'QUATERNION'
                bone.rotation_quaternion = data['rotation_local']
                bone.location = data['location_local']
                obj.data.bones.get(bone_name).use_inherit_rotation = data['inherit_rotation']

                # Load rotation mode
                bone.rotation_mode = rotation_mode

        self.report({'INFO'}, 'T-Pose successfully restored!')
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
            # Save rotation mode
            rotation_mode = bone.rotation_mode
            if rotation_mode == 'QUATERNION':
                rotation_mode = 'XYZ'

            bone.rotation_mode = 'QUATERNION'
            rot = bone.matrix.to_euler().to_quaternion().copy()
            i = 5
            print('actor_bones[\'' + bone.name + '\'] = Quaternion(('
                  + str(round(rot[0], i)) + ', '
                  + str(round(rot[1], i)) + ', '
                  + str(round(rot[2], i)) + ', '
                  + str(round(rot[3], i))
                  + '))')

            # Load rotation mode
            bone.rotation_mode = rotation_mode

        return {'FINISHED'}
