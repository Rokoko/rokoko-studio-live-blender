from . import animations

# Face shapekeys
face_shapes = [
    'eyeBlinkLeft',
    'eyeLookDownLeft',
    'eyeLookInLeft',
    'eyeLookOutLeft',
    'eyeLookUpLeft',
    'eyeSquintLeft',
    'eyeWideLeft',
    'eyeBlinkRight',
    'eyeLookDownRight',
    'eyeLookInRight',
    'eyeLookOutRight',
    'eyeLookUpRight',
    'eyeSquintRight',
    'eyeWideRight',
    "jawForward",
    "jawLeft",
    "jawRight",
    "jawOpen",
    "mouthClose",
    "mouthFunnel",
    "mouthPucker",
    "mouthLeft",
    "mouthRight",
    "mouthSmileLeft",
    "mouthSmileRight",
    "mouthFrownLeft",
    "mouthFrownRight",
    "mouthDimpleLeft",
    "mouthDimpleRight",
    "mouthStretchLeft",
    "mouthStretchRight",
    "mouthRollLower",
    "mouthRollUpper",
    "mouthShrugLower",
    "mouthShrugUpper",
    "mouthPressLeft",
    "mouthPressRight",
    "mouthLowerDownLeft",
    "mouthLowerDownRight",
    "mouthUpperUpLeft",
    "mouthUpperUpRight",
    "browDownLeft",
    "browDownRight",
    "browInnerUp",
    "browOuterUpLeft",
    "browOuterUpRight",
    "cheekPuff",
    "cheekSquintLeft",
    "cheekSquintRight",
    "noseSneerLeft",
    "noseSneerRight",
    "tongueOut"
]


# Creates the list of props and trackers for the objects panel
def get_props_trackers(self, context):
    choices = [('None', '-None-', 'None')]

    for prop in animations.props:
        # 1. Will be returned by context.scene
        # 2. Will be shown in lists
        # 3. will be shown in the hover description (below description)
        choices.append(('PR|' + prop['id'] + '|' + prop['name'], 'Prop: ' + prop['name'], 'Prop: ' + prop['name']))

    for tracker in animations.trackers:
        choices.append(('TR|' + tracker['name'], 'Tracker: ' + tracker['name'], 'Tracker: ' + tracker['name']))

    return choices


# Creates the list of faces for the objects panel
def get_faces(self, context):
    choices = [('None', '-None-', 'None')]

    for face in animations.faces:
        # 1. Will be returned by context.scene
        # 2. Will be shown in lists
        # 3. will be shown in the hover description (below description)
        choices.append((face['faceId'], face['faceId'], face['faceId']))

    return choices


# Creates the list of actors for the objects panel
def get_actors(self, context):
    choices = [('None', '-None-', 'None')]

    for actor in animations.actors:
        # 1. Will be returned by context.scene
        # 2. Will be shown in lists
        # 3. will be shown in the hover description (below description)
        choices.append((actor['id'] + '|' + actor['name'], actor['name'], actor['name']))

    return choices


# Creates the list of actors for the objects panel
def get_face_shapes(self, context):
    choices = []
    mesh = context.object

    if not hasattr(mesh.data, 'shape_keys') or not hasattr(mesh.data.shape_keys, 'key_blocks'):
        return choices

    for shapekey in mesh.data.shape_keys.key_blocks:
        # 1. Will be returned by context.scene
        # 2. Will be shown in lists
        # 3. will be shown in the hover description (below description)
        choices.append((shapekey.name, shapekey.name, shapekey.name))

    return choices
