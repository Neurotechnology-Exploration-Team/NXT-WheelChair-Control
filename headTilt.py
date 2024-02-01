import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams
import numpy as np
import tkinter as tk
import time
def initialize_board():
    params = BrainFlowInputParams()
    params.serial_port = 'COM3'
    board_id = brainflow.BoardIds.CYTON_BOARD.value
    board = BoardShim(board_id, params)
    board.prepare_session()
    board.start_stream()
    return board

def zero_gyroscope(board):
    time.sleep(2)
    data = board.get_current_board_data(num_samples=1)
    gyro_data = data[9:12, :]  # Assuming gyroscope channels are at indices 9, 10, and 11
    #zero_point = gyro_data.mean(axis=1)
    return gyro_data

def get_gyroscope_data(board, zero_point):
    data = board.get_current_board_data(num_samples=1)
    gyro_data = data[9:12, :]  # Assuming gyroscope channels are at indices 9, 10, and 11
    #gyro_data = gyro_data - zero_point.reshape(-1, 1)
    return gyro_data

def predict_tilt(gyro_data, lr_threshold, fb_threshold):
    global zero_point
    tilt_direction = {"left_right": "No left/right tilt", "forward_backward": "No forward/backward tilt"}
    if gyro_data[0] > zero_point[0]+lr_threshold:
        tilt_direction["left_right"] = "Tilting right"
    elif gyro_data[0] < zero_point[0]-lr_threshold:
        tilt_direction["left_right"] = "Tilting left"
    if gyro_data[1] > zero_point[1]+fb_threshold:
        tilt_direction["forward_backward"] = "Tilting forward"
    elif gyro_data[1] < zero_point[1]-fb_threshold:
        tilt_direction["forward_backward"] = "Tilting backward"
    return tilt_direction

def increase_lr_threshold():
    global lr_threshold
    lr_threshold += 0.1
    lr_threshold_label.config(text=f'Left/Right Threshold: {lr_threshold}')

def increase_fb_threshold():
    global fb_threshold
    fb_threshold += 0.1
    fb_threshold_label.config(text=f'Forward/Backward Threshold: {fb_threshold}')

def update_data():
    global board, lr_threshold, fb_threshold
    gyro_data = get_gyroscope_data(board, zero_point)
    tilt_direction = predict_tilt(gyro_data, lr_threshold, fb_threshold)
    gyro_label.config(text=f'Gyro Data: {gyro_data.ravel()}')
    tilt_label.config(text=f'Left/Right: {tilt_direction["left_right"]}, Forward/Backward: {tilt_direction["forward_backward"]}')
    root.after(200, update_data)  # Update every 200 ms

if __name__ == '__main__':
    global zero_point
    lr_threshold = 0.2  # initial threshold for left/right tilt
    fb_threshold = 0.2  # initial threshold for forward/backward tilt
    
    board = initialize_board()
    zero_point = zero_gyroscope(board)
    
    root = tk.Tk()
    root.title('Gyroscope Data')
    root.geometry('400x400')  # Set the dimensions of the window to be a square
    
    gyro_label = tk.Label(root, text='Gyro Data: ')
    gyro_label.pack()
    
    tilt_label = tk.Label(root, text='Left/Right: , Forward/Backward: ')
    tilt_label.pack()
    
    lr_threshold_label = tk.Label(root, text=f'Left/Right Threshold: {lr_threshold}')
    lr_threshold_label.pack()
    
    fb_threshold_label = tk.Label(root, text=f'Forward/Backward Threshold: {fb_threshold}')
    fb_threshold_label.pack()
    
    lr_increase_button = tk.Button(root, text='Increase Left/Right Threshold', command=increase_lr_threshold)
    lr_increase_button.pack()
    
    fb_increase_button = tk.Button(root, text='Increase Forward/Backward Threshold', command=increase_fb_threshold)
    fb_increase_button.pack()
    
    root.after(200, update_data)  # Start updating data every 200 ms
    root.mainloop()
    board.stop_stream()
    board.release_session()
