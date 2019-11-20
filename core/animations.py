import bpy

# version = None
# timestamp = None
# playbacktimestamp = None
props = []
trackers = []
faces = []
actors = []


def clear_animations():
    global props, trackers, faces, actors
    props = []
    trackers = []
    faces = []
    actors = []


# Creates the list of props and trackers for the objects panel
def get_props_trackers(self, context):
    choices = []

    for prop in props:
        # 1. Will be returned by context.scene
        # 2. Will be shown in lists
        # 3. will be shown in the hover description (below description)
        choices.append(('PR|' + prop['id'] + '|' + prop['name'], 'Prop: ' + prop['name'], 'Prop: ' + prop['name']))

    for tracker in trackers:
        choices.append(('TR|' + tracker['name'], 'Tracker: ' + tracker['name'], 'Tracker: ' + tracker['name']))

    return choices


# Creates the list of faces for the objects panel
def get_faces(self, context):
    choices = []

    for face in faces:
        # 1. Will be returned by context.scene
        # 2. Will be shown in lists
        # 3. will be shown in the hover description (below description)
        choices.append((face['faceId'], face['faceId'], face['faceId']))

    return choices


# Creates the list of actors for the objects panel
def get_actors(self, context):
    choices = []

    for actor in actors:
        # 1. Will be returned by context.scene
        # 2. Will be shown in lists
        # 3. will be shown in the hover description (below description)
        choices.append((actor['id'] + '|' + actor['name'], actor['name'], actor['name']))

    return choices


def animate():
    for obj in bpy.data.objects:
        if obj.ssp_animations_props_trackers and obj.ssp_animations_props_trackers.startswith('PR|'):
            obj_id = obj.ssp_animations_props_trackers.split('|')[1]
            prop = [prop for prop in props if prop['id'] == obj_id]

            # print('PROP', obj.name, obj_id, prop)

            if not prop:
                return

            obj.rotation_mode = 'QUATERNION'
            obj.location = (
                prop[0]['position']['x'],
                prop[0]['position']['y'],
                prop[0]['position']['z'],
            )
            obj.rotation_quaternion = (
                prop[0]['rotation']['w'],
                prop[0]['rotation']['x'],
                prop[0]['rotation']['y'],
                prop[0]['rotation']['z'],
            )
        if obj.ssp_animations_props_trackers and obj.ssp_animations_props_trackers.startswith('TR|'):
            obj_id = obj.ssp_animations_props_trackers.split('|')[1]
            tracker = [tracker for tracker in trackers if tracker['name'] == obj_id]

            # print('TRACKER', obj.name, obj_id)

            if not tracker:
                return

            obj.rotation_mode = 'QUATERNION'
            obj.location = (
                tracker[0]['position']['x'],
                tracker[0]['position']['y'],
                tracker[0]['position']['z'],
            )
            obj.rotation_quaternion = (
                prop[0]['rotation']['w'],
                prop[0]['rotation']['x'],
                prop[0]['rotation']['y'],
                prop[0]['rotation']['z'],
            )
