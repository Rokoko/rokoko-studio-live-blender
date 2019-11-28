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

# actor_bones = [
#     'hip',
#     'spine',
#     'chest',
#     'neck',
#     'head',
#
#     'leftShoulder',
#     'leftUpperArm',
#     'leftLowerArm',
#     'leftHand',
#
#     'rightShoulder',
#     'rightUpperArm',
#     'rightLowerArm',
#     'rightHand',
#
#     'leftUpLeg',
#     'leftLeg',
#     'leftFoot',
#     'leftToe',
#     'leftToeEnd',
#
#     'rightUpLeg',
#     'rightLeg',
#     'rightFoot',
#     'rightToe',
#     'rightToeEnd',
#
#     'leftThumbProximal',
#     'leftThumbMedial',
#     'leftThumbDistal',
#     'leftThumbTip',
#
#     'leftIndexProximal',
#     'leftIndexMedial',
#     'leftIndexDistal',
#     'leftIndexTip',
#
#     'leftMiddleProximal',
#     'leftMiddleMedial',
#     'leftMiddleDistal',
#     'leftMiddleTip',
#
#     'leftRingProximal',
#     'leftRingMedial',
#     'leftRingDistal',
#     'leftRingTip',
#
#     'leftLittleProximal',
#     'leftLittleMedial',
#     'leftLittleDistal',
#     'leftLittleTip',
#
#     'rightThumbProximal',
#     'rightThumbMedial',
#     'rightThumbDistal',
#     'rightThumbTip',
#
#     'rightIndexProximal',
#     'rightIndexMedial',
#     'rightIndexDistal',
#     'rightIndexTip',
#
#     'rightMiddleProximal',
#     'rightMiddleMedial',
#     'rightMiddleDistal',
#     'rightMiddleTip',
#
#     'rightRingProximal',
#     'rightRingMedial',
#     'rightRingDistal',
#     'rightRingTip',
#
#     'rightLittleProximal',
#     'rightLittleMedial',
#     'rightLittleDistal',
#     'rightLittleTip',
# ]

# # Reference model bones, this is used to calculate the offset of the received data
actor_bones = OrderedDict()

