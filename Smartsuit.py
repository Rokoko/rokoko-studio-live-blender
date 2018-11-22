#defining plugin informations visible when user adds it in user preferences
bl_info = {"name": "Smartsuit", "author": "Rokoko", "category": "Animation"}

#import FBX primary: Y secondary: X - correct for edit mode but not pose mode

import bpy
from bpy.props import BoolProperty
from threading import Thread
from time import sleep
from random import randint
from socket import *
from enum import Enum
import numpy as np
import struct
import mathutils
from mathutils import Quaternion 
import math

from bpy.types import(
        Panel,
        Operator,
        PropertyGroup
        )

from bpy.props import(
        StringProperty,
        PointerProperty,
        FloatProperty
        )

portNumber = 0
suitID = "default"
initial_suitname = "default"

enable_component = True

class CharacterRotations():
    def __init__(self):
        self.character_hip              = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_stomach          = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_chest            = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_neck             = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_head             = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_left_shoulder    = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_left_arm         = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_left_forearm     = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_left_hand        = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_right_shoulder   = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_right_arm        = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_right_forearm    = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_right_hand       = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_left_upleg       = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_left_leg         = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_left_foot        = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_right_upleg      = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_right_leg        = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.character_right_foot       = Quaternion((0.0, 0.0, 0.0, 0.0))
        
#character rotations
character_rotations = CharacterRotations()

class RotationOffsets():
    def __init__(self):
        self.offset_hip              = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_stomach          = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_chest            = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_neck             = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_head             = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_left_shoulder    = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_left_arm         = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_left_forearm     = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_left_hand        = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_right_shoulder   = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_right_arm        = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_right_forearm    = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_right_hand       = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_left_upleg       = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_left_leg         = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_left_foot        = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_right_upleg      = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_right_leg        = Quaternion((0.0, 0.0, 0.0, 0.0))
        self.offset_right_foot       = Quaternion((0.0, 0.0, 0.0, 0.0))

#character rotations
rotation_offsets = RotationOffsets()

#SUIT AND FRAME CLASSES ARE HANDLED HERE
class Suit():

    def __init__(self):
        self.name = ""
        self.frames = []
        
    def get_frame_from_sensor(self, sensor):
        for frame in self.frames:
            if frame.get_sensor() == sensor:
                return frame
        
class Frame():
    
    def __init__(self):
        self.addr = b'\xff'
        self.int_addr = -1
        self.isAnotherSensorConnected = b'\xff'
        self.behaviour = b'\xff'
        self.command = b'\xff'
        
        self.acceleration = []
        self.quaternion = []
        self.gyro = []
        self.magnetometer = []
        self.microseconds = 0
        
    def get_sensor(self):
        return self.int_addr
        
class SensorAddress():
    def __init__(self):
        self.hip_sensor              = 160
        self.stomach_sensor          = 161
        self.chest_sensor            = 162
        self.neck_sensor             = 163
        self.head_sensor             = 64
        self.left_shoulder_sensor    = 33
        self.left_arm_sensor         = 34
        self.left_forearm_sensor     = 35
        self.left_hand_sensor        = 36
        self.right_shoulder_sensor   = 97
        self.right_arm_sensor        = 98
        self.right_forearm_sensor    = 99
        self.right_hand_sensor       = 100
        self.left_upleg_sensor       = 1
        self.left_leg_sensor         = 2
        self.left_foot_sensor        = 3
        self.right_upleg_sensor      = 129
        self.right_leg_sensor        = 130
        self.right_foot_sensor       = 131
        self.addr_list               = [160,161,162,163,64,33,34,35,36,97,98,99,100,1,2,3,129,130,131]#[160,1,2,3,129,130,131,161,162,163,64,33,34,45,36,97,98,99,100]
    
