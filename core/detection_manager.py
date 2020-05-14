import os
import bpy
import json
import pathlib

from .auto_detect_lists.bones import bone_list

bone_detection_list = {}
bone_detection_list_custom = {}

main_dir = str(pathlib.Path(os.path.dirname(__file__)).parent.resolve())
resources_dir = os.path.join(main_dir, "resources")
custom_bones_dir = os.path.join(resources_dir, "custom_bones")
custom_bone_list_file = os.path.join(custom_bones_dir, "custom_bone_list.json")


def load_bone_detection_list():
    global bone_detection_list, bone_detection_list_custom

    # Create the list from the internal bone list
    bone_detection_list = create_internal_bone_list()
    bone_detection_list_custom = load_custom_bone_list_from_file()

    bone_detection_list = combine_bone_lists()

    # Print the whole bone list
    # print_bone_detection_list()


def update_bone_lists():
    global bone_detection_list
    bone_detection_list = combine_bone_lists()


def save_custom_bone_list():
    save_retargeting_to_list()
    save_to_file_and_update()


def save_to_file_and_update():
    save_custom_to_file()
    load_bone_detection_list()


def save_custom_to_file(file_path=custom_bone_list_file):
    new_custom_list = clean_custom_list()
    with open(file_path, 'w', encoding="utf8") as outfile:
        json.dump(new_custom_list, outfile, ensure_ascii=False, indent=4)


def load_custom_bone_list_from_file(file_path=custom_bone_list_file):
    custom_bone_list = {}
    try:
        with open(file_path, encoding="utf8") as file:
            custom_bone_list = json.load(file)
    except FileNotFoundError:
        print('Custom bone list not found.')
    except json.decoder.JSONDecodeError:
        print("Custom bone list is not a valid json file!")

    if not custom_bone_list.get('rokoko_custom_bones') or not custom_bone_list.get('version'):
        print("Custom bone list file is not a valid bone list fine")
        return {}

    custom_bone_list.pop('rokoko_custom_bones')
    custom_bone_list.pop('version')

    return custom_bone_list


def clean_custom_list():
    new_custom_list = {
        'rokoko_custom_bones':  True,
        'version': 1,
    }

    # Remove all empty fields and make all custom fields lowercase
    for key, values in bone_detection_list_custom.items():
        if not values:
            continue

        for i in range(len(values)):
            values[i] = values[i].lower()

        new_custom_list[key] = values

    return new_custom_list


def save_retargeting_to_list():
    global bone_detection_list_custom
    for bone_item in bpy.context.scene.rsl_retargeting_bone_list:
        if not bone_item.bone_name_source or not bone_item.bone_name_target:
            continue
        if bone_item.bone_name_target_detected == bone_item.bone_name_target:
            continue

        bone_name_key = bone_item.bone_name_key
        bone_name_source = bone_item.bone_name_source.lower()
        bone_name_target = bone_item.bone_name_target.lower()
        bone_name_target_detected = bone_item.bone_name_target_detected.lower()

        if bone_name_key and bone_name_key != 'spine':
            if not bone_detection_list_custom.get(bone_name_key):
                bone_detection_list_custom[bone_name_key] = []

            # TODO Idea: If a target bone got detected but was removed and left empty, add it to a ignore list. So if that exact match-up gets detected again, leave it empty

            # If the detected target is in the custom bones list but it got changed, remove it from the list and don't add the new bone into the list (maybe do add it, we'll have to see how this turns out)
            if bone_name_target_detected in bone_detection_list_custom[bone_name_key]:
                bone_detection_list_custom[bone_name_key].remove(bone_name_target_detected)
                continue

            # If the source bone got detected but the target bone got changed, save the target bone into the custom list
            if bone_name_target not in bone_detection_list_custom[bone_name_key]:
                bone_detection_list_custom[bone_name_key] = [bone_name_target] + bone_detection_list_custom[bone_name_key]
            continue

        # If it is a completely new pair of bones or a spine bone, add it as a new bone to the list
        bone_detection_list_custom['custom_bone_' + bone_name_source] = [bone_name_source, bone_name_target]


def combine_bone_lists():
    new_bone_list = {}

    # Set dictionary structure
    for key in bone_detection_list.keys():
        new_bone_list[key] = []

    # Load in custom bones into the dictionary
    for key, bones in bone_detection_list_custom.items():
        new_bone_list[key] = []
        for bone in bones:
            new_bone_list[key].append(bone.lower())
            # new_bone_list[key].append(standardize_bone_name(bone))

    # Load in internal bones
    for key, bones in bone_detection_list.items():
        for bone in bones:
            new_bone_list[key].append(bone)

    return new_bone_list


def import_custom_list(directory, file_name):
    global bone_detection_list_custom

    file_path = os.path.join(directory, file_name)
    new_custom_bone_list = load_custom_bone_list_from_file(file_path=file_path)

    # Merge the new and old custom bone lists
    for key, bones in bone_detection_list_custom.items():
        if not new_custom_bone_list.get(key):
            new_custom_bone_list[key] = []

        for bone in new_custom_bone_list[key]:
            if bone in bones:
                bones.remove(bone)

        new_custom_bone_list[key] += bones

    bone_detection_list_custom = new_custom_bone_list


def export_custom_list2(directory):
    file_path = os.path.join(directory, 'custom_bone_list.json')

    i = 1
    while os.path.isfile(file_path):
        file_path = os.path.join(directory, 'custom_bone_list' + str(i) + '.json')
        i += 1

    save_custom_to_file(file_path=file_path)

    return os.path.basename(file_path)


def export_custom_list(file_path):

    save_custom_to_file(file_path=file_path)

    return os.path.basename(file_path)


def delete_custom_list():
    global bone_detection_list_custom
    bone_detection_list_custom = {}
    save_to_file_and_update()


def print_bone_detection_list():
    # for key, values in bone_detection_list.items():
    #     print(key, values)
    #     print()
    # print('CUSTOM')
    for key, values in bone_detection_list_custom.items():
        print(key, values)
        print('--> ', bone_detection_list[key])
        print()


def create_internal_bone_list():
    new_bone_list = {}

    for bone_key, bone_values in bone_list.items():
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


def get_bone_list():
    return bone_detection_list


def get_custom_bone_list():
    return bone_detection_list_custom


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