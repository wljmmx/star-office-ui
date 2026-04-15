"""Task management service for independent task list system."""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass
class TaskChecklistItem:
    """Task checklist item."""
    id: str
    title: str
    completed: bool = False
    completed_at: Optional[str] = None
    order: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "completed_at": self.completed_at,
            "order": self.order,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TaskChecklistItem':
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid4())),
            title=data.get("title", ""),
            completed=data.get("completed", False),
            completed_at=data.get("completed_at"),
            order=data.get("order", 0),
        )


@dataclass
class TaskList:
    """Task list data model."""
    id: str
    name: str
    description: str = ""
    color: str = "#3b82f6"
    icon: str = "📋"
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "icon": self.icon,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TaskList':
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            color=data.get("color", "#3b82f6"),
            icon=data.get("icon", "📋"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )


class ExtendedTask:
    """Extended task model with list management."""
    
    def __init__(
        self,
        task_id: str,
        name: str,
        description: str = "",
        status: str = "pending",
        list_id: Optional[str] = None,
        position: int = 0,
        checklist: Optional[List[TaskChecklistItem]] = None,
        **kwargs
    ):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.status = status
        self.list_id = list_id
        self.position = position
        self.checklist = checklist or []
        self.extra = kwargs
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "taskId": self.task_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "list_id": self.list_id,
            "position": self.position,
            "checklist": [item.to_dict() for item in self.checklist],
            "checklist_progress": self.get_checklist_progress(),
            **{k: v for k, v in self.extra.items() if v is not None}
        }
    
    def get_checklist_progress(self) -> dict:
        """Get checklist progress."""
        total = len(self.checklist)
        completed = sum(1 for item in self.checklist if item.completed)
        return {
            "total": total,
            "completed": completed,
            "percentage": (completed / total * 100) if total > 0 else 0,
        }
    
    def add_checklist_item(self, title: str) -> TaskChecklistItem:
        """Add a checklist item."""
        item = TaskChecklistItem(
            id=str(uuid4()),
            title=title,
            order=len(self.checklist),
        )
        self.checklist.append(item)
        return item
    
    def complete_checklist_item(self, item_id: str) -> bool:
        """Mark a checklist item as completed."""
        for item in self.checklist:
            if item.id == item_id:
                item.completed = True
                item.completed_at = datetime.now().isoformat()
                return True
        return False
    
    def update_position(self, new_position: int) -> None:
        """Update task position in list."""
        self.position = new_position


class TaskManager:
    """Manager for task operations."""
    
    # Default task lists
    DEFAULT_LISTS = [
        {
            "id": "backlog",
            "name": "待办事项",
            "description": "所有待处理的任务",
            "color": "#6b7280",
            "icon": "📋",
        },
        {
            "id": "in_progress",
            "name": "进行中",
            "description": "当前正在处理的任务",
            "color": "#3b82f6",
            "icon": "🔄",
        },
        {
            "id": "review",
            "name": "待审核",
            "description": "等待审核的任务",
            "color": "#f59e0b",
            "icon": "🔍",
        },
        {
            "id": "done",
            "name": "已完成",
            "description": "已完成的任务",
            "color": "#10b981",
            "icon": "✅",
        },
    ]
    
    # Status to list mapping
    STATUS_TO_LIST = {
        "pending": "backlog",
        "todo": "backlog",
        "in_progress": "in_progress",
        "progress": "in_progress",
        "review": "review",
        "reviewing": "review",
        "done": "done",
        "completed": "done",
        "closed": "done",
    }
    
    @classmethod
    def get_default_lists(cls) -> List[TaskList]:
        """Get default task lists."""
        return [TaskList.from_dict(lst) for lst in cls.DEFAULT_LISTS]
    
    @classmethod
    def map_status_to_list(cls, status: str) -> str:
        """Map task status to list ID."""
        return cls.STATUS_TO_LIST.get(status.lower(), "backlog")
    
    @classmethod
    def create_task(
        cls,
        task_id: Optional[str] = None,
        name: str = "",
        description: str = "",
        status: str = "pending",
        list_id: Optional[str] = None,
        checklist: Optional[List[dict]] = None,
    ) -> ExtendedTask:
        """Create a new task."""
        if not task_id:
            task_id = str(uuid4())
        
        if not list_id:
            list_id = cls.map_status_to_list(status)
        
        task_checklist = [
            TaskChecklistItem.from_dict(item) for item in (checklist or [])
        ]
        
        return ExtendedTask(
            task_id=task_id,
            name=name,
            description=description,
            status=status,
            list_id=list_id,
            checklist=task_checklist,
        )
    
    @classmethod
    def move_task_to_list(cls, task: ExtendedTask, target_list_id: str) -> None:
        """Move task to a different list."""
        task.list_id = target_list_id
        # Auto-update status based on list
        for status, list_id in cls.STATUS_TO_LIST.items():
            if list_id == target_list_id:
                if status in ["pending", "todo"]:
                    task.status = "pending"
                elif status in ["in_progress", "progress"]:
                    task.status = "in_progress"
                elif status in ["review", "reviewing"]:
                    task.status = "review"
                elif status in ["done", "completed", "closed"]:
                    task.status = "done"
                break
    
    @classmethod
    def sort_tasks_by_position(cls, tasks: List[ExtendedTask]) -> List[ExtendedTask]:
        """Sort tasks by position within their lists."""
        return sorted(tasks, key=lambda t: (t.list_id, t.position))


class TaskListService:
    """Service for task list operations."""
    
    def __init__(self):
        """Initialize task list service."""
        self.lists = {lst["id"]: TaskList.from_dict(lst) for lst in TaskManager.DEFAULT_LISTS}
        self.tasks: Dict[str, ExtendedTask] = {}
    
    def get_all_lists(self) -> List[TaskList]:
        """Get all task lists."""
        return list(self.lists.values())
    
    def get_list(self, list_id: str) -> Optional[TaskList]:
        """Get a specific task list."""
        return self.lists.get(list_id)
    
    def get_tasks_by_list(self, list_id: str) -> List[ExtendedTask]:
        """Get all tasks in a list."""
        return TaskManager.sort_tasks_by_position([
            task for task in self.tasks.values() 
            if task.list_id == list_id
        ])
    
    def add_task(self, task: ExtendedTask) -> None:
        """Add a task."""
        self.tasks[task.task_id] = task
    
    def update_task(self, task: ExtendedTask) -> None:
        """Update a task."""
        if task.task_id in self.tasks:
            self.tasks[task.task_id] = task
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
    
    def move_task(self, task_id: str, target_list_id: str, new_position: int = 0) -> bool:
        """Move a task to a different list."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        TaskManager.move_task_to_list(task, target_list_id)
        task.update_position(new_position)
        return True