address_map = SensorAddress()
        
        
#RECEIVER IS HANDLED HERE
class SmartsuitReceiver():

    def __init__(self):
        self.running = False
    
    def start(self):

        print("starting listener")
        self.running = True
        self.thread = Thread(target = self.run, args=[])
        self.thread.start()
    def run(self):
        UDP_IP = "" #"" or "localhost" ?
        
        if portNumber == 0:
            UDP_PORT = 14041
        else:
            UDP_PORT = portNumber
        
        sock = socket(AF_INET, # Internet
                         SOCK_DGRAM) # UDP
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((UDP_IP, int(UDP_PORT)))
        
        print ("Waiting on port: " + str(UDP_PORT))
        
        count = 0
        
        while self.running:
            try:
                data, addr = sock.recvfrom(2048) # buffer size is 2048 bytes
                offset = 4
                suitname = (data[:offset-1]).decode('unicode_escape')
                
                global suitID
                #print("                 SUIT ID: " + str(suitID))
                global initial_suitname
                if count == 0:
                    initial_suitname = (data[:offset-1]).decode('unicode_escape')
                    count+=1
                    print("                     INITIAL SUIT " + str(initial_suitname))
                
                correct_data = False
                
                if suitID != "default":
                    if suitID == suitname:
                        correct_data = True
                else:
                    if suitname == initial_suitname:
                        correct_data = True
            
                if correct_data:
                    sensors = (len(data) - offset) / 60
                    current_index = offset
                    suit = Suit()
                    
                    #print("Suit corresponds to selected one")
                    
                    for i in range(int(sensors)):
                        try:
                            
                            suit.frames.clear()
                            frame = Frame()
                            firstbuffer = data[current_index:current_index+offset]
                            
                            intFirstbuffer = struct.unpack('I', data[current_index:current_index+offset])[0]
                            
                            frame.addr = struct.pack("B", intFirstbuffer & 0xff)
                            frame.int_addr = intFirstbuffer & 0xff
                            
                            frame.isAnotherSensorConnected = bytes((intFirstbuffer >> 8) & 0xff)
                            frame.behaviour = bytes((intFirstbuffer >> 16) & 0xff)
                            frame.command = bytes((intFirstbuffer >> 24) & 0xff)

                            current_index += offset
                            #acceleration
                            x = struct.unpack('f', data[current_index:current_index+offset])[0]
                            current_index += offset
                            y = struct.unpack('f', data[current_index:current_index+offset])[0]
                            current_index += offset
                            z = struct.unpack('f', data[current_index:current_index+offset])[0]
                            current_index += offset
                            frame.acceleration.append([x, y, z])
                            #quaternion
                            w = struct.unpack('f', data[current_index:current_index+offset])[0]
                            current_index += offset
                            x = struct.unpack('f', data[current_index:current_index+offset])[0]
                            current_index += offset
                            y = struct.unpack('f', data[current_index:current_index+offset])[0]
                            current_index += offset
                            z = struct.unpack('f', data[current_index:current_index+offset])[0]
                            current_index += offset
                            frame.quaternion.append(Quaternion((w, x, y, z)))
                            #gyro
                            x = struct.unpack('f', data[current_index:current_index+offset])[0]
                            current_index += offset
                            y = struct.unpack('f', data[current_index:current_index+offset])[0]
                            current_index += offset
                            z = struct.unpack('f', data[current_index:current_index+offset])[0]
                            current_index += offset
                            frame.gyro.append([x, y, z])
                            #magnetometer
                            x = struct.unpack('f', data[current_index:current_index+offset])[0]
                            current_index += offset
                            y = struct.unpack('f', data[current_index:current_index+offset])[0]
                            current_index += offset
                            z = struct.unpack('f', data[current_index:current_index+offset])[0]
                            current_index += offset
                            frame.magnetometer.append([x,y,z])
                            #timestamp
                            frame.microseconds = struct.unpack('I', data[current_index:current_index+offset])[0]
                            current_index += offset
                            
                            suit.frames.append(frame)
                            
                            for current_sensor in address_map.addr_list:
                                if suit.get_frame_from_sensor(current_sensor):
                                    apply_animation(suit.get_frame_from_sensor(current_sensor))

                        except Exception as e:
                            print(e)                      
                #else:
                    #print("Suit doesn't corresponds to selected one.  SuitID is " + str(suitID) + ".      Suitname is " + str(suitname)+ ".      Initial name is " + str(initial_suitname))
            except:
                pass
        sock.shutdown(SHUT_RDWR)
        sock.close()
        
    def stop(self):
        print("stopping listener")
        self.running = False

receiver = SmartsuitReceiver()

