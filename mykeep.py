import argparse
import json
import logging
import os
from pathlib import Path
import re
import sys
import textwrap

import gkeepapi

USERNAME = ''  # Full GMail address, not just the username.
PASSWORD = ''  # App-password here (remember to delete it in account).

MYKEEP_DIR = Path('/'.join([
    os.getenv('USERPROFILE' if 'win' in sys.platform else 'HOME'),
    Path(__file__).name.split('.')[0]
]))  # C:\Users\<your_username>\mykeep

MASTER_TOKEN_FILE = MYKEEP_DIR / 'secret_token.txt'
SAVE_LOCATION_DIR = MYKEEP_DIR / 'notes'
KEEP_STATE_FILE = MYKEEP_DIR / 'state.json'

_log = logging.getLogger(__file__)


def login_and_sync() -> gkeepapi.Keep:
    """Login and sync to the Google Keep servers."""
    keep = gkeepapi.Keep()
    state = None

    if KEEP_STATE_FILE.exists():
        _log.info('Restoring saved state')
        state = json.loads(KEEP_STATE_FILE.read_text(encoding='utf8'))

    try:
        _log.info('Reading credentials from master token file')
        keep.resume(USERNAME, MASTER_TOKEN_FILE.read_text().strip(), state=state)
    except OSError:
        try:
            _log.info('Falling back to username/password in %s', __file__)
            keep.login(USERNAME, PASSWORD, state=state)
        except gkeepapi.exception.LoginException:
            _log.error('Failed to authenticate with Google')
            return None

        try:
            MASTER_TOKEN_FILE.write_text(keep.getMasterToken())
        except OSError:
            _log.info('Failed to save token to %s', MASTER_TOKEN_FILE)

    _log.info('Synchronizing with Google servers')
    keep.sync()

    _log.info('Saving state for next time')
    KEEP_STATE_FILE.write_text(json.dumps(keep.dump()), encoding='utf8')

    return keep


def main():
    parser = argparse.ArgumentParser(
        description='Download your Google Keep notes')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    args = parser.parse_args()

    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    if args.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)

    if not (keep := login_and_sync()):
        _log.info('Failed to login and sync with Google Keep')
        return 1

    SAVE_LOCATION_DIR.mkdir(exist_ok=True)

    num_written = 0
    for index, note in enumerate(keep.all()):
        bad_chars = '\?\\\/\:\*\"\<\>\|\r'
        valid_title = re.sub(f'[{bad_chars}]+', ' ', note.title)
        note_path = SAVE_LOCATION_DIR / f'{index} {valid_title}.md'

        # labels = keep.getLabel()
        labels = [label.name for label in note.labels.all()]

        front_matter = textwrap.dedent(f"""\
            ---
            title: {note.title}
            labels: {' '.join(labels)}
            ---
        """)
        content = front_matter + note.text

        try:
            note_path.write_text(content, encoding='utf8')
            num_written += 1
        except OSError as exc:
            print(f'Failed saving "{str(note_path.name)}": {exc}',
                  file=sys.stderr)

    print(f'Wrote {num_written} files out of {index + 1} notes.')


if __name__ == "__main__":
    main()
