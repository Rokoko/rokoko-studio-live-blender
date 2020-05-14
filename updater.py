import os
import bpy
import ssl
import time
import json
import urllib
import shutil
import pathlib
import zipfile
import addon_utils
from threading import Thread
from bpy.app.handlers import persistent

GITHUB_URL = 'https://api.github.com/repos/RokokoElectronics/rokoko-studio-live-blender/releases'
GITHUB_URL_BETA = 'https://github.com/RokokoElectronics/rokoko-studio-live-blender/archive/beta.zip'

no_ver_check = False
fake_update = False

version_list = []
is_checking_for_update = False
checked_on_startup = False
current_version = []
current_version_str = ''
update_needed = False
latest_version = None
latest_version_str = ''
used_updater_panel = False
update_finished = False
remind_me_later = False
is_ignored_version = False

confirm_update_to = ''

show_error = ''

main_dir = os.path.dirname(__file__)
downloads_dir = os.path.join(main_dir, "downloads")
resources_dir = os.path.join(main_dir, "resources")
ignore_ver_file = os.path.join(resources_dir, "ignore_version.txt")
no_auto_ver_check_file = os.path.join(resources_dir, "no_auto_ver_check.txt")

# Get package name, important for panel in user preferences
package_name = ''
for mod in addon_utils.modules():
    if mod.bl_info['name'] == 'Rokoko Studio Live for Blender':
        package_name = mod.__name__


class Version:
    def __init__(self, data):
        # Set version string
        version_string = data.get('tag_name').lower().replace('-', '.').replace('_', '.')
        if version_string.startswith('v.'):
            version_string = version_string[2:]
        if version_string.startswith('v'):
            version_string = version_string[1:]

        # Set version number
        version_number = []
        for i in version_string.split('.'):
            if i.isdigit():
                version_number.append(int(i))

        # Set version data
        self.version_string = version_string
        self.version_number = version_number
        self.name = data.get('name')
        self.download_link = data.get('zipball_url')
        self.patch_notes = data.get('body')
        self.release_date = data.get('published_at')

        if 'T' in data.get('published_at')[1:]:
            self.release_date = data.get('published_at').split('T')[0]

        # If the name of the release contains "yanked", ignore it
        if 'yanked' in self.name.lower():
            return

        version_list.append(self)


def get_version_by_string(version_string) -> Version:
    for version in version_list:
        if version.version_string == version_string:
            return version


def get_latest_version() -> Version:
    return version_list[0]


def check_for_update_background(check_on_startup=False):
    global is_checking_for_update, checked_on_startup
    if check_on_startup and checked_on_startup:
        # print('ALREADY CHECKED ON STARTUP')
        return
    if is_checking_for_update:
        # print('ALREADY CHECKING')
        return

    checked_on_startup = True

    if check_on_startup and os.path.isfile(no_auto_ver_check_file):
        print('AUTO CHECK DISABLED VIA FILE')
        return

    is_checking_for_update = True

    thread = Thread(target=check_for_update, args=[])
    thread.start()


def check_for_update():
    print('Checking for Rokoko Studio Live update...')

    # Get all releases from Github
    if not get_github_releases():
        finish_update_checking(error='Could not check for updates,'
                                     '\ntry again later.')
        return

    if not version_list:
        finish_update_checking(error='No plugin versions available.')
        return

    # Check if an update is needed
    global update_needed, is_ignored_version
    update_needed = check_for_update_available()
    is_ignored_version = check_ignored_version()

    # Update needed, show the notification popup if it wasn't checked through the UI
    if update_needed:
        print('Update found!')
        if not used_updater_panel and not is_ignored_version:
            prepare_to_show_update_notification()
    else:
        print('No update found.')

    # Finish update checking, update the UI
    finish_update_checking()


def get_github_releases():
    global version_list
    version_list = []

    if fake_update:
        print('FAKE INSTALL!')

        Version({
            'tag_name': 'v-99-99',
            'name': 'v-99-99',
            'zipball_url': '',
            'body': 'Put exiting new stuff here\nOr maybe there is?',
            'published_at': 'Today'
        })

        Version({
            'tag_name': '12.34.56',
            'name': '12.34.56 Test Release',
            'zipball_url': '',
            'body': 'Nothing new to see',
            'published_at': 'A week ago probably'
        })
        return True

    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        with urllib.request.urlopen(GITHUB_URL) as url:
            data = json.loads(url.read().decode())
    except urllib.error.URLError as e:
        print('URL ERROR:', e)
        return False

    if not data:
        if type(data) == list:
            return True
        return False

    for version_data in data:
        Version(version_data)

    return True