def apply_animation(frame):
    #print()
    #print(frame)
    global rotation_offsets
    global character_rotations
    
    not_found = True
    if not_found:
        for b in bpy.context.scene.objects.active.pose.bones:
            #print(b)
            #print(b.matrix_basis.to_quaternion())

            rot = b.matrix_basis.to_quaternion()
            
            b.rotation_mode = 'QUATERNION'
            
            sce = bpy.context.scene
            arma = bpy.data.armatures.get(sce.arma_name)
            #print(frame.get_sensor())
            #sensorBone.rotation*boneOffset
            
            #if frame.get_sensor() == 160 and b.basename == str(arma.bones[sce.smartsuit_hip].basename):
                #b.rotation_quaternion = frame.quaternion[0] * rotation_offsets.offset_hip
                #break
                #print("!!!!!!!!!!!  " + str(character_rotations.character_hip))
                #print("!!!!!!!!!!!  " + str(rotation_offsets.offset_hip))
                #print("!!!!!!!!!!!  " + str(character_rotations.character_hip * rotation_offsets.offset_hip))
            if frame.get_sensor() == 160 and b.basename == str(arma.bones[sce.smartsuit_hip].basename):
                b.rotation_quaternion == frame.quaternion[0] #* rotation_offsets.offset_hip
                #character_rotations.character_hip = character_rotations.character_hip * rotation_offsets.offset_hip
                #break
                not_found = False
            elif frame.get_sensor() == 161 and b.basename == str(arma.bones[sce.smartsuit_stomach].basename): #STOMACH
                #b.rotation_quaternion = character_rotations.character_stomach * rotation_offsets.offset_stomach
                #character_rotations.character_stomach = character_rotations.character_stomach * rotation_offsets.offset_stomach #* mathutils.Euler((0.0, math.radians(10.0), 0.0), 'XYZ').to_quaternion()
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_stomach
                #break
                not_found = False
            elif frame.get_sensor() == 162 and b.basename == str(arma.bones[sce.smartsuit_chest].basename): #CHEST
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_chest
                #break
                not_found = False
            elif frame.get_sensor() == 163 and b.basename == str(arma.bones[sce.smartsuit_neck].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_neck
                #break
                not_found = False
            elif frame.get_sensor() == 64 and b.basename == str(arma.bones[sce.smartsuit_head].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_head
                #break
                not_found = False
            elif frame.get_sensor() == 33 and b.basename == str(arma.bones[sce.smartsuit_leftShoulder].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_left_shoulder
                #break
                not_found = False
            elif frame.get_sensor() == 34 and b.basename == str(arma.bones[sce.smartsuit_leftArm].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_left_arm
                #break
                not_found = False
            elif frame.get_sensor() == 35 and b.basename == str(arma.bones[sce.smartsuit_leftForearm].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_left_forearm
                #break
                not_found = False
            elif frame.get_sensor() == 36 and b.basename == str(arma.bones[sce.smartsuit_leftHand].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_left_hand
                #break
                not_found = False
            elif frame.get_sensor() == 97 and b.basename == str(arma.bones[sce.smartsuit_rightShoulder].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_right_shoulder
                #break
                not_found = False
            elif frame.get_sensor() == 98 and b.basename == str(arma.bones[sce.smartsuit_rightArm].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_right_arm
                #break
                not_found = False
            elif frame.get_sensor() == 99 and b.basename == str(arma.bones[sce.smartsuit_rightForearm].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_right_forearm
                #break
                not_found = False
            elif frame.get_sensor() == 100 and b.basename == str(arma.bones[sce.smartsuit_rightHand].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_right_hand
                #break
                not_found = False
            elif frame.get_sensor() == 1 and b.basename == str(arma.bones[sce.smartsuit_leftUpleg].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_left_upleg
                #break
                not_found = False
            elif frame.get_sensor() == 2 and b.basename == str(arma.bones[sce.smartsuit_leftLeg].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_left_leg
                #break
                not_found = False
            elif frame.get_sensor() == 3 and b.basename == str(arma.bones[sce.smartsuit_leftFoot].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_left_foot
                #break
                not_found = False
            elif frame.get_sensor() == 129 and b.basename == str(arma.bones[sce.smartsuit_rightUpleg].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_right_upleg
                #break
                not_found = False
            elif frame.get_sensor() == 130 and b.basename == str(arma.bones[sce.smartsuit_rightLeg].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_right_leg
                #break
                not_found = False
            elif frame.get_sensor() == 131 and b.basename == str(arma.bones[sce.smartsuit_rightFoot].basename):
                b.rotation_quaternion = frame.quaternion[0] #* rotation_offsets.offset_right_foot
                #break
                not_found = False
            #else:
                #print ("PROBLEM " + str(frame.get_sensor()) + "     " + str(b.basename))

#LISTENERS ARE HANDLED HERE
class SmartsuitStartListener(bpy.types.Operator):
    bl_idname = "smartsuit.start_listener"
    bl_label = "Start Listener"
 
    def execute(self, context):
        receiver.start()
        return{'FINISHED'}   

class SmartsuitStopListener(bpy.types.Operator):
    bl_idname = "smartsuit.stop_listener"
    bl_label = "Stop Listener"
 
    def execute(self, context):
        receiver.stop()
        return{'FINISHED'}
    
class ButtonInitializeSkeleton(bpy.types.Operator):
    bl_idname = "button.initialize_skeleton"
    bl_label = "Initialize skeleton"
 
    def execute(self, context):
        
        print()
        print()
        print()
        print()
        print()
        
        global rotation_offsets
        global character_rotations
        
        for b in bpy.context.scene.objects.active.pose.bones:
            #print(b)
            # use the decompose method
            #loc, rot, sca = b.matrix_basis.decompose()
            # or use the to_quaternion method
            rot = b.matrix_basis.to_quaternion()
            b.rotation_mode = 'QUATERNION'
            #print(rot)
            #print()
            sce = context.scene
            arma = bpy.data.armatures.get(sce.arma_name)
            #print(arma.bones[sce.smartsuit_hip].basename)
            #print(arma.bones[sce.smartsuit_hip].matrix_local.to_quaternion())
            #print(b.basename)
            #print(b.matrix_basis.to_quaternion())
            #print(b.matrix_channel.to_quaternion())
            
            #store current character values
            if b.basename == str(arma.bones[sce.smartsuit_hip].basename):
                character_rotations.character_hip = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_stomach].basename):
                character_rotations.character_stomach = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_chest].basename):
                character_rotations.character_chest = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_neck].basename):
                character_rotations.character_neck = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_head].basename):
                character_rotations.character_head = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_leftShoulder].basename):
                character_rotations.character_left_shoulder = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_leftArm].basename):
                character_rotations.character_left_arm = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_leftForearm].basename):
                character_rotations.character_left_forearm = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_leftHand].basename):
                character_rotations.character_left_hand = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_rightShoulder].basename):
                character_rotations.character_right_shoulder = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_rightArm].basename):
                character_rotations.character_right_arm = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_rightForearm].basename):
                character_rotations.character_right_forearm = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_rightHand].basename):
                character_rotations.character_right_hand = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_leftUpleg].basename):
                character_rotations.character_left_upleg = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_leftLeg].basename):
                character_rotations.character_left_leg = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_leftFoot].basename):
                character_rotations.character_left_foot = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_rightUpleg].basename):
                character_rotations.character_right_upleg = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_rightLeg].basename):
                character_rotations.character_right_leg = rot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_rightFoot].basename):
                character_rotations.character_right_foot = rot
            else:
                print ("PROBLEM: " + str(b.basename))
            
        print("HERE")

        ideal_rotation = TPoseRotations()
        
        rotation_offsets.offset_hip               = ideal_rotation.hip.inverted() * character_rotations.character_hip
        rotation_offsets.offset_stomach           = ideal_rotation.stomach.inverted() * character_rotations.character_stomach
        rotation_offsets.offset_chest             = ideal_rotation.chest.inverted() * character_rotations.character_chest
        rotation_offsets.offset_neck              = ideal_rotation.neck.inverted() * character_rotations.character_neck
        rotation_offsets.offset_head              = ideal_rotation.head.inverted() * character_rotations.character_head
        rotation_offsets.offset_left_shoulder     = ideal_rotation.left_shoulder.inverted() * character_rotations.character_left_shoulder
        rotation_offsets.offset_left_arm          = ideal_rotation.left_arm.inverted() * character_rotations.character_left_arm
        rotation_offsets.offset_left_forearm      = ideal_rotation.left_forearm.inverted() * character_rotations.character_left_forearm
        rotation_offsets.offset_left_hand         = ideal_rotation.left_hand.inverted() * character_rotations.character_left_hand
        rotation_offsets.offset_right_shoulder    = ideal_rotation.right_shoulder.inverted() * character_rotations.character_right_shoulder
        rotation_offsets.offset_right_arm         = ideal_rotation.right_arm.inverted() * character_rotations.character_right_arm
        rotation_offsets.offset_right_forearm     = ideal_rotation.right_forearm.inverted() * character_rotations.character_right_forearm
        rotation_offsets.offset_right_hand        = ideal_rotation.right_hand.inverted() * character_rotations.character_right_hand
        rotation_offsets.offset_left_upleg        = ideal_rotation.left_upleg.inverted() * character_rotations.character_left_upleg
        rotation_offsets.offset_left_leg          = ideal_rotation.left_leg.inverted() * character_rotations.character_left_leg
        rotation_offsets.offset_left_foot         = ideal_rotation.left_foot.inverted() * character_rotations.character_left_foot
        rotation_offsets.offset_right_upleg       = ideal_rotation.right_upleg.inverted() * character_rotations.character_right_upleg
        rotation_offsets.offset_right_leg         = ideal_rotation.right_leg.inverted() * character_rotations.character_right_leg
        rotation_offsets.offset_right_foot        = ideal_rotation.right_foot.inverted() * character_rotations.character_right_foot

