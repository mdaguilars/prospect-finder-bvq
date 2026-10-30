"""
Endpoints de consulta del ranking operativo de Prospect Finder BVQ.

Este router permite:

- consultar el ranking general de prospectos;
- buscar y filtrar empresas;
- consultar el detalle individual de una empresa;
- visualizar sus principales indicadores financieros;
- consultar los emisores históricos más similares;
- consultar el perfil financiero histórico de cada emisor comparable.

El score de afinidad y la similitud con emisores históricos se
mantienen como indicadores independientes.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.core.database import get_db
from src.api.models.prospect import IssuerReferenceProfile
from src.api.models.prospect import IssuerSimilarityMatch
from src.api.models.prospect import IssuerSimilaritySummary
from src.api.models.prospect import OperationalProspect


router = APIRouter(
    prefix="/prospects",
    tags=["prospects"],
)


# ============================================================
# UTILIDADES
# ============================================================

def clean_text(
    value: str | None,
) -> str | None:
    """
    Normaliza textos devueltos por la API:

    - elimina espacios al inicio y al final;
    - reemplaza múltiples espacios internos por uno solo.
    """

    if value is None:
        return None

    return " ".join(
        value.split()
    )


def normalized_text(column):
    """
    Normaliza valores de texto directamente en PostgreSQL:

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


def build_reference_profile_payload(
    profile: IssuerReferenceProfile | None,
) -> dict | None:
    """
    Construye el perfil financiero histórico del emisor comparable.

    Las siete variables corresponden exactamente a las utilizadas
    por el motor de similitud v10.

    Si no existe perfil, devuelve None.
    """

    if profile is None:
        return None

    return {
        "activos":
            profile.activos_final,

        "patrimonio":
            profile.patrimonio_final,

        "ingresos_ventas":
            profile.bi_ingresos_ventas,

        "numero_empleados":
            profile.bi_n_empleados,

        "ratio_patrimonio_activos":
            profile.fin_ratio_patrimonio_activos,

        "roa":
            profile.fin_roa,

        "rotacion_activos":
            profile.fin_rotacion_activos,
    }


def build_reference_percentiles_payload(
    profile: IssuerReferenceProfile | None,
) -> dict | None:
    """
    Devuelve los siete percentiles utilizados para calcular
    la distancia entre el prospecto y el emisor histórico.

    Se conservan para transparencia y trazabilidad.
    """

    if profile is None:
        return None

    return {
        "activos":
            profile.pct__activos_final,

        "patrimonio":
            profile.pct__patrimonio_final,

        "ingresos_ventas":
            profile.pct__bi_ingresos_ventas,

        "numero_empleados":
            profile.pct__bi_n_empleados,

        "ratio_patrimonio_activos":
            profile.pct__fin_ratio_patrimonio_activos,

        "roa":
            profile.pct__fin_roa,

        "rotacion_activos":
            profile.pct__fin_rotacion_activos,
    }


# ============================================================
# RANKING GENERAL
# ============================================================

