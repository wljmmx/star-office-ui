"""Tasks API routes."""

from flask import jsonify
from . import tasks_bp
from services.database_service import get_db_service

@tasks_bp.route('', methods=['GET'])
def get_all_tasks():
    """Get all tasks."""
    try:
        db = get_db_service()
        tasks = db.load_all_tasks()
        return jsonify({
            "ok": True,
            "tasks": [task.to_dict() for task in tasks]
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500
