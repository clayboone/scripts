#!/usr/bin/env python3
"""
send_mouse_click.py

Requires:
    https://pypi.python.org/pypi/pynput
"""

import asyncio
import signal
import sys

from pynput.mouse import Button, Controller

EVENT_LOOP = asyncio.get_event_loop()


async def click(button=Button.left, duration=0.1, delay=1.0):
    """Send a mouse click."""
    mouse = Controller()
    mouse.press(button)
    await asyncio.sleep(duration)
    mouse.release(button)
    await asyncio.sleep(delay)


def setup_signal_handlers():
    def sigint_handler(_signal, _frame):
        EVENT_LOOP.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint_handler)


def main():
    setup_signal_handlers()

    while True:
        asyncio.ensure_future(click())

    EVENT_LOOP.run_forever()


if __name__ == '__main__':
    main()
