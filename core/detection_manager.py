import os
import bpy
import json
import pathlib

from . import retargeting
from .auto_detect_lists.bones import bone_list, ignore_rokoko_retargeting_bones
from .auto_detect_lists.shapes import shape_list

bone_detection_list = {}
bone_detection_list_unmodified = {}
bone_detection_list_custom = {}
shape_detection_list = {}
shape_detection_list_unmodified = {}
shape_detection_list_custom = {}

main_dir = str(pathlib.Path(os.path.dirname(__file__)).parent.resolve())
resources_dir = os.path.join(main_dir, "resources")
custom_bones_dir = os.path.join(resources_dir, "custom_bones")
custom_bone_list_file = os.path.join(custom_bones_dir, "custom_bone_list.json")


def load_detection_lists():
    global bone_detection_list, bone_detection_list_unmodified, bone_detection_list_custom, shape_detection_list, shape_detection_list_unmodified, shape_detection_list_custom

    # Create the lists from the internal naming lists
    bone_detection_list_unmodified = setup_bone_list(bone_list)
    shape_detection_list_unmodified = setup_shape_list()

    # Load the custom naming lists from the file
    bone_detection_list_custom, shape_detection_list_custom = load_custom_lists_from_file()

    # Combine custom and internal lists
    bone_detection_list = combine_lists(bone_detection_list_unmodified, bone_detection_list_custom)
    shape_detection_list = combine_lists(shape_detection_list_unmodified, shape_detection_list_custom)

    # Print the whole bone list
    # print_bone_detection_list()


def setup_bone_list(raw_bone_list):
    new_bone_list = {}

    for bone_key, bone_values in raw_bone_list.items():
        # Add the bones to the list if no side indicator is found
        if 'left' not in bone_key:
            new_bone_list[bone_key] = [bone_value.lower() for bone_value in bone_values]
            if bone_key == 'spine':
                new_bone_list['chest'] = [bone_value.lower() for bone_value in bone_values]
            continue

        # Add bones to the list that are two sided
        bone_values_left = []
        bone_values_right = []

        for bone_name in bone_values:
            bone_name = bone_name.lower()

            if '\l' in bone_name:
                for replacement in ['l', 'left', 'r', 'right']:
                    bone_name_new = bone_name.replace('\l', replacement)

                    # Debug if duplicates are found
                    if bone_name_new in bone_values_left or bone_name_new in bone_values_right:
                        print('Duplicate autodetect bone entry:', bone_name, bone_name_new)
                        continue

                    if 'l' in replacement:
                        bone_values_left.append(bone_name_new)
                    else:
                        bone_values_right.append(bone_name_new)

        bone_key_left = bone_key
        bone_key_right = bone_key.replace('left', 'right')

        new_bone_list[bone_key_left] = bone_values_left
        new_bone_list[bone_key_right] = bone_values_right

    return new_bone_list


def setup_shape_list():
    new_shape_list = {}

    for shape_key, shape_names in shape_list.items():
        new_shape_list[shape_key] = [shape_key.lower()] + [shape_name.lower() for shape_name in shape_names]

    return new_shape_list


# Combines the list and inputs the second list first
def combine_lists(internal_list, custom_list):
    combined_list = {}

    # Set dictionary structure
    for key in internal_list.keys():
        combined_list[key] = []

    # Load in custom values into the dictionary
    for key, values in custom_list.items():
        combined_list[key] = []
        for value in values:
            combined_list[key].append(value.lower())

    # Load in internal values
    for key, values in internal_list.items():
        for value in values:
            combined_list[key].append(value)

    return combined_list


def print_bone_detection_list():
    print('BONES')
    for key, values in bone_detection_list.items():
        print(key, values)
        print()

    print('CUSTOM BONES')
    for key, values in bone_detection_list_custom.items():
        print(key, values)
        print('--> ', bone_detection_list[key])
        print()

    # print('SHAPES')
    # for key, values in shape_detection_list.items():
    #     print(key, values)

    print('CUSTOM SHAPES')
    for key, values in shape_detection_list_custom.items():
        print(key, values)
        print('--> ', shape_detection_list[key])
        print()
    print()


