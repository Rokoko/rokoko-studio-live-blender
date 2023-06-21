
import bpy

from .auto_detect_lists.bones import bone_list, ignore_rokoko_retargeting_bones
from .auto_detect_lists.shapes import shape_list


class DetectionManager:

    def __init__(self, name_dict):
        self.name_dict_original = name_dict
        self.name_dict = {}

        self._setup_dict()

    def _setup_dict(self):
        for key, values in self.name_dict_original.items():
            self._add_names(key, values)

    def _add_names(self, key, values):
        raise NotImplementedError

    def print_dict(self):
        for key, values in self.name_dict.items():
            print(f"{key}: {values}")


class BoneDetectionManager(DetectionManager):
    def _add_names(self, key, values):
        # Add names to the list without changes if the key is not sided
        if "left" not in key:
            self.name_dict[key] = [name.lower() for name in values]
            if key == "spine":
                self.name_dict["chest"] = self.name_dict[key].copy()
            return

        # Add names to the list with changes if the key is sided
        names_left = []
        names_right = []

        for name in values:
            name = name.lower()

            if "\l" not in name:
                print(f"Warning: {name} from {key} does not contain a '\\l' marker")
                continue

            for replacement in ['l', 'left', 'r', 'right']:
                name_new = name.replace("\l", replacement)
                
                if name_new in names_left or name_new in names_right:
                    print(f"Warning: {name_new} from {key} is already in the list")
                    continue
                
                if "l" in replacement:
                    names_left.append(name_new)
                else:
                    names_right.append(name_new)

        self.name_dict[key] = names_left
        self.name_dict[key.replace("left", "right")] = names_right


class ShapeDetectionManager(DetectionManager):
        def _add_names(self, key, values):
            self.name_dict[key] = [key] + [name.lower() for name in values]
                


# bones = BoneDetectionManager(bone_list)
# bones.print_dict()

# shapes = ShapeDetectionManager(shape_list)
# shapes.print_dict()