def check_for_update_available():
    if not version_list:
        return False

    global latest_version, latest_version_str
    latest_version = get_latest_version().version_number
    latest_version_str = get_latest_version().version_string

    if latest_version > current_version:
        return True


def finish_update_checking(error=''):
    global is_checking_for_update, show_error
    is_checking_for_update = False

    # Only show error if the update panel was used before
    if used_updater_panel:
        show_error = error

    ui_refresh()


def ui_refresh():
    # A way to refresh the ui
    refreshed = False
    while not refreshed:
        if hasattr(bpy.data, 'window_managers'):
            for windowManager in bpy.data.window_managers:
                for window in windowManager.windows:
                    for area in window.screen.areas:
                        area.tag_redraw()
            refreshed = True
            # print('Refreshed UI')
        else:
            time.sleep(0.5)


def get_update_post():
    if hasattr(bpy.app.handlers, 'scene_update_post'):
        return bpy.app.handlers.scene_update_post
    else:
        return bpy.app.handlers.depsgraph_update_post


def prepare_to_show_update_notification():
    return  # TODO: Implement?
    # This is necessary to show a popup directly after startup
    # You will get a nasty error otherwise
    # This will add the function to the scene_update_post and it will be executed every frame. that's why it needs to be removed again asap
    # print('PREPARE TO SHOW UI')
    if show_update_notification not in get_update_post():
        get_update_post().append(show_update_notification)


@persistent
def show_update_notification(scene):  # One argument in necessary for some reason
    # print('SHOWING UI NOW!!!!')

    # # Immediately remove this from handlers again
    if show_update_notification in get_update_post():
        get_update_post().remove(show_update_notification)

    # Show notification popup
    # atr = UpdateNotificationPopup.bl_idname.split(".")
    # getattr(getattr(bpy.ops, atr[0]), atr[1])('INVOKE_DEFAULT')
    bpy.ops.rsl_updater.update_notification_popup('INVOKE_DEFAULT')


def update_now(version=None, latest=False, beta=False):
    if fake_update:
        finish_update()
        return
    if beta:
        print('UPDATE TO BETA')
        update_link = GITHUB_URL_BETA
    elif latest or not version:
        print('UPDATE TO ' + latest_version_str)
        update_link = get_latest_version().download_link
        bpy.context.scene.rsl_updater_version_list = latest_version_str
    else:
        print('UPDATE TO ' + version)
        update_link = get_version_by_string(version).download_link

    download_file(update_link)


def download_file(update_url):
    if not update_url:
        finish_update()
        return

    # Load all the directories and files
    update_zip_file = os.path.join(downloads_dir, "rokoko-update.zip")

    # Remove existing download folder
    if os.path.isdir(downloads_dir):
        print("DOWNLOAD FOLDER EXISTED")
        shutil.rmtree(downloads_dir)

    # Create download folder
    pathlib.Path(downloads_dir).mkdir(exist_ok=True)

    # Download zip
    print('DOWNLOAD FILE')
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        urllib.request.urlretrieve(update_url, update_zip_file)
    except urllib.error.URLError:
        print("FILE COULD NOT BE DOWNLOADED")
        shutil.rmtree(downloads_dir)
        finish_update(error='Could not download update.')
        return
    print('DOWNLOAD FINISHED')

    # If zip is not downloaded, abort
    if not os.path.isfile(update_zip_file):
        print("ZIP NOT FOUND!")
        shutil.rmtree(downloads_dir)
        finish_update(error='Could not find the'
                            '\ndownloaded zip.')
        return

    # Extract the downloaded zip
    print('EXTRACTING ZIP')
    with zipfile.ZipFile(update_zip_file, "r") as zip_ref:
        zip_ref.extractall(downloads_dir)
    print('EXTRACTED')

    # Delete the extracted zip file
    print('REMOVING ZIP FILE')
    os.remove(update_zip_file)

    # Detect the extracted folders and files
    print('SEARCHING FOR INIT 1')

    def search_init(path):
        print('SEARCHING IN ' + path)
        files = os.listdir(path)
        if "__init__.py" in files:
            print('FOUND')
            return path
        folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        if len(folders) != 1:
            print(len(folders), 'FOLDERS DETECTED')
            return None
        print('GOING DEEPER')
        return search_init(os.path.join(path, folders[0]))

    print('SEARCHING FOR INIT 2')
    extracted_zip_dir = search_init(downloads_dir)
    if not extracted_zip_dir:
        print("INIT NOT FOUND!")
        shutil.rmtree(downloads_dir)
        finish_update(error='Could not find Rokoko Studio'
                            '\nLive in the downloaded zip.')
        return

    # Remove old addon files
    clean_addon_dir()

    # Move the extracted files to their correct places
    def move_files(from_dir, to_dir):
        print('MOVE FILES TO DIR:', to_dir)
        files = os.listdir(from_dir)
        for file in files:
            file_dir = os.path.join(from_dir, file)
            target_dir = os.path.join(to_dir, file)
            print('MOVE', file_dir)

            # If file exists
            if os.path.isfile(file_dir) and os.path.isfile(target_dir):
                os.remove(target_dir)
                shutil.move(file_dir, to_dir)
                print('REMOVED AND MOVED', file)

            elif os.path.isdir(file_dir) and os.path.isdir(target_dir):
                move_files(file_dir, target_dir)

            else:
                shutil.move(file_dir, to_dir)
                print('MOVED', file)

    move_files(extracted_zip_dir, main_dir)

    # Delete download folder
    print('DELETE DOWNLOADS DIR')
    shutil.rmtree(downloads_dir)

    # Finish the update
    finish_update()


