"""Data models for Star Office UI."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class Agent:
    """Agent data model."""
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
        """Create Agent from database record."""
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
        """Map agent state to area."""
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
        """Convert to dictionary."""
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
    """Task data model."""
    task_id: str
    title: str
    status: str = "pending"
    progress: int = 0
    assigned_to: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @classmethod
    def from_db(cls, db_record: dict) -> 'Task':
        """Create Task from database record."""
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
        """Convert to dictionary."""
        return {
            "taskId": self.task_id,
            "title": self.title,
            "status": self.status,
            "progress": self.progress,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
