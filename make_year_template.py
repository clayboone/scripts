"""Make a diary template for a given year."""
import argparse
import textwrap
from datetime import datetime, timedelta
from typing import Any


class Diary:
    TEMPLATE = textwrap.dedent(
        """\
        # Year of {year}

        {weeks}

        <!-- Modeline --> <!-- {{{{{{1 -->
        <!-- markdownlint-disable-file -->
        <!-- vim: sw=2 ts=2 tw=80 expandtab spell nonumber fdm=marker ai sts=2
          -->

        """
    )

    def __init__(self, year) -> None:
        self.year = year

    def iter_weeks(self):
        start = first_monday_of_year = {
            d.weekday(): d
            for d in [datetime(self.year, 1, 1) + timedelta(days=x) for x in range(7)]
        }[0]

        while start.year == first_monday_of_year.year:
            yield "\n".join(
                [
                    f"## Week of {start.strftime('%Y-%m-%d')} <!-- {{{{{{1 -->\n",
                    *[
                        f"### {d.strftime('%Y-%m-%d')} <!-- {{{{{{2 -->\n"
                        for d in ((start + timedelta(days=t)) for t in range(5))
                    ],
                    "\n<!-- 1}}} -->\n",
                ]
            )
            start += timedelta(days=7)

    def __str__(self) -> str:
        return self.TEMPLATE.format(year=self.year, weeks="\n".join(self.iter_weeks()))


def valid_year(val: Any) -> int:
    if not (1970 <= (val := int(val)) < 10_000):
        raise ValueError(f"Invalid year {val}")
    return val


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="""\
            Remember to call `python.exe` from Git Bash (instead of `python`).
            Redirect stdout to the new file.
        """,
    )
    parser.add_argument("year", type=valid_year, help="year to make template for")
    args = parser.parse_args()

    print(Diary(args.year))


if __name__ == "__main__":
    main()
