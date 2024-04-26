"""
file: main.py

description: File that passes control to the correct server or client depending on platform

author: Matt London
"""
import sys
import logging

from wheelchair_interface.rnet_controller.RNetController import RNetController
from wheelchair_interface.clientserver import pi_server, nano_client
from wheelchair_interface.input_receivers import headtilt


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    if "server" in sys.argv:
        pi_server.main()
    elif "client" in sys.argv:
        nano_client.main()
    elif "headtilt" in sys.argv:
        headtilt.headTilt()
    elif "runcmd" in sys.argv:
        controller = RNetController(0)
        controller.set_speed_range(10)
        controller.close()
    else:
        logging.error("Unrecognized command line option. Enter \"server\" or \"client\"")


if __name__ == "__main__":
    main()
