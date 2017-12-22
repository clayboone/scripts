#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""connect_scan.py

Port scan some hosts by attempting to establish a TCP connection.

Requirements:
    pygments >= 2.2.0
"""
import sys
import argparse
import socket
from contextlib import contextmanager

# import pygments

@contextmanager
def open_tcp_connection(host, port, timeout=0.4):
    """Attempt to connect to host on port over TCP.

    Args:
        host (str): The address of the host to connect to.
        port (int): The port to connect to on host.

    Yield (socket.socket) on success, False otherwise
    """
    sock = socket.socket()
    sock.settimeout(timeout)

    try:
        sock.connect((host, port))
    except OSError:
        # Closed ports will time out, no need to re-raise
        sock = False

    yield sock

    if sock:
        sock.close()

def is_port_up(host, port):
    """Accessory to lookup().

    This adds syntactic sugar for connecting after a name has been resolved.
    """
    connection_success = False
    with open_tcp_connection(host, port) as sock:
        if sock:
            connection_success = True
    return connection_success

def resolve_name(host):
    """Resolve the text name of a host to an address on the Internet.

    Return (tuple):
        success (bool): Whether resolving failed or not.
        result (str): The IP address as a string.
    """
    try:
        result = socket.gethostbyname(host)
    except socket.gaierror:
        result = 'Unable to resolve host ' + host

    return result

def lookup_hosts(hosts, ports):
    """Resolve a list of hosts by name to IP addresses and try connect
    to them on TCP ports.

    Args:
        hosts (list): The hosts to connect to.
        ports (list): The ports on hosts to connect to.
    """
    for host in hosts:
        print(host, '[' + resolve_name(host) + ']', end=': ')

        for port in ports:
            if is_port_up(host, port):
                print('[' + str(port) + ']', end=' ')

        print()

def is_portnum(input_str):
    """Return True if input can be represented as a positive integer.

    Args:
        input_str (str): an input

    Return (bool): True if input_str is positive integer; False otherwise
    """
    try:
        int(input_str)
        if int(input_str) < 0 or int(input_str) > 65535:
            raise ValueError
    except ValueError:
        return False
    else:
        return True

def main(argv):
    """Program entry point"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=("Scan some ports on some hosts"))
    parser.add_argument('host', nargs='+', help='hostname to scan')
    parser.add_argument('-p', '--ports', type=str, default='80,443',
                        help='Comma separated list of ports to scan')
    # parser.add_argument('-v', '--verbose', action='count', default=0,
    #                     help='Enable verbose output')
    args = parser.parse_args(argv)

    ports = [int(port) for port in args.ports.split(',') if is_portnum(port)]

    if not ports:
        print('No ports specified')

    lookup_hosts(args.host, ports)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
