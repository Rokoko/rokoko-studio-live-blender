import bpy
import requests


class CommandTest(bpy.types.Operator):
    bl_idname = 'rsl.command_test'
    bl_label = 'Test Command API'
    bl_description = 'Testing'
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            request = get_request('')
        except requests.exceptions.ConnectionError:
            self.report({'ERROR'}, 'Could not connect to Rokoko Studio!')
            return {'CANCELLED'}

        data = request.json()
        print(data)

        if is_error(self, data):
            return {'CANCELLED'}

        self.report({'INFO'}, 'Successfully tested!')
        return {'FINISHED'}


class StartCalibration(bpy.types.Operator):
    bl_idname = 'rsl.command_start_calibration'
    bl_label = 'Start Calibration'
    bl_description = 'Starts calibration of a specific Smartsuit Pro.'
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            request = post_request('/calibrate')
        except requests.exceptions.ConnectionError:
            self.report({'ERROR'}, 'Could not connect to Rokoko Studio!')
            return {'CANCELLED'}

        data = request.json()
        print(data)

        if is_error(self, data):
            return {'CANCELLED'}

        self.report({'INFO'}, 'Calibration started successfully!')
        return {'FINISHED'}


class Restart(bpy.types.Operator):
    bl_idname = 'rsl.command_restart'
    bl_label = 'Restart Smartsuit(s)'
    bl_description = 'Restarts one or all Smartsuit Pro\'s'
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            request = post_request('/restart')
        except requests.exceptions.ConnectionError:
            self.report({'ERROR'}, 'Could not connect to Rokoko Studio!')
            return {'CANCELLED'}

        data = request.json()
        print(data)

        if is_error(self, data):
            return {'CANCELLED'}

        self.report({'INFO'}, 'Smartsuits restarted successfully!!')
        return {'FINISHED'}


class StartRecording(bpy.types.Operator):
    bl_idname = 'rsl.command_start_recording'
    bl_label = 'Start Recording'
    bl_description = 'Starts recording all connected Smartsuit Pro\'s'
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            request = post_request('/recording/start')
        except requests.exceptions.ConnectionError:
            self.report({'ERROR'}, 'Could not connect to Rokoko Studio!')
            return {'CANCELLED'}

        data = request.json()
        print(data)

        if is_error(self, data):
            return {'CANCELLED'}

        self.report({'INFO'}, 'Recording started successfully!')
        return {'FINISHED'}


class StopRecording(bpy.types.Operator):
    bl_idname = 'rsl.command_stop_recording'
    bl_label = 'Stop Recording'
    bl_description = 'Stops recording all connected Smartsuit Pro\'s'
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            request = post_request('/recording/stop')
        except requests.exceptions.ConnectionError:
            self.report({'ERROR'}, 'Could not connect to Rokoko Studio!')
            return {'CANCELLED'}

        data = request.json()
        print(data)

        if is_error(self, data):
            return {'CANCELLED'}

        self.report({'INFO'}, 'Recording stopped successfully!')
        return {'FINISHED'}
    

def get_request(additions):
    scn = bpy.context.scene
    return requests.get(f'http://{scn.rsl_command_ip_address}:{scn.rsl_command_ip_port}/v1/{scn.rsl_command_api_key}' + additions)


def post_request(additions, json=None):
    if json is None:
        json = {}
    scn = bpy.context.scene
    return requests.post(f'http://{scn.rsl_command_ip_address}:{scn.rsl_command_ip_port}/v1/{scn.rsl_command_api_key}' + additions, json=json)


def is_error(self, data):
    if not data.get('response_code'):
        self.report({'ERROR'}, 'No response from Studio!')
        return True

    if data.get('response_code') != 'OK':

        if data.get('response_code') == 'INVALID_REQUEST':
            self.report({'ERROR'}, data.get('response_code') + '\n' + data.get('description') + ' Check your API key.')
            return True

        self.report({'ERROR'}, data.get('response_code') + '\n' + data.get('description'))
        return True
    return False
