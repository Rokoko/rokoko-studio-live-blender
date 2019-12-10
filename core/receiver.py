import json
import socket
from . import animations, utils
import datetime
import time
import bpy


# Starts UPD server and handles data received from Rokoko Studio
class Receiver:

    sock = None

    # Redraw counters
    i = -1
    i_np = 0

    def run(self):
        # start_time = time.clock()

        data_raw = None
        received = True

        try:
            data_raw, address = self.sock.recvfrom(32768)  # Maybe up to 65536
        except BlockingIOError:
            received = False
            print('No packet')
        except OSError as e:
            received = False
            print('Packet error:', e.strerror)

        if received:
            # Process animation data
            self.process_data(json.loads(data_raw))

            # Advance animation frame
            if bpy.context.scene.rsl_recording:
                bpy.context.scene.frame_current += 1

            # Update UI if neccessary
            self.i += 1
            self.i_np = 0
            if self.i % (bpy.context.scene.rsl_receiver_fps * 5) == 0:
                utils.ui_refresh_properties()
                pass
        else:
            self.i_np += 1
            if self.i_np == bpy.context.scene.rsl_receiver_fps:
                self.i = -1


        # end_time = time.clock()
        # delta = end_time - start_time
        # print()
        # print(start_time)
        # print(end_time)
        # print(time.clock(), delta, 60 / delta)

    @staticmethod
    def process_data(data):
        if not data:
            return

        # animations.version = self.json_data['version']
        # animations.timestamp = self.json_data['timestamp']
        # animations.playbacktimestamp = self.json_data['playbackTimestamp']
        animations.props = data['props']
        animations.trackers = data['trackers']
        animations.faces = data['faces']
        animations.actors = data['actors']

        animations.animate()

    def start(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)
        self.sock.bind(("127.0.0.1", port))

        self.i = -1
        self.i_np = 0

        print("Rokoko Studio Live started listening on port " + str(port))

    def stop(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print("Rokoko Studio Live stopped listening")
