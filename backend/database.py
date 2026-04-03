#!/usr/bin/env python3
"""Database layer for Star Office UI - SQLite integration with github-collab."""

import sqlite3
import os
from typing import List, Dict, Optional
from datetime import datetime

# Database path configuration
GITHUB_COLLAB_DB = os.environ.get(
    "GITHUB_COLLAB_DB",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "skills", "github-collab", "github-collab.db")
)

# Resolve relative path
if not os.path.isabs(GITHUB_COLLAB_DB):
    GITHUB_COLLAB_DB = os.path.abspath(GITHUB_COLLAB_DB)


def normalize_agent_state(status: str) -> str:
    """Map github-collab status to Star-Office-UI state."""
    VALID_STATES = frozenset({"idle", "writing", "researching", "executing", "syncing", "error"})
    
    if not status:
        return "idle"
    
    status_lower = status.lower().strip()
    
    # Direct mapping
    if status_lower in VALID_STATES:
        return status_lower
    
    # Semantic mapping
    status_map = {
        "active": "writing",
        "working": "writing",
        "busy": "writing",
        "coding": "writing",
        "developing": "writing",
        "research": "researching",
        "searching": "researching",
        "running": "executing",
        "exec": "executing",
        "deploying": "executing",
        "sync": "syncing",
        "failed": "error",
        "broken": "error",
        "offline": "idle",
        "resting": "idle",
        "waiting": "idle",
    }
    
    return status_map.get(status_lower, "idle")


def state_to_area(state: str) -> str:
    """Map agent state to office area."""
    STATE_TO_AREA = {
        "idle": "breakroom",
        "writing": "writing",
        "researching": "writing",
        "executing": "writing",
        "syncing": "writing",
        "error": "error",
    }
    return STATE_TO_AREA.get(state, "breakroom")


def get_db_connection():
    """Get database connection."""
    if not os.path.exists(GITHUB_COLLAB_DB):
        raise FileNotFoundError(f"github-collab database not found: {GITHUB_COLLAB_DB}")
    
    conn = sqlite3.connect(GITHUB_COLLAB_DB)
    conn.row_factory = sqlite3.Row
    return conn


def load_agents_from_db() -> List[Dict]:
    """Load agents from github-collab database."""
    DEFAULT_AGENTS = [
        {
            "agentId": "star",
            "name": "Star",
            "isMain": True,
            "state": "idle",
            "detail": "待命中，随时准备为你服务",
            "updated_at": datetime.now().isoformat(),
            "area": "breakroom",
            "source": "local",
            "joinKey": None,
            "authStatus": "approved",
            "authExpiresAt": None,
            "lastPushAt": None,
            "pixel_character": None,
            "avatar_url": None,
            "role": "main",
        }
    ]
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query agents with optional task info - match actual table schema
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
        
        if not rows:
            return DEFAULT_AGENTS
        
        agents = []
        for row in rows:
            agent = {
                "agentId": str(row["id"]),
                "name": row["name"] or "Unknown",
                "pixel_character": None,
                "avatar_url": None,
                "role": row["type"] or "dev",
                "state": normalize_agent_state(row["status"]),
                "area": state_to_area(normalize_agent_state(row["status"])),
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
        
        return agents if agents else DEFAULT_AGENTS
    
    except FileNotFoundError as e:
        print(f"[DB] Database not found: {e}")
        return DEFAULT_AGENTS
    except Exception as e:
        print(f"[DB] Error loading agents: {e}")
        return DEFAULT_AGENTS


def _get_agent_detail(row) -> str:
    """Generate agent detail message from task info."""
    state = normalize_agent_state(row["status"])
    
    if state == "idle":
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
    
    return state_messages.get(state, "工作中...")


def load_tasks_from_db() -> List[Dict]:
    """Load tasks from github-collab database."""
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
        
        return tasks
    
    except Exception as e:
        print(f"[DB] Error loading tasks: {e}")
        return []


def get_agent_by_id(agent_id: str) -> Optional[Dict]:
    """Get a specific agent by ID."""
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
            return None
        
        return {
            "agentId": str(row["id"]),
            "name": row["name"] or "Unknown",
            "pixel_character": None,
            "avatar_url": None,
            "role": row["type"] or "dev",
            "state": normalize_agent_state(row["status"]),
            "area": state_to_area(normalize_agent_state(row["status"])),
            "source": "github-collab",
            "isMain": row["type"] == "manager",
            "detail": _get_agent_detail(row),
            "updated_at": datetime.now().isoformat(),
            "task_id": row["task_id"],
            "task_title": row["task_title"],
            "task_progress": row["task_progress"],
        }
    
    except Exception as e:
        print(f"[DB] Error getting agent {agent_id}: {e}")
        return None


def update_agent_status(agent_id: str, status: str) -> bool:
    """Update agent status in database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE agents
            SET status = ?, last_heartbeat = ?
            WHERE id = ?
        """, (status, datetime.now().isoformat(), agent_id))
        
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        
        return updated
    
    except Exception as e:
        print(f"[DB] Error updating agent {agent_id}: {e}")
        return False


if __name__ == "__main__":
    # Test database connection
    print(f"Database path: {GITHUB_COLLAB_DB}")
    print(f"Database exists: {os.path.exists(GITHUB_COLLAB_DB)}")
    
    agents = load_agents_from_db()
    print(f"\nLoaded {len(agents)} agents:")
    for agent in agents:
        print(f"  - {agent['name']} ({agent['agentId']}): {agent['state']} @ {agent['area']}")
    
    tasks = load_tasks_from_db()
    print(f"\nLoaded {len(tasks)} tasks:")
    for task in tasks:
        print(f"  - {task['title']} ({task['status']}): {task['progress']}%")
