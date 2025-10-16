"""
API package initialization.

This module makes the routes subpackage discoverable for concise imports.
For example:
    from src.api.routes.events import router as events_router
"""

# Expose submodules for discoverability (import side-effects only)
from . import routes  # noqa: F401


# PUBLIC_INTERFACE
def api_package_info() -> str:
    """Return basic information about the API package."""
    return "src.api package with FastAPI app and routes"