def save_retargeting_to_list():
    global bone_detection_list, bone_detection_list_custom
    armature_target = retargeting.get_target_armature()
    retargeting_dict = detect_retarget_bones()

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
            if not bone_detection_list_custom.get(bone_name_key_detected):
                bone_detection_list_custom[bone_name_key_detected] = []

            # TODO Idea: If a target bone got detected but was removed and left empty, add it to an ignore list. So if that exact match-up gets detected again, leave it empty

            # If the detected target is in the custom bones list but it got changed, remove it from the list. If the new bone gets detected automatically now, don't add it to the custom list
            if bone_name_target_detected.lower() in bone_detection_list_custom[bone_name_key_detected]:
                if bone_name_key_detected.startswith('custom_bone_') and len(bone_detection_list_custom[bone_name_key_detected]) == 2:
                    bone_detection_list_custom.pop(bone_name_key_detected)
                else:
                    bone_detection_list_custom[bone_name_key_detected].remove(bone_name_target_detected.lower())

                # Update the bone detection list in order to correctly figure out if the new selected bone needs to be saved
                bone_detection_list = combine_lists(bone_detection_list_unmodified, bone_detection_list_custom)

                retargeting_dict = detect_retarget_bones()
                bone_name_detected_new, _ = retargeting_dict[bone_item.bone_name_source]
                if bone_name_detected_new.lower() == bone_name_target:
                    # print('No need to add new bone to save')
                    continue

            # If the source bone got detected but the target bone got changed, save the target bone into the custom list
            if bone_name_target not in bone_detection_list_custom[bone_name_key_detected]:
                bone_detection_list_custom[bone_name_key_detected] = [bone_name_target] + bone_detection_list_custom[bone_name_key_detected]
            continue

        # If it is a completely new pair of bones or a spine bone, add it as a new bone to the list
        bone_detection_list_custom['custom_bone_' + bone_name_source] = [bone_name_source, bone_name_target]

    # Save the updated custom list locally and update
    save_to_file_and_update()


def save_live_data_bone_to_list(bone_key, bone_name, bone_name_previous):
    global bone_detection_list, bone_detection_list_custom

    if not bone_detection_list_custom.get(bone_key):
        bone_detection_list_custom[bone_key] = []

    # If the previously detected bone name is in the custom bones list but it got changed, remove it from the list. If the new bone gets detected automatically now, don't add it to the custom list
    if bone_name_previous.lower() in bone_detection_list_custom[bone_key]:
        bone_detection_list_custom[bone_key].remove(bone_name_previous.lower())
        # print('Removed:', bone_name_previous)

        # Update the bone detection list in order to correctly figure out if the new selected bone needs to be saved
        bone_detection_list = combine_lists(bone_detection_list_unmodified, bone_detection_list_custom)

        bone_name_detected_new = detect_bone(bpy.context.active_object, bone_key)
        if bone_name_detected_new == bone_name:
            # print('No need to add new bone to save')
            return

    bone_detection_list_custom[bone_key] = [bone_name] + bone_detection_list_custom[bone_key]


def save_live_data_shape_to_list(shape_key, shape_name, shape_name_previous):
    global shape_detection_list, shape_detection_list_custom

    if not shape_detection_list_custom.get(shape_key):
        shape_detection_list_custom[shape_key] = []

    # If the previously detected shape name is in the custom shapes list but it got changed, remove it from the list. If the new shapekey gets detected automatically now, don't add it to the custom list
    if shape_name_previous.lower() in shape_detection_list_custom[shape_key]:
        shape_detection_list_custom[shape_key].remove(shape_name_previous.lower())
        # print('Removed:', shape_name_previous)

        # Update the shapekey detection list in order to correctly figure out if the new selected shapekey needs to be saved
        shape_detection_list = combine_lists(shape_detection_list_unmodified, shape_detection_list_custom)

        shape_name_detected_new = detect_shape(bpy.context.active_object, shape_key)
        if shape_name_detected_new == shape_name:
            # print('No need to add new bone to save')
            return

    shape_detection_list_custom[shape_key] = [shape_name] + shape_detection_list_custom[shape_key]


def save_to_file_and_update():
    save_custom_to_file()
    load_detection_lists()


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
    for key, values in bone_detection_list_custom.items():
        if not values:
            continue

        for i in range(len(values)):
            values[i] = values[i].lower()

        new_bone_list[key] = values

    # Remove all empty fields and make all custom fields lowercase
    for key, values in shape_detection_list_custom.items():
        if not values:
            continue

        for i in range(len(values)):
            values[i] = values[i].lower()

        new_shape_list[key] = values

    new_custom_list['bones'] = new_bone_list
    new_custom_list['shapes'] = new_shape_list

    return new_custom_list


