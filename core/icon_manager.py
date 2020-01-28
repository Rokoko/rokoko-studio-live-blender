import os
import pathlib
from bpy.utils import previews
from enum import Enum

icons = None


class Icons(Enum):
    FACE = 'FACE'
    SUIT = 'SUIT'
    VP = 'VP'
    PAIRED = 'PAIRED'
    ROKOKO = 'ROKOKO'
    START_RECORDING = 'RECORD'
    STOP_RECORDING = 'STOP'
    RESTART = 'RESTART'
    CALIBRATE = 'CALIBRATE'

    def get_icon(self):
        return icons.get(self.value).icon_id


def load_icons():
    # Path to the icons folder
    # The path is calculated relative to this py file inside the addon folder
    main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
    resources_dir = os.path.join(str(main_dir), "resources")
    icons_dir = os.path.join(resources_dir, "icons")

    pcoll = previews.new()

    # Load a preview thumbnail of a file and store in the previews collection
    pcoll.load('FACE', os.path.join(icons_dir, 'icon-row-face-32.png'), 'IMAGE')
    pcoll.load('SUIT', os.path.join(icons_dir, 'icon-row-suit-32.png'), 'IMAGE')
    pcoll.load('VP', os.path.join(icons_dir, 'icon-vp-32.png'), 'IMAGE')
    pcoll.load('PAIRED', os.path.join(icons_dir, 'icon-paired-32.png'), 'IMAGE')
    pcoll.load('ROKOKO', os.path.join(icons_dir, 'icon-rokoko-32.png'), 'IMAGE')
    pcoll.load('RECORD', os.path.join(icons_dir, 'icon-record-32.png'), 'IMAGE')
    pcoll.load('RESTART', os.path.join(icons_dir, 'icon-restart-32.png'), 'IMAGE')
    pcoll.load('STOP', os.path.join(icons_dir, 'icon-stop-white-32.png'), 'IMAGE')
    pcoll.load('CALIBRATE', os.path.join(icons_dir, 'icon-straight-pose-32.png'), 'IMAGE')

    global icons
    icons = pcoll


def unload_icons():
    global icons
    previews.remove(icons)
