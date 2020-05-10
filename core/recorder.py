import bpy
import copy

from collections import OrderedDict

recorded_data = {}
recorded_timestamps = OrderedDict()


def toggle_recording(self, context):
    new_state = context.scene.rsl_recording

    if new_state:
        start_recorder(context)
    else:
        stop_recorder(context)


def start_recorder(context):
    if recorded_data:
        return
    # Here can be stuff done when starting the recorder
    pass


def stop_recorder(context):
    if not recorded_data:
        return

    # Set animation settings
    context.scene.render.fps = context.scene.rsl_receiver_fps

    # Convert timestamps to keyframes to have a shared time axis
    convert_timestamps_to_keyframes()

    # Process each type of recorded data
    for data_type, objects in recorded_data.items():
        if not objects:
            continue

        if data_type == 'actors':
            for obj_name, data in objects.items():
                process_actor_recording(obj_name, data)

        elif data_type == 'faces':
            for obj_name, data in objects.items():
                process_face_recording(obj_name, data)

        elif data_type == 'objects':
            for obj_name, data in objects.items():
                process_object_recording(obj_name, data)

    # Clear recorded data
    recorded_data.clear()
    recorded_timestamps.clear()

    print('\nSuccessfully saved the recording!')


def process_actor_recording(obj_name, data):
    armature = bpy.data.objects.get(obj_name)
    if not armature:
        print('Armature', obj_name, 'not found!')
        return

    # Create new action
    action = bpy.data.actions.new(name='Anim Arm ' + obj_name)
    action.use_fake_user = True
    armature.animation_data_create().action = action

    # Handle recording data
    data_paths = OrderedDict()
    for item in data:
        if item['location']:
            data_path = 'pose.bones["%s"].location' % item['bone_name']
            if not data_paths.get(data_path):
                data_paths[data_path] = []
            data_paths[data_path].append((item['timestamp'], item['location']))

        if item['rotation']:
            data_path = 'pose.bones["%s"].rotation_euler' % item['bone_name']
            if not data_paths.get(data_path):
                data_paths[data_path] = []
            data_paths[data_path].append((item['timestamp'], item['rotation']))

        use_inherit_rotation = False
        data_path = 'data.bones["%s"].use_inherit_rotation' % item['bone_name']
        if not data_paths.get(data_path):
            data_paths[data_path] = []
        data_paths[data_path].append((item['timestamp'], [use_inherit_rotation]))

    for data_path, values_tmp in data_paths.items():
        frame_count = len(values_tmp)
        values_tmp = list(zip(*values_tmp))  # This unzips the list of tuples into two separate lists
        timestamps = list(values_tmp[0])
        values = list(values_tmp[1])
        index_len = len(values[0])

        for axis_i in range(index_len):
            curve = action.fcurves.new(data_path=data_path, index=axis_i)
            keyframe_points = curve.keyframe_points
            keyframe_points.add(frame_count)

            for frame_i in range(frame_count):
                timestamp = timestamps[frame_i]
                transform = values[frame_i][axis_i]
                keyframe_points[frame_i].co = (
                    recorded_timestamps[timestamp],
                    transform)
                keyframe_points[frame_i].interpolation = 'LINEAR'


def process_object_recording(obj_name, data):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        print('Object', obj_name, 'not found!')
        return

    # Create new action
    action = bpy.data.actions.new(name='Anim Obj ' + obj_name)
    action.use_fake_user = True
    obj.animation_data_create().action = action

    # Handle recording data
    data_paths = OrderedDict()
    for item in data:
        if item['location']:
            data_path = 'location'
            if not data_paths.get(data_path):
                data_paths[data_path] = []

            data_paths[data_path].append((item['timestamp'], item['location']))

        if item['rotation']:
            data_path = 'rotation_quaternion'
            if not data_paths.get(data_path):
                data_paths[data_path] = []

            data_paths[data_path].append((item['timestamp'], item['rotation']))

    for data_path, values in data_paths.items():
        # print(data_path)
        frame_count = len(values)
        index_len = 3 if data_path.endswith('location') else 4

        for axis_i in range(index_len):
            curve = action.fcurves.new(data_path=data_path, index=axis_i)
            keyframe_points = curve.keyframe_points
            keyframe_points.add(frame_count)

            for frame_i in range(frame_count):
                timestamp = values[frame_i][0]
                transform = values[frame_i][1]
                keyframe_points[frame_i].co = (
                    recorded_timestamps[timestamp],
                    transform[axis_i])
                keyframe_points[frame_i].interpolation = 'LINEAR'


