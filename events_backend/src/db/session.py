"""
Database session and engine management.

- Reads DATABASE_URL from environment (default sqlite:///./events.db)
- Creates SQLAlchemy Engine and SessionLocal
- Provides FastAPI dependency get_db()
- Auto-creates tables in development mode
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.core.config import settings
from src.db.base import create_all_tables


def _engine_kwargs_from_url(db_url: str) -> dict:
    """Return engine kwargs based on driver and environment."""
    kwargs: dict = {"pool_pre_ping": True}
    if db_url.startswith("sqlite"):
        # SQLite needs check_same_thread for multithreaded servers like Uvicorn
        kwargs["connect_args"] = {"check_same_thread": False}
    return kwargs


DATABASE_URL: str = settings.DATABASE_URL

engine = create_engine(DATABASE_URL, **_engine_kwargs_from_url(DATABASE_URL))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session.

    Yields:
        sqlalchemy.orm.Session: A SQLAlchemy session bound to the configured engine.
    """
    db: Optional[Session] = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Context manager providing a transactional scope around a series of operations.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Auto-create tables in development/local environments to improve DX
if os.getenv("ENV", "development").lower() in ("dev", "develop", "development", "local"):
    # Import models to ensure they are registered with Base.metadata before create_all
    # Import kept inside the block to avoid circulars on module import
    from src.db import models  # noqa: F401

    create_all_tables(engine)
