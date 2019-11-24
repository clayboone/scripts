#!/usr/bin/env python3
"""
send_mouse_click.py

Requires:
    https://pypi.python.org/pypi/pynput
"""

import asyncio
import signal
import sys
import time

from pynput.mouse import Button, Controller

EVENT_LOOP = asyncio.get_event_loop()


def click(button=Button.left, duration=0.1):
    """Send a mouse click."""
    mouse = Controller()
    mouse.press(button)
    time.sleep(duration)
    mouse.release(button)


def setup_signal_handlers():
    def sigint_handler(_signal, _frame):
        EVENT_LOOP.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint_handler)


def main():
    setup_signal_handlers()

    asyncio.ensure_future(click(duration=2))
    asyncio.ensure_future(click(duration=2))
    EVENT_LOOP.run_forever()


if __name__ == '__main__':
    main()
