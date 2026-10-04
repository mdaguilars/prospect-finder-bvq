"""
Aplicación principal de Prospect Finder BVQ API.

Esta aplicación expone mediante FastAPI los servicios necesarios
para consumir el ranking operativo, similitud con emisores históricos
y explicabilidad del modelo.

Durante el arranque se inicializa y precalienta el runtime SHAP
para evitar que el primer usuario de la aplicación tenga que esperar
el costo de inicialización de PermutationExplainer.

La API mantiene separadas las capas de:

- configuración;
- base de datos;
- modelos ORM;
- routers/endpoints;
- lógica analítica.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.core.config import settings
from src.api.routers.catalogs import router as catalogs_router
from src.api.routers.explainability import (
    router as explainability_router,
)
from src.api.routers.health import router as health_router
from src.api.routers.prospects import router as prospects_router
from src.api.services.explainability import (
    _get_runtime,
)
from src.api.services.explainability import (
    explain_prospect,
)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    """
    Inicializa los componentes costosos de explicabilidad
    antes de aceptar solicitudes.

    El precalentamiento ejecuta una explicación SHAP real
    sobre una empresa del universo operativo. De esta manera,
    PermutationExplainer y los componentes internos utilizados
    por SHAP quedan preparados para las siguientes consultas.
    """

    print()
    print(
        "Inicializando explicabilidad SHAP..."
    )

    runtime = _get_runtime()

    operational = runtime[
        "operational"
    ]

    if operational.empty:
        raise RuntimeError(
            "No existen empresas en el universo "
            "operativo para precalentar SHAP."
        )

    warmup_expediente = int(
        operational.index[
            0
        ]
    )

    print(
        "Precalentando SHAP con expediente "
        f"{warmup_expediente}..."
    )

    explain_prospect(
        expediente_key=warmup_expediente,
        expected_score=None,
        top_n=1,
    )

    print(
        "SHAP inicializado correctamente."
    )
    print()

    yield


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
    lifespan=lifespan,
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


app.include_router(
    explainability_router,
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