# Records fake frames through the real recorder onto Newton Static.blend (body), Newton_HeadFace (face shape keys)
# and a simple prop, stops recording and checks with frame_set that the recording plays back: each checked frame
# shows the values that were recorded for it, and the first and last frames differ.
# Also checks get_fcurves_from_action on an action with two slots, an action without slots and a slot without curves.
# Exits with code 1 on failure.
#
# Run from the repo root in background Blender:
#   blender -b --factory-startup --python-exit-code 1 --python tests/test_recording_playback.py -- .
import bpy
import importlib.util
import math
import pathlib
import sys
from mathutils import Quaternion

# The example file only opens from Blender 4.2 on
if bpy.app.version < (4, 2, 0):
    print(f"Blender {bpy.app.version_string}: skipped: needs Blender 4.2+")
    sys.exit(0)

args = sys.argv[sys.argv.index("--") + 1:]
addon_dir = pathlib.Path(args[0]).resolve()

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

animations = rsl.core.animations
utils = rsl.core.utils
reference_rots = rsl.core.animation_lists.get_bones(with_gloves=False)
FRAMES = 5
HAS_SLOTS = bpy.app.version >= (4, 4, 0)

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{'  (' + detail + ')' if detail else ''}")


def close(a, b, tol=1e-3):
    return all(abs(x - y) < tol for x, y in zip(a, b))


# --- Scene: Newton armature and face from the example file, plus a cube as prop ---
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(newton_blend)) as (data_from, data_to):
    data_to.objects = list(data_from.objects)
for obj in data_to.objects:
    bpy.context.scene.collection.objects.link(obj)
armature = next(o for o in data_to.objects if o.type == 'ARMATURE')
face = bpy.data.objects["Newton_HeadFace"]
prop_mesh = bpy.data.meshes.new("PropMesh")
prop = bpy.data.objects.new("TestPropObj", prop_mesh)
bpy.context.scene.collection.objects.link(prop)

bpy.context.view_layer.objects.active = armature
armature.select_set(True)
bpy.ops.rsl.detect_actor_bones()
for shape in rsl.core.animation_lists.face_shapes:
    setattr(face, 'rsl_face_' + shape, rsl.core.detection_manager.detect_shape(face, shape))

body_bone = armature.rsl_actor_leftUpLeg  # A bone that the recorder keys with its rotation
face_shape_key = face.rsl_face_jawOpen


def set_live_frame(i):
    t = i / FRAMES
    delta = Quaternion((1, 0, 0), math.radians(40 * t))
    body = {}
    for bone_name, ref_rot in reference_rots.items():
        rot = delta @ ref_rot
        body[bone_name] = {'rotation': {'w': rot.w, 'x': rot.x, 'y': rot.y, 'z': rot.z},
                           'position': {'x': 0, 'y': 1, 'z': 0.2 * t}}
    face_data = {shape: 80 * t for shape in rsl.core.animation_lists.face_shapes}
    face_data['parentName'] = 'TestActor'
    prop_rot = Quaternion((0, 1, 0), math.radians(60 * t))

    ld = animations.live_data
    ld.version = 3
    ld.timestamp = i / bpy.context.scene.rsl_receiver_fps  # One live frame per scene frame
    ld.actors = [{'name': 'TestActor', 'meta': {'hasGloves': False, 'hasFace': True},
                  'dimensions': {'hipHeight': 1.0}, 'body': body}]
    ld.faces = [face_data]
    ld.props = [{'name': 'TestProp',
                 'position': {'x': 0.5 * t, 'y': 1, 'z': 0},
                 'rotation': {'w': prop_rot.w, 'x': prop_rot.x, 'y': prop_rot.y, 'z': prop_rot.z}}]


# Assign actor, face and prop (the enums read their items from the live data)
set_live_frame(0)
armature.rsl_animations_actors = 'TestActor'
face.rsl_animations_faces = 'TestActor'
prop.rsl_animations_props_trackers = 'TestProp'


# --- Record through the real recorder ---
def read_state():
    return {
        'body': tuple(armature.pose.bones[body_bone].rotation_euler),
        'face': (face.data.shape_keys.key_blocks[face_shape_key].value,),
        'prop': tuple(prop.location) + tuple(prop.rotation_quaternion),
    }


