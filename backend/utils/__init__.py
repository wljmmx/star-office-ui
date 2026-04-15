"""Utility functions package."""

from .json_utils import load_json_file, save_json_file

# Lazy import for Flask dependencies
try:
    from .sync_service import SyncService
    
    def get_sync_service(socketio=None):
        """Get or create SyncService instance."""
        if not hasattr(get_sync_service, '_instance'):
            get_sync_service._instance = SyncService(socketio)
        return get_sync_service._instance
    
    __all__ = ['load_json_file', 'save_json_file', 'SyncService', 'get_sync_service']
except ImportError:
    __all__ = ['load_json_file', 'save_json_file']
