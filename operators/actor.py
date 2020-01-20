import bpy
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

        # Create tpose data
        tpose_location_local = {}
        tpose_location_object = {}
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

            object_space_location = bone.matrix @ bone.location
            tpose_location_local[bone.name] = bone.location
            tpose_location_object[bone.name] = object_space_location

        # Save data to custom data
        custom_data['rsl_tpose_location_local'] = tpose_location_local
        custom_data['rsl_tpose_location_object'] = tpose_location_object
        custom_data['rsl_tpose_rotation'] = tpose_rotation
        custom_data['rsl_tpose_rotation_global'] = tpose_rotation_global

        # Save custom data in object
        obj['CUSTOM'] = custom_data

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
        tpose_rotation = custom_data.get('rsl_tpose_rotation')
        if not tpose_rotation:
            self.report({'ERROR'}, 'Please set the T-Pose first.')
            return {'CANCELLED'}

        # Get tpose data from custom data
        tpose_location_local = custom_data.get('rsl_tpose_location_local')

        # Apply rotations to armature
        for bone_name, rot in tpose_rotation.items():
            bone = obj.pose.bones.get(bone_name)
            if bone:
                bone.rotation_mode = 'QUATERNION'
                bone.rotation_quaternion = rot
                if tpose_location_local[bone_name]:
                    bone.location = tpose_location_local[bone_name]

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
