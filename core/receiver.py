
import bpy
import time
import socket
import traceback
from . import animations, utils, animation_handler, live_data_manager

error_temp = ''
show_error = []


# Starts UPD server and handles data received from Rokoko Studio
class Receiver:

    sock = None

    # Redraw counters
    i = -1    # Number of continuous received packets
    i_np = 0  # Number of continuous no packets

    # Error counters
    error_temp = []
    error_count = 0

    def __init__(self):
        self.animator = animation_handler.Animator()
        self.live_data_packet = None

    def run(self):
        data_raw = None
        received = True
        error = []
        force_error = False

        # Try to receive a packet
        try:
            data_raw, address = self.sock.recvfrom(65536)
        except BlockingIOError as e:
            print('Blocking error:', e)
            error = ['Receiving no data!']
        except OSError as e:
            print('Packet error:', e.strerror)
            error = ['Packets too big!']
            force_error = True
        except AttributeError as e:
            print('Socket error:', e)
            error = ['Socket not running!']
            force_error = True

        # start_time = time.time()

        # Process the packet
        if data_raw:
            # print('SIZE:', len(data_raw))
            # print('DATA:', data_raw)

            # Process animation data
            error, force_error = self.process_data(data_raw)

            # print(round((time.time() - start_time) * 1000, 4), 'ms')

        self.handle_ui_updates(received)
        self.handle_error(error, force_error)

    def process_data(self, data_raw) -> ([str], bool):
        """
        Processes the received data. If there was an error it returns a list of strings creating the error message
        and if the error should be forced to show immediately instead of after a couple of packages
        :param data_raw:
        :return:
        """
        try:
            animations.live_data.init(data_raw)
            # self.live_data_packet = live_data_manager.LiveDataPacket(data_raw)
        except ValueError as e:
            print('Packet contained no data')
            print(e)
            return ['Packets contain no data!'], False
        except (UnicodeDecodeError, TypeError) as e:
            print('Wrong live data format! Use JSON v2 or higher!')
            print(e)
            print(traceback.format_exc())
            return ['Wrong data format!', 'Use JSON v2 or higher!'], True
        except KeyError as e:
            print('KeyError:', e)
            return ['Incompatible JSON version!', 'Use the latest Studio', 'and plugin versions.'], True
        except ImportError as e:
            # This error is specifically when the operating system isn't supported
            if "os" in e.msg:
                print('Unsupported operating system!', 'Use JSON v2 or v3 in the', 'Custom panel in Rokoko Studio.')
                return ['Unsupported operating system!', 'Use JSON v2 or v3 in the', 'Custom panel in Rokoko Studio.'], True

            # This error occurs, when the LZ4 package could not be loaded while it was needed
            print('Unsupported Blender version or operating system! Use older Blender or JSON v2/v3.')
            print(e)
            return ['Unsupported Blender version', 'or operating system! Use', 'older Blender or JSON v2/v3.'], True

        animations.animate()

        # TODO: COMPLETE THIS:
        # self.animator.animate(self.live_data_packet)

        return None, False

    def handle_ui_updates(self, received):
        # Update UI every 5 seconds when packets are received continuously
        if received:
            self.i += 1
            self.i_np = 0
            if self.i % (bpy.context.scene.rsl_receiver_fps * 5) == 0:
                utils.ui_refresh_properties()
                utils.ui_refresh_view_3d()
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
        self.sock.setblocking(False)
        self.sock.bind(('', port))

        self.i = -1
        self.i_np = 0

        self.error_temp = []
        self.error_count = 0

        # self.animator.setup() # TODO

        global show_error
        show_error = False

        print("Rokoko Studio Live started listening on port " + str(port))

    def stop(self):
        self.sock.close()
        # self.animator.destroy()
        print("Rokoko Studio Live stopped listening")
