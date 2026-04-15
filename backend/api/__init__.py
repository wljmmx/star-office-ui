"""API routes package."""

from flask import Blueprint

# API Version
API_VERSION = 'v1'

# Create blueprints
agents_bp = Blueprint('agents', __name__, url_prefix=f'/{API_VERSION}/agents')
tasks_bp = Blueprint('tasks', __name__, url_prefix=f'/{API_VERSION}/tasks')
state_bp = Blueprint('state', __name__, url_prefix=f'/{API_VERSION}/state')
assets_bp = Blueprint('assets', __name__, url_prefix=f'/{API_VERSION}/assets')
config_bp = Blueprint('config', __name__, url_prefix=f'/{API_VERSION}/config')
join_keys_bp = Blueprint('join_keys', __name__, url_prefix=f'/{API_VERSION}/join-keys')
health_bp = Blueprint('health', __name__, url_prefix='/api/health')
# Import submodules to register routes
from . import agents
from . import tasks
from . import state
from . import assets
from . import config
from . import join_keys

__all__ = [
    'API_VERSION',
    'agents_bp',
    'tasks_bp', 
    'state_bp',
    'assets_bp',
    'config_bp',
    'join_keys_bp',
    'health_bp',
]
