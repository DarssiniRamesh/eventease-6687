from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.api.routes.events import router as events_router

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


@app.get("/", tags=["Health"], summary="Health Check", description="Simple health check endpoint.")
def health_check():
    """
    Health Check

    Returns:
        A simple message indicating service health.
    """
    return {"message": "Healthy"}


# Include Events router
app.include_router(events_router)
