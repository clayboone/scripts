#!/usr/bin/env python3

import argparse
import hashlib
import sys
from pathlib import Path

HASHERS = [
    hashlib.md5,
    hashlib.sha1,
    hashlib.sha256,
]

WIDTH = max(len(hsh.__name__.removeprefix("openssl_")) for hsh in HASHERS)


def main():
    parser = argparse.ArgumentParser(description="Hash some files.")
    parser.add_argument("files",
                        nargs=argparse.ONE_OR_MORE,
                        help=("files to hash"))
    args = parser.parse_args()

    for file in args.files:
        try:
            contents = Path(file).read_bytes()
        except FileNotFoundError as exc:
            print(f"{file}: {exc}", file=sys.stderr)
            continue

        print(f"{file}\n{'=' * len(file)}")

        for hasher in HASHERS:
            hasher_name = hasher.__name__.removeprefix("openssl_")
            padding = " " * (WIDTH - len(hasher_name) + 1)
            digest = hasher(contents).hexdigest()

            print(f"{hasher_name}:{padding}{digest}")

        print()


if __name__ == "__main__":
    main()
