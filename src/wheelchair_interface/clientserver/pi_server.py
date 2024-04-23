import serial
import threading
import logging
import queue
from ..rnet_controller.RNetController import RNetController
from ..protocol.processor import decode_move_cmd, InvalidCmdException
from ..protocol.resources import *




def process_command(controller: RNetController, command: bytearray) -> bool:
    """
    This will decide what needs to be run and send it to the correct function to send to the chair

    :param controller: Interface to the wheelchair
    :param command: The command to be processed by the wheelchair
    :return: If it could be processed and ran successfully
    """
    try:
        direction, duration = decode_move_cmd(command)
        controller.drive_direction_seconds(direction, duration)
        return True

    except InvalidCmdException as e:
        logging.error(e.message)
        return False


def process_commands(controller: RNetController, command_queue: queue.Queue):
    """
    Threaded function to pop commands and process them

    :param controller: Interface to the wheelchair
    :param command_queue: The queue to get the commands from
    """
    while True:
        if not command_queue.empty():
            command = command_queue.get()
            process_command(controller, command)
            command_queue.task_done()


def main():
    # Establish an RNET controller interface
    rnet_controller = None
    for _ in range(RECONNECTION_ATTEMPTS):
        logging.info("Attempting connection to wheelchair...")
        rnet_controller = RNetController()
        if rnet_controller.is_connected():
            logging.info("Wheelchair connected successfully.")
            break
        else:
            logging.error("Failed to connect to wheelchair")

    # Ensure successful connection
    if not rnet_controller.is_connected():
        logging.error(f"Failed to connect after {RECONNECTION_ATTEMPTS} attempts. Exiting..")
        return

    # Create a queue to store commands
    command_queue = queue.Queue()

    # Start the thread for processing commands
    thread = threading.Thread(target=process_commands, args=[rnet_controller, command_queue])
    thread.daemon = True
    thread.start()

    with serial.Serial(PI_DEVICE, BAUD_RATE) as serial_device:
        while True:
            # Grab the command
            received_command = serial_device.readline().decode().strip()

            if received_command:
                logging.info(f"Received command: {received_command}")
                # Add command to the queue
                command_queue.put(received_command)


if __name__ == "__main__":
    main()

