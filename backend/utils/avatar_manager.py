"""Avatar management utilities for Agent appearance system."""

import json
from typing import Dict, Optional, Any
from dataclasses import dataclass, field, asdict

@dataclass
class AvatarConfig:
    """Avatar configuration data class."""
    avatar_type: str = "pixel"  # pixel, emoji, image, 3d
    avatar_data: Optional[str] = None  # JSON string with avatar details
    pixel_character: Optional[str] = None  # Pixel art character
    avatar_url: Optional[str] = None  # URL for image avatars
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "avatar_type": self.avatar_type,
            "avatar_data": self.avatar_data,
            "pixel_character": self.pixel_character,
            "avatar_url": self.avatar_url,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AvatarConfig':
        """Create from dictionary."""
        return cls(
            avatar_type=data.get("avatar_type", "pixel"),
            avatar_data=data.get("avatar_data"),
            pixel_character=data.get("pixel_character"),
            avatar_url=data.get("avatar_url"),
        )
    
    def get_display_data(self) -> dict:
        """Get display-ready avatar data."""
        result = {
            "type": self.avatar_type,
            "data": None,
        }
        
        if self.avatar_type == "pixel":
            result["data"] = self.pixel_character
        elif self.avatar_type == "image":
            result["data"] = self.avatar_url
        elif self.avatar_type == "emoji":
            result["data"] = self.avatar_data
        elif self.avatar_type == "3d":
            result["data"] = json.loads(self.avatar_data) if self.avatar_data else None
        
        return result


class AvatarManager:
    """Manager for avatar operations."""
    
    # Default avatars by agent type
    DEFAULT_AVATARS = {
        "manager": {
            "avatar_type": "pixel",
            "pixel_character": "👨‍💼",
        },
        "dev": {
            "avatar_type": "pixel",
            "pixel_character": "👨‍💻",
        },
        "tester": {
            "avatar_type": "pixel",
            "pixel_character": "🧪",
        },
        "default": {
            "avatar_type": "pixel",
            "pixel_character": "🤖",
        },
    }
    
    @classmethod
    def get_default_avatar(cls, agent_type: str = "default") -> AvatarConfig:
        """Get default avatar for agent type."""
        avatar_data = cls.DEFAULT_AVATARS.get(agent_type, cls.DEFAULT_AVATARS["default"])
        return AvatarConfig(
            avatar_type=avatar_data.get("avatar_type", "pixel"),
            pixel_character=avatar_data.get("pixel_character"),
        )
    
    @classmethod
    def generate_pixel_avatar(cls, name: str, seed: Optional[int] = None) -> str:
        """Generate a simple pixel avatar based on name."""
        # Simple hash-based character selection
        import hashlib
        hash_input = f"{name}-{seed}" if seed else name
        hash_val = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        
        # Character options
        characters = ["🤖", "👨‍💻", "👩‍💻", "👨‍🔬", "👩‍🔬", "👨‍🎓", "👩‍🎓"]
        return characters[hash_val % len(characters)]
    
    @classmethod
    def validate_avatar_data(cls, avatar_type: str, avatar_data: str) -> bool:
        """Validate avatar data based on type."""
        if not avatar_data:
            return True  # Empty data is valid
        
        if avatar_type == "json":
            try:
                json.loads(avatar_data)
                return True
            except json.JSONDecodeError:
                return False
        
        return True
    
    @classmethod
    def merge_avatar_with_agent(cls, agent_dict: dict, avatar_config: AvatarConfig) -> dict:
        """Merge avatar configuration into agent dictionary."""
        agent_dict["avatar_type"] = avatar_config.avatar_type
        agent_dict["avatar_data"] = avatar_config.avatar_data
        agent_dict["pixel_character"] = avatar_config.pixel_character
        agent_dict["avatar_url"] = avatar_config.avatar_url
        
        # Add display avatar
        display_data = avatar_config.get_display_data()
        agent_dict["display_avatar"] = display_data
        
        return agent_dict


def create_avatar_from_agent_type(agent_type: str, name: str) -> AvatarConfig:
    """Create avatar configuration based on agent type."""
    avatar = AvatarManager.get_default_avatar(agent_type)
    
    # Generate unique character if using default
    if avatar.pixel_character == "🤖":
        avatar.pixel_character = AvatarManager.generate_pixel_avatar(name)
    
    return avatar
