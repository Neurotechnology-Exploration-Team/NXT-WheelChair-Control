import logging
import math

from .resources import *


class InvalidTimeException(Exception):
    """
    Used to express that a time is not valid for the protocol
    """
    def __init__(self, message):
        self.message = message
        super(InvalidTimeException, self).__init__(message)


class InvalidCmdException(Exception):
    """
    Used to express that the command received does not match the protocol
    """
    def __init__(self, message):
        self.message = message
        super(InvalidCmdException, self).__init__(message)


def encode_time(seconds: float) -> tuple[int, int]:
    """
    Take a value of seconds and encode it to the mantissa, exponent form

    :param seconds: Duration to encode in seconds
    :return: (mantissa, exponent)
    """
    # Convert to milliseconds
    ms = round(seconds * 1000)

    # Make sure it is valid
    if ms < MIN_MILLISECONDS or ms > MAX_MILLISECONDS:
        raise InvalidTimeException(f"Milliseconds must be [{MIN_MILLISECONDS}, {MAX_MILLISECONDS:.2E}]")

    # Now get the exponent and mantissa
    exponent = 0
    mantissa = ms

    while mantissa % 10 == 0 or mantissa >= 256:
        mantissa //= 10
        exponent += 1

    return mantissa, exponent


def decode_time(mantissa: int, exponent: int) -> float:
    """
    Take value of mantissa and exponent and convert it to seconds

    :param mantissa: Mantissa of the number
    :param exponent: Power of ten of the number
    :return: Conversion to seconds
    """
    ms = mantissa * (10 ** exponent)
    seconds = ms / 1000

    return seconds


def is_valid_cmd(raw_cmd: bytearray) -> bool:
    """
    Make sure a raw command appears to follow the protocol

    :param raw_cmd: Command received over the wire
    :return: Whether it matches the protocol
    """
    cmd = list(raw_cmd)

    if len(cmd) != PROTOCOL_LENGTH:
        return False

    if cmd[0] != STX:
        return False

    if cmd[-1] != ETX:
        return False

    return True


def encode_move_cmd(direction: Direction, duration: float) -> bytearray:
    """
    Encode a move instruction to raw protocol for sending

    :param direction: Direction to instruct
    :param duration: Time to repeat that direction (seconds)
    :return: Bytearray suitable for sending over the wire
    """
    cmd = [0 for _ in range(PROTOCOL_LENGTH)]

    # Set start
    cmd[0] = STX

    # Set direction
    cmd[1] = int(direction)

    # Encode time
    mantissa, exponent = encode_time(duration)
    cmd[2] = mantissa
    cmd[3] = exponent

    # Set end
    cmd[-1] = ETX

    logging.debug(f"Encoded command as {cmd}")

    # Return the result converted to a byte array
    return bytearray(cmd)


def decode_move_cmd(raw_cmd: bytearray) -> tuple[Direction, float]:
    """
    Decode a raw move command into a direction and duration (seconds)

    :param raw_cmd: Raw bytes received over the wire
    :return: (Direction, duration in seconds)
    """
    # Make sure it is valid
    if not is_valid_cmd(raw_cmd):
        raise InvalidCmdException("Command received does not match protocol")

    cmd = list(raw_cmd)

    # Grab the direction
    direction = Direction(cmd[1])

    # Convert the time
    mantissa = cmd[2]
    exponent = cmd[3]
    duration = decode_time(mantissa, exponent)

    # Now we can return
    logging.debug(f"Decoded command as ({direction}, {duration})")

    return direction, duration
