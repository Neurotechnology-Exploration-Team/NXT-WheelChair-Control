# Nano to Pi Direction Communication Protocol

## Usage
This protocol will go over communication from the Jetson Nano to the Raspberry Pi.
In the wheelchair project this allows the Jetson Nano to compute required direction and send it off to the Pi for chair control.
This communication protocol will be passed over UART.

## UART Settings
| Setting | Configuration |
|---------|---------------|
| Speed   | 115200        |


## Wiring
Since commands only need to be sent from the Nano to the Pi, we only need two wires as follows.

| Nano           | Pi           |
|----------------|--------------|
| GND            | GND          |
| TXD0 (GPIO 14) | RX (GPIO 15) |

## Protocol Specification
This protocol needs to send direction input over the wire

**Transmission:**

| Byte # | Content                | Hex       | Description               |
|--------|------------------------|-----------|---------------------------|
| 0      | STX                    | 0xfe      | Start byte                |
| 1      | Direction              | 0x01-0x04 | Direction to go           |
| 2      | Duration mantissa (ms) | 0x01-0xfd | Mantissa of move duration |
| 3      | Duration exponent (ms) | 0x00-0xfd | Exponent of move duration |
| 4      | ETX                    | 0xff      | End byte                  |

**Directions:**

| Hex  | Direction |
|------|-----------|
| 0x01 | Forwards  |
| 0x02 | Backwards |
| 0x03 | Left      |
| 0x04 | Right     |

## Example transmissions
Examples of valid transmissions to command the chair
### Move forwards for 4 seconds (4.0 * 10^3 ms)
```
0xfe 0x01 0x04 0x03 0xff
```

### Turn left for 0.2 seconds (2.0 * 10^2 ms)
```
0xfe 0x03 0x02 0x02 0xff
```