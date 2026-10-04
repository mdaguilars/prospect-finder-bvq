"""
Catálogos operativos de Prospect Finder BVQ.

Este router entrega los valores disponibles para filtros de la
interfaz, obtenidos directamente desde PostgreSQL.

Actualmente expone:

- provincias;
- tipos de compañía.

Los valores se normalizan eliminando espacios innecesarios y se
acompañan del número de empresas existentes en el universo operativo.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.core.database import get_db
from src.api.models.prospect import OperationalProspect


router = APIRouter(
    prefix="/catalogs",
    tags=["catalogs"],
)


def normalized_text(column):
    """
    Normaliza valores de texto en PostgreSQL:

    - elimina espacios al inicio;
    - elimina espacios al final;
    - reemplaza múltiples espacios internos por uno solo.
    """

    return func.regexp_replace(
        func.trim(column),
        "[[:space:]]+",
        " ",
        "g",
    )


@router.get("")
def get_catalogs(
    db: Session = Depends(get_db),
) -> dict:
    """
    Devuelve los catálogos necesarios para construir
    los filtros de la interfaz web.
    """

    provincia_value = normalized_text(
        OperationalProspect.provincia
    )

    provincias_query = (
        select(
            provincia_value.label("value"),
            func.count(
                OperationalProspect.expediente_key
            ).label("count"),
        )
        .where(
            OperationalProspect.provincia.is_not(None),
            provincia_value != "",
        )
        .group_by(
            provincia_value
        )
        .order_by(
            provincia_value.asc()
        )
    )

    provincias_rows = (
        db.execute(
            provincias_query
        )
        .mappings()
        .all()
    )

    tipo_value = normalized_text(
        OperationalProspect.tipo_compania
    )

    tipos_query = (
        select(
            tipo_value.label("value"),
            func.count(
                OperationalProspect.expediente_key
            ).label("count"),
        )
        .where(
            OperationalProspect.tipo_compania.is_not(None),
            tipo_value != "",
        )
        .group_by(
            tipo_value
        )
        .order_by(
            tipo_value.asc()
        )
    )

    tipos_rows = (
        db.execute(
            tipos_query
        )
        .mappings()
        .all()
    )

    provincias = [
        {
            "value": row["value"],
            "count": row["count"],
        }
        for row in provincias_rows
    ]

    tipos_compania = [
        {
            "value": row["value"],
            "count": row["count"],
        }
        for row in tipos_rows
    ]

    return {
        "provincias": provincias,
        "tipos_compania": tipos_compania,
        "metadata": {
            "total_provincias": len(
                provincias
            ),
            "total_tipos_compania": len(
                tipos_compania
            ),
        },
    }