#!/usr/bin/env python3
"""
send_mouse_click.py

Requires:
    https://pypi.python.org/pypi/pynput
"""

import sys
import time
from pynput.mouse   import Button, Controller

def send_mouse1_event(mouse_down_delay=0.05):
    """Send a left-click"""
    mouse = Controller()
    mouse.press(Button.left)
    time.sleep(mouse_down_delay)
    mouse.release(Button.left)

def main(argv):
    send_mouse1_event()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
