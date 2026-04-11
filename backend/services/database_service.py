"""Database service layer for github-collab integration."""

import sqlite3
import logging
from typing import List, Optional, Dict
from pathlib import Path

from config import Config
from models import Agent, Task

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for interacting with github-collab database."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database service."""
        self.db_path = db_path or Config.DATABASE_PATH
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file exists, create and initialize if not."""
        if not self.db_path.exists():
            # Create parent directory if it doesn't exist
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            # Initialize the database with tables
            self._initialize_database()
            logger.info(f"Database created and initialized: {self.db_path}")
        else:
            logger.debug(f"Database already exists: {self.db_path}")
    
    def _initialize_database(self):
        """Initialize database with agents and tasks tables."""
        logger.info("Initializing database tables...")
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # Create agents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT DEFAULT 'dev',
                    status TEXT DEFAULT 'idle',
                    capabilities TEXT,
                    address TEXT,
                    max_concurrent_tasks INTEGER DEFAULT 1,
                    session_id TEXT,
                    current_task_id TEXT,
                    last_heartbeat TEXT,
                    avatar_type TEXT,
                    avatar_data TEXT,
                    pixel_character TEXT,
                    avatar_url TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (current_task_id) REFERENCES tasks(id)
                )
            """)
            logger.info("Created agents table")
            
            # Create tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    assigned_agent TEXT,
                    priority INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now')),
                    completed_at TEXT,
                    list_id TEXT,
                    position INTEGER,
                    checklist TEXT,
                    FOREIGN KEY (assigned_agent) REFERENCES agents(id)
                )
            """)
            logger.info("Created tasks table")
            
            conn.commit()
            logger.info("Database initialization completed successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise
        finally:
            conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def load_all_agents(self) -> List[Agent]:
        """Load all agents from database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Load agents with avatar fields
            cursor.execute("""
                SELECT id, name, type, status, current_task_id, last_heartbeat, 
                       capabilities, address, max_concurrent_tasks, session_id,
                       avatar_type, avatar_data, pixel_character, avatar_url
                FROM agents
                ORDER BY id
            """)
            agent_rows = cursor.fetchall()
            
            # Load tasks
            cursor.execute("""
                SELECT id, project_id, name, description, status, assigned_agent, 
                       priority, created_at, updated_at, completed_at,
                       list_id, position, checklist
                FROM tasks
            """)
            task_rows = cursor.fetchall()
            
            # Create task lookup
            tasks_map = {row['id']: Task.from_db(dict(row)) for row in task_rows}
            
            # Create agents with task info
            agents = []
            for row in agent_rows:
                db_record = dict(row)
                task = tasks_map.get(db_record.get('current_task_id'))
                agent = Agent.from_db(db_record, task)
                agents.append(agent)
            
            return agents
        
        finally:
            conn.close()
    
    def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """Get a specific agent by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, type, status, current_task_id, last_heartbeat,
                       capabilities, address, max_concurrent_tasks, session_id,
                       avatar_type, avatar_data, pixel_character, avatar_url
                FROM agents
                WHERE id = ?
            """, (agent_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            db_record = dict(row)
            
            # Get task if assigned
            task_id = db_record.get('current_task_id')
            task = None
            if task_id:
                cursor.execute("""
                    SELECT id, project_id, name, description, status, assigned_agent,
                           priority, created_at, updated_at, completed_at,
                           list_id, position, checklist
                    FROM tasks
                    WHERE id = ?
                """, (task_id,))
                task_row = cursor.fetchone()
                if task_row:
                    task = Task.from_db(dict(task_row))
            
            return Agent.from_db(db_record, task)
        
        finally:
            conn.close()
    
    def update_agent_status(self, agent_id: str, new_status: str) -> bool:
        """Update agent status in database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE agents
                SET status = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (new_status, agent_id))
            
            conn.commit()
            return cursor.rowcount > 0
        
        finally:
            conn.close()
    
    def update_agent_avatar(
        self,
        agent_id: str,
        avatar_type: str,
        avatar_data: str,
        pixel_character: str = None
    ) -> bool:
        """Update agent avatar information."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE agents
                SET avatar_type = ?, avatar_data = ?, pixel_character = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (avatar_type, avatar_data, pixel_character, agent_id))
            
            conn.commit()
            return cursor.rowcount > 0
        
        finally:
            conn.close()
    
    def load_all_tasks(self) -> List[Task]:
        """Load all tasks from database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, project_id, name, description, status, assigned_agent,
                       priority, created_at, updated_at, completed_at,
                       list_id, position, checklist
                FROM tasks
                ORDER BY updated_at DESC
            """)
            
            tasks = [Task.from_db(dict(row)) for row in cursor.fetchall()]
            return tasks
        
        finally:
            conn.close()
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a specific task by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, project_id, name, description, status, assigned_agent,
                       priority, created_at, updated_at, completed_at,
                       list_id, position, checklist
                FROM tasks
                WHERE id = ?
            """, (task_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return Task.from_db(dict(row))
        
        finally:
            conn.close()
    
    def get_tasks_by_agent(self, agent_id: str) -> List[Task]:
        """Get all tasks assigned to a specific agent."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, project_id, name, description, status, assigned_agent,
                       priority, created_at, updated_at, completed_at,
                       list_id, position, checklist
                FROM tasks
                WHERE assigned_agent = ?
                ORDER BY updated_at DESC
            """, (agent_id,))
            
            tasks = [Task.from_db(dict(row)) for row in cursor.fetchall()]
            return tasks
        
        finally:
            conn.close()
    
    def get_tasks_by_list(self, list_id: str) -> List[Task]:
        """Get all tasks in a specific list."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, project_id, name, description, status, assigned_agent,
                       priority, created_at, updated_at, completed_at,
                       list_id, position, checklist
                FROM tasks
                WHERE list_id = ?
                ORDER BY position ASC
            """, (list_id,))
            
            tasks = [Task.from_db(dict(row)) for row in cursor.fetchall()]
            return tasks
        
        finally:
            conn.close()
    
    def create_task(self, task: Task) -> bool:
        """Create a new task in database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tasks (
                    id, project_id, name, description, status, assigned_agent,
                    priority, created_at, updated_at, completed_at,
                    list_id, position, checklist
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.id,
                task.project_id,
                task.name,
                task.description,
                task.status,
                task.assigned_agent,
                task.priority,
                task.created_at,
                task.updated_at,
                task.completed_at,
                task.list_id,
                task.position,
                task.checklist
            ))
            
            conn.commit()
            return cursor.rowcount > 0
        
        finally:
            conn.close()
    
    def update_task(self, task: Task) -> bool:
        """Update an existing task in database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE tasks
                SET project_id = ?, name = ?, description = ?, status = ?,
                    assigned_agent = ?, priority = ?, updated_at = ?,
                    completed_at = ?, list_id = ?, position = ?, checklist = ?
                WHERE id = ?
            """, (
                task.project_id,
                task.name,
                task.description,
                task.status,
                task.assigned_agent,
                task.priority,
                task.updated_at,
                task.completed_at,
                task.list_id,
                task.position,
                task.checklist,
                task.id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
        
        finally:
            conn.close()
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task from database by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM tasks
                WHERE id = ?
            """, (task_id,))
            
            conn.commit()
            return cursor.rowcount > 0
        
        finally:
            conn.close()
    
    def normalize_agent_state(self, state: str) -> str:
        """Normalize agent state to valid values."""
        valid_states = Config.VALID_AGENT_STATES
        state_lower = state.lower().strip()
        
        if state_lower in valid_states:
            return state_lower
        
        # Map common synonyms
        state_mapping = {
            "waiting": "idle",
            "standby": "idle",
            "coding": "writing",
            "developing": "writing",
            "coding": "writing",
            "testing": "executing",
            "deploying": "executing",
            "running": "executing",
            "synchronizing": "syncing",
            "failed": "error",
            "broken": "error",
        }
        
        return state_mapping.get(state_lower, "idle")

# Singleton instance
_db_service: Optional[DatabaseService] = None

def get_db_service() -> DatabaseService:
    """Get database service singleton."""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service


# ============================================================================
# Legacy compatibility layer - for backward compatibility with database.py
# ============================================================================

import os
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


def _normalize_agent_state_legacy(status: str) -> str:
    """Map github-collab status to Star-Office-UI state (legacy)."""
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


def _state_to_area_legacy(state: str) -> str:
    """Map agent state to office area (legacy)."""
    STATE_TO_AREA = {
        "idle": "breakroom",
        "writing": "writing",
        "researching": "writing",
        "executing": "writing",
        "syncing": "writing",
        "error": "error",
    }
    return STATE_TO_AREA.get(state, "breakroom")


def _get_agent_detail_legacy(row) -> str:
    """Generate agent detail message from task info (legacy)."""
    state = _normalize_agent_state_legacy(row["status"])
    
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


def load_agents_from_db() -> List[Dict]:
    """Load agents from github-collab database (legacy compatibility)."""
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
        if not os.path.exists(GITHUB_COLLAB_DB):
            raise FileNotFoundError(f"github-collab database not found at: {GITHUB_COLLAB_DB}\nChecked paths: {FALLBACK_PATHS}")
        
        conn = sqlite3.connect(GITHUB_COLLAB_DB)
        conn.row_factory = sqlite3.Row
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
            state = _normalize_agent_state_legacy(row["status"])
            agent = {
                "agentId": str(row["id"]),
                "name": row["name"] or "Unknown",
                "type": row["type"] or "dev",
                "state": state,
                "area": _state_to_area_legacy(state),
                "capabilities": row["capabilities"] or "",
                "address": row["address"] or "",
                "source": "github-collab",
                "isMain": row["type"] == "manager",
                "detail": _get_agent_detail_legacy(row),
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


def load_tasks_from_db() -> List[Dict]:
    """Load tasks from github-collab database (legacy compatibility)."""
    try:
        if not os.path.exists(GITHUB_COLLAB_DB):
            raise FileNotFoundError(f"github-collab database not found at: {GITHUB_COLLAB_DB}\nChecked paths: {FALLBACK_PATHS}")
        
        conn = sqlite3.connect(GITHUB_COLLAB_DB)
        conn.row_factory = sqlite3.Row
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
