"""
Endpoints de explicabilidad de Prospect Finder BVQ.

Este router expone:

- explicación SHAP local por empresa;
- importancia global SHAP del modelo.

En modo normal utiliza el modelo congelado v10 y las evidencias SHAP
reales. En modo evaluador puede devolver una explicación sintética local
para demostrar el flujo funcional sin requerir artefactos privados.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.core.config import settings
from src.api.core.database import get_db
from src.api.models.prospect import OperationalProspect
from src.api.services.demo_explainability import (
    get_demo_global_importance,
    get_demo_prospect_explanation,
)
from src.api.services.explainability import (
    ExplainabilityError,
)
from src.api.services.explainability import (
    explain_prospect,
)
from src.api.services.explainability import (
    get_global_importance,
)


router = APIRouter(
    prefix="/explainability",
    tags=["explainability"],
)


@router.get(
    "/global"
)
def get_global_shap(
    limit: int = Query(
        default=15,
        ge=1,
        le=25,
        description=(
            "Número máximo de variables "
            "a devolver."
        ),
    ),
) -> dict:
    """
    Devuelve la importancia global SHAP.

    En modo normal se utiliza la evidencia SHAP real ya calculada.
    En modo evaluador se conserva la ruta compatible con el frontend.
    """

    if settings.evaluator_demo_mode:
        try:
            return get_global_importance(
                limit=limit
            )
        except (
            FileNotFoundError,
            ExplainabilityError,
            ValueError,
        ):
            return get_demo_global_importance(
                limit=limit
            )

    try:
        return get_global_importance(
            limit=limit
        )

    except (
        FileNotFoundError,
        ExplainabilityError,
        ValueError,
    ) as error:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(
                error
            ),
        ) from error


@router.get(
    "/prospects/{expediente_key}"
)
def get_prospect_explanation(
    expediente_key: int,
    top_n: int = Query(
        default=10,
        ge=1,
        le=25,
        description=(
            "Número de factores SHAP "
            "principales a devolver."
        ),
    ),
    db: Session = Depends(
        get_db
    ),
) -> dict:
    """
    Genera una explicación local para una empresa del ranking.

    En modo normal utiliza SHAP real. En modo evaluador utiliza
    una explicación sintética claramente identificada.
    """

    prospect = db.execute(
        select(
            OperationalProspect
        ).where(
            OperationalProspect.expediente_key
            == expediente_key
        )
    ).scalar_one_or_none()

    if prospect is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "No se encontró una empresa "
                "con el expediente solicitado."
            ),
        )

    if settings.evaluator_demo_mode:
        return get_demo_prospect_explanation(
            prospect=prospect,
            top_n=top_n,
        )

    try:
        explanation = explain_prospect(
            expediente_key=expediente_key,
            expected_score=(
                prospect.score_afinidad
            ),
            top_n=top_n,
        )

    except KeyError as error:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(
                error
            ),
        ) from error

    except (
        ExplainabilityError,
        FileNotFoundError,
        ValueError,
    ) as error:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(
                error
            ),
        ) from error

    explanation[
        "ranking"
    ] = {
        "posicion":
            prospect.ranking,
        "percentil":
            prospect.percentil_ranking,
    }

    return explanation
