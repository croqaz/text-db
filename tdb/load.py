import os
import time
from glob import glob
from pathlib import Path
from subprocess import check_output
from typing import Callable, Optional

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
from prop import get as dot_get  # noqa: F401

from export import export_db

KEY_SEP = '-'

ROOT_FOLDER = str(Path.home())


def load_files(files: str, keys: list, config: dict, interact=False):
    """
    High level discover and load JL files.
    The functions in config are:
    * the key used for de-duplication
    * the validation for one or more fields
    * the transform function
    """
    # Exposed for interact:
    data: dict = {}
    input_files: list = []

    def export(out_path: str):
        """ Shortcut function """
        return export_db(data.values(), out_path)

    # Not available in interact:
    key_func = create_key_func(keys, config)
    validate_func = create_validate_func(config)
    transform_func = None

    for fpath in files:
        fpath = str(Path(fpath).expanduser().resolve())
        for fname in sorted(glob(fpath)):
            input_files.append(fname)
            load_json_file(fname, data, key_func, validate_func, transform_func)

    del files
    del key_func
    del validate_func
    del transform_func

    if interact:
        # %colors linux
        embed()


def load_json_file(file_name: str,
                   data: dict,
                   key_func: Callable,
                   validate_func: Optional[Callable] = None,
                   transform_func: Optional[Callable] = None,
                   verbose=True):
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
        'invalid_items': 0,
        'validation_err': 0,
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
        # Validate item
        try:
            if validate_func and not validate_func(item):
                stats['invalid_items'] += 1
                continue
        except Exception as err:
            print(f'Cannot validate item "{item}" from "{rel_name}" : {err}')
            stats['validation_err'] += 1
            continue
        # Process item
        if transform_func:
            item = transform_func(item)
        # Calculate unique key
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


def create_validate_func(config: dict):
    validate = None
    if callable(config.get('validate')):
        validate = config['validate']
    # elif config.get('validate') and isinstance(config['validate'], (list, tuple)):
    #     # Does this even make sense?
    #     validate = lambda o: ???
    return validate


def create_transform_func(config: dict):
    transform = None
    if callable(config.get('transform')):
        transform = config['transform']
    return transform
