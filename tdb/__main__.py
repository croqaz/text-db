from argparse import ArgumentParser
from pathlib import Path
from functools import partial

from .load import load_files
from .export import export_db
from .config import load_local_config


def parse_args():
    cmdline = ArgumentParser()
    cmdline.add_argument('files', nargs='+')
    cmdline.add_argument('-n', '--limit', type=int, help='stop after number of items')
    cmdline.add_argument('--limit-lines', type=int, help='stop after number of lines')
    cmdline.add_argument('-k', '--keys', action='append', default=[])
    cmdline.add_argument('-c', '--config', default={}, help='Python config file with keys, filters')
    cmdline.add_argument('-e', '--export', type=Path, help='interact with the DB')
    cmdline.add_argument('-i', '--interact', help='interact with the DB', action='store_true')
    cmdline.add_argument('--noconfig', action='store_true', help='Force ignoring all configs')
    cmdline.add_argument('--verbose', help='show detailed logs', action='store_true')
    opts = cmdline.parse_args()
    print('CMD opts:', opts)

    if opts.config:
        try:
            opts.config = load_local_config(opts.config)
            print(f'Loaded local config {opts.config}\n')
        except Exception as err:
            print(f'Cannot load "{opts.config}": {err}\n')

    if opts.limit and opts.limit < 0:
        raise ValueError('The limit cannot be negative')

    return opts


if __name__ == '__main__':
    opts = parse_args()
    if not opts.noconfig and not opts.keys and not opts.config:
        print('Warning: The KEYS are empty!')

    partial_call = partial(
        load_files,
        opts.files,
        opts.keys,
        limit=opts.limit,
        limit_lines=opts.limit_lines,
        verbose=opts.verbose,
    )

    if opts.export:
        db = partial_call(config=opts.config)
        export_db(db.values(), opts.export)
    elif opts.noconfig:
        partial_call(interact=opts.interact)
    else:
        partial_call(config=opts.config, interact=opts.interact)
