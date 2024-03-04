# NXT-WheelChair-Control
A library for controlling wheelchairs with R-Net technology used in the NXT Wheelchair project. Library code is based on the code written by redragonx in https://github.com/redragonx/can2RNET and refactored into an object-oriented format.

## Usage
The `RNetController` class implements the code in an object-oriented format. Once instantiated with the bus number the following functions are available for use:
- `drive_forward_seconds`
- `drive_back_seconds`
- `turn_left_seconds`
- `turn_right_seconds`

Each have the calling convention of `function(seconds: int)`, where `seconds` is the amount of time you want the action to repeat.

Other less explanatory functions are as follows:
- `set_speed_range`
  - Takes an integer `0` through `100` which sets the wheelchair speed to that number.
- `stop_chair`
  - Takes no arguments.
  - Sends a stop command to the wheelchair, though it should stop on its own after a move timer expires.
- `close`
  - Takes no arguments
  - Closes the open socket with the can system. Always good practice to close connections.
