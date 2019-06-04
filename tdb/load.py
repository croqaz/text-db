import os
import time
import ujson as json
from glob import glob
from pathlib import Path
from subprocess import check_output

import ipdb

CWD = os.getcwd()
KEY_SEP = '-'


def load_files(files: str, keys: list, config: dict, interact=False):
    """
    High level discover and load JL files.
    The params are:
    * the key used for de-duplication
    * the validation for one or more fields
    * the filters for one or more fields
    """
    data = {}
    input_files = []
    for fpath in files:
        fpath = str(Path(fpath).expanduser().resolve())
        for fname in sorted(glob(fpath)):
            input_files.append(fname)
            load_db_file(fname, data, keys, config)
    if interact:
        ipdb.set_trace()


def load_db_file(file_name: str, data: dict, keys: list, config: dict):
    """
    Loads a single JL file.
    """
    t0 = time.monotonic()
    wc, _ = check_output(f'wc -l {file_name}', shell=True).strip().split()
    fsize = int(wc)
    isize = len(data)
    perc1 = fsize // 100

    if not keys and config.get('keys') and callable(config['keys']):
        gen_key = config['keys']
    elif keys and isinstance(keys, (list, tuple)):
        gen_key = lambda o: KEY_SEP.join(str(o.get(k, '')) for k in keys)
    else:
        gen_key = lambda o: str(o)

    rel_name = os.path.relpath(file_name, CWD)
    print(f'Loading {fsize:,} lines from "{rel_name}" ...')

    index = 0
    empty_keys = 0
    local_db = {}

    for line in open(file_name):
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except Exception as err:
            print(f'ERR loading line "{line[:35]}" from "{rel_name}" : {err}')
        index += 1
        if not index % perc1:
            print('#', end='', flush=True)
        key = gen_key(item)
        # Empty keys don't make any sense, drop them
        if not key:
            empty_keys += 1
            continue
        local_db[key] = item

    data.update(local_db)
    t1 = time.monotonic()

    empty_keys_str = f' ignored {empty_keys} empty keys,' if empty_keys else ''

    print(f'\nLoaded {len(local_db):,} items{empty_keys_str}, '
          f'added {len(data) - isize:,} new items in {t1-t0:.2f}s\n')
