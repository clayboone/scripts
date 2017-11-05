#!/usr/bin/env python3
"""
mouse_clicker.py

Click the mouse repeatedly until stopped. Requires Pynput
https://pypi.python.org/pypi/pynput
"""

from time import sleep

from pynput.mouse import Button, Controller

def send_mouse1_event(mouse_down_delay=0.4):
    mouse = Controller()
    mouse.press(Button.left)
    sleep(mouse_down_delay)
    mouse.release(Button.left)

if __name__ == '__main__':
    send_mouse1_event()
