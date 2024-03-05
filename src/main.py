from rnet_controller.RNetController import RNetController
from brainflow import BoardShim, BrainFlowInputParams, BoardIds
import time
import numpy as np

def main():
    controller = RNetController(0)
    HELLO(controller)
    controller.close()


if __name__ == "__main__":
    main()


def HELLO(wheelchair:RNetController):


    # Initialize BrainFlow
    params = BrainFlowInputParams()
    # Update 'serial_port' with the actual COM port for your device
    params.serial_port = 'COM3'
    board_id = BoardIds.CYTON_BOARD.value  # Replace YOUR_BOARD_ID with your actual board ID
    board = BoardShim(board_id, params)

    # Start the session
    board.prepare_session()
    board.start_stream()

    # Accelerometer channel indices
    accel_channels = [9, 10, 11]  # X, Y, Z channels

    def calibrate_direction(prompt):
        input(f"Please tilt your head {prompt} and press Enter to continue...")
        # Collecting data for calibration
        time.sleep(2)  # Adjust the duration as needed
        data = board.get_board_data()  # This gets all data since the stream started
        accel_data = data[accel_channels]  # Extract accelerometer data

        # Calculate the average to mitigate noise
        avg_accel_data = np.mean(accel_data, axis=1)
        return avg_accel_data

    # Calibration phase
    print("Calibration phase. Follow the instructions on the screen.")
    forward_max = calibrate_direction("all the way forward")
    left_max = calibrate_direction("all the way to the left")
    right_max = calibrate_direction("all the way to the right")
    resting_state = calibrate_direction("to the resting position (look straight ahead)")

    # Calculate dynamic thresholds based on calibration
    FORWARD_THRESHOLD = (forward_max[0] + resting_state[0]) / 2
    LEFT_RIGHT_THRESHOLD = (np.abs(left_max[1] - resting_state[1]) + np.abs(right_max[1] - resting_state[1])) / 2
    controls = "stop"
    lastControl = controls
    try:
        print("Starting head tilt detection. Press Ctrl+C to exit.")
        while True:
            data = board.get_board_data()  # Continuously read data
            if data.size == 0:
                continue

            current_accel_data = np.mean(data[accel_channels], axis=1)
            x_diff = current_accel_data[0] - resting_state[0]
            y_diff = current_accel_data[1] - resting_state[1]

            # Determine the tilt direction based on calibrated thresholds
            if x_diff > FORWARD_THRESHOLD:
                print("Forward tilt detected")
                controls = "Right"
            elif y_diff < -LEFT_RIGHT_THRESHOLD:
                print("Left tilt detected")
                controls = "Left"
            elif y_diff > LEFT_RIGHT_THRESHOLD:
                print("Right tilt detected")
                controls = "Forward"
            else:
                controls = "stop"
            if controls != lastControl:
                if controls == "Forward":
                    wheelchair.drive_forward_seconds(1)
                elif controls == "Right":
                    wheelchair.turn_right_seconds(1)

                else:
                    wheelchair.stop_chair()


            time.sleep(0.1)  # Adjust as needed

    except KeyboardInterrupt:
        # Cleanup
        board.stop_stream()
        board.release_session()
