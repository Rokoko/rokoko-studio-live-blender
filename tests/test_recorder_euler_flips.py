# Records a bone that tumbles fast around all three axes through the real recorder (pose bone matrix set like
# animate_actor does, record_bone, stop_recorder) and plays it back. Checks that each keyed frame shows the
# recorded rotation and that no in-between frame turns further from its two neighbouring keys than the motion
# between those keys, so the recording never flips between the two Euler sets of one rotation.
# Exits with code 1 on failure.
#
# Run from the repo root in background Blender:
#   blender -b --factory-startup --python-exit-code 1 --python tests/test_recorder_euler_flips.py -- .
import bpy
import importlib.util
import math
import pathlib
import sys
from mathutils import Matrix, Quaternion

args = sys.argv[sys.argv.index("--") + 1:]
addon_dir = pathlib.Path(args[0]).resolve()

# Import the add-on as a package (its folder name has dashes) and register only what the test needs
spec = importlib.util.spec_from_file_location("rsl_under_test", addon_dir / "__init__.py",
                                              submodule_search_locations=[str(addon_dir)])
rsl = importlib.util.module_from_spec(spec)
sys.modules["rsl_under_test"] = rsl
spec.loader.exec_module(rsl)
bpy.utils.register_class(rsl.panels.retargeting.BoneListItem)  # Needed by a scene property
rsl.properties.register()

recorder = rsl.core.recorder
FRAMES = 120
STEP = (math.radians(17), math.radians(23), math.radians(29))  # Turn per frame around X, Y and Z

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{'  (' + detail + ')' if detail else ''}")


def angle(a, b):
    # Angle between two rotations, ignoring the sign of the quaternion (atan2 stays precise for small angles, acos does not)
    d = a.conjugated() @ b
    return 2 * math.atan2(math.sqrt(d.x ** 2 + d.y ** 2 + d.z ** 2), abs(d.w))


# --- Scene: an armature with one bone ---
bpy.ops.wm.read_factory_settings(use_empty=True)
arm_data = bpy.data.armatures.new("TumbleArm")
armature = bpy.data.objects.new("TumbleArm", arm_data)
bpy.context.scene.collection.objects.link(armature)
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='EDIT')
edit_bone = arm_data.edit_bones.new("bone")
edit_bone.head = (0, 0, 0)
edit_bone.tail = (0, 0, 1)
bpy.ops.object.mode_set(mode='OBJECT')
pose_bone = armature.pose.bones["bone"]
pose_bone.rotation_mode = 'XYZ'


def tumble(i):
    return (Quaternion((1, 0, 0), STEP[0] * i)
            @ Quaternion((0, 1, 0), STEP[1] * i)
            @ Quaternion((0, 0, 1), STEP[2] * i))


def shown_rotation():
    return pose_bone.rotation_euler.to_quaternion()


# --- Record through the real recorder ---
fps = bpy.context.scene.rsl_receiver_fps
bpy.context.scene.rsl_recording = True
recorded = []
for i in range(FRAMES):
    pose_bone.matrix = tumble(i).to_matrix().to_4x4()  # Blender picks the Euler set, like in animate_actor
    bpy.context.view_layer.update()
    recorder.record_bone(i / fps, armature.name, "bone", pose_bone.rotation_euler)
    recorded.append(shown_rotation())
bpy.context.scene.rsl_recording = False  # Calls stop_recorder, which writes the action

# --- Playback ---
print(f"\nBlender {bpy.app.version_string}")
print("Recorder Euler flips:")
scene = bpy.context.scene
keys = []
worst_key = 0
for i in range(FRAMES):
    scene.frame_set(i)
    keys.append(shown_rotation())
    worst_key = max(worst_key, angle(keys[i], recorded[i]))
check("every keyed frame shows the recorded rotation", worst_key < 1e-4, f"worst {math.degrees(worst_key):.5f} deg")

bad = []
for i in range(FRAMES - 1):
    step = angle(keys[i], keys[i + 1])
    for sub in (0.25, 0.5, 0.75):
        scene.frame_set(i, subframe=sub)
        mid = shown_rotation()
        jump = max(angle(mid, keys[i]), angle(mid, keys[i + 1]))
        if jump > step + 1e-3:
            bad.append(f"frame {i + sub}: {math.degrees(jump):.1f} deg vs {math.degrees(step):.1f} between keys")
check("no in-between frame turns more than the motion between its keys", not bad,
      f"{len(bad)} bad, first: {bad[0]}" if bad else "")

failures = results.count(False)
print(f"\nRESULT: {'FAILED' if failures else 'PASSED'} ({failures} of {len(results)} checks failed)")
sys.exit(1 if failures else 0)
