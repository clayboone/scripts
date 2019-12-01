import argparse
import logging
from pathlib import Path
import random
import sys
import textwrap

_log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def _parse_args():
    parser = argparse.ArgumentParser(description=textwrap.dedent("""\
        Create some files filled with some random content in a directory.
        """))
    parser.add_argument('-o', '--outdir', type=str, default='.',
                        help='output directory')
    parser.add_argument('-n', '--number-of-files', type=int, default=0,
                        help='Number of files to create')
    parser.add_argument('-t', '--type', type=str, default='numeric',
                        help='Type of each file. Either "numeric" or "random"')
    parser.add_argument('-s', '--size', type=str,
                        help='Size of each file')
    parser.add_argument('-f', '--force', action='store_true',
                        help='create files even if output directory is not empty')
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
    _log.debug('num:\t%d', args.number_of_files)
    _log.debug('type:\t"%s"', args.type)
    _log.debug('size:\t%s', args.size)
    _log.debug('force:\t%s', args.force)
    _log.debug('verbosity:\t%d', args.verbose)

    return args


class File:
    def __init__(self, name: str, type_: str = None, length: int = None, content: str = None):
        self.name = Path(name)
        self.type = type_ or 'numeric'
        self.length = length or 0
        self.content = content or self.generate_content()

    def __repr__(self):
        return f'File("{self.name}", {self.content})'

    def generate_content(self):  # TODO
        return 'FIXME'

    def save(self):  # TODO
        pass


def main():
    args = _parse_args()

    outdir = Path(args.outdir)
    if outdir.exists():
        if args.force:
            _log.warning('Output directory exists. Continuing anyways.')
        else:
            print(f'Output directory exsits: {outdir.absolute()}', file=sys.stderr)
            return

    _log.info('Creating directory "%s"', outdir.absolute())
    outdir.mkdir(exist_ok=True)

    # We generate and write in separate steps to measure performance
    # independantly.
    files = []
    _log.info('Generating %d files', args.number_of_files)
    for file_num in range(args.number_of_files):
        files.append(File(outdir / f'File #{file_num}.txt'))
        if file_num == 0:
            _log.debug('First file:\n%s', repr(files[0]))

    _log.info('%s %d files', 'Skipping' if args.dry_run else 'Writing', len(files))
    for file in files:
        file.save()


if __name__ == "__main__":
    main()
