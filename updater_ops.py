import bpy

from . import updater


class CheckForUpdateButton(bpy.types.Operator):
    bl_idname = 'rsl_updater.check_for_update'
    bl_label = 'Check now for Update'
    bl_description = 'Checks if a new update is available for Rokoko Studio Live'
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return not updater.is_checking_for_update

    def execute(self, context):
        updater.used_updater_panel = True
        updater.check_for_update_background()
        return {'FINISHED'}


class UpdateToLatestButton(bpy.types.Operator):
    bl_idname = 'rsl_updater.update_latest'
    bl_label = 'Update Now'
    bl_description = 'Updates Rokoko Studio Live to the latest compatible version'
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return updater.update_needed

    def execute(self, context):
        updater.confirm_update_to = 'latest'
        updater.used_updater_panel = True

        bpy.ops.rsl_updater.confirm_update_panel('INVOKE_DEFAULT')
        return {'FINISHED'}


class UpdateToSelectedButton(bpy.types.Operator):
    bl_idname = 'rsl_updater.update_selected'
    bl_label = 'Update to Selected version'
    bl_description = 'Updates Rokoko Studio Live to the selected version'
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if updater.is_checking_for_update or not updater.version_list:
            return False
        return True

    def execute(self, context):
        updater.confirm_update_to = context.scene.rsl_updater_version_list
        updater.used_updater_panel = True

        bpy.ops.rsl_updater.confirm_update_panel('INVOKE_DEFAULT')
        return {'FINISHED'}


class UpdateToBetaButton(bpy.types.Operator):
    bl_idname = 'rsl_updater.update_beta'
    bl_label = 'Update to Beta version'
    bl_description = 'Updates Rokoko Studio Live to the Beta version'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        updater.confirm_update_to = 'beta'
        updater.used_updater_panel = True

        bpy.ops.rsl_updater.confirm_update_panel('INVOKE_DEFAULT')
        return {'FINISHED'}


class RemindMeLaterButton(bpy.types.Operator):
    bl_idname = 'rsl_updater.remind_me_later'
    bl_label = 'Remind me later'
    bl_description = 'This hides the update notification til the next Blender restart'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        updater.remind_me_later = True
        self.report({'INFO'}, 'You will be reminded later')
        return {'FINISHED'}


class IgnoreThisVersionButton(bpy.types.Operator):
    bl_idname = 'rsl_updater.ignore_this_version'
    bl_label = 'Ignore this version'
    bl_description = 'Ignores this version. You will be reminded again when the next version releases'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        updater.set_ignored_version()
        self.report({'INFO'}, 'Version ' + updater.latest_version_str + ' will be ignored.')
        return {'FINISHED'}


class ShowPatchnotesPanel(bpy.types.Operator):
    bl_idname = 'rsl_updater.show_patchnotes'
    bl_label = 'Patchnotes'
    bl_description = 'Shows the patchnotes of the selected version'
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if updater.is_checking_for_update or not updater.version_list:
            return False
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        updater.used_updater_panel = True
        dpi_value = updater.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * 8.3))

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.prop(context.scene, 'rsl_updater_version_list')

        if context.scene.rsl_updater_version_list:
            version = updater.get_version_by_string(context.scene.rsl_updater_version_list)

            col.separator()
            row = col.row(align=True)
            row.label(text=version.name, icon='SOLO_ON')

            col.separator()
            for line in version.patch_notes.replace('**', '').split('\r\n'):
                if line.startswith("["):
                    continue
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text=line)

            col.separator()
            row = col.row(align=True)
            row.label(text='Released: ' + version.release_date)

        col.separator()


