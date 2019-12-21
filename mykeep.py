import argparse
import json
import logging
import os
from pathlib import Path
import re
import sys

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

# Non-exported const specific to this file. The name is fine.
_log = logging.getLogger(__file__)  # pylint: disable=invalid-name


def login_and_sync(use_state=True) -> gkeepapi.Keep:
    """Login and sync to the Google Keep servers."""
    keep = gkeepapi.Keep()
    state = None

    if use_state and KEEP_STATE_FILE.exists():
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
    try:
        keep.sync()
    except gkeepapi.exception.SyncException as exc:
        # Warning because this should use the restored state anyways.
        _log.warning('Failed to sync with Google servers: "%s".', exc)

    _log.info('Saving state for next sync')
    try:
        if use_state:
            KEEP_STATE_FILE.write_text(json.dumps(keep.dump()), encoding='utf8')
    except OSError:
        _log.info('Failed to save state file %s', str(KEEP_STATE_FILE))

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

    # Pylint and Python are out of sync on the walrus operator.
    if not (keep := login_and_sync()):  # pylint: disable=superfluous-parens
        _log.info('Failed to login and sync with Google Keep')
        return 1

    SAVE_LOCATION_DIR.mkdir(exist_ok=True)

    bytes_written = []
    for index, note in enumerate(keep.all()):
        bad_chars = r'\?\\\/\:\*\"\<\>\|\r'
        valid_title = re.sub(f'[{bad_chars}]+', ' ', note.title)
        note_path = SAVE_LOCATION_DIR / f'{index} {valid_title}.md'

        content = f'---\ntitle: {note.title}\n'
        if labels := [label.name for label in note.labels.all()]:
            content += 'labels: {}\n'.format(' '.join(label.lower()
                                                      for label in labels))
        content += f'---\n{note.text}'

        try:
            bytes_written.append(note_path.write_text(content, encoding='utf8'))
        except OSError as exc:
            _log.error('Failed saving "%s": %s', note_path.name, exc)

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
