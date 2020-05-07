import bpy

from .main import ToolPanel
from ..operators import retargeting
from ..core.icon_manager import Icons

from bpy.types import PropertyGroup, UIList
from bpy.props import StringProperty


# Retargeting panel
class RetargetingPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rsl_retargeting_v00'
    bl_label = 'Retargeting'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False

        row = layout.row(align=True)
        row.label(text='Select the armatures:')

        row = layout.split(factor=0.26, align=True)
        row.label(text='Source:')
        row.prop(context.scene, 'rsl_retargeting_armature_source', text='')

        row = layout.split(factor=0.26, align=True)
        row.label(text='Target:')
        row.prop(context.scene, 'rsl_retargeting_armature_target', text='')

        if context.scene.rsl_retargeting_armature_source == 'None' \
                or context.scene.rsl_retargeting_armature_source == '' \
                or context.scene.rsl_retargeting_armature_target == 'None' \
                or context.scene.rsl_retargeting_armature_target == '':
            return

        if not context.scene.rsl_retargeting_bone_list:
            row = layout.row(align=True)
            row.scale_y = 1.2
            row.operator(retargeting.BuildBoneList.bl_idname, icon_value=Icons.CALIBRATE.get_icon())
            return

        subrow = layout.row(align=True)
        row = subrow.row(align=True)
        row.scale_y = 1.2
        row.operator(retargeting.BuildBoneList.bl_idname, text='Rebuild Bone List', icon_value=Icons.CALIBRATE.get_icon())
        row = subrow.row(align=True)
        row.scale_y = 1.2
        row.alignment = 'RIGHT'
        row.operator(retargeting.ClearBoneList.bl_idname, text="", icon='X')

        layout.separator()

        row = layout.row(align=True)
        row.template_list("RSL_UL_BoneList", "Bone List", context.scene, "rsl_retargeting_bone_list", context.scene, "rsl_retargeting_bone_list_index", rows=1, maxrows=10)

        row = layout.row(align=True)
        row.scale_y = 1.4
        row.operator(retargeting.RetargetAnimation.bl_idname, icon_value=Icons.CALIBRATE.get_icon())


class BoneListItem(PropertyGroup):
    """Properties of the bone list items"""
    bone_name_source: StringProperty(
        name="Source Bone",
        description="The source bone name",
        default="Undefined")

    bone_name_target: StringProperty(
        name="Target Bone",
        description="The target bone name",
        default="")


class RSL_UL_BoneList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = bpy.data.objects.get(context.scene.rsl_retargeting_armature_target)

        layout = layout.split(factor=0.36, align=True)
        layout.label(text=item.bone_name_source)
        layout.prop_search(item, 'bone_name_target', obj.pose, "bones", text='')