class ConfirmUpdatePanel(bpy.types.Operator):
    bl_idname = 'rsl_updater.confirm_update_panel'
    bl_label = 'Confirm Update'
    bl_description = 'This shows you a panel in which you have to confirm your update choice'
    bl_options = {'INTERNAL'}

    show_patchnotes = False

    def execute(self, context):
        print('UPDATE TO ' + updater.confirm_update_to)
        if updater.confirm_update_to == 'beta':
            updater.update_now(beta=True)
        elif updater.confirm_update_to == 'latest':
            updater.update_now(latest=True)
        else:
            updater.update_now(version=updater.confirm_update_to)
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = updater.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * 4.2))

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        version_str = updater.confirm_update_to
        if updater.confirm_update_to == 'latest':
            version_str = updater.latest_version_str
        elif updater.confirm_update_to == 'beta':
            version_str = 'Beta'

        col.separator()
        row = col.row(align=True)
        row.label(text='Version: ' + version_str)

        if updater.confirm_update_to == 'beta':
            col.separator()
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text='Warning:')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=' The beta version might be unstable, some features')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=' might not work correctly, or it might only be')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=' compatible with the latest Blender version.')
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=' Check the Rokoko Github repo for more details.')

        else:
            row.operator(ShowPatchnotesPanel.bl_idname, text='Show Patchnotes')

        col.separator()
        col.separator()
        row = col.row(align=True)
        row.scale_y = 0.65
        row.label(text='Update now:', icon='URL')


class UpdateCompletePanel(bpy.types.Operator):
    bl_idname = 'rsl_updater.update_complete_panel'
    bl_label = 'Installation Report'
    bl_description = 'The update if now complete'
    bl_options = {'INTERNAL'}

    show_patchnotes = False

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = updater.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * 4.2))

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        if updater.update_finished:
            row = col.row(align=True)
            row.scale_y = 0.9
            row.label(text='Rokoko Studio Live was successfully updated.', icon='FILE_TICK')

            row = col.row(align=True)
            row.scale_y = 0.9
            row.label(text='Restart Blender to complete the update.', icon='BLANK1')
        else:
            row = col.row(align=True)
            row.scale_y = 0.9
            row.label(text='Update failed.', icon='CANCEL')

            row = col.row(align=True)
            row.scale_y = 0.9
            row.label(text='See Updater Panel for more info.', icon='BLANK1')


class UpdateNotificationPopup(bpy.types.Operator):
    bl_idname = 'rsl_updater.update_notification_popup'
    bl_label = 'Update available'
    bl_description = 'This shows you that an update is available'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        action = context.scene.rsl_update_action
        if action == 'UPDATE':
            updater.update_now(latest=True)
        elif action == 'IGNORE':
            updater.set_ignored_version()
        else:
            # Remind later aka defer
            updater.remind_me_later = True
        updater.ui_refresh()
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = updater.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * 4.7))

    # def invoke(self, context, event):
    #     return context.window_manager.invoke_props_dialog(self)

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.split(factor=0.55, align=True)
        row.scale_y = 1.05
        row.label(text='Rokoko Studio Live v' + updater.latest_version_str + ' available!', icon='SOLO_ON')
        row.operator(ShowPatchnotesPanel.bl_idname, text='Show Patchnotes')

        col.separator()
        col.separator()
        col.separator()
        row = col.row(align=True)
        row.prop(context.scene, 'rsl_update_action', expand=True)


def draw_update_notification_panel(layout):
    if not updater.update_needed or updater.remind_me_later or updater.is_ignored_version:
        return

    col = layout.column(align=True)

    if updater.update_finished:
        col.separator()
        row = col.row(align=True)
        row.label(text='Restart Blender to complete update!', icon='ERROR')
        col.separator()
        return

    row = col.row(align=True)
    row.scale_y = 0.75
    row.label(text='Update v' + updater.latest_version_str + ' available!', icon='SOLO_ON')

    col.separator()
    row = col.row(align=True)
    row.scale_y = 1.3
    row.operator(UpdateToLatestButton.bl_idname, text='Update Now')

    row = col.row(align=True)
    row.scale_y = 1
    row.operator(RemindMeLaterButton.bl_idname, text='Defer')
    row.operator(IgnoreThisVersionButton.bl_idname, text='Ignore')

    col.separator()
    col.separator()
    col.separator()


