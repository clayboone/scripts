#!/usr/bin/env python3
"""Print a random dinner based on what we can cook and what day it is."""

import random
import calendar
from datetime import (date, timedelta)


class Dinner():
    """Pseudo-random dinner generator."""

    DINNERS = {
        'easy': [
            'Pizza Bagels',
            'Conchigli Bolognaise',
            'Linguini Bolognaise',
            'Cottage Pie',
            'Shepherd\'s Pie',
            'Stir Fry (Rice)',
            'Stir Fry (Noodles)',
            'Jacket Potatos',
            'Frozen Lasagna',
            'Frozen Toad\'n\'Hole',
        ],
        'hard': [
            'English Breakfast',
            'Chicken Roast Dinner',
            'Homemade Pizza',
            'Homemade Lasagna',
            'Homemade Enchiladas',
            'Homemade Toad\'n\'Hole',
            'Aubergine Bake',
        ],
        'tuesdays': [
            'Tacos!',
            'Burritos',
            'Frozen Chimichangas',
            'Frozen Enchiladas',
        ]
    }

    def __init__(self):
        pass

    def __repr__(self):
        return 'Dinner()'

    @classmethod
    def pick_dinner(cls, day_offset):
        """Return a random dinner from one of the lists as a string."""
        choice = None
        seed = date.today() + timedelta(days=day_offset)
        random.seed(seed.strftime('%Y%m%d'))

        # FIXME: This shouldn't print anything
        print(seed.strftime('%Y-%m-%d %A:\t'), end=' ')

        if random.choices(['normal', 'takeout'],
                          weights=[0.9, 0.1])[0] == 'takeout':
            choice = 'Takeout!'
        else:
            weekday = calendar.weekday(seed.year, seed.month, seed.day)
            if weekday == 1:
                choice = random.choice(cls.DINNERS['tuesdays'])
            elif weekday in (5, 6):
                choice = random.choice(cls.DINNERS['hard'])
            else:
                choice = random.choice(cls.DINNERS['easy'])

        print(choice)  # FIXME
        return choice


def main():
    """CLI program entry point."""
    for i in range(-5, 15):
        if i == 0:
            print()
        Dinner().pick_dinner(day_offset=i)
        if i == 0:
            print()


if __name__ == "__main__":
    main()
