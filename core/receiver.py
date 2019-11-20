import bpy
import json
import socket
from . import animations


# class that handles data received from suits and decides is it is proper to use
# applies the animation when the start listener button is pressed
class Receiver:

    def run(self):
        data_raw = None
        recieved = True

        try:
            data_raw, address = self.sock.recvfrom(32768)  # Maybe up to 65536
        except BlockingIOError:
            recieved = False
            print('No packet')
        except OSError:
            recieved = False
            print('Packet too long')

        if recieved:
            self.process_data(json.loads(data_raw))

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

    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)
        self.sock.bind(("127.0.0.1", port))

        print("SmartsuitPro started listening on port " + str(port))

    def __del__(self):
        self.sock.close()
        print("SmartsuitPro stopped listening")
