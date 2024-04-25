import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import time


import logging
import socket
import pickle

from wheelchair_interface.protocol.resources import *


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


if __name__ == "__main__":
    logging.error("Should not be run directly. Import its functionality.")







def headTilt():
	params = BrainFlowInputParams()
	params.serial_port = 'COM3'  # Change to the actual port
	board = BoardShim(BoardIds.CYTON_BOARD.value, params)
	board.prepare_session()
	board.start_stream()

	try:
		while True:
			data = board.get_board_data()
			if len(data[0])==0:
				print("CONTINUING")
				continue

			# Accelerometer data is on channels (X:9, Y:10, Z:11)
			accel_x = data[9][0]
			accel_y = data[10][0]
			accel_z = data[11][0]

			#print(f'Accelerometer X: {accel_x[0]}, Y: {accel_y[0]}, Z: {accel_z[0]}')

			if accel_y>=-.8:
				print("FORWARD")
				send_move_cmd(Direction.FORWARD, .25)
			elif abs(accel_x)>.05:
				if accel_x<-.05:
					print('LEFT')
					send_move_cmd(Direction.LEFT, .25)
				else:
					print("RIGHT")
					send_move_cmd(Direction.RIGHT, .25)
			else:
				print("REST")
				#send_move_cmd(Direction., .5)

			time.sleep(.5)

	except KeyboardInterrupt:
		print("Stopping the data stream...")

	finally:
		board.stop_stream()
		board.release_session()
if __name__ == "__main__":
	headTilt()