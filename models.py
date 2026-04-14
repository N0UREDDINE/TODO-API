"""
Pydantic models — request validation & response serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

PriorityLevel = Literal["low", "medium", "high"]


class TodoCreate(BaseModel):
    """Payload for creating a new todo."""

    title: str = Field(..., min_length=1, max_length=200, examples=["Buy groceries"])
    description: Optional[str] = Field(None, max_length=1000, examples=["Milk, eggs, bread"])
    priority: PriorityLevel = Field("medium", examples=["medium"])
    due_date: Optional[str] = Field(
        None,
        description="Optional due date in ISO 8601 format (YYYY-MM-DD)",
        examples=["2026-04-30"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "priority": "high",
                "due_date": "2026-04-30",
            }
        }
    }


class TodoUpdate(BaseModel):
    """Payload for a full (PUT) update — all fields required."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    done: bool
    priority: PriorityLevel
    due_date: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Buy organic groceries",
                "description": "From the farmers' market",
                "done": False,
                "priority": "high",
                "due_date": "2026-04-30",
            }
        }
    }


class TodoPatch(BaseModel):
    """Payload for a partial (PATCH) update — all fields optional."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    done: Optional[bool] = None
    priority: Optional[PriorityLevel] = None
    due_date: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {"done": True}
        }
    }


class TodoResponse(BaseModel):
    """Shape of a todo item returned by the API."""

    id: str
    title: str
    description: Optional[str]
    done: bool
    priority: PriorityLevel
    due_date: Optional[str]
    created_at: str
    updated_at: str
