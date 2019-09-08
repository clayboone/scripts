#!/usr/bin/env python3
"""Print or set the screen brightness."""

import re
import sys
from pathlib import Path


class Backlight():
    """Representation of the screen brightness on Intel devices."""
    SYS_BACKLIGHT = Path('/sys/class/backlight/intel_backlight')
    BRIGHTNESS = SYS_BACKLIGHT / 'brightness'
    MAX_BRIGHTNESS = SYS_BACKLIGHT / 'max_brightness'

    @classmethod
    def get_brightness(cls) -> float:
        """Return the current brightness percentage."""
        return (float(cls.BRIGHTNESS.read_text()) /
                float(cls.MAX_BRIGHTNESS.read_text()))

    @classmethod
    def set_brightness(cls, percentage: float):
        """Set the brightness given a percentage."""
        max_raw = int(cls.MAX_BRIGHTNESS.read_text())
        min_raw = int(max_raw * 0.01)

        val_raw = int(percentage * max_raw)
        val_raw = max_raw if val_raw > max_raw else val_raw
        val_raw = min_raw if val_raw < min_raw else val_raw

        cls.BRIGHTNESS.write_text(f'{val_raw}\n')


def main():  # pylint: disable=inconsistent-return-statements
    """Program entry point."""
    if len(sys.argv) < 2:
        return print(f'{Backlight.get_brightness() * 100:.0f}%')

    value = sys.argv[1].rstrip('%')
    if re.search(r'^[+-]?\d*$', value):
        Backlight.set_brightness(
            float(value) / 100 +
            Backlight.get_brightness() if value.startswith(('+', '-')) else 0)
    else:
        print(f'Usage: {sys.argv[0]} [+-]<NUM>[%]')
        print('Without arguments, print the current brightness.')


if __name__ == '__main__':
    main()
