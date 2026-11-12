# Reproduction test for Add Example Actor deleting user collections.
# Checks that the operator refuses to run while the receiver is running, that a failing load reports an error and leaves no empty collection,
# that collections without users (and with only a fake user) are left untouched, and that the example actor is still added correctly.
# Exits with code 1 on failure.
#
# Run from the repo root in background Blender:
#   blender -b --factory-startup --python-exit-code 1 --python tests/test_add_example_actor.py -- .
import bpy
import importlib.util
import pathlib
import sys

# The example file only opens from Blender 4.2 on
if bpy.app.version < (4, 2, 0):
    print(f"Blender {bpy.app.version_string}: skipped: needs Blender 4.2+")
    sys.exit(0)

addon_dir = pathlib.Path(sys.argv[sys.argv.index("--") + 1])

# Import the add-on as a package (its folder name has dashes) and register only the operator under test
spec = importlib.util.spec_from_file_location("rsl_under_test", addon_dir / "__init__.py",
                                              submodule_search_locations=[str(addon_dir)])
rsl = importlib.util.module_from_spec(spec)
sys.modules["rsl_under_test"] = rsl
spec.loader.exec_module(rsl)
bpy.utils.register_class(rsl.operators.actor.AddExampleActor)

failures = []


def check(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    if not cond:
        failures.append(msg)


# 0. While the receiver is running, the operator must refuse and import nothing
receiver = rsl.operators.receiver
receiver.receiver_enabled = True
objects_before_guard = len(bpy.data.objects)
try:
    guard_result = bpy.ops.rsl.add_example_actor()
    guard_error = ''
except RuntimeError as e:  # An operator that reports an error raises when called from Python
    guard_result = {'CANCELLED'}
    guard_error = str(e)
receiver.receiver_enabled = False
print(f"\nWith receiver running: {guard_result} {guard_error.strip()}")
check(guard_result == {'CANCELLED'} and 'Stop the receiver first' in guard_error,
      "Add Example Actor is refused with 'Stop the receiver first' while the receiver runs")
check(len(bpy.data.objects) == objects_before_guard and not bpy.data.collections.get("Rokoko Streaming Example"),
      "Nothing was imported while the receiver runs")

# 0b. If the example file can't be loaded, the operator reports an error and leaves no empty collection behind
example_file = rsl.core.utils.NEWTON_BLEND_FILE
rsl.core.utils.NEWTON_BLEND_FILE = example_file.with_name("missing example file.blend")
collections_before_fail = set(bpy.data.collections)
try:
    fail_result = bpy.ops.rsl.add_example_actor()
    fail_error = ''
except RuntimeError as e:
    fail_result = {'CANCELLED'}
    fail_error = str(e)
rsl.core.utils.NEWTON_BLEND_FILE = example_file
print(f"\nWith a missing example file: {fail_result} {fail_error.strip()}")
check(fail_result == {'CANCELLED'} and 'Could not load the example actor' in fail_error,
      "A failing load is reported with 'Could not load the example actor'")
new_after_fail = set(bpy.data.collections) - collections_before_fail
check(not new_after_fail, f"No collection is left behind after a failing load (new: {sorted(c.name for c in new_after_fail)})")


def make_collection(name):
    col = bpy.data.collections.new(name)
    obj = bpy.data.objects.new(name + "_Obj", None)
    col.objects.link(obj)
    return col


# 1. A user collection that was linked to the scene and later unlinked -> zero users
orphan = make_collection("UserOrphan")
bpy.context.scene.collection.children.link(orphan)
bpy.context.scene.collection.children.unlink(orphan)

# 2. A user collection kept only by a fake user
fake = make_collection("UserFake")
fake.use_fake_user = True

print(f"\nBefore: UserOrphan users={orphan.users}, UserFake users={fake.users}")
collections_before = set(bpy.data.collections)
objects_before = set(bpy.data.objects)

# Names of everything inside the example file, to verify the actor still arrives complete
with bpy.data.libraries.load(str(rsl.core.utils.NEWTON_BLEND_FILE)) as (data_from, _):
    example_obj_names = set(data_from.objects)

# Run the real operator
result = bpy.ops.rsl.add_example_actor()
print(f"Operator result: {result}\n")

# --- User data must be untouched ---
orphan = bpy.data.collections.get("UserOrphan")
check(orphan is not None, "UserOrphan collection still exists")
if orphan:
    check(orphan.users == 0, f"UserOrphan still has 0 users (has {orphan.users})")
    check([o.name for o in orphan.objects] == ["UserOrphan_Obj"], "UserOrphan still contains UserOrphan_Obj")

fake = bpy.data.collections.get("UserFake")
check(fake is not None, "UserFake collection still exists")
if fake:
    check(fake.use_fake_user and fake.users == 1, f"UserFake still only has its fake user (users={fake.users})")
    check([o.name for o in fake.objects] == ["UserFake_Obj"], "UserFake still contains UserFake_Obj")

for name in ("UserOrphan_Obj", "UserFake_Obj"):
    obj = bpy.data.objects.get(name)
    check(obj is not None and obj.parent is None, f"{name} still exists and was not reparented")

# --- Example actor must still be added correctly ---
example = bpy.data.collections.get("Rokoko Streaming Example")
check(example is not None, "'Rokoko Streaming Example' collection exists")
if example:
    check(example.name in bpy.context.scene.collection.children, "Example collection is linked to the scene")
    check(len(example.children) == 0, f"Example collection has no leftover child collections ({len(example.children)})")
    example_names = {o.name for o in example.objects}
    check(example_names == example_obj_names,
          f"Example collection holds exactly the {len(example_obj_names)} objects from the file (got {len(example_names)})")
    check(not (example_names & {"UserOrphan_Obj", "UserFake_Obj"}), "No user objects ended up in the example collection")
    check(bpy.context.view_layer.objects.active is not None
          and bpy.context.view_layer.objects.active.name == "Root", "Example root object 'Root' is active")

new_collections = set(bpy.data.collections) - collections_before
check({c.name for c in new_collections} == {"Rokoko Streaming Example"},
      f"Only the example collection was added to bpy.data (new: {sorted(c.name for c in new_collections)})")
check(objects_before <= set(bpy.data.objects), "No pre-existing object was deleted")

print(f"\nRESULT: {'FAILED' if failures else 'PASSED'} ({len(failures)} failures)")
sys.exit(1 if failures else 0)
