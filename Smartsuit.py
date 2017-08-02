import bpy
from threading import Thread
from time import sleep
from random import randint
from mathutils import Vector
import socket

class SmartsuitReceiver():

    def __init__(self):
        self.running = False
    
    def start(self):
        print("starting listener")
        self.running = True
        self.thread = Thread(target = self.run, args=[])
        self.thread.start()
    def run(self):
        UDP_IP = "0.0.0.0"
        UDP_PORT = 14041
        
        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        sock.bind((UDP_IP, UDP_PORT))
        
        while self.running:
            try:
                data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
#                print ("received message:" + data.decode('utf-8'))
                #print(bpy.context.scene.smartsuit_bone)
                #print("thread running")
                #print(bpy.types.Scene.smartsuit_bone.data)
                ob = bpy.data.objects.get(bpy.context.scene.smartsuit_bone)#bpy.context.scene.objects.active

                # And you can rotate the object the same way
                ob.rotation_euler = (ob.rotation_euler.x + 1,ob.rotation_euler.y + 1,0)  # Note that you n
            except:
                pass
        sock.shutdown(socket.SHUT_RDWR)
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

class HelloWorldPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Smartsuit Pro Panel"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def threaded(self):
        for i in range(0, 100):
            sleep(10)
            

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Hello world!", icon='WORLD_DATA')

        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        row = layout.row()
        row.prop(obj, "name")
        
        if receiver.running:
            row = layout.row()
            row.operator("Smartsuit.stop_listener")
        else:
            row = layout.row()
            row.operator("smartsuit.start_listener")
                
        row = layout.row()
        row.prop_search(context.scene, "smartsuit_bone", context.scene, "objects")
        row = layout.row()
        row.prop_search(context.scene, "smartsuit_hip", context.scene, "objects")

        #row = layout.row()
        #row.operator("mesh.primitive_cube_add")


bpy.utils.register_module(__name__)
