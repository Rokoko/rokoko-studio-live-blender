import bpy
import time

import numpy as np
from mathutils import Euler, Quaternion


def ui_refresh():
    # A way to refresh the ui
    refreshed = False
    while not refreshed:
        if hasattr(bpy.data, 'window_managers'):
            for windowManager in bpy.data.window_managers:
                for window in windowManager.windows:
                    for area in window.screen.areas:
                        print(windowManager.name, window, area)
                        area.tag_redraw()
            refreshed = True
            # print('Refreshed UI')
        else:
            time.sleep(0.5)


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