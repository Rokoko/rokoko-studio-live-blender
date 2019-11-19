import bpy
import socket
from threading import Thread


# class that handles data received from suits and decides is it is proper to use
# applies the animation when the start listener button is pressed
class Receiver:

    def run(self):
        recieved = True

        try:
            data = self.sock.recvfrom(32768)
        except BlockingIOError:
            recieved = False
            print('No packet')
        except OSError:
            recieved = False
            print('Packet too long')

        if recieved:
            print('\n\n', data)

    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(0)
        self.sock.bind(("127.0.0.1", port))

        print("SmartsuitPro started listening on port " + str(port))

    def __del__(self):
        self.sock.close()
        print("SmartsuitPro stopped listening")