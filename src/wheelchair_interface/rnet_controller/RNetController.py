import logging
import socket
import struct
import binascii

from time import time

from ..protocol.resources import Direction

class RNetController:
    """
    Class that will handle all communication to the can bus

    Authors:
        - Matt London

    Notes:
        - Written with reference to the can2RNET project licensed under GPL:
            Python canbus functions for R-net exploration by Specter and RedDragonX
    """
    MAX_POSITIVE = 100
    """ Max value to go forward or right """

    MAX_NEGATIVE = 400
    """ Max value to go back or left """

    DRIVE_FRAME_START = "02000000#"
    """ Start of the drive instruction frame """

    STOP_FRAME = f"{DRIVE_FRAME_START}0000"
    """ The whole of the stop frame """

    SPEED_FRAME_START = "0a040100#"
    """ Start of speed change instruction frame """

    MIN_SPEED = 0x00
    """ Minimum speed of the chair """

    MAX_SPEED = 0x64
    """ Maximum speed of the chair """

    def __init__(self, bus_num: int = 0):
        """
        Constructor for a controller, connects to the given bus number

        @param bus_num: Bus number to connect to
        """
        try:
            self._can_socket = self._open_connection(bus_num)

        except socket.error:
            self._can_socket = None

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
    def _dec2hex(decimal_num: int, hex_len: int) -> str:
        """
        Convert dec to hex with leading 0s and no '0x'

        @param decimal_num: Decimal number to convert
        @param hex_len: Number of hex digits you want final result to have (pads with 0)
        @return: Hex string with no leading '0x'
        """
        h = hex(int(decimal_num))[2:]
        l = len(h)
        if h[l - 1] == "L":
            l -= 1
        if h[l - 2] == "x":
            h = "0" + hex(int(decimal_num))[1:]
        return ("0" * hex_len + h)[l:l + hex_len]

    def _can_send(self, command_string: str) -> bool:
        """
        Send a command to the opened socket

        @param command_string: String to build into a command and send
        @return: If the command was sent successfully
        """
        if self._can_socket is None:
            logging.error("Cannot send command as no canbus socket is open")
            return False

        try:
            out = self._build_frame(command_string)

            self._can_socket.send(out)
            return True

        except socket.error:
            logging.error(f"Error sending CAN frame {command_string}")
            return False

    def _drive_seconds(self, seconds: float, x: int, y: int) -> None:
        """
        Function to drive the chair for a given number of seconds in a certain direction

        @param seconds: Number of seconds to continue in a given direction for
        @param x: Amount to aim in x
        @param y: Amount to aim in y
        """
        start_time = time()
        stop_time = start_time + seconds

        forward_frame = self.DRIVE_FRAME_START + self._dec2hex(x, 2) + self._dec2hex(y, 2)
        while time() < stop_time:
            self._can_send(forward_frame)

        # Send the stop command
        self.stop_chair()

    def drive_direction_seconds(self, direction: Direction, seconds: float) -> None:
        """
        Drive a direction for given timeframe

        :param direction: Direction to move in
        :param seconds: Time to move in that direction
        """
        if direction == Direction.FORWARD:
            self.drive_forward_seconds(seconds)
        elif direction == Direction.BACKWARD:
            self.drive_back_seconds(seconds)
        elif direction == Direction.LEFT:
            self.turn_left_seconds(seconds)
        elif direction == Direction.RIGHT:
            self.turn_right_seconds(seconds)

    def is_connected(self) -> bool:
        """
        Check if there is an established connection

        :return: If there is a current connection established over can
        """
        return self._can_socket is not None

    def drive_forward_seconds(self, seconds: float) -> None:
        """
        Drive max forward

        @param seconds: Time to drive for
        """
        self._drive_seconds(seconds, 0, self.MAX_POSITIVE)

    def drive_back_seconds(self, seconds: float) -> None:
        """
        Drive max back

        @param seconds: Time to drive for
        """
        self._drive_seconds(seconds, 0, self.MAX_NEGATIVE)

    def turn_left_seconds(self, seconds: float) -> None:
        """
        Turn max left

        @param seconds: Time to drive for
        """
        self._drive_seconds(seconds, self.MAX_NEGATIVE, 0)

    def turn_right_seconds(self, seconds: float) -> None:
        """
        Turn max right

        @param seconds: Time to drive for
        """
        self._drive_seconds(seconds, self.MAX_POSITIVE, 0)

    def set_speed_range(self, speed_range: int) -> bool:
        """
        Set the speed of the chair

        @param speed_range: Speed range to set (between 0 and 100)
        @return: Whether the speed was successfully set
        """
        if self.MIN_SPEED <= speed_range <= self.MAX_SPEED:
            self._can_send(self.SPEED_FRAME_START + self._dec2hex(speed_range, 2))
            return True
        else:
            logging.error(f"Invalid RNET SpeedRange: {speed_range}")
            return False

    def stop_chair(self) -> None:
        """
        Stop the chair's movement
        """
        # Send the stop command
        self._can_send(self.STOP_FRAME)

    def close(self) -> None:
        """
        Close the connection to the chair
        """
        self._can_socket.close()
        self._can_socket = None
