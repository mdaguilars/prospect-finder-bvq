"""
Pruebas automáticas de explicabilidad
de Prospect Finder BVQ API.

Estas pruebas validan:

- importancia global SHAP ya calculada;
- estructura de una explicación local;
- integración de la explicación con el ranking;
- manejo de expedientes inexistentes.

La explicación SHAP local pesada se sustituye mediante
monkeypatch durante las pruebas automáticas para evitar
recalcular PermutationExplainer en cada ejecución de pytest.

La reconstrucción real del score mediante SHAP se valida
separadamente durante las pruebas funcionales del sistema.
"""

from __future__ import annotations

import pytest

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.api.core.database import SessionLocal
from src.api.routers import explainability


EXPECTED_EXPEDIENTE = 719648

EXPECTED_SCORE = (
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


def test_global_shap_importance() -> None:
    """
    La importancia global debe leer los resultados
    SHAP previamente validados del modelo v10.
    """

    response = (
        explainability.get_global_shap(
            limit=10
        )
    )

    assert response[
        "method"
    ] == (
        "SHAP model-agnostic mediante "
        "PermutationExplainer"
    )

    assert len(
        response[
            "items"
        ]
    ) == 10

    first = response[
        "items"
    ][
        0
    ]

    assert first[
        "rank"
    ] == 1

    assert first[
        "feature"
    ] == "activos_final"

    assert first[
        "label"
    ] == "Activos"

    assert first[
        "mean_abs_shap"
    ] == pytest.approx(
        0.0620299243591289,
        abs=1e-12,
    )


def test_local_explanation_endpoint_structure(
    monkeypatch,
    db_session: Session,
) -> None:
    """
    Verifica la integración del endpoint local
    sin ejecutar nuevamente el cálculo pesado SHAP.
    """

    def fake_explain_prospect(
        expediente_key: int,
        expected_score: float | None,
        top_n: int,
    ) -> dict:

        assert (
            expediente_key
            == EXPECTED_EXPEDIENTE
        )

        assert (
            expected_score
            == pytest.approx(
                EXPECTED_SCORE,
                abs=1e-12,
            )
        )

        assert top_n == 5

        return {
            "empresa": {
                "expediente_key":
                    EXPECTED_EXPEDIENTE,
                "nombre":
                    "EMPRESA PRUEBA A S.A.",
            },
            "score": {
                "modelo":
                    EXPECTED_SCORE,
            },
            "shap": {
                "base_value":
                    0.1783474992099843,
                "reconstructed_score":
                    EXPECTED_SCORE,
                "local_error":
                    0.0,
            },
            "principales_factores": [
                {
                    "feature":
                        "activos_final",
                    "label":
                        "Activos",
                    "shap_value":
                        0.25,
                    "direction":
                        "aumenta_afinidad",
                }
            ],
            "metadata": {
                "model_name":
                    "v10_hgb_financial_c3",
                "config_id":
                    "C3_CONSERVATIVE",
            },
        }

    monkeypatch.setattr(
        explainability,
        "explain_prospect",
        fake_explain_prospect,
    )

    response = (
        explainability
        .get_prospect_explanation(
            expediente_key=(
                EXPECTED_EXPEDIENTE
            ),
            top_n=5,
            db=db_session,
        )
    )

    assert response[
        "empresa"
    ][
        "nombre"
    ] == "EMPRESA PRUEBA A S.A."

    assert response[
        "score"
    ][
        "modelo"
    ] == pytest.approx(
        EXPECTED_SCORE,
        abs=1e-12,
    )

    assert response[
        "ranking"
    ][
        "posicion"
    ] == 1

    assert response[
        "ranking"
    ][
        "percentil"
    ] == pytest.approx(
        100.0,
        abs=1e-12,
    )

    assert response[
        "principales_factores"
    ][
        0
    ][
        "feature"
    ] == "activos_final"


def test_local_explanation_prospect_not_found(
    db_session: Session,
) -> None:
    """
    Un expediente inexistente debe producir
    una respuesta equivalente a HTTP 404.
    """

    with pytest.raises(
        HTTPException
    ) as error:

        explainability.get_prospect_explanation(
            expediente_key=(
                9_999_999_999
            ),
            top_n=5,
            db=db_session,
        )

    assert (
        error.value.status_code
        == 404
    )
