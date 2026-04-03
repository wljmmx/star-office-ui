#!/usr/bin/env python3
"""Store utilities for asset management."""

import json
import os
from pathlib import Path

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_POSITIONS_FILE = os.path.join(ROOT_DIR, "asset-positions.json")
ASSET_DEFAULTS_FILE = os.path.join(ROOT_DIR, "asset-defaults.json")
RUNTIME_CONFIG_FILE = os.path.join(ROOT_DIR, "runtime-config.json")
JOIN_KEYS_FILE = os.path.join(ROOT_DIR, "join-keys.json")


def load_asset_positions(file_path=ASSET_POSITIONS_FILE):
    """Load asset positions from file."""
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Store] Error loading positions: {e}")
        return {}


def save_asset_positions(file_path=ASSET_POSITIONS_FILE, data=None):
    """Save asset positions to file."""
    if data is None:
        data = {}
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[Store] Error saving positions: {e}")
        return False


def load_asset_defaults(file_path=ASSET_DEFAULTS_FILE):
    """Load asset defaults from file."""
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Store] Error loading defaults: {e}")
        return {}


def save_asset_defaults(file_path=ASSET_DEFAULTS_FILE, data=None):
    """Save asset defaults to file."""
    if data is None:
        data = {}
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[Store] Error saving defaults: {e}")
        return False


def load_runtime_config(file_path=RUNTIME_CONFIG_FILE):
    """Load runtime configuration from file."""
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Store] Error loading config: {e}")
        return {}


def save_runtime_config(file_path=RUNTIME_CONFIG_FILE, data=None):
    """Save runtime configuration to file."""
    if data is None:
        data = {}
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[Store] Error saving config: {e}")
        return False


def load_join_keys(file_path=JOIN_KEYS_FILE):
    """Load join keys from file."""
    if not os.path.exists(file_path):
        return {"keys": []}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Store] Error loading join keys: {e}")
        return {"keys": []}


def save_join_keys(file_path=JOIN_KEYS_FILE, data=None):
    """Save join keys to file."""
    if data is None:
        data = {"keys": []}
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[Store] Error saving join keys: {e}")
        return False
