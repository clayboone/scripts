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

log = logging.getLogger(__name__)


def login_and_sync(use_state=True) -> gkeepapi.Keep:
    """Login and sync to the Google Keep servers."""
    keep = gkeepapi.Keep()
    state = None

    if use_state and KEEP_STATE_FILE.exists():
        log.info('Restoring saved state')
        state = json.loads(KEEP_STATE_FILE.read_text(encoding='utf8'))

    try:
        log.info('Reading credentials from master token file')
        keep.resume(USERNAME, MASTER_TOKEN_FILE.read_text().strip(), state=state)
    except OSError:
        try:
            log.info('Falling back to username/password in %s', __file__)
            keep.login(USERNAME, PASSWORD, state=state)
        except gkeepapi.exception.LoginException:
            log.error('Failed to authenticate with Google')
            return None

        try:
            MASTER_TOKEN_FILE.write_text(keep.getMasterToken())
        except OSError:
            log.info('Failed to save token to %s', MASTER_TOKEN_FILE)

    log.info('Synchronizing with Google servers')
    try:
        keep.sync()
    except gkeepapi.exception.SyncException as exc:
        # Warning because this should use the restored state anyways.
        log.warning('Failed to sync with Google servers: "%s".', exc)

    if use_state:
        log.info('Saving state for next sync')
        try:
            KEEP_STATE_FILE.write_text(json.dumps(keep.dump()), encoding='utf8')
        except OSError:
            log.info('Failed to save state file %s', str(KEEP_STATE_FILE))

    return keep


def remove_invalid_chars(string: str) -> str:
    """Convert a string to a valid filename for the platform."""
    if 'win' not in sys.platform:
        log.warning('Method not yet tested on other platforms')

    bad_chars = r'\?\\\/\:\*\"\<\>\|\r'
    return re.sub(f'[{bad_chars}]+', ' ', string).strip()


def main():
    parser = argparse.ArgumentParser(
        description='Download your Google Keep notes')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    args = parser.parse_args()

    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    if args.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)

    # Pylint and Python disagree about the walrus operator.
    if not (keep := login_and_sync()):  # pylint: disable=superfluous-parens
        log.info('Failed to login and sync with Google Keep')
        return 1

    SAVE_LOCATION_DIR.mkdir(exist_ok=True)

    bytes_written = []
    for index, note in enumerate(keep.all()):
        note_path = SAVE_LOCATION_DIR / f'{index} {remove_invalid_chars(note.name)}.md'
        content = textwrap.dedent(f"""\
            ---
            title: {note.title}
            labels: {' '.join([label.name for label in note.labels.all()])}
            ---
            {note.text}
        """)

        try:
            bytes_written.append(note_path.write_text(content, encoding='utf8'))
        except OSError as exc:
            log.error('Failed saving "%s": %s', note_path.name, exc)

    if total_notes := len(keep.all()):
        print('Wrote {} files out of {} notes ({:.02f}KiB).'.format(
            len(bytes_written),
            total_notes,
            sum(bytes_written) / 1024
        ))
    else:
        print(f'This account has no Keep notes to download!')

    return 0


if __name__ == "__main__":
    main()
