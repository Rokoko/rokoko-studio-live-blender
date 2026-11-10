# Checks when Set as T-Pose and Straighten Arms refuse to run on an armature with T-Pose data (Newton):
# only while the receiver is running and the armature is attached to an actor, since only then does
# the stream overwrite its pose. Exits with code 1 on failure.
#
# Run from the repo root in background Blender:
#   blender -b --factory-startup --python-exit-code 1 --python tests/test_pose_guard.py -- .
import bpy
import importlib.util
import pathlib
import sys

addon_dir = pathlib.Path(sys.argv[sys.argv.index("--") + 1]).resolve()
newton_blend = addon_dir / "resources" / "models" / "Newton Static.blend"

# Import the add-on as a package (its folder name has dashes) and register only what the test needs
spec = importlib.util.spec_from_file_location("rsl_under_test", addon_dir / "__init__.py",
                                              submodule_search_locations=[str(addon_dir)])
rsl = importlib.util.module_from_spec(spec)
sys.modules["rsl_under_test"] = rsl
spec.loader.exec_module(rsl)
bpy.utils.register_class(rsl.panels.retargeting.BoneListItem)  # Needed by a scene property
rsl.properties.register()
bpy.utils.register_class(rsl.operators.actor.InitTPose)
bpy.utils.register_class(rsl.operators.actor.StraightenArms)

receiver = rsl.operators.receiver
results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{'  (' + detail + ')' if detail else ''}")


def run(op):
    try:
        return op(), ''
    except RuntimeError as e:  # An operator that reports an error raises when called from Python
        return {'CANCELLED'}, str(e).strip()


# --- Scene: Newton armature, which has T-Pose data, and one actor in the live data ---
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(newton_blend)) as (data_from, data_to):
    data_to.objects = [name for name in data_from.objects if name == 'Root']
armature = data_to.objects[0]
bpy.context.scene.collection.objects.link(armature)
bpy.context.view_layer.objects.active = armature
armature.select_set(True)
rsl.core.animations.live_data.version = 3
rsl.core.animations.live_data.actors = [{'name': 'TestActor', 'meta': {'hasGloves': False, 'hasFace': False}}]

print(f"\nBlender {bpy.app.version_string}")
check("Newton has T-Pose data", bool(armature['CUSTOM'].get('rsl_tpose_bones')))

cases = [
    # receiver running, attached actor, expected to be blocked
    (True, 'None', False),
    (True, 'TestActor', True),
    (False, 'TestActor', False),
]
for receiver_running, actor, blocked in cases:
    receiver.receiver_enabled = receiver_running
    armature.rsl_animations_actors = actor
    situation = f"receiver {'running' if receiver_running else 'stopped'}, actor {actor}"
    for name, op in (("Set as T-Pose", bpy.ops.rsl.init_tpose), ("Straighten Arms", bpy.ops.rsl.straighten_arms)):
        result, error = run(op)
        if blocked:
            check(f"{situation}: {name} is refused", result == {'CANCELLED'} and 'Stop the receiver first' in error, error or str(result))
        else:
            check(f"{situation}: {name} runs", result == {'FINISHED'}, error or str(result))
receiver.receiver_enabled = False

failures = results.count(False)
print(f"\nRESULT: {'FAILED' if failures else 'PASSED'} ({failures} of {len(results)} checks failed)")
sys.exit(1 if failures else 0)
