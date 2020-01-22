import bpy

import numpy as np
from mathutils import Euler, Quaternion, Vector


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


# class containing function that represent Blender's coordinate space - currently uses functions used for unity plugin
class ReferenceSpace():
    def __init__(self):
        self.unity_default = Euler((90, 0, 0), 'ZXY').to_quaternion()

    def validation_check(self, quaternion):
        list = [quaternion.w, quaternion.x, quaternion.y, quaternion.z]
        for i in list:
            if np.isnan(i):
                return False
            else:
                return True

    def Quaternion_fromUnity(self, rotation):
        if self.validation_check(rotation):
            result = Quaternion((rotation.w, rotation.x, rotation.y, rotation.z))
            # FQuat result(rotation.X, rotation.Y, rotation.Z, rotation.W);
            # result.z = -result.z
            # result.y = -result.y
            preModifier = Euler((0, 0, 0), 'XYZ').to_quaternion()
            postModifier = Euler((0, 90, 0), 'XYZ').to_quaternion()
            unity_rotation = self.unity_default @ result
            # unity_rotation.x = -unity_rotation.x
            # unity_rotation.y = -unity_rotation.y
            # FQuat postModifier = FQuat::MakeFromEuler(FVector(0, 0, 180));
            # return modifier * result * postModifier;
            # print ("!!!!!!!!!!!!! " + str(result))
            # print ("_____________ " + str(unity_rotation))
            #            return rotation
            #            return rotation
            return preModifier @ result @ postModifier
        else:
            return Quaternion.identity()

    def get_quaternion_correct_rotation(self, quaternion):
        return self.Quaternion_fromUnity(quaternion)


matmul = (lambda a, b: a.__matmul__(b))


class BoneConverterPoseMode:
    def __init__(self, pose_bone):
        mat = pose_bone.matrix.to_3x3()
        mat[1], mat[2] = mat[2].copy(), mat[1].copy()
        self.__mat = mat.transposed()
        self.__mat_rot = pose_bone.matrix_basis.to_3x3()
        self.convert_rotation = self._convert_rotation

    def _convert_rotation(self, rota):
        rot = Quaternion((rota.w, rota.x, rota.y, rota.z))
        rot = Quaternion(matmul(self.__mat, rot.axis) * -1, rot.angle)
        return matmul(self.__mat_rot, rot.to_matrix()).to_quaternion()