@router.get("")
def get_prospects(
    page: int = Query(
        default=1,
        ge=1,
        description="Número de página.",
    ),
    page_size: int = Query(
        default=50,
        ge=1,
        le=200,
        description="Número de empresas por página.",
    ),
    search: str | None = Query(
        default=None,
        description=(
            "Búsqueda parcial por nombre, RUC "
            "o expediente."
        ),
    ),
    provincia: str | None = Query(
        default=None,
        description="Filtro por provincia.",
    ),
    tipo_compania: str | None = Query(
        default=None,
        description="Filtro por tipo de compañía.",
    ),
    min_score: float | None = Query(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "Score mínimo de afinidad. "
            "No representa una probabilidad calibrada."
        ),
    ),
    min_similitud: float | None = Query(
        default=None,
        ge=0.0,
        le=100.0,
        description=(
            "Similitud mínima con el emisor histórico "
            "más cercano."
        ),
    ),
    comparables_disponibles: bool | None = Query(
        default=None,
        description=(
            "Permite filtrar empresas con o sin "
            "comparables históricos disponibles."
        ),
    ),
    db: Session = Depends(get_db),
) -> dict:
    """
    Consulta paginada del ranking operativo.

    El orden predeterminado corresponde al ranking generado
    por el modelo, desde la empresa con mayor prioridad hacia
    la de menor prioridad.
    """

    filters = []

    # --------------------------------------------------------
    # BÚSQUEDA
    # --------------------------------------------------------

    if search:
        search_clean = clean_text(
            search
        )

        if search_clean:
            search_pattern = (
                f"%{search_clean}%"
            )

            search_filters = [
                OperationalProspect.nombre.ilike(
                    search_pattern
                ),
                OperationalProspect.ruc.ilike(
                    search_pattern
                ),
            ]

            try:
                expediente_value = int(
                    search_clean
                )

                search_filters.append(
                    OperationalProspect.expediente_key
                    == expediente_value
                )

            except ValueError:
                pass

            filters.append(
                or_(
                    *search_filters
                )
            )

    # --------------------------------------------------------
    # PROVINCIA
    # --------------------------------------------------------

    if provincia:
        provincia_clean = clean_text(
            provincia
        )

        if provincia_clean:
            filters.append(
                normalized_text(
                    OperationalProspect.provincia
                )
                == provincia_clean
            )

    # --------------------------------------------------------
    # TIPO DE COMPAÑÍA
    # --------------------------------------------------------

    if tipo_compania:
        tipo_compania_clean = clean_text(
            tipo_compania
        )

        if tipo_compania_clean:
            filters.append(
                normalized_text(
                    OperationalProspect.tipo_compania
                )
                == tipo_compania_clean
            )

    # --------------------------------------------------------
    # SCORE MÍNIMO
    # --------------------------------------------------------

    if min_score is not None:
        filters.append(
            OperationalProspect.score_afinidad
            >= min_score
        )

    # --------------------------------------------------------
    # SIMILITUD MÍNIMA
    # --------------------------------------------------------

    if min_similitud is not None:
        filters.append(
            IssuerSimilaritySummary
            .similitud_emisor_top1
            >= min_similitud
        )

    # --------------------------------------------------------
    # DISPONIBILIDAD DE COMPARABLES
    # --------------------------------------------------------

    if comparables_disponibles is not None:
        filters.append(
            IssuerSimilaritySummary
            .comparables_disponibles
            == comparables_disponibles
        )

    # --------------------------------------------------------
    # CONSULTA PRINCIPAL
    # --------------------------------------------------------

    base_query = (
        select(
            OperationalProspect.expediente_key,
            OperationalProspect.ruc,
            OperationalProspect.nombre,
            OperationalProspect.anio,
            OperationalProspect.fecha_decision,
            OperationalProspect.tipo_compania,
            OperationalProspect.provincia,
            OperationalProspect.ranking,
            OperationalProspect.score_afinidad,
            OperationalProspect.percentil_ranking,
            OperationalProspect.n_features_disponibles,
            OperationalProspect.pct_features_disponibles,

            IssuerSimilaritySummary
            .comparables_disponibles,

            IssuerSimilaritySummary
            .similitud_emisor_top1,

            IssuerSimilaritySummary
            .similitud_emisores_top5_promedio,

            IssuerSimilaritySummary
            .estado_similitud,
        )
        .select_from(
            OperationalProspect
        )
        .outerjoin(
            IssuerSimilaritySummary,
            IssuerSimilaritySummary.expediente_key
            == OperationalProspect.expediente_key,
        )
    )

    # --------------------------------------------------------
    # CONTEO
    # --------------------------------------------------------

    count_query = (
        select(
            func.count(
                OperationalProspect.expediente_key
            )
        )
        .select_from(
            OperationalProspect
        )
        .outerjoin(
            IssuerSimilaritySummary,
            IssuerSimilaritySummary.expediente_key
            == OperationalProspect.expediente_key,
        )
    )

    # --------------------------------------------------------
    # APLICAR FILTROS
    # --------------------------------------------------------

    if filters:
        base_query = base_query.where(
            *filters
        )

        count_query = count_query.where(
            *filters
        )

    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

    total = db.execute(
        count_query
    ).scalar_one()

    offset = (
        page - 1
    ) * page_size

    # --------------------------------------------------------
    # PAGINACIÓN
    # --------------------------------------------------------

    query = (
        base_query
        .order_by(
            OperationalProspect
            .ranking
            .asc()
        )
        .offset(
            offset
        )
        .limit(
            page_size
        )
    )

    rows = (
        db.execute(
            query
        )
        .mappings()
        .all()
    )

    # --------------------------------------------------------
    # RESPUESTA
    # --------------------------------------------------------

    items = [
        {
            "expediente_key":
                row[
                    "expediente_key"
                ],

            "ruc":
                clean_text(
                    row["ruc"]
                ),

            "nombre":
                clean_text(
                    row["nombre"]
                ),

            "anio":
                row[
                    "anio"
                ],

            "fecha_decision":
                row[
                    "fecha_decision"
                ],

            "tipo_compania":
                clean_text(
                    row[
                        "tipo_compania"
                    ]
                ),

            "provincia":
                clean_text(
                    row[
                        "provincia"
                    ]
                ),

            "ranking":
                row[
                    "ranking"
                ],

            "score_afinidad":
                row[
                    "score_afinidad"
                ],

            "percentil_ranking":
                row[
                    "percentil_ranking"
                ],

            "calidad_datos": {
                "n_features_disponibles":
                    row[
                        "n_features_disponibles"
                    ],

                "pct_features_disponibles":
                    row[
                        "pct_features_disponibles"
                    ],
            },

            "similitud_emisores": {
                "comparables_disponibles":
                    row[
                        "comparables_disponibles"
                    ],

                "similitud_top1":
                    row[
                        "similitud_emisor_top1"
                    ],

                "similitud_top5_promedio":
                    row[
                        "similitud_emisores_top5_promedio"
                    ],

                "estado":
                    clean_text(
                        row[
                            "estado_similitud"
                        ]
                    ),
            },
        }
        for row in rows
    ]

    total_pages = (
        (
            total
            + page_size
            - 1
        )
        // page_size
    )

    return {
        "metadata": {
            "page":
                page,

            "page_size":
                page_size,

            "total_records":
                total,

            "total_pages":
                total_pages,

            "sort":
                "ranking_asc",

            "score_note": (
                "El score de afinidad es un indicador "
                "de priorización y no una probabilidad "
                "calibrada."
            ),

            "similarity_note": (
                "La similitud con emisores históricos "
                "es un indicador independiente del score "
                "predictivo."
            ),
        },

        "items":
            items,
    }


