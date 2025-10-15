"""
SQLAlchemy ORM models for the application.
"""
from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Enum,
    Integer,
    DateTime,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class EventStatus(str, enum.Enum):
    draft = "draft"
    published = "published"


class Event(Base):
    """
    Event ORM model representing an event in the system.
    """
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    location: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus, name="event_status"),
        nullable=False,
        default=EventStatus.draft,
        index=True,
    )
    # Keep tags simple as comma-separated values to avoid JSON deps
    tags: Mapped[str | None] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
