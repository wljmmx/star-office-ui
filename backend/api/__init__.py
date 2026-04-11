"""API routes package."""

# Import all blueprints from individual modules
from .agents import agents_bp
from .tasks import tasks_bp
from .state import state_bp
from .assets import assets_bp
from .config import config_bp
from .join_keys import join_keys_bp
from .avatars import avatars_bp
from .environments import environments_bp

__all__ = [
    'agents_bp',
    'tasks_bp',
    'state_bp',
    'assets_bp',
    'config_bp',
    'join_keys_bp',
    'avatars_bp',
    'environments_bp',
]
