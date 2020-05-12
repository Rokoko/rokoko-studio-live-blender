import bpy

from ..core import animation_lists
from ..core import detection_manager


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
            shortest_detected_shape = None
            for shapekey in obj.data.shape_keys.key_blocks:
                if shape_name.lower() in shapekey.name.lower():
                    if not shortest_detected_shape or len(shortest_detected_shape) > len(shapekey.name):
                        shortest_detected_shape = shapekey.name

            if shortest_detected_shape:
                setattr(obj, 'rsl_face_' + shape_name, shortest_detected_shape)

        return {'FINISHED'}


class DetectActorBones(bpy.types.Operator):
    bl_idname = "rsl.detect_actor_bones"
    bl_label = "Auto Detect"
    bl_description = "Automatically detect actor bones for supported naming schemes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object

        for bone_name_key in animation_lists.actor_bones.keys():
            bone_names = detection_manager.get_bone_list()[bone_name_key]
            for bone in obj.pose.bones:
                bone_name = detection_manager.standardize_bone_name(bone.name)
                if bone_name in bone_names:
                    setattr(obj, 'rsl_actor_' + bone_name_key, bone.name)

                    # If looking for the chest bone, use the last found entry instead of the first one
                    if bone_name_key != 'chest':
                        break

        return {'FINISHED'}


class DetectGloveBones(bpy.types.Operator):
    bl_idname = "rsl.detect_glove_bones"
    bl_label = "Auto Detect"
    bl_description = "Automatically detect glove bones for supported naming schemes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object

        for bone_name_key in animation_lists.glove_bones.keys():
            bone_names = detection_manager.get_bone_list()[bone_name_key]
            for bone in obj.pose.bones:
                bone_name = detection_manager.standardize_bone_name(bone.name)
                if bone_name in bone_names:
                    setattr(obj, 'rsl_glove_' + bone_name_key, bone.name)

        return {'FINISHED'}
