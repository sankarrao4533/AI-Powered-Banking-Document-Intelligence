"""FastAPI application factory for Sentinel Banking Intelligence."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.config import settings


def create_app() -> FastAPI:
    """Instantiate and configure the FastAPI application."""
    app = FastAPI(
        title="Sentinel Banking Document Intelligence API",
        version="2.0.0",
        description="Enterprise Hybrid GraphRAG and Regulatory Governance API for Banking.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    app.include_router(router, prefix="/api")
    return app


app = create_app()
