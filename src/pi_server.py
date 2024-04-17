import serial
import threading
import queue


DEVICE = "/dev/ttyS0"
BAUD_RATE = 115200


def process_command(command: bytearray):
    """
    This will decide what needs to be run and send it to the correct function to send to the chair

    :param command: The command to be processed by the wheelchair
    :return:
    """
    print(f"Processing command: {command}")


def process_commands(command_queue: queue.Queue):
    """
    Threaded function to pop commands and process them

    :param command_queue: The queue to get the commands from
    """
    while True:
        if not command_queue.empty():
            command = command_queue.get()
            process_command(command)
            command_queue.task_done()


def main():
    # Create a queue to store commands
    command_queue = queue.Queue()

    # Start the thread for processing commands
    thread = threading.Thread(target=process_commands, args=[command_queue])
    thread.daemon = True
    thread.start()

    with serial.Serial(DEVICE, BAUD_RATE, timeout=1) as serial_device:
        while True:
            # Grab the command
            received_command = serial_device.readline().decode().strip()

            if received_command:
                print(f"Received command: {received_command}")
                # Add command to the queue
                command_queue.put(received_command)

    # TODO add break clause


if __name__ == "__main__":
    main()

