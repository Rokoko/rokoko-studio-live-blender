import bpy
from ..core import animations, animation_lists
from ..operators.detector import DetectFaceShapes


# Create a panel in the Object category of all objects
class ObjectsPanel(bpy.types.Panel):
    bl_label = "Rokoko Studio Live"
    bl_idname = "OBJECT_PT_rsl_objects"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if obj.type == 'ARMATURE':
            self.draw_actor(context, layout)

        elif obj.type == 'MESH':
            self.draw_tracker(context, layout)
            self.draw_face(context, layout)

        else:
            self.draw_tracker(context, layout)

    @staticmethod
    def draw_tracker(context, layout):
        # Adding this to refresh the UI when hovered over this
        # Useful because starting the receiver doesn't update the up automatically
        row = layout.row(align=True)
        row.scale_y = 0.2
        row.prop(context.scene, 'rsl_ui_refresher', text=' ', toggle=True, emboss=False)

        row = layout.row(align=True)
        row.label(text='Attach to tracker or prop:')

        if not animations.trackers and not animations.props:
            row = layout.row(align=True)
            row.label(text='No prop or tracker data available.', icon='INFO')
            return

        row = layout.row(align=True)
        row.prop(context.object, 'rsl_animations_props_trackers')

    @staticmethod
    def draw_actor(context, layout):
        row = layout.row(align=True)
        row.scale_y = 0.2
        row.prop(context.scene, 'rsl_ui_refresher', text=' ', toggle=True, emboss=False)

        row = layout.row(align=True)
        row.label(text='Attach to actor:')

        if not animations.actors:
            row = layout.row(align=True)
            row.label(text='No actor data available.', icon='INFO')
            return

        row = layout.row(align=True)
        row.prop(context.object, 'rsl_animations_actors')

    @staticmethod
    def draw_face(context, layout):
        obj = context.object

        row = layout.row(align=True)
        row.scale_y = 0.2
        row.prop(context.scene, 'rsl_ui_refresher', text=' ', toggle=True, emboss=False)

        layout.separator()

        row = layout.row(align=True)
        row.label(text='Attach to face:')

        if not animations.faces:
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
            row.operator(DetectFaceShapes.bl_idname)

            if not hasattr(obj.data, 'shape_keys') or not hasattr(obj.data.shape_keys, 'key_blocks'):
                row = layout.row(align=True)
                row.label(text='This mesh has no shapekeys!', icon='INFO')
                return

            for shape in animation_lists.face_shapes:
                row = layout.row(align=True)
                row.prop_search(obj, 'rsl_face_' + shape, obj.data.shape_keys, "key_blocks", text=shape)
