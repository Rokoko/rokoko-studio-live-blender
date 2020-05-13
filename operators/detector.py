import os
import bpy
import bpy_extras

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


class ImportCustomBones(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "rsl.import_custom_bones"
    bl_label = "Import Custom Bones"
    bl_description = "Import a custom bone naming scheme"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    files = bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})
    directory = bpy.props.StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})
    filter_glob = bpy.props.StringProperty(default='*.json;', options={'HIDDEN'})

    def execute(self, context):
        import_count = 0
        if self.directory:
            for f in self.files:
                file_name = f.name
                if not file_name.endswith('.json'):
                    continue
                detection_manager.import_custom_list(self.directory, file_name)
                import_count += 1

        # If this operator is called with no directory but a filepath argument, import that
        elif self.filepath:
            detection_manager.import_custom_list(os.path.dirname(self.filepath), os.path.basename(self.filepath))
            import_count += 1

        detection_manager.save_to_file_and_update()

        if not import_count:
            self.report({'ERROR'}, 'No files were imported.')
            return {'FINISHED'}

        self.report({'INFO'}, 'Successfully imported new naming schemes.')
        return {'FINISHED'}


class ExportCustomBones(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "rsl.export_custom_bones"
    bl_label = "Export Custom Bones"
    bl_description = "Export your custom bones naming schemes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    filename_ext = ".json"
    filter_glob = bpy.props.StringProperty(default='*.json;', options={'HIDDEN'})

    def execute(self, context):
        file_name = detection_manager.export_custom_list(self.filepath)

        self.report({'INFO'}, 'Exported custom naming schemes as "' + file_name + '".')
        return {'FINISHED'}


class ClearCustomBones(bpy.types.Operator):
    bl_idname = "rsl.clear_custom_bones"
    bl_label = "Clear Custom Bones"
    bl_description = "Clear all custom bones naming schemes"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        # file_name = detection_manager.export_custom_list(self.directory)
        file_name = detection_manager.export_custom_list(self.filepath)

        self.report({'INFO'}, 'Cleared all custom bone naming schemes!')
        return {'FINISHED'}
