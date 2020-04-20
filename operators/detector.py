import bpy

from ..core import animation_lists
from ..core.auto_detect_lists.bones import bone_list


class DetectFaceShapes(bpy.types.Operator):
    bl_idname = "rsl.detect_face_shapes"
    bl_label = "Auto Detect"
    bl_description = "Automatically detect face shape keys for supported naming schemes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object

        if not hasattr(obj.data, 'shape_keys') or not hasattr(obj.data.shape_keys, 'key_blocks'):
            self.report({'ERROR'}, 'This mesh has no shapekeys!')
            return {'CANCELLED'}

        for shape_name in animation_lists.face_shapes:
            shortest_detected_shape = None
            for shapekey in obj.data.shape_keys.key_blocks:
                if shape_name.lower() in shapekey.name.lower():
                    if not shortest_detected_shape or len(shortest_detected_shape) > len(shapekey.name):
                        shortest_detected_shape = shapekey.name

            if shortest_detected_shape:
                setattr(obj, 'rsl_face_' + shape_name, shortest_detected_shape)

        return {'FINISHED'}


class DetectActorBones(bpy.types.Operator):
    bl_idname = "rsl.detect_actor_bones"
    bl_label = "Auto Detect"
    bl_description = "Automatically detect actor bones for supported naming schemes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object

        for bone_name_key in animation_lists.actor_bones.keys():
            bone_names = get_bone_list()[bone_name_key]
            for bone in obj.pose.bones:
                bone_name = standardize_bone_name(bone.name)
                if bone_name in bone_names:
                    setattr(obj, 'rsl_actor_' + bone_name_key, bone.name)

                    # If looking for the chest bone, use the last found entry instead of the first one
                    if bone_name_key != 'chest':
                        break

        return {'FINISHED'}


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


def get_bone_list():
    new_bone_list = {}

    for bone_key, bone_values in bone_list.items():
        if 'left' not in bone_key:
            new_bone_list[bone_key] = [bone_value.lower() for bone_value in bone_values]
            if bone_key == 'spine':
                new_bone_list['chest'] = [bone_value.lower() for bone_value in bone_values]
            continue

        bone_values_left = []
        bone_values_right = []

        for bone_name in bone_values:
            bone_name = bone_name.lower()

            if '\l' in bone_name:
                bone_name_l = bone_name.replace('\l', 'l')
                bone_name_left = bone_name.replace('\l', 'left')
                bone_name_r = bone_name.replace('\l', 'r')
                bone_name_right = bone_name.replace('\l', 'right')

                # Debug if duplicates are found
                if bone_name_l in bone_values_left:
                    print('Duplicate autodetect bone entry:', bone_name, bone_name_l)
                    continue

                bone_values_left.append(bone_name_l)
                bone_values_left.append(bone_name_left)
                bone_values_right.append(bone_name_r)
                bone_values_right.append(bone_name_right)

        bone_key_left = bone_key
        bone_key_right = bone_key.replace('left', 'right')

        new_bone_list[bone_key_left] = bone_values_left
        new_bone_list[bone_key_right] = bone_values_right

    return new_bone_list
