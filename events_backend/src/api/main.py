from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text  # SQLAlchemy 2.x compatible text construct
import logging

from src.core.config import settings
from src.api.routes.events import router as events_router
from src.db.session import SessionLocal  # for startup DB check


# Configure basic logging for the application
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("events_backend")


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
    allow_origins=["*"],
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
    db = None
    try:
        db = SessionLocal()
        # execute a trivial no-op to initialize connection pool lazily using SQLAlchemy 2.x text()
        db.execute(text("SELECT 1"))
        logger.info("Database startup check: OK")
    except Exception as exc:
        # Raising here will cause uvicorn to fail fast with a clear error
        # This is preferable to latent failures on first request.
        logger.exception("Database startup check failed")
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


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Log HTTPExceptions to aid diagnostics while preserving client-facing messages and status codes.
    """
    logger.warning("HTTPException on %s %s: %s", request.method, request.url.path, exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all exception handler for uncaught errors.

    Logs the exception with stack trace and returns a generic 500 response to the client.
    """
    logger.exception("Unhandled exception on %s %s: %s", request.method, request.url.path, str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Include Events router
app.include_router(events_router)
