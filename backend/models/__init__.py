"""Data Models Module for Star Office UI.

This module defines the core data models used throughout the application.
It provides type-safe dataclasses for agents and tasks with conversion
methods for database operations and API serialization.

Classes:
    Agent: Represents an AI agent with state, tasks, and metadata
    Task: Represents a work task assigned to agents

Usage:
    >>> from models import Agent, Task
    >>> agent = Agent(agent_id="1", name="Alice", state="writing")
    >>> agent_dict = agent.to_dict()
    >>> db_agent = Agent.from_db(record, task)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class Agent:
    """Agent data model representing an AI agent in the system.
    
    Attributes:
        agent_id: Unique identifier for the agent
        name: Display name of the agent
        pixel_character: Optional pixel art character filename
        avatar_url: Optional URL to avatar image
        role: Agent role (default: 'dev')
        state: Current agent state (idle, writing, researching, executing, syncing, error)
        detail: Additional status detail or current task description
        area: Physical area where agent is located (breakroom, writing, error)
        task_id: ID of currently assigned task
        task_title: Title of currently assigned task
        task_progress: Progress percentage of current task (0-100)
        updated_at: ISO format timestamp of last update
    
    Example:
        >>> agent = Agent(
        ...     agent_id="agent-001",
        ...     name="CodeBot",
        ...     state="writing",
        ...     task_title="Implement feature X"
        ... )
        >>> print(agent.state)
        'writing'
    """
    agent_id: str
    name: str
    pixel_character: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = "dev"
    state: str = "idle"
    detail: str = "待命中"
    area: str = "breakroom"
    task_id: Optional[str] = None
    task_title: Optional[str] = None
    task_progress: int = 0
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @classmethod
    def from_db(cls, db_record: dict, task: Optional['Task'] = None) -> 'Agent':
        """Create Agent instance from database record.
        
        Args:
            db_record: Dictionary containing agent data from database
            task: Optional associated Task object
            
        Returns:
            Agent instance populated with database values
            
        Example:
            >>> record = {'id': '1', 'name': 'Alice', 'status': 'writing'}
            >>> agent = Agent.from_db(record)
            >>> assert agent.agent_id == '1'
        """
        agent = cls(
            agent_id=db_record.get('id', ''),
            name=db_record.get('name', 'Unknown'),
            pixel_character=db_record.get('pixel_character'),
            avatar_url=db_record.get('avatar_url'),
            role=db_record.get('role', 'dev'),
            state=db_record.get('status', 'idle'),
            area=cls.map_state_to_area(db_record.get('status', 'idle')),
            task_id=db_record.get('current_task_id'),
            updated_at=db_record.get('updated_at', datetime.now().isoformat())
        )
        
        # Add task info if available
        if task:
            agent.task_title = task.title
            agent.task_progress = task.progress
            agent.detail = task.title
        
        return agent
    
    @staticmethod
    def map_state_to_area(state: str) -> str:
        """Map agent state to physical area location.
        
        Maps agent work states to their corresponding physical areas
        in the office layout for visualization purposes.
        
        Args:
            state: Current agent state string
            
        Returns:
            Area name where agent should be displayed
            
        Mapping:
            - 'idle' -> 'breakroom'
            - 'writing', 'researching', 'executing', 'syncing' -> 'writing'
            - 'error' -> 'error'
            - Unknown states -> 'breakroom'
        """
        mapping = {
            "idle": "breakroom",
            "writing": "writing",
            "researching": "writing",
            "executing": "writing",
            "syncing": "writing",
            "error": "error",
        }
        return mapping.get(state, "breakroom")
    
    def to_dict(self) -> dict:
        """Convert Agent instance to dictionary for API serialization.
        
        Returns:
            Dictionary with camelCase keys for frontend compatibility
            
        Example:
            >>> agent = Agent(agent_id="1", name="Test")
            >>> d = agent.to_dict()
            >>> assert d['agentId'] == '1'
        """
        return {
            "agentId": self.agent_id,
            "name": self.name,
            "pixel_character": self.pixel_character,
            "avatar_url": self.avatar_url,
            "role": self.role,
            "state": self.state,
            "detail": self.detail,
            "area": self.area,
            "task_id": self.task_id,
            "task_title": self.task_title,
            "task_progress": self.task_progress,
            "updated_at": self.updated_at,
        }

@dataclass
class Task:
    """Task data model representing a work task.
    
    Attributes:
        task_id: Unique identifier for the task
        title: Task title/description
        status: Current task status (pending, in_progress, completed)
        progress: Completion percentage (0-100)
        assigned_to: ID of agent assigned to this task
        created_at: ISO format timestamp when task was created
        updated_at: ISO format timestamp of last update
    
    Example:
        >>> task = Task(
        ...     task_id="task-001",
        ...     title="Implement login feature",
        ...     status="in_progress",
        ...     progress=50
        ... )
    """
    task_id: str
    title: str
    status: str = "pending"
    progress: int = 0
    assigned_to: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @classmethod
    def from_db(cls, db_record: dict) -> 'Task':
        """Create Task instance from database record.
        
        Args:
            db_record: Dictionary containing task data from database
            
        Returns:
            Task instance populated with database values
        """
        return cls(
            task_id=db_record.get('id', ''),
            title=db_record.get('title', 'Unknown Task'),
            status=db_record.get('status', 'pending'),
            progress=db_record.get('progress', 0),
            assigned_to=db_record.get('assigned_to'),
            created_at=db_record.get('created_at', datetime.now().isoformat()),
            updated_at=db_record.get('updated_at', datetime.now().isoformat()),
        )
    
    def to_dict(self) -> dict:
        """Convert Task instance to dictionary for API serialization.
        
        Returns:
            Dictionary with camelCase keys for frontend compatibility
        """
        return {
            "taskId": self.task_id,
            "title": self.title,
            "status": self.status,
            "progress": self.progress,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