#        print(rotation_offsets.offset_hip)
#        print(rotation_offsets.offset_stomach)
#        print(rotation_offsets.offset_chest)
#        print(rotation_offsets.offset_neck)
#        print(rotation_offsets.offset_head)
#        print(rotation_offsets.offset_left_shoulder)
#        print(rotation_offsets.offset_left_arm)
#        print(rotation_offsets.offset_left_forearm)
#        print(rotation_offsets.offset_left_hand)
#        print(rotation_offsets.offset_right_shoulder)
#        print(rotation_offsets.offset_right_arm)
#        print(rotation_offsets.offset_right_forearm)
#        print(rotation_offsets.offset_right_hand)
#        print(rotation_offsets.offset_left_upleg)
#        print(rotation_offsets.offset_left_leg)
#        print(rotation_offsets.offset_left_foot)
#        print(rotation_offsets.offset_right_upleg)
#        print(rotation_offsets.offset_right_leg)
#        print(rotation_offsets.offset_right_foot)        

        return{'FINISHED'}

class ButtonRestoreTpose(bpy.types.Operator):
    bl_idname = "button.restore_tpose"
    bl_label = "Restore Tpose"
 
    def execute(self, context):
        print("RESTORE")
        
#        print(character_rotations.character_hip)
#        print(character_rotations.character_stomach)
#        print(character_rotations.character_chest)
#        print(character_rotations.character_neck)
#        print(character_rotations.character_head)
#        print(character_rotations.character_left_shoulder)
#        print(character_rotations.character_left_arm)
#        print(character_rotations.character_left_forearm)
#        print(character_rotations.character_left_hand)
#        print(character_rotations.character_right_shoulder)
#        print(character_rotations.character_right_arm)
#        print(character_rotations.character_right_forearm)
#        print(character_rotations.character_right_hand)
#        print(character_rotations.character_left_upleg)
#        print(character_rotations.character_left_leg)
#        print(character_rotations.character_left_foot)
#        print(character_rotations.character_right_upleg)
#        print(character_rotations.character_right_leg)
#        print(character_rotations.character_right_foot)
        
        
        for b in bpy.context.scene.objects.active.pose.bones:
            rot = b.matrix_basis.to_quaternion()
            b.rotation_mode = 'QUATERNION'
            sce = bpy.context.scene
            arma = bpy.data.armatures.get(sce.arma_name)
            #print(frame.get_sensor())
            #sensorBone.rotation*boneOffset
            
            if b.basename == str(arma.bones[sce.smartsuit_hip].basename):
                b.rotation_quaternion == character_rotations.character_hip
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_stomach].basename):
                b.rotation_quaternion = character_rotations.character_stomach
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_chest].basename):
                b.rotation_quaternion = character_rotations.character_chest
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_neck].basename):
                b.rotation_quaternion = character_rotations.character_neck
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_head].basename):
                b.rotation_quaternion = character_rotations.character_head
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_leftShoulder].basename):
                b.rotation_quaternion = character_rotations.character_left_shoulder
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_leftArm].basename):
                b.rotation_quaternion = character_rotations.character_left_arm
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_leftForearm].basename):
                b.rotation_quaternion = character_rotations.character_left_forearm
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_leftHand].basename):
                b.rotation_quaternion = character_rotations.character_left_hand
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_rightShoulder].basename):
                b.rotation_quaternion = character_rotations.character_right_shoulder
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_rightArm].basename):
                b.rotation_quaternion = character_rotations.character_right_arm
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_rightForearm].basename):
                b.rotation_quaternion = character_rotations.character_right_forearm
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_rightHand].basename):
                b.rotation_quaternion = character_rotations.character_right_hand
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_leftUpleg].basename):
                b.rotation_quaternion = character_rotations.character_left_upleg
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_leftLeg].basename):
                b.rotation_quaternion = character_rotations.character_left_leg
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_leftFoot].basename):
                b.rotation_quaternion = character_rotations.character_left_foot
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_rightUpleg].basename):
                b.rotation_quaternion = character_rotations.character_right_upleg
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_rightLeg].basename):
                b.rotation_quaternion = character_rotations.character_right_leg
                continue
            elif b.basename == str(arma.bones[sce.smartsuit_rightFoot].basename):
                b.rotation_quaternion = character_rotations.character_right_foot
                continue
        
        return{'FINISHED'}  
    
