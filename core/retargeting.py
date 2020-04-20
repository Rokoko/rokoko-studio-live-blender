import bpy


# Creates the list of armatures for the retargeting panel
def get_armatures_source(self, context):
    choices = [('None', '-None-', 'None')]

    for arm in bpy.data.objects:
        if arm.type != 'ARMATURE' or not arm.animation_data:
            continue

        # 1. Will be returned by context.scene
        # 2. Will be shown in lists
        # 3. will be shown in the hover description (below description)
        choices.append((arm.name, arm.name, arm.name))

    return choices


# Creates the list of armatures for the retargeting panel
def get_armatures_target(self, context):
    choices = [('None', '-None-', 'None')]

    for arm in bpy.data.objects:
        if arm.type != 'ARMATURE' or arm.name == context.scene.rsl_retargeting_armature_source:
            continue

        # 1. Will be returned by context.scene
        # 2. Will be shown in lists
        # 3. will be shown in the hover description (below description)
        choices.append((arm.name, arm.name, arm.name))

    return choices


# If the retargeting armatures get changed, clear the bone list
def clear_bone_list(self, context):
    context.scene.rsl_retargeting_bone_list.clear()

