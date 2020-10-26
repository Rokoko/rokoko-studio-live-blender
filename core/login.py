import os
import bpy
import ctypes
import pathlib
import platform
import requests
from threading import Thread


if platform.system() == "Windows":
    from ctypes import wintypes

lib = None
show_password = False
credentials_updated = True
logged_in_email = ''

error_show_wrong_auth = False
error_show_no_connection = False

main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
resources_dir = os.path.join(main_dir, "resources")
cache_dir = os.path.join(resources_dir, "cache")
libs_dir = os.path.join(resources_dir, "libs")

cache_file = os.path.join(cache_dir, ".cache")

if platform.system() == "Windows":
    os_libs_dir = os.path.join(libs_dir, "win")
    lib_file = os.path.join(os_libs_dir, "rokoko-id.dll")
elif platform.system() == "Darwin":
    os_libs_dir = os.path.join(libs_dir, "mac")
    lib_file = os.path.join(os_libs_dir, "librokoko-id.dylib")
else:
    os_libs_dir = os.path.join(libs_dir, "linux")
    lib_file = os.path.join(os_libs_dir, "librokoko-id.so")

classes = []
classes_login = []


def load():
    global lib

    # Add the libs dir to the paths
    if os_libs_dir not in os.environ['PATH']:
        # print("ADDED")
        os.environ['PATH'] = os_libs_dir + os.pathsep + os.environ['PATH']

    # Create cache folder if it doesn't exist
    if not os.path.isdir(cache_dir):
        os.mkdir(cache_dir)

    # Load in the library
    if not lib:
        # print()
        # print('LIB EXISTS 1?', os.path.isfile(lib_file), lib_file)
        # print('LIB EXISTS 2?', os.path.isfile(lib_file.replace("\\", "/")), lib_file.replace("\\", "/"))
        # print('ENVIRONMENT:', os.environ['PATH'])
        # path = os.environ['PATH'].split(os.pathsep)[0]
        # print('DLLs:', os.listdir(path))
        # print()

        # print(1, os.getcwd())
        # os.chdir(os_libs_dir)
        # print(2, os.getcwd())
        # print(3, os_libs_dir)
        # print(4, lib_file)

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

    if platform.system() == "Windows":
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

    # lib.getCachePath.restype = ctypes.c_char_p
    # print("Current cache path:", lib.getCachePath(), lib.getCachePath().decode())

    # Check if the cache file is valid. If it isn't, try getting a new access token.
    logged_in = lib.readCache()
    if not logged_in:
        logged_in = lib.signInCache()
        if logged_in:
            store_email()
        unload()
        return logged_in

    store_email()

    # Update the access token in the background, since it isn't needed for the login process
    thread = Thread(target=update_cache_token_async, args=[])
    thread.start()

    return logged_in


def login(email, password):
    global error_show_wrong_auth, error_show_no_connection, credentials_updated
    load()

    # If nothing was changed in the fields, don't try to login in order to reduce spam
    if not credentials_updated:
        return False

    # Check if already signed in
    if lib.isSignedIn():
        print('ALREADY SIGNED IN!')
        register_classes()
        return True

    # Sign in with email and password
    lib.signIn.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    logged_in = lib.signIn(email.encode(), password.encode())

    if logged_in:
        register_classes()
        error_show_wrong_auth = False
        error_show_no_connection = False
        return True

    credentials_updated = False

    # If the login failed, test if Blender has access to the internet
    try:
        _ = requests.get('http://www.rokoko.com/', timeout=5)
    except requests.ConnectionError:
        print("No internet connection available.")
        error_show_no_connection = True
        credentials_updated = True

    error_show_wrong_auth = True
    return False


def logout():
    load()
    lib.signOut()
    unload()
    unregister_classes()


def register_classes():
    store_email()

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


def store_email():
    fallback_email = "Not Found"
    if hasattr(bpy.context, "scene"):
        fallback_email = bpy.context.scene.rsl_login_email

    try:
        # Store the email of the user
        global logged_in_email
        lib.getEmail.restype = ctypes.c_char_p
        logged_in_email = lib.getEmail().decode()
    except UnicodeDecodeError:
        logged_in_email = fallback_email


def update_cache_token_async():
    lib.signInCache()
    unload()