#Enable/Disable Operator
class ButtonEnableDisableComponent(bpy.types.Operator):
    bl_label = "Enable Component"
    bl_idname = "button.enable_disable_component"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
       #switch bool property to opposite. if you don't toggle just set to False
        global enable_component
        if enable_component:
            enable_component = False
            receiver.stop()
        else:
            enable_component = True
            receiver.stop()
        context.scene.my_bool_property = not context.scene.my_bool_property
        return {'FINISHED'}

#UI IS HANDLED HERE
class IgnitProperties(bpy.types.PropertyGroup):
    my_enum = bpy.props.EnumProperty(
        name = "My options",
        description = "My enum description",
        items = [
            ("Receiver" , "Receiver" , "Description..."),
            ("Controller", "Controller", "other description")        
        ],
        #update=update_after_enum()
    )
    #my_string = bpy.props.StringProperty()
    # my_integer = bpy.props.IntProperty()
    def update_after_enum(self):
        print('self.my_enum ---->', self.my_enum)


class SmartsuitProPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Smartsuit Pro Panel"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

   
    def draw(self, context):
        layout = self.layout
        scene = context.object
        
        row = layout.row()
        row.scale_y = 3.0
        enable_component
        if enable_component:
            layout.operator("button.enable_disable_component", text = "Disable Component")
        else:
            layout.operator("button.enable_disable_component", text = "Enable Component")
        
        row = layout.row()
        row.prop(scene.smartsuit_panel, "my_enum", expand=True)
        row.enabled = context.scene.my_bool_property
        
        global portNumber 
        global suitID
        
        if scene.smartsuit_panel.my_enum == 'Receiver':
            obj = context.object
            #ID bpy.types.Object.suit_id_prop
            col = layout.column(align = True)
            col.enabled = context.scene.my_bool_property
            col.prop(obj, "suit_id_prop")
            suitID = obj.suit_id_prop
            #PORT
            col = layout.column(align = True)
            col.enabled = context.scene.my_bool_property
            col.prop(obj, "streaming_port_property")
            portNumber = obj.streaming_port_property
            if receiver.running:
                row = layout.row()
                row.enabled = context.scene.my_bool_property
                row.operator("Smartsuit.stop_listener")
            else:
                row = layout.row()
                row.enabled = context.scene.my_bool_property
                row.operator("smartsuit.start_listener")

        elif scene.smartsuit_panel.my_enum == 'Controller':
            #col = layout.column(align=True)
            #col.operator("mesh.primitive_monkey_add", text="AddRig", icon='ERROR')
            
            
            sce = context.scene
            col = layout.column()
            col.enabled = context.scene.my_bool_property
            col.prop(sce, "arma", text = "Armature")

            col.prop_search(sce, "arma_name", bpy.data, "armatures", text="Armature name")
            arma = bpy.data.armatures.get(sce.arma_name)
            bonenames = ["smartsuit_hip", "smartsuit_stomach", "smartsuit_chest", "smartsuit_neck", \
                         "smartsuit_head", "smartsuit_leftShoulder", "smartsuit_leftArm", \
                         "smartsuit_leftForearm", "smartsuit_leftHand", "smartsuit_rightShoulder", \
                         "smartsuit_rightArm", "smartsuit_rightForearm", "smartsuit_rightHand", "smartsuit_leftUpleg", \
                         "smartsuit_leftLeg", "smartsuit_leftFoot", "smartsuit_rightUpleg", "smartsuit_rightLeg", "smartsuit_rightFoot" ]
            if arma is not None:
                #col.prop_search(sce, "bone_name", arma, "bones")
                col.prop_search(sce, "smartsuit_hip", arma, "bones", icon = 'BONE_DATA', text = "Hip")
                col.prop_search(sce, "smartsuit_stomach", arma, "bones", icon = 'BONE_DATA', text = "Stomach")
                col.prop_search(sce, "smartsuit_chest", arma, "bones", icon = 'BONE_DATA', text = "Chest")
                col.prop_search(sce, "smartsuit_neck", arma, "bones", icon = 'BONE_DATA', text = "Neck")
                col.prop_search(sce, "smartsuit_head", arma, "bones", icon = 'BONE_DATA', text = "Head")
                col.prop_search(sce, "smartsuit_leftShoulder", arma, "bones", icon = 'BONE_DATA', text = "Left Shoulder")
                col.prop_search(sce, "smartsuit_leftArm", arma, "bones", icon = 'BONE_DATA', text = "Left Arm")
                col.prop_search(sce, "smartsuit_leftForearm", arma, "bones", icon = 'BONE_DATA', text = "Left Forearm")
                col.prop_search(sce, "smartsuit_leftHand", arma, "bones", icon = 'BONE_DATA', text = "Left Hand")
                col.prop_search(sce, "smartsuit_rightShoulder", arma, "bones", icon = 'BONE_DATA', text = "Right Shoulder")
                col.prop_search(sce, "smartsuit_rightArm", arma, "bones", icon = 'BONE_DATA', text = "Right Arm")
                col.prop_search(sce, "smartsuit_rightForearm", arma, "bones", icon = 'BONE_DATA', text = "Right Forearm")
                col.prop_search(sce, "smartsuit_rightHand", arma, "bones", icon = 'BONE_DATA', text = "Right Hand")
                col.prop_search(sce, "smartsuit_leftUpleg", arma, "bones", icon = 'BONE_DATA', text = "Left Up Leg")
                col.prop_search(sce, "smartsuit_leftLeg", arma, "bones", icon = 'BONE_DATA', text = "Left Leg")
                col.prop_search(sce, "smartsuit_leftFoot", arma, "bones", icon = 'BONE_DATA', text = "Left Foot")
                col.prop_search(sce, "smartsuit_rightUpleg", arma, "bones", icon = 'BONE_DATA', text = "Right Up Leg")
                col.prop_search(sce, "smartsuit_rightLeg", arma, "bones", icon = 'BONE_DATA', text = "Right Leg")
                col.prop_search(sce, "smartsuit_rightFoot", arma, "bones", icon = 'BONE_DATA', text = "Right Foot")
                #print()
                #print()
                #print()
                #for bonename in bonenames:
                    #print ( bonename, tuple(math.degrees(a) for a in arma.bones[sce[bonename]].matrix.to_euler()))
                    #print ( bonename, arma.bones[sce[bonename]].matrix.to_euler().to_quaternion())
                
            col = layout.column(align=True)
            col.enabled = context.scene.my_bool_property
            col.operator("button.initialize_skeleton")
            
            col = layout.column(align=True)
            col.enabled = context.scene.my_bool_property
            col.operator("button.restore_tpose")

    
                
