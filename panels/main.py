import bpy
import datetime

from .. import updater, updater_ops
from ..core import animations
from ..core import recorder as recorder_manager
from ..core import receiver as receiver_cls
from ..core.icon_manager import Icons
from ..operators import receiver, recorder

row_scale = 0.75
paired_inputs = {}


# Initializes the Rokoko panel in the toolbar
class ToolPanel(object):
    bl_label = 'Rokoko'
    bl_idname = 'VIEW3D_TS_rokoko'
    bl_category = 'Rokoko'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'


def separator(layout, scale=1):
    # Add small separator
    row = layout.row(align=True)
    row.scale_y = scale
    row.label(text='')


# Main panel of the Rokoko panel
class ReceiverPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rsl_receiver_v2'
    bl_label = 'Rokoko Studio Live'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False

        # box = layout.box()
        updater.check_for_update_background(check_on_startup=True)
        updater_ops.draw_update_notification_panel(layout)

        col = layout.column()

        row = col.row(align=True)
        row.label(text='Port:')
        row.enabled = not receiver.receiver_enabled
        row.prop(context.scene, 'rsl_receiver_port', text='')

        # row = col.row(align=True)
        # row.label(text='FPS:')
        # row.enabled = not receiver.receiver_enabled
        # row.prop(context.scene, 'rsl_receiver_fps', text='')

        row = col.row(align=True)
        row.label(text='Scene Scale:')
        row.prop(context.scene, 'rsl_scene_scaling', text='')

        layout.separator()

        row = layout.row(align=True)
        row.prop(context.scene, 'rsl_reset_scene_on_stop')

        row = layout.row(align=True)
        row.prop(context.scene, 'rsl_hide_mesh_during_play')

        row = layout.row(align=True)
        row.scale_y = 1.3
        if receiver.receiver_enabled:
            row.operator(receiver.ReceiverStop.bl_idname, icon='PAUSE', depress=True)
        else:
            row.operator(receiver.ReceiverStart.bl_idname, icon='PLAY')

        row = layout.row(align=True)
        row.scale_y = 1.3
        row.enabled = receiver.receiver_enabled
        if not context.scene.rsl_recording:
            row.operator(recorder.RecorderStart.bl_idname, icon_value=Icons.START_RECORDING.get_icon())
        else:
            row.operator(recorder.RecorderStop.bl_idname, icon='SNAP_FACE', depress=True)

            # Calculate recording time
            timestamps = list(recorder_manager.recorded_timestamps.keys())
            if timestamps:
                time_recorded = int(timestamps[-1] - timestamps[0])
                row = layout.row(align=True)
                row.label(text='Recording time: ' + str(datetime.timedelta(seconds=time_recorded)))

        if receiver.receiver_enabled and receiver_cls.show_error:
            for i, error in enumerate(receiver_cls.show_error):
                if i == 0:
                    row = layout.row(align=True)
                    row.label(text=error, icon='ERROR')
                else:
                    row = layout.row(align=True)
                    row.scale_y = 0.3
                    row.label(text=error, icon='BLANK1')
            return

        if animations.live_data.version <= 2:
            show_connetions_v2(layout)
        else:
            show_connetions_v3(layout)


def show_connetions_v2(layout):
    # Show all inputs
    global paired_inputs
    paired_inputs = {}
    used_trackers = []
    used_faces = []

    # Get all paired inputs. Paired inputs are paired to an object in the scene
    for obj in bpy.data.objects:
        # Get paired props and trackers
        if animations.live_data.props or animations.live_data.trackers:
            if obj.rsl_animations_props_trackers and obj.rsl_animations_props_trackers != 'None':
                paired = paired_inputs.get(obj.rsl_animations_props_trackers.split('|')[1])
                if not paired:
                    paired_inputs[obj.rsl_animations_props_trackers.split('|')[1]] = [obj.name]
                else:
                    paired.append(obj.name)

        # Get paired faces
        if animations.live_data.faces and obj.rsl_animations_faces and obj.rsl_animations_faces != 'None':
            paired = paired_inputs.get(obj.rsl_animations_faces)
            if not paired:
                paired_inputs[obj.rsl_animations_faces] = [obj.name]
            else:
                paired.append(obj.name)

        # Get paired actors
        if animations.live_data.actors and obj.rsl_animations_actors and obj.rsl_animations_actors != 'None':
            paired = paired_inputs.get(obj.rsl_animations_actors)
            if not paired:
                paired_inputs[obj.rsl_animations_actors] = [obj.name]
            else:
                paired.append(obj.name)

    # This is used as a small spacer
    row = layout.row(align=True)
    row.scale_y = 0.01
    row.label(text=' ')

    # Display all paired and unpaired inputs
    for actor in animations.live_data.actors:
        if actor['profileName']:
            row = layout.row(align=True)
            row.scale_y = row_scale
            row.label(text=actor['profileName'], icon='ANTIALIASED')

            split = layout.row(align=True)
            split.scale_y = row_scale
            add_indent(split)
            show_actor(split, actor)

            for tracker in animations.live_data.trackers:
                if tracker['connectionId'] == actor['name']:
                    split = layout.row(align=True)
                    split.scale_y = row_scale
                    add_indent(split, empty=True)
                    add_indent(split)
                    show_tracker(split, tracker)
                    used_trackers.append(tracker['name'])

            for face in animations.live_data.faces:
                if face.get('profileName') and face.get('profileName') == actor['profileName']:
                    split = layout.row(align=True)
                    split.scale_y = row_scale
                    add_indent(split)
                    show_face(split, face)
                    used_faces.append(face['faceId'])

            # split = layout.row(align=True)
            # add_indent(split)
            # row = split.row(align=True)
            # row.label(text='faceId', icon_value=Icons.FACE.get_icon())

    for prop in animations.live_data.props:
        show_prop(layout, prop, scale=True)

        for tracker in animations.live_data.trackers:
            if tracker['connectionId'] == prop['id']:
                split = layout.row(align=True)
                split.scale_y = row_scale
                add_indent(split)
                show_tracker(split, tracker)
                used_trackers.append(tracker['name'])

    for tracker in animations.live_data.trackers:
        if tracker['name'] not in used_trackers:
            show_tracker(layout, tracker, scale=True)

    # row = layout.row(align=True)
    # row.label(text='5', icon_value=Icons.VP.get_icon())

    for face in animations.live_data.faces:
        if face['faceId'] not in used_faces:
            show_face(layout, face, scale=True)