# From tpose reference model
# actor_bones['hip'] = Quaternion((1.0, -0.0, -0.0, 0.0))
# actor_bones['spine'] = Quaternion((1.0, 0.0, 0.0, -0.0))
# actor_bones['chest'] = Quaternion((1.0, 0.0, 0.0, -0.0))
# actor_bones['neck'] = Quaternion((1.0, 0.0, 0.0, -0.0))
# actor_bones['head'] = Quaternion((1.0, 0.0, 0.0, -0.0))
#
# actor_bones['leftShoulder'] = Quaternion((0.0, 0.707107, 0.707107, -0.0))
# actor_bones['leftUpperArm'] = Quaternion((0.5, -0.5, -0.5, -0.5))
# actor_bones['leftLowerArm'] = Quaternion((0.499999, -0.500001, -0.500001, -0.5))
# actor_bones['leftHand'] = Quaternion((0.499999, -0.5, -0.500001, -0.5))
#
# actor_bones['rightShoulder'] = Quaternion((1e-06, -0.707107, 0.707106, 0.0))
# actor_bones['rightUpperArm'] = Quaternion((0.5, -0.5, 0.5, 0.5))
# actor_bones['rightLowerArm'] = Quaternion((0.5, -0.500001, 0.499999, 0.5))
# actor_bones['rightHand'] = Quaternion((0.5, -0.5, 0.5, 0.5))
#
# actor_bones['leftUpLeg'] = Quaternion((-0.0, 0.707107, 0.0, 0.707106))
# actor_bones['leftLeg'] = Quaternion((1e-06, 0.707107, -1e-06, 0.707106))
# actor_bones['leftFoot'] = Quaternion((-0.0, -1e-06, -0.707107, -0.707106))
# actor_bones['leftToe'] = Quaternion((0.0, 2e-06, 0.707107, 0.707107))
# actor_bones['leftToeEnd'] = Quaternion((0.0, 2e-06, 0.707107, 0.707107))
#
# actor_bones['rightUpLeg'] = Quaternion((-0.0, 0.707107, -0.0, -0.707106))
# actor_bones['rightLeg'] = Quaternion((-0.0, 0.707107, -0.0, -0.707106))
# actor_bones['rightFoot'] = Quaternion((0.0, -0.0, 0.707107, 0.707107))
# actor_bones['rightToe'] = Quaternion((0.0, -0.0, 0.707107, 0.707107))
# actor_bones['rightToeEnd'] = Quaternion((0.0, -0.0, 0.707107, 0.707107))
#
# actor_bones['leftThumbProximal'] = Quaternion((0.532703, 0.110084, -0.070133, -0.836176))
# actor_bones['leftThumbMedial'] = Quaternion((0.57966, 0.019215, 0.075366, -0.811138))
# actor_bones['leftThumbDistal'] = Quaternion((0.579945, -0.006088, 0.110676, -0.80708))
#
# actor_bones['leftIndexProximal'] = Quaternion((0.452686, -0.55591, -0.41048, -0.563512))
# actor_bones['leftIndexMedial'] = Quaternion((0.376252, -0.610241, -0.333415, -0.61227))
# actor_bones['leftIndexDistal'] = Quaternion((0.293381, -0.654131, -0.250646, -0.650551))
#
# actor_bones['leftMiddleProximal'] = Quaternion((0.430458, -0.560985, -0.430461, -0.560985))
# actor_bones['leftMiddleMedial'] = Quaternion((0.353556, -0.61237, -0.353558, -0.612371))
# actor_bones['leftMiddleDistal'] = Quaternion((0.270597, -0.653281, -0.2706, -0.653282))
#
# actor_bones['leftRingProximal'] = Quaternion((0.372484, -0.617536, -0.473547, -0.505626))
# actor_bones['leftRingMedial'] = Quaternion((0.288694, -0.660872, -0.403501, -0.563109))
# actor_bones['leftRingDistal'] = Quaternion((0.19996, -0.692901, -0.326544, -0.610961))
#
# actor_bones['leftLittleProximal'] = Quaternion((0.349962, -0.620115, -0.492061, -0.500858))
# actor_bones['leftLittleMedial'] = Quaternion((0.266028, -0.66049, -0.422473, -0.560801))
# actor_bones['leftLittleDistal'] = Quaternion((0.177544, -0.68956, -0.345665, -0.611147))
#
# actor_bones['rightThumbProximal'] = Quaternion((0.532703, 0.110084, 0.070131, 0.836176))
# actor_bones['rightThumbMedial'] = Quaternion((0.579659, 0.019214, -0.075368, 0.811138))
# actor_bones['rightThumbDistal'] = Quaternion((0.579946, -0.006088, -0.110678, 0.807079))
#
# actor_bones['rightIndexProximal'] = Quaternion((0.452687, -0.55591, 0.410478, 0.563512))
# actor_bones['rightIndexMedial'] = Quaternion((0.376254, -0.610241, 0.333414, 0.61227))
# actor_bones['rightIndexDistal'] = Quaternion((0.293383, -0.654131, 0.250645, 0.65055))
#
# actor_bones['rightMiddleProximal'] = Quaternion((0.43046, -0.560986, 0.430459, 0.560985))
# actor_bones['rightMiddleMedial'] = Quaternion((0.353557, -0.612371, 0.353557, 0.61237))
# actor_bones['rightMiddleDistal'] = Quaternion((0.270599, -0.653281, 0.270599, 0.653281))
#
# actor_bones['rightRingProximal'] = Quaternion((0.372486, -0.617537, 0.473546, 0.505626))
# actor_bones['rightRingMedial'] = Quaternion((0.288696, -0.660872, 0.403499, 0.563109))
# actor_bones['rightRingDistal'] = Quaternion((0.199962, -0.692901, 0.326543, 0.61096))
#
# actor_bones['rightLittleProximal'] = Quaternion((0.349964, -0.620115, 0.49206, 0.500858))
# actor_bones['rightLittleMedial'] = Quaternion((0.26603, -0.66049, 0.422473, 0.560801))
# actor_bones['rightLittleDistal'] = Quaternion((0.177546, -0.689561, 0.345664, 0.611146))


