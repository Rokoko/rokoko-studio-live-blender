import os
import pathlib
from bpy.utils import previews

icons = None

# Path to the icons folder
# The path is calculated relative to this py file inside the addon folder
main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
resources_dir = os.path.join(str(main_dir), "resources")
icons_dir = os.path.join(resources_dir, "icons")


def load_icons():
    pcoll = previews.new()

    # Load a preview thumbnail of a file and store in the previews collection
    pcoll.load('FACE', os.path.join(icons_dir, 'icon-row-face-32.png'), 'IMAGE')
    pcoll.load('SUIT', os.path.join(icons_dir, 'icon-row-suit-32.png'), 'IMAGE')
    pcoll.load('VP', os.path.join(icons_dir, 'icon-vp-32.png'), 'IMAGE')
    pcoll.load('PAIRED', os.path.join(icons_dir, 'icon-paired-32.png'), 'IMAGE')
    pcoll.load('ROKOKO', os.path.join(icons_dir, 'icon-rokoko-32.png'), 'IMAGE')

    global icons
    icons = pcoll


def unload_icons():
    global icons
    previews.remove(icons)


def get_icon(icon_id):
    return icons.get(icon_id).icon_id
