#!/usr/bin/env python3
"""
send_mouse_click.py

Requires:
    https://pypi.python.org/pypi/pynput
"""

import time
from pynput.mouse   import Button, Controller

def send_mouse1_event(mouse_down_delay=0.05):
    """Send a left-click"""
    mouse = Controller()
    mouse.press(Button.left)
    time.sleep(mouse_down_delay)
    mouse.release(Button.left)

if __name__ == '__main__':
    send_mouse1_event()
