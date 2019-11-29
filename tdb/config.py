"""
Load local config files.
"""
from pathlib import Path
from runpy import run_path
from typing import Dict, Callable

KNOWN_FIELDS = ('keys', 'validate', 'transform')


def load_local_config(fname: str, model='tdb_config') -> Dict[str, Callable]:
    """
    Load local Text-DB config and return the functions.
    Only keys, filters, validation are used.
    """
    config: Dict[str, Callable] = {}

    fpath = str(Path(fname).expanduser().resolve())
    module = run_path(fpath)

    if module.get(model):
        config = module[model]
    if not isinstance(config, dict):
        return {}

    return {k: v for k, v in config.items() if k in KNOWN_FIELDS}