def draw_updater_panel(context, layout, user_preferences=False):
    col = layout.column(align=True)

    scale_big = 2
    scale_small = 1.2

    if user_preferences:
        row = col.row(align=True)
        row.scale_y = 0.8
        row.label(text='Rokoko Studio Live Updater:', icon='URL')
        col.separator()

    if updater.update_finished:
        col.separator()
        row = col.row(align=True)
        row.scale_y = 0.75
        row.label(text='Restart Blender to', icon='ERROR')
        row = col.row(align=True)
        row.scale_y = 0.75
        row.label(text='complete the update!', icon='BLANK1')
        col.separator()
        return

    # If the plugin didn't load correctly, don't show the current version
    if "error" in updater.current_version_str:
        row = col.row(align=True)
        row.scale_y = 0.85
        row.label(text="Failed to load the plugin. Try updating to latest or beta version:", icon='ERROR')
        col.separator()

    if updater.show_error:
        errors = updater.show_error.split('\n')
        for i, error in enumerate(errors):
            row = col.row(align=True)
            row.scale_y = 0.85
            row.label(text=error, icon='ERROR' if i == 0 else 'BLANK1')
        col.separator()

    if updater.is_checking_for_update:
        if not updater.used_updater_panel:
            row = col.row(align=True)
            row.scale_y = scale_big
            row.operator(CheckForUpdateButton.bl_idname, text='Checking..')
        else:
            split = col.row(align=True)
            row = split.row(align=True)
            row.scale_y = scale_big
            row.operator(CheckForUpdateButton.bl_idname, text='Checking..')
            row = split.row(align=True)
            row.alignment = 'RIGHT'
            row.scale_y = scale_big
            row.operator(CheckForUpdateButton.bl_idname, text="", icon='FILE_REFRESH')

    elif updater.update_needed:
        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = scale_big
        row.operator(UpdateToLatestButton.bl_idname, text='Update now to ' + updater.latest_version_str)
        row = split.row(align=True)
        row.alignment = 'RIGHT'
        row.scale_y = scale_big
        row.operator(CheckForUpdateButton.bl_idname, text="", icon='FILE_REFRESH')

    elif not updater.used_updater_panel or not updater.version_list:
        row = col.row(align=True)
        row.scale_y = scale_big
        row.operator(CheckForUpdateButton.bl_idname, text='Check now for Update')

    else:
        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = scale_big
        row.operator(UpdateToLatestButton.bl_idname, text='Up to Date!')
        row = split.row(align=True)
        row.alignment = 'RIGHT'
        row.scale_y = scale_big
        row.operator(CheckForUpdateButton.bl_idname, text="", icon='FILE_REFRESH')

    col.separator()
    col.separator()
    split = col.row(align=True)
    row = split.split(factor=0.3, align=True)
    row.scale_y = scale_small
    row.active = True if not updater.is_checking_for_update and updater.version_list else False
    row.label(text='Version:')
    row.prop(context.scene, 'rsl_updater_version_list', text='')
    row = split.row(align=True)
    row.scale_y = scale_small
    row.operator(ShowPatchnotesPanel.bl_idname, text="", icon='WORDWRAP_ON')

    row = col.row(align=True)
    row.scale_y = scale_small
    row.active = True if not updater.is_checking_for_update and updater.version_list else False
    selected_version_compatible = updater.is_version_compatible(context.scene.rsl_updater_version_list)
    row.operator(UpdateToSelectedButton.bl_idname, text='Install Selected Version' if selected_version_compatible else 'Force Install Selected Version')

    row = col.row(align=True)
    row.scale_y = scale_small
    row.operator(UpdateToBetaButton.bl_idname, text='Install Beta Version')

    # If version is default, don't show the current version
    if "error" in updater.current_version_str:
        return

    col.separator()
    row = col.row(align=True)
    row.scale_y = 0.65
    row.label(text='Add-on version: ' + updater.current_version_str)

    # Show compatibility info
    blender_version = ".".join(str(x) for x in bpy.app.version)
    row = col.row(align=True)
    row.scale_y = 0.65
    row.label(text='Blender version: ' + blender_version)

    # Check if there are any compatible versions available
    if updater.version_list:
        compatible_versions = [v for v in updater.version_list if updater.is_version_compatible(v.version_string)]
        if not compatible_versions:
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text='No compatible versions found', icon='ERROR')
            row = col.row(align=True)
            row.scale_y = 0.65
            row.label(text='for this Blender version', icon='BLANK1')


