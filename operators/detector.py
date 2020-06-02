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

        for shape_name_key in animation_lists.face_shapes:
            setattr(obj, 'rsl_face_' + shape_name_key, detection_manager.detect_shape(obj, shape_name_key))

        return {'FINISHED'}


class DetectActorBones(bpy.types.Operator):
    bl_idname = "rsl.detect_actor_bones"
    bl_label = "Auto Detect"
    bl_description = "Automatically detect actor bones for supported naming schemes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object

        for bone_name_key in animation_lists.actor_bones.keys():
            setattr(obj, 'rsl_actor_' + bone_name_key, detection_manager.detect_bone(obj, bone_name_key))

        return {'FINISHED'}


class SaveCustomShapes(bpy.types.Operator):
    bl_idname = "rsl.save_custom_shapes"
    bl_label = "Save Custom Shapes"
    bl_description = "This saves the currently selected shapekeys and they will then get automatically detected"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        obj = context.object

        # Go over all face shapekeys and see if the user changed the detected shapekey. If yes, save that new shapekey
        for shape_name_key in animation_lists.face_shapes:
            shape_name_selected = getattr(obj, 'rsl_face_' + shape_name_key)
            if not shape_name_selected:
                continue  # TODO idea: maybe save these unselected choices as well

            shape_name_detected = detection_manager.detect_shape(obj, shape_name_key)

            if shape_name_detected == shape_name_selected:  # This means that the user changed nothing, so don't save this
                continue

            detection_manager.save_live_data_shape_to_list(shape_name_key, shape_name_selected, shape_name_detected)

        # At the end save all custom shapes to the file
        detection_manager.save_to_file_and_update()

        return {'FINISHED'}


class SaveCustomBones(bpy.types.Operator):
    bl_idname = "rsl.save_custom_bones"
    bl_label = "Save Custom Bones"
    bl_description = "This saves the currently selected bones and they will then get automatically detected"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        obj = context.object

        # Go over all actor bones and see if the user changed the detected bone. If yes, save that new bone
        for bone_name_key in animation_lists.actor_bones.keys():
            bone_name_selected = getattr(obj, 'rsl_actor_' + bone_name_key)
            if not bone_name_selected:
                continue  # TODO idea: maybe save these unselected choices as well

            bone_name_detected = detection_manager.detect_bone(obj, bone_name_key)

            if bone_name_detected == bone_name_selected:  # This means that the user changed nothing, so don't save this
                continue

            detection_manager.save_live_data_bone_to_list(bone_name_key, bone_name_selected, bone_name_detected)

        # At the end save all custom bones to the file
        detection_manager.save_to_file_and_update()

        return {'FINISHED'}


class SaveCustomBonesRetargeting(bpy.types.Operator):
    bl_idname = "rsl.save_custom_bones_retargeting"
    bl_label = "Save Custom Bones"
    bl_description = "This saves the currently selected bones and they will then get automatically detected"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        # Save the bone list if the user changed anything
        detection_manager.save_retargeting_to_list()

        return {'FINISHED'}


class ImportCustomBones(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "rsl.import_custom_schemes"
    bl_label = "Import Custom Scheme"
    bl_description = "Import a custom naming scheme"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})
    directory: bpy.props.StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})
    filter_glob: bpy.props.StringProperty(default='*.json;', options={'HIDDEN'})

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
    bl_idname = "rsl.export_custom_schemes"
    bl_label = "Export Custom Scheme"
    bl_description = "Export your custom naming schemes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default='*.json;', options={'HIDDEN'})

    def execute(self, context):
        file_name = detection_manager.export_custom_list(self.filepath)

        if not file_name:
            self.report({'ERROR'}, 'You don\'t have any custom naming schemes!')
            return {'FINISHED'}

        self.report({'INFO'}, 'Exported custom naming schemes as "' + file_name + '".')
        return {'FINISHED'}


class ClearCustomBones(bpy.types.Operator):
    bl_idname = "rsl.clear_custom_bones"
    bl_label = "Clear Custom Bones"
    bl_description = "Clear all custom bone naming schemes"
    bl_options = {'INTERNAL'}

    def draw(self, context):
        layout = self.layout

        layout.separator()

        row = layout.row(align=True)
        row.scale_y = 0.5
        row.label(text='You are about to delete all stored custom bone naming schemes.', icon='ERROR')

        row = layout.row(align=True)
        row.scale_y = 0.5
        row.label(text='Continue?', icon='BLANK1')

        layout.separator()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def execute(self, context):
        detection_manager.delete_custom_bone_list()

        self.report({'INFO'}, 'Cleared all custom bone naming schemes!')
        return {'FINISHED'}


class ClearCustomShapes(bpy.types.Operator):
    bl_idname = "rsl.clear_custom_shapes"
    bl_label = "Clear Custom Shapekeys"
    bl_description = "Clear all custom shape naming schemes"
    bl_options = {'INTERNAL'}

    def draw(self, context):
        layout = self.layout

        layout.separator()

        row = layout.row(align=True)
        row.scale_y = 0.5
        row.label(text='You are about to delete all stored custom shape naming schemes.', icon='ERROR')

        row = layout.row(align=True)
        row.scale_y = 0.5
        row.label(text='Continue?', icon='BLANK1')

        layout.separator()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def execute(self, context):
        detection_manager.delete_custom_shape_list()

        self.report({'INFO'}, 'Cleared all custom shape naming schemes!')
        return {'FINISHED'}
