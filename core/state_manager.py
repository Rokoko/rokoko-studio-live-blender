import bpy
import copy

from . import utils
from ..operators import receiver

objects = {}
faces = {}
armatures = {}

hidden_meshes = {}


def save_scene():
    for obj in bpy.context.scene.objects:
        save_object(obj)
        if obj.type == 'MESH':
            save_face(obj)
        elif obj.type == 'ARMATURE':
            save_armature(obj)


def load_scene():
    for obj in bpy.context.scene.objects:
        load_object(obj)
        if obj.type == 'MESH':
            load_face(obj)
        elif obj.type == 'ARMATURE':
            load_armature(obj)

    hidden_meshes.clear()


# Object handler
def save_object(obj):
    if obj.rsl_animations_props_trackers == 'None':
        return

    global objects
    rotation_mode = obj.rotation_mode
    obj.rotation_mode = 'QUATERNION'
    objects[obj.name] = copy.deepcopy({
        'location': obj.location,
        'rotation': obj.rotation_quaternion,
        'rotation_mode': rotation_mode,
        # 'hidden': obj.hide_get()
    })


def load_object(obj):
    if not bpy.context.scene.rsl_reset_scene_on_stop:
        return

    global objects

    obj_data = objects.get(obj.name)
    if not obj_data:
        return

    obj.rotation_mode = 'QUATERNION'
    obj.location = obj_data['location']
    obj.rotation_quaternion = obj_data['rotation']
    # obj.rotation_mode = obj_data['rotation_mode']
    # obj.hide_set(obj_data['hidden'])

    # Remove element from dictionary
    objects.pop(obj.name)


# Face mesh handler
def save_face(obj):
    if not hasattr(obj.data, 'shape_keys') or not hasattr(obj.data.shape_keys, 'key_blocks'):
        return
    if obj.rsl_animations_faces == 'None':
        return

    global faces
    shapekeys = {}

    for shapekey in obj.data.shape_keys.key_blocks:
        shapekeys[shapekey.name] = shapekey.value

    faces[obj.name] = copy.deepcopy(shapekeys)

    if obj.name in hidden_meshes.keys():
        unhide_mesh(obj, hidden_meshes[obj.name])


def load_face(obj):
    if not bpy.context.scene.rsl_reset_scene_on_stop:
        return

    global faces
    shapekey_data = faces.get(obj.name)
    if not shapekey_data or not hasattr(obj.data, 'shape_keys') or not hasattr(obj.data.shape_keys, 'key_blocks'):
        return

    for shapekey_name, value in shapekey_data.items():
        shapekey = obj.data.shape_keys.key_blocks.get(shapekey_name)
        if not shapekey:
            continue

        shapekey.value = value

    # Remove element from dictionary
    faces.pop(obj.name)

    # Hide this mesh if it is animated by an armature and it should be hidden
    if bpy.context.scene.rsl_hide_mesh_during_play:
        for mod in obj.modifiers:
            if mod.type == 'ARMATURE':
                armature = mod.object
                if armatures.get(armature.name):
                    hide_mesh(obj, armature)


# Armature handler
def save_armature(obj):
    global armatures

    # Return if no actor and no glove is assigned to this armature
    # if not obj.rsl_animations_actors or obj.rsl_animations_actors == 'None':  # <-- This should work but for some reason it doesn't
    if obj.rsl_animations_actors == 'None':
        print('NO ASSIGNED DATA:', obj.rsl_animations_actors)
        return

    utils.set_active(obj)
    bpy.ops.object.mode_set(mode='OBJECT')

    bones = {}

    for bone in obj.pose.bones:
        # Fix rotation mode
        if bone.rotation_mode == 'QUATERNION':
            bone.rotation_mode = 'XYZ'

        bones[bone.name] = {
            'location': bone.location,
            'rotation': bone.rotation_euler,
            'rotation_mode': bone.rotation_mode,
            'inherit_rotation': obj.data.bones.get(bone.name).use_inherit_rotation
        }

    armatures[obj.name] = copy.deepcopy(bones)

    hide_meshes_on_play(obj)


def load_armature(obj):
    unhide_meshes_on_stop(obj)

    if not bpy.context.scene.rsl_reset_scene_on_stop:
        return

    global armatures
    bone_data = armatures.get(obj.name)
    if not bone_data:
        return

    for bone_name, bone_data in bone_data.items():
        bone = obj.pose.bones.get(bone_name)
        if not bone:
            continue

        location = bone_data['location']
        rotation = bone_data['rotation']
        rotation_mode = bone_data['rotation_mode']
        inherit_rotation = bone_data['inherit_rotation']

        # Fix rotation mode
        if rotation_mode == 'QUATERNION':
            rotation_mode = 'XYZ'

        bone.location = location
        bone.rotation_mode = rotation_mode
        bone.rotation_euler = rotation
        obj.data.bones.get(bone_name).use_inherit_rotation = inherit_rotation

    # Remove element from dictionary
    armatures.pop(obj.name)


def update_object(self, context):
    if not receiver.receiver_enabled:
        return

    obj = context.object
    new_state = obj.rsl_animations_props_trackers

    if new_state != 'None':
        if not objects.get(obj.name):
            save_object(obj)
    else:
        load_object(obj)


def update_face(self, context):
    if not receiver.receiver_enabled:
        return

    obj = context.object
    new_state = obj.rsl_animations_faces

    if new_state != 'None':
        if not faces.get(obj.name):
            save_face(obj)
    else:
        load_face(obj)


def update_actor(self, context):
    if not receiver.receiver_enabled:
        return

    obj = context.object
    new_state = obj.rsl_animations_actors

    if new_state != 'None':
        if not armatures.get(obj.name):
            save_armature(obj)
    else:
        load_armature(obj)


def update_glove(self, context):
    if not receiver.receiver_enabled:
        return

    obj = context.object
    new_state = obj.rsl_animations_gloves

    if new_state != 'None':
        if not armatures.get(obj.name):
            save_armature(obj)
    else:
        load_armature(obj)


def hide_meshes_on_play(armature):
    if not bpy.context.scene.rsl_hide_mesh_during_play:
        return

    global faces
    for mesh in bpy.context.scene.objects:
        if mesh.type != 'MESH':
            continue

        hide_mesh(mesh, armature)


def unhide_meshes_on_stop(armature):
    for mesh_name in copy.copy(hidden_meshes).keys():
        mesh = bpy.context.scene.objects.get(mesh_name)
        if not mesh:
            continue
        unhide_mesh(mesh, armature)


def update_hidden_meshes(self, context):
    if not receiver.receiver_enabled:
        return

    new_state = context.scene.rsl_hide_mesh_during_play

    for armature_name in armatures.keys():
        armature = bpy.context.scene.objects.get(armature_name)
        if not armature:
            continue

        if new_state:
            hide_meshes_on_play(armature)
        else:
            unhide_meshes_on_stop(armature)


def hide_mesh(mesh, armature):
    if faces.get(mesh.name):
        return

    for mod in mesh.modifiers:
        if mod.type == 'ARMATURE' and mod.object == armature:
            mesh.hide_set(True)
            mod.object = None
            hidden_meshes[mesh.name] = armature


def unhide_mesh(mesh, armature):
    mesh.hide_set(False)

    for mod in mesh.modifiers:
        if mod.type == 'ARMATURE' and hidden_meshes[mesh.name] == armature:
            mod.object = hidden_meshes[mesh.name]
            hidden_meshes.pop(mesh.name)
