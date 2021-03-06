import os
import time
from glob import glob
from pathlib import Path
from subprocess import check_output
from typing import Callable, Optional, Dict, Any

from json import loads
try:
    from orjson import loads  # type: ignore
except ImportError:
    pass
try:
    from ujson import loads  # type: ignore
except ImportError:
    pass

from IPython import embed
from prop import get as dot_get  # noqa: F401

from .export import export_db

KEY_SEP = '-'

ROOT_FOLDER = str(Path.home())


def load_files(  # noqa: C901
        files: str,
        keys: list = [],
        config: dict = {},
        limit: int = 0,
        limit_lines: int = 0,
        verbose=False,
        interact=False) -> Dict[Any, Any]:
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
    transform_func = create_transform_func(config)

    if verbose:
        t0 = time.monotonic()

    for fpath in files:
        fpath = str(Path(fpath).expanduser().resolve())
        for fname in sorted(glob(fpath)):
            input_files.append(fname)
            load_json_file(fname,
                           data,
                           key_func,
                           validate_func,
                           transform_func,
                           limit=limit,
                           limit_lines=limit_lines,
                           verbose=verbose)

    if verbose:
        t1 = time.monotonic()
        print(f'Loaded {len(data):,} items in {t1-t0:.3f} sec.\n')
        del t0, t1

    del files
    del key_func
    del validate_func
    del transform_func

    if interact:
        # %colors linux
        embed()

    return data


def load_json_file(  # noqa: C901
        file_name: str,
        db_data: Optional[dict] = None,
        key_func: Optional[Callable] = None,
        validate_func: Optional[Callable] = None,
        transform_func: Optional[Callable] = None,
        merge_func: Optional[Callable] = None,
        limit: int = 0,
        limit_lines: int = 0,
        verbose=False):
    """
    Loads a single JL file and inject the result into DB DATA.
    """
    if db_data is None:
        db_data = {}

    if key_func is None:
        key_func = repr

    if merge_func is None:
        # The default merging strategy totally ignores the old item
        merge_func = lambda old_item, new_item: new_item

    t0 = time.monotonic()
    isize = len(db_data)

    nr_lines = wc_lines(file_name)
    if limit_lines and limit_lines < nr_lines:
        nr_lines = limit_lines

    rel_name = os.path.relpath(file_name, ROOT_FOLDER)

    if verbose:
        print(f'Loading {nr_lines:,} lines from "{rel_name}" ...')
        current_perc = 0.0
        if nr_lines >= 100:
            perc1 = nr_lines / 100.0
            progress_chr = '#'
        else:
            perc1 = 1
            progress_chr = (100 // nr_lines) * '#'

    stats = {
        'time': .0,
        'lines': 0,
        'empty_keys': 0,
        'empty_items': 0,
        'duplicate_keys': 0,
        'invalid_items': 0,
        'key_func_err': 0,
        'merging_err': 0,
        'validation_err': 0,
    }
    local_db: dict = {}

    for line in open(file_name):
        line = line.strip()
        if not line:
            continue

        if limit_lines and stats['lines'] >= limit_lines:
            break
        # Increment nr of non-empty lines
        stats['lines'] += 1

        # Show progress
        if verbose and stats['lines'] >= current_perc:
            current_perc += perc1
            print(progress_chr, end='', flush=True)
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
        except Exception:
            stats['validation_err'] += 1
            continue

        # Calculate unique key
        try:
            key = key_func(item)
        except Exception:
            stats['key_func_err'] += 1
            continue

        # Ignore null keys, they don't make sense
        if not key:
            stats['empty_keys'] += 1
            continue

        # Process item
        if transform_func:
            item = transform_func(item)

        if key in local_db:
            stats['duplicate_keys'] += 1

            try:
                local_db[key] = merge_func(local_db[key], item)
            except Exception:
                stats['merging_err'] += 1
                continue
        else:
            local_db[key] = item

        if limit and len(local_db) >= limit:
            break

    db_data.update(local_db)
    t1 = time.monotonic()

    if verbose:
        stats['time'] = float(f'{t1-t0:.3f}')
        print(f'\nStatistics: {stats}')
        print(f'Loaded {len(local_db):,} items, added {len(db_data) - isize:,} new items.\n')

    return local_db


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
