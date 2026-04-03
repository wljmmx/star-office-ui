"""Agents API routes."""

from flask import jsonify, request
from . import agents_bp
from database import get_db_connection
from datetime import datetime

@agents_bp.route('', methods=['GET'])
def get_all_agents():
    """Get all agents."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                a.id,
                a.name,
                a.type,
                a.status,
                a.current_task_id,
                t.id as task_id,
                t.name as task_title,
                t.status as task_status,
                t.priority as task_progress
            FROM agents a
            LEFT JOIN tasks t ON a.current_task_id = t.id
            ORDER BY a.id
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        agents = []
        for row in rows:
            agent = {
                "agentId": str(row["id"]),
                "name": row["name"] or "Unknown",
                "pixel_character": None,
                "avatar_url": None,
                "role": row["type"] or "dev",
                "state": row["status"] or "idle",
                "area": "writing" if row["status"] in ["writing", "researching", "executing", "syncing"] else "breakroom",
                "source": "github-collab",
                "isMain": row["type"] == "manager",
                "detail": _get_agent_detail(row),
                "updated_at": datetime.now().isoformat(),
                "joinKey": None,
                "authStatus": "approved",
                "authExpiresAt": None,
                "lastPushAt": None,
                "task_id": row["task_id"],
                "task_title": row["task_title"],
                "task_progress": row["task_progress"],
            }
            agents.append(agent)
        
        return jsonify({
            "ok": True,
            "agents": agents
        })
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

def _get_agent_detail(row) -> str:
    """Generate agent detail message from task info."""
    status = row["status"] or "idle"
    
    if status == "idle":
        return "待命中，随时准备为你服务"
    
    if row["task_title"]:
        progress = row["task_progress"] or 0
        return f"正在处理：{row['task_title']} ({progress}%)"
    
    state_messages = {
        "writing": "正在编写代码...",
        "researching": "正在调研方案...",
        "executing": "正在执行任务...",
        "syncing": "正在同步数据...",
        "error": "遇到错误，需要协助",
    }
    
    return state_messages.get(status, "工作中...")

@agents_bp.route('/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get a specific agent."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                a.id,
                a.name,
                a.type,
                a.status,
                a.current_task_id,
                t.id as task_id,
                t.name as task_title,
                t.status as task_status,
                t.priority as task_progress
            FROM agents a
            LEFT JOIN tasks t ON a.current_task_id = t.id
            WHERE a.id = ?
        """, (agent_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                "ok": False,
                "msg": "Agent not found"
            }), 404
        
        agent = {
            "agentId": str(row["id"]),
            "name": row["name"] or "Unknown",
            "pixel_character": None,
            "avatar_url": None,
            "role": row["type"] or "dev",
            "state": row["status"] or "idle",
            "area": "writing" if row["status"] in ["writing", "researching", "executing", "syncing"] else "breakroom",
            "source": "github-collab",
            "isMain": row["type"] == "manager",
            "detail": _get_agent_detail(row),
            "updated_at": datetime.now().isoformat(),
            "task_id": row["task_id"],
            "task_title": row["task_title"],
            "task_progress": row["task_progress"],
        }
        
        return jsonify({
            "ok": True,
            "agent": agent
        })
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@agents_bp.route('/<agent_id>/status', methods=['POST'])
def update_agent_status(agent_id):
    """Update agent status."""
    try:
        data = request.get_json() or {}
        new_status = data.get('state', '')
        
        if not new_status:
            return jsonify({
                "ok": False,
                "msg": "Missing state parameter"
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE agents
            SET status = ?, last_heartbeat = ?
            WHERE id = ?
        """, (new_status, datetime.now().isoformat(), agent_id))
        
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        
        if updated:
            return jsonify({
                "ok": True,
                "state": new_status
            })
        
        return jsonify({
            "ok": False,
            "msg": "Failed to update agent status"
        }), 500
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500
