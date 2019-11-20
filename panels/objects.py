import bpy


# Create a panel in the Object category of all objects
class ObjectsPanel(bpy.types.Panel):
    bl_label = "Smartsuit Pro Panel"
    bl_idname = "OBJECT_PT_ssp_objects"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if obj.type == 'ARMATURE':
            self.draw_actor(context, layout)

        elif obj.type == 'MESH':
            self.draw_face(context, layout)

        else:
            self.draw_tracker(context, layout)

    @staticmethod
    def draw_tracker(context, layout):
        row = layout.row(align=True)
        row.label(text='Attach to tracker or prop:')

        row = layout.row(align=True)
        row.prop(context.object, 'ssp_animations_props_trackers')

    @staticmethod
    def draw_actor(context, layout):
        row = layout.row(align=True)
        row.label(text='Attach to actor:')

        row = layout.row(align=True)
        row.prop(context.object, 'ssp_animations_actors')

    @staticmethod
    def draw_face(context, layout):
        row = layout.row(align=True)
        row.label(text='Attach to face:')

        row = layout.row(align=True)
        row.prop(context.object, 'ssp_animations_faces')


