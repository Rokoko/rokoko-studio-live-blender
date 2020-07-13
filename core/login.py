import os
import bpy
import ctypes
import pathlib
from ctypes import wintypes

lib = None
show_password = False
show_wrong_auth = False
credentials_updated = True
logged_in_email = ''

main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
resources_dir = os.path.join(main_dir, "resources")
cache_dir = os.path.join(resources_dir, "cache")
libs_dir = os.path.join(resources_dir, "libs")

lib_file = os.path.join(libs_dir, "rokoko-id.dll")
cache_file = os.path.join(cache_dir, ".cache")

classes = []
classes_login = []


def load():
    global lib

    # Add the libs dir to the paths
    if libs_dir not in os.environ['PATH']:
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + libs_dir

    # Create cache folder if it doesn't exist
    if not os.path.isdir(cache_dir):
        os.mkdir(cache_dir)

    # Load in the library
    if not lib:
        print('LIB EXISTS?', os.path.isfile(lib_file), lib_file)
        lib = ctypes.CDLL(lib_file)

    # Set the cache path
    # print('IS FILE', os.path.isfile(cache_file), cache_file)
    lib.setCachePath.argtypes = [ctypes.c_char_p]
    lib.setCachePath(cache_file.encode())


def unload():
    global lib
    if not lib:
        return

    lib.close()

    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel32.FreeLibrary.argtypes = [wintypes.HMODULE]
    kernel32.FreeLibrary(lib._handle)

    lib = None


def login_from_cache(classes_list, classes_login_list):
    global classes, classes_login, logged_in_email
    classes = classes_list
    classes_login = classes_login_list

    try:
        load()
    except OSError as e:
        print(e)
        return

    lib.getCachePath.restype = ctypes.c_char_p
    print("Current cache path:", lib.getCachePath().decode())

    lib.signInCache()

    logged_in = lib.isSignedIn()

    if logged_in:
        try:
            # Store the email of the user
            lib.getEmail.restype = ctypes.c_char_p
            logged_in_email = lib.getEmail().decode()
        except UnicodeDecodeError:
            logged_in_email = 'Not Found'

    unload()

    return logged_in


def login(email, password):
    global show_wrong_auth, credentials_updated
    load()

    # If nothing was changed in the fields, don't try to login in order to reduce spam
    if not credentials_updated:
        return False

    # Check if already signed in
    if lib.isSignedIn():
        print('ALREADY SIGNED IN!')
        register_classes(email)
        return True

    # Sign in with email and password
    lib.signIn.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    result = lib.signIn(email.encode(), password.encode())
    print('RESULT', result)

    if result == 0:
        register_classes(email)
        show_wrong_auth = False
        return True

    show_wrong_auth = True
    credentials_updated = False
    return False


def logout():
    load()
    lib.signOut()
    unload()
    unregister_classes()


def register_classes(email):
    try:
        # Store the email of the user
        global logged_in_email
        lib.getEmail.restype = ctypes.c_char_p
        logged_in_email = lib.getEmail().decode()
    except UnicodeDecodeError:
        logged_in_email = email

    # Unload the library
    unload()

    # Reset the credentials, so they won't get saved
    bpy.context.scene.rsl_login_email = ''
    bpy.context.scene.rsl_login_password = ''
    bpy.context.scene.rsl_login_password_shown = ''

    # Unregister login classes
    for cls in reversed(classes_login):
        bpy.utils.unregister_class(cls)

    # Register normal classes
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister_classes():
    global logged_in_email
    logged_in_email = ''

    # Unregister login classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # Register normal classes
    for cls in classes_login:
        bpy.utils.register_class(cls)


def credentials_update(self, context):
    global credentials_updated
    credentials_updated = True
