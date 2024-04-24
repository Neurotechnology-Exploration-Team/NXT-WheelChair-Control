"""
file: WASD.py

description: Demonstration for using a keyboard to control the chair with WASD

author: Matt London
"""

import sys
import keyboard

from ..rnet_controller.RNetController import RNetController


DRIVE_TIME = 1
""" Time to drive for when each key is pressed """


def action(key, controller: RNetController) -> None:
    """
    Take an action and command the chair to move

    :param key: Key that is pressed
    :param controller: Controller to send commands to
    """
    if key == 'w':
        controller.drive_forward_seconds(DRIVE_TIME)
    elif key == 's':
        controller.drive_back_seconds(DRIVE_TIME)
    elif key == 'a':
        controller.turn_left_seconds(DRIVE_TIME)
    elif key == 'd':
        controller.turn_right_seconds(DRIVE_TIME)


def terminate(key, controller: RNetController) -> None:
    """
    When called, exit the program cleanly

    :param key: Key which is pressed (Will always be q)
    :param controller: Controller to stop and close
    """
    controller.stop_chair()
    controller.close()

    sys.exit(0)


def main():
    """
    Main program to take keyboard input
    """
    controller = RNetController(0)

    key_functions = {
        'w': action,
        'a': action,
        's': action,
        'd': action,
        'q': terminate
    }

    while True:
        for key, func in key_functions.items():
            if keyboard.is_pressed(key):
                while keyboard.is_pressed(key):
                    func(key, controller)


if __name__ == "__main__":
    main()
