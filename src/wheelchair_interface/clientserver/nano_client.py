"""
file: nano_client.py

description: This program will take movement commands and send them over uart to the pi
"""
import serial
import socket
import pickle
import logging

from ..protocol.processor import encode_move_cmd
from ..protocol.resources import *


def send_command(command: bytearray, serial_device: serial.Serial) -> None:
    """
    Sends a command to the chair

    :param command: Bytes to send
    :param serial_device: Device to send the command to
    """
    serial_device.write(command)
    logging.info("Command sent successfully.")


def process_data(data: bytes, serial_device: serial.Serial) -> None:
    """
    Process the data received over the socket

    :param data: Bytes from the socket
    :param serial_device: Serial device to send move command
    """
    direction, duration = pickle.loads(data)
    logging.info(f"Received data: {data}")
    cmd = encode_move_cmd(direction, duration)
    cmd.append(ord('\n'))
    logging.info(f"Sending command: {cmd}...")
    send_command(cmd, serial_device)


def main():
    """
    Main function responsible for sending the move commands to the wheelchair
    """
    with serial.Serial(NANO_DEVICE, BAUD_RATE, timeout=1) as serial_device, \
            socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_device:
        logging.info(f"Opening socket connection on: {SOCKET_HOST}:{SOCKET_PORT}")
        socket_device.bind((SOCKET_HOST, SOCKET_PORT))
        socket_device.listen(1)

        while True:
            logging.info("Waiting for connection...")
            conn, addr = socket_device.accept()
            logging.info(f"Connection from {addr}.")

            with conn:
                while True:
                    logging.info("Listening for command...")
                    data = conn.recv(1024)
                    if not data:
                        break

                    process_data(data, serial_device)


if __name__ == "__main__":
    main()
