"""Health check endpoint."""

from flask import Blueprint, jsonify
from datetime import datetime

health_bp = Blueprint('health', __name__, url_prefix='/api/health')

@health_bp.route("", methods=["GET"])
def health_check():
    """Health check endpoint for Docker and load balancers."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "star-office-ui"
    })

__all__ = ['health_bp']
