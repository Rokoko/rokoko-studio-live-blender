#defining plugin informations visible when user adds it in user preferences
bl_info = {"name": "Smartsuit", "author": "Rokoko", "category": "Animation"}

import bpy
from threading import Thread
from time import sleep
from random import randint
from mathutils import Vector
from socket import *
from enum import Enum
import numpy as np
import struct

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

#SUIT AND FRAME CLASSES ARE HANDLED HERE
class Suit():

    def __init__(self):
        self.name = ""
        self.frames = []
        
class Frame():
    
    def __init__(self):
        self.addr = b'\xff'
        self.isAnotherSensorConnected = b'\xff'
        self.behaviour = b'\xff'
        self.command = b'\xff'
        
        self.acceleration = []
        self.quaternion = []
        self.gyro = []
        self.magnetometer = []
        self.microseconds = 0
        
        
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
                            frame = Frame()
                            firstbuffer = data[current_index:current_index+offset]
                            
                            intFirstbuffer = struct.unpack('I', data[current_index:current_index+offset])[0]
                            
                            frame.addr = struct.pack("B", intFirstbuffer & 0xff)
                            
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
                            
                            suit.frames.clear()
                            suit.frames.append(frame)
                            
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

class SmartsuitProperty(bpy.types.PropertyGroup):

    bpy.types.Scene.Hip = bpy.props.StringProperty("smartsuit_hip")
    bpy.types.Scene.Stomach = bpy.props.StringProperty("smartsuit_stomach")
    bpy.types.Scene.Chest = bpy.props.StringProperty("smartsuit_chest")
    bpy.types.Scene.Neck = bpy.props.StringProperty("smartsuit_neck")
    bpy.types.Scene.Head = bpy.props.StringProperty("smartsuit_head")
    bpy.types.Scene.Left_Shoulder = bpy.props.StringProperty("smartsuit_leftShoulder")
    bpy.types.Scene.Left_Arm = bpy.props.StringProperty("smartsuit_leftArm")
    bpy.types.Scene.Left_Forearm = bpy.props.StringProperty("smartsuit_leftForeArm")
    bpy.types.Scene.Left_Hand = bpy.props.StringProperty("smartsuit_leftHand")
    bpy.types.Scene.Right_Shoulder = bpy.props.StringProperty("smartsuit_rightShoulder")
    bpy.types.Scene.Right_Arm = bpy.props.StringProperty("smartsuit_rightArm")
    bpy.types.Scene.Right_Forearm = bpy.props.StringProperty("smartsuit_rightForearm")
    bpy.types.Scene.Right_Hand = bpy.props.StringProperty("smartsuit_rightHand")
    bpy.types.Scene.Left_Up_Leg = bpy.props.StringProperty("smartsuit_leftUpLeg")
    bpy.types.Scene.Left_Leg = bpy.props.StringProperty("smartsuit_leftLeg")
    bpy.types.Scene.Left_Foot = bpy.props.StringProperty("smartsuit_leftFoot")
    bpy.types.Scene.Right_Up_Leg = bpy.props.StringProperty("smartsuit_rightUpleg")
    bpy.types.Scene.Right_Leg = bpy.props.StringProperty("smartsuit_rightLeg")
    bpy.types.Scene.Right_Foot = bpy.props.StringProperty("smartsuit_rightFoot")
    
    coll = bpy.props.CollectionProperty(
        type = bpy.types.PropertyGroup
    )

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


class IGLayoutDemoPanel(bpy.types.Panel):
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
        row.prop(scene.ignit_panel, "my_enum", expand=True)
        
        global portNumber 
        global suitID
        
        if scene.ignit_panel.my_enum == 'Receiver':
            obj = context.object
            #ID bpy.types.Object.suit_id_prop
            col = layout.column(align = True)
            col.prop(obj, "suit_id_prop")
            suitID = obj.suit_id_prop
            #PORT
            col = layout.column(align = True)
            col.prop(obj, "my_string_prop")
            portNumber = obj.my_string_prop
            if receiver.running:
                row = layout.row()
                row.operator("Smartsuit.stop_listener")
            else:
                row = layout.row()
                row.operator("smartsuit.start_listener")

        elif scene.ignit_panel.my_enum == 'Controller':
            #col = layout.column(align=True)
            #col.operator("mesh.primitive_monkey_add", text="AddRig", icon='ERROR')

            row = layout.row()
            row.prop_search(context.scene, "Hip", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Stomach", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Chest", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Neck", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Head", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Left_Shoulder", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Left_Arm", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Left_Forearm", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Left_Hand", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Right_Shoulder", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Right_Arm", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Right_Forearm", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Right_Hand", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Left_Up_Leg", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Left_Leg", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Left_Foot", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Right_Up_Leg", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Right_Leg", context.scene, "objects", icon = 'BONE_DATA')
            row = layout.row()
            row.prop_search(context.scene, "Right_Foot", context.scene, "objects", icon = 'BONE_DATA')
            

#layout.prop(scene, "mychosenObject")

def scene_mychosenobject_poll(self, object):
    return object.type == 'CURVE'

#register and unregister all the relevant classes in the file
def register ():
    bpy.utils.register_module(__name__)
    bpy.types.Object.ignit_panel = bpy.props.PointerProperty(type=IgnitProperties)
    bpy.types.Object.my_string_prop = bpy.props.StringProperty \
      (
        name = "Streaming port",
        description = "My description",
        default = "default"
      )
      
    bpy.types.Object.suit_id_prop = bpy.props.StringProperty \
      (
        name = "Suit ID",
        description = "My description",
        default = "default"
      )
    
def unregister ():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Object.ignit_panel
    del bpy.types.Object.my_string_prop
    del bpy.types.Object.suit_id_prop

if __name__ == "__main__":
    register()