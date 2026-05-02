"""Rulează backend-ul FastAPI cu `python -m web.backend`."""

import uvicorn

from web.backend.settings import settings


if __name__ == "__main__":
    uvicorn.run(
        "web.backend.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
