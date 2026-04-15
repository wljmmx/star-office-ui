"""Utility functions package."""

from .json_utils import load_json_file, save_json_file
<<<<<<< HEAD
from .sync_service import SyncService

__all__ = [
    'load_json_file',
    'save_json_file',
    'SyncService',
]
=======

# Lazy import for Flask dependencies
try:
    from .sync_service import SyncService
    __all__ = ['load_json_file', 'save_json_file', 'SyncService']
except ImportError:
    __all__ = ['load_json_file', 'save_json_file']
>>>>>>> origin/master
