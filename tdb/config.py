"""
Load local config files.
"""
import os
import sys

KNOWN_FIELDS = ('keys', 'filters', 'validation')


def load_local_config(fname: str, model='tdb_config'):
    """
    Load local Text-DB config and return the functions.
    Only keys, filters, validation are used.
    """
    sys.path.append(os.getcwd())
    module = __import__(fname)
    if not hasattr(module, model):
        return
    config = getattr(module, model)
    if not isinstance(config, dict):
        return
    return {k: v for k, v in config.items() if k in KNOWN_FIELDS}
