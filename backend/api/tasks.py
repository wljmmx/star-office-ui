"""Tasks API routes."""

import json
from datetime import datetime
from flask import Blueprint, jsonify, request
from config import Config
from services.database_service import get_db_service
from services.task_manager import TaskManager, TaskList, TaskListService

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

# Initialize task list service
task_list_service = TaskListService()

@tasks_bp.route('', methods=['GET'])
def get_all_tasks():
    """Get all tasks."""
    try:
        db = get_db_service()
        tasks = db.load_all_tasks()
        return jsonify({
            "ok": True,
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
        # Load all tasks and find the one we need
        tasks = db.load_all_tasks()
        task = next((t for t in tasks if t.task_id == task_id), None)
        
        if task:
            return jsonify({
                "ok": True,
                "data": {
                    "task": task.to_dict()
                }
            }), 200
        
        return jsonify({
            "ok": False,
            "msg": "Task not found",
            "data": None
        }), 404
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@tasks_bp.route('/agent/<agent_id>', methods=['GET'])
def get_agent_tasks(agent_id):
    """Get all tasks assigned to a specific agent."""
    try:
        db = get_db_service()
        tasks = db.load_all_tasks()
        agent_tasks = [t for t in tasks if t.assigned_agent == agent_id]
        
        return jsonify({
            "ok": True,
            "data": {
                "tasks": [task.to_dict() for task in agent_tasks],
                "count": len(agent_tasks)
            }
        }), 200
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@tasks_bp.route('/list/<list_id>', methods=['GET'])
def get_tasks_by_list(list_id):
    """Get all tasks in a specific list."""
    try:
        db = get_db_service()
        tasks = db.load_all_tasks()
        list_tasks = [t for t in tasks if t.list_id == list_id]
        
        # Sort by position
        list_tasks = sorted(list_tasks, key=lambda t: t.position)
        
        return jsonify({
            "ok": True,
            "data": {
                "list_id": list_id,
                "tasks": [task.to_dict() for task in list_tasks],
                "count": len(list_tasks)
            }
        }), 200
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@tasks_bp.route('/lists', methods=['GET'])
def get_all_lists():
    """Get all task lists."""
    try:
        lists = TaskManager.get_default_lists()
        return jsonify({
            "ok": True,
            "data": {
                "lists": [lst.to_dict() for lst in lists]
            }
        }), 200
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@tasks_bp.route('', methods=['POST'])
def create_task():
    """Create a new task."""
    try:
        data = request.get_json() or {}
        
        if not data.get('name'):
            return jsonify({
                "ok": False,
                "msg": "Task name is required",
                "data": None
            }), 400
        
        # Create task using TaskManager
        task = TaskManager.create_task(
            name=data['name'],
            description=data.get('description', ''),
            status=data.get('status', 'pending'),
            list_id=data.get('list_id'),
            checklist=data.get('checklist'),
        )
        
        # Save to database
        conn = sqlite3.connect(str(Config.DATABASE_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tasks (id, project_id, name, description, status, assigned_agent,
                             priority, list_id, position, checklist, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            task.task_id,
            data.get('project_id'),
            task.name,
            task.description,
            task.status,
            data.get('assigned_agent'),
            data.get('priority', 5),
            task.list_id,
            task.position,
            json.dumps([item.to_dict() for item in task.checklist]) if task.checklist else None
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "ok": True,
            "data": {
                "task": task.to_dict()
            }
        }), 201
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@tasks_bp.route('/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task."""
    try:
        data = request.get_json() or {}
        
        conn = sqlite3.connect(str(Config.DATABASE_PATH))
        cursor = conn.cursor()
        
        # Check if task exists
        cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                "ok": False,
                "msg": "Task not found"
            }), 404
        
        # Build update query
        updates = []
        params = []
        
        if 'name' in data:
            updates.append("name = ?")
            params.append(data['name'])
        if 'description' in data:
            updates.append("description = ?")
            params.append(data.get('description', ''))
        if 'status' in data:
            updates.append("status = ?")
            params.append(data['status'])
        if 'assigned_agent' in data:
            updates.append("assigned_agent = ?")
            params.append(data.get('assigned_agent'))
        if 'priority' in data:
            updates.append("priority = ?")
            params.append(data['priority'])
        if 'list_id' in data:
            updates.append("list_id = ?")
            params.append(data['list_id'])
        if 'position' in data:
            updates.append("position = ?")
            params.append(data['position'])
        if 'checklist' in data:
            updates.append("checklist = ?")
            params.append(json.dumps(data['checklist']))
        
        if updates:
            updates.append("updated_at = datetime('now')")
            params.append(task_id)
            
            cursor.execute(f"""
                UPDATE tasks
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            
            conn.commit()
        
        conn.close()
        
        return jsonify({
            "ok": True,
            "msg": "Task updated successfully",
            "data": {
                "task_id": task_id,
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@tasks_bp.route('/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task."""
    try:
        conn = sqlite3.connect(str(Config.DATABASE_PATH))
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        
        if deleted:
            return jsonify({
                "ok": True,
                "msg": "Task deleted successfully",
                "data": {
                    "task_id": task_id,
                }
            }), 200
        
        return jsonify({
            "ok": False,
            "msg": "Task not found",
            "data": None
        }), 404
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@tasks_bp.route('/<task_id>/checklist/<item_id>/complete', methods=['POST'])
def complete_checklist_item(task_id, item_id):
    """Mark a checklist item as complete."""
    try:
        import json
        
        conn = sqlite3.connect(str(Config.DATABASE_PATH))
        cursor = conn.cursor()
        
        # Get current checklist
        cursor.execute("SELECT checklist FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({
                "ok": False,
                "msg": "Task not found",
                "data": None
            }), 404
        
        checklist = json.loads(row['checklist']) if row['checklist'] else []
        
        # Find and update item
        for item in checklist:
            if item['id'] == item_id:
                item['completed'] = True
                item['completed_at'] = datetime.now().isoformat()
                break
        
        # Save updated checklist
        cursor.execute("""
            UPDATE tasks SET checklist = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (json.dumps(checklist), task_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "ok": True,
            "msg": "Checklist item completed",
            "data": {
                "task_id": task_id,
                "item_id": item_id,
                "checklist": checklist
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500
