#defining plugin informations visible when user adds it in user preferences
bl_info = {"name": "Smartsuit", "author": "Rokoko", "category": "Animation"}

import bpy
from threading import Thread
from time import sleep
from random import randint
from mathutils import Vector
from socket import *
from enum import Enum

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

class SmartsuitReceiver():
    
    #chosenPort = 0

    def __init__(self):
        self.running = False
    
    def start(self):
        print("starting listener")
        self.running = True
        self.thread = Thread(target = self.run, args=[])
        self.thread.start()
    def run(self):
        UDP_IP = "" #"" or "localhost" ?
        UDP_PORT = 14041
        #UDP_PORT = chosenPort
        
        sock = socket(AF_INET, # Internet
                         SOCK_DGRAM) # UDP
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((UDP_IP, UDP_PORT))
        
        print ("Waiting on port: " + str(UDP_PORT))
        
        while self.running:
            try:
                data, addr = sock.recvfrom(2048) # buffer size is 1024 bytes
#                print ("received message:" + data.decode('utf-8'))
                #print(bpy.context.scene.smartsuit_bone)
                #print("thread running")
                #print(bpy.types.Scene.smartsuit_bone.data)
                ob = bpy.data.objects.get(bpy.context.scene.smartsuit_bone)#bpy.context.scene.objects.active
                #print("OB " + str(ob))
                # And you can rotate the object the same way
                ob.rotation_euler = (ob.rotation_euler.x + 1,ob.rotation_euler.y + 1,0)  # Note that you n
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

class HelloWorldPanel(bpy.types.Panel):   #change to modifier instead of panel
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

        #row = layout.row()
        #row.label(text="Streaming port")
        #row.prop(obj, "name")
        
        col = layout.column(align = True)
        col.prop(obj, "my_string_prop")
        #TODO MAKE THIS WORK
        #SmartsuitReceiver.chosenPort = obj.my_string_prop
        #print("!!!" + str(chosenPort))
        
#        col = layout.column()
#        col.prop(obj, "string")
#        col = layout.column()
#        col.prop(obj, "size")
#        col = layout.column()
#        col.operator("some.thing")
        
        if receiver.running:
            row = layout.row()
            row.operator("Smartsuit.stop_listener")
        else:
            row = layout.row()
            row.operator("smartsuit.start_listener")

        col = layout.column(align=True)
        col.operator("mesh.primitive_monkey_add", text="AddRig", icon='ERROR')

        row = layout.row()
        row.prop_search(context.scene, "smartsuit_bone", context.scene, "objects")
        row = layout.row()
        row.prop_search(context.scene, "smartsuit_hip", context.scene, "objects")
        #row = layout.row()
        #row.operator("mesh.primitive_cube_add")

# class Add_some_thing(Operator):

#     bl_idname = "some.thing"
#     bl_label = "Streaming port"
#     bl_description = "some description"

#     def execute(self, context):

#         # you need to get your stored properties
#         scene = context.object 
#         # you get some of your properties to use them
#         string = scene.string
#         size = scene.size

#         # you do some thing to use your property with
#         bpy.ops.mesh.primitive_cube_add()
#         # you can change some of the added object props as the defined in the ui property 
#         context.active_object.name = string 
#         context.active_object.scale = [size, size, size]
#         return {'FINISHED'}

# # your properties here
# class addon_Properties(PropertyGroup):

#     string = StringProperty(
#         name = "the name",
#         description="name of the object to add",
#         default = ""
#         )
#     size = FloatProperty(
#         name = "size",
#         description = "size of the object to add",
#         default = 1.0,
#         )  

class IgnitProperties(bpy.types.PropertyGroup):
    my_enum = bpy.props.EnumProperty(
        name = "My options",
        description = "My enum description",
        items = [
            ("Silver" , "Silver" , "Description..."),
            ("Gold", "Gold", "other description"),
            ("Space Grey", "Space Grey", "Some other description")            
        ],
        #update=update_after_enum()
    )
    # my_string = bpy.props.StringProperty()
    # my_integer = bpy.props.IntProperty()

    def update_after_enum(self, context):
        print('self.my_enum ---->', self.my_enum)


class IGLayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "IG Layout Demo"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        row.prop(scene.ignit_panel, "my_enum", expand=True)


#register and unregister all the relevant classes in the file
def register ():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.ignit_panel = bpy.props.PointerProperty(type=IgnitProperties)
    bpy.types.Object.my_string_prop = bpy.props.StringProperty \
      (
        name = "Streaming port",
        description = "My description",
        default = "default"
      )
    
def unregister ():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.ignit_panel
    del bpy.types.Object.my_string_prop

if __name__ == "__main__":
    register()

print("DONEEE")