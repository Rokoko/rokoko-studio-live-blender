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
    'jawForward',
    'jawLeft',
    'jawRight',
    'jawOpen',
    'mouthClose',
    'mouthFunnel',
    'mouthPucker',
    'mouthLeft',
    'mouthRight',
    'mouthSmileLeft',
    'mouthSmileRight',
    'mouthFrownLeft',
    'mouthFrownRight',
    'mouthDimpleLeft',
    'mouthDimpleRight',
    'mouthStretchLeft',
    'mouthStretchRight',
    'mouthRollLower',
    'mouthRollUpper',
    'mouthShrugLower',
    'mouthShrugUpper',
    'mouthPressLeft',
    'mouthPressRight',
    'mouthLowerDownLeft',
    'mouthLowerDownRight',
    'mouthUpperUpLeft',
    'mouthUpperUpRight',
    'browDownLeft',
    'browDownRight',
    'browInnerUp',
    'browOuterUpLeft',
    'browOuterUpRight',
    'cheekPuff',
    'cheekSquintLeft',
    'cheekSquintRight',
    'noseSneerLeft',
    'noseSneerRight',
    'tongueOut'
]

# Face shapekeys
actor_bones = [
    'hip',
    'spine',
    'chest',
    'neck',
    'head',

    'leftShoulder',
    'leftUpperArm',
    'leftLowerArm',
    'leftHand',

    'rightShoulder',
    'rightUpperArm',
    'rightLowerArm',
    'rightHand',

    'leftUpLeg',
    'leftLeg',
    'leftFoot',
    'leftToe',
    'leftToeEnd',

    'rightUpLeg',
    'rightLeg',
    'rightFoot',
    'rightToe',
    'rightToeEnd',

    'leftThumbProximal',
    'leftThumbMedial',
    'leftThumbDistal',
    'leftThumbTip',

    'leftIndexProximal',
    'leftIndexMedial',
    'leftIndexDistal',
    'leftIndexTip',

    'leftMiddleProximal',
    'leftMiddleMedial',
    'leftMiddleDistal',
    'leftMiddleTip',

    'leftRingProximal',
    'leftRingMedial',
    'leftRingDistal',
    'leftRingTip',

    'leftLittleProximal',
    'leftLittleMedial',
    'leftLittleDistal',
    'leftLittleTip',

    'rightThumbProximal',
    'rightThumbMedial',
    'rightThumbDistal',
    'rightThumbTip',

    'rightIndexProximal',
    'rightIndexMedial',
    'rightIndexDistal',
    'rightIndexTip',

    'rightMiddleProximal',
    'rightMiddleMedial',
    'rightMiddleDistal',
    'rightMiddleTip',

    'rightRingProximal',
    'rightRingMedial',
    'rightRingDistal',
    'rightRingTip',

    'rightLittleProximal',
    'rightLittleMedial',
    'rightLittleDistal',
    'rightLittleTip',
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
        choices.append((actor['id'], actor['id'], actor['id']))

    return choices
