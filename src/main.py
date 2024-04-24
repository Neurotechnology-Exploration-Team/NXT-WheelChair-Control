"""
file: main.py

description: File that passes control to the correct server or client depending on platform

author: Matt London
"""
import sys
import logging

from wheelchair_interface.clientserver import pi_server, nano_client


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    if "server" in sys.argv:
        pi_server.main()
    elif "client" in sys.argv:
        nano_client.main()
    else:
        logging.error("Unrecognized command line option. Enter \"server\" or \"client\"")


if __name__ == "__main__":
    main()
