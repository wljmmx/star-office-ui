"""Database service layer for github-collab integration."""

import sqlite3
from typing import List, Optional, Dict
from pathlib import Path
from threading import Lock

from config import Config
from models import Agent, Task, Project

class ConnectionPool:
    """Simple connection pool for thread-safe database access."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.lock = Lock()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a thread-safe database connection."""
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

class DatabaseService:
    """Service for interacting with github-collab database."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database service."""
        self.db_path = db_path or Config.DATABASE_PATH
        self.pool = ConnectionPool(self.db_path)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file exists."""
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"github-collab database not found: {self.db_path}"
            )
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return self.pool.get_connection()
    
    def load_all_projects(self) -> List[Project]:
        """Load all projects from database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, github_url, description, status, work_dir, 
                       created_at, updated_at
                FROM projects
                ORDER BY created_at DESC
            """)
            
            projects = [Project.from_db(dict(row)) for row in cursor.fetchall()]
            return projects
        
        finally:
            conn.close()
    
    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """Get a specific project by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, github_url, description, status, work_dir, 
                       created_at, updated_at
                FROM projects
                WHERE id = ?
            """, (project_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return Project.from_db(dict(row))
        
        finally:
            conn.close()
    
    def load_all_agents(self) -> List[Agent]:
        """Load all agents from database with project associations."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Load agents with project info
            cursor.execute("""
                SELECT a.id, a.name, a.pixel_character, a.avatar_url, a.role, a.status, 
                       a.current_task_id, a.current_project_id, a.project_name, a.project_url,
                       a.created_at, a.updated_at
                FROM agents a
                ORDER BY a.id
            """)
            agent_rows = cursor.fetchall()
            
            # Load tasks with project info
            cursor.execute("""
                SELECT t.id, t.title, t.status, t.progress, t.assigned_to, 
                       t.project_id, t.project_name, t.project_url,
                       t.created_at, t.updated_at
                FROM tasks t
            """)
            task_rows = cursor.fetchall()
            
            # Load all projects
            cursor.execute("""
                SELECT id, name, github_url, description, status, work_dir, 
                       created_at, updated_at
                FROM projects
            """)
            project_rows = cursor.fetchall()
            
            # Create lookups
            tasks_map = {}
            for row in task_rows:
                row_dict = dict(row)
                project = None
                if row_dict.get('project_id'):
                    project = Project.from_db({
                        'id': row_dict['project_id'],
                        'name': row_dict.get('project_name'),
                        'github_url': row_dict.get('project_url'),
                    })
                tasks_map[row['id']] = Task.from_db(row_dict, project)
            
            projects_map = {row['id']: Project.from_db(dict(row)) for row in project_rows}
            
            # Create agents with task and project info
            agents = []
            for row in agent_rows:
                db_record = dict(row)
                
                # Get task if assigned
                task_id = db_record.get('current_task_id')
                task = tasks_map.get(task_id) if task_id else None
                
                # Get project from agent's project fields or from task
                project = None
                if db_record.get('current_project_id'):
                    project = projects_map.get(db_record['current_project_id'])
                    if not project:
                        # Create project from stored fields
                        project = Project.from_db({
                            'id': db_record['current_project_id'],
                            'name': db_record.get('project_name'),
                            'github_url': db_record.get('project_url'),
                        })
                elif task and task.project_id:
                    # Inherit project from task
                    project = projects_map.get(task.project_id)
                
                agent = Agent.from_db(db_record, task, project)
                agents.append(agent)
            
            return agents
        
        finally:
            conn.close()
    
    def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """Get a specific agent by ID with project associations."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, pixel_character, avatar_url, role, status, 
                       current_task_id, current_project_id, project_name, project_url,
                       created_at, updated_at
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
            project = None
            
            if task_id:
                cursor.execute("""
                    SELECT id, title, status, progress, assigned_to, 
                           project_id, project_name, project_url,
                           created_at, updated_at
                    FROM tasks
                    WHERE id = ?
                """, (task_id,))
                task_row = cursor.fetchone()
                if task_row:
                    task_dict = dict(task_row)
                    # Get project for task
                    if task_dict.get('project_id'):
                        project = self.get_project_by_id(task_dict['project_id'])
                    task = Task.from_db(task_dict, project)
            
            # Get project from agent's project fields if not from task
            if not project and db_record.get('current_project_id'):
                project = self.get_project_by_id(db_record['current_project_id'])
            
            return Agent.from_db(db_record, task, project)
        
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
        """Load all tasks from database with project associations."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, status, progress, assigned_to, 
                       project_id, project_name, project_url,
                       created_at, updated_at
                FROM tasks
                ORDER BY updated_at DESC
            """)
            
            tasks = []
            for row in cursor.fetchall():
                row_dict = dict(row)
                project = None
                
                # Load project if associated
                if row_dict.get('project_id'):
                    project = self.get_project_by_id(row_dict['project_id'])
                    if not project:
                        # Create project from stored fields
                        project = Project.from_db({
                            'id': row_dict['project_id'],
                            'name': row_dict.get('project_name'),
                            'github_url': row_dict.get('project_url'),
                        })
                
                tasks.append(Task.from_db(row_dict, project))
            
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
_db_service_lock = Lock()

def get_db_service() -> DatabaseService:
    """Get database service singleton."""
    global _db_service
    with _db_service_lock:
        if _db_service is None:
            _db_service = DatabaseService()
    return _db_service