def import_custom_list(directory, file_name):
    global bone_detection_list_custom, shape_detection_list_custom

    file_path = os.path.join(directory, file_name)
    new_custom_bone_list, new_custom_shape_list = load_custom_lists_from_file(file_path=file_path)

    # Merge the new and old custom bone lists
    for key, bones in bone_detection_list_custom.items():
        if not new_custom_bone_list.get(key):
            new_custom_bone_list[key] = []

        for bone in new_custom_bone_list[key]:
            if bone in bones:
                bones.remove(bone)

        new_custom_bone_list[key] += bones

    # Merge the new and old custom shape lists
    for key, shapes in shape_detection_list_custom.items():
        if not new_custom_shape_list.get(key):
            new_custom_shape_list[key] = []

        for shape in new_custom_shape_list[key]:
            if shape in shapes:
                shapes.remove(shape)

        new_custom_shape_list[key] += shapes

    bone_detection_list_custom = new_custom_bone_list
    shape_detection_list_custom = new_custom_shape_list


def export_custom_list2(directory):
    file_path = os.path.join(directory, 'custom_bone_list.json')

    i = 1
    while os.path.isfile(file_path):
        file_path = os.path.join(directory, 'custom_bone_list' + str(i) + '.json')
        i += 1

    save_custom_to_file(file_path=file_path)

    return os.path.basename(file_path)


def export_custom_list(file_path):
    if not bone_detection_list_custom and not shape_detection_list_custom:
        return None

    save_custom_to_file(file_path=file_path)
    return os.path.basename(file_path)


def delete_custom_bone_list():
    global bone_detection_list_custom
    bone_detection_list_custom = {}
    save_to_file_and_update()


def delete_custom_shape_list():
    global shape_detection_list_custom
    shape_detection_list_custom = {}
    save_to_file_and_update()


def get_bone_list():
    return bone_detection_list


def get_custom_bone_list():
    return bone_detection_list_custom


def get_shape_list():
    return shape_detection_list


def get_custom_shape_list():
    return shape_detection_list_custom


def standardize_bone_name(name):
    # List of chars to replace if they are at the start of a bone name
    starts_with = [
        ('_', ''),
        ('ValveBiped_', ''),
        ('Valvebiped_', ''),
        ('Bip1_', 'Bip_'),
        ('Bip01_', 'Bip_'),
        ('Bip001_', 'Bip_'),
        ('Character1_', ''),
        ('HLP_', ''),
        ('JD_', ''),
        ('JU_', ''),
        ('Armature|', ''),
        ('Bone_', ''),
        ('C_', ''),
        ('Cf_S_', ''),
        ('Cf_J_', ''),
        ('G_', ''),
        ('Joint_', ''),
        ('DEF_', ''),
    ]

    # Standardize names
    # Make all the underscores!
    name = name.replace(' ', '_') \
        .replace('-', '_') \
        .replace('.', '_') \
        .replace('____', '_') \
        .replace('___', '_') \
        .replace('__', '_') \

    # Replace if name starts with specified chars
    for replacement in starts_with:
        if name.startswith(replacement[0]):
            name = replacement[1] + name[len(replacement[0]):]

    # Remove digits from the start
    name_split = name.split('_')
    if len(name_split) > 1 and name_split[0].isdigit():
        name = name_split[1]

    # Specific condition
    name_split = name.split('"')
    if len(name_split) > 3:
        name = name_split[1]

    # Another specific condition
    if ':' in name:
        for i, split in enumerate(name.split(':')):
            if i == 0:
                name = ''
            else:
                name += split

    # Remove S0 from the end
    if name[-2:] == 'S0':
        name = name[:-2]

    if name[-4:] == '_Jnt':
        name = name[:-4]

    return name.lower()


def detect_shape(obj, shape_name_key):
    # Go through the target mesh and search for shapekey that fit the main shapekey
    found_shape_name = ''
    is_custom = False

    for shapekey in obj.data.shape_keys.key_blocks:
        if is_custom:  # If a custom shapekey name was found, stop searching. it has priority
            break

        if shape_detection_list_custom.get(shape_name_key):
            for shape_name_detected in shape_detection_list_custom[shape_name_key]:
                if shape_name_detected == shapekey.name.lower():
                    found_shape_name = shapekey.name
                    is_custom = True
                    break

        if found_shape_name and shape_name_key != 'chest':  # If a shape_name was found, only continue looking for custom shapekey names, they have priority
            continue

        for shape_name_detected in shape_detection_list[shape_name_key]:
            if shape_name_detected == shapekey.name.lower():
                found_shape_name = shapekey.name
                break

        # If nothing was found, check if the shapekey names match exactly
        if not found_shape_name and shape_name_key.lower() == shapekey.name.lower():
            found_shape_name = shapekey.name

    return found_shape_name


