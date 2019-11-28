"""
Load local config files.
"""
from pathlib import Path
from typing import Any, Dict, Callable

KNOWN_FIELDS = ('keys', 'validate', 'transform')


def load_local_config(fname: str, model='tdb_config') -> Dict[str, Callable]:
    """
    Load local Text-DB config and return the functions.
    Only keys, filters, validation are used.
    """
    config: Dict[str, Callable] = {}
    glob_vars: Dict[str, Any] = {}
    local_vars: Dict[str, Any] = {}

    fpath = str(Path(fname).expanduser().resolve())
    exec(open(fpath).read(), glob_vars, local_vars)

    if glob_vars.get(model):
        config = glob_vars[model]
    elif local_vars.get(model):
        config = local_vars[model]
    if not isinstance(config, dict):
        return {}

    return {k: v for k, v in config.items() if k in KNOWN_FIELDS}
