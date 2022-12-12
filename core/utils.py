
import os
import sys
import bpy
import math
import json
import pathlib
import asyncio
from mathutils import Vector, Matrix
from contextlib import suppress

main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
resources_dir = os.path.join(main_dir, "resources")


def ui_refresh_properties():
    # Refreshes the properties panel
    for windowManager in bpy.data.window_managers:
        for window in windowManager.windows:
            for area in window.screen.areas:
                if area.type == 'PROPERTIES':
                    area.tag_redraw()


def ui_refresh_view_3d():
    # Refreshes the view 3D panel
    for windowManager in bpy.data.window_managers:
        for window in windowManager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()


def ui_refresh_all():
    if not hasattr(bpy.data, "window_managers"):
        return
    # Refreshes all panels
    for windowManager in bpy.data.window_managers:
        for window in windowManager.windows:
            for area in window.screen.areas:
                area.tag_redraw()


def reprint(*x):
    # This prints a message in the same console line continuously
    sys.stdout.write("\r" + " ".join(x))
    sys.stdout.flush()


def set_active(obj, select=False, deselect_others=False):
    if deselect_others:
        bpy.ops.object.select_all(action='DESELECT')
    if select:
        set_select(obj, True)

    bpy.context.view_layer.objects.active = obj


def get_active():
    return bpy.context.view_layer.objects.active


def set_hide(obj, hide):
    # obj.hide_viewport = hide
    obj.hide_set(hide)


def set_select(obj, select):
    obj.select_set(select)


def mat3_to_vec_roll(mat):
    vecmat = vec_roll_to_mat3(mat.col[1], 0)
    vecmatinv = vecmat.inverted()
    rollmat = vecmatinv @ mat
    roll = math.atan2(rollmat[0][2], rollmat[2][2])
    return roll


def vec_roll_to_mat3(vec, roll):
    target = Vector((0, 0.1, 0))
    nor = vec.normalized()
    axis = target.cross(nor)
    if axis.dot(axis) > 0.0000000001:
        axis.normalize()
        theta = target.angle(nor)
        bMatrix = Matrix.Rotation(theta, 3, axis)
    else:
        updown = 1 if target.dot(nor) > 0 else -1
        bMatrix = Matrix.Scale(updown, 3)
        bMatrix[2][2] = 1.0

    rMatrix = Matrix.Rotation(roll, 3, nor)
    mat = rMatrix @ bMatrix
    return mat


async def cancel_gen(agen):
    """
    Stops an asynchronous generator from outside.
    :param agen: The asynchronous generator
    :return:
    """
    task = asyncio.create_task(agen.__anext__())
    task.cancel()
    with suppress(Exception):
        await task
    await agen.aclose()


def add_armature(edit=False):
    objs_tmp = [obj for obj in bpy.data.objects]
    bpy.ops.object.armature_add(location=[0.0, 0.0, 0.0], enter_editmode=edit)
    return [obj for obj in bpy.data.objects if obj not in objs_tmp][0]


def print_armature_data(armature_name):
    # For dev purpose only
    armature_tmp = bpy.data.objects.get(armature_name)
    set_active(armature_tmp, select=True, deselect_others=True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    from . import detection_manager

    data = []
    for bone in armature_tmp.pose.bones:
        bone_data = {
            "name": bone.name,
            "position_head": [bone.head[0], bone.head[1], bone.head[2]],
            "position_tail": [bone.tail[0], bone.tail[1], bone.tail[2]],
            "parent": bone.parent.name if bone.parent else None,
        }
        data.append(bone_data)

    print(json.dumps(data, indent=4))

    raise Exception("Printed all bones")


def load_default_armature():
    json_file_path = os.path.join(resources_dir, "armature_default.json")
    with open(json_file_path, "r") as f:
        data = json.load(f)
    return data