def show_connetions_v3(layout):
    # Show all inputs
    global paired_inputs
    paired_inputs = {}

    for obj in bpy.data.objects:
        # Get props
        if obj.rsl_animations_props_trackers and obj.rsl_animations_props_trackers != 'None':
            if animations.live_data.props:
                prop = animations.live_data.get_prop_by_obj(obj)
                if prop:
                    prop_id = animations.live_data.get_prop_id(prop)
                    if not paired_inputs.get(prop_id):
                        paired_inputs[prop_id] = [obj.name]
                    else:
                        paired_inputs[prop_id].append(obj.name)

        # Get faces
        if animations.live_data.faces and obj.rsl_animations_faces and obj.rsl_animations_faces != 'None':
            face = animations.live_data.get_face_by_obj(obj)
            if face:
                face_id = animations.live_data.get_face_id(face)
                if not paired_inputs.get(face_id):
                    paired_inputs[face_id] = [obj.name]
                else:
                    paired_inputs[face_id].append(obj.name)

        # Get actors
        if animations.live_data.actors and obj.rsl_animations_actors and obj.rsl_animations_actors != 'None':
            actor = animations.live_data.get_actor_by_obj(obj)
            if actor:
                actor_id = animations.live_data.get_actor_id(actor)
                if not paired_inputs.get(actor_id):
                    paired_inputs[actor_id] = [obj.name]
                else:
                    paired_inputs[actor_id].append(obj.name)

    # This is used as a small spacer
    row = layout.row(align=True)
    row.scale_y = 0.01
    row.label(text=' ')

    # Display all paired and unpaired inputs
    for actor in animations.live_data.actors:
        show_actor(layout, actor)

        for face in animations.live_data.faces:
            if animations.live_data.get_face_parent_id(face) == animations.live_data.get_actor_id(actor):
                split = layout.row(align=True)
                split.scale_y = row_scale
                add_indent(split)
                show_face(split, face)

    for prop in animations.live_data.props:
        show_prop(layout, prop, scale=True)


def add_indent(split, empty=False):
    row = split.row(align=True)
    row.alignment = 'LEFT'
    if empty:
        row.label(text="", icon='BLANK1')
    else:
        row.label(text="", icon_value=Icons.PAIRED.get_icon())


def show_actor(layout, actor, scale=False):
    row = layout.row(align=True)
    if scale:
        row.scale_y = row_scale

    actor_id = animations.live_data.get_actor_id(actor)
    if paired_inputs.get(actor_id):
        row.label(text=actor_id + '  --> ' + ', '.join(paired_inputs.get(actor_id)), icon_value=Icons.SUIT.get_icon())
    else:
        row.enabled = False
        row.label(text=actor_id, icon_value=Icons.SUIT.get_icon())


def show_glove(layout, glove, scale=False):
    row = layout.row(align=True)
    if scale:
        row.scale_y = row_scale

    if paired_inputs.get(glove['gloveID']):
        row.label(text=glove['gloveID'] + '  --> ' + ', '.join(paired_inputs.get(glove['gloveID'])), icon='VIEW_PAN')
    else:
        row.enabled = False
        row.label(text=glove['gloveID'], icon='VIEW_PAN')


def show_face(layout, face, scale=False):
    row = layout.row(align=True)
    if scale:
        row.scale_y = row_scale

    face_id = animations.live_data.get_face_id(face)
    if paired_inputs.get(face_id):
        row.label(text=face_id + '  --> ' + ', '.join(paired_inputs.get(face_id)), icon_value=Icons.FACE.get_icon())
    else:
        row.enabled = False
        row.label(text=face_id, icon_value=Icons.FACE.get_icon())


def show_tracker(layout, tracker, scale=False):
    row = layout.row(align=True)
    if scale:
        row.scale_y = row_scale

    if paired_inputs.get(tracker['name']):
        row.label(text=tracker['name'] + '  --> ' + ', '.join(paired_inputs.get(tracker['name'])), icon_value=Icons.VP.get_icon())
    else:
        row.enabled = False
        row.label(text=tracker['name'], icon_value=Icons.VP.get_icon())


def show_prop(layout, prop, scale=False):
    row = layout.row(align=True)
    if scale:
        row.scale_y = row_scale

    prop_id = animations.live_data.get_prop_name_raw(prop)
    if paired_inputs.get(prop_id):
        row.label(text=prop_id + '  --> ' + ', '.join(paired_inputs.get(prop_id)), icon='FILE_3D')
    else:
        row.enabled = False
        row.label(text=prop_id, icon='FILE_3D')
