from enum import IntEnum

PROTOCOL_LENGTH = 5
STX = 0xfe
ETX = 0xff

MIN_MANTISSA = 0x01
MAX_MANTISSA = 0xfd
MIN_EXPONENT = 0x00
MAX_EXPONENT = 0xfd
MIN_MILLISECONDS = MIN_MANTISSA * (10 ** MIN_EXPONENT)
MAX_MILLISECONDS = MAX_MANTISSA * (10 ** MAX_EXPONENT)


class Direction(IntEnum):
    FORWARD = 0x01,
    BACKWARD = 0x02,
    LEFT = 0x03,
    RIGHT = 0x04
