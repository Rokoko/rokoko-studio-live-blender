# Checks retargeting and Save Custom Bones on the example actor:
# - Save Custom Bones right after Auto Detect saves no custom names, and a changed bone is saved.
# - Newton to Newton: Build Bone List uses no target bone twice, Retarget Animation completes,
#   and the target plays back the same pose as the source.
# Uses its own empty custom name lists and doesn't write the custom names file. Exits with code 1 on failure.
#
# Run from the repo root in background Blender:
#   blender -b --factory-startup --python-exit-code 1 --python tests/test_retargeting.py -- .
import bpy
import importlib.util
import math
import pathlib
import sys

# The example file only opens from Blender 4.2 on
if bpy.app.version < (4, 2, 0):
    print(f"Blender {bpy.app.version_string}: skipped: needs Blender 4.2+")
    sys.exit(0)

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
for cls in (rsl.operators.detector.DetectActorBones, rsl.operators.detector.SaveCustomBones,
            rsl.operators.retargeting.BuildBoneList, rsl.operators.retargeting.RetargetAnimation):
    bpy.utils.register_class(cls)

detection_manager = rsl.core.detection_manager
custom_schemes_manager = rsl.core.custom_schemes_manager
utils = rsl.core.utils

# Keep the user's custom names file untouched: the operators only change the custom lists in memory
custom_schemes_manager.save_to_file_and_update = lambda: None
detection_manager.load_detection_lists()
detection_manager.bone_detection_list_custom = {}
detection_manager.bone_detection_list = detection_manager.combine_lists(detection_manager.bone_detection_list_unmodified, {})

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{'  (' + detail + ')' if detail else ''}")


def load_newton():
    with bpy.data.libraries.load(str(newton_blend)) as (data_from, data_to):
        data_to.objects = list(data_from.objects)
    for obj in data_to.objects:
        bpy.context.scene.collection.objects.link(obj)
    return next(o for o in data_to.objects if o.type == 'ARMATURE')


def saved_custom_names():
    return {key: names for key, names in detection_manager.bone_detection_list_custom.items() if names}


# --- Save Custom Bones on the unchanged example actor ---
print("Save Custom Bones:")
bpy.ops.wm.read_factory_settings(use_empty=True)
actor = load_newton()
bpy.context.view_layer.objects.active = actor
bpy.ops.rsl.detect_actor_bones()
bpy.ops.rsl.save_custom_bones()
check("saves no custom names right after Auto Detect", not saved_custom_names(), str(saved_custom_names()))

actor.rsl_actor_leftHand = 'LeftFinger1Metacarpal'
bpy.ops.rsl.save_custom_bones()
saved = saved_custom_names()  # Names are only lowercased when the file is saved and loaded, which this test skips
check("saves only the changed bone", saved == {'leftHand': ['LeftFinger1Metacarpal']}, str(saved))
detection_manager.bone_detection_list_custom = {}
detection_manager.bone_detection_list = detection_manager.combine_lists(detection_manager.bone_detection_list_unmodified, {})

# --- Newton to Newton retargeting ---
print("Retargeting Newton to Newton:")
bpy.ops.wm.read_factory_settings(use_empty=True)
source = load_newton()
target = load_newton()

# Give the source an animation: bend every bone a bit more over frames 1 to 60 and move the hips up
if source.animation_data:
    source.animation_data.action = None
for frame in (1, 30, 60):
    for i, bone in enumerate(source.pose.bones):
        bone.rotation_mode = 'XYZ'
        bone.rotation_euler = (math.radians(frame / 4 + i % 5), 0, 0)
        bone.keyframe_insert('rotation_euler', frame=frame)
    source.pose.bones['Hips'].location = (0, frame / 100, 0)
    source.pose.bones['Hips'].keyframe_insert('location', frame=frame)
source_action_name = source.animation_data.action.name

scene = bpy.context.scene
scene.rsl_retargeting_armature_source = source
scene.rsl_retargeting_armature_target = target
bpy.ops.rsl.build_bone_list()
targets = [item.bone_name_target for item in scene.rsl_retargeting_bone_list if item.bone_name_target]
duplicates = sorted({name for name in targets if targets.count(name) > 1})
check("Build Bone List uses no target bone twice", not duplicates, str(duplicates))
mapped = {item.bone_name_source: item.bone_name_target for item in scene.rsl_retargeting_bone_list if item.bone_name_target}
wrong = {s: t for s, t in mapped.items() if s != t}
check("each source bone maps to the target bone with the same name", not wrong, str(wrong))
check("the arms are mapped", all(mapped.get(name) == name for name in ('LeftShoulder', 'LeftArm', 'RightShoulder', 'RightArm')),
      str({name: mapped.get(name) for name in ('LeftShoulder', 'LeftArm', 'RightShoulder', 'RightArm')}))

try:
    result = bpy.ops.rsl.retarget_animation()
except RuntimeError as e:
    result = str(e)
check("Retarget Animation completes", result == {'FINISHED'}, str(result))

target_action = target.animation_data.action if target.animation_data else None
check("target has the retargeted action", target_action is not None and target_action.name == source_action_name + ' Retarget',
      target_action.name if target_action else 'no action')
if hasattr(target.animation_data, 'action_slot'):
    check("a slot is assigned to the target (Blender 4.4+)", target.animation_data.action_slot is not None)
fcurves = utils.get_fcurves_from_action(target_action, target) if target_action else []
check("the target action has F-curves", len(fcurves) > 0, f"{len(fcurves)} F-curves")


def local_rotation(armature, bone_name):
    # The bone's own animated rotation. Both armatures are the same rig, so these must match after retargeting.
    # (Armature space matrices don't refresh after frame_set in a background script, so they can't be compared here)
    return armature.pose.bones[bone_name].matrix_basis.to_quaternion()


def angle_between(rot_a, rot_b):
    # q and -q are the same rotation, so take the shorter way round
    angle = math.degrees(rot_a.rotation_difference(rot_b).angle)
    return min(angle, 360 - angle)


def chain_mapped(bone):
    # Retargeting bakes the visual pose, so a bone's own rotation only matches the source if all its parents are retargeted too.
    # Not the case for the finger 2-5 proximals, since Auto Detect leaves the metacarpals empty
    return bone is None or (bone.name in mapped and chain_mapped(bone.parent))


compared = {s: t for s, t in mapped.items() if chain_mapped(source.pose.bones[s])}


def max_pose_difference(frame):
    # Largest rotation difference in degrees between source and target bones
    scene.frame_set(frame)
    return max(angle_between(local_rotation(source, s), local_rotation(target, t)) for s, t in compared.items())


bone = mapped.get('Spine1', next(iter(mapped)))
scene.frame_set(1)
rot_first = local_rotation(target, bone)
scene.frame_set(60)
rot_last = local_rotation(target, bone)
moved = angle_between(rot_first, rot_last)
check(f"the target plays back: {bone} turns between frames 1 and 60", moved > 1, f"{moved:.1f}°")
for frame in (1, 30, 60):
    difference = max_pose_difference(frame)
    check(f"frame {frame}: target pose matches the source", difference < 1, f"{len(compared)} bones, largest difference {difference:.2f}°")

failures = results.count(False)
print(f"\nRESULT: {'FAILED' if failures else 'PASSED'} ({failures} of {len(results)} checks failed)")
sys.exit(1 if failures else 0)
