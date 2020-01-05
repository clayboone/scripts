#!/usr/bin/env python3
"""Print a random dinner based on what we can cook and what day it is."""

import calendar
import datetime as dt
import random
from typing import Optional


class Meal:
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
            "Chilled Bangers and Mash",
            "Frozen Hotpot",
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

    @classmethod
    def mexican(cls) -> str:
        return random.choice(cls.DINNERS["mexican"])

    @classmethod
    def hard(cls) -> str:
        return random.choice(cls.DINNERS["hard"])

    @classmethod
    def easy(cls) -> str:
        return random.choice(cls.DINNERS["easy"])


class Dinner:
    """Pseudo-random dinner generator."""
    DATE_FMT = "%Y-%m-%d"
    CHANCE_FOR_TAKEOUT = 0.2

    def __init__(self, date: dt.datetime):
        today = dt.date.today().strftime(self.DATE_FMT)

        self._choice: Optional[str] = None
        self._date: dt.datetime = date
        self.date: str = self._date.strftime(self.DATE_FMT)
        self.day_name: str = "Today" if self.date == today else date.strftime("%A")

        random.seed(self.date)

    def __str__(self):
        return self.choose_dinner()

    def choose_dinner(self) -> str:
        """Return a random dinner from the apropriate list."""
        if not self._choice:
            weekday = calendar.weekday(self._date.year, self._date.month, self._date.day)

            if self.is_takeout_day():
                self._choice = "Takeout!"
            elif weekday == calendar.TUESDAY:
                self._choice = Meal.mexican()
            elif weekday in (calendar.SATURDAY, calendar.SUNDAY):
                self._choice = Meal.hard()
            else:
                self._choice = Meal.easy()

        return self._choice

    def is_takeout_day(self) -> bool:
        """Return whether this day is a takeout day."""
        assert 0.0 <= self.CHANCE_FOR_TAKEOUT <= 1.0

        weights = [self.CHANCE_FOR_TAKEOUT, 1.0 - self.CHANCE_FOR_TAKEOUT]
        return random.choices([True, False], weights=weights)[0]


def main():
    """Entry point."""
    today = dt.date.today().strftime(Dinner.DATE_FMT)
    dinners = [Dinner(dt.date.today() + dt.timedelta(days=_)) for _ in range(-5, 15)]

    for dinner in dinners:
        fmt = "{0}{1}{0}".format("\n" if dinner.date == today else "", "{} {}:\t{}")
        print(fmt.format(dinner.date, dinner.day_name, dinner))


if __name__ == "__main__":
    main()
