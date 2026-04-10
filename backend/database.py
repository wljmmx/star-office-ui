#!/usr/bin/env python3
"""Database layer for Star Office UI - SQLite integration with github-collab."""

import sqlite3
import os
from typing import List, Dict, Optional
from datetime import datetime

# Database path configuration - use environment variable or default
GITHUB_COLLAB_DB = os.environ.get(
    "GITHUB_COLLAB_DB",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "github-collab", "github-collab.db")
)

# Fallback paths to try
FALLBACK_PATHS = [
    "/home/wljmmx/.openclaw/workspace/coder/skills/github-collab/github-collab.db",
    "/workspace/skills/github-collab/github-collab.db",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "skills", "github-collab", "github-collab.db"),
]

# Find existing database
if not os.path.exists(GITHUB_COLLAB_DB):
    for path in FALLBACK_PATHS:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            GITHUB_COLLAB_DB = abs_path
            break


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
        raise FileNotFoundError(f"github-collab database not found at: {GITHUB_COLLAB_DB}\nChecked paths: {FALLBACK_PATHS}")
    
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
        
        # Query agents with optional task info
        cursor.execute("""
            SELECT 
                a.id,
                a.name,
                a.type,
                a.status,
                a.capabilities,
                a.address,
                a.current_task_id,
                a.last_heartbeat,
                t.name as task_name,
                t.status as task_status,
                t.description as task_description
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
            state = normalize_agent_state(row["status"])
            agent = {
                "agentId": str(row["id"]),
                "name": row["name"] or "Unknown",
                "type": row["type"] or "dev",
                "state": state,
                "area": state_to_area(state),
                "capabilities": row["capabilities"] or "",
                "address": row["address"] or "",
                "source": "github-collab",
                "isMain": row["type"] == "manager",
                "detail": _get_agent_detail(row),
                "updated_at": row["last_heartbeat"] or datetime.now().isoformat(),
                "joinKey": None,
                "authStatus": "approved",
                "authExpiresAt": None,
                "lastPushAt": None,
                "pixel_character": None,
                "avatar_url": None,
                "role": row["type"] or "dev",
                "task_id": row["current_task_id"],
                "task_name": row["task_name"],
                "task_status": row["task_status"],
                "task_description": row["task_description"],
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
    
    if row["task_name"]:
        return f"正在处理：{row['task_name']}"
    
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
                project_id,
                name,
                description,
                status,
                assigned_agent,
                priority,
                created_at,
                updated_at,
                completed_at
            FROM tasks
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            task = {
                "id": row["id"],
                "project_id": row["project_id"],
                "name": row["name"],
                "description": row["description"],
                "status": row["status"],
                "assigned_agent": row["assigned_agent"],
                "priority": row["priority"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "completed_at": row["completed_at"],
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
                a.pixel_character,
                a.avatar_url,
                a.role,
                a.status,
                a.current_task_id,
                t.title as task_title,
                t.status as task_status,
                t.progress as task_progress
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
            "pixel_character": row["pixel_character"],
            "avatar_url": row["avatar_url"],
            "role": row["role"] or "dev",
            "state": normalize_agent_state(row["status"]),
            "area": state_to_area(normalize_agent_state(row["status"])),
            "source": "github-collab",
            "isMain": row["role"] == "main",
            "detail": _get_agent_detail(row),
            "updated_at": datetime.now().isoformat(),
            "task_id": row["current_task_id"],
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
            SET status = ?, updated_at = ?
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
    print(f"Database size: {os.path.getsize(GITHUB_COLLAB_DB) if os.path.exists(GITHUB_COLLAB_DB) else 0} bytes")
    
    agents = load_agents_from_db()
    print(f"\nLoaded {len(agents)} agents:")
    for agent in agents:
        print(f"  - {agent['name']} ({agent['agentId']}): {agent['state']} @ {agent['area']}")
        if agent.get('task_title'):
            print(f"    Task: {agent['task_title']} ({agent.get('task_progress', 0)}%)")
    
    tasks = load_tasks_from_db()
    print(f"\nLoaded {len(tasks)} tasks:")
    for task in tasks:
        print(f"  - {task['title']} ({task['status']}): {task['progress']}%")