# ============================================================
# DETALLE DE EMPRESA
# ============================================================

@router.get("/{expediente_key}")
def get_prospect_detail(
    expediente_key: int,
    db: Session = Depends(get_db),
) -> dict:
    """
    Devuelve el detalle completo de una empresa del ranking.

    Incluye:

    - identificación;
    - priorización;
    - calidad de información;
    - indicadores financieros;
    - similitud con emisores históricos;
    - cinco emisores comparables;
    - perfil financiero histórico de cada comparable;
    - percentiles utilizados para calcular la similitud.
    """

    # --------------------------------------------------------
    # PROSPECTO
    # --------------------------------------------------------

    prospect = db.execute(
        select(
            OperationalProspect
        )
        .where(
            OperationalProspect.expediente_key
            == expediente_key
        )
    ).scalar_one_or_none()

    if prospect is None:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=(
                "No se encontró una empresa con el "
                "expediente solicitado."
            ),
        )

    # --------------------------------------------------------
    # RESUMEN DE SIMILITUD
    # --------------------------------------------------------

    similarity = db.execute(
        select(
            IssuerSimilaritySummary
        )
        .where(
            IssuerSimilaritySummary.expediente_key
            == expediente_key
        )
    ).scalar_one_or_none()

    # --------------------------------------------------------
    # COMPARABLES
    # --------------------------------------------------------

    matches = (
        db.execute(
            select(
                IssuerSimilarityMatch
            )
            .where(
                IssuerSimilarityMatch.expediente_key
                == expediente_key
            )
            .order_by(
                IssuerSimilarityMatch
                .orden_comparable
                .asc()
            )
        )
        .scalars()
        .all()
    )

    # --------------------------------------------------------
    # EXPEDIENTES DE EMISORES REFERENCIA
    # --------------------------------------------------------

    reference_keys = list(
        {
            match.emisor_expediente_key
            for match in matches
        }
    )

    # --------------------------------------------------------
    # PERFILES HISTÓRICOS
    # --------------------------------------------------------

    reference_profiles_by_key: dict[
        int,
        IssuerReferenceProfile,
    ] = {}

    if reference_keys:
        reference_profiles = (
            db.execute(
                select(
                    IssuerReferenceProfile
                )
                .where(
                    IssuerReferenceProfile
                    .expediente_key
                    .in_(
                        reference_keys
                    )
                )
            )
            .scalars()
            .all()
        )

        reference_profiles_by_key = {
            profile.expediente_key:
                profile

            for profile in reference_profiles
        }

    # --------------------------------------------------------
    # CONSTRUIR COMPARABLES
    # --------------------------------------------------------

    comparables = []

    for match in matches:
        reference_profile = (
            reference_profiles_by_key.get(
                match.emisor_expediente_key
            )
        )

        perfil_financiero = (
            build_reference_profile_payload(
                reference_profile
            )
        )

        percentiles_similitud = (
            build_reference_percentiles_payload(
                reference_profile
            )
        )

        comparables.append(
            {
                "orden":
                    match.orden_comparable,

                "similitud":
                    match.similitud,

                "distancia_percentiles":
                    match.distancia_percentiles,

                "mismo_tipo_compania":
                    match.mismo_tipo_compania,

                "emisor": {
                    "expediente_key":
                        match.emisor_expediente_key,

                    "ruc":
                        clean_text(
                            match.emisor_ruc
                        ),

                    "nombre":
                        clean_text(
                            match.emisor_nombre
                        ),

                    "anio_perfil":
                        match.emisor_anio_perfil,

                    "fecha_decision_perfil":
                        match.emisor_fecha_decision_perfil,

                    "fecha_primera_inscripcion":
                        match.emisor_fecha_primera_inscripcion,

                    "tipo_compania":
                        clean_text(
                            match.emisor_tipo_compania
                        ),

                    "provincia":
                        clean_text(
                            match.emisor_provincia
                        ),

                    # ----------------------------------------
                    # NUEVO
                    # ----------------------------------------

                    "perfil_disponible":
                        reference_profile
                        is not None,

                    "perfil_financiero":
                        perfil_financiero,

                    "percentiles_similitud":
                        percentiles_similitud,
                },
            }
        )

    # --------------------------------------------------------
    # PAYLOAD DE SIMILITUD
    # --------------------------------------------------------

    similarity_payload = {
        "comparables_disponibles":
            False,

        "similitud_top1":
            None,

        "similitud_top5_promedio":
            None,

        "distancia_top1":
            None,

        "n_emisores_comparados":
            None,

        "estado":
            None,

        "metodologia":
            None,
    }

    if similarity is not None:
        similarity_payload = {
            "comparables_disponibles":
                similarity
                .comparables_disponibles,

            "similitud_top1":
                similarity
                .similitud_emisor_top1,

            "similitud_top5_promedio":
                similarity
                .similitud_emisores_top5_promedio,

            "distancia_top1":
                similarity
                .distancia_emisor_top1,

            "n_emisores_comparados":
                similarity
                .n_emisores_comparados,

            "estado":
                clean_text(
                    similarity
                    .estado_similitud
                ),

            "metodologia":
                clean_text(
                    similarity
                    .metodologia_similitud
                ),
        }

    # --------------------------------------------------------
    # RESPUESTA FINAL
    # --------------------------------------------------------

    return {
        "empresa": {
            "expediente_key":
                prospect.expediente_key,

            "ruc":
                clean_text(
                    prospect.ruc
                ),

            "nombre":
                clean_text(
                    prospect.nombre
                ),

            "anio":
                prospect.anio,

            "fecha_decision":
                prospect.fecha_decision,

            "tipo_compania":
                clean_text(
                    prospect.tipo_compania
                ),

            "provincia":
                clean_text(
                    prospect.provincia
                ),
        },

        "priorizacion": {
            "ranking":
                prospect.ranking,

            "score_afinidad":
                prospect.score_afinidad,

            "percentil_ranking":
                prospect.percentil_ranking,

            "nota": (
                "El score de afinidad es un indicador "
                "de priorización y no una probabilidad "
                "calibrada."
            ),
        },

        "calidad_datos": {
            "n_features_disponibles":
                prospect
                .n_features_disponibles,

            "pct_features_disponibles":
                prospect
                .pct_features_disponibles,
        },

        "indicadores_financieros": {
            "activos":
                prospect.activos_final,

            "patrimonio":
                prospect.patrimonio_final,

            "ingresos_ventas":
                prospect.bi_ingresos_ventas,

            "numero_empleados":
                prospect.bi_n_empleados,

            "ratio_patrimonio_activos":
                prospect
                .fin_ratio_patrimonio_activos,

            "roa":
                prospect.fin_roa,

            "margen_neto":
                prospect.fin_margen_neto,

            "rotacion_activos":
                prospect.fin_rotacion_activos,

            "roe":
                prospect.fin_roe,

            "crecimiento_activos":
                prospect.fin_crecimiento_activos,

            "crecimiento_patrimonio":
                prospect
                .fin_crecimiento_patrimonio,

            "crecimiento_ventas":
                prospect.fin_crecimiento_ventas,

            "crecimiento_empleados":
                prospect.fin_crecimiento_empleados,
        },

        "similitud_emisores": {
            **similarity_payload,

            "nota": (
                "La similitud con emisores históricos "
                "es un indicador independiente del score "
                "predictivo."
            ),

            "variables_comparacion": [
                "activos",
                "patrimonio",
                "ingresos_ventas",
                "numero_empleados",
                "ratio_patrimonio_activos",
                "roa",
                "rotacion_activos",
            ],

            "comparables":
                comparables,
        },

        "modelo": {
            "nombre":
                clean_text(
                    prospect.modelo
                ),

            "configuracion":
                clean_text(
                    prospect
                    .configuracion_modelo
                ),
        },
    }