def detect_bone(obj, bone_name_key, bone_name_source=None):
    # Go through the target armature and search for bones that fit the main source bone
    found_bone_name = ''
    is_custom = False

    if not bone_name_source:
        bone_name_source = bone_name_key

    for bone in obj.pose.bones:
        if is_custom:  # If a custom bone name was found, stop searching. it has priority
            break

        if bone_detection_list_custom.get(bone_name_key):
            for bone_name_detected in bone_detection_list_custom[bone_name_key]:
                if bone_name_detected == bone.name.lower():
                    found_bone_name = bone.name
                    is_custom = True
                    break

        if found_bone_name and bone_name_key != 'chest':  # If a bone_name was found, only continue looking for custom bone names, they have priority
            continue

        for bone_name_detected in bone_detection_list[bone_name_key]:
            if bone_name_detected == standardize_bone_name(bone.name):
                found_bone_name = bone.name
                break

        # If nothing was found, check if the bone names match exactly
        if not found_bone_name and bone_name_source.lower() == bone.name.lower():
            found_bone_name = bone.name

    return found_bone_name


def detect_retarget_bones() -> {str: (str, str)}:
    """
    Detects all matching bones in the target and source armatures
    :return: A dictionary with the source bone name as key and a tuple of the target bone name and their shared key name as value
    """
    bone_list_animated = []
    retargeting_dict = {}
    armature_source = retargeting.get_source_armature()
    armature_target = retargeting.get_target_armature()

    # Get all source bones from the animation and add them to bone_list_animated
    for fc in armature_source.animation_data.action.fcurves:
        bone_name = fc.data_path.split('"')
        if len(bone_name) == 3 and bone_name[1] not in bone_list_animated:
            bone_list_animated.append(bone_name[1])

    # Check if this animation is from Rokoko Studio. Ignore certain bones in that case
    is_rokoko_animation = False
    if 'newton' in bone_list_animated and 'RightFinger1Tip' in bone_list_animated and 'HeadVertex' in bone_list_animated and 'LeftFinger2Metacarpal' in bone_list_animated:
        is_rokoko_animation = True

    spines_source = []
    spines_target = []
    found_main_bones = []

    # Then add all the bones to the retargeting dictionary
    for bone_name in bone_list_animated:
        if is_rokoko_animation and bone_name in ignore_rokoko_retargeting_bones:
            continue

        bone_item_source = bone_name
        bone_item_target = ''
        main_bone_name = ''
        standardized_bone_name_source = standardize_bone_name(bone_name)

        # Find the main bone name (bone name key) of the source bone
        for bone_main, bone_values in bone_detection_list.items():
            if bone_main == 'chest':  # Ignore chest bones, these are only used for live data
                continue
            if bone_main in found_main_bones:  # Only find main bones once, except for spines
                continue
            # If the source bone name is found in the bone detection list, add its main bone name to the list of found main bones
            if bone_name.lower() in bone_values or standardized_bone_name_source in bone_values or standardized_bone_name_source == bone_main.lower():
                main_bone_name = bone_main
                if main_bone_name != 'spine':  # Ignore the spine bones for now, so that it can add the custom spine bones first
                    found_main_bones.append(main_bone_name)
                    break

        # Add the source bone and the main bone name to the retargeting dict with an empty targeting bone name
        retargeting_dict[bone_item_source] = ("", main_bone_name)

        # If no main bone name was found, continue
        if not main_bone_name:
            continue

        # If it's a spine bone, add it to the list for later fixing
        if main_bone_name == 'spine':
            spines_source.append(bone_name)
            continue

        # If it's a custom spine/chest bone, add it to the spine list nonetheless
        custom_main_bone = main_bone_name.startswith('custom_bone_')
        if custom_main_bone and standardize_bone_name(main_bone_name.replace('custom_bone_', '')) in bone_detection_list['spine']:
            spines_source.append(bone_name)

        # Go through the target armature and search for bones that fit the main source bone
        bone_item_target = detect_bone(armature_target, main_bone_name, bone_name_source=bone_item_source)

        # Add the bone to the retargeting list again
        retargeting_dict[bone_item_source] = (bone_item_target, main_bone_name)

    # Add target spines to list for later fixing
    for bone in armature_target.pose.bones:
        bone_name_standardized = standardize_bone_name(bone.name)
        if bone_name_standardized in bone_detection_list['spine']:
            spines_target.append(bone.name)

    # Fix spine auto detection
    if spines_target and spines_source:
        # print(spines_source)
        spine_dict = {}

        i = 0
        for spine in reversed(spines_source):
            i += 1
            if i == len(spines_target):
                break
            spine_dict[spine] = spines_target[-i]

        spine_dict[spines_source[0]] = spines_target[0]

        # Fill in fixed spines into unfilled matches
        for spine_source, spine_target in spine_dict.items():
            for bone_source, bone_values in retargeting_dict.items():
                bone_target, bone_key = bone_values
                if bone_source == spine_source and not bone_target:
                    retargeting_dict[bone_source] = (spine_target, bone_key)
                    break

    return retargeting_dict
