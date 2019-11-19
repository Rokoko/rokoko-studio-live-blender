import bpy
import json
import socket
from threading import Thread


# class that handles data received from suits and decides is it is proper to use
# applies the animation when the start listener button is pressed
class Receiver:

    def run(self):
        data = None
        recieved = True

        try:
            data, address = self.sock.recvfrom(32768)  # Maybe up to 65536
        except BlockingIOError:
            recieved = False
            print('No packet')
        except OSError:
            recieved = False
            print('Packet too long')

        if recieved:
            # print('\n\n', data)
            # print('Got something')
            self.process_data(data)
            pass

    @staticmethod
    def process_data(data):
        json_data = json.loads(data)
        version = json_data['version']
        timestamp = json_data['timestamp']
        playbacktimestamp = json_data['playbackTimestamp']
        props = json_data['props']
        trackers = json_data['trackers']
        faces = json_data['faces']
        actors = json_data['actors']

    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)
        self.sock.bind(("127.0.0.1", port))

        print("SmartsuitPro started listening on port " + str(port))

    def __del__(self):
        self.sock.close()
        print("SmartsuitPro stopped listening")