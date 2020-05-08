import bpy


# This filters the objects shown to only include armatures and under certain conditions
def poll_source_armatures(self, obj):
    return obj.type == 'ARMATURE' and obj.animation_data and obj.animation_data.action


def poll_target_armatures(self, obj):
    return obj.type == 'ARMATURE' and obj != get_source_armature()


# If the retargeting armatures get changed, clear the bone list
def clear_bone_list(self, context):
    context.scene.rsl_retargeting_bone_list.clear()


def get_source_armature():
    return bpy.context.scene.rsl_retargeting_armature_source


def get_target_armature():
    return bpy.context.scene.rsl_retargeting_armature_target