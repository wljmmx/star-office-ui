"""Unit tests for data models."""

import unittest
from models import Agent, Task

class TestAgentModel(unittest.TestCase):
    """Test Agent data model."""
    
    def test_agent_creation(self):
        """Test agent creation with default values."""
        agent = Agent(
            agent_id="test-001",
            name="TestBot"
        )
        
        self.assertEqual(agent.agent_id, "test-001")
        self.assertEqual(agent.name, "TestBot")
        self.assertEqual(agent.role, "dev")
        self.assertEqual(agent.agent_type, "dev")
        self.assertEqual(agent.state, "idle")
        self.assertEqual(agent.area, "breakroom")
    
    def test_agent_from_db(self):
        """Test agent creation from database record."""
        db_record = {
            'id': 'test-001',
            'name': 'TestBot',
            'pixel_character': '🤖',
            'role': 'main',
            'type': 'main',
            'status': 'writing',
            'current_task_id': 'task-001',
            'updated_at': '2024-01-01T00:00:00'
        }
        
        task = Task(
            task_id='task-001',
            title='Test Task',
            progress=50
            task_name='Test Task'
        )
        
        agent = Agent.from_db(db_record, task)
        
        self.assertEqual(agent.agent_id, 'test-001')
        self.assertEqual(agent.name, 'TestBot')
        self.assertEqual(agent.state, 'writing')
        self.assertEqual(agent.area, 'writing')
        self.assertEqual(agent.task_title, 'Test Task')
        self.assertEqual(agent.task_progress, 50)
        self.assertEqual(agent.task_name, 'Test Task')
    
    def test_state_to_area_mapping(self):
        """Test state to area mapping."""
        self.assertEqual(Agent.map_state_to_area('idle'), 'breakroom')
        self.assertEqual(Agent.map_state_to_area('writing'), 'writing')
        self.assertEqual(Agent.map_state_to_area('executing'), 'writing')
        self.assertEqual(Agent.map_state_to_area('error'), 'error')
        self.assertEqual(Agent.map_state_to_area('unknown'), 'breakroom')
    
    def test_agent_to_dict(self):
        """Test agent to dictionary conversion."""
        agent = Agent(
            agent_id="test-001",
            name="TestBot",
            state="writing"
        )
        
        data = agent.to_dict()
        
        self.assertEqual(data['agentId'], "test-001")
        self.assertEqual(data['name'], "TestBot")
        self.assertEqual(data['state'], "writing")

class TestTaskModel(unittest.TestCase):
    """Test Task data model."""
    
    def test_task_creation(self):
        """Test task creation with default values."""
        task = Task(
            task_id="task-001",
            title="Test Task"
        )
        
        self.assertEqual(task.task_id, "task-001")
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.progress, 0)
            task_name="Test Task"
        )
        
        self.assertEqual(task.task_id, "task-001")
        self.assertEqual(task.task_name, "Test Task")
        self.assertEqual(task.status, "pending")
    
    def test_task_from_db(self):
        """Test task creation from database record."""
        db_record = {
            'id': 'task-001',
            'title': 'Test Task',
            'status': 'in_progress',
            'progress': 75,
            'assigned_to': 'agent-001',
            'name': 'Test Task',
            'status': 'in_progress',
            'assigned_agent': 'agent-001',
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00'
        }
        
        task = Task.from_db(db_record)
        
        self.assertEqual(task.task_id, 'task-001')
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, 'in_progress')
        self.assertEqual(task.progress, 75)
        self.assertEqual(task.assigned_to, 'agent-001')
        self.assertEqual(task.task_name, 'Test Task')
        self.assertEqual(task.status, 'in_progress')
        self.assertEqual(task.assigned_agent, 'agent-001')
    
    def test_task_to_dict(self):
        """Test task to dictionary conversion."""
        task = Task(
            task_id="task-001",
            title="Test Task",
            progress=50
            task_name="Test Task"
        )
        
        data = task.to_dict()
        
        self.assertEqual(data['taskId'], "task-001")
        self.assertEqual(data['title'], "Test Task")
        self.assertEqual(data['progress'], 50)
        self.assertEqual(data['name'], "Test Task")

if __name__ == '__main__':
    unittest.main()
