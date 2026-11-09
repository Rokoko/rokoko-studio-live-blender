# Streams fake JSON v3 frames through the real animate_actor and checks that the character walks
# along its own facing direction without vertical drift, also when the armature, a parent or the
# hip bone's rest orientation is rotated. Also checks that a forward lean follows the character.
# Exits with code 1 on failure.
#
# Run from the repo root in background Blender (the FBX and MPFB files are optional, their cases are skipped without them):
#   blender -b --factory-startup --python-exit-code 1 --python tests/test_hip_walk_direction.py -- . <newton.fbx> <mpfb.blend>
import bpy
import importlib.util
import math
import pathlib
import sys
from mathutils import Quaternion, Vector

args = sys.argv[sys.argv.index("--") + 1:]
addon_dir = pathlib.Path(args[0]).resolve()
newton_fbx = pathlib.Path(args[1]) if len(args) > 1 else None
mpfb_blend = pathlib.Path(args[2]) if len(args) > 2 else None
newton_blend = pathlib.Path(__file__).resolve().parent.parent / "resources" / "models" / "Newton Static.blend"

# Import the add-on as a package (its folder name has dashes) and register only what the test needs
spec = importlib.util.spec_from_file_location("rsl_under_test", addon_dir / "__init__.py",
                                              submodule_search_locations=[str(addon_dir)])
rsl = importlib.util.module_from_spec(spec)
sys.modules["rsl_under_test"] = rsl
spec.loader.exec_module(rsl)
bpy.utils.register_class(rsl.panels.retargeting.BoneListItem)  # Needed by a scene property
rsl.properties.register()
rsl.core.detection_manager.load_detection_lists()
bpy.utils.register_class(rsl.operators.detector.DetectActorBones)
bpy.utils.register_class(rsl.operators.actor.InitTPose)

animations = rsl.core.animations
reference_rots = rsl.core.animation_lists.get_bones(with_gloves=False)

HIP_HEIGHT = 1.0
LEAN = Quaternion((1, 0, 0), math.radians(30))  # Studio space: rotation around the actor's right axis


def send_frame(obj, position=(0, HIP_HEIGHT, 0), delta=Quaternion()):
    body = {}
    for bone_name, ref_rot in reference_rots.items():
        rot = delta @ ref_rot
        body[bone_name] = {'rotation': {'w': rot.w, 'x': rot.x, 'y': rot.y, 'z': rot.z},
                           'position': {'x': position[0], 'y': position[1], 'z': position[2]}}
    animations.live_data.version = 3
    animations.live_data.actors = [{'name': 'TestActor', 'meta': {'hasGloves': False, 'hasFace': False},
                                    'dimensions': {'hipHeight': HIP_HEIGHT}, 'body': body}]
    obj.rsl_animations_actors = 'TestActor'
    # Bone matrices depend on their parents, so let the pose settle like it does over several live frames
    for _ in range(3):
        animate_actor_and_update(obj)


def animate_actor_and_update(obj):
    animations.animate_actor(obj)
    bpy.context.view_layer.update()


def world_head(obj, key):
    return obj.matrix_world @ obj.pose.bones[getattr(obj, 'rsl_actor_' + key)].head


def flat(v):
    return Vector((v.x, v.y, 0))


def angle_deg(a, b):
    return math.degrees(flat(a).angle(flat(b)))


def setup(obj, set_tpose):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.rsl.detect_actor_bones()
    if set_tpose:
        bpy.ops.rsl.init_tpose()


def load_newton_blend():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(newton_blend)) as (data_from, data_to):
        data_to.objects = list(data_from.objects)
    for obj in data_to.objects:
        bpy.context.scene.collection.objects.link(obj)
    obj = next(o for o in data_to.objects if o.type == 'ARMATURE')
    setup(obj, set_tpose=False)  # The example file comes with its T-pose
    return obj


def load_newton_fbx():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(newton_fbx))
    obj = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    setup(obj, set_tpose=True)
    return obj


def load_mpfb():
    bpy.ops.wm.open_mainfile(filepath=str(mpfb_blend))
    obj = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    setup(obj, set_tpose=True)
    return obj


def rotate_z(obj, degrees):
    obj.rotation_euler.z += math.radians(degrees)
    bpy.context.view_layer.update()
    return obj


def parent_to_rotated_empty(obj, degrees):
    empty = bpy.data.objects.new("RotatedParent", None)
    bpy.context.scene.collection.objects.link(empty)
    empty.rotation_euler.z = math.radians(degrees)
    obj.parent = empty
    bpy.context.view_layer.update()
    return obj


def measure(obj):
    send_frame(obj)
    hip0, head0 = world_head(obj, 'hip'), world_head(obj, 'head')
    left = world_head(obj, 'leftUpLeg') - world_head(obj, 'rightUpLeg')
    facing = flat(left).cross(Vector((0, 0, 1)))  # A character facing -Y has its left side at +X

    send_frame(obj, position=(0, HIP_HEIGHT, 1))  # One metre forward
    walk = world_head(obj, 'hip') - hip0
    send_frame(obj, position=(1, HIP_HEIGHT, 0))  # One metre to the actor's right
    side = world_head(obj, 'hip') - hip0
    send_frame(obj, delta=LEAN)
    lean = world_head(obj, 'head') - head0

    return {
        'walk': angle_deg(walk, facing),
        'side': angle_deg(side, -left),
        'drift': max(abs(walk.z) / flat(walk).length, abs(side.z) / flat(side).length),
        'lean': angle_deg(lean, facing),
    }


cases = [("Newton Static.blend", load_newton_blend)]
if newton_fbx:
    cases.append(("Newton FBX with its parent", load_newton_fbx))
cases += [("Newton armature rotated 90 on Z", lambda: rotate_z(load_newton_blend(), 90)),
          ("Newton parented to empty rotated 45 on Z", lambda: parent_to_rotated_empty(load_newton_blend(), 45))]
if mpfb_blend:
    cases += [("MPFB", load_mpfb),
              ("MPFB rotated 90 on Z", lambda: rotate_z(load_mpfb(), 90))]

failures = 0
print(f"\n{'Case':42} {'walk vs facing':>15} {'side vs right':>14} {'vertical m/m':>13} {'lean vs facing':>15}")
for name, load in cases:
    r = measure(load())
    ok = r['walk'] < 1 and r['side'] < 1 and r['drift'] < 0.01 and r['lean'] < 1
    failures += not ok
    print(f"{name:42} {r['walk']:14.1f}° {r['side']:13.1f}° {r['drift']:13.3f} {r['lean']:14.1f}°  {'PASS' if ok else 'FAIL'}")

print(f"\nRESULT: {'FAILED' if failures else 'PASSED'} ({failures} of {len(cases)} cases failed)")
sys.exit(1 if failures else 0)
