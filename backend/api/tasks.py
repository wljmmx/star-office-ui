"""Tasks API routes."""

from flask import Blueprint, jsonify, request
from services.database_service import get_db_service

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

@tasks_bp.route('', methods=['GET'])
def get_all_tasks():
    """Get all tasks."""
    try:
        db = get_db_service()
        tasks = db.load_all_tasks()
        return jsonify({
            "ok": True,
            "msg": "操作成功",
            "data": {
                "tasks": [task.to_dict() for task in tasks]
            }
        }), 200
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@tasks_bp.route('/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task."""
    try:
        db = get_db_service()
        task = db.get_task_by_id(task_id)
        
        if task:
            return jsonify({
                "ok": True,
                "msg": "操作成功",
                "data": {
                    "task": task.to_dict()
                }
            }), 200
        
        return jsonify({
            "ok": False,
            "msg": "任务未找到",
            "data": None
        }), 404
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500
