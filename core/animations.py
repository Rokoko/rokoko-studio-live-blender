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


def get_props_trackers(self, context):
    choices = []

    for prop in props:
        # 1. Will be returned by context.scene
        # 2. Will be shown in lists
        # 3. will be shown in the hover description (below description)
        choices.append((prop['id'], 'Prop: ' + prop['name'], 'Prop: ' + prop['name']))

    for tracker in trackers:
        choices.append((tracker['name'], 'Tracker: ' + tracker['name'], 'Tracker: ' + tracker['name']))

    return choices


def get_faces(self, context):
    choices = []

    for face in faces:
        # 1. Will be returned by context.scene
        # 2. Will be shown in lists
        # 3. will be shown in the hover description (below description)
        choices.append((face['faceId'], face['faceId'], face['faceId']))

    return choices


def get_actors(self, context):
    choices = []

    for actor in actors:
        # 1. Will be returned by context.scene
        # 2. Will be shown in lists
        # 3. will be shown in the hover description (below description)
        choices.append((actor['id'], actor['name'], actor['name']))

    return choices