def finish_update(error=''):
    global update_finished, show_error
    show_error = error

    if not error:
        update_finished = True

    bpy.ops.rsl_updater.update_complete_panel('INVOKE_DEFAULT')
    ui_refresh()
    print("UPDATE DONE!")


def clean_addon_dir():
    print("CLEAN ADDON FOLDER")

    # first remove root files and folders (except update folder, important folders and resource folder)
    files = [f for f in os.listdir(main_dir) if os.path.isfile(os.path.join(main_dir, f))]
    folders = [f for f in os.listdir(main_dir) if os.path.isdir(os.path.join(main_dir, f))]

    for f in files:
        file = os.path.join(main_dir, f)
        try:
            os.remove(file)
            print("Clean removing file {}".format(file))
        except OSError:
            print("Failed to pre-remove file " + file)

    for f in folders:
        folder = os.path.join(main_dir, f)
        if f.startswith('.') or f == 'resources' or f == 'downloads':
            continue

        try:
            shutil.rmtree(folder)
            print("Clean removing folder and contents {}".format(folder))
        except OSError:
            print("Failed to pre-remove folder " + folder)

    # then remove resource files and folders (except settings and google dict)
    resources_folder = os.path.join(main_dir, 'resources')
    files = [f for f in os.listdir(resources_folder) if os.path.isfile(os.path.join(resources_folder, f))]
    folders = [f for f in os.listdir(resources_folder) if os.path.isdir(os.path.join(resources_folder, f))]

    for f in files:
        if f == 'no_auto_ver_check.txt':
            continue

        file = os.path.join(resources_folder, f)
        try:
            os.remove(file)
            print("Clean removing file {}".format(file))
        except OSError:
            print("Failed to pre-remove " + file)

    for f in folders:
        if f == 'custom_bones':
            continue

        folder = os.path.join(resources_folder, f)
        try:
            shutil.rmtree(folder)
            print("Clean removing folder and contents {}".format(folder))
        except OSError:
            print("Failed to pre-remove folder " + folder)


def set_ignored_version():
    # Create resources folder
    pathlib.Path(resources_dir).mkdir(exist_ok=True)

    # Create ignore file
    with open(ignore_ver_file, 'w', encoding="utf8") as outfile:
        outfile.write(latest_version_str)

    # Set ignored status
    global is_ignored_version
    is_ignored_version = True
    print('IGNORE VERSION ' + latest_version_str)


def check_ignored_version():
    if not os.path.isfile(ignore_ver_file):
        # print('IGNORE FILE NOT FOUND')
        return False

    # Read ignore file
    with open(ignore_ver_file, 'r', encoding="utf8") as outfile:
        version = outfile.read()

    # Check if the latest version matches the one in the ignore file
    if latest_version_str == version:
        print('Update ignored.')
        return True

    # Delete ignore version file if the latest version is not the version in the file
    try:
        os.remove(ignore_ver_file)
    except OSError:
        print("FAILED TO REMOVE IGNORE VERSION FILE")

    return False


def get_version_list(self, context):
    choices = []
    for version in version_list:
        choices.append((version.version_string, version.version_string, version.version_string))

    bpy.types.Object.Enum = choices
    return bpy.types.Object.Enum


def get_user_preferences():
    return bpy.context.user_preferences if hasattr(bpy.context, 'user_preferences') else bpy.context.preferences
