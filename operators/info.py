import bpy
import webbrowser


class LicenseButton(bpy.types.Operator):
    bl_idname = 'rsl.info_license'
    bl_label = 'License'
    bl_description = 'Opens the license in the browser'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open('https://github.com/RokokoElectronics/rokoko-studio-live-blender/blob/master/LICENSE.md')
        self.report({'INFO'}, 'Opened license.')
        return {'FINISHED'}


class RokokoButton(bpy.types.Operator):
    bl_idname = 'rsl.info_rokoko'
    bl_label = 'Website'
    bl_description = 'Opens the Rokoko website in the browser'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open('https://www.rokoko.com/en')
        self.report({'INFO'}, 'Opened Rokoko website.')
        return {'FINISHED'}


class DocumentationButton(bpy.types.Operator):
    bl_idname = 'rsl.info_documentation'
    bl_label = 'Documentation'
    bl_description = 'Opens the documentation in the browser'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open('https://rokoko.freshdesk.com/support/solutions/folders/47000761699')
        self.report({'INFO'}, 'Opened documentation.')
        return {'FINISHED'}


class ForumButton(bpy.types.Operator):
    bl_idname = 'rsl.info_forum'
    bl_label = 'Join our Forums'
    bl_description = 'Opens the Rokoko Blender forum in the browser'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open('https://rokoko.freshdesk.com/support/discussions/forums/47000399880')
        self.report({'INFO'}, 'Opened forums.')
        return {'FINISHED'}
