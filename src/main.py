import sys

import wheelchair_interface.protocol
from wheelchair_interface.clientserver import pi_server, nano_client
import wheelchair_interface.rnet_controller


def main():
    if "server" in sys.argv:
        pi_server.main()
    elif "client" in sys.argv:
        nano_client.main()


if __name__ == "__main__":
    main()