def work_bone():
     print("eheh")
            
def arma_items(self, context):
    obs = []
    for ob in context.scene.objects:
        if ob.type == 'ARMATURE':
            obs.append((ob.name, ob.name, ""))
    return obs

def arma_upd(self, context):
    self.arma_coll.clear()
    for ob in context.scene.objects:
        if ob.type == 'ARMATURE':
            item = self.arma_coll.add()
            item.name = ob.name

def bone_items(self, context):
    arma = context.scene.objects.get(self.arma)
    if arma is None:
        return
    return [(bone.name, bone.name, "") for bone in arma.data.bones]

class TPoseRotations():
    def __init__(self):
        self.hip =              Quaternion((0.0000, 1.0000, -0.0000, 0.0000))       # (179.9999640278213, -8.6514596632621e-06, -0.00010928302672020402)
        self.stomach =          Quaternion((0.0000, -0.0000, 1.0000, 0.0000))       # (-1.6627644312105827e-05, 179.999991348578, 6.329294126870617e-05)
        self.chest =            Quaternion((1.0000, -0.0000, 0.0000, -0.0000))      # (-3.166622691692359e-05, 5.008915419875408e-06, -2.7683269183022257e-12)
        self.neck =             Quaternion((1.0000, -0.0000, 0.0000, -0.0000))      # (-6.584304548521024e-05, -4.649582692995772e-12, -1.7302847674988336e-05)
        self.head =             Quaternion((1.0000, 0.0000, 0.0000, 0.0000))        # (0.00015898597751220708, -8.777585478335839e-14, 5.464151336010201e-05)
        self.left_shoulder =    Quaternion((0.7064, 0.0308, 0.0308, 0.7064))        # (5.000012234264331, -2.049056425315026e-05, 89.99996835353231)
        self.left_arm =         Quaternion((0.7064, -0.0308, 0.7064, -0.0308))      # (-90.00041231582837, 85.00002399427287, -90.00011178750489)
        self.left_forearm =     Quaternion((1.0000, 0.0000, 0.0000, 0.0000))        # (6.852871440756901e-05, 4.0580783691880345e-06, 4.923084207908311e-05)
        self.left_hand =        Quaternion((1.0000, -0.0000, -0.0000, -0.0000))     # (-1.6160629372008192e-05, -3.891070526730204e-05, -0.0001959952594585099)
        self.right_shoulder =   Quaternion((0.7071, -0.0000, 0.0000, -0.7071))      # (-2.659182443593447e-05, -8.777313143341238e-10, -89.99998884409983)
        self.right_arm =        Quaternion((0.7071, 0.0000, -0.7071, 0.0000))       # (9.229199187329988e-05, -89.99993420258647, 0.0)
        self.right_forearm =    Quaternion((1.0000, -0.0000, -0.0000, 0.0000))      # (-9.85182823577228e-05, -3.7664324460059345e-07, 2.521974800590258e-05)
        self.right_hand =       Quaternion((1.0000, 0.0000, -0.0000, -0.0000))      # (0.00020247717005401566, -2.4787370476730205e-06, -9.759400034329302e-06)
        self.left_upleg =       Quaternion((0.0000, -0.7071, -0.0000, -0.7071))     # (-179.99990938630796, -89.99993420258647, 0.0)
        self.left_leg =         Quaternion((1.0000, -0.0000, 0.0000, 0.0000))       #(-8.962425537623507e-05, -2.732068340007114e-05, 4.45268861807309e-05)
        self.left_foot =        Quaternion((0.7071, -0.0000, 0.7071, 0.0000))       # (-0.00017678782765272435, 89.99992054220813, 0.0)
        self.right_upleg =      Quaternion((0.0000, -0.7071, 0.0000, 0.7071))       #(-179.999991348578, 89.99989322145144, 0.0)
        self.right_leg =        Quaternion((1.0000, -0.0000, 0.0000, 0.0000))       #(-7.244569543242285e-05, -2.367822383577229e-05, 4.091792533789247e-05)
        self.right_foot =       Quaternion((0.7071, 0.0000, -0.7071, 0.0000))       # (5.3730861421926367e-05, -89.99998201391065, 0.0)

