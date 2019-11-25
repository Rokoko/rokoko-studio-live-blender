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
        # Animate all trackers and props
        if props or trackers:
            if obj.rsl_animations_props_trackers and obj.rsl_animations_props_trackers != 'None':
                obj_id = obj.rsl_animations_props_trackers.split('|')

                if obj_id[0] == 'PR':
                    prop = [prop for prop in props if prop['id'] == obj_id[1]]
                    if prop:
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
                    if tracker:
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

        # Animate all faces
        if faces and obj.type == 'MESH':
            if not hasattr(obj.data, 'shape_keys') or not hasattr(obj.data.shape_keys, 'key_blocks'):
                continue
            if not obj.rsl_animations_faces or obj.rsl_animations_faces == 'None':
                continue

            face = [face for face in faces if face['faceId'] == obj.rsl_animations_faces]
            if not face:
                continue

            for shape in animation_lists.face_shapes:
                if obj.data.shape_keys.key_blocks.get(getattr(obj, 'rsl_face_' + shape)):
                    obj.data.shape_keys.key_blocks[getattr(obj, 'rsl_face_' + shape)].slider_min = -1
                    obj.data.shape_keys.key_blocks[getattr(obj, 'rsl_face_' + shape)].value = face[0][shape] / 100

        # Animate all actors
        elif actors and obj.type == 'ARMATURE' and obj.mode == 'POSE':
            if not obj.rsl_animations_actors or obj.rsl_animations_actors == 'None':
                continue

            actor = [actor for actor in actors if actor['id'] == obj.rsl_animations_actors]
            if not actor:
                continue

            for bone_name in animation_lists.actor_bones:
                bone = obj.pose.bones.get(getattr(obj, 'rsl_actor_' + bone_name))
                if bone:
                    bone.rotation_mode = 'QUATERNION'
                    # bone.location = (
                    #     actor[0][bone_name]['position']['x'],
                    #     actor[0][bone_name]['position']['y'],
                    #     actor[0][bone_name]['position']['z'],
                    # )
                    bone.rotation_quaternion = (
                        actor[0][bone_name]['rotation']['w'],
                        -actor[0][bone_name]['rotation']['x'],
                        actor[0][bone_name]['rotation']['y'],
                        actor[0][bone_name]['rotation']['z'],
                    )


def pos_studio_to_blender(x, y, z):
    return -x, -z, y


def rot_studio_to_blender(w, x, y, z):
    return w, x, z, -y
