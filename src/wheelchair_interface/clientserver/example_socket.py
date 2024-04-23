import socket
import pickle

from ..protocol.resources import *


def send_move_cmd(direction: Direction, duration: float, host=SOCKET_HOST, port=SOCKET_PORT) -> None:
    """
    Send a move command to the nano interface over socket

    :param direction: Direction to move
    :param duration: Time to move
    :param host: Socket host address (set default)
    :param port: Socket port (set default)
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        # Encode it into data
        data = pickle.dumps((int(direction), duration))

        # Send over the socket
        client_socket.sendall(data)


def main():
    # Test send move forward for 1 second
    send_move_cmd(Direction.FORWARD, 1)


if __name__ == "__main__":
    main()
