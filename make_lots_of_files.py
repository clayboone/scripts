import argparse
import logging
from pathlib import Path
import random
import textwrap

_log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def positive_int(value: str):
    try:
        value = int(value)

        if value < 0:
            raise ValueError()
    except ValueError as exc:
        _log.error(exc_info=exc)

    return value

def valid_type(value: str):
    valid_types = ['numeric', 'ascii']

    if value not in valid_types:
        raise ValueError(f'Invalid type "{value}"')

    return value


def _parse_args():
    parser = argparse.ArgumentParser(description=textwrap.dedent("""\
        Create some files filled with some random content in a directory.
        """))
    parser.add_argument('outdir', type=str, default='.',
                        help='Output directory')
    parser.add_argument('numfiles', type=positive_int, default=0,
                        help='Number of files to create')
    parser.add_argument('-t', '--type', type=valid_type, default='numeric',
                        help='Type of each file. Either "numeric" or "ascii"')
    parser.add_argument('-s', '--size', type=positive_int, default=0,
                        help='Size of each file')
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='Do everything except write files')
    parser.add_argument('-v', '--verbose', default=0, action='count',
                        help='Be noisy')

    args = parser.parse_args()

    # If --verbose was passed, we might need to enable it for the next lines.
    # Order is significant; we can only set log level once.
    if args.verbose > 1:
        logging.basicConfig(level=logging.DEBUG)
    if args.verbose > 0:
        logging.basicConfig(level=logging.INFO)

    _log.debug('outdir:\t"%s"', args.outdir)
    _log.debug('num:\t%d', args.numfiles)
    _log.debug('type:\t"%s"', args.type)
    _log.debug('size:\t%s', args.size)
    _log.debug('dry:\t%s', args.dry_run)
    _log.debug('verbose:\t%d', args.verbose)

    return args


class File:
    def __init__(self, name: str, type_: str = 'numeric', length: int = 0, content: str = None):
        self.name = Path(name)
        self.length = length
        self.type = type_

        if content:
            self.content = content
        else:
            self.generate_content()

    def __repr__(self):
        return f'File("{self.name}", "{self.content}")'

    def generate_content(self):
        content = ''
        alphabet = None

        if self.type == 'numeric':
            alphabet = [str(i) for i in range(0, 10)]

        if self.type == 'ascii':
            alphabet = [chr(i) for i in range(32, 127)] + ['\n']

        for _ in range(0, self.length):
            content += random.choice(alphabet)

        self.content = content

    def save(self, dry_run: bool = False):
        if dry_run:
            _log.debug('Skipping (dry run): "%s"', str(self.name.resolve()))
        else:
            _log.debug('Writing: "%s"', str(self.name.resolve()))
            self.name.write_text(self.content, encoding='utf8')

    async def asave(self):  # TODO
        pass


def is_empty(name: str):
    # The very first file indicates non-empty.
    for _ in Path(name).iterdir():
        break
    else:
        return True

    return False


def main():
    args = _parse_args()

    outdir = Path(args.outdir)
    if outdir.exists():
        if not is_empty(outdir):
            _log.error('Output directory is not empty: "%s"', str(outdir.resolve()))
            return
    else:
        if args.dry_run:
            _log.info('Would create "%s"', outdir.resolve())
        else:
            _log.info('Creating "%s"', outdir.resolve())
            outdir.mkdir()

    if args.numfiles < 1:
        _log.error('No files to write.')
        return

    # We generate content and write files in separate steps to measure
    # performance independantly.
    files = []
    _log.info('Generating %d files', args.numfiles)
    for file_num in range(args.numfiles):
        files.append(File(outdir / f'File #{file_num}.txt', length=args.size, type_=args.type))

    _log.info('%s %d files', 'Skipping' if args.dry_run else 'Writing', len(files))
    for file in files:
        file.save(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
