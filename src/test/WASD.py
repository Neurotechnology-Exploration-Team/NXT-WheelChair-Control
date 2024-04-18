import sys

import keyboard

from src.wheelchair_interface.rnet_controller import RNetController


DRIVE_TIME = 1


def action(key, controller: RNetController):
    if key == 'w':
        controller.drive_forward_seconds(DRIVE_TIME)
    elif key == 's':
        controller.drive_back_seconds(DRIVE_TIME)
    elif key == 'a':
        controller.turn_left_seconds(DRIVE_TIME)
    elif key == 'd':
        controller.turn_right_seconds(DRIVE_TIME)


def terminate(key, controller: RNetController):
    controller.stop_chair()
    controller.close()

    sys.exit(0)


key_functions = {
    'w': action,
    'a': action,
    's': action,
    'd': action,
    'q': terminate
}


def main():
    controller = RNetController(0)

    while True:
        for key, func in key_functions.items():
            if keyboard.is_pressed(key):
                while keyboard.is_pressed(key):
                    func(key, controller)


if __name__ == "__main__":
    main()
