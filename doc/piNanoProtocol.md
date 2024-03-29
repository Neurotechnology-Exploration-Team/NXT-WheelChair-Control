# Nano to Pi Direction Communication Protocol

## Usage
This protocol will go over communication from the Jetson Nano to the Raspberry Pi.
In the wheelchair project this allows the Jetson Nano to compute required direction and send it off to the Pi for chair control.
This communication protocol will be passed over UART.

## UART Settings
| Setting | Configuration |
|---------|---------------|
| Speed   | 115200        |
|         |               |


## Wiring
Since commands only need to be sent from the Nano to the Pi, we only need two wires as follows.

| Nano           | Pi           |
|----------------|--------------|
| GND            | GND          |
| TXD0 (GPIO 14) | RX (GPIO 15) |
