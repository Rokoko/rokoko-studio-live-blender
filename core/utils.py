import asyncio
from typing import Any

import bpy
import math
import sys

from bpy_extras import anim_utils
from contextlib import suppress
from mathutils import Vector, Matrix


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


def set_active(obj):
    obj.select_set(True)
    obj.hide_set(False)
    bpy.context.view_layer.objects.active = obj


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


def get_fcurves_from_action(action: bpy.types.Action, slot_identifier: int = 0) -> list[Any]:
    """Returns all F-curves in the action that match the slot identifier.
    :param action: The action to search in
    :param slot_identifier: The slot identifier to search for. Only needed for Blender 5.0.0 and newer.
    :return: A list of F-curves that match the slot identifier
    """
    if hasattr(action, 'fcurves'):
        fcurves = action.fcurves
    else:  # Blender 5.0.0 and newer
        action_slot = action.slots[slot_identifier]  # TODO: Add UI selection for action slot. Currently only uses the first slot.
        channelbag: bpy.types.ActionChannelbag = anim_utils.action_get_channelbag_for_slot(action, action_slot)
        fcurves = channelbag.fcurves if channelbag else []
    return fcurves


def create_fcurve_in_action(action: bpy.types.Action, data_path: str, array_index: int = -1, slot_identifier: int = 0, action_group: str = "") -> bpy.types.FCurve:
    """Creates a new F-curve in the action with the given data path and array index.
    :param action: The action to create the F-curve in
    :param data_path: The data path of the F-curve
    :param array_index: The array index of the F-curve
    :param slot_identifier: The slot identifier to create the F-curve in. Only needed for Blender 5.0.0 and newer.
    :param action_group: The action group to assign the F-curve to. Only needed for Blender 5.0.0 and newer.
    :return: The created F-curve
    """
    if hasattr(action, 'fcurves'):
        fcurves = action.fcurves
        fcurve = fcurves.new(data_path=data_path, index=array_index, action_group=action_group)
    else:  # Blender 5.0.0 and newer
        action_slot = action.slots[slot_identifier]  # TODO: Add UI selection for action slot. Currently only uses the first slot.
        channelbag: bpy.types.ActionChannelbag = anim_utils.action_get_channelbag_for_slot(action, action_slot)
        if channelbag is None:
            channelbag = action.channels.new(name=f"Channelbag_{slot_identifier}")
        fcurve = channelbag.fcurves.ensure(data_path, index=array_index, group_name=action_group)

    return fcurve
