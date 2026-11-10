# Checks Auto Detect (rsl.detect_actor_bones):
# - Without custom names, Newton gets the mapping saved in Newton Static.blend and MPFB's game engine rig
#   gets the mapping below, both made with the detection before custom names were matched first.
# - Custom names win over default matches: with the custom name spine -> Hips, spine gets Hips,
#   even though hip comes earlier and matches Hips by default.
# Uses its own custom name lists, so the user's saved custom names don't affect it. Exits with code 1 on failure.
#
# Run from the repo root in background Blender:
#   blender -b --factory-startup --python-exit-code 1 --python tests/test_auto_detect.py -- .
import bpy
import importlib.util
import pathlib
import sys

addon_dir = pathlib.Path(sys.argv[sys.argv.index("--") + 1]).resolve()

# Import the add-on as a package (its folder name has dashes) and register only what the test needs
spec = importlib.util.spec_from_file_location("rsl_under_test", addon_dir / "__init__.py",
                                              submodule_search_locations=[str(addon_dir)])
rsl = importlib.util.module_from_spec(spec)
sys.modules["rsl_under_test"] = rsl
spec.loader.exec_module(rsl)
newton_blend = rsl.core.utils.NEWTON_BLEND_FILE
bpy.utils.register_class(rsl.panels.retargeting.BoneListItem)  # Needed by a scene property
rsl.properties.register()
rsl.core.detection_manager.load_detection_lists()
bpy.utils.register_class(rsl.operators.detector.DetectActorBones)

detection_manager = rsl.core.detection_manager
bone_keys = list(rsl.core.animation_lists.get_bones().keys())

# MPFB game engine rig: bone names with their parents, in the rig's bone order
MPFB_BONES = [
    ('Root', None), ('pelvis', 'Root'), ('spine_01', 'pelvis'), ('spine_02', 'spine_01'), ('spine_03', 'spine_02'),
    ('clavicle_l', 'spine_03'), ('upperarm_l', 'clavicle_l'), ('lowerarm_l', 'upperarm_l'), ('hand_l', 'lowerarm_l'),
    ('index_01_l', 'hand_l'), ('index_02_l', 'index_01_l'), ('index_03_l', 'index_02_l'),
    ('middle_01_l', 'hand_l'), ('middle_02_l', 'middle_01_l'), ('middle_03_l', 'middle_02_l'),
    ('pinky_01_l', 'hand_l'), ('pinky_02_l', 'pinky_01_l'), ('pinky_03_l', 'pinky_02_l'),
    ('ring_01_l', 'hand_l'), ('ring_02_l', 'ring_01_l'), ('ring_03_l', 'ring_02_l'),
    ('thumb_01_l', 'hand_l'), ('thumb_02_l', 'thumb_01_l'), ('thumb_03_l', 'thumb_02_l'),
    ('clavicle_r', 'spine_03'), ('upperarm_r', 'clavicle_r'), ('lowerarm_r', 'upperarm_r'), ('hand_r', 'lowerarm_r'),
    ('index_01_r', 'hand_r'), ('index_02_r', 'index_01_r'), ('index_03_r', 'index_02_r'),
    ('middle_01_r', 'hand_r'), ('middle_02_r', 'middle_01_r'), ('middle_03_r', 'middle_02_r'),
    ('pinky_01_r', 'hand_r'), ('pinky_02_r', 'pinky_01_r'), ('pinky_03_r', 'pinky_02_r'),
    ('ring_01_r', 'hand_r'), ('ring_02_r', 'ring_01_r'), ('ring_03_r', 'ring_02_r'),
    ('thumb_01_r', 'hand_r'), ('thumb_02_r', 'thumb_01_r'), ('thumb_03_r', 'thumb_02_r'),
    ('neck_01', 'spine_03'), ('head', 'neck_01'),
    ('thigh_l', 'pelvis'), ('calf_l', 'thigh_l'), ('foot_l', 'calf_l'), ('ball_l', 'foot_l'),
    ('thigh_r', 'pelvis'), ('calf_r', 'thigh_r'), ('foot_r', 'calf_r'), ('ball_r', 'foot_r'),
]

