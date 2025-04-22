# NXT-WheelChair-Control
A library for controlling wheelchairs with R-Net technology used in the NXT Wheelchair project. Library code is based on the code written by redragonx in https://github.com/redragonx/can2RNET and refactored into an object-oriented format.

## Installation notes
Brainflow is very confusing to install. Install it by building from source. Build instructions [here](https://brainflow.readthedocs.io/en/stable/BuildBrainFlow.html#compilation-label) and Python installation instructions [here](https://brainflow.readthedocs.io/en/stable/BuildBrainFlow.html). This worked installing on the Pi. It must be built from source because they don't offer binaries for arm64.

## Usage Instructions
1. Connect a PiCan v2 Hat to a motorized wheelchair's can interface
2. Follow Raspberry Pi socket setup [here](https://github.com/redragonx/can2RNET?tab=readme-ov-file#raspberry-pi-setup)
3. Using `raspi_config` disable login over serial and enable hardward serial support
4. Run the main file on a Jetson Nano in client mode
   - `python3 main.py client`
5. Run the main file on the Raspberry Pi in server mode
   - `python3 main.py server`
6. Use the provided example socket command to direct the wheelchair on the Jetson Nano
   - Example function in `src/wheelchair_interface/clientserver/socket_client.py`


## Package breakdown
An explanation of each package within the `wheelchair_interface` main package.

### clientserver
The `clientserver` package handles the implementation of the protocol on the Raspberry Pi and Jetson Nano side.

- `nano_client.py`
  - Client which receives commands from a socket and passes them over UART to the Pi
- `pi_server.py`
  - Server which accepts commands over UART and passes them to the wheelchair
- `socket_client.py`
  - Contains functions to be called within the user's program to send socket commands on the Jetson Nano
### protocol
The `protocol` class contains implementation functions of the protocol discussed in `doc/piNanoProtocol.md`.

- `processor.py`
  - Implementation of encode and decode functions for sending instructions over UART
- `resources.py`
  - Common constants used in different files

### input_receivers
The `input_receivers` package contains example implementations of RNetController or receivers to be run independent and speak to the client in `clientserver`.

- `headtilt.py`
  - Interfaces with a head accelerometer and leverages the functionality of `clientserver`
- `WASD.py`
  - Runs independently of `clientserver` and speaks directly to the RNetController.

### rnet_controller
The `rnet_controller` package handles direct communication with the wheelchair through the can protocol.
It includes a class to abstract away specific bitstrings used to control the chair and instead gives it an object-oriented interface.

- `RNetController.py`
  - Class to abstract low-level communication into object-oriented class

#### Usage
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