#register and unregister all the relevant classes in the file
def register ():
    bpy.utils.register_module(__name__)
    bpy.types.Object.smartsuit_panel = bpy.props.PointerProperty(type=IgnitProperties)
    bpy.types.Scene.my_bool_property = BoolProperty(name='My Bool Property', default = True)# create bool property for switching
    bpy.types.Object.streaming_port_property = bpy.props.StringProperty \
      (
        name = "Streaming port",
        description = "My description",
        default = "14041"
      )
      
    bpy.types.Object.suit_id_prop = bpy.props.StringProperty \
      (
        name = "Suit ID",
        description = "My description",
        default = "default"
      )
      
    bpy.types.Scene.arma = bpy.props.EnumProperty(items=arma_items, update=arma_upd)
    bpy.types.Scene.arma_name = bpy.props.StringProperty()
    bpy.types.Scene.smartsuit_hip = bpy.props.StringProperty("smartsuit_hip")
    bpy.types.Scene.smartsuit_stomach = bpy.props.StringProperty("smartsuit_stomach")
    bpy.types.Scene.smartsuit_chest = bpy.props.StringProperty("smartsuit_chest")
    bpy.types.Scene.smartsuit_neck = bpy.props.StringProperty("smartsuit_neck")
    bpy.types.Scene.smartsuit_head = bpy.props.StringProperty("smartsuit_head")
    bpy.types.Scene.smartsuit_leftShoulder = bpy.props.StringProperty("smartsuit_leftShoulder")
    bpy.types.Scene.smartsuit_leftArm = bpy.props.StringProperty("smartsuit_leftArm")
    bpy.types.Scene.smartsuit_leftForearm = bpy.props.StringProperty("smartsuit_leftForearm")
    bpy.types.Scene.smartsuit_leftHand = bpy.props.StringProperty("smartsuit_leftHand")
    bpy.types.Scene.smartsuit_rightShoulder = bpy.props.StringProperty("smartsuit_rightShoulder")
    bpy.types.Scene.smartsuit_rightArm = bpy.props.StringProperty("smartsuit_rightArm")
    bpy.types.Scene.smartsuit_rightForearm = bpy.props.StringProperty("smartsuit_rightForearm")
    bpy.types.Scene.smartsuit_rightHand = bpy.props.StringProperty("smartsuit_rightHand")
    bpy.types.Scene.smartsuit_leftUpleg = bpy.props.StringProperty("smartsuit_leftUpleg")
    bpy.types.Scene.smartsuit_leftLeg = bpy.props.StringProperty("smartsuit_leftLeg")
    bpy.types.Scene.smartsuit_leftFoot = bpy.props.StringProperty("smartsuit_leftFoot")
    bpy.types.Scene.smartsuit_rightUpleg = bpy.props.StringProperty("smartsuit_rightUpleg")
    bpy.types.Scene.smartsuit_rightLeg = bpy.props.StringProperty("smartsuit_rightLeg")
    bpy.types.Scene.smartsuit_rightFoot = bpy.props.StringProperty("smartsuit_rightFoot")
    
