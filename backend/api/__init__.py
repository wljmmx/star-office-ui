"""API routes package."""

from flask import Blueprint

# Create blueprints
agents_bp = Blueprint('agents', __name__, url_prefix='/api/agents')
tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')
projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')
state_bp = Blueprint('state', __name__, url_prefix='/api/state')
assets_bp = Blueprint('assets', __name__, url_prefix='/api/assets')
config_bp = Blueprint('config', __name__, url_prefix='/api/config')
join_keys_bp = Blueprint('join_keys', __name__, url_prefix='/api/join-keys')
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
