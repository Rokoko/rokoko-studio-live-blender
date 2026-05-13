
import asyncio
import bpy
import math
import pathlib
import sys

from bpy_extras import anim_utils
from contextlib import suppress
from mathutils import Vector, Matrix
from typing import Any


MAIN_DIR = pathlib.Path(__file__).parent.parent
RECOURSES_DIR = MAIN_DIR / "resources"
MODELS_DIR = RECOURSES_DIR / "models"
NEWTON_BLEND_FILE = MODELS_DIR / "Newton Static.blend"


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
    # Blender 4.5 and older (Legacy)
    if hasattr(action, 'fcurves'):
        # Note: In 5.0, action.fcurves is removed. hasattr check ensures backward compatibility.
        fcurves = action.fcurves
        fcurve = fcurves.new(data_path=data_path, index=array_index, action_group=action_group)

    # Blender 5.0+ (Slotted Actions)
    else:
        # 1. Ensure a slot exists
        if not action.slots:
            action.slots.new(name="Slot_0", id_type="OBJECT")

        # 2. Get the Slot Object
        try:
            action_slot = action.slots[slot_identifier]
        except IndexError:
            # Fallback if the requested identifier doesn't exist
            action_slot = action.slots.new(name=f"Slot_{slot_identifier}", id_type="OBJECT")

        # 3. Ensure the Channelbag exists
        channelbag = anim_utils.action_ensure_channelbag_for_slot(action, action_slot)

        # 4. Ensure/Create the F-Curve
        # Note: 'group_name' is the 5.0 parameter for 'action_group'
        fcurve = channelbag.fcurves.ensure(data_path, index=array_index, group_name=action_group)

    return fcurve


def import_blend_file(path: pathlib.Path, link: bool, name: str = None, import_types: list = None, link_scene: str = None):
    if import_types is None:
        import_types = ["collections"]

    # Create new collection and link it to the specified scene
    collection_blend = bpy.data.collections.new(name if name else path.stem)
    main_collection = bpy.context.scene.collection
    if link_scene:
        main_collection = find_layer_collection(name=link_scene).collection
    main_collection.children.link(collection_blend)

    # Create a list of all objects before the import
    objs_before_import = [obj for obj in bpy.data.objects]

    # Load and append the collections from the blend file
    # link=True means that the objects remain in the other blend file and
    # are only linked to this one. This is much faster than copying the data.
    with bpy.data.libraries.load(str(path), link=link) as (data_from, data_to):
        for type_name in import_types:
            for data in getattr(data_from, type_name):
                getattr(data_to, type_name).append(data)

    # Link the collections to their blend collection
    for collection in bpy.data.collections:
        if collection.users < 1:
            collection_blend.children.link(collection)

    # Get all objects that were imported compared to the objects that existed beforehand
    imported_objs = [obj for obj in bpy.data.objects if obj not in objs_before_import]
    root_objs = [obj for obj in imported_objs if not obj.parent]

    if len(root_objs) == 1:
        parent = root_objs[0]
    else:
        # Create a parent for all imported objects
        parent = bpy.data.objects.new(path.stem, None)
        collection_blend.objects.link(parent)

        # Set the parent and link it to the blend collection
        for obj in imported_objs:
            if not obj.parent:
                obj.parent = parent

    # Set the parent object as active
    set_active(parent)

    # Set the main collection as active
    bpy.context.view_layer.active_layer_collection = find_layer_collection(collection_blend.name)

    # Delete all collection in the parent collection
    for collection in collection_blend.children_recursive:
        for obj in collection.objects:
            collection_blend.objects.link(obj)
            collection.objects.unlink(obj)
        bpy.data.collections.remove(collection, do_unlink=True)

    return imported_objs


def find_layer_collection(name: str, parent_layer_collection=None) -> bpy.types.LayerCollection | None:
    """ Recursively traverse layer_collection for a particular name """
    if parent_layer_collection is None:
        parent_layer_collection = bpy.context.view_layer.layer_collection

    if parent_layer_collection.name == name:
        return parent_layer_collection

    for layer in parent_layer_collection.children:
        found = find_layer_collection(name, layer)
        if found:
            return found
    return None
