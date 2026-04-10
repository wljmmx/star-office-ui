"""Data models for Star Office UI."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class Agent:
    """Agent data model."""
    agent_id: str
    name: str
    agent_type: str = "dev"
    state: str = "idle"
    detail: str = "待命中"
    area: str = "breakroom"
    capabilities: str = ""
    address: str = ""
    task_id: Optional[str] = None
    task_name: Optional[str] = None
    task_status: str = "pending"
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @classmethod
    def from_db(cls, db_record: dict, task: Optional['Task'] = None) -> 'Agent':
        """Create Agent from database record."""
        status = db_record.get('status', 'idle')
        agent = cls(
            agent_id=str(db_record.get('id', '')),
            name=db_record.get('name', 'Unknown'),
            agent_type=db_record.get('type', 'dev'),
            state=cls.normalize_state(status),
            area=cls.map_state_to_area(cls.normalize_state(status)),
            capabilities=db_record.get('capabilities', ''),
            address=db_record.get('address', ''),
            task_id=db_record.get('current_task_id'),
            updated_at=db_record.get('last_heartbeat', datetime.now().isoformat())
        )
        
        # Add task info if available
        if task:
            agent.task_name = task.task_name
            agent.task_status = task.status
            agent.detail = f"正在处理：{task.task_name}"
        else:
            agent.detail = cls.get_state_message(agent.state)
        
        return agent
    
    @staticmethod
    def normalize_state(status: str) -> str:
        """Normalize status to state."""
        if not status:
            return "idle"
        status_lower = status.lower().strip()
        if status_lower in {"idle", "writing", "researching", "executing", "syncing", "error"}:
            return status_lower
        mapping = {
            "active": "writing",
            "working": "writing",
            "busy": "writing",
            "pending": "idle",
            "completed": "idle",
            "failed": "error",
        }
        return mapping.get(status_lower, "idle")
    
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
    
    @staticmethod
    def get_state_message(state: str) -> str:
        """Get message for state."""
        messages = {
            "idle": "待命中，随时准备为你服务",
            "writing": "正在编写代码...",
            "researching": "正在调研方案...",
            "executing": "正在执行任务...",
            "syncing": "正在同步数据...",
            "error": "遇到错误，需要协助",
        }
        return messages.get(state, "工作中...")
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "agentId": self.agent_id,
            "name": self.name,
            "type": self.agent_type,
            "state": self.state,
            "detail": self.detail,
            "area": self.area,
            "capabilities": self.capabilities,
            "address": self.address,
            "task_id": self.task_id,
            "task_name": self.task_name,
            "task_status": self.task_status,
            "updated_at": self.updated_at,
            "isMain": self.agent_type == "manager",
            "pixel_character": None,
            "avatar_url": None,
            "role": self.agent_type,
        }

@dataclass
class Task:
    """Task data model."""
    task_id: str
    task_name: str
    description: str = ""
    status: str = "pending"
    project_id: Optional[str] = None
    assigned_agent: Optional[str] = None
    priority: int = 5
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    
    @classmethod
    def from_db(cls, db_record: dict) -> 'Task':
        """Create Task from database record."""
        return cls(
            task_id=str(db_record.get('id', '')),
            task_name=db_record.get('name', 'Unknown Task'),
            description=db_record.get('description', ''),
            status=db_record.get('status', 'pending'),
            project_id=str(db_record.get('project_id', '')) if db_record.get('project_id') else None,
            assigned_agent=db_record.get('assigned_agent'),
            priority=db_record.get('priority', 5),
            created_at=db_record.get('created_at', datetime.now().isoformat()),
            updated_at=db_record.get('updated_at', datetime.now().isoformat()),
            completed_at=db_record.get('completed_at'),
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "taskId": self.task_id,
            "name": self.task_name,
            "description": self.description,
            "status": self.status,
            "project_id": self.project_id,
            "assigned_agent": self.assigned_agent,
            "priority": self.priority,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
        }
