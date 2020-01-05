#!/usr/bin/env python3
"""Print a random dinner based on what we can cook and what day it is."""

import calendar
import datetime as dt
import random
from typing import Optional


class Dinner:
    """Pseudo-random dinner generator."""

    CHANCE_FOR_TAKEOUT = 0.2

    DINNERS = {
        "easy": [
            "Pizza Bagels",
            "Conchigli Bolognaise",
            "Linguini Bolognaise",
            "Cottage Pie",
            "Shepherd's Pie",
            "Stir Fry (Rice)",
            "Stir Fry (Noodles)",
            "Jacket Potatos",
            "Frozen Lasagna",
            "Frozen Toad'n'Hole",
        ],
        "hard": [
            "English Breakfast",
            "Chicken Roast Dinner",
            "Homemade Pizza",
            "Homemade Lasagna",
            "Homemade Enchiladas",
            "Homemade Toad'n'Hole",
            "Aubergine Bake",
        ],
        "mexican": [
            "Tacos!",
            "Burritos",
            "Frozen Chimichangas",
            "Frozen Enchiladas",
        ]
    }

    def __init__(self, date: dt.datetime):
        today = dt.date.today().strftime("%Y-%m-%d")
        self.date = date.strftime("%Y-%m-%d")
        self.day_name = "Today" if self.date == today else date.strftime("%A")
        self.weekday = calendar.weekday(date.year, date.month, date.day)
        self._choice: Optional[str] = None

        random.seed(self.date)

    def __str__(self):
        return self.choose_dinner()

    def choose_dinner(self) -> str:
        """Return a random dinner from the apropriate list."""
        if not self._choice:
            if self.is_takeout_day():
                self._choice = "Takeout!"
            elif self.weekday == calendar.TUESDAY:
                self._choice = random.choice(self.DINNERS["mexican"])
            elif self.weekday in (calendar.SATURDAY, calendar.SUNDAY):
                self._choice = random.choice(self.DINNERS["hard"])
            else:
                self._choice = random.choice(self.DINNERS["easy"])

        return self._choice

    def is_takeout_day(self) -> bool:
        """Return whether this day is a takeout day."""
        assert 0.0 <= self.CHANCE_FOR_TAKEOUT <= 1.0

        weights = [self.CHANCE_FOR_TAKEOUT, 1.0 - self.CHANCE_FOR_TAKEOUT]
        return random.choices([True, False], weights=weights)[0]

def main():
    """Entry point."""
    today = dt.date.today().strftime("%Y-%m-%d")
    dinners = [Dinner(dt.date.today() + dt.timedelta(days=_)) for _ in range(-5, 15)]

    for dinner in dinners:
        fmt = "{0}{1}{0}".format("\n" if dinner.date == today else "", "{} {}:\t{}")
        print(fmt.format(dinner.date, dinner.day_name, dinner))


if __name__ == "__main__":
    main()
