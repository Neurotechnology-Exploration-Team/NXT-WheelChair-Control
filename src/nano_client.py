"""
file: nano_client.py

description: This program will take movement commands and send them over uart to the pi
"""
import serial

DEVICE = "/dev/ttyTHS1"
BAUD_RATE = 115200


def send_command(command: list[int], serial_device: serial.Serial):
    """
    Sends a command to the chair

    :param command: List of bytes to send
    :param serial_device: Device to send the command to
    """
    # TODO Make sure this works
    serial_device.write(bytearray(command))
    print(f"Sent command: {command}")


def main():
    """
    Main function responsible for sending the move commands to the wheelchair
    """
    serial_device = serial.Serial(DEVICE, BAUD_RATE, timeout=1)
    while True:
        # TODO Placeholder
        # Example moves forward for 4 seconds
        command = [0xfe, 0x01, 0x04, 0x03, 0xff]
        send_command(command, serial_device)


if __name__ == "__main__":
    main()
