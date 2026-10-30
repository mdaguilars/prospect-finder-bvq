"""
Pruebas automáticas del ranking operativo
de Prospect Finder BVQ API.

Estas pruebas utilizan la base PostgreSQL local cargada
con el universo operativo validado.

Se verifican:

- ranking general;
- filtros;
- detalle individual;
- indicadores financieros;
- comparables históricos;
- manejo de expedientes inexistentes.
"""

from __future__ import annotations

import pytest

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.api.core.database import SessionLocal
from src.api.routers.prospects import get_prospect_detail
from src.api.routers.prospects import get_prospects


EXPECTED_TOTAL_PROSPECTS = 137_156

EXPECTED_TOP_EXPEDIENTE = 719648

EXPECTED_TOP_SCORE = (
    0.9736944399096824
)


@pytest.fixture
def db_session():
    """
    Crea una sesión PostgreSQL para cada prueba
    y garantiza su cierre al finalizar.
    """

    database = SessionLocal()

    try:
        yield database

    finally:
        database.close()


def query_prospects(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 5,
    search: str | None = None,
    provincia: str | None = None,
    tipo_compania: str | None = None,
    min_score: float | None = None,
    min_similitud: float | None = None,
    comparables_disponibles: bool | None = None,
) -> dict:
    """
    Ejecuta get_prospects proporcionando explícitamente
    todos los parámetros que normalmente FastAPI
    resolvería desde la solicitud HTTP.
    """

    return get_prospects(
        page=page,
        page_size=page_size,
        search=search,
        provincia=provincia,
        tipo_compania=tipo_compania,
        min_score=min_score,
        min_similitud=min_similitud,
        comparables_disponibles=(
            comparables_disponibles
        ),
        db=db,
    )


def test_operational_ranking_first_page(
    db_session: Session,
) -> None:
    """
    El ranking debe devolver el universo completo
    y comenzar por la empresa ubicada en posición 1.
    """

    response = query_prospects(
        db_session,
        page=1,
        page_size=5,
    )

    metadata = response[
        "metadata"
    ]

    items = response[
        "items"
    ]

    assert metadata[
        "total_records"
    ] == EXPECTED_TOTAL_PROSPECTS

    assert metadata[
        "page"
    ] == 1

    assert metadata[
        "page_size"
    ] == 5

    assert len(
        items
    ) == 5

    first = items[
        0
    ]

    assert first[
        "ranking"
    ] == 1

    assert first[
        "expediente_key"
    ] == EXPECTED_TOP_EXPEDIENTE

    assert isinstance(first["nombre"], str)
    assert first["nombre"].strip()

    assert first[
        "provincia"
    ] == "PICHINCHA"

    assert first[
        "tipo_compania"
    ] == "ANÓNIMA"

    assert first[
        "score_afinidad"
    ] == pytest.approx(
        EXPECTED_TOP_SCORE,
        abs=1e-12,
    )

    assert first[
        "calidad_datos"
    ][
        "pct_features_disponibles"
    ] == 100.0

    assert first[
        "similitud_emisores"
    ][
        "comparables_disponibles"
    ] is True


def test_filter_by_province(
    db_session: Session,
) -> None:
    """
    El filtro por provincia debe aceptar el valor
    normalizado utilizado por la interfaz.
    """

    response = query_prospects(
        db_session,
        provincia="PICHINCHA",
        page_size=5,
    )

    assert response[
        "metadata"
    ][
        "total_records"
    ] == 43_487

    assert len(
        response[
            "items"
        ]
    ) == 5

    assert all(
        item[
            "provincia"
        ] == "PICHINCHA"
        for item in response[
            "items"
        ]
    )


def test_filter_normalized_company_type(
    db_session: Session,
) -> None:
    """
    El filtro debe funcionar aunque la fuente original
    contenga espacios internos adicionales.
    """

    response = query_prospects(
        db_session,
        tipo_compania=(
            "SUCURSAL EXTRANJERA"
        ),
        page_size=5,
    )

    assert response[
        "metadata"
    ][
        "total_records"
    ] == 722

    assert all(
        item[
            "tipo_compania"
        ] == "SUCURSAL EXTRANJERA"
        for item in response[
            "items"
        ]
    )


def test_prospect_detail(
    db_session: Session,
) -> None:
    """
    El detalle debe devolver identificación,
    priorización, finanzas y cinco comparables.
    """

    response = get_prospect_detail(
        expediente_key=(
            EXPECTED_TOP_EXPEDIENTE
        ),
        db=db_session,
    )

    empresa = response[
        "empresa"
    ]

    priorizacion = response[
        "priorizacion"
    ]

    financieros = response[
        "indicadores_financieros"
    ]

    similitud = response[
        "similitud_emisores"
    ]

    assert isinstance(empresa["nombre"], str)
    assert empresa["nombre"].strip()

    assert isinstance(empresa["ruc"], str)
    assert len(empresa["ruc"]) == 13
    assert empresa["ruc"].isdigit()

    assert empresa[
        "provincia"
    ] == "PICHINCHA"

    assert priorizacion[
        "ranking"
    ] == 1

    assert priorizacion[
        "score_afinidad"
    ] == pytest.approx(
        EXPECTED_TOP_SCORE,
        abs=1e-12,
    )

    assert financieros[
        "activos"
    ] == pytest.approx(
        143_864_325.23,
        abs=0.01,
    )

    assert financieros[
        "patrimonio"
    ] == pytest.approx(
        14_158_114.52,
        abs=0.01,
    )

    assert similitud[
        "comparables_disponibles"
    ] is True

    assert similitud[
        "n_emisores_comparados"
    ] == 5

    assert len(
        similitud[
            "comparables"
        ]
    ) == 5

    assert similitud[
        "comparables"
    ][
        0
    ][
        "orden"
    ] == 1

    assert similitud[
        "comparables"
    ][
        0
    ][
        "emisor"
    ][
        "nombre"
    ] == (
        "DISTRIBUIDORA DE MOTOCICLETAS "
        "MOTDIS S.A."
    )


def test_prospect_not_found(
    db_session: Session,
) -> None:
    """
    Un expediente inexistente debe producir
    una respuesta equivalente a HTTP 404.
    """

    with pytest.raises(
        HTTPException
    ) as error:

        get_prospect_detail(
            expediente_key=(
                9_999_999_999
            ),
            db=db_session,
        )

    assert error.value.status_code == 404
