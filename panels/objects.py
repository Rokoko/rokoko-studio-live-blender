import bpy

from ..core import animations, animation_lists
from ..operators.actor import InitTPose, ResetTPose
from ..operators import detector


# Create a panel in the Object category of all objects
class ObjectsPanel(bpy.types.Panel):
    bl_label = "Rokoko Studio Live Setup"
    bl_idname = "OBJECT_PT_rsl_objects_v2"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        self.draw_tracker(context, layout)

        if obj.type == 'MESH':
            self.draw_face(context, layout)

        elif obj.type == 'ARMATURE':
            self.draw_actor(context, layout)

    @staticmethod
    def draw_tracker(context, layout):
        obj = context.object

        props_string = 'Prop or Tracker' if animations.live_data.version <= 2 else 'prop'

        row = layout.row(align=True)
        row.label(text=f'Attach to {props_string}:')

        if not animations.live_data.trackers and not animations.live_data.props:
            row = layout.row(align=True)
            row.label(text=f'No {props_string.lower()} data available.', icon='INFO')
            return

        row = layout.row(align=True)
        row.prop(context.object, 'rsl_animations_props_trackers')

        if obj.rsl_animations_props_trackers and obj.rsl_animations_props_trackers != 'None':
            row = layout.row(align=True)
            row.prop(context.object, 'rsl_use_custom_scale')
            if obj.rsl_use_custom_scale:
                row.prop(context.object, 'rsl_custom_scene_scale', text='')

    @staticmethod
    def draw_face(context, layout):
        obj = context.object

        layout.separator()

        row = layout.row(align=True)
        row.label(text='Attach to Face:')

        if not animations.live_data.faces:
            row = layout.row(align=True)
            row.label(text='No face data available.', icon='INFO')
            row = layout.row(align=True)
            row.scale_y = 0.1
            return

        row = layout.row(align=True)
        row.prop(obj, 'rsl_animations_faces')

        if obj.rsl_animations_faces and obj.rsl_animations_faces != 'None':
            layout.separator()
            row = layout.row(align=True)
            row.label(text='Select Shapekeys:')
            row.operator(detector.DetectFaceShapes.bl_idname)

            if not hasattr(obj.data, 'shape_keys') or not hasattr(obj.data.shape_keys, 'key_blocks'):
                row = layout.row(align=True)
                row.label(text='This mesh has no shapekeys!', icon='INFO')
                return

            draw_import_export(layout, shapes=True)

            for shape in animation_lists.face_shapes:
                row = layout.row(align=True)
                row.prop_search(obj, 'rsl_face_' + shape, obj.data.shape_keys, "key_blocks", text=shape)

    @staticmethod
    def draw_actor(context, layout):
        obj = context.object

        layout.separator()

        row = layout.row(align=True)
        row.label(text='Attach to Actor:')

        if not animations.live_data.actors:
            row = layout.row(align=True)
            row.label(text='No actor data available.', icon='INFO')
        else:
            row = layout.row(align=True)
            row.prop(context.object, 'rsl_animations_actors')

        if obj.rsl_animations_actors and obj.rsl_animations_actors != 'None':
            layout.separator()

            split = layout.row(align=True)
            row = split.split(factor=0.16, align=True)
            row.label(text='Bones:')
            row.operator(detector.DetectActorBones.bl_idname)
            row.operator(InitTPose.bl_idname)
            row.operator(ResetTPose.bl_idname)

            # if obj.rsl_animations_actors and obj.rsl_animations_actors != 'None':
            if not obj.get('CUSTOM') or not obj.get('CUSTOM').get('rsl_tpose_bones'):
                row = layout.row(align=True)
                row.label(text='T-Pose is not set yet!', icon='ERROR')

            draw_import_export(layout)

            col = layout.column()
            show_gloves = True
            for actor_bone in animation_lists.actor_bones.keys():
                if not show_gloves:
                    continue

                split = col.row(align=True)
                row = split.split(factor=0.32, align=True)
                row.label(text=actor_bone + ':')
                row.prop_search(obj, 'rsl_actor_' + actor_bone, obj.pose, "bones", text='')

                # Make a split after right toe to separate hands
                if actor_bone == 'rightToe':
                    if not animations.live_data.has_gloves(animations.live_data.get_actor_by_obj(obj)):  # Stop showing glove bones if they are not supported by the JSON version
                        show_gloves = False
                        continue
                    col.separator()
                    row = col.row(align=True)
                    row.label(text='Gloves:', icon='VIEW_PAN')

                if actor_bone == 'leftLittleDistal':
                    col.separator()


def draw_import_export(layout, shapes=False):
    layout.separator()

    row = layout.row(align=True)
    row.label(text='Custom Naming Schemes:')
    if shapes:
        row.operator(detector.SaveCustomShapes.bl_idname, text='Save Current Naming Scheme')
    else:
        row.operator(detector.SaveCustomBones.bl_idname, text='Save Current Naming Scheme')

    subrow = layout.row(align=True)
    row = subrow.row(align=True)
    row.scale_y = 0.9
    row.operator(detector.ImportCustomBones.bl_idname, text='Import')
    row.operator(detector.ExportCustomBones.bl_idname, text='Export')
    row = subrow.row(align=True)
    row.scale_y = 0.9
    row.alignment = 'RIGHT'
    if shapes:
        row.operator(detector.ClearCustomShapes.bl_idname, text='', icon='X')
    else:
        row.operator(detector.ClearCustomBones.bl_idname, text='', icon='X')

    layout.separator()