import bpy
import webbrowser

from ..core import login_manager as lm


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
        webbrowser.open('https://github.com/Rokoko/rokoko-studio-live-blender#readme')
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


class ToggleRokokoIDButton(bpy.types.Operator):
    bl_idname = 'rsl.toggle_rokoko_id'
    bl_label = 'Toggle Rokoko ID'
    bl_description = 'Toggles the visibility of your Rokoko ID'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        lm.user.display_email = not lm.user.display_email
        return {'FINISHED'}
