import time
from os import path
import ujson as json
from subprocess import check_output

KEY_SEP = '-'

ROOT_FOLDER = '.'


cdef int wc_lines(str file_name):
    cdef int fsize = int(
        check_output(f'wc -l {file_name}', shell=True).strip().split()[0]
    )
    return fsize


def load_json_file(str file_name, dict data, object key_func):
    """
    Loads a single JL file.
    """
    cdef float t0 = time.monotonic()
    cdef int fsize = wc_lines(file_name)
    cdef int isize = len(data)
    cdef float perc1 = fsize // 100

    cdef str rel_name = path.relpath(file_name, ROOT_FOLDER)
    print(f'Loading {fsize:,} lines from "{rel_name}" ...')

    cdef dict stats = {
        'time': 0,
        'lines': 0,
    }
    # cdef dict local_db = {}

    cdef str line
    cdef str key
    cdef object item

    for line in open(file_name):
        line = line.strip()
        if line == '':
            continue
        # Increment nr of non-empty lines
        stats['lines'] += 1
        # Show progress
        if not stats['lines'] % perc1:
            print('#')  #, end='', flush=True)
        try:
            item = json.loads(line)
        except Exception as err:
            if len(line) > 45:
                print(f'ERR loading line "{line[:20]}...{line[-20:]}" from "{rel_name}" : {err}')
            else:
                print(f'ERR loading line "{line}" from "{rel_name}" : {err}')
        # Ignore null items, they don't make sense
        if not item:
            # stats['empty_items'] += 1
            continue
        # Will process filters here
        # Will process item here
        key = key_func(item)
        # Ignore null keys, they don't make sense
        if not key:
            # stats['empty_keys'] += 1
            continue
        data[key] = item

    # data.update(local_db)
    cdef float t1 = time.monotonic()
    stats['time'] = f'{t1-t0:.3f}s'

    print(f'\nStatistics: {stats}')
    print(f'Loaded all items, added {len(data) - isize:,} new items.\n')
