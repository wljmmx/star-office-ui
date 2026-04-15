"""API routes package."""

# Import blueprints from individual modules
from .agents import agents_bp
from .tasks import tasks_bp
from .projects import projects_bp
from .state import state_bp
from .assets import assets_bp
from .config import config_bp
from .join_keys import join_keys_bp

from flask import Blueprint
health_bp = Blueprint('health', __name__, url_prefix='/api')

__all__ = [
    'agents_bp',
    'tasks_bp',
    'projects_bp',
    'state_bp',
    'assets_bp',
    'config_bp',
    'join_keys_bp',
    'health_bp',
]
