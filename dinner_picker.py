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

    def __init__(self, datetime_seed=None):
        self.seed = datetime_seed
        random.seed(self.seed.strftime('%Y%m%d'))

    def __repr__(self):
        return 'Dinner({})'.format(
            self.seed
        )

    def __str__(self):
        """Return a random dinner from one of the lists as a string."""
        choice = None

        if random.choices(['normal', 'takeout'],
                          weights=[0.9, 0.1])[0] == 'takeout':
            choice = 'Takeout!'
        else:
            weekday = calendar.weekday(
                self.seed.year, self.seed.month, self.seed.day)

            if weekday == 1:
                choice = random.choice(self.DINNERS['tuesdays'])
            elif weekday in (5, 6):
                choice = random.choice(self.DINNERS['hard'])
            else:
                choice = random.choice(self.DINNERS['easy'])

        return choice


def main():
    """CLI program entry point."""
    for i in range(-5, 15):
        seed = date.today() + timedelta(days=i)
        day = 'Today' if i == 0 else seed.strftime('%A')
        dinner = Dinner(seed)

        fmt = '{} {}:\t{}'
        if i == 0:
            fmt = '\n' + fmt + '\n'

        print(fmt.format(seed.strftime('%Y-%m-%d'), day, dinner))


if __name__ == "__main__":
    main()
