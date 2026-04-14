"""Database service layer with connection pool management."""

import sqlite3
from typing import List, Optional, Dict
from pathlib import Path
from contextlib import contextmanager
from queue import Queue, Empty
import threading
import time

from config import Config
from models import Agent, Task


class ConnectionPool:
    """Thread-safe SQLite connection pool with context manager support."""
    
    def __init__(self, db_path: Path, pool_size: int = 5, timeout: float = 30.0):
        """
        Initialize connection pool.
        
        Args:
            db_path: Path to SQLite database file
            pool_size: Maximum number of connections in pool
            timeout: Timeout in seconds for acquiring a connection
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self.timeout = timeout
        self._pool: Queue = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._initialized = False
        
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection with proper settings."""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=self.timeout,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrent performance
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        return conn
    
    def initialize(self):
        """Initialize the connection pool with connections."""
        if self._initialized:
            return
        
        with self._lock:
            for _ in range(self.pool_size):
                conn = self._create_connection()
                self._pool.put(conn)
            self._initialized = True
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for acquiring and releasing connections.
        
        Usage:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM agents")
        """
        if not self._initialized:
            self.initialize()
        
        try:
            conn = self._pool.get(timeout=self.timeout)
            yield conn
        except Empty:
            raise RuntimeError("Connection pool timeout - no available connections")
        finally:
            self._pool.put(conn)
    
    def close_all(self):
        """Close all connections in the pool."""
        with self._lock:
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    conn.close()
                except Empty:
                    break
            self._initialized = False


class DatabaseService:
    """Service for interacting with database using connection pool."""
    
    def __init__(self, db_path: Optional[Path] = None, pool_size: int = 5):
        """
        Initialize database service with connection pool.
        
        Args:
            db_path: Path to database file (uses config default if not provided)
            pool_size: Number of connections in the pool
        """
        self.db_path = db_path or Config.DATABASE_PATH
        self.pool_size = pool_size
        self._pool: Optional[ConnectionPool] = None
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file exists."""
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found: {self.db_path}"
            )
    
    def _get_pool(self) -> ConnectionPool:
        """Get or create connection pool."""
        if self._pool is None:
            self._pool = ConnectionPool(self.db_path, self.pool_size)
        return self._pool
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM agents")
        """
        pool = self._get_pool()
        with pool.get_connection() as conn:
            yield conn
    
    def load_all_agents(self) -> List[Agent]:
        """Load all agents from database with optimized connection usage."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Load agents
            cursor.execute("""
                SELECT id, name, pixel_character, avatar_url, role, status, 
                       current_task_id, created_at, updated_at
                FROM agents
                ORDER BY id
            """)
            agent_rows = cursor.fetchall()
            
            # Load tasks
            cursor.execute("""
                SELECT id, title, status, progress, assigned_to, created_at, updated_at
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
    
    def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """Get a specific agent by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, pixel_character, avatar_url, role, status, 
                       current_task_id, created_at, updated_at
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
                    SELECT id, title, status, progress, assigned_to, created_at, updated_at
                    FROM tasks
                    WHERE id = ?
                """, (task_id,))
                task_row = cursor.fetchone()
                if task_row:
                    task = Task.from_db(dict(task_row))
            
            return Agent.from_db(db_record, task)
    
    def update_agent_status(self, agent_id: str, new_status: str) -> bool:
        """Update agent status in database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE agents
                SET status = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (new_status, agent_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def load_all_tasks(self) -> List[Task]:
        """Load all tasks from database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, status, progress, assigned_to, created_at, updated_at
                FROM tasks
                ORDER BY updated_at DESC
            """)
            
            tasks = [Task.from_db(dict(row)) for row in cursor.fetchall()]
            return tasks
    
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
    
    def close(self):
        """Close all database connections."""
        if self._pool:
            self._pool.close_all()
            self._pool = None


# Singleton instance with lazy initialization
_db_service: Optional[DatabaseService] = None
_db_service_lock = threading.Lock()


def get_db_service() -> DatabaseService:
    """Get database service singleton (thread-safe)."""
    global _db_service
    if _db_service is None:
        with _db_service_lock:
            if _db_service is None:
                _db_service = DatabaseService()
    return _db_service


def reset_db_service():
    """Reset database service (useful for testing)."""
    global _db_service
    with _db_service_lock:
        if _db_service:
            _db_service.close()
            _db_service = None
