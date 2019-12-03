from argparse import ArgumentParser

from .load import load_files
from .config import load_local_config


def parse_args():
    cmdline = ArgumentParser()
    cmdline.add_argument('files', nargs='+')
    cmdline.add_argument('-n', '--limit', type=int, help='stop after number of items')
    cmdline.add_argument('-k', '--keys', action='append', default=[])
    cmdline.add_argument('-c', '--config', default={}, help='Python config file with keys, filters')
    cmdline.add_argument('-i', '--interact', help='interact with the DB', action='store_true')
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
    if not opts.keys and not opts.config:
        print('Warning: The KEYS are empty!')
    load_files(opts.files, opts.limit, opts.keys, opts.config, interact=opts.interact)
