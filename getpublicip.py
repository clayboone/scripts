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
import requests

def get_public_ip(version=4):
    """
    Return the outside-global IPv4 address of this host as a string using
    the HTTPS flavor of httpbin.org. On error, return None.

    TODO:
        * Change over to using icanhazip instead of httpbin. httpbin won't
          support IPv6 at this time because it's deployed on Heroku and they
          don't support IPv6
    """
    result = None

    try:
        request = requests.get('https://httpbin.org/ip')
    except (requests.ConnectionError, requests.ConnectTimeout):
        pass

    if request.status_code == 200:
        for key, val in request.json().items():
            if key == 'origin':
                result = val
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
