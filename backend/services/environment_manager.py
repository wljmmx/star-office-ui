"""Environment management service for office environments."""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

@dataclass
class Environment:
    """Office environment data model."""
    id: str
    name: str
    description: str = ""
    theme: str = "default"
    background_image: Optional[str] = None
    layout_config: Optional[str] = None  # JSON
    settings: Optional[str] = None  # JSON
    is_active: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "theme": self.theme,
            "background_image": self.background_image,
            "layout_config": json.loads(self.layout_config) if self.layout_config else None,
            "settings": json.loads(self.settings) if self.settings else None,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Environment':
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            theme=data.get("theme", "default"),
            background_image=data.get("background_image"),
            layout_config=data.get("layout_config"),
            settings=data.get("settings"),
            is_active=bool(data.get("is_active", False)),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )
    
    @classmethod
    def from_db(cls, db_record: dict) -> 'Environment':
        """Create from database record."""
        return cls(
            id=str(db_record.get("id", "")),
            name=db_record.get("name", ""),
            description=db_record.get("description", ""),
            theme=db_record.get("theme", "default"),
            background_image=db_record.get("background_image"),
            layout_config=db_record.get("layout_config"),
            settings=db_record.get("settings"),
            is_active=bool(db_record.get("is_active", 0)),
            created_at=db_record.get("created_at", datetime.now().isoformat()),
            updated_at=db_record.get("updated_at", datetime.now().isoformat()),
        )


@dataclass
class AgentDesk:
    """Agent desk assignment data model."""
    id: str
    agent_id: str
    desk_number: int
    position_x: float = 0.0
    position_y: float = 0.0
    assigned_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "desk_number": self.desk_number,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "assigned_at": self.assigned_at,
        }
    
    @classmethod
    def from_db(cls, db_record: dict) -> 'AgentDesk':
        """Create from database record."""
        return cls(
            id=str(db_record.get("id", "")),
            agent_id=db_record.get("agent_id", ""),
            desk_number=db_record.get("desk_number", 0),
            position_x=float(db_record.get("position_x", 0.0)),
            position_y=float(db_record.get("position_y", 0.0)),
            assigned_at=db_record.get("assigned_at", datetime.now().isoformat()),
        )


class EnvironmentManager:
    """Manager for office environment operations."""
    
    # Default environment configuration
    DEFAULT_ENVIRONMENT = {
        "id": "default",
        "name": "Default Office",
        "description": "Standard office environment",
        "theme": "default",
        "background_image": None,
        "layout_config": json.dumps({
            "areas": {
                "breakroom": {"x": 0, "y": 0, "width": 300, "height": 200},
                "writing": {"x": 300, "y": 0, "width": 500, "height": 400},
                "error": {"x": 800, "y": 0, "width": 200, "height": 200},
            }
        }),
        "settings": json.dumps({
            "show_grid": True,
            "grid_size": 50,
            "animation_speed": 1.0,
        }),
        "is_active": True,
    }
    
    # Predefined themes
    THEMES = {
        "default": {
            "primary_color": "#3b82f6",
            "secondary_color": "#10b981",
            "background_color": "#f3f4f6",
            "text_color": "#1f2937",
        },
        "dark": {
            "primary_color": "#60a5fa",
            "secondary_color": "#34d399",
            "background_color": "#1f2937",
            "text_color": "#f9fafb",
        },
        "cyberpunk": {
            "primary_color": "#f472b6",
            "secondary_color": "#22d3ee",
            "background_color": "#0f172a",
            "text_color": "#e2e8f0",
        },
    }
    
    @classmethod
    def get_default_environment(cls) -> Environment:
        """Get default environment."""
        return Environment.from_dict(cls.DEFAULT_ENVIRONMENT)
    
    @classmethod
    def get_theme(cls, theme_name: str) -> dict:
        """Get theme configuration."""
        return cls.THEMES.get(theme_name, cls.THEMES["default"])
    
    @classmethod
    def validate_environment(cls, env: Environment) -> bool:
        """Validate environment configuration."""
        if not env.id or not env.name:
            return False
        
        if env.theme and env.theme not in cls.THEMES:
            # Custom theme is allowed
            pass
        
        return True


class DeskManager:
    """Manager for desk assignments."""
    
    # Default desk layout
    DEFAULT_DESK_COUNT = 10
    
    @classmethod
    def generate_desk_id(cls, agent_id: str) -> str:
        """Generate desk ID from agent ID."""
        return f"desk_{agent_id}"
    
    @classmethod
    def calculate_position(cls, desk_number: int, cols: int = 5) -> tuple:
        """Calculate x, y position from desk number."""
        col = (desk_number - 1) % cols
        row = (desk_number - 1) // cols
        return col * 100, row * 100
    
    @classmethod
    def create_desk_assignment(
        cls, 
        agent_id: str, 
        desk_number: int
    ) -> AgentDesk:
        """Create a new desk assignment."""
        x, y = cls.calculate_position(desk_number)
        return AgentDesk(
            id=cls.generate_desk_id(agent_id),
            agent_id=agent_id,
            desk_number=desk_number,
            position_x=x,
            position_y=y,
        )
