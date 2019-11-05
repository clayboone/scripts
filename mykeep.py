import os
from pathlib import Path
import re
import sys

import gkeepapi

USERNAME = ''  # Full GMail address, not just the username.
PASSWORD = ''  # App-password here (remember to delete it in account).

MYKEEP_DIR = Path('/'.join([
    os.getenv('USERPROFILE' if 'win' in sys.platform else 'HOME'),
    Path(__file__).name.split('.')[0],
]))
MASTER_TOKEN_FILE = MYKEEP_DIR / 'secret_token.txt'
SAVE_LOCATION_DIR = MYKEEP_DIR / 'notes'


def login_and_sync() -> gkeepapi.Keep:
    """Login and sync to the Google Keep servers."""
    # TODO: We can use caching to improve performance.
    keep = gkeepapi.Keep()

    if MASTER_TOKEN_FILE.exists():
        keep.resume(USERNAME, MASTER_TOKEN_FILE.read_text().strip())
    else:
        try:
            keep.login(USERNAME, PASSWORD)
        except gkeepapi.exception.LoginException:
            print('Unable to auth! Figure it out.', file=sys.stderr)
            sys.exit(1)

        try:
            MASTER_TOKEN_FILE.write_text(keep.getMasterToken())
        except OSError:
            pass  # TODO: This is at least a warning...

    keep.sync()
    return keep


def main():
    keep = login_and_sync()
    num_written = 0

    if not SAVE_LOCATION_DIR.exists():
        SAVE_LOCATION_DIR.mkdir()

    for index, note in enumerate(keep.all()):
        bad_chars = '\ \?\\\/\:\*\"\<\>\|\r'
        valid_title = re.sub(f'[{bad_chars}]+', '_', note.title)
        filename = f'{index}_{valid_title}.txt'

        note_file = SAVE_LOCATION_DIR / filename
        try:
            # TODO: Write tags as front-matter and blobs as fire emoji.
            note_file.write_text(note.text, encoding='utf8')
            num_written += 1
        except OSError as exc:
            print(f'Failed saving "{str(note_file.name)}": {exc}',
                  file=sys.stderr)

    print(f'Wrote {num_written} files out of {index + 1} notes.')


if __name__ == "__main__":
    main()