# From Studio Live export
# actor_bones['hip'] = Quaternion((1.0, 0.0, 0.0, 0.0))
# actor_bones['spine'] = Quaternion((1.0, 0.0, 0.0, 0.0))
# actor_bones['chest'] = Quaternion((1.0, 0.0, 0.0, 0.0))
# actor_bones['neck'] = Quaternion((1.0, 0.0, 0.0, 0.0))
# actor_bones['head'] = Quaternion((1.0, 0.0, 0.0, 0.0))
#
# actor_bones['leftShoulder'] = Quaternion((0.707106, 0.0, -0.0, -0.707107))
# actor_bones['leftUpperArm'] = Quaternion((0.707106, 2e-06, 0.0, -0.707107))
# actor_bones['leftLowerArm'] = Quaternion((0.707106, -0.0, -0.0, -0.707107))
# actor_bones['leftHand'] = Quaternion((0.707106, -0.0, -0.0, -0.707107))
#
# actor_bones['rightShoulder'] = Quaternion((0.707106, -0.0, -0.0, 0.707107))
# actor_bones['rightUpperArm'] = Quaternion((0.707106, -0.0, -0.0, 0.707107))
# actor_bones['rightLowerArm'] = Quaternion((0.707106, -3e-06, -0.0, 0.707108))
# actor_bones['rightHand'] = Quaternion((0.707106, -3e-06, -0.0, 0.707108))
#
# actor_bones['leftUpLeg'] = Quaternion((-0.0, 0.0, 0.0, 1.0))
# actor_bones['leftLeg'] = Quaternion((0.000721, -0.000752, -1e-06, -0.999999))
# actor_bones['leftFoot'] = Quaternion((-0.0, -0.0, 0.707107, 0.707107))
# actor_bones['leftToe'] = Quaternion((-0.0, -0.0, 0.707107, 0.707107))
#
# actor_bones['rightUpLeg'] = Quaternion((-0.0, 0.0, 0.0, 1.0))
# actor_bones['rightLeg'] = Quaternion((0.000722, -0.000401, 1e-06, 1.0))
# actor_bones['rightFoot'] = Quaternion((-0.0, -0.0, 0.707107, 0.707107))
# actor_bones['rightToe'] = Quaternion((-0.0, -0.0, 0.707107, 0.707107))
#
# actor_bones['leftThumbProximal'] = Quaternion((0.532703, 0.110084, -0.070133, -0.836176))
# actor_bones['leftThumbMedial'] = Quaternion((0.57966, 0.019215, 0.075366, -0.811138))
# actor_bones['leftThumbDistal'] = Quaternion((0.579945, -0.006088, 0.110676, -0.80708))
#
# actor_bones['leftIndexProximal'] = Quaternion((0.452686, -0.55591, -0.41048, -0.563512))
# actor_bones['leftIndexMedial'] = Quaternion((0.376252, -0.610241, -0.333415, -0.61227))
# actor_bones['leftIndexDistal'] = Quaternion((0.293381, -0.654131, -0.250646, -0.650551))
#
# actor_bones['leftMiddleProximal'] = Quaternion((0.430458, -0.560985, -0.430461, -0.560985))
# actor_bones['leftMiddleMedial'] = Quaternion((0.353556, -0.61237, -0.353558, -0.612371))
# actor_bones['leftMiddleDistal'] = Quaternion((0.270597, -0.653281, -0.2706, -0.653282))
#
# actor_bones['leftRingProximal'] = Quaternion((0.372484, -0.617536, -0.473547, -0.505626))
# actor_bones['leftRingMedial'] = Quaternion((0.288694, -0.660872, -0.403501, -0.563109))
# actor_bones['leftRingDistal'] = Quaternion((0.19996, -0.692901, -0.326544, -0.610961))
#
# actor_bones['leftLittleProximal'] = Quaternion((0.349962, -0.620115, -0.492061, -0.500858))
# actor_bones['leftLittleMedial'] = Quaternion((0.266028, -0.66049, -0.422473, -0.560801))
# actor_bones['leftLittleDistal'] = Quaternion((0.177544, -0.68956, -0.345665, -0.611147))
#
# actor_bones['rightThumbProximal'] = Quaternion((0.532703, 0.110084, 0.070131, 0.836176))
# actor_bones['rightThumbMedial'] = Quaternion((0.579659, 0.019214, -0.075368, 0.811138))
# actor_bones['rightThumbDistal'] = Quaternion((0.579946, -0.006088, -0.110678, 0.807079))
#
# actor_bones['rightIndexProximal'] = Quaternion((0.452687, -0.55591, 0.410478, 0.563512))
# actor_bones['rightIndexMedial'] = Quaternion((0.376254, -0.610241, 0.333414, 0.61227))
# actor_bones['rightIndexDistal'] = Quaternion((0.293383, -0.654131, 0.250645, 0.65055))
#
# actor_bones['rightMiddleProximal'] = Quaternion((0.43046, -0.560986, 0.430459, 0.560985))
# actor_bones['rightMiddleMedial'] = Quaternion((0.353557, -0.612371, 0.353557, 0.61237))
# actor_bones['rightMiddleDistal'] = Quaternion((0.270599, -0.653281, 0.270599, 0.653281))
#
# actor_bones['rightRingProximal'] = Quaternion((0.372486, -0.617537, 0.473546, 0.505626))
# actor_bones['rightRingMedial'] = Quaternion((0.288696, -0.660872, 0.403499, 0.563109))
# actor_bones['rightRingDistal'] = Quaternion((0.199962, -0.692901, 0.326543, 0.61096))
#
# actor_bones['rightLittleProximal'] = Quaternion((0.349964, -0.620115, 0.49206, 0.500858))
# actor_bones['rightLittleMedial'] = Quaternion((0.26603, -0.66049, 0.422473, 0.560801))
# actor_bones['rightLittleDistal'] = Quaternion((0.177546, -0.689561, 0.345664, 0.611146))


