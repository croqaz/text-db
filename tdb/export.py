import os
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import ujson as json

ROOT_FOLDER = str(Path.home())


def export_db(data_list: list, out_path: str):
    # https://programiz.com/python-programming/methods/string/format
    # out_path = '~/DATA/Project/{created_at:.7}/proj-data.jl'

    t0 = time.monotonic()
    print('Saving data list ...')

    out_path = str(Path(out_path).expanduser().resolve())
    now = datetime.now()
    open_fds = {}
    file_index = defaultdict(int)

    for o in data_list:
        # Expand the format string using NOW and the object data
        out_file = out_path.format(now=now, **o)
        if out_file not in open_fds:
            out_fold, _ = os.path.split(out_file)
            os.makedirs(out_fold, exist_ok=True)
            rel_name = os.path.relpath(out_file, ROOT_FOLDER)
            print(f'Opening file "{rel_name}" for writing ...')
            open_fds[out_file] = open(out_file, 'w')

        file_index[out_file] += 1
        fd = open_fds[out_file]
        fd.write(json.dumps(o, ensure_ascii=False, escape_forward_slashes=False, sort_keys=True))
        fd.write('\n')

    for fd in open_fds.values():
        fd.close()

    t1 = time.monotonic()
    file_index = {os.path.relpath(k, ROOT_FOLDER): v for k, v in file_index.items()}

    print(f'\nStatistics: {file_index}')
    print(f'Exported all items in {t1-t0:.2f}s!')
    # The end