def unregister ():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Object.smartsuit_panel
    del bpy.types.Scene.my_bool_property
    del bpy.types.Object.streaming_port_property
    del bpy.types.Object.suit_id_prop
    
    del bpy.types.Scene.arma
    del bpy.types.Scene.arma_name
    del bpy.types.Scene.smartsuit_hip
    del bpy.types.Scene.smartsuit_stomach
    del bpy.types.Scene.smartsuit_chest
    del bpy.types.Scene.smartsuit_neck
    del bpy.types.Scene.smartsuit_head
    del bpy.types.Scene.smartsuit_leftShoulder
    del bpy.types.Scene.smartsuit_leftArm
    del bpy.types.Scene.smartsuit_leftForearm
    del bpy.types.Scene.smartsuit_leftHand
    del bpy.types.Scene.smartsuit_rightShoulder
    del bpy.types.Scene.smartsuit_rightArm
    del bpy.types.Scene.smartsuit_rightForearm
    del bpy.types.Scene.smartsuit_rightHand
    del bpy.types.Scene.smartsuit_leftUpleg
    del bpy.types.Scene.smartsuit_leftLeg
    del bpy.types.Scene.smartsuit_leftFoot
    del bpy.types.Scene.smartsuit_rightUpleg
    del bpy.types.Scene.smartsuit_rightLeg
    del bpy.types.Scene.smartsuit_rightFoot

if __name__ == "__main__":
    register()
    
print("DONE")