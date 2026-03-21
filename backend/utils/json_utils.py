"""JSON utility functions."""

import json
from pathlib import Path
from typing import Any, TypeVar, Optional

T = TypeVar('T')

def load_json_file(file_path: Path, default: T) -> T:
    """Load JSON file with default fallback."""
    try:
        if not Path(file_path).exists():
            return default
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default

def save_json_file(file_path: Path, data: Any):
    """Save data to JSON file."""
    # Ensure parent directory exists
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
