import os
import bpy
import json
import pathlib

from . import retargeting
from . import detection_manager

main_dir = str(pathlib.Path(os.path.dirname(__file__)).parent.resolve())
resources_dir = os.path.join(main_dir, "resources")
custom_bones_dir = os.path.join(resources_dir, "custom_bones")
custom_bone_list_file = os.path.join(custom_bones_dir, "custom_bone_list.json")


def save_retargeting_to_list():
    armature_target = retargeting.get_target_armature()
    retargeting_dict = detection_manager.detect_retarget_bones()

    for bone_item in bpy.context.scene.rsl_retargeting_bone_list:
        if not bone_item.bone_name_source or not bone_item.bone_name_target:
            continue

        bone_name_key = bone_item.bone_name_key
        bone_name_source = bone_item.bone_name_source.lower()
        bone_name_target = bone_item.bone_name_target.lower()
        bone_name_target_detected, bone_name_key_detected = retargeting_dict[bone_item.bone_name_source]

        if bone_name_target_detected == bone_item.bone_name_target:
            continue

        if bone_name_key_detected and bone_name_key_detected != 'spine':
            if not detection_manager.bone_detection_list_custom.get(bone_name_key_detected):
                detection_manager.bone_detection_list_custom[bone_name_key_detected] = []

            # TODO Idea: If a target bone got detected but was removed and left empty, add it to an ignore list. So if that exact match-up gets detected again, leave it empty

            # If the detected target is in the custom bones list but it got changed, remove it from the list. If the new bone gets detected automatically now, don't add it to the custom list
            if bone_name_target_detected.lower() in detection_manager.bone_detection_list_custom[bone_name_key_detected]:
                if bone_name_key_detected.startswith('custom_bone_') and len(detection_manager.bone_detection_list_custom[bone_name_key_detected]) == 2:
                    detection_manager.bone_detection_list_custom.pop(bone_name_key_detected)
                else:
                    detection_manager.bone_detection_list_custom[bone_name_key_detected].remove(bone_name_target_detected.lower())

                # Update the bone detection list in order to correctly figure out if the new selected bone needs to be saved
                detection_manager.bone_detection_list = detection_manager.combine_lists(detection_manager.bone_detection_list_unmodified, detection_manager.bone_detection_list_custom)

                retargeting_dict = detection_manager.detect_retarget_bones()
                bone_name_detected_new, _ = retargeting_dict[bone_item.bone_name_source]
                if bone_name_detected_new.lower() == bone_name_target:
                    # print('No need to add new bone to save')
                    continue

            # If the source bone got detected but the target bone got changed, save the target bone into the custom list
            if bone_name_target not in detection_manager.bone_detection_list_custom[bone_name_key_detected]:
                detection_manager.bone_detection_list_custom[bone_name_key_detected] = [bone_name_target] + detection_manager.bone_detection_list_custom[bone_name_key_detected]
            continue

        # If it is a completely new pair of bones or a spine bone, add it as a new bone to the list
        detection_manager.bone_detection_list_custom['custom_bone_' + bone_name_source] = [bone_name_source, bone_name_target]

    # Save the updated custom list locally and update
    save_to_file_and_update()


def save_live_data_bone_to_list(bone_key, bone_name, bone_name_previous):
    if not detection_manager.bone_detection_list_custom.get(bone_key):
        detection_manager.bone_detection_list_custom[bone_key] = []

    # If the previously detected bone name is in the custom bones list but it got changed, remove it from the list. If the new bone gets detected automatically now, don't add it to the custom list
    if bone_name_previous.lower() in detection_manager.bone_detection_list_custom[bone_key]:
        detection_manager.bone_detection_list_custom[bone_key].remove(bone_name_previous.lower())
        # print('Removed:', bone_name_previous)

        # Update the bone detection list in order to correctly figure out if the new selected bone needs to be saved
        detection_manager.bone_detection_list = detection_manager.combine_lists(detection_manager.bone_detection_list_unmodified, detection_manager.bone_detection_list_custom)

        bone_name_detected_new = detection_manager.detect_bone(bpy.context.active_object, bone_key)
        if bone_name_detected_new == bone_name:
            # print('No need to add new bone to save')
            return

    detection_manager.bone_detection_list_custom[bone_key] = [bone_name] + detection_manager.bone_detection_list_custom[bone_key]


