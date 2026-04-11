"""Store utilities for file-based data storage.

Provides functions for loading and saving JSON-based configuration files:
- Asset positions
- Asset defaults
- Runtime configuration
- Join keys
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def _safe_load_json(file_path: str) -> Dict[str, Any]:
    """Safely load JSON from file, return empty dict on error."""
    path = Path(file_path)
    if not path.exists():
        logger.debug(f"File not found, returning empty dict: {file_path}")
        return {}
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading {file_path}: {e}")
        return {}


def _safe_save_json(file_path: str, data: Dict[str, Any]) -> bool:
    """Safely save JSON to file, return True on success."""
    path = Path(file_path)
    try:
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logger.error(f"Error saving {file_path}: {e}")
        return False


# Asset positions
def load_asset_positions(file_path: str) -> Dict[str, Any]:
    """Load asset positions from JSON file."""
    return _safe_load_json(file_path)


def save_asset_positions(file_path: str, data: Dict[str, Any]) -> bool:
    """Save asset positions to JSON file."""
    return _safe_save_json(file_path, data)


# Asset defaults
def load_asset_defaults(file_path: str) -> Dict[str, Any]:
    """Load asset defaults from JSON file."""
    return _safe_load_json(file_path)


def save_asset_defaults(file_path: str, data: Dict[str, Any]) -> bool:
    """Save asset defaults to JSON file."""
    return _safe_save_json(file_path, data)


# Runtime config
def load_runtime_config(file_path: str) -> Dict[str, Any]:
    """Load runtime configuration from JSON file."""
    return _safe_load_json(file_path)


def save_runtime_config(file_path: str, data: Dict[str, Any]) -> bool:
    """Save runtime configuration to JSON file."""
    return _safe_save_json(file_path, data)


# Join keys
def load_join_keys(file_path: str) -> Dict[str, Any]:
    """Load join keys from JSON file."""
    return _safe_load_json(file_path)


def save_join_keys(file_path: str, data: Dict[str, Any]) -> bool:
    """Save join keys to JSON file."""
    return _safe_save_json(file_path, data)
