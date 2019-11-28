import bpy
from ..core import animation_lists


class DetectFaceShapes(bpy.types.Operator):
    bl_idname = "rsl.detect_face_shapes"
    bl_label = "Auto Detect"
    bl_description = "Automatically detect face shape keys for supported naming schemes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object

        if not hasattr(obj.data, 'shape_keys') or not hasattr(obj.data.shape_keys, 'key_blocks'):
            self.report({'ERROR'}, 'This mesh has no shapekeys!')
            return {'CANCELLED'}

        for shape_name in animation_lists.face_shapes:
            for shapekey in obj.data.shape_keys.key_blocks:
                if shape_name.lower() in shapekey.name.lower():
                    setattr(obj, 'rsl_face_' + shape_name, shapekey.name)

        return {'FINISHED'}


class DetectActorBones(bpy.types.Operator):
    bl_idname = "rsl.detect_actor_bones"
    bl_label = "Auto Detect"
    bl_description = "Automatically detect actor bones for supported naming schemes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object

        # TODO: Remove this
        # bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        #
        # for bone in obj.data.edit_bones:
        #     if len(bone.children) == 1:
        #         p1 = bone.head
        #         p2 = bone.children[0].head
        #         dist = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2) ** (1 / 2)
        #
        #         # Only connect them if the other bone is a certain distance away, otherwise blender will delete them
        #         if dist > 0.005:
        #             bone.tail = bone.children[0].head
        #
        # bpy.ops.object.mode_set(mode='POSE', toggle=False)

        for bone_name in animation_lists.actor_bones.keys():
            for bone in obj.pose.bones:
                if bone_name.lower() in bone.name.lower():
                    setattr(obj, 'rsl_actor_' + bone_name, bone.name)

        return {'FINISHED'}