bpy.context.scene.rsl_recording = True  # Calls start_recorder through the property update
recorded = []
for i in range(FRAMES):
    set_live_frame(i)
    animations.animate_actor(armature)
    animations.animate_face(face)
    animations.animate_tracker_prop(prop)
    recorded.append(read_state())
bpy.context.scene.rsl_recording = False  # Calls stop_recorder, which writes the actions

# --- Playback ---
print(f"\nBlender {bpy.app.version_string}")
print("Recording playback:")
targets = {'body': armature, 'face': face, 'prop': prop}
for key, obj in targets.items():
    ad = obj.animation_data
    action = ad.action if ad else None
    check(f"{key}: object has the recorded action", action is not None, action.name if action else "no action")
    if HAS_SLOTS and action:
        check(f"{key}: a slot of the action is assigned", ad.action_slot is not None,
              f"slots: {[s.identifier for s in action.slots]}, assigned: {ad.action_slot.identifier if ad.action_slot else None}")

    shown = []
    for frame in (0, FRAMES - 1):
        bpy.context.scene.frame_set(frame)
        shown.append(read_state()[key])
    check(f"{key}: frame 0 shows the first recorded values", close(shown[0], recorded[0][key]),
          f"shown {[round(v, 3) for v in shown[0]]}, recorded {[round(v, 3) for v in recorded[0][key]]}")
    check(f"{key}: frame {FRAMES - 1} shows the last recorded values", close(shown[1], recorded[-1][key]),
          f"shown {[round(v, 3) for v in shown[1]]}, recorded {[round(v, 3) for v in recorded[-1][key]]}")
    check(f"{key}: first and last frames differ", not close(shown[0], shown[1]))


# --- get_fcurves_from_action edge cases ---
def run(name, fn):
    try:
        fn()
    except Exception as e:
        check(name, False, f"{type(e).__name__}: {e}")


def multi_slot():
    # One action with a mesh object's slot first and the armature's slot second
    mesh_obj = bpy.data.objects.new("SlotMesh", bpy.data.meshes.new("SlotMesh"))
    bpy.context.scene.collection.objects.link(mesh_obj)
    arm = bpy.data.objects.new("SlotArm", bpy.data.armatures.new("SlotArm"))
    bpy.context.scene.collection.objects.link(arm)
    action = bpy.data.actions.new("MultiSlot")
    for obj, path in ((mesh_obj, 'location'), (arm, 'pose.bones["hip"].rotation_euler')):
        ad = obj.animation_data_create()
        ad.action = action
        ad.action_slot = action.slots.new(id_type='OBJECT', name=obj.name)
        if not action.layers:  # Layer and strip API works from 4.4 on, unlike anim_utils' channelbag helpers (5.0)
            action.layers.new("Layer").strips.new(type='KEYFRAME')
        bag = action.layers[0].strips[0].channelbag(ad.action_slot, ensure=True)
        bag.fcurves.new(path, index=0)
    paths = [fc.data_path for fc in utils.get_fcurves_from_action(action, obj=arm)]
    check("two slots: returns the armature's curves for the armature", paths == ['pose.bones["hip"].rotation_euler'], str(paths))
    paths = [fc.data_path for fc in utils.get_fcurves_from_action(action, obj=mesh_obj)]
    check("two slots: returns the mesh's curves for the mesh", paths == ['location'], str(paths))


def check_empty(name, action, obj):
    fcurves = utils.get_fcurves_from_action(action, obj=obj)
    check(f"{name}: returns no curves", len(list(fcurves)) == 0)
    check(f"{name}: find() works and finds nothing", fcurves.find('location', index=0) is None)


def no_slots():
    action = bpy.data.actions.new("NoSlots")
    armature.animation_data.action = action
    check_empty("action without slots", action, armature)


def slot_without_curves():
    action = bpy.data.actions.new("EmptySlot")
    armature.animation_data.action = action
    armature.animation_data.action_slot = action.slots.new(id_type='OBJECT', name=armature.name)
    check_empty("slot without curves", action, armature)


print("get_fcurves_from_action:")
if HAS_SLOTS:
    run("two slots", multi_slot)
    run("action without slots", no_slots)
    run("slot without curves", slot_without_curves)
else:
    run("action without curves", no_slots)

failures = results.count(False)
print(f"\nRESULT: {'FAILED' if failures else 'PASSED'} ({failures} of {len(results)} checks failed)")
sys.exit(1 if failures else 0)
