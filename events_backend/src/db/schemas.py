"""
Pydantic schemas for Event entity.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator, ValidationInfo, ConfigDict


class EventBase(BaseModel):
    """Shared properties for Event schemas."""
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Detailed description of the event")
    start_time: datetime = Field(..., description="Start time (timezone-aware datetime)")
    end_time: datetime = Field(..., description="End time (timezone-aware datetime)")
    location: Optional[str] = Field(None, description="Event location (optional)")
    capacity: Optional[int] = Field(None, ge=0, description="Maximum attendees (optional)")
    status: Literal["draft", "published"] = Field("draft", description="Event status")
    tags: Optional[str] = Field(
        None,
        description="Comma-separated tags (e.g., 'tech,meetup,web')",
    )

    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, v: datetime, info: ValidationInfo):
        """
        Validate that end_time is after start_time.

        With Pydantic v2, cross-field access is via ValidationInfo.data.
        """
        start = info.data.get("start_time")
        if start and v <= start:
            raise ValueError("end_time must be after start_time")
        return v


class EventCreate(EventBase):
    """Schema for creating a new Event."""
    pass


class EventUpdate(BaseModel):
    """Schema for updating an existing Event (all fields optional)."""
    title: Optional[str] = Field(None, description="Event title")
    description: Optional[str] = Field(None, description="Detailed description of the event")
    start_time: Optional[datetime] = Field(None, description="Start time (timezone-aware datetime)")
    end_time: Optional[datetime] = Field(None, description="End time (timezone-aware datetime)")
    location: Optional[str] = Field(None, description="Event location (optional)")
    capacity: Optional[int] = Field(None, ge=0, description="Maximum attendees (optional)")
    status: Optional[Literal["draft", "published"]] = Field(None, description="Event status")
    tags: Optional[str] = Field(None, description="Comma-separated tags")

    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, v: datetime | None, info: ValidationInfo):
        """
        Only validate if both start and end provided; uses Pydantic v2 ValidationInfo.
        """
        start = info.data.get("start_time")
        if v is not None and start is not None and v <= start:
            raise ValueError("end_time must be after start_time")
        return v


class EventOut(EventBase):
    """Schema returned in API responses for Event."""
    id: int = Field(..., description="Event identifier")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")

    # Ensure ORM objects (SQLAlchemy) are converted correctly in Pydantic v2
    model_config = ConfigDict(from_attributes=True)
