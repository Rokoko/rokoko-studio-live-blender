import os
import bpy
import pathlib

icons = None

# Path to the icons folder
# The path is calculated relative to this py file inside the addon folder
main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
resources_dir = os.path.join(str(main_dir), "resources")
icons_dir = os.path.join(resources_dir, "icons")


def load_icons():
    # Note that preview collections returned by bpy.utils.previews
    # are regular py objects - you can use them to store custom data.
    pcoll = bpy.utils.previews.new()

    # Load a preview thumbnail of a file and store in the previews collection
    pcoll.load('FACE', os.path.join(icons_dir, 'icon-row-face-32.png'), 'IMAGE')
    pcoll.load('SUIT', os.path.join(icons_dir, 'icon-row-suit-32.png'), 'IMAGE')
    pcoll.load('VP', os.path.join(icons_dir, 'icon-vp-32.png'), 'IMAGE')
    pcoll.load('PAIRED', os.path.join(icons_dir, 'icon-paired-32.png'), 'IMAGE')

    global icons
    icons = pcoll


def unload_icons():
    global icons
    bpy.utils.previews.remove(icons)


def get_icon(icon_id):
    return icons.get(icon_id).icon_id
