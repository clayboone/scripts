#!/usr/bin/env python3
""" get_public_ip.py
This module finds the outside IP address of the current host.

It's intended to be used as an i3blocks command, so at most this program
should output exactly one line to stdout.

I've also decided to print 'service unreachable' instead of '0.0.0.0' for both
IPv4 and IPv6. It's lowercase becaseu the default i3 font doesn't like upper-
case characters on my screen. And it's english rather than zeros for two rea-
sons:
    * 0.0.0.0 is ambiguous because it's the 'any' address in most config files
    * I don't know the IPv6 equivalent to IPv4's 0.0.0.0; it's probably [::],
      or somehting similar, which is a far enough departure from a typical-
      looking v6 address that it doesn't really make sense to have in the i3-
      blocks status bar area.
"""

import sys
import argparse
import socket
from contextlib import contextmanager

@contextmanager
def open_tcp_connection(host, port, version=6):
    """Attempt to connect to host on port over TCP.

    Args:
        host (str): The address of the host to connect to.
        port (int): The port to connect to on host.
        version (int): Internet Protocol version to use.

    Yield (socket.socket) on success, False otherwise
    """
    if version == 4:
        sock = socket.socket(family=socket.AF_INET)
    else:
        sock = socket.socket(family=socket.AF_INET6)

    try:
        sock.connect((host, port))
    except OSError:
        sock = False

    if sock:
        yield sock
        sock.close()

def get_public_ip(version=6):
    """Return the outside IP address of this host as a string using the
    icanhazip.com service.

    Args:
        version (int): The Internet Protocol version number to find.

    Return (str or None): An IP address string.
    """
    result = None
    with open_tcp_connection('icanhazip.com', 80, version) as sock:
        sock.send(b'GET / HTTP/1.1\r\nHost: icanhazip.com\r\n\r\n')
        message = sock.recv(2048)

    result = str(message, encoding='utf-8').splitlines()[-1]
    return result

def main(argv):
    """Program entry point

    Args:
        argv (list): Unparsed arguments passed to program
    """
    parser = argparse.ArgumentParser(
        description='Print the public IP address of this host',
        epilog=('If --auto is specified, first attempt to retrieve IPv6 '
                'address. Then fall back to IPv4 if that fails. (default=auto)')
        )
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument(
        '-a', '--auto', action='store_const', const=0, dest='ip_version',
        default=0)
    version_group.add_argument(
        '-4', '--ipv4', action='store_const', const=4, dest='ip_version')
    version_group.add_argument(
        '-6', '--ipv6', action='store_const', const=6, dest='ip_version')
    args = parser.parse_args(argv)

    if args.ip_version == 0:
        for version in [6, 4]:
            address = get_public_ip(version)
            if address:
                break
        else:
            address = 'service unreachable (auto)'
    else:
        address = get_public_ip(args.ip_version) or 'service unreachable'

    print('{}'.format(address))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