def save_live_data_shape_to_list(shape_key, shape_name, shape_name_previous):

    if not detection_manager.shape_detection_list_custom.get(shape_key):
        detection_manager.shape_detection_list_custom[shape_key] = []

    # If the previously detected shape name is in the custom shapes list but it got changed, remove it from the list. If the new shapekey gets detected automatically now, don't add it to the custom list
    if shape_name_previous.lower() in detection_manager.shape_detection_list_custom[shape_key]:
        detection_manager.shape_detection_list_custom[shape_key].remove(shape_name_previous.lower())
        # print('Removed:', shape_name_previous)

        # Update the shapekey detection list in order to correctly figure out if the new selected shapekey needs to be saved
        detection_manager.shape_detection_list = detection_manager.combine_lists(detection_manager.shape_detection_list_unmodified, detection_manager.shape_detection_list_custom)

        shape_name_detected_new = detection_manager.detect_shape(bpy.context.active_object, shape_key)
        if shape_name_detected_new == shape_name:
            # print('No need to add new bone to save')
            return

    detection_manager.shape_detection_list_custom[shape_key] = [shape_name] + detection_manager.shape_detection_list_custom[shape_key]


def save_to_file_and_update():
    save_custom_to_file()
    detection_manager.load_detection_lists()


def save_custom_to_file(file_path=custom_bone_list_file):
    new_custom_list = clean_custom_list()
    print('To File:', new_custom_list)

    if not os.path.isdir(custom_bones_dir):
        os.mkdir(custom_bones_dir)

    with open(file_path, 'w', encoding="utf8") as outfile:
        json.dump(new_custom_list, outfile, ensure_ascii=False, indent=4)


def load_custom_lists_from_file(file_path=custom_bone_list_file):
    custom_bone_list = {}
    try:
        with open(file_path, encoding="utf8") as file:
            custom_bone_list = json.load(file)
    except FileNotFoundError:
        print('Custom bone list not found.')
    except json.decoder.JSONDecodeError:
        print("Custom bone list is not a valid json file!")

    if custom_bone_list.get('rokoko_custom_names') is None or custom_bone_list.get('version') is None or custom_bone_list.get('bones') is None or custom_bone_list.get('shapes') is None:
        print("Custom name list file is not a valid name list file")
        return {}, {}

    custom_bone_list.pop('rokoko_custom_names')
    custom_bone_list.pop('version')

    return custom_bone_list.get('bones'), custom_bone_list.get('shapes')


def clean_custom_list():
    new_custom_list = {
        'rokoko_custom_names':  True,
        'version': 1,
        'bones': {},
        'shapes': {}
    }

    new_bone_list = {}
    new_shape_list = {}

    # Remove all empty fields and make all custom fields lowercase
    for key, values in detection_manager.bone_detection_list_custom.items():
        if not values:
            continue

        for i in range(len(values)):
            values[i] = values[i].lower()

        new_bone_list[key] = values

    # Remove all empty fields and make all custom fields lowercase
    for key, values in detection_manager.shape_detection_list_custom.items():
        if not values:
            continue

        for i in range(len(values)):
            values[i] = values[i].lower()

        new_shape_list[key] = values

    new_custom_list['bones'] = new_bone_list
    new_custom_list['shapes'] = new_shape_list

    return new_custom_list


def import_custom_list(directory, file_name):
    file_path = os.path.join(directory, file_name)
    new_custom_bone_list, new_custom_shape_list = load_custom_lists_from_file(file_path=file_path)

    # Merge the new and old custom bone lists
    for key, bones in detection_manager.bone_detection_list_custom.items():
        if not new_custom_bone_list.get(key):
            new_custom_bone_list[key] = []

        for bone in new_custom_bone_list[key]:
            if bone in bones:
                bones.remove(bone)

        new_custom_bone_list[key] += bones

    # Merge the new and old custom shape lists
    for key, shapes in detection_manager.shape_detection_list_custom.items():
        if not new_custom_shape_list.get(key):
            new_custom_shape_list[key] = []

        for shape in new_custom_shape_list[key]:
            if shape in shapes:
                shapes.remove(shape)

        new_custom_shape_list[key] += shapes

    detection_manager.bone_detection_list_custom = new_custom_bone_list
    detection_manager.shape_detection_list_custom = new_custom_shape_list


def export_custom_list2(directory):
    file_path = os.path.join(directory, 'custom_bone_list.json')

    i = 1
    while os.path.isfile(file_path):
        file_path = os.path.join(directory, 'custom_bone_list' + str(i) + '.json')
        i += 1

    save_custom_to_file(file_path=file_path)

    return os.path.basename(file_path)


def export_custom_list(file_path):
    if not detection_manager.bone_detection_list_custom and not detection_manager.shape_detection_list_custom:
        return None

    save_custom_to_file(file_path=file_path)
    return os.path.basename(file_path)


def delete_custom_bone_list():
    detection_manager.bone_detection_list_custom = {}
    save_to_file_and_update()


def delete_custom_shape_list():
    detection_manager.shape_detection_list_custom = {}
    save_to_file_and_update()
