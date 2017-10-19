#!/usr/bin/env python3
"""This module finds the outside IP address of the current host"""

import requests

def get_public_ipv4():
    """
    Return the outside-global IPv4 address of this host as a string using
    the HTTPS flavor of httpbin.org. On error, return '0.0.0.0'
    """
    result = '0.0.0.0'
    request = requests.get('https://httpbin.org/ip')
    if request.status_code == 200:
        for key, val in request.json().items():
            if key == 'origin':
                result = val
    return result

if __name__ == '__main__':
    print('{}'.format(get_public_ipv4()))
