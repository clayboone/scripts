#!/usr/bin/env python3
"""Print the public IP address of this host to stdout."""

import json

import requests


def main():
    HTTP_BIN_URI = 'https://httpbin.org/ip'

    # FIXME: Legend tells of a time without internet...
    with requests.get(HTTP_BIN_URI) as response:
        origin = json.loads(response.content.decode('utf8'))['origin']

    origins = [r.strip() for r in origin.split(',')]

    # Httpbin returns two identical values in all of my tests. When they change,
    # it's time to find out why.
    if any(origins[0] != i for i in origins[1:]):
        raise ValueError('Values are not the same.')

    print(origins[0])


if __name__ == '__main__':
    main()
