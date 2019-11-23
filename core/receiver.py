import json
import socket
from . import animations


# Starts UPD server and handles data received from Rokoko Studio
class Receiver:

    sock = None

    def run(self):
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

    def start(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)
        self.sock.bind(("127.0.0.1", port))

        print("Rokoko Studio Live started listening on port " + str(port))

    def stop(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print("Rokoko Studio Live stopped listening")