# demo bare-bones preferences
class DemoPreferences(bpy.types.AddonPreferences):
    bl_idname = updater.package_name

    def draw(self, context):
        layout = self.layout
        draw_updater_panel(context, layout, user_preferences=True)


to_register = [
    CheckForUpdateButton,
    UpdateToLatestButton,
    UpdateToSelectedButton,
    UpdateToBetaButton,
    RemindMeLaterButton,
    IgnoreThisVersionButton,
    ShowPatchnotesPanel,
    ConfirmUpdatePanel,
    UpdateCompletePanel,
    UpdateNotificationPopup,
    DemoPreferences,
]


registered = False


def register():
    global registered
    if registered:
        return

    # Set initial version
    current_version = []
    for i in (1, 0, 0):
        current_version.append(str(i))
        updater.current_version.append(i)

    # Set current version string and add beta tag and increase version number
    updater.current_version_str = '.'.join(current_version)
    current_version[2] = str(int(current_version[2]) + 1)
    updater.current_version_str = '.'.join(current_version) + ".error"

    bpy.types.Scene.rsl_updater_version_list = bpy.props.EnumProperty(
        name='Version',
        description='Select the version you want to install\n',
        items=updater.get_version_list
    )
    bpy.types.Scene.rsl_update_action = bpy.props.EnumProperty(
        name="Choose action",
        description="Action",
        items=[
            ("UPDATE", "Update Now", "Updates now to the latest version"),
            ("IGNORE", "Ignore this version", "This ignores this version. You will be reminded again when the next version releases"),
            ("DEFER", "Remind me later", "Hides the update notification til the next Blender restart")
        ]
    )

    # Register all Updater classes
    count = 0
    for cls in to_register:
        try:
            bpy.utils.register_class(cls)
            count += 1
        except ValueError:
            pass
    # print('Registered', count, 'Rokoko Studio Live updater classes.')
    if count < len(to_register):
        print('Skipped', len(to_register) - count, 'Rokoko Studio Live updater classes.')

    # Delete and rename files that didn't get deleted during the update process
    updater.delete_and_rename_files_on_startup()

    print("LOADED UPDATER!")
    registered = True


def update_info(bl_info, beta_branch):
    # If not beta branch, always disable fake updates and no version checks!
    if not beta_branch:
        updater.fake_update = False
        updater.no_ver_check = False

    # Set current version
    current_version = []
    updater.current_version = []
    for i in bl_info['version']:
        current_version.append(str(i))
        updater.current_version.append(i)

    # Set current version string (and add beta tag and increase version number if true)
    updater.current_version_str = '.'.join(current_version)
    if beta_branch:
        current_version[2] = str(int(current_version[2]) + 1)
        updater.current_version_str = '.'.join(current_version) + ".beta"


def unregister():
    global registered
    registered = False

    # Unregister all Updater classes
    for cls in reversed(to_register):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError as e:
            print(f"Error unregistering {cls.__name__}: {e}")

    if hasattr(bpy.types.Scene, 'rsl_updater_version_list'):
        del bpy.types.Scene.rsl_updater_version_list
