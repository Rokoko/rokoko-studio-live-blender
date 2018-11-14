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

#SUIT AND FRAME CLASSES ARE HANDLED HERE
class Suit():

    def __init__(self):
        self.name = ""
        self.frames = []
        
class Frame():
    
    def __init__(self):#SENSORS STRUCT
        addr = b'\xff'
        isAnotherSensorConnected = b'\xff'
        behaviour = b'\xff'
        command = b'\xff'
        
        acceleration = np.zeros([0.0,0.0,0.0])
        quaternion = np.zeros([0.0,0.0,0.0,0.0])
        gyro = np.zeros([0.0,0.0,0.0])
        magnetometer = np.zeros([0.0,0.0,0.0])
        microseconds = 0
        
        
#SRECEIVER IS HANDLED HERE
class SmartsuitReceiver():
    
    #chosenPort = 0

    def __init__(self):
        self.running = False
        self.port = 14041
        #self.chosenPort = bpy.types.Object.my_string_prop
    
    def start(self):
        #print(self.chosenPort)

        print("starting listener")
        self.running = True
        self.thread = Thread(target = self.run, args=[])
        self.thread.start()
    def run(self):
        UDP_IP = "" #"" or "localhost" ?
        UDP_PORT = self.port
        #UDP_PORT = chosenPort
        print("!!!!!!")
        print (bpy.types.Object.my_string_prop)
        
        sock = socket(AF_INET, # Internet
                         SOCK_DGRAM) # UDP
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((UDP_IP, UDP_PORT))
        
        print ("Waiting on port: " + str(UDP_PORT))
        
        while self.running:
            try:
                data, addr = sock.recvfrom(2048) # buffer size is 1024 bytes
                offset = 4
                suitname = (data[:offset-1]).decode('unicode_escape')
                
                sensors = (len(data) - offset) / 60

                current_index = offset
                suit = Suit()
                suit.name = suitname
                
                print (data)
                
                for i in range(int(sensors)):
                    frame = Frame()
                    
                    firstbuffer = data[current_index:current_index+offset]
                    print (firstbuffer)
                    intFirstbuffer = int.from_bytes(firstbuffer, byteorder='big', signed = False)
                    #intFirstBuffer = struct.unpack('i', data)[0]
                    print ("SENSOR: " + str(i))
                    print(intFirstbuffer & 0xff)
                    print((intFirstbuffer >> 8) & 0xff)
                    print((intFirstbuffer >> 16) & 0xff)
                    print((intFirstbuffer >> 24) & 0xff)
                    
                    frame.addr = (intFirstbuffer & 0xff)
                    frame.isAnotherSensorConnected = ((intFirstbuffer >> 8) & 0xff)
                    frame.behaviour = rint((intFirstbuffer >> 16) & 0xff)
                    frame.command = ((intFirstbuffer >> 24) & 0xff)

                    current_index += offset
                    #acceleration
                    x = struct.unpack('f', data[current_index:current_index+offset])[0]
                    print()
                    print("value")
                    print (x)
                    current_index += offset
                    y = struct.unpack('f', data[current_index:current_index+offset])[0]
                    current_index += offset
                    z = struct.unpack('f', data[current_index:current_index+offset])[0]
                    current_index += offset
                    frame.acceleration = np.zeros([x, y, z])
                    #quaternion
                    w = struct.unpack('f', data[current_index:current_index+offset])[0]
                    current_index += offset
                    x = struct.unpack('f', data[current_index:current_index+offset])[0]
                    current_index += offset
                    y = struct.unpack('f', data[current_index:current_index+offset])[0]
                    current_index += offset
                    z = struct.unpack('f', data[current_index:current_index+offset])[0]
                    current_index += offset
                    frame.quaternion = np.zeros([w, x, y, z])
                    #gyro
                    x = struct.unpack('f', data[current_index:current_index+offset])[0]
                    current_index += offset
                    y = struct.unpack('f', data[current_index:current_index+offset])[0]
                    current_index += offset
                    z = struct.unpack('f', data[current_index:current_index+offset])[0]
                    current_index += offset
                    frame.gyro = np.zeros([x, y, z])
                    #magnetometer
                    x = struct.unpack('f', data[current_index:current_index+offset])[0]
                    current_index += offset
                    y = struct.unpack('f', data[current_index:current_index+offset])[0]
                    current_index += offset
                    z = struct.unpack('f', data[current_index:current_index+offset])[0]
                    current_index += offset
                    frame.magnetometer = np.zeros([x, y, z])
                    #timestamp
                    frame.microseconds = struct.unpack('i', data[current_index:current_index+offset])
                    
                    #just keep the last frame
                    suit.frames.clear()
                    suit.frames.append(frame)
                    
                
#                try:
 #                   for i in range(sensors):
  #                      firstbuffer = int(data[offset:])
   #                     print()
    #                    print("BUFFER")
     #                   print(firstbuffer)
      #                  offster+=4
       #         except:
        #            print("Error")
                #print(data[3])
                #print(bpy.context.scene.smartsuit_bone)
                #print("thread running")
                #print(bpy.types.Scene.smartsuit_bone.data)
                ob = bpy.data.objects.get(bpy.context.scene.smartsuit_bone)#bpy.context.scene.objects.active
                ob =bpy.types.Object.my_string_prop #= bpy.props.StringProperty
                #print(type(ob))
                #print("OB " + str(ob))
                # And you can rotate the object the same way
                #ob.rotation_euler = (ob.rotation_euler.x + 1,ob.rotation_euler.y + 1,0)  # Note that you n
            except:
                pass
        sock.shutdown(SHUT_RDWR)
        sock.close()
        
    def stop(self):
        print("stopping listener")
        self.running = False

receiver = SmartsuitReceiver()

class SmartsuitProperty(bpy.types.PropertyGroup):

    bpy.types.Scene.smartsuit_bone = bpy.props.StringProperty("smartsuit_bone")
    bpy.types.Scene.smartsuit_hip = bpy.props.StringProperty("Hip")
    coll = bpy.props.CollectionProperty(
        type = bpy.types.PropertyGroup
    )


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


#UI IS HANDLED HERE
class IgnitProperties(bpy.types.PropertyGroup):
    my_enum = bpy.props.EnumProperty(
        name = "My options",
        description = "My enum description",
        items = [
            ("Receiver" , "Receiver" , "Description..."),
            ("Controller", "Controller", "other description"),
            #("Space Grey", "Space Grey", "Some other description")            
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
        
        if scene.ignit_panel.my_enum == 'Receiver':
            obj = context.object
            col = layout.column(align = True)
            col.prop(obj, "my_string_prop")
            obj
            if receiver.running:
                row = layout.row()
                row.operator("Smartsuit.stop_listener")
            else:
                row = layout.row()
                row.operator("smartsuit.start_listener")

        elif scene.ignit_panel.my_enum == 'Controller':
            col = layout.column(align=True)
            col.operator("mesh.primitive_monkey_add", text="AddRig", icon='ERROR')

            row = layout.row()
            row.prop_search(context.scene, "smartsuit_bone", context.scene, "objects")
            row = layout.row()
            row.prop_search(context.scene, "smartsuit_hip", context.scene, "objects")


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
    
def unregister ():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Object.ignit_panel
    del bpy.types.Object.my_string_prop

if __name__ == "__main__":
    register()

print("DONEEE")