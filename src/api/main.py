"""
Aplicación principal de Prospect Finder BVQ API.

Esta aplicación expone mediante FastAPI los servicios necesarios
para consumir el ranking operativo, similitud con emisores históricos
y posteriormente la explicabilidad del modelo.

La API mantiene separadas las capas de:

- configuración;
- base de datos;
- modelos ORM;
- routers/endpoints;
- lógica analítica.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.core.config import settings
from src.api.routers.catalogs import router as catalogs_router
from src.api.routers.health import router as health_router
from src.api.routers.prospects import router as prospects_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API del prototipo Prospect Finder BVQ para consulta del "
        "ranking de prospectos, indicadores, comparables históricos "
        "y explicabilidad del modelo de priorización."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router,
    prefix=settings.api_prefix,
)


app.include_router(
    prospects_router,
    prefix=settings.api_prefix,
)


app.include_router(
    catalogs_router,
    prefix=settings.api_prefix,
)


@app.get(
    "/",
    tags=["root"],
)
def root() -> dict:
    """
    Endpoint raíz de la API.
    """

    return {
        "application": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "api_prefix": settings.api_prefix,
        "documentation": "/docs",
    }