"""
Health check de Prospect Finder BVQ API.

Este endpoint permite verificar:

- que la API esté ejecutándose;
- que PostgreSQL responda;
- la versión de la aplicación;
- el entorno configurado.

No expone credenciales ni información sensible.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import status

from src.api.core.config import settings
from src.api.core.database import check_database_connection
from src.api.core.database import get_database_info


router = APIRouter(
    prefix="/health",
    tags=[
        "health",
    ],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
)
def health_check() -> dict:
    """
    Devuelve el estado general de la API
    y de la conexión a PostgreSQL.
    """

    database_ok = (
        check_database_connection()
    )

    database_info = (
        get_database_info()
    )

    overall_status = (
        "ok"
        if database_ok
        else "degraded"
    )

    return {
        "status":
            overall_status,
        "application":
            settings.app_name,
        "version":
            settings.app_version,
        "environment":
            settings.environment,
        "database": {
            "connected":
                database_ok,
            "driver":
                database_info[
                    "driver"
                ],
            "host":
                database_info[
                    "host"
                ],
            "port":
                database_info[
                    "port"
                ],
            "database":
                database_info[
                    "database"
                ],
        },
    }