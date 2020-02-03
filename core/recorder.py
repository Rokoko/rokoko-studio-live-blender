import bpy
import copy

recorded_data = {}


def toggle_recording(self, context):
    new_state = context.scene.rsl_recording

    if new_state:
        start_recorder(context)
    else:
        stop_recorder(context)


def start_recorder(context):
    if recorded_data:
        return
    pass


def stop_recorder(context):
    if not recorded_data:
        return

    # Set animation settings
    context.scene.render.fps = context.scene.rsl_receiver_fps

    found = False
    animation_counter = 1
    action_name_prefix = 'Rokoko Anim '

    while not found:
        is_new_number = True
        for a in bpy.data.actions:
            if a.name.startswith(action_name_prefix + str(animation_counter)):
                is_new_number = False
                break
        if is_new_number:
            found = True
        else:
            animation_counter += 1

    action_name_prefix = 'Rokoko Anim ' + str(animation_counter) + ': '

    def get_frame(frame_number):
        return int(round((timestamps[frame_number] - timestamps[0]) * context.scene.rsl_receiver_fps, 0))

    def get_corrected_frame_number(frame_index):
        # Fix frames numbers that are incorrect because of rounding errors
        curr_frame = get_frame(frame_index)
        if 0 < frame_index < len(timestamps) - 1:
            prev_frame = get_frame(frame_index - 1)
            next_frame = get_frame(frame_index + 1)
            if prev_frame == curr_frame and next == curr_frame + 2:
                curr_frame += 1
            if next_frame == curr_frame and prev_frame == curr_frame - 2:
                curr_frame -= 1
        if frame_index == len(timestamps) - 1:
            prev_frame = get_frame(frame_index - 1)
            if prev_frame == curr_frame:
                curr_frame += 1
        return curr_frame

    def add_keyframe(action_tmp, data_path, data_index, group_name, frame_value):
        if not action_tmp:
            print('NO ACTION!')
            return
        fc = action_tmp.fcurves.find(data_path=data_path, index=data_index)
        if not fc:
            fc = action_tmp.fcurves.new(data_path=data_path, index=data_index, action_group=group_name)
            if index != 0:
                fc.keyframe_points.add(1)
                fc.keyframe_points[-1].interpolation = 'LINEAR'
                fc.keyframe_points[-1].co = (0, frame_value)
        fc.keyframe_points.add(1)
        fc.keyframe_points[-1].interpolation = 'CONSTANT'
        fc.keyframe_points[-1].co = (frame, frame_value)

    index = -1
    timestamps = list(recorded_data.keys())
    for data in recorded_data.values():
        index += 1
        frame = get_corrected_frame_number(index)
        # print('Frame', frame, get_frame(index), (timestamp - timestamps[0]) * context.scene.rsl_receiver_fps)

        objects = data.get('objects')
        faces = data.get('faces')
        actors = data.get('actors')

        if actors:
            for arm_name, bones in actors.items():
                armature = context.scene.objects.get(arm_name)
                if not armature:
                    continue

                # Create new action in which the recorded animation will be stored and assign the action to the armature
                action = bpy.data.actions.get(action_name_prefix + 'Armature ' + arm_name)
                if not action:
                    action = bpy.data.actions.new(name=action_name_prefix + 'Armature ' + arm_name)
                    action.use_fake_user = True
                    armature.animation_data_create().action = action

                for bone_name, bone_data in bones.items():
                    bone = armature.pose.bones.get(bone_name)
                    if not bone:
                        continue

                    location = bone_data['location']
                    rotation = bone_data['rotation']
                    location_path = 'pose.bones["%s"].location' % bone_name
                    rotation_path = 'pose.bones["%s"].rotation_quaternion' % bone_name
                    inherit_rotation_path = 'data.bones["%s"].use_inherit_rotation' % bone_name

                    # Add location
                    if location:
                        for i in range(3):
                            add_keyframe(action, location_path, i, arm_name, location[i])

                    # Add rotation
                    for i in range(4):
                        add_keyframe(action, rotation_path, i, arm_name, rotation[i])

                    # Add inherit rotation
                    add_keyframe(action, inherit_rotation_path, 0, arm_name, False)

        if faces:
            for mesh_name, shapekeys in faces.items():
                mesh = context.scene.objects.get(mesh_name)
                if not mesh or not hasattr(mesh.data, 'shape_keys') or not hasattr(mesh.data.shape_keys, 'key_blocks'):
                    continue

                # Create new action in which the recorded animation will be stored and assign the action to the mesh
                action = bpy.data.actions.get(action_name_prefix + 'Mesh ' + mesh_name)
                if not action:
                    action = bpy.data.actions.new(name=action_name_prefix + 'Mesh ' + mesh_name)
                    mesh.animation_data_create().action = action

                for shapekey_name, value in shapekeys.items():
                    shapekey = mesh.data.shape_keys.key_blocks.get(shapekey_name)
                    if not shapekey:
                        continue

                    value_path = 'data.shape_keys.key_blocks["%s"].value' % shapekey_name

                    # Add value
                    add_keyframe(action, value_path, 0, mesh_name, value)

        if objects:
            for obj_name, obj_data in objects.items():
                obj = context.scene.objects.get(obj_name)
                if not obj:
                    continue

                # Create new action in which the recorded animation will be stored and assign the action to the object
                action = bpy.data.actions.get(action_name_prefix + 'Obj ' + obj_name)
                if not action:
                    action = bpy.data.actions.new(name=action_name_prefix + 'Obj ' + obj_name)
                    obj.animation_data_create().action = action

                location = obj_data['location']
                rotation = obj_data['rotation']
                location_path = 'location'
                rotation_path = 'rotation_quaternion'

                # Add location
                for i in range(3):
                    add_keyframe(action, location_path, i, obj_name, location[i])

                # Add rotation
                for i in range(4):
                    add_keyframe(action, rotation_path, i, obj_name, rotation[i])

    # Clear recorded data
    recorded_data.clear()


def record_bone(timestamp, arm_name, bone_name, rotation, location=None):
    if not recorded_data.get(timestamp):
        recorded_data[timestamp] = {
            'objects': {},
            'faces': {},
            'actors': {}
        }
    if not recorded_data[timestamp]['actors'].get(arm_name):
        recorded_data[timestamp]['actors'][arm_name] = {}

    recorded_data[timestamp]['actors'][arm_name][bone_name] = copy.deepcopy({
        'rotation': rotation,
        'location': location
    })


def record_face(timestamp, mesh_name, shapekey_name, value):
    if not recorded_data.get(timestamp):
        recorded_data[timestamp] = {
            'objects': {},
            'faces': {},
            'actors': {}
        }
    if not recorded_data[timestamp]['faces'].get(mesh_name):
        recorded_data[timestamp]['faces'][mesh_name] = {}

    recorded_data[timestamp]['faces'][mesh_name][shapekey_name] = copy.deepcopy(value)


def record_object(timestamp, obj_name, rotation, location):
    if not recorded_data.get(timestamp):
        recorded_data[timestamp] = {
            'objects': {},
            'faces': {},
            'actors': {}
        }
    if not recorded_data[timestamp]['objects'].get(obj_name):
        recorded_data[timestamp]['objects'][obj_name] = copy.deepcopy({
            'rotation': rotation,
            'location': location
        })
