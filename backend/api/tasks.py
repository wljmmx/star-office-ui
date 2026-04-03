"""Tasks API routes."""

from flask import jsonify, request
from . import tasks_bp
from database import get_db_connection
from datetime import datetime

@tasks_bp.route('', methods=['GET'])
def get_all_tasks():
    """Get all tasks."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id,
                name as title,
                status,
                priority as progress,
                assigned_agent as assigned_to,
                created_at,
                updated_at
            FROM tasks
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            task = {
                "id": row["id"],
                "title": row["title"],
                "status": row["status"],
                "progress": row["priority"] or 0,
                "assigned_to": row["assigned_agent"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            tasks.append(task)
        
        return jsonify({
            "ok": True,
            "tasks": tasks
        })
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@tasks_bp.route('/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id,
                name as title,
                description,
                status,
                priority as progress,
                assigned_agent as assigned_to,
                created_at,
                updated_at
            FROM tasks
            WHERE id = ?
        """, (task_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                "ok": False,
                "msg": "Task not found"
            }), 404
        
        task = {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "status": row["status"],
            "progress": row["priority"] or 0,
            "assigned_to": row["assigned_agent"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        
        return jsonify({
            "ok": True,
            "task": task
        })
    
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
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update task fields
        updates = []
        values = []
        
        if "status" in data:
            updates.append("status = ?")
            values.append(data["status"])
        
        if "progress" in data:
            updates.append("priority = ?")
            values.append(data["progress"])
        
        if "assigned_to" in data:
            updates.append("assigned_agent = ?")
            values.append(data["assigned_to"])
        
        if updates:
            updates.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(task_id)
            
            cursor.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
            
            # Fetch updated task
            cursor.execute("""
                SELECT 
                    id,
                    name as title,
                    description,
                    status,
                    priority as progress,
                    assigned_agent as assigned_to,
                    created_at,
                    updated_at
                FROM tasks
                WHERE id = ?
            """, (task_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                task = {
                    "id": row["id"],
                    "title": row["title"],
                    "description": row["description"],
                    "status": row["status"],
                    "progress": row["priority"] or 0,
                    "assigned_to": row["assigned_agent"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
                
                return jsonify({
                    "ok": True,
                    "task": task
                })
        
        return jsonify({
            "ok": False,
            "msg": "No updates provided"
        }), 400
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500
