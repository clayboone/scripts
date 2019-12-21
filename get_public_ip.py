#!/usr/bin/env python3
"""Print the public IP address of this host to stdout."""

import json

import requests


def get_public_ip():
    HTTP_BIN_URI = 'https://httpbin.org/ip'
    ERROR_STRING = '?.?.?.?'

    try:
        with requests.get(HTTP_BIN_URI) as response:
            origin = json.loads(response.content.decode('utf8'))['origin']
    except (requests.ConnectionError, requests.ConnectTimeout) as exc:
        return ERROR_STRING

    origins = [r.strip() for r in origin.split(',')]

    # Httpbin returns two identical values in all of my tests. When they change,
    # it's time to find out why.
    if any(origins[0] != origin for origin in origins[1:]):
        raise ValueError('Values are not the same.')

    return origins[0]


def main():
    print(get_public_ip())


if __name__ == '__main__':
    main()
