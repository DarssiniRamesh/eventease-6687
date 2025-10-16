"""
Pydantic schemas for Event entity.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Literal, List, Union

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
    # Accept either a comma-separated string or an array of strings from clients.
    # We normalize to a comma-separated string for storage and downstream logic.
    tags: Optional[Union[str, List[str]]] = Field(
        None,
        description="Tags can be provided as a comma-separated string (e.g., 'tech,meetup,web') or as an array of strings.",
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

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, v: Optional[Union[str, List[str]]]) -> Optional[str]:
        """
        Normalize tags to a comma-separated string.

        Accepts:
          - None
          - string: returns stripped string (collapsing extra spaces around commas)
          - list[str]: joins with commas after stripping whitespace and ignoring empties
        """
        if v is None:
            return None
        if isinstance(v, str):
            # Normalize spaces around commas and trim
            parts = [p.strip() for p in v.split(",") if p.strip()]
            return ",".join(parts) if parts else None
        if isinstance(v, list):
            parts: List[str] = []
            for item in v:
                if not isinstance(item, str):
                    raise ValueError("Each tag must be a string")
                s = item.strip()
                if s:
                    parts.append(s)
            return ",".join(parts) if parts else None
        # Should not reach here due to type union, but safe-guard
        raise ValueError("Invalid type for tags")


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
    # Accept string or array like in create; normalize to comma-separated string
    tags: Optional[Union[str, List[str]]] = Field(
        None,
        description="Tags can be provided as a comma-separated string or array of strings",
    )

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

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, v: Optional[Union[str, List[str]]]) -> Optional[str]:
        """
        Normalize tags to a comma-separated string for updates as well.
        """
        if v is None:
            return None
        if isinstance(v, str):
            parts = [p.strip() for p in v.split(",") if p.strip()]
            return ",".join(parts) if parts else None
        if isinstance(v, list):
            cleaned = []
            for item in v:
                if not isinstance(item, str):
                    raise ValueError("Each tag must be a string")
                s = item.strip()
                if s:
                    cleaned.append(s)
            return ",".join(cleaned) if cleaned else None
        raise ValueError("Invalid type for tags")


class EventOut(EventBase):
    """Schema returned in API responses for Event."""
    id: int = Field(..., description="Event identifier")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")
    # Note: EventOut inherits tags field which accepts string or list,
    # but due to normalization it will be returned as a comma-separated string.

    # Ensure ORM objects (SQLAlchemy) are converted correctly in Pydantic v2
    model_config = ConfigDict(from_attributes=True)
