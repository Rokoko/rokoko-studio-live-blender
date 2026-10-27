import bpy
import copy
from mathutils import Matrix, Vector

from . import receiver
from ..core import utils


def is_pose_streamed(obj):
    # The stream only animates armatures with T-Pose data, so only then does it overwrite the pose
    custom_data = obj.get('CUSTOM')
    return receiver.receiver_enabled and bool(custom_data and custom_data.get('rsl_tpose_bones'))


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

        if is_pose_streamed(obj):
            self.report({'ERROR'}, 'Stop the receiver first. This armature already has a T-Pose, so its current pose comes from the stream.')
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='OBJECT')

        # Get current custom data
        custom_data = obj.get('CUSTOM')
        if not custom_data:
            custom_data = {}

        bones = {}

        # Save local and global space rotations and local and object space locations for each bone
        for bone in obj.pose.bones:
            # Save rotation mode
            rotation_mode = bone.rotation_mode

            # Save bone pose data
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


class StraightenArms(bpy.types.Operator):
    bl_idname = "rsl.straighten_arms"
    bl_label = "Straighten Arms"
    bl_description = "Rotates the mapped arms straight out to the sides. Use this on A-Pose characters before setting the T-Pose"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object
        if obj.type != 'ARMATURE':
            self.report({'ERROR'}, 'This is not an armature!')
            return {'CANCELLED'}

        if is_pose_streamed(obj):
            self.report({'ERROR'}, 'Stop the receiver first. This armature already has a T-Pose, so the stream would overwrite the pose.')
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='OBJECT')

        # Get the mapped upper arm, lower arm and hand of both sides
        arms = {}
        missing = []
        for side in ['left', 'right']:
            arms[side] = []
            for bone_key in [side + 'UpperArm', side + 'LowerArm', side + 'Hand']:
                bone = obj.pose.bones.get(getattr(obj, 'rsl_actor_' + bone_key))
                if not bone:
                    missing.append(bone_key)
                arms[side].append(bone)

        if missing:
            self.report({'ERROR'}, 'Please map these bones first: ' + ', '.join(missing))
            return {'CANCELLED'}

        for side, (upper_arm, lower_arm, hand) in arms.items():
            if lower_arm not in upper_arm.children_recursive or hand not in lower_arm.children_recursive:
                self.report({'ERROR'}, 'The mapped ' + side + ' arm bones are not a parent-child chain!')
                return {'CANCELLED'}

        # World up direction in armature space, so this also works if the armature or its parent is rotated
        up = (obj.matrix_world.to_3x3().inverted() @ Vector((0, 0, 1))).normalized()

        for side, other_side in [('left', 'right'), ('right', 'left')]:
            upper_arm, lower_arm, hand = arms[side]

            # Sideways direction of the character: from the other upper arm joint to this one, flattened to horizontal
            outward = upper_arm.head - arms[other_side][0].head
            outward -= up * outward.dot(up)
            outward.normalize()

            # Save the current pose of the whole arm. All bones get moved together like one rigid piece,
            # so the hand and fingers stay attached even if a bone doesn't inherit its parent's rotation
            chain = [upper_arm] + upper_arm.children_recursive
            matrices = {bone.name: bone.matrix.copy() for bone in chain}

            # Rotate the upper arm and then the lower arm. Directions are measured from joint to joint, since bone tails are not reliable
            for joint, next_joint in [(upper_arm, lower_arm), (lower_arm, hand)]:
                pivot = matrices[joint.name].translation
                direction = matrices[next_joint.name].translation - pivot
                rotation = direction.rotation_difference(outward).to_matrix().to_4x4()
                transform = Matrix.Translation(pivot) @ rotation @ Matrix.Translation(-pivot)

                for bone in [joint] + joint.children_recursive:
                    matrices[bone.name] = transform @ matrices[bone.name]

            # Apply the new pose parent first and update in between, so each child is set relative to its parent's new pose
            for bone in chain:
                bone.matrix = matrices[bone.name]
                context.view_layer.update()

        self.report({'INFO'}, 'Arms straightened!')
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


class AddExampleActor(bpy.types.Operator):
    bl_idname = "rsl.add_example_actor"
    bl_label = "Add Example Actor"
    bl_description = "Adds a fully configured and working example actor to instantly start livestreaming from Rokoko Studio"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        utils.import_blend_file(utils.NEWTON_BLEND_FILE, False, "Rokoko Streaming Example")

        self.report({'INFO'}, 'Added example actor')
        return {'FINISHED'}
