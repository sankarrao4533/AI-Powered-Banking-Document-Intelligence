"""CLI entrypoint to launch the Sentinel Banking API service."""

import uvicorn
from src.config import settings

if __name__ == "__main__":
    print(f"Starting Sentinel Banking API on http://{settings.API_HOST}:{settings.API_PORT} ...")
    uvicorn.run(
        "src.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
    )
