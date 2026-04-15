"""Configuration management for Star Office UI."""

import os
from pathlib import Path

class Config:
    """Base configuration."""
    
    # Paths - Use absolute path resolution
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    # Frontend directory
    FRONTEND_DIR = BASE_DIR / "frontend"
    
    # Database path - prioritize environment variable
    ENV_DB_PATH = os.getenv("DATABASE_PATH")
    if ENV_DB_PATH:
        DATABASE_PATH = Path(ENV_DB_PATH)
    else:
        # Fallback to default path
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
    
    # Ensure database directory exists
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
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
    
    # Socket.IO CORS config
    SOCKETIO_CORS_ORIGINS = ["*"]
    
    # Agent states
    VALID_AGENT_STATES = ["idle", "writing", "researching", "executing", "syncing", "error"]
    
    # API version
    API_VERSION = "v1"