# Tpose from Studio live
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
actor_bones['leftToeEnd'] = Quaternion((0.0, -0.0, 0.70711, -0.70711))

actor_bones['rightUpLeg'] = Quaternion((0.70711, -0.0, -0.70711, 0.0))
actor_bones['rightLeg'] = Quaternion((0.70711, -0.0, -0.70711, 0.0))
actor_bones['rightFoot'] = Quaternion((0.0, 0.0, -0.70711, 0.70711))
actor_bones['rightToe'] = Quaternion((0.0, 0.0, -0.70711, 0.70711))
actor_bones['rightToeEnd'] = Quaternion((0.0, 0.0, -0.70711, 0.70711))

actor_bones['leftThumbProximal'] = Quaternion((-0.0923, -0.56098, -0.70106, 0.43046))
actor_bones['leftThumbMedial'] = Quaternion((-0.2706, -0.65328, -0.65328, 0.2706))
actor_bones['leftThumbDistal'] = Quaternion((-0.2706, -0.65328, -0.65328, 0.2706))
actor_bones['leftThumbTip'] = Quaternion((-0.2706, -0.65328, -0.65328, 0.2706))

actor_bones['leftIndexProximal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
actor_bones['leftIndexMedial'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
actor_bones['leftIndexDistal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
actor_bones['leftIndexTip'] = Quaternion((-0.5, -0.5, -0.5, 0.5))

actor_bones['leftMiddleProximal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
actor_bones['leftMiddleMedial'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
actor_bones['leftMiddleDistal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
actor_bones['leftMiddleTip'] = Quaternion((-0.5, -0.5, -0.5, 0.5))

actor_bones['leftRingProximal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
actor_bones['leftRingMedial'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
actor_bones['leftRingDistal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
actor_bones['leftRingTip'] = Quaternion((-0.5, -0.5, -0.5, 0.5))

actor_bones['leftLittleProximal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
actor_bones['leftLittleMedial'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
actor_bones['leftLittleDistal'] = Quaternion((-0.5, -0.5, -0.5, 0.5))
actor_bones['leftLittleTip'] = Quaternion((-0.5, -0.5, -0.5, 0.5))

actor_bones['rightThumbProximal'] = Quaternion((0.0923, 0.56099, -0.70106, 0.43046))
actor_bones['rightThumbMedial'] = Quaternion((0.2706, 0.65328, -0.65328, 0.2706))
actor_bones['rightThumbDistal'] = Quaternion((0.2706, 0.65328, -0.65328, 0.2706))
actor_bones['rightThumbTip'] = Quaternion((0.2706, 0.65328, -0.65328, 0.2706))

actor_bones['rightIndexProximal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
actor_bones['rightIndexMedial'] = Quaternion((0.5, 0.5, -0.5, 0.5))
actor_bones['rightIndexDistal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
actor_bones['rightIndexTip'] = Quaternion((0.5, 0.5, -0.5, 0.5))

actor_bones['rightMiddleProximal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
actor_bones['rightMiddleMedial'] = Quaternion((0.5, 0.5, -0.5, 0.5))
actor_bones['rightMiddleDistal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
actor_bones['rightMiddleTip'] = Quaternion((0.5, 0.5, -0.5, 0.5))

actor_bones['rightRingProximal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
actor_bones['rightRingMedial'] = Quaternion((0.5, 0.5, -0.5, 0.5))
actor_bones['rightRingDistal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
actor_bones['rightRingTip'] = Quaternion((0.5, 0.5, -0.5, 0.5))

actor_bones['rightLittleProximal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
actor_bones['rightLittleMedial'] = Quaternion((0.5, 0.5, -0.5, 0.5))
actor_bones['rightLittleDistal'] = Quaternion((0.5, 0.5, -0.5, 0.5))
actor_bones['rightLittleTip'] = Quaternion((0.5, 0.5, -0.5, 0.5))


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
