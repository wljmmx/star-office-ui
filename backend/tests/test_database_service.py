"""Unit tests for database service with connection pooling."""

import unittest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database_service import DatabaseService, ConnectionPool, get_db_service, reset_db_service
from config import Config


class TestConnectionPool(unittest.TestCase):
    """Tests for ConnectionPool class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.db_path = Path(self.temp_db.name)
        
        # Initialize database with test schema
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT,
                status TEXT DEFAULT 'idle'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)
        conn.commit()
        conn.close()
        
        self.pool = ConnectionPool(self.db_path, pool_size=3)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.pool.close_all()
        self.temp_db.close()
        Path(self.temp_db.name).unlink(missing_ok=True)
        reset_db_service()
    
    def test_pool_initialization(self):
        """Test connection pool initialization."""
        self.pool.initialize()
        # Pool should have 3 connections
        self.assertEqual(self.pool._pool.qsize(), 3)
    
    def test_context_manager(self):
        """Test connection context manager."""
        with self.pool.get_connection() as conn:
            # Connection should be valid
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            self.assertIn(('agents',), tables)
            self.assertIn(('tasks',), tables)
    
    def test_concurrent_connections(self):
        """Test that pool handles concurrent connections."""
        import threading
        
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                with self.pool.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    results.append((worker_id, result))
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Create 5 threads trying to get connections
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # All workers should succeed
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 5)


class TestDatabaseService(unittest.TestCase):
    """Tests for DatabaseService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.db_path = Path(self.temp_db.name)
        
        # Initialize database with test schema and data
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        # Create tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT,
                pixel_character TEXT,
                avatar_url TEXT,
                role TEXT DEFAULT 'dev',
                status TEXT DEFAULT 'idle',
                current_task_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT,
                status TEXT DEFAULT 'pending',
                progress INTEGER DEFAULT 0,
                assigned_to TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert test data
        conn.execute("""
            INSERT INTO agents (id, name, status, current_task_id)
            VALUES ('agent-1', 'Test Agent', 'idle', 'task-1')
        """)
        conn.execute("""
            INSERT INTO tasks (id, title, status, progress)
            VALUES ('task-1', 'Test Task', 'in_progress', 50)
        """)
        
        conn.commit()
        conn.close()
        
        self.db_service = DatabaseService(self.db_path, pool_size=2)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.db_service.close()
        self.temp_db.close()
        Path(self.temp_db.name).unlink(missing_ok=True)
        reset_db_service()
    
    def test_load_all_agents(self):
        """Test loading all agents."""
        agents = self.db_service.load_all_agents()
        self.assertEqual(len(agents), 1)
        self.assertEqual(agents[0].agent_id, 'agent-1')
        self.assertEqual(agents[0].name, 'Test Agent')
        self.assertEqual(agents[0].state, 'idle')
    
    def test_get_agent_by_id(self):
        """Test getting agent by ID."""
        agent = self.db_service.get_agent_by_id('agent-1')
        self.assertIsNotNone(agent)
        self.assertEqual(agent.agent_id, 'agent-1')
        self.assertEqual(agent.name, 'Test Agent')
        
        # Test non-existent agent
        agent = self.db_service.get_agent_by_id('non-existent')
        self.assertIsNone(agent)
    
    def test_update_agent_status(self):
        """Test updating agent status."""
        success = self.db_service.update_agent_status('agent-1', 'writing')
        self.assertTrue(success)
        
        # Verify update
        agent = self.db_service.get_agent_by_id('agent-1')
        self.assertEqual(agent.state, 'writing')
        
        # Test updating non-existent agent
        success = self.db_service.update_agent_status('non-existent', 'idle')
        self.assertFalse(success)
    
    def test_load_all_tasks(self):
        """Test loading all tasks."""
        tasks = self.db_service.load_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, 'task-1')
        self.assertEqual(tasks[0].title, 'Test Task')
        self.assertEqual(tasks[0].progress, 50)
    
    def test_normalize_agent_state(self):
        """Test state normalization."""
        # Valid states should return as-is
        self.assertEqual(self.db_service.normalize_agent_state('idle'), 'idle')
        self.assertEqual(self.db_service.normalize_agent_state('writing'), 'writing')
        
        # Synonyms should be mapped
        self.assertEqual(self.db_service.normalize_agent_state('waiting'), 'idle')
        self.assertEqual(self.db_service.normalize_agent_state('coding'), 'writing')
        self.assertEqual(self.db_service.normalize_agent_state('testing'), 'executing')
        
        # Invalid states should default to idle
        self.assertEqual(self.db_service.normalize_agent_state('unknown'), 'idle')
        
        # Case insensitivity
        self.assertEqual(self.db_service.normalize_agent_state('IDLE'), 'idle')
        self.assertEqual(self.db_service.normalize_agent_state('  Writing  '), 'writing')


class TestSingleton(unittest.TestCase):
    """Tests for database service singleton pattern."""
    
    def setUp(self):
        """Set up test fixtures."""
        reset_db_service()
    
    def tearDown(self):
        """Clean up test fixtures."""
        reset_db_service()
    
    @patch('services.database_service.Config')
    def test_get_db_service_returns_same_instance(self, mock_config):
        """Test that get_db_service returns the same instance."""
        # Mock the config to avoid file not found errors
        mock_config.DATABASE_PATH = Path(__file__).parent / 'test.db'
        
        service1 = get_db_service()
        service2 = get_db_service()
        
        self.assertIs(service1, service2)
    
    def test_reset_db_service(self):
        """Test that reset_db_service clears the singleton."""
        reset_db_service()
        
        # After reset, getting service should create new instance
        from services.database_service import _db_service
        self.assertIsNone(_db_service)


if __name__ == '__main__':
    unittest.main()
