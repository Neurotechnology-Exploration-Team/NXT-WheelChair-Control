import logging
import socket
import struct
import binascii

from time import time

# TODO Need to add function to send exploit?

def dec2hex(dec,hexlen):  #convert dec to hex with leading 0s and no '0x'
    h=hex(int(dec))[2:]
    l=len(h)
    if h[l-1]=="L":
        l-=1  #strip the 'L' that python int sticks on
    if h[l-2]=="x":
        h= '0'+hex(int(dec))[1:]
    return ('0'*hexlen+h)[l:l+hexlen]

class RNetController:
    """
    Class that will handle all communication to the can bus

    Authors:
        - Matt London

    Notes:
        - Written with reference to the can2RNET project licensed under GPL:
            Python canbus functions for R-net exploration by Specter and RedDragonX
    """
    def __init__(self, bus_num: int = 0):
        """
        Constructor for a controller, connects to the given bus number

        @param bus_num: Bus number to connect to
        """
        try:
            self.can_socket = self._open_connection(bus_num)

        except socket.error:
            self.can_socket = None

    @staticmethod
    def _open_connection(bus_num: int) -> socket.socket:
        """
        Open a connection to the bus and return the socket

        @param bus_num: Bus number to connect to (0 for the hat)
        @return: A socket with an open connection to the bus
        """
        bus_num = str(bus_num)

        # Attempt to open a socket
        try:
            can_socket = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        except socket.error:
            logging.error("Failed to create a canbus socket")
            raise socket.error

        # Attempt to connect to the canbus
        try:
            can_socket.bind((f"can{bus_num}",))
            logging.info(f"Socket connect to can: {bus_num}")
        except socket.error:
            logging.error(f"Failed to open can{bus_num} socket")
            logging.info(f"Attempting to open vcan{bus_num} socket")

            # Now we will try to connect to virtual can (vcan)
            try:
                can_socket.bind((f"vcan{bus_num}",))
                logging.info(f"Socket connected to vcan{bus_num}")
            except socket.error:
                logging.error(f"Failed to open vcan{bus_num} socket")
                raise socket.error

        return can_socket

    @staticmethod
    def _build_frame(can_string: str) -> bytes:
        """
        Build a data frame to send to the bus in the following format:

        FORMAT FOR CANSEND (matches candump -l)
            <can_id>#{R|data}          for CAN 2.0 frames
            <can_id>##<flags>{data}    for CAN FD frames

        @param can_string: Command string to build into a frame
        @return:
        """
        if "#" not in can_string:
            logging.error("Cannot build command frame: missing #")
            raise Exception("Must have # in command string")

        can_split = can_string.split("#")
        can_id_len = len(can_split[0])

        rtr = "#R" in can_string
        if can_id_len == 3:
            can_id = struct.pack("I", int(can_split[0], 16) + 0x40000000 * rtr)
        elif can_id_len == 8:
            can_id = struct.pack("I", int(can_split[0], 16) + 0x80000000 + 0x40000000 * rtr)
        else:
            logging.error(f"Cannot build command frame: cansend frame id format error: {can_string}")
            raise Exception("Frame id format error")

        can_dlc = 0
        len_data_str = len(can_split[1])
        if not rtr and len_data_str <= 16 and not len_data_str & 1:
            can_data = binascii.unhexlify(can_split[1])
            can_dlc = len(can_data)
            can_data = can_data.ljust(8, b"\x00")
        elif not len_data_str or rtr:
            can_data = b"\x00\x00\x00\x00\x00\x00\x00\x00"
        else:
            logging.error(f"Cannot build command frame: data format error: {can_string}")
            raise Exception("Data format error")

        return can_id + struct.pack("B", can_dlc & 0xF) + b"\x00\x00\x00" + can_data

    @staticmethod
    def _dec2hex(decimal_num, hex_len):
        """
        Convert dec to hex with leading 0s and no '0x'

        @param decimal_num: Decimal number to convert
        @param hex_len: Number of hex digits you want final result to have (pads with 0)
        @return: Hex string with no leading '0x'
        """
        h = hex(int(decimal_num))[2:]
        l = len(h)
        if h[l - 1] == "L":
            l -= 1  # strip the 'L' that python int sticks on
        if h[l - 2] == "x":
            h = "0" + hex(int(decimal_num))[1:]
        return ("0" * hex_len + h)[l:l + hex_len]

    def _can_send(self, command_string: str) -> bool:
        """
        Send a command to the opened socket

        @param command_string: String to build into a command and send
        @return: If the command was sent successfully
        """
        if self.can_socket is None:
            logging.error("Cannot send command as no canbus socket is open")
            return False

        try:
            out = self._build_frame(command_string)

            self.can_socket.send(out)
            return True

        except socket.error:
            logging.error(f"Error sending CAN frame {command_string}")
            return False

    def drive_forward_seconds(self, seconds):
        start_time = time()
        stop_time = start_time + seconds
        self.set_speed_range(10)

        forward_frame = '02000000#' + dec2hex(0, 2) + dec2hex(60, 2)
        while time() < stop_time:
            self._can_send(forward_frame)

        stop_frame = '02000000#0000'

        # Send the stop command
        self._can_send(stop_frame)

    def set_speed_range(self, speed_range) -> bool:
        """
        Set the speed of the chair

        @param speed_range: Speed range to set (between 0 and 100)
        @return: Whether the speed was successfully set
        """
        if 0x00 <= speed_range <= 0x64:
            # TODO all IDs like the following should be set as constants once rather than hardcoded
            self._can_send("0a040100#" + self._dec2hex(speed_range, 2))
            return True
        else:
            logging.error(f"Invalid RNET SpeedRange: {speed_range}")
            return False

    def move_forward(self):
        """
        Move the chair forward
        """
        # Create forward frame
        forward_frame = '02000000#' + self._dec2hex(0, 2) + self._dec2hex(60, 2)

        # Send can frame
        self._can_send(forward_frame)

    def turn_left(self):
        """
        Turn the chair left
        """
        # TODO specify amount chair turns
        # TODO verify if this works
        left_frame = '02000000#' + self._dec2hex(400, 2) + self._dec2hex(0, 2)

        self._can_send(left_frame)

    def turn_right(self):
        """
        Turn the chair right
        """
        # TODO specify amount chair turns
        # TODO verify this as well
        right_frame = '02000000#' + self._dec2hex(200, 2) + self._dec2hex(0, 2)

        self._can_send(right_frame)

    def stop_chair(self):
        """
        Stop the chair's movement
        """
        # Create Stop frame
        stop_frame = '02000000#0000'

        # Send the stop command
        self._can_send(stop_frame)
