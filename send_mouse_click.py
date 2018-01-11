#!/usr/bin/env python3
"""
GMouseClicker

Click the mouse repeatedly until stopped.

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
