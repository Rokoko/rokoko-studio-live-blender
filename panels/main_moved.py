import bpy

from .main import ReceiverPanel, ToolPanel


# Create a panel in the Object category of all objects
class RokokoPanel(bpy.types.Panel):
    bl_label = "Rokoko Studio Live"
    bl_idname = "PT_rsl_main_v0"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.label(text='TEST!')

        ReceiverPanel.draw(self, context)


class RokokoSubPanel(RokokoPanel):
    bl_parent_id = "PT_rokoko_main"
    bl_label = "Panel 1"

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is the main panel.")





class HelloWorldPanel:
    bl_category = "Tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"


class HELLO_PT_World1(HelloWorldPanel, bpy.types.Panel):
    bl_idname = "PT_rokoko_main"
    bl_label = "Rokoko"

    def draw(self, context):
        pass


class HELLO_PT_World2(HelloWorldPanel, bpy.types.Panel):
    bl_parent_id = "PT_rokoko_main"
    bl_label = "Panel 2"

    def draw(self, context):
        layout = self.layout
        layout.label(text="First Sub Panel of Panel 1.")


class HELLO_PT_World3(HelloWorldPanel, bpy.types.Panel):
    bl_parent_id = "PT_rokoko_main"
    bl_label = "Panel 3"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Second Sub Panel of Panel 1.")


# class HELLO_PT_World3(ToolPanel, bpy.types.Panel):
#     # bl_idname = 'VIEW3D_PT_rsl_retargeting_v2'
#     bl_parent_id = "PT_rokoko_main"
#     bl_label = 'Retargeting'
#     bl_options = {'DEFAULT_CLOSED'}
#
#     def draw(self, context):
#         layout = self.layout
#         layout.label(text="First Sub Panel of Panel 1.")