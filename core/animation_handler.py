
import bpy
from mathutils import Quaternion, Matrix, Vector

from . import utils, live_data_manager, animation_lists


# Todo: Add actor class in here, make it create it's own armature and store them independent from the live data packets


class Animator:

    def __init__(self):
        self.armature = None

        self.t_pose_data = {}
        self.t_pose_hips_height = 0

    def setup(self):
        if self.armature:
            self.destroy()

        self.armature = bpy.data.objects.get("Rokoko Armature")
        if self.armature and self.armature.data.name == "Rokoko":
            self.destroy()

        # utils.print_armature_data("Character1_Reference")

        # Create armature
        self.armature = utils.add_armature(edit=True)
        self.armature.name = "Rokoko Armature"
        self.armature.data.name = "Rokoko"

        # Load default armature data
        data = utils.load_default_armature()

        # Delete all existing bones
        for bone in self.armature.data.edit_bones:
            self.armature.data.edit_bones.remove(bone)

        # Create bones from data
        for bone_data in data:
            bone = self.armature.data.edit_bones.new(bone_data["name"])
            bone.head = bone_data["position_head"]
            bone.tail = bone_data["position_tail"]

        # Set parents
        for bone_data in data:
            bone = self.armature.data.edit_bones[bone_data["name"]]
            parent_bone = self.armature.data.edit_bones[bone_data["parent"]] if bone_data["parent"] else None
            bone.parent = parent_bone

        # Enter object mode
        bpy.ops.object.mode_set(mode="OBJECT")

        # Disable bones inherit rotation
        for bone in self.armature.data.bones:
            bone.use_inherit_rotation = False

        # Set the bones rotation mode to euler
        for bone in self.armature.pose.bones:
            if bone.rotation_mode == 'QUATERNION':
                bone.rotation_mode = 'XYZ'

            # Set the tpose data
            self.t_pose_data[bone.name] = bone.matrix.to_quaternion()

        # Set hips height for the t pose
        self.t_pose_hips_height = self.armature.pose.bones["hip"].location[1]

    def destroy(self):
        if not self.armature:
            return

        try:
            bpy.data.armatures.remove(self.armature.data, do_unlink=True)
        except ReferenceError:
            pass
        self.armature = None

    def animate(self, live_data: live_data_manager.LiveDataPacket):

        for actor in live_data.actors:
            for bone_name, values in actor.bones.items():
                if bone_name.endswith("End") or bone_name.endswith("Tip"):
                    continue
                bone = self.armature.pose.bones[bone_name]

                rot_data = values["rotation"]
                rotation = Quaternion((rot_data["w"], rot_data["x"], rot_data["y"], rot_data["z"]))

                studio_reference_tpose_rot = animation_lists.get_bone_default_rotation(bone_name, True)

                # The global rotation of the models t-pose, which was set by the user
                bone_tpose_rot_global = self.t_pose_data[bone_name]

                # The new pose in which the bone should be (still in Studio space)
                studio_new_pose = rotation

                mat_obj = self.armature.matrix_local.decompose()[1].to_matrix().to_4x4()
                mat_default = Matrix((
                    (1, 0, 0, 0),
                    (0, 0, -1, 0),
                    (0, 1, 0, 0),
                    (0, 0, 0, 1)
                ))
                rot_transform = (mat_default.inverted() @ mat_obj).to_quaternion()

                def transform(rot):
                    return rot_transform @ rot

                def transform_back(rot):
                    return rot_transform.inverted() @ rot

                # Transform rotation matrix of tpose to target space
                bone_tpose_rot_global = transform(bone_tpose_rot_global)

                # Calculate bone offset from tpose and add it to live data rotation
                rot_offset_ref = rot_to_blender(studio_reference_tpose_rot).inverted() @ bone_tpose_rot_global
                final_rot = rot_to_blender(studio_new_pose) @ rot_offset_ref

                # Transform rotation matrix back from target space
                final_rot = transform_back(final_rot)

                # Set new bone rotation
                orig_loc, _, _ = bone.matrix.decompose()
                orig_loc_mat = Matrix.Translation(orig_loc)
                rotation_mat = final_rot.to_matrix().to_4x4()

                # Set final bone matrix
                bone.matrix = orig_loc_mat @ rotation_mat

                if bone_name != "hip":
                    continue

                # Set location of the hip
                pos_data = values["position"]

                y = pos_data["y"]
                y_live_data_hips_offset_modifier = y / actor.hips_height
                y_adjusted = self.t_pose_hips_height * y_live_data_hips_offset_modifier

                y_adjusted = y - actor.hips_height

                position = Vector((pos_data["x"], y_adjusted, pos_data["z"]))
                bone.location = pos_hips_studio_to_blender(position)


def pos_hips_studio_to_blender(vec):
    return Vector((
        -vec.x,
        vec.y,
        vec.z
    ))


# Function to convert from Studio to Blender space
def rot_to_blender(rot):
    return Quaternion((
        rot.w,
        rot.x,
        -rot.y,
        -rot.z,
    )) @ Quaternion((0, 0, 0, 1))
