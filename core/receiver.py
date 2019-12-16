import json
import socket
from . import animations, utils
import datetime
import time
import bpy

error_temp = ''
show_error = []


# Starts UPD server and handles data received from Rokoko Studio
class Receiver:

    sock = None
    data_raw = None

    # Redraw counters
    i = -1    # Number of continuous received packets
    i_np = 0  # Number of continuous no packets

    # Error counters
    error_temp = []
    error_count = 0

    def run(self):
        received = True
        error = []
        force_error = False

        # Try to recieve a packet
        try:
            data_raw2, address = self.sock.recvfrom(32768)  # Maybe up to 65536
        except BlockingIOError:
            received = False
            print('No packet')
            error = ['Receiving no data!']
        except OSError as e:
            received = False
            print('Packet error:', e.strerror)
            error = ['Packets too big!']
            force_error = True

        if received:
            self.data_raw = data_raw2
            # Process animation data
            error, force_error = self.process_data()

            # Advance animation frame
            if bpy.context.scene.rsl_recording:
                bpy.context.scene.frame_current += 1

        self.handle_ui_updates(received)
        self.handle_error(error, force_error)

    def process_data(self):
        if not self.data_raw:
            print('Packet contained no data')
            return ['Packets contain no data!'], False

        try:
            data = json.loads(self.data_raw)
        except UnicodeDecodeError:
            print('Wrong live data format! Use JSON v2!')
            return ['Wrong data format!', 'Use JSON v2 or higher!'], True

        if data['version'] < 2:
            print('Old json data version! Please use v2 or higher')
            return ['Old data format!', 'Use JSON v2 or higher!'], True

        # animations.timestamp = data['timestamp']
        # animations.playbacktimestamp = data['playbackTimestamp']
        animations.props = data['props']
        animations.trackers = data['trackers']
        animations.faces = data['faces']
        animations.actors = data['actors']

        animations.animate()

        return '', False

    def handle_ui_updates(self, received):
        # Update UI every 5 seconds when packets are received continuously
        if received:
            self.i += 1
            self.i_np = 0
            if self.i % (bpy.context.scene.rsl_receiver_fps * 5) == 0:
                utils.ui_refresh_properties()
            return

        # If receiving a packet after one second of no packets, update UI with next packet
        self.i_np += 1
        if self.i_np == bpy.context.scene.rsl_receiver_fps:
            self.i = -1

    def handle_error(self, error, force_error):
        global show_error
        if not error:
            self.error_count = 0
            if not show_error:
                return
            self.error_temp = []
            show_error = []
            utils.ui_refresh_view_3d()
            print('REFRESH')
            return

        if not self.error_temp:
            self.error_temp = error
            if force_error:
                self.error_count = bpy.context.scene.rsl_receiver_fps - 1
            return

        if error == self.error_temp:
            self.error_count += 1
        else:
            self.error_temp = error
            if force_error:
                self.error_count = bpy.context.scene.rsl_receiver_fps
            else:
                self.error_count = 0

        if self.error_count == bpy.context.scene.rsl_receiver_fps:
            show_error = self.error_temp
            utils.ui_refresh_view_3d()
            print('REFRESH')

    def start(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)
        self.sock.bind(("127.0.0.1", port))

        self.i = -1
        self.i_np = 0

        self.error_temp = []
        self.error_count = 0

        global show_error
        show_error = False

        print("Rokoko Studio Live started listening on port " + str(port))

    def stop(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

        print("Rokoko Studio Live stopped listening")
