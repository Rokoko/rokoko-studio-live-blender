import bpy
from . import animation_lists

# version = None
# timestamp = None
# playbacktimestamp = None
props = []
trackers = []
faces = []
actors = []


def clear_animations():
    global props, trackers, faces, actors
    props = []
    trackers = []
    faces = []
    actors = []


def animate():
    for obj in bpy.data.objects:
        if obj.rsl_animations_props_trackers and obj.rsl_animations_props_trackers != 'None':
            obj_id = obj.rsl_animations_props_trackers.split('|')
            if obj_id[0] == 'PR':
                prop = [prop for prop in props if prop['id'] == obj_id[1]]

                # print('PROP', obj.name, obj_id, prop)

                if not prop:
                    return

                obj.rotation_mode = 'QUATERNION'
                obj.location = pos_studio_to_blender(
                    prop[0]['position']['x'],
                    prop[0]['position']['y'],
                    prop[0]['position']['z'],
                )
                obj.rotation_quaternion = rot_studio_to_blender(
                    prop[0]['rotation']['w'],
                    prop[0]['rotation']['x'],
                    prop[0]['rotation']['y'],
                    prop[0]['rotation']['z'],
                )

            elif obj_id[0] == 'TR':
                tracker = [tracker for tracker in trackers if tracker['name'] == obj_id[1]]

                # print('TRACKER', obj.name, obj_id)

                if not tracker:
                    return

                obj.rotation_mode = 'QUATERNION'
                obj.location = pos_studio_to_blender(
                    tracker[0]['position']['x'],
                    tracker[0]['position']['y'],
                    tracker[0]['position']['z'],
                )
                obj.rotation_quaternion = rot_studio_to_blender(
                    tracker[0]['rotation']['w'],
                    tracker[0]['rotation']['x'],
                    tracker[0]['rotation']['y'],
                    tracker[0]['rotation']['z'],
                )

        if obj.type == 'MESH':
            mesh = bpy.data.meshes[obj.name]
            if not hasattr(obj.data, 'shape_keys') or not hasattr(obj.data.shape_keys, 'key_blocks'):
                continue
            if not obj.rsl_animations_faces or obj.rsl_animations_faces == 'None':
                continue

            face = [face for face in faces if face['faceId'] == obj.rsl_animations_faces]

            if not face:
                return

            for shape in animation_lists.face_shapes:
                obj.data.shape_keys.key_blocks[getattr(mesh, 'rsl_face_' + shape)].slider_min = -1
                obj.data.shape_keys.key_blocks[getattr(mesh, 'rsl_face_' + shape)].value = face[0][shape] / 100


def pos_studio_to_blender(x, y, z):
    return -x, -z, y


def rot_studio_to_blender(w, x, y, z):
    return w, x, z, -y
