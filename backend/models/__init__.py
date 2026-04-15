"""Data models for Star Office UI."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class Project:
    """Project data model."""
    project_id: int
    name: str
    github_url: str
    description: Optional[str] = None
    status: str = "active"
    work_dir: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @classmethod
    def from_db(cls, db_record: dict) -> 'Project':
        """Create Project from database record."""
        return cls(
            project_id=db_record.get('id', 0),
            name=db_record.get('name', 'Unknown Project'),
            github_url=db_record.get('github_url', ''),
            description=db_record.get('description'),
            status=db_record.get('status', 'active'),
            work_dir=db_record.get('work_dir'),
            created_at=db_record.get('created_at', datetime.now().isoformat()),
            updated_at=db_record.get('updated_at', datetime.now().isoformat()),
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "projectId": self.project_id,
            "name": self.name,
            "githubUrl": self.github_url,
            "description": self.description,
            "status": self.status,
            "workDir": self.work_dir,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }

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
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    project_url: Optional[str] = None
    parent_agent_id: Optional[str] = None
    subagents: List[str] = field(default_factory=list)
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @classmethod
    def from_db(cls, db_record: dict, task: Optional['Task'] = None, project: Optional['Project'] = None) -> 'Agent':
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
            # Add project info from task if available
            if project:
                agent.project_id = project.project_id
                agent.project_name = project.name
                agent.project_url = project.github_url
        
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
            "project_id": self.project_id,
            "project_name": self.project_name,
            "project_url": self.project_url,
            "parent_agent_id": self.parent_agent_id,
            "subagents": self.subagents,
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
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    project_url: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @classmethod
    def from_db(cls, db_record: dict, project: Optional['Project'] = None) -> 'Task':
        """Create Task from database record."""
        task = cls(
            task_id=db_record.get('id', ''),
            title=db_record.get('title', 'Unknown Task'),
            status=db_record.get('status', 'pending'),
            progress=db_record.get('progress', 0),
            assigned_to=db_record.get('assigned_to'),
            created_at=db_record.get('created_at', datetime.now().isoformat()),
            updated_at=db_record.get('updated_at', datetime.now().isoformat()),
        )
        
        # Add project info if available
        if project:
            task.project_id = project.project_id
            task.project_name = project.name
            task.project_url = project.github_url
        
        return task
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "taskId": self.task_id,
            "title": self.title,
            "status": self.status,
            "progress": self.progress,
            "assigned_to": self.assigned_to,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "project_url": self.project_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
