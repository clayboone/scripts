#!/usr/bin/env python3
"""
GMouseClicker

Click the mouse repeatedly until stopped.

Requires:
    https://pypi.python.org/pypi/pynput
    https://github.com/thesharp/daemonize
"""

import sys
import argparse
import time

from daemonize      import Daemonize
from pynput.mouse   import Button, Controller

def print_stderr(msg):
    print('{}'.format(msg), file=sys.stderr)

def send_mouse1_event(mouse_down_delay=0.4):
    mouse = Controller()
    mouse.press(Button.left)
    time.sleep(mouse_down_delay)
    mouse.release(Button.left)

if __name__ == '__main__':
    send_mouse1_event()
