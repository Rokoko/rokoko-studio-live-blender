import sys
import bpy


def ui_refresh_properties():
    # Refreshes the properties panel
    for windowManager in bpy.data.window_managers:
        for window in windowManager.windows:
            for area in window.screen.areas:
                if area.type == 'PROPERTIES':
                    area.tag_redraw()


def ui_refresh_view_3d():
    # Refreshes the view 3D panel
    for windowManager in bpy.data.window_managers:
        for window in windowManager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()


def ui_refresh_all():
    # Refreshes all panels
    for windowManager in bpy.data.window_managers:
        for window in windowManager.windows:
            for area in window.screen.areas:
                area.tag_redraw()


def reprint(*x):
    # This prints a message in the same console line continuously
    sys.stdout.write("\r" + " ".join(x))
    sys.stdout.flush()