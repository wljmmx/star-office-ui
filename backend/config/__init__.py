"""Configuration management for Star Office UI."""

import os
from pathlib import Path

class Config:
    """Base configuration."""
    
    # Paths - Use absolute path resolution
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    # Frontend directory
    FRONTEND_DIR = BASE_DIR / "frontend"
    
    # Database path - multiple fallback strategies
    DATABASE_PATH = BASE_DIR / "skills" / "github-collab" / "github-collab.db"
    
    # Fallback 1: Try github-collab directory
    if not DATABASE_PATH.exists():
        ALT_DB_PATH = BASE_DIR / "github-collab" / "github-collab.db"
        if ALT_DB_PATH.exists():
            DATABASE_PATH = ALT_DB_PATH
    
    # Fallback 2: Try parent skills directory
    if not DATABASE_PATH.exists():
        ALT_DB_PATH = BASE_DIR.parent / "skills" / "github-collab" / "github-collab.db"
        if ALT_DB_PATH.exists():
            DATABASE_PATH = ALT_DB_PATH
    
    # Fallback 3: Try environment variable
    ENV_DB_PATH = os.getenv("GITHUB_COLLAB_DB")
    if ENV_DB_PATH and Path(ENV_DB_PATH).exists():
        DATABASE_PATH = Path(ENV_DB_PATH)
    
    # Data files
    ASSET_POSITIONS_FILE = BASE_DIR / "asset-positions.json"
    ASSET_DEFAULTS_FILE = BASE_DIR / "asset-defaults.json"
    RUNTIME_CONFIG_FILE = BASE_DIR / "runtime-config.json"
    JOIN_KEYS_FILE = BASE_DIR / "join-keys.json"
    
    # Flask config
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "star-office-secret-key")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    
    # Server config
    HOST = os.getenv("SOUI_HOST", "0.0.0.0")
    PORT = int(os.getenv("SOUI_PORT", "5000"))
    DEBUG = os.getenv("SOUI_DEBUG", "true").lower() == "true"
    
    # SocketIO config
    SOCKETIO_CORS_ORIGINS = "*"
    SOCKETIO_ASYNC_MODE = "threading"
    
    # Sync config
    SYNC_INTERVAL = int(os.getenv("SOUI_SYNC_INTERVAL", "5"))  # seconds
    
    # State mapping
    VALID_AGENT_STATES = frozenset({
        "idle", "writing", "researching", "executing", "syncing", "error"
    })
    
    STATE_TO_AREA_MAP = {
        "idle": "breakroom",
        "writing": "writing",
        "researching": "writing",
        "executing": "writing",
        "syncing": "writing",
        "error": "error",
    }
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist."""
        cls.FRONTEND_DIR.mkdir(exist_ok=True)
        # Don't create database directory - it should exist

# Initialize config
Config.ensure_directories()
