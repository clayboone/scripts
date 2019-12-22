import argparse
import json
import logging
import os
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import textwrap

import gkeepapi

USERNAME = ''  # Full GMail address, not just the username.
PASSWORD = ''  # App-password here (remember to delete it in account).

MYKEEP_DIR = Path('/'.join([
    os.getenv('USERPROFILE' if 'win' in sys.platform else 'HOME'),
    Path(__file__).name.split('.')[0]
]))  # C:\Users\<your_username>\mykeep

MASTER_TOKEN_FILE = MYKEEP_DIR / 'secret_token.txt'
KEEP_STATE_FILE = MYKEEP_DIR / 'state.json'

FALLBACK_EDITOR = 'vim'

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


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


def save_notes(keep: gkeepapi.Keep, dest: str) -> int:
    """Save the all notes to a folder.

    @param keep Keep object containing notes.
    @param dest Destination directory to write files.
    @return Number of files written.
    """
    bytes_written = []
    for index, note in enumerate(keep.all()):
        note_path = Path(dest) / f'{index} {remove_invalid_chars(note.title)}.md'
        content = textwrap.dedent(f"""\
            ---
            title: {note.title}
            labels: {' '.join([label.name for label in note.labels.all()])}
            ---
        """)
        content += note.text

        try:
            bytes_written.append(note_path.write_text(content, encoding='utf8'))
        except OSError as exc:
            log.error('Failed saving "%s": %s', note_path.name, exc)

    log.info('Wrote %s files from %s notes (%.02f KiB).',
             len(bytes_written),
             len(keep.all()),
             sum(bytes_written) / 1024)

    return len(bytes_written) or None


def main():
    parser = argparse.ArgumentParser(
        description='Download your Google Keep notes')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Use multiple times to increase verbosity')
    parser.add_argument('-d', '--directory', type=str,
                        help='Download location for note files')
    parser.epilog = (f'Specifying an output directory with the "-d" option '
                     f'will prevent {sys.argv[0]} from running an editor.')
    args = parser.parse_args()

    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    if args.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)

    if not (keep := login_and_sync()):  # pylint: disable=superfluous-parens
        log.error('Failed to login and sync with Google Keep')
        return 1

    if args.directory:
        save_notes(keep, args.directory)
    else:
        with TemporaryDirectory() as tempdir:
            save_notes(keep, tempdir)

            # TODO: Different editors support using folders differently (eg.
            # VSCode, Vim) or not at all (eg. Nano) and this line is pretty
            # ugly as it uses os.system(). Also, there's no guarantee that
            # anything will actually run in Windows' cmd.exe, so we may need to
            # actually search $PATH to see if we can run an editor.
            os.system(os.getenv('EDITOR', FALLBACK_EDITOR) + f' {tempdir}')

            # TODO: Read notes for changes and re-sync.

    return 0


if __name__ == "__main__":
    main()
