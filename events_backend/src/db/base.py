"""
Database base definition and development-time table creation.

This module defines the SQLAlchemy Declarative Base and includes a convenience
function to create all tables in development environments.
"""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative Base for all ORM models."""
    pass


# PUBLIC_INTERFACE
def create_all_tables(engine) -> None:
    """
    Create all tables defined on the Base metadata.

    Intended to be used on application startup in development environments.
    """
    Base.metadata.create_all(bind=engine)
