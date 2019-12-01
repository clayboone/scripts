import argparse
import logging
from pathlib import Path
import random
import sys
import textwrap

_log = logging.getLogger(__file__)  # pylint: disable=invalid-name


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
    parser.add_argument('-l', '--length', type=int, default=1024,
                        help='Average length of each file')
    parser.add_argument('-f', '--force', action='store_true',
                        help='create files even if output directory is not empty')
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
    _log.debug('length:\t%d', args.length)
    _log.debug('force:\t%s', args.force)
    _log.debug('verbosity:\t%d', args.verbose)

    return args


def main():
    args = _parse_args()

    outdir = Path(args.outdir)
    if outdir.exists():
        if args.force:
            _log.warning('Output directory exists. Continuing anyways.')
        else:
            print(f'Fatal: Output directory exsits: {outdir.absolute()}', file=sys.stderr)
            return

    _log.info('Creating directory "%s"', outdir.absolute())
    outdir.mkdir(exist_ok=True)

    _log.info('Creating %d files', args.number_of_files)
    for file_num in range(args.number_of_files):
        file_path = outdir / f'File #{file_num}.txt'

        if args.type == 'numeric':
            max_int = args.number_of_files * 10
            file_path.write_text('{}\n'.format(random.randint(0, max_int)))
        else:
            pass

    _log.info('Wrote %d files', args.number_of_files)


if __name__ == "__main__":
    main()
