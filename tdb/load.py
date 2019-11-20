import os
import time
from glob import glob
from typing import Callable
from pathlib import Path
from subprocess import check_output

from json import loads
try:
    from orjson import loads  # type: ignore
except Exception:
    pass
try:
    from ujson import loads  # type: ignore
except Exception:
    pass

from IPython import embed

KEY_SEP = '-'

ROOT_FOLDER = str(Path.home())


def load_files(files: str, keys: list, config: dict, interact=False):
    """
    High level discover and load JL files.
    The params are:
    * the key used for de-duplication
    * the validation for one or more fields
    * the filters for one or more fields
    """
    data: dict = {}
    input_files: list = []
    key_func = create_key_func(keys, config)
    for fpath in files:
        fpath = str(Path(fpath).expanduser().resolve())
        for fname in sorted(glob(fpath)):
            input_files.append(fname)
            load_json_file(fname, data, key_func)
    if interact:
        # %colors linux
        embed()


def load_json_file(file_name: str, data: dict, key_func: Callable, verbose=True):
    """
    Loads a single JL file.
    """
    t0 = time.monotonic()
    wc, _ = check_output(f'wc -l {file_name}', shell=True).strip().split()
    fsize = int(wc)
    isize = len(data)
    perc1 = fsize // 100

    rel_name = os.path.relpath(file_name, ROOT_FOLDER)
    if verbose:
        print(f'Loading {fsize:,} lines from "{rel_name}" ...')

    stats = {
        'time': .0,
        'lines': 0,
        'empty_keys': 0,
        'empty_items': 0,
    }
    local_db: dict = {}

    for line in open(file_name):
        line = line.strip()
        if not line:
            continue
        # Increment nr of non-empty lines
        stats['lines'] += 1
        # Show progress
        if not stats['lines'] % perc1:
            print('#', end='', flush=True)
        try:
            item = loads(line)
        except Exception as err:
            if len(line) > 45:
                print(f'ERR loading line "{line[:20]}...{line[-20:]}" from "{rel_name}" : {err}')
            else:
                print(f'ERR loading line "{line}" from "{rel_name}" : {err}')
        # Ignore null items, they don't make sense
        if not item:
            stats['empty_items'] += 1
            continue
        # Will process filters here
        # Will process item here
        key = key_func(item)
        # Ignore null keys, they don't make sense
        if not key:
            stats['empty_keys'] += 1
            continue
        local_db[key] = item

    data.update(local_db)
    t1 = time.monotonic()
    print('\n')

    if verbose:
        stats['time'] = float(f'{t1-t0:.3f}')
        print(f'Statistics: {stats}')
        print(f'Loaded {len(local_db):,} items, added {len(data) - isize:,} new items.\n')


def wc_lines(file_name: str) -> int:
    wc_l = check_output(f'wc -l {file_name}', shell=True).strip().split()[0]
    return int(wc_l)


def create_key_func(keys: list, config: dict):
    if not keys and config.get('keys') and callable(config['keys']):
        gen_key = config['keys']
    elif keys and isinstance(keys, (list, tuple)):
        gen_key = lambda o: KEY_SEP.join(str(o.get(k, '')) for k in keys)
    else:
        gen_key = lambda o: str(o)
    return gen_key