# Result of Auto Detect on the MPFB rig before custom names were matched first (keys not listed stay empty)
MPFB_EXPECTED = {
    'hip': 'pelvis', 'spine': 'spine_01', 'chest': 'spine_03', 'neck': 'neck_01', 'head': 'head',
    'leftShoulder': 'clavicle_l', 'leftUpperArm': 'upperarm_l', 'leftLowerArm': 'lowerarm_l', 'leftHand': 'hand_l',
    'rightShoulder': 'clavicle_r', 'rightUpperArm': 'upperarm_r', 'rightLowerArm': 'lowerarm_r', 'rightHand': 'hand_r',
    'leftUpLeg': 'thigh_l', 'leftLeg': 'calf_l', 'leftFoot': 'foot_l', 'leftToe': 'ball_l',
    'rightUpLeg': 'thigh_r', 'rightLeg': 'calf_r', 'rightFoot': 'foot_r', 'rightToe': 'ball_r',
}
for side in ('l', 'r'):
    for finger, mpfb_finger in (('Thumb', 'thumb'), ('Index', 'index'), ('Middle', 'middle'), ('Ring', 'ring'), ('Little', 'pinky')):
        for i, segment in enumerate(('Proximal', 'Medial', 'Distal')):
            MPFB_EXPECTED[('left' if side == 'l' else 'right') + finger + segment] = f'{mpfb_finger}_0{i + 1}_{side}'

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{'  (' + detail + ')' if detail else ''}")


def set_custom_names(custom):
    # Same as load_detection_lists, but with the given custom names instead of the user's saved ones
    detection_manager.bone_detection_list_custom = custom
    detection_manager.bone_detection_list = detection_manager.combine_lists(
        detection_manager.bone_detection_list_unmodified, custom)


def auto_detect(armature):
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.rsl.detect_actor_bones()
    return {key: getattr(armature, 'rsl_actor_' + key) for key in bone_keys}


def diff(got, expected):
    return {key: (got.get(key, ''), expected.get(key, '')) for key in bone_keys if got.get(key, '') != expected.get(key, '')}


# --- Scene: Newton armature from the example file and an MPFB rig built from its bone names ---
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(newton_blend)) as (data_from, data_to):
    data_to.objects = [name for name in data_from.objects if name == 'Root']
newton = data_to.objects[0]
bpy.context.scene.collection.objects.link(newton)
newton_saved = {key: getattr(newton, 'rsl_actor_' + key) for key in bone_keys}

mpfb = bpy.data.objects.new("MPFB", bpy.data.armatures.new("MPFB"))
bpy.context.scene.collection.objects.link(mpfb)
bpy.context.view_layer.objects.active = mpfb
bpy.ops.object.mode_set(mode='EDIT')
for i, (name, parent) in enumerate(MPFB_BONES):
    bone = mpfb.data.edit_bones.new(name)
    bone.head = (0, 0, i * 0.1)
    bone.tail = (0, 0.05, i * 0.1)
    if parent:
        bone.parent = mpfb.data.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT')

print(f"\nBlender {bpy.app.version_string}")

# --- Without custom names: same result as before ---
print("Without custom names:")
set_custom_names({})
got = auto_detect(newton)
check("Newton gets the mapping saved in Newton Static.blend", not diff(got, newton_saved), str(diff(got, newton_saved)))
got = auto_detect(mpfb)
check("MPFB gets the same mapping as before", not diff(got, MPFB_EXPECTED), str(diff(got, MPFB_EXPECTED)))

# --- Custom names win over default matches (reviewer's case) ---
print("With the custom name spine -> Hips:")
set_custom_names({'spine': ['hips']})
got = auto_detect(newton)
check("spine gets Hips", got['spine'] == 'Hips', f"spine: '{got['spine']}'")
others = [key for key, bone in got.items() if bone == 'Hips' and key not in ('spine', 'chest')]
check("no other key gets Hips", not others, str(others))
changed = {key for key in diff(got, newton_saved)} - {'hip', 'spine', 'chest'}
check("keys other than hip, spine and chest keep their default bones", not changed, str({k: (got[k], newton_saved[k]) for k in changed}))

failures = results.count(False)
print(f"\nRESULT: {'FAILED' if failures else 'PASSED'} ({failures} of {len(results)} checks failed)")
sys.exit(1 if failures else 0)
