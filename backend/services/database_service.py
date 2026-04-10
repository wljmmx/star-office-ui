"""Database service layer for github-collab integration."""

import sqlite3
from typing import List, Optional, Dict
from pathlib import Path

from config import Config
from models import Agent, Task

class DatabaseService:
    """Service for interacting with github-collab database."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database service."""
        self.db_path = db_path or Config.DATABASE_PATH
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file exists."""
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"github-collab database not found: {self.db_path}"
            )
    
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
            
            # Load agents
            cursor.execute("""
                SELECT id, name, type, status, current_task_id, last_heartbeat, 
                       capabilities, address, max_concurrent_tasks, session_id
                FROM agents
                ORDER BY id
            """)
            agent_rows = cursor.fetchall()
            
            # Load tasks
            cursor.execute("""
                SELECT id, project_id, name, description, status, assigned_agent, 
                       priority, created_at, updated_at, completed_at
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
                       capabilities, address, max_concurrent_tasks, session_id
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
                           priority, created_at, updated_at, completed_at
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
    
    def load_all_tasks(self) -> List[Task]:
        """Load all tasks from database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, project_id, name, description, status, assigned_agent,
                       priority, created_at, updated_at, completed_at
                FROM tasks
                ORDER BY updated_at DESC
            """)
            
            tasks = [Task.from_db(dict(row)) for row in cursor.fetchall()]
            return tasks
        
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
