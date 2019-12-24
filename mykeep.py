import argparse
import json
import logging
import os
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
from typing import Optional, Union
import textwrap

import gkeepapi

USERNAME = ''  # Full GMail address, not just the username.
PASSWORD = ''  # App-password here (remember to delete it in account).

FALLBACK_EDITOR = 'vim'

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Config:
    """Configuration settings object for mykeep.py"""
    STATE_FILENAME = 'state.json'
    TOKEN_FILENAME = 'token'

    def __init__(self, use_state: bool = True):
        self.use_state = use_state
        self._path = None
        self._state_path = self.path / self.STATE_FILENAME
        self._token_path = self.path / self.TOKEN_FILENAME

    @staticmethod
    def _resolve_environment(unresolved_path: str) -> str:
        resolved_path = None
        if match := re.search(r'\$\w+', unresolved_path):
            escaped_val = os.getenv(match[0][1:], '').replace('\\', '\\\\')
            resolved_path = re.sub(r'\$\w+', escaped_val, unresolved_path)

        # FIXME: This is an interesting statement...
        return resolved_path or unresolved_path

    @property
    def path(self):
        """Path object of the configuration directory."""
        if self._path:
            return self._path

        if 'win' in sys.platform:
            possible_paths = ['$USERPROFILE/.mykeep', '$LOCALAPPDATA/mykeep']
        else:
            possible_paths = ['$HOME/.mykeep', '$XDG_CONFIG_HOME/mykeep', '$HOME/.config/mykeep']

        for possible_path in possible_paths:
            possible_path = Path(self._resolve_environment(possible_path))
            if possible_path.is_dir():
                self._path = possible_path

        if not self._path:
            self._path = Path(self._resolve_environment(possible_paths[-1]))
            self._path.mkdir()

        log.info('Using config path "%s"', str(self._path))
        return self._path

    @property
    def state(self) -> Optional[dict]:
        if not self.use_state:
            log.info('Skipping loading state.')
            return None

        try:
            return json.loads(self._state_path.read_text(encoding='utf8'))
        except FileNotFoundError:
            log.info('No state file found.')
            return None

    @state.setter
    def state(self, value: dict) -> int:
        if not self.use_state:
            log.info('Skipping saving state.')
            return 0

        log.info('Saving state to "%s"', str(self._state_path))
        try:
            return self._state_path.write_text(json.dumps(value), encoding='utf8')
        except OSError as exc:
            log.error('Failed saving state file: %s', exc)
            return 0

    @property
    def token(self) -> Optional[str]:
        try:
            return self._token_path.read_text().strip()
        except FileNotFoundError:
            log.info('No token file found.')
            return None

    @token.setter
    def token(self, value: str) -> int:
        log.info('Saving token to "%s"', str(self._token_path))
        try:
            return self._token_path.write_text(value)
        except OSError as exc:
            log.error('Failed saving token file: %s', exc)
            return 0


def login_and_sync(config: Config) -> gkeepapi.Keep:
    """Login and sync to the Google Keep servers."""
    keep = gkeepapi.Keep()

    # TODO: Swap around order here to prefer login/password. Warn when both
    # types of credential are available.
    try:
        log.info('Reading credentials from master token file')
        keep.resume(USERNAME, config.token, state=config.state)
    except gkeepapi.exception.LoginException:
        try:
            log.info('Falling back to username/password in %s', __file__)
            keep.login(USERNAME, PASSWORD, state=config.state)
        except gkeepapi.exception.LoginException:
            return None

        config.token = keep.getMasterToken()

    log.info('Synchronizing with Google servers')
    try:
        keep.sync()
    except gkeepapi.exception.SyncException as exc:
        # Warning because this should use the restored state anyways.
        log.warning('Failed to sync with Google servers: "%s".', exc)

    config.state = keep.dump()

    return keep


def remove_invalid_chars(string: str) -> str:
    """Convert a string to a valid filename for the platform."""
    if 'win' not in sys.platform:
        log.warning('Method not yet tested on other platforms')

    bad_chars = r'\?\\\/\:\*\"\<\>\|\r'
    return re.sub(f'[{bad_chars}]+', ' ', string).strip()


def save_notes(keep: gkeepapi.Keep, dest: Union[Path, str]) -> int:
    """Save all notes to a directory.

    @param keep Keep object containing notes.
    @param dest Directory wherein to write files.
    @return Number of files written.
    """
    bytes_written = []
    for index, note in enumerate(keep.all()):
        log.debug('Saving note "%s"', note.title)
        note_path = Path(dest) / f'{index} {remove_invalid_chars(note.title)}.md'

        log.debug('Using filename "%s"', str(note_path))
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

    stats = len(bytes_written), len(keep.all()), sum(bytes_written) / 1024
    log.info('Wrote %s files from %s notes (%.02f KiB).', *stats)

    return len(bytes_written)


def main():
    parser = argparse.ArgumentParser(
        description='Download your Google Keep notes')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='use multiple times to increase verbosity')
    parser.add_argument('--no-state', action='store_true', default=False,
                        help=f'prevent {sys.argv[0]} from storing and using state.')
    parser.add_argument('-d', '--directory', type=str,
                        help='download location for note files')
    parser.epilog = (f'Specifying an output directory with the "-d" option '
                     f'will prevent {sys.argv[0]} from running an editor.')
    args = parser.parse_args()

    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    if args.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)

    config = Config(use_state=not args.no_state)
    keep = login_and_sync(config)

    if not keep:
        log.error('Failed to authenticate with Google')
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
            #
            # run_editor(tempdir)
            #   -> vscode: code --new-window --folder-uri $tempdir
            #   ->    vim: vim $tempdir
            #   -> editors that don't support folders -> bash?

            os.system(os.getenv('EDITOR', FALLBACK_EDITOR) + f' {tempdir}')

            # TODO: Read notes for changes and re-sync.

    return 0


if __name__ == "__main__":
    main()
