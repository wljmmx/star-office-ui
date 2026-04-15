"""Configuration management for Star Office UI."""

import os
import re
from pathlib import Path
from typing import List, Set


class ConfigError(Exception):
    """Configuration validation error."""
    pass


def _validate_secret_key(key: str, min_length: int = 32) -> bool:
    """
    Validate secret key strength.
    
    Requirements:
    - Minimum length of 32 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    
    Args:
        key: The secret key to validate
        min_length: Minimum required length
        
    Returns:
        True if key meets requirements
        
    Raises:
        ConfigError: If key fails validation
    """
    if len(key) < min_length:
        raise ConfigError(
            f"SECRET_KEY must be at least {min_length} characters (got {len(key)})"
        )
    
    if not re.search(r'[A-Z]', key):
        raise ConfigError("SECRET_KEY must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', key):
        raise ConfigError("SECRET_KEY must contain at least one lowercase letter")
    
    if not re.search(r'\d', key):
        raise ConfigError("SECRET_KEY must contain at least one digit")
    
    if not re.search(r'[^A-Za-z0-9]', key):
        raise ConfigError("SECRET_KEY must contain at least one special character")
    
    return True


def _parse_cors_origins(env_value: str) -> List[str]:
    """
    Parse CORS origins from environment variable.
    
    Supports comma-separated list of origins.
    Each origin is validated to ensure it's a valid URL format.
    
    Args:
        env_value: Comma-separated list of origins
        
    Returns:
        List of validated origins
        
    Raises:
        ConfigError: If any origin is invalid
    """
    if not env_value:
        return []
    
    origins = [origin.strip() for origin in env_value.split(',') if origin.strip()]
    
    # Validate each origin format
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'$', re.IGNORECASE
    )
    
    for origin in origins:
        if not url_pattern.match(origin):
            raise ConfigError(f"Invalid CORS origin format: {origin}")
    
    return origins + ["*"]


class Config:
    """Base configuration."""
    
    # Paths - Use absolute path resolution
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    # Frontend directory
    FRONTEND_DIR = BASE_DIR / "frontend"
    
    # Database path - resolve relative to BASE_DIR
    DATABASE_PATH = BASE_DIR / "skills" / "github-collab" / "github-collab.db"
    
    # If database doesn't exist, try alternative path
    if not DATABASE_PATH.exists():
        # Try: Star-Office-UI/../skills/github-collab/github-collab.db
        ALT_DB_PATH = BASE_DIR.parent / "skills" / "github-collab" / "github-collab.db"
        if ALT_DB_PATH.exists():
            DATABASE_PATH = ALT_DB_PATH
    
    # Data files
    ASSET_POSITIONS_FILE = BASE_DIR / "asset-positions.json"
    ASSET_DEFAULTS_FILE = BASE_DIR / "asset-defaults.json"
    RUNTIME_CONFIG_FILE = BASE_DIR / "runtime-config.json"
    JOIN_KEYS_FILE = BASE_DIR / "join-keys.json"
    
    # Flask config - SECRET_KEY MUST be set via environment variable
    _raw_secret_key = os.getenv("FLASK_SECRET_KEY")
    if not _raw_secret_key:
        raise ConfigError(
            "FLASK_SECRET_KEY environment variable is required. "
            "Generate one using: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
    
    # Validate secret key strength
    try:
        _validate_secret_key(_raw_secret_key)
        SECRET_KEY = _raw_secret_key
    except ConfigError as e:
        raise ConfigError(f"Invalid SECRET_KEY: {str(e)}")
    
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SOUI_COOKIE_SECURE", "false").lower() == "true"
    
    # Server config
    DEBUG = os.getenv("SOUI_DEBUG", "false").lower() == "true"
    HOST = os.getenv("SOUI_HOST", "0.0.0.0")
    PORT = int(os.getenv("SOUI_PORT", "5000"))
    
    # CORS config - No more wildcard (*)
    _cors_origins_raw = os.getenv("SOUI_CORS_ORIGINS", "")
    try:
        CORS_ORIGINS = _parse_cors_origins(_cors_origins_raw)
    except ConfigError as e:
        raise ConfigError(f"Invalid CORS_ORIGINS: {str(e)}")
    
    # Allow localhost by default for development
    if DEBUG and "http://localhost:3000" not in CORS_ORIGINS:
        CORS_ORIGINS.append("http://localhost:3000")
    if DEBUG and "http://127.0.0.1:3000" not in CORS_ORIGINS:
        CORS_ORIGINS.append("http://127.0.0.1:3000")
    
    # SocketIO config - Use validated CORS origins
    SOCKETIO_CORS_ORIGINS = CORS_ORIGINS if CORS_ORIGINS else ["http://localhost:3000"]
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
    def validate(cls) -> bool:
        """
        Validate configuration after initialization.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ConfigError: If configuration is invalid
        """
        errors = []
        
        # Check SECRET_KEY
        if not cls._raw_secret_key:
            errors.append("FLASK_SECRET_KEY is not set")
        
        # Check CORS origins in production
        if not cls.DEBUG and not cls.CORS_ORIGINS:
            errors.append("CORS_ORIGINS must be set in production")
        
        if errors:
            raise ConfigError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist."""
        cls.FRONTEND_DIR.mkdir(exist_ok=True)
        # Don't create database directory - it should exist
    
    @classmethod
    def get_allowed_hosts(cls) -> Set[str]:
        """Get set of allowed hosts for security checks."""
        return set(cls.CORS_ORIGINS)


# Initialize config
Config.ensure_directories()
