import bpy
import webbrowser


class ForumButton(bpy.types.Operator):
    bl_idname = 'rsl.info_forum'
    bl_label = 'Join our Forums'
    bl_description = 'Opens the Rokoko forums in the browser'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open('https://rokoko.freshdesk.com/support/discussions')
        self.report({'INFO'}, 'Opened forums')
        return {'FINISHED'}