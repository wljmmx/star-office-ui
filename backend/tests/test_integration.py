"""Integration tests for Star Office UI systems."""

import unittest
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "github-collab" / "github-collab.db"

# Import modules
import sys
sys.path.insert(0, str(BASE_DIR))

from models import Agent, Task
from utils.avatar_manager import AvatarManager, AvatarConfig
from services.environment_manager import EnvironmentManager, Environment, DeskManager
from services.task_manager import TaskManager, TaskList, ExtendedTask


class TestAvatarSystem(unittest.TestCase):
    """Test Avatar System Integration."""
    
    def test_create_avatar_config(self):
        """Test creating avatar configuration."""
        avatar = AvatarConfig(
            avatar_type="pixel",
            pixel_character="🤖"
        )
        
        self.assertEqual(avatar.avatar_type, "pixel")
        self.assertEqual(avatar.pixel_character, "🤖")
    
    def test_avatar_to_dict(self):
        """Test avatar serialization."""
        avatar = AvatarConfig(
            avatar_type="emoji",
            avatar_data="👨‍💻"
        )
        
        data = avatar.to_dict()
        self.assertEqual(data["avatar_type"], "emoji")
        self.assertEqual(data["pixel_character"], None)
    
    def test_get_default_avatar(self):
        """Test getting default avatar by type."""
        avatar = AvatarManager.get_default_avatar("dev")
        
        self.assertIsNotNone(avatar)
        self.assertEqual(avatar.avatar_type, "pixel")
    
    def test_generate_pixel_avatar(self):
        """Test generating pixel avatar from name."""
        char1 = AvatarManager.generate_pixel_avatar("Agent1")
        char2 = AvatarManager.generate_pixel_avatar("Agent2")
        
        self.assertIn(char1, ["🤖", "👨‍💻", "👩‍💻", "👨‍🔬", "👩‍🔬", "👨‍🎓", "👩‍🎓"])
        # Same name should generate same character
        self.assertEqual(char1, AvatarManager.generate_pixel_avatar("Agent1"))
    
    def test_validate_avatar_data(self):
        """Test avatar data validation."""
        # Valid empty data
        self.assertTrue(AvatarManager.validate_avatar_data("pixel", ""))
        
        # Valid JSON data
        json_data = json.dumps({"color": "blue"})
        self.assertTrue(AvatarManager.validate_avatar_data("json", json_data))
        
        # Invalid JSON data
        self.assertFalse(AvatarManager.validate_avatar_data("json", "invalid json"))


class TestEnvironmentSystem(unittest.TestCase):
    """Test Environment System Integration."""
    
    def test_create_environment(self):
        """Test creating environment."""
        env = Environment(
            id="test_env",
            name="Test Environment",
            description="Test description",
            theme="dark",
            is_active=True
        )
        
        self.assertEqual(env.id, "test_env")
        self.assertEqual(env.theme, "dark")
        self.assertTrue(env.is_active)
    
    def test_environment_to_dict(self):
        """Test environment serialization."""
        env = Environment(
            id="test",
            name="Test",
            settings=json.dumps({"grid": True})
        )
        
        data = env.to_dict()
        self.assertEqual(data["id"], "test")
        self.assertIsInstance(data["settings"], dict)
        self.assertTrue(data["settings"]["grid"])
    
    def test_get_default_environment(self):
        """Test getting default environment."""
        env = EnvironmentManager.get_default_environment()
        
        self.assertEqual(env.id, "default")
        self.assertTrue(env.is_active)
    
    def test_get_theme(self):
        """Test getting theme configuration."""
        theme = EnvironmentManager.get_theme("dark")
        
        self.assertIn("primary_color", theme)
        self.assertIn("background_color", theme)
    
    def test_validate_environment(self):
        """Test environment validation."""
        # Valid environment
        valid_env = Environment(id="test", name="Test", is_active=False)
        self.assertTrue(EnvironmentManager.validate_environment(valid_env))
        
        # Invalid environment (no name)
        invalid_env = Environment(id="test", name="", is_active=False)
        self.assertFalse(EnvironmentManager.validate_environment(invalid_env))


class TestDeskSystem(unittest.TestCase):
    """Test Desk Assignment System."""
    
    def test_generate_desk_id(self):
        """Test desk ID generation."""
        desk_id = DeskManager.generate_desk_id("agent123")
        
        self.assertEqual(desk_id, "desk_agent123")
    
    def test_calculate_position(self):
        """Test desk position calculation."""
        x, y = DeskManager.calculate_position(1, cols=5)
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)
        
        x, y = DeskManager.calculate_position(6, cols=5)
        self.assertEqual(x, 0)
        self.assertEqual(y, 100)
    
    def test_create_desk_assignment(self):
        """Test creating desk assignment."""
        desk = DeskManager.create_desk_assignment("agent1", 5)
        
        self.assertEqual(desk.agent_id, "agent1")
        self.assertEqual(desk.desk_number, 5)
        self.assertIsNotNone(desk.position_x)
        self.assertIsNotNone(desk.position_y)


class TestTaskListSystem(unittest.TestCase):
    """Test Task List System Integration."""
    
    def test_create_task(self):
        """Test creating extended task."""
        task = TaskManager.create_task(
            name="Test Task",
            description="Test description",
            status="pending"
        )
        
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.list_id, "backlog")  # Auto-mapped
    
    def test_task_checklist(self):
        """Test task checklist functionality."""
        task = TaskManager.create_task("Test Task")
        
        # Add checklist item
        item = task.add_checklist_item("Step 1")
        self.assertEqual(item.title, "Step 1")
        self.assertFalse(item.completed)
        
        # Complete item
        result = task.complete_checklist_item(item.id)
        self.assertTrue(result)
        self.assertTrue(item.completed)
        self.assertIsNotNone(item.completed_at)
    
    def test_checklist_progress(self):
        """Test checklist progress calculation."""
        task = TaskManager.create_task("Test Task")
        
        task.add_checklist_item("Step 1")
        task.add_checklist_item("Step 2")
        task.complete_checklist_item(task.checklist[0].id)
        
        progress = task.get_checklist_progress()
        self.assertEqual(progress["total"], 2)
        self.assertEqual(progress["completed"], 1)
        self.assertEqual(progress["percentage"], 50.0)
    
    def test_move_task_to_list(self):
        """Test moving task between lists."""
        task = TaskManager.create_task("Test Task", status="pending")
        self.assertEqual(task.list_id, "backlog")
        
        TaskManager.move_task_to_list(task, "in_progress")
        self.assertEqual(task.list_id, "in_progress")
        self.assertEqual(task.status, "in_progress")
    
    def test_sort_tasks_by_position(self):
        """Test sorting tasks by position."""
        task1 = TaskManager.create_task("Task 1")
        task1.position = 2
        
        task2 = TaskManager.create_task("Task 2")
        task2.position = 1
        
        tasks = [task1, task2]
        sorted_tasks = TaskManager.sort_tasks_by_position(tasks)
        
        self.assertEqual(sorted_tasks[0].task_id, task2.task_id)
        self.assertEqual(sorted_tasks[1].task_id, task1.task_id)


class TestDatabaseIntegration(unittest.TestCase):
    """Test Database Integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db_path = DB_PATH
        if not self.db_path.exists():
            self.skipTest("Database not found")
    
    def test_agents_table_has_avatar_columns(self):
        """Test that agents table has avatar columns."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(agents)")
        columns = [row[1] for row in cursor.fetchall()]
        
        conn.close()
        
        self.assertIn("avatar_type", columns)
        self.assertIn("avatar_data", columns)
    
    def test_tasks_table_has_list_columns(self):
        """Test that tasks table has list management columns."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [row[1] for row in cursor.fetchall()]
        
        conn.close()
        
        self.assertIn("list_id", columns)
        self.assertIn("position", columns)
        self.assertIn("checklist", columns)
    
    def test_environments_table_exists(self):
        """Test that environments table exists."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='environments'")
        result = cursor.fetchone()
        
        conn.close()
        
        self.assertIsNotNone(result)
    
    def test_agent_desks_table_exists(self):
        """Test that agent_desks table exists."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agent_desks'")
        result = cursor.fetchone()
        
        conn.close()
        
        self.assertIsNotNone(result)
    
    def test_default_environment_exists(self):
        """Test that default environment was inserted."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM environments WHERE id='default'")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        self.assertGreater(count, 0)


class TestModelIntegration(unittest.TestCase):
    """Test Model Integration with New Fields."""
    
    def test_agent_model_has_avatar_fields(self):
        """Test that Agent model includes avatar fields."""
        agent = Agent(
            agent_id="test",
            name="Test Agent",
            avatar_type="pixel",
            pixel_character="🤖",
            desk_number=5
        )
        
        data = agent.to_dict()
        
        self.assertIn("avatar_type", data)
        self.assertIn("pixel_character", data)
        self.assertIn("desk_number", data)
        self.assertEqual(data["avatar_type"], "pixel")
        self.assertEqual(data["desk_number"], 5)
    
    def test_task_model_has_list_fields(self):
        """Test that Task model includes list management fields."""
        task = Task(
            task_id="test",
            task_name="Test Task",
            list_id="backlog",
            position=1,
            checklist=json.dumps([{"id": "1", "title": "Step 1", "completed": False}])
        )
        
        data = task.to_dict()
        
        self.assertIn("list_id", data)
        self.assertIn("position", data)
        self.assertIn("checklist", data)
        self.assertEqual(data["list_id"], "backlog")
        self.assertEqual(data["position"], 1)
        self.assertIsInstance(data["checklist"], list)


def run_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("Star Office UI - Integration Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAvatarSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvironmentSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestDeskSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskListSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestModelIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
