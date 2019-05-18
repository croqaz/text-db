from argparse import ArgumentParser

# from load import load_files


def parse_args():
    cmdline = ArgumentParser()
    cmdline.add_argument('files', nargs='+')
    cmdline.add_argument('-k', '--keys', action='append')
    cmdline.add_argument('-i', '--interact', help='interact with the DB', action='store_true')
    cmdline.add_argument('--verbose', help='show detailed logs', action='store_true')
    opts = cmdline.parse_args()

    return opts


if __name__ == '__main__':
    opts = parse_args()
    print('CMD opts:', opts)
    # load_files(opts.files, opts.keys)
