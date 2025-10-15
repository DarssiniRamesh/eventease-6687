from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.api.routes.events import router as events_router
from src.db.session import SessionLocal  # for startup DB check


app = FastAPI(
    title="EventEase Backend",
    description="Backend API for the Event Management App.",
    version="0.1.0",
    openapi_tags=[
        {"name": "Health", "description": "Health and diagnostics"},
        {"name": "Events", "description": "Event CRUD and listing"},
    ],
)

# CORS configuration driven by environment via Settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """
    Application startup hook.

    Verifies basic database connectivity early to surface configuration or permission issues.
    """
    # Attempt to get and close a session to ensure engine and DB URL are valid
    db = None
    try:
        db = SessionLocal()
        # execute a trivial no-op to initialize connection pool lazily
        db.execute("SELECT 1")
    except Exception as exc:
        # Raising here will cause uvicorn to fail fast with a clear error
        # This is preferable to latent failures on first request.
        raise RuntimeError(f"Database startup check failed: {exc}") from exc
    finally:
        if db is not None:
            db.close()


# PUBLIC_INTERFACE
@app.get(
    "/",
    tags=["Health"],
    summary="Health Check (root)",
    description="Simple health check endpoint at root.",
)
def root_health_check():
    """
    Health Check at root path.

    Returns:
        A simple message indicating service health.
    """
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Simple health check endpoint.",
)
def health_check():
    """
    Health Check endpoint.

    Returns:
        A simple message indicating service health.
    """
    return {"status": "ok"}


# Include Events router
app.include_router(events_router)
