#defining plugin informations visible when user adds it in user preferences
bl_info = {"name": "Smartsuit", "author": "Rokoko", "category": "Animation"}

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
        self.stomach_sensor          = 1
        self.chest_sensor            = 2
        self.neck_sensor             = 3
        self.head_sensor             = 129
        self.left_shoulder_sensor    = 130
        self.left_arm_sensor         = 131
        self.left_forearm_sensor     = 161
        self.left_hand_sensor        = 162
        self.right_shoulder_sensor   = 163
        self.right_arm_sensor        = 64
        self.right_forearm_sensor    = 33
        self.right_hand_sensor       = 34
        self.left_upleg_sensor       = 35
        self.left_leg_sensor         = 36
        self.left_foot_sensor        = 97
        self.right_upleg_sensor      = 98
        self.right_leg_sensor        = 99
        self.right_foot_sensor       = 100
        
        
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
                print("                 SUIT ID: " + str(suitID))
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
                    
                    print("Suit corresponds to selected one")
                    
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
                            frame.quaternion.append([w, x, y, z])
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
                            #send_frame_to_controller(suit.frames)
                            #print("returning")
                            #print(suit.get_frame_from_sensor(1))
                            
                            if suit.get_frame_from_sensor(1):
                                apply_animation(suit.get_frame_from_sensor(1))
                            
#                            for frame in suit.frames:
#                                if frame.get_sensor() == sensor:
#                                    return frames
                            
                            
                        except Exception as e:
                            print(e)
                else:
                    print("Suit doesn't corresponds to selected one")
            except:
                pass
        sock.shutdown(SHUT_RDWR)
        sock.close()
        
    def stop(self):
        print("stopping listener")
        self.running = False

receiver = SmartsuitReceiver()

def apply_animation(frame):
    print("APLLY ANIMMMM")
    print()
    print()

    for b in bpy.context.scene.objects.active.pose.bones:
        if (b.basename)
        print(b.basename)
        # use the decompose method
        loc, rot, sca = b.matrix_basis.decompose()
        # or use the to_quaternion method
        rot = b.matrix_basis.to_quaternion()
        print(rot)
        print()
    
#    ob = bpy.data.objects['Armature']
#    bpy.context.scene.objects.active = ob
#    bpy.ops.object.mode_set(mode='POSE')

#    pbone = ob.pose.bones[bname]
#    # Set rotation mode to Euler XYZ, easier to understand
#    # than default quaternions
#    pbone.rotation_mode = 'XYZ'
#    # select axis in ['X','Y','Z']  <--bone local
#    axis = 'Z'
#    angle = 120
#    pbone.rotation_euler.rotate_axis(axis, math.radians(angle))
#    bpy.ops.object.mode_set(mode='OBJECT')
#    #insert a keyframe
#    pbone.keyframe_insert(data_path="rotation_euler" ,frame=1)

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
        print("HERE")
        
        global rotation_offsets
        global character_rotations
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

                #store current character values
                global character_rotations
                character_rotations.character_hip               = arma.bones[sce.smartsuit_hip].matrix.to_quaternion()  #also try PoseBone.matrix_basis tp see the difference
                character_rotations.character_stomach           = arma.bones[sce.smartsuit_stomach].matrix.to_quaternion()
                character_rotations.character_chest             = arma.bones[sce.smartsuit_chest].matrix.to_quaternion()
                character_rotations.character_neck              = arma.bones[sce.smartsuit_neck].matrix.to_quaternion()
                character_rotations.character_head              = arma.bones[sce.smartsuit_head].matrix.to_quaternion()
                character_rotations.character_left_shoulder     = arma.bones[sce.smartsuit_leftShoulder].matrix.to_quaternion()
                character_rotations.character_left_arm          = arma.bones[sce.smartsuit_leftArm].matrix.to_quaternion()
                character_rotations.character_left_forearm      = arma.bones[sce.smartsuit_leftForearm].matrix.to_quaternion()
                character_rotations.character_left_hand         = arma.bones[sce.smartsuit_leftHand].matrix.to_quaternion()
                character_rotations.character_right_shoulder    = arma.bones[sce.smartsuit_rightShoulder].matrix.to_quaternion()
                character_rotations.character_right_arm         = arma.bones[sce.smartsuit_rightArm].matrix.to_quaternion()
                character_rotations.character_right_forearm     = arma.bones[sce.smartsuit_rightForearm].matrix.to_quaternion()
                character_rotations.character_right_hand        = arma.bones[sce.smartsuit_rightHand].matrix.to_quaternion()
                character_rotations.character_left_upleg        = arma.bones[sce.smartsuit_leftUpleg].matrix.to_quaternion()
                character_rotations.character_left_leg          = arma.bones[sce.smartsuit_leftLeg].matrix.to_quaternion()
                character_rotations.character_left_foot         = arma.bones[sce.smartsuit_leftFoot].matrix.to_quaternion()
                character_rotations.character_right_upleg       = arma.bones[sce.smartsuit_rightUpleg].matrix.to_quaternion()
                character_rotations.character_right_leg         = arma.bones[sce.smartsuit_rightLeg].matrix.to_quaternion()
                character_rotations.character_right_foot        = arma.bones[sce.smartsuit_rightFoot].matrix.to_quaternion()
                
            col = layout.column(align=True)
            col.enabled = context.scene.my_bool_property
            col.operator("button.initialize_skeleton")
            
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
        #self.root = [90,-90,0] #correct??
        self.hip =              Quaternion((-0.000000, 0.707, 0.707, 0.000000))
        self.stomach =          Quaternion((1.000, 0.000, 0.000, 0.000))
        self.chest =            Quaternion((1.000, 0.000, -0.000, 0.000))
        self.neck =             Quaternion((1.000, 0.000, -0.000, 0.000))
        self.head =             Quaternion((1.000, 0.000, 0.000, 0.000))
        self.left_shoulder =    Quaternion((1.000, 0.000, -0.000, -0.000))
        self.left_arm =         Quaternion((1.000, 0.000, -0.000000, -0.000000))
        self.left_forearm =     Quaternion((1.000, -0.000, -0.000, -0.00000))
        self.left_hand =        Quaternion((1.000, 0.000, 0.000000, 0.000001))
        self.right_shoulder =   Quaternion((1.000, -0.000, -0.000, 0.000))
        self.right_arm =        Quaternion((1.000, -0.000, 0.000001, 0.000001))
        self.right_forearm =    Quaternion((1.000, 0.000, -0.000, 0.0000000))
        self.right_hand =       Quaternion((1.000, 0.000, -0.000, 0.000))
        self.left_upleg =       Quaternion((1.000, -0.000, -0.000000, -0.000000))
        self.left_leg =         Quaternion((1.000, -0.000, 0.000000, 0.000000))
        self.left_foot =        Quaternion((1.000, 0.000001, -0.000001, -0.000))
        self.right_upleg =      Quaternion((1.000, -0.000, -0.000, 0.000000))
        self.right_leg =        Quaternion((1.000, 0.000, -0.000, -0.000000))
        self.right_foot =       Quaternion((1.000, 0.000000, 0.000000, -0.000))

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