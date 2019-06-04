"""
Load local config files.
"""
import os
import sys


def load_local_config(fname: str):
    """
    Load local Text-DB config and return the functions.
    Only keys, filters, validate are used.
    """
    sys.path.append(os.getcwd())
    module = __import__(fname)
    if not hasattr(module, 'tdb_config'):
        return
    config = module.tdb_config
    if not isinstance(config, dict):
        return
    return config
