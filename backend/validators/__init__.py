"""Request validation models using Pydantic."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class AgentStatusUpdateRequest(BaseModel):
    """Validation model for agent status update requests."""
    
    state: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="New agent state"
    )
    
    @field_validator('state')
    @classmethod
    def validate_state(cls, v: str) -> str:
        """Validate and normalize state value."""
        valid_states = {'idle', 'writing', 'researching', 'executing', 'syncing', 'error'}
        v_lower = v.lower().strip()
        
        if v_lower in valid_states:
            return v_lower
        
        # Map common synonyms
        state_mapping = {
            "waiting": "idle",
            "standby": "idle",
            "coding": "writing",
            "developing": "writing",
            "testing": "executing",
            "deploying": "executing",
            "running": "executing",
            "synchronizing": "syncing",
            "failed": "error",
            "broken": "error",
        }
        
        return state_mapping.get(v_lower, "idle")


class AssetPositionsRequest(BaseModel):
    """Validation model for asset positions update."""
    
    positions: dict = Field(
        ...,
        description="Asset positions configuration"
    )
    
    @field_validator('positions')
    @classmethod
    def validate_positions(cls, v: dict) -> dict:
        """Validate positions is a non-empty dict."""
        if not isinstance(v, dict):
            raise ValueError("Positions must be a dictionary")
        return v


class AssetDefaultsRequest(BaseModel):
    """Validation model for asset defaults update."""
    
    defaults: dict = Field(
        ...,
        description="Asset defaults configuration"
    )
    
    @field_validator('defaults')
    @classmethod
    def validate_defaults(cls, v: dict) -> dict:
        """Validate defaults is a dict."""
        if not isinstance(v, dict):
            raise ValueError("Defaults must be a dictionary")
        return v


class ConfigUpdateRequest(BaseModel):
    """Validation model for runtime config update."""
    
    gemini_api_key: Optional[str] = Field(
        None,
        min_length=10,
        max_length=200,
        description="Gemini API key"
    )
    custom_config: Optional[dict] = Field(
        None,
        description="Custom configuration options"
    )


class AgentIDPath(BaseModel):
    """Validation model for agent ID path parameter."""
    
    agent_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Agent unique identifier"
    )
    
    @field_validator('agent_id')
    @classmethod
    def validate_agent_id(cls, v: str) -> str:
        """Validate agent ID format."""
        v = v.strip()
        if not v:
            raise ValueError("Agent ID cannot be empty")
        return v


class ValidationErrorResponse(BaseModel):
    """Standard error response model."""
    
    ok: bool = False
    msg: str = "An error occurred"
    errors: Optional[List[str]] = None


class SuccessResponse(BaseModel):
    """Standard success response model."""
    
    ok: bool = True
    data: Optional[dict] = None
    message: Optional[str] = "Success"
