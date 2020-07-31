import bpy
import time
import addon_utils

from threading import Thread

if bpy.app.version < (2, 83, 17):
    from io_scene_fbx import import_fbx
    from io_scene_fbx.import_fbx import blen_read_animations_curves_iter, blen_read_object_transform_do


def start_fbx_patch_timer():
    if bpy.app.version >= (2, 83, 17):  # This patch is officially accepted in Blender 2.83.17, so don't patch it
        return

    # Asynchronously start the timer looking for the right time to patch the fbx importer
    thread = Thread(target=time_fbx_patch, args=[])
    thread.start()


def time_fbx_patch():
    # Wait for Blender to finish loading up
    found_scene = False
    while not found_scene:
        if hasattr(bpy.context, 'scene'):
            found_scene = True
        else:
            time.sleep(0.5)

    # Enable fbx if it isn't enabled yet
    fbx_is_enabled = addon_utils.check('io_scene_fbx')[1]
    if not fbx_is_enabled:
        addon_utils.enable('io_scene_fbx')

    # Patch fbx importer
    patch_fbx_importer()


def patch_fbx_importer():
    import_fbx.blen_read_animations_action_item = blen_read_animations_action_item_patched


# This is the modified Blender function that will replace the original one
def blen_read_animations_action_item_patched(action, item, cnodes, fps, anim_offset):
    """
    'Bake' loc/rot/scale into the action,
    taking any pre_ and post_ matrix into account to transform from fbx into blender space.
    """
    from bpy.types import Object, PoseBone, ShapeKey, Material, Camera
    from itertools import chain

    fbx_curves = []
    for curves, fbxprop in cnodes.values():
        for (fbx_acdata, _blen_data), channel in curves.values():
            fbx_curves.append((fbxprop, channel, fbx_acdata))

    # Leave if no curves are attached (if a blender curve is attached to scale but without keys it defaults to 0).
    if len(fbx_curves) == 0:
        return

    blen_curves = []
    props = []
    keyframes = {}

    # Add each keyframe to the keyframe dict
    def store_keyframe(fc, frame, value):
        fc_key = (fc.data_path, fc.array_index)
        if not keyframes.get(fc_key):
            keyframes[fc_key] = []
        keyframes[fc_key].append((frame, value))

    if isinstance(item, Material):
        grpname = item.name
        props = [("diffuse_color", 3, grpname or "Diffuse Color")]
    elif isinstance(item, ShapeKey):
        props = [(item.path_from_id("value"), 1, "Key")]
    elif isinstance(item, Camera):
        props = [(item.path_from_id("lens"), 1, "Camera")]
    else:  # Object or PoseBone:
        if item.is_bone:
            bl_obj = item.bl_obj.pose.bones[item.bl_bone]
        else:
            bl_obj = item.bl_obj

        # We want to create actions for objects, but for bones we 'reuse' armatures' actions!
        grpname = item.bl_obj.name

        # Since we might get other channels animated in the end, due to all FBX transform magic,
        # we need to add curves for whole loc/rot/scale in any case.
        props = [(bl_obj.path_from_id("location"), 3, grpname or "Location"),
                 None,
                 (bl_obj.path_from_id("scale"), 3, grpname or "Scale")]
        rot_mode = bl_obj.rotation_mode
        if rot_mode == 'QUATERNION':
            props[1] = (bl_obj.path_from_id("rotation_quaternion"), 4, grpname or "Quaternion Rotation")
        elif rot_mode == 'AXIS_ANGLE':
            props[1] = (bl_obj.path_from_id("rotation_axis_angle"), 4, grpname or "Axis Angle Rotation")
        else:  # Euler
            props[1] = (bl_obj.path_from_id("rotation_euler"), 3, grpname or "Euler Rotation")

    blen_curves = [action.fcurves.new(prop, index=channel, action_group=grpname)
                   for prop, nbr_channels, grpname in props for channel in range(nbr_channels)]

    if isinstance(item, Material):
        for frame, values in blen_read_animations_curves_iter(fbx_curves, anim_offset, 0, fps):
            value = [0,0,0]
            for v, (fbxprop, channel, _fbx_acdata) in values:
                assert(fbxprop == b'DiffuseColor')
                assert(channel in {0, 1, 2})
                value[channel] = v

            for fc, v in zip(blen_curves, value):
                store_keyframe(fc, frame, v)

    elif isinstance(item, ShapeKey):
        for frame, values in blen_read_animations_curves_iter(fbx_curves, anim_offset, 0, fps):
            value = 0.0
            for v, (fbxprop, channel, _fbx_acdata) in values:
                assert(fbxprop == b'DeformPercent')
                assert(channel == 0)
                value = v / 100.0

            for fc, v in zip(blen_curves, (value,)):
                store_keyframe(fc, frame, v)

    elif isinstance(item, Camera):
        for frame, values in blen_read_animations_curves_iter(fbx_curves, anim_offset, 0, fps):
            value = 0.0
            for v, (fbxprop, channel, _fbx_acdata) in values:
                assert(fbxprop == b'FocalLength')
                assert(channel == 0)
                value = v

            for fc, v in zip(blen_curves, (value,)):
                store_keyframe(fc, frame, v)

    else:  # Object or PoseBone:
        if item.is_bone:
            bl_obj = item.bl_obj.pose.bones[item.bl_bone]
        else:
            bl_obj = item.bl_obj

        transform_data = item.fbx_transform_data
        rot_eul_prev = bl_obj.rotation_euler.copy()
        rot_quat_prev = bl_obj.rotation_quaternion.copy()

        # Pre-compute inverted local rest matrix of the bone, if relevant.
        restmat_inv = item.get_bind_matrix().inverted_safe() if item.is_bone else None

        # Create a dict to store all keyframes in order to add them later all at once
        keyframes = {}

        for frame, values in blen_read_animations_curves_iter(fbx_curves, anim_offset, 0, fps):
            for v, (fbxprop, channel, _fbx_acdata) in values:
                if fbxprop == b'Lcl Translation':
                    transform_data.loc[channel] = v
                elif fbxprop == b'Lcl Rotation':
                    transform_data.rot[channel] = v
                elif fbxprop == b'Lcl Scaling':
                    transform_data.sca[channel] = v
            mat, _, _ = blen_read_object_transform_do(transform_data)

            # compensate for changes in the local matrix during processing
            if item.anim_compensation_matrix:
                mat = mat @ item.anim_compensation_matrix

            # apply pre- and post matrix
            # post-matrix will contain any correction for lights, camera and bone orientation
            # pre-matrix will contain any correction for a parent's correction matrix or the global matrix
            if item.pre_matrix:
                mat = item.pre_matrix @ mat
            if item.post_matrix:
                mat = mat @ item.post_matrix

            # And now, remove that rest pose matrix from current mat (also in parent space).
            if restmat_inv:
                mat = restmat_inv @ mat

            # Now we have a virtual matrix of transform from AnimCurves, we can insert keyframes!
            loc, rot, sca = mat.decompose()
            if rot_mode == 'QUATERNION':
                if rot_quat_prev.dot(rot) < 0.0:
                    rot = -rot
                rot_quat_prev = rot
            elif rot_mode == 'AXIS_ANGLE':
                vec, ang = rot.to_axis_angle()
                rot = ang, vec.x, vec.y, vec.z
            else:  # Euler
                rot = rot.to_euler(rot_mode, rot_eul_prev)
                rot_eul_prev = rot

            # Add each keyframe and its value to the keyframe dict
            for fc, value in zip(blen_curves, chain(loc, rot, sca)):
                store_keyframe(fc, frame, value)

    # Add all keyframe points to the fcurves at once and modify them after
    for fc_key, key_values in keyframes.items():
        data_path, index = fc_key

        # Add all keyframe points at once
        fcurve = action.fcurves.find(data_path=data_path, index=index)
        num_keys = len(key_values)
        fcurve.keyframe_points.add(num_keys)

        # Apply values to each keyframe point
        for kf_point, v in zip(fcurve.keyframe_points, key_values):
            kf_point.co = v
            kf_point.interpolation = 'LINEAR'

    # Since we inserted our keyframes in 'FAST' mode, we have to update the fcurves now.
    for fc in blen_curves:
        fc.update()
