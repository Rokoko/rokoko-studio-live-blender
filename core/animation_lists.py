from collections import OrderedDict

from mathutils import Quaternion

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

# Tpose from Studio live
actor_bones = OrderedDict()
actor_bones['hip'] = Quaternion((-1.0, 0.0, -0.0, 0.0))
actor_bones['spine'] = Quaternion((-0.0, -0.0, 0.0, -1.0))
actor_bones['chest'] = Quaternion((-0.0, -0.0, 0.0, -1.0))
actor_bones['neck'] = Quaternion((-0.0, -0.0, 0.0, -1.0))
actor_bones['head'] = Quaternion((-0.0, -0.0, 0.0, -1.0))

actor_bones['leftShoulder'] = Quaternion((-0.70711, 0.0, 0.0, 0.70711))
actor_bones['leftUpperArm'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
actor_bones['leftLowerArm'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
actor_bones['leftHand'] = Quaternion((-0.5, -0.5, -0.5, 0.5))

actor_bones['rightShoulder'] = Quaternion((0.70711, 0.0, -0.0, 0.70711))
actor_bones['rightUpperArm'] = Quaternion((0.5, 0.5, -0.5, 0.5))
actor_bones['rightLowerArm'] = Quaternion((0.5, 0.5, -0.5, 0.5))
actor_bones['rightHand'] = Quaternion((0.5, 0.5, -0.5, 0.5))

actor_bones['leftUpLeg'] = Quaternion((0.70711, -0.0, 0.70711, -0.0))
actor_bones['leftLeg'] = Quaternion((0.70711, -0.0, 0.70711, 0.0))
actor_bones['leftFoot'] = Quaternion((0.0, -0.0, 0.70711, -0.70711))
actor_bones['leftToe'] = Quaternion((0.0, -0.0, 0.70711, -0.70711))
# actor_bones['leftToeEnd'] = Quaternion((0.0, -0.0, 0.70711, -0.70711))

actor_bones['rightUpLeg'] = Quaternion((0.70711, -0.0, -0.70711, 0.0))
actor_bones['rightLeg'] = Quaternion((0.70711, -0.0, -0.70711, 0.0))
actor_bones['rightFoot'] = Quaternion((0.0, 0.0, -0.70711, 0.70711))
actor_bones['rightToe'] = Quaternion((0.0, 0.0, -0.70711, 0.70711))
# actor_bones['rightToeEnd'] = Quaternion((0.0, 0.0, -0.70711, 0.70711))

# actor_bones['leftThumbProximal'] = Quaternion((-0.0923, -0.56098, -0.70106, 0.43046))
# actor_bones['leftThumbMedial'] = Quaternion((-0.2706, -0.65328, -0.65328, 0.2706))
# actor_bones['leftThumbDistal'] = Quaternion((-0.2706, -0.65328, -0.65328, 0.2706))
# # actor_bones['leftThumbTip'] = Quaternion((-0.2706, -0.65328, -0.65328, 0.2706))
#
# actor_bones['leftIndexProximal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
# actor_bones['leftIndexMedial'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
# actor_bones['leftIndexDistal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
# # actor_bones['leftIndexTip'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
#
# actor_bones['leftMiddleProximal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
# actor_bones['leftMiddleMedial'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
# actor_bones['leftMiddleDistal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
# # actor_bones['leftMiddleTip'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
#
# actor_bones['leftRingProximal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
# actor_bones['leftRingMedial'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
# actor_bones['leftRingDistal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
# # actor_bones['leftRingTip'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
#
# actor_bones['leftLittleProximal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
# actor_bones['leftLittleMedial'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
# actor_bones['leftLittleDistal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
# # actor_bones['leftLittleTip'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
#
# actor_bones['rightThumbProximal'] = Quaternion((0.0923, 0.56099, -0.70106, 0.43046))
# actor_bones['rightThumbMedial'] = Quaternion((0.2706, 0.65328, -0.65328, 0.2706))
# actor_bones['rightThumbDistal'] = Quaternion((0.2706, 0.65328, -0.65328, 0.2706))
# # actor_bones['rightThumbTip'] = Quaternion((0.2706, 0.65328, -0.65328, 0.2706))
#
# actor_bones['rightIndexProximal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
# actor_bones['rightIndexMedial'] = Quaternion((0.5, 0.5, -0.5, 0.5))
# actor_bones['rightIndexDistal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
# # actor_bones['rightIndexTip'] = Quaternion((0.5, 0.5, -0.5, 0.5))
#
# actor_bones['rightMiddleProximal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
# actor_bones['rightMiddleMedial'] = Quaternion((0.5, 0.5, -0.5, 0.5))
# actor_bones['rightMiddleDistal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
# # actor_bones['rightMiddleTip'] = Quaternion((0.5, 0.5, -0.5, 0.5))
#
# actor_bones['rightRingProximal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
# actor_bones['rightRingMedial'] = Quaternion((0.5, 0.5, -0.5, 0.5))
# actor_bones['rightRingDistal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
# # actor_bones['rightRingTip'] = Quaternion((0.5, 0.5, -0.5, 0.5))
#
# actor_bones['rightLittleProximal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
# actor_bones['rightLittleMedial'] = Quaternion((0.5, 0.5, -0.5, 0.5))
# actor_bones['rightLittleDistal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
# # actor_bones['rightLittleTip'] = Quaternion((0.5, 0.5, -0.5, 0.5))


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
