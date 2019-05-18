import os
import time
import ujson as json
from glob import glob
from pathlib import Path
from subprocess import check_output

CWD = os.getcwd()
KEY_SEP = '-'


def load_files(files: str, keys: list):
    data = {}
    for fpath in files:
        fpath = str(Path(fpath).expanduser().resolve())
        for fname in sorted(glob(fpath)):
            load_db_file(fname, data, keys)
    import ipdb
    ipdb.set_trace()


def load_db_file(file_name: str, data: dict, keys: list):
    """
    Loads a JL file.
    """
    t0 = time.monotonic()
    wc, _ = check_output(f'wc -l {file_name}', shell=True).strip().split()
    fsize = int(wc)
    isize = len(data)
    perc1 = fsize // 100

    rel_name = os.path.relpath(file_name, CWD)
    print(f'Loading {fsize:,} lines from "{rel_name}" ...')

    index = 0
    local_db = {}
    for line in open(file_name):
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except Exception as err:
            print(f'ERR loading line "{line[:35]}" from "{file_name}" : {err}')
        index += 1
        if not index % perc1:
            print('#', end='', flush=True)
        local_db[gen_key(item, keys)] = item

    data.update(local_db)
    t1 = time.monotonic()

    print(f'\nLoaded {len(local_db):,} items, added {len(data) - isize:,} new items in {t1-t0:.2f}s\n')


def gen_key(item, keys: list) -> str:
    if keys and isinstance(keys, (list, tuple)):
        return KEY_SEP.join(str(item.get(k, '')) for k in keys)
    else:
        return str(item)