def process_face_recording(obj_name, data):
    mesh = bpy.data.objects.get(obj_name)
    if not mesh:
        print('Object', obj_name, 'not found!')
        return

    # Create new action
    action = bpy.data.actions.new(name='Anim Face ' + obj_name)
    action.use_fake_user = True
    mesh.animation_data_create().action = action

    # Handle recording data
    data_paths = OrderedDict()
    for item in data:
        data_path = 'data.shape_keys.key_blocks["%s"].value' % item['shapekey_name']
        if not data_paths.get(data_path):
            data_paths[data_path] = []

        data_paths[data_path].append((item['timestamp'], item['value']))

    for data_path, values in data_paths.items():
        # print(data_path)
        frame_count = len(values)

        curve = action.fcurves.new(data_path=data_path, index=0)
        keyframe_points = curve.keyframe_points
        keyframe_points.add(frame_count)

        for frame_i in range(frame_count):
            timestamp = values[frame_i][0]
            shapekey_value = values[frame_i][1]
            keyframe_points[frame_i].co = (
                recorded_timestamps[timestamp],
                shapekey_value)
            keyframe_points[frame_i].interpolation = 'LINEAR'


def convert_timestamps_to_keyframes():
    timestamps = list(recorded_timestamps.keys())

    def get_frame(frame_number):
        return int(round((timestamps[frame_number] - timestamps[0]) * bpy.context.scene.rsl_receiver_fps, 0))

    # Fix frame numbers that are incorrect because of rounding errors
    for i, timestamp in enumerate(timestamps):
        curr_frame = get_frame(i)

        if 0 < i < len(timestamps) - 1:
            prev_frame = get_frame(i - 1)
            next_frame = get_frame(i + 1)
            if prev_frame == curr_frame and next == curr_frame + 2:
                curr_frame += 1
            if next_frame == curr_frame and prev_frame == curr_frame - 2:
                curr_frame -= 1

        if i == len(timestamps) - 1:
            prev_frame = get_frame(i - 1)
            if prev_frame == curr_frame:
                curr_frame += 1

        recorded_timestamps[timestamp] = curr_frame


def record_bone(timestamp, arm_name, bone_name, rotation, location=None):
    if not recorded_data.get('actors'):
        recorded_data['actors'] = {}
    if not recorded_data['actors'].get(arm_name):
        recorded_data['actors'][arm_name] = []

    data = {
        'timestamp': timestamp,
        'bone_name': bone_name,
        'rotation': copy.deepcopy(rotation),
        'location': copy.deepcopy(location)
    }

    recorded_data['actors'][arm_name].append(data)
    recorded_timestamps[timestamp] = 0


def record_face(timestamp, mesh_name, shapekey_name, value):
    if not recorded_data.get('faces'):
        recorded_data['faces'] = {}
    if not recorded_data['faces'].get(mesh_name):
        recorded_data['faces'][mesh_name] = []

    data = {
        'timestamp': timestamp,
        'shapekey_name': shapekey_name,
        'value': copy.deepcopy(value)
    }

    recorded_data['faces'][mesh_name].append(data)
    recorded_timestamps[timestamp] = 0


def record_object(timestamp, obj_name, rotation, location):
    if not recorded_data.get('objects'):
        recorded_data['objects'] = {}
    if not recorded_data['objects'].get(obj_name):
        recorded_data['objects'][obj_name] = []

    data = {
        'timestamp': timestamp,
        'rotation': copy.deepcopy(rotation),
        'location': copy.deepcopy(location)
    }

    recorded_data['objects'][obj_name].append(data)
    recorded_timestamps[timestamp] = 0
