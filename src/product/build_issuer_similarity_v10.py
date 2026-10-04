"""
Prospect Finder BVQ
Motor de similitud con emisores históricos - v10.

Objetivo
--------
Comparar empresas prospectables al corte 2024-05-01 con perfiles
históricos de empresas que ya eran emisores conocidos a esa fecha.

El motor de similitud es independiente del score predictivo v10.

Principios metodológicos
------------------------
1. No utiliza TARGET_24M para calcular similitud.
2. No utiliza emisores inscritos después del 2024-05-01 como referencia.
3. Cada emisor histórico se representa con su última observación
   disponible ANTES de su primera inscripción.
4. Las variables financieras se transforman a percentiles dentro
   de cada año para hacer comparables distintos periodos.
5. Solo se calculan comparables cuando las 7 variables seleccionadas
   están disponibles.
6. tipo_compania se conserva como contexto, pero NO modifica
   matemáticamente la distancia.
7. La similitud no se combina con score_afinidad mediante pesos
   arbitrarios.
8. El score v10 y la similitud con emisores son señales separadas.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors


# ============================================================
# CONFIGURACIÓN
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

FINANCIAL_DATA_PATH = (
    ROOT
    / "data"
    / "processed"
    / "v10_features_financial_2012_2023.csv.gz"
)

BASE_DATA_PATH = (
    ROOT
    / "data"
    / "processed"
    / "v10_base_integrated_2012_2023.csv.gz"
)

OPERATIONAL_RANKING_PATH = (
    ROOT
    / "data"
    / "processed"
    / "v10_operational_ranking_2024_05_01.csv.gz"
)

OUTPUT_DATA_DIR = (
    ROOT
    / "data"
    / "processed"
)

OUTPUT_REPORT_DIR = (
    ROOT
    / "reports"
    / "results"
    / "v10"
    / "product"
)

OUTPUT_SUMMARY = (
    OUTPUT_DATA_DIR
    / "v10_issuer_similarity_summary_2024_05_01.csv.gz"
)

OUTPUT_MATCHES = (
    OUTPUT_DATA_DIR
    / "v10_issuer_similarity_matches_2024_05_01.csv.gz"
)

OUTPUT_REFERENCE = (
    OUTPUT_REPORT_DIR
    / "v10_issuer_reference_profiles_2024_05_01.csv"
)

OUTPUT_TOP500 = (
    OUTPUT_REPORT_DIR
    / "v10_operational_top500_with_similarity_2024_05_01.csv"
)

OUTPUT_METADATA = (
    OUTPUT_REPORT_DIR
    / "v10_issuer_similarity_metadata.json"
)

DECISION_DATE = pd.Timestamp(
    "2024-05-01"
)

OPERATIONAL_YEAR = 2023

N_NEIGHBORS = 5


# ============================================================
# VARIABLES DEL MOTOR DE SIMILITUD
# ============================================================

SIMILARITY_FEATURES = [
    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",
    "fin_ratio_patrimonio_activos",
    "fin_roa",
    "fin_rotacion_activos",
]

CONTEXT_FEATURES = [
    "tipo_compania",
    "provincia",
]

IDENTIFICATION_COLUMNS = [
    "ANIO",
    "EXPEDIENTE_KEY",
    "RUC",
    "NOMBRE",
]

PERCENTILE_PREFIX = "pct__"


# ============================================================
# VALIDACIONES GENERALES
# ============================================================

def validar_archivos() -> None:
    """
    Comprueba que existan todos los archivos requeridos.
    """

    required = [
        FINANCIAL_DATA_PATH,
        BASE_DATA_PATH,
        OPERATIONAL_RANKING_PATH,
    ]

    missing = [
        path
        for path in required
        if not path.exists()
    ]

    if missing:
        text = "\n".join(
            str(path)
            for path in missing
        )

        raise FileNotFoundError(
            "Faltan archivos requeridos:\n"
            f"{text}"
        )


# ============================================================
# CARGA DE DATOS FINANCIEROS
# ============================================================

def cargar_datos_financieros() -> pd.DataFrame:
    """
    Carga las variables necesarias para construir
    percentiles históricos y operativos.
    """

    columns = list(
        dict.fromkeys(
            IDENTIFICATION_COLUMNS
            + SIMILARITY_FEATURES
            + CONTEXT_FEATURES
        )
    )

    dataframe = pd.read_csv(
        FINANCIAL_DATA_PATH,
        usecols=columns,
        dtype={
            "RUC": "string",
            "NOMBRE": "string",
            "tipo_compania": "string",
            "provincia": "string",
        },
        low_memory=False,
    )

    for variable in SIMILARITY_FEATURES:
        dataframe[
            variable
        ] = pd.to_numeric(
            dataframe[
                variable
            ],
            errors="coerce",
        )

    return dataframe


# ============================================================
# PERCENTILES ANUALES
# ============================================================

def calcular_percentiles_anuales(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transforma cada variable financiera en su posición
    percentil dentro del mismo año.

    Cada variable queda en escala [0, 1].

    Esto evita comparar directamente valores monetarios de
    diferentes periodos y reduce la influencia de outliers.
    """

    output = dataframe.copy()

    for variable in SIMILARITY_FEATURES:

        percentile_column = (
            PERCENTILE_PREFIX
            + variable
        )

        output[
            percentile_column
        ] = (
            output
            .groupby(
                "ANIO"
            )[
                variable
            ]
            .rank(
                method="average",
                pct=True,
                na_option="keep",
            )
        )

    return output


# ============================================================
# EMISORES HISTÓRICOS CONOCIDOS AL CORTE
# ============================================================

def construir_perfiles_emisores(
    financial_percentiles: pd.DataFrame,
) -> pd.DataFrame:
    """
    Construye un único perfil pre-emisión por cada empresa
    que YA era emisor conocido al 2024-05-01.

    Se selecciona la última fecha_decision estrictamente
    anterior a fecha_primera_inscripcion.
    """

    base = pd.read_csv(
        BASE_DATA_PATH,
        usecols=[
            "ANIO",
            "EXPEDIENTE_KEY",
            "fecha_decision",
            "fecha_primera_inscripcion",
        ],
        low_memory=False,
    )

    base[
        "fecha_decision"
    ] = pd.to_datetime(
        base[
            "fecha_decision"
        ],
        errors="coerce",
    )

    base[
        "fecha_primera_inscripcion"
    ] = pd.to_datetime(
        base[
            "fecha_primera_inscripcion"
        ],
        errors="coerce",
    )

    # --------------------------------------------------------
    # SOLO EMISORES CONOCIDOS AL CORTE
    # --------------------------------------------------------

    known_issuers = base.loc[
        base[
            "fecha_primera_inscripcion"
        ].notna()
        &
        (
            base[
                "fecha_primera_inscripcion"
            ]
            <= DECISION_DATE
        )
    ].copy()

    known_issuer_count = (
        known_issuers[
            "EXPEDIENTE_KEY"
        ]
        .nunique()
    )

    # --------------------------------------------------------
    # ÚNICAMENTE OBSERVACIONES PRE-EMISIÓN
    # --------------------------------------------------------

    pre_issuance = known_issuers.loc[
        known_issuers[
            "fecha_decision"
        ].notna()
        &
        (
            known_issuers[
                "fecha_decision"
            ]
            <
            known_issuers[
                "fecha_primera_inscripcion"
            ]
        )
    ].copy()

    # --------------------------------------------------------
    # ÚLTIMO PERFIL DISPONIBLE ANTES DE INSCRIPCIÓN
    # --------------------------------------------------------

    latest_pre_issuance = (
        pre_issuance
        .sort_values(
            [
                "EXPEDIENTE_KEY",
                "fecha_decision",
            ]
        )
        .groupby(
            "EXPEDIENTE_KEY",
            as_index=False,
        )
        .tail(
            1
        )
        .copy()
    )

    profile_columns = [
        "ANIO",
        "EXPEDIENTE_KEY",
        "fecha_decision",
        "fecha_primera_inscripcion",
    ]

    latest_pre_issuance = (
        latest_pre_issuance[
            profile_columns
        ]
        .copy()
    )

    # --------------------------------------------------------
    # JOIN CON VARIABLES + PERCENTILES
    # --------------------------------------------------------

    reference = (
        latest_pre_issuance
        .merge(
            financial_percentiles,
            on=[
                "ANIO",
                "EXPEDIENTE_KEY",
            ],
            how="left",
            validate="one_to_one",
        )
    )

    reference[
        "dias_hasta_inscripcion"
    ] = (
        reference[
            "fecha_primera_inscripcion"
        ]
        -
        reference[
            "fecha_decision"
        ]
    ).dt.days

    reference[
        "emisor_conocido_al_corte"
    ] = True

    reference.attrs[
        "known_issuer_count"
    ] = int(
        known_issuer_count
    )

    reference.attrs[
        "pre_issuance_profile_count"
    ] = int(
        len(
            latest_pre_issuance
        )
    )

    return reference


# ============================================================
# FILTRO DE COMPLETITUD
# ============================================================

def filtrar_perfiles_completos(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Conserva únicamente observaciones que tienen disponibles
    las siete variables financieras seleccionadas.
    """

    complete_mask = (
        dataframe[
            SIMILARITY_FEATURES
        ]
        .notna()
        .all(
            axis=1
        )
    )

    complete = dataframe.loc[
        complete_mask
    ].copy()

    return (
        complete,
        complete_mask,
    )


# ============================================================
# UNIVERSO OPERATIVO
# ============================================================

def construir_universo_operativo(
    financial_percentiles: pd.DataFrame,
) -> pd.DataFrame:
    """
    Obtiene el universo operativo exacto utilizado por
    el ranking v10 y le incorpora los percentiles 2023.
    """

    ranking = pd.read_csv(
        OPERATIONAL_RANKING_PATH,
        dtype={
            "RUC": "string",
            "NOMBRE": "string",
        },
        low_memory=False,
    )

    if ranking[
        "EXPEDIENTE_KEY"
    ].duplicated().any():
        raise ValueError(
            "El ranking operativo contiene "
            "EXPEDIENTE_KEY duplicados."
        )

    financial_2023 = (
        financial_percentiles.loc[
            financial_percentiles[
                "ANIO"
            ]
            == OPERATIONAL_YEAR
        ]
        .copy()
    )

    if financial_2023[
        "EXPEDIENTE_KEY"
    ].duplicated().any():
        raise ValueError(
            "El dataset financiero 2023 contiene "
            "EXPEDIENTE_KEY duplicados."
        )

    percentile_columns = [
        PERCENTILE_PREFIX
        + variable
        for variable in SIMILARITY_FEATURES
    ]

    columns_to_join = [
        "ANIO",
        "EXPEDIENTE_KEY",
        *SIMILARITY_FEATURES,
        *percentile_columns,
    ]

    # Algunas columnas financieras ya existen en ranking.
    # Solo agregamos percentiles y usamos las variables
    # originales del ranking para validar consistencia.
    join_columns = [
        "ANIO",
        "EXPEDIENTE_KEY",
        *percentile_columns,
    ]

    operational = (
        ranking
        .merge(
            financial_2023[
                join_columns
            ],
            on=[
                "ANIO",
                "EXPEDIENTE_KEY",
            ],
            how="left",
            validate="one_to_one",
        )
    )

    if len(
        operational
    ) != len(
        ranking
    ):
        raise ValueError(
            "El universo de similitud no coincide "
            "con el ranking operativo."
        )

    if operational[
        percentile_columns
    ].isna().all(
        axis=1
    ).any():
        missing_rows = int(
            operational[
                percentile_columns
            ]
            .isna()
            .all(
                axis=1
            )
            .sum()
        )

        raise ValueError(
            "Existen empresas sin ningún percentil "
            f"financiero: {missing_rows}"
        )

    return operational


# ============================================================
# MATRICES PARA NEAREST NEIGHBORS
# ============================================================

def obtener_columnas_percentiles() -> list[str]:
    """
    Devuelve las siete columnas transformadas a percentiles.
    """

    return [
        PERCENTILE_PREFIX
        + variable
        for variable in SIMILARITY_FEATURES
    ]


def validar_percentiles(
    dataframe: pd.DataFrame,
    name: str,
) -> None:
    """
    Verifica que todos los percentiles completos estén
    dentro del rango esperado [0, 1].
    """

    columns = (
        obtener_columnas_percentiles()
    )

    values = dataframe[
        columns
    ].to_numpy(
        dtype="float64"
    )

    if not np.isfinite(
        values
    ).all():
        raise ValueError(
            f"{name} contiene percentiles "
            "no finitos."
        )

    if (
        (values < 0).any()
        or (values > 1).any()
    ):
        raise ValueError(
            f"{name} contiene percentiles "
            "fuera del rango [0, 1]."
        )


# ============================================================
# CONVERSIÓN DISTANCIA -> SIMILITUD
# ============================================================

def convertir_distancia_a_similitud(
    distances: np.ndarray,
) -> np.ndarray:
    """
    Convierte distancia euclidiana sobre variables en [0,1]
    a una escala intuitiva de similitud 0-100.

    Distancia máxima teórica:
        sqrt(numero_de_variables)

    Similitud:
        100 * (1 - distancia / distancia_maxima)

    Finalmente se limita a [0,100].
    """

    max_distance = math.sqrt(
        len(
            SIMILARITY_FEATURES
        )
    )

    similarity = (
        1.0
        -
        (
            distances
            / max_distance
        )
    ) * 100.0

    similarity = np.clip(
        similarity,
        0.0,
        100.0,
    )

    return similarity


# ============================================================
# MOTOR DE SIMILITUD
# ============================================================

def calcular_similitud(
    operational_complete: pd.DataFrame,
    reference_complete: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Encuentra los cinco perfiles históricos de emisores
    más cercanos para cada empresa operacional elegible.
    """

    percentile_columns = (
        obtener_columnas_percentiles()
    )

    validar_percentiles(
        operational_complete,
        "Universo operativo",
    )

    validar_percentiles(
        reference_complete,
        "Referencia de emisores",
    )

    X_operational = (
        operational_complete[
            percentile_columns
        ]
        .to_numpy(
            dtype="float64"
        )
    )

    X_reference = (
        reference_complete[
            percentile_columns
        ]
        .to_numpy(
            dtype="float64"
        )
    )

    if len(
        reference_complete
    ) < N_NEIGHBORS:
        raise ValueError(
            "No existen suficientes perfiles históricos "
            "para calcular los vecinos solicitados."
        )

    print(
        "\nEntrenando índice de vecinos históricos..."
    )

    neighbors = NearestNeighbors(
        n_neighbors=N_NEIGHBORS,
        metric="euclidean",
        algorithm="brute",
        n_jobs=-1,
    )

    neighbors.fit(
        X_reference
    )

    print(
        "Buscando emisores históricos similares..."
    )

    distances, indices = (
        neighbors.kneighbors(
            X_operational,
            return_distance=True,
        )
    )

    similarities = (
        convertir_distancia_a_similitud(
            distances
        )
    )

    # --------------------------------------------------------
    # RESUMEN POR EMPRESA
    # --------------------------------------------------------

    summary = operational_complete[
        [
            "ranking",
            "score_afinidad",
            "percentil_ranking",
            "fecha_decision",
            "ANIO",
            "EXPEDIENTE_KEY",
            "RUC",
            "NOMBRE",
            "tipo_compania",
            "provincia",
            "pct_features_disponibles",
        ]
    ].copy()

    summary[
        "comparables_disponibles"
    ] = True

    summary[
        "similitud_emisor_top1"
    ] = similarities[
        :,
        0
    ]

    summary[
        "similitud_emisores_top5_promedio"
    ] = similarities.mean(
        axis=1
    )

    summary[
        "distancia_emisor_top1"
    ] = distances[
        :,
        0
    ]

    summary[
        "n_emisores_comparados"
    ] = N_NEIGHBORS

    # --------------------------------------------------------
    # TABLA LONG DE LOS 5 VECINOS
    # --------------------------------------------------------

    query_positions = np.repeat(
        np.arange(
            len(
                operational_complete
            )
        ),
        N_NEIGHBORS,
    )

    neighbor_order = np.tile(
        np.arange(
            1,
            N_NEIGHBORS
            + 1,
        ),
        len(
            operational_complete
        ),
    )

    reference_positions = (
        indices.reshape(
            -1
        )
    )

    flat_distances = (
        distances.reshape(
            -1
        )
    )

    flat_similarities = (
        similarities.reshape(
            -1
        )
    )

    query = (
        operational_complete
        .reset_index(
            drop=True
        )
        .iloc[
            query_positions
        ]
        .reset_index(
            drop=True
        )
    )

    reference = (
        reference_complete
        .reset_index(
            drop=True
        )
        .iloc[
            reference_positions
        ]
        .reset_index(
            drop=True
        )
    )

    matches = pd.DataFrame(
        {
            "EXPEDIENTE_KEY":
                query[
                    "EXPEDIENTE_KEY"
                ].to_numpy(),
            "RUC":
                query[
                    "RUC"
                ].to_numpy(),
            "NOMBRE":
                query[
                    "NOMBRE"
                ].to_numpy(),
            "ranking_v10":
                query[
                    "ranking"
                ].to_numpy(),
            "score_afinidad":
                query[
                    "score_afinidad"
                ].to_numpy(),
            "orden_comparable":
                neighbor_order,
            "similitud":
                flat_similarities,
            "distancia_percentiles":
                flat_distances,
            "emisor_EXPEDIENTE_KEY":
                reference[
                    "EXPEDIENTE_KEY"
                ].to_numpy(),
            "emisor_RUC":
                reference[
                    "RUC"
                ].to_numpy(),
            "emisor_NOMBRE":
                reference[
                    "NOMBRE"
                ].to_numpy(),
            "emisor_ANIO_perfil":
                reference[
                    "ANIO"
                ].to_numpy(),
            "emisor_fecha_decision_perfil":
                reference[
                    "fecha_decision"
                ]
                .dt.date
                .astype(
                    "string"
                )
                .to_numpy(),
            "emisor_fecha_primera_inscripcion":
                reference[
                    "fecha_primera_inscripcion"
                ]
                .dt.date
                .astype(
                    "string"
                )
                .to_numpy(),
            "emisor_tipo_compania":
                reference[
                    "tipo_compania"
                ].to_numpy(),
            "emisor_provincia":
                reference[
                    "provincia"
                ].to_numpy(),
        }
    )

    matches[
        "mismo_tipo_compania"
    ] = (
        query[
            "tipo_compania"
        ]
        .astype(
            "string"
        )
        .fillna(
            ""
        )
        .to_numpy()
        ==
        reference[
            "tipo_compania"
        ]
        .astype(
            "string"
        )
        .fillna(
            ""
        )
        .to_numpy()
    )

    return (
        summary,
        matches,
    )


# ============================================================
# RESUMEN PARA EMPRESAS SIN COMPARABLES
# ============================================================

def construir_resumen_completo(
    operational: pd.DataFrame,
    similarity_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Devuelve una fila para TODAS las empresas del ranking.

    Las empresas sin las 7 variables completas permanecen
    en el producto, pero con estado de similitud no disponible.
    """

    base_columns = [
        "ranking",
        "score_afinidad",
        "percentil_ranking",
        "fecha_decision",
        "ANIO",
        "EXPEDIENTE_KEY",
        "RUC",
        "NOMBRE",
        "tipo_compania",
        "provincia",
        "pct_features_disponibles",
    ]

    base = operational[
        base_columns
    ].copy()

    similarity_columns = [
        "EXPEDIENTE_KEY",
        "comparables_disponibles",
        "similitud_emisor_top1",
        "similitud_emisores_top5_promedio",
        "distancia_emisor_top1",
        "n_emisores_comparados",
    ]

    output = (
        base
        .merge(
            similarity_summary[
                similarity_columns
            ],
            on="EXPEDIENTE_KEY",
            how="left",
            validate="one_to_one",
        )
    )

    output[
        "comparables_disponibles"
    ] = (
        output[
            "comparables_disponibles"
        ]
        .fillna(
            False
        )
        .astype(
            bool
        )
    )

    output[
        "estado_similitud"
    ] = np.where(
        output[
            "comparables_disponibles"
        ],
        "DISPONIBLE",
        "INFORMACION_INSUFICIENTE",
    )

    output[
        "metodologia_similitud"
    ] = (
        "Distancia euclidiana sobre "
        "7 percentiles financieros anuales"
    )

    return (
        output
        .sort_values(
            "ranking"
        )
        .reset_index(
            drop=True
        )
    )


# ============================================================
# EXPORTACIÓN DE PERFILES DE REFERENCIA
# ============================================================

def preparar_referencia_exportable(
    reference_complete: pd.DataFrame,
) -> pd.DataFrame:
    """
    Selecciona campos útiles para auditoría metodológica.
    """

    percentile_columns = (
        obtener_columnas_percentiles()
    )

    columns = [
        "ANIO",
        "EXPEDIENTE_KEY",
        "RUC",
        "NOMBRE",
        "tipo_compania",
        "provincia",
        "fecha_decision",
        "fecha_primera_inscripcion",
        "dias_hasta_inscripcion",
        *SIMILARITY_FEATURES,
        *percentile_columns,
    ]

    output = reference_complete[
        columns
    ].copy()

    output[
        "fecha_decision"
    ] = (
        output[
            "fecha_decision"
        ]
        .dt.date
        .astype(
            "string"
        )
    )

    output[
        "fecha_primera_inscripcion"
    ] = (
        output[
            "fecha_primera_inscripcion"
        ]
        .dt.date
        .astype(
            "string"
        )
    )

    return output


# ============================================================
# MAIN
# ============================================================

def construir_motor_similitud() -> None:
    """
    Ejecuta el flujo completo.
    """

    print(
        "\n"
        "================================================="
    )
    print(
        "PROSPECT FINDER BVQ"
    )
    print(
        "Motor de similitud con emisores históricos"
    )
    print(
        "=================================================\n"
    )

    validar_archivos()

    OUTPUT_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # DATOS FINANCIEROS Y PERCENTILES
    # --------------------------------------------------------

    print(
        "Cargando datos financieros..."
    )

    financial = (
        cargar_datos_financieros()
    )

    print(
        f"Filas históricas cargadas: "
        f"{len(financial):,}"
    )

    print(
        "\nCalculando percentiles dentro de cada año..."
    )

    financial_percentiles = (
        calcular_percentiles_anuales(
            financial
        )
    )

    # --------------------------------------------------------
    # REFERENCIA DE EMISORES CONOCIDOS AL CORTE
    # --------------------------------------------------------

    print(
        "\nConstruyendo perfiles históricos "
        "pre-emisión..."
    )

    reference = (
        construir_perfiles_emisores(
            financial_percentiles
        )
    )

    known_issuer_count = int(
        reference.attrs[
            "known_issuer_count"
        ]
    )

    pre_profile_count = int(
        reference.attrs[
            "pre_issuance_profile_count"
        ]
    )

    print(
        "Emisores conocidos al corte: "
        f"{known_issuer_count:,}"
    )

    print(
        "Emisores con perfil pre-emisión: "
        f"{pre_profile_count:,}"
    )

    (
        reference_complete,
        reference_complete_mask,
    ) = filtrar_perfiles_completos(
        reference
    )

    print(
        "Perfiles históricos completos "
        f"(7/7 variables): "
        f"{len(reference_complete):,}"
    )

    reference_incomplete = (
        len(
            reference
        )
        -
        len(
            reference_complete
        )
    )

    print(
        "Perfiles históricos excluidos por "
        "información insuficiente: "
        f"{reference_incomplete:,}"
    )

    if reference_complete.empty:
        raise ValueError(
            "No existen perfiles históricos completos."
        )

    # --------------------------------------------------------
    # UNIVERSO OPERATIVO
    # --------------------------------------------------------

    print(
        "\nConstruyendo universo operativo..."
    )

    operational = (
        construir_universo_operativo(
            financial_percentiles
        )
    )

    print(
        f"Universo operativo total: "
        f"{len(operational):,}"
    )

    (
        operational_complete,
        operational_complete_mask,
    ) = filtrar_perfiles_completos(
        operational
    )

    print(
        "Empresas con información suficiente "
        f"(7/7 variables): "
        f"{len(operational_complete):,}"
    )

    operational_incomplete = (
        len(
            operational
        )
        -
        len(
            operational_complete
        )
    )

    print(
        "Empresas sin comparables por "
        "información insuficiente: "
        f"{operational_incomplete:,}"
    )

    # --------------------------------------------------------
    # SIMILITUD
    # --------------------------------------------------------

    (
        similarity_summary,
        similarity_matches,
    ) = calcular_similitud(
        operational_complete,
        reference_complete,
    )

    # --------------------------------------------------------
    # RESUMEN PARA TODO EL UNIVERSO
    # --------------------------------------------------------

    full_summary = (
        construir_resumen_completo(
            operational,
            similarity_summary,
        )
    )

    # --------------------------------------------------------
    # VALIDACIONES
    # --------------------------------------------------------

    if len(
        full_summary
    ) != len(
        operational
    ):
        raise ValueError(
            "El resumen final no conserva "
            "todo el universo operativo."
        )

    if full_summary[
        "EXPEDIENTE_KEY"
    ].duplicated().any():
        raise ValueError(
            "El resumen contiene empresas duplicadas."
        )

    expected_matches = (
        len(
            operational_complete
        )
        * N_NEIGHBORS
    )

    if len(
        similarity_matches
    ) != expected_matches:
        raise ValueError(
            "Cantidad inesperada de comparables. "
            f"Esperado: {expected_matches:,}; "
            f"obtenido: {len(similarity_matches):,}"
        )

    if (
        similarity_matches[
            "similitud"
        ].lt(
            0
        ).any()
        or
        similarity_matches[
            "similitud"
        ].gt(
            100
        ).any()
    ):
        raise ValueError(
            "Existen similitudes fuera "
            "del rango [0,100]."
        )

    # --------------------------------------------------------
    # EXPORTACIONES
    # --------------------------------------------------------

    print(
        "\nExportando resultados..."
    )

    full_summary.to_csv(
        OUTPUT_SUMMARY,
        index=False,
        compression="gzip",
    )

    similarity_matches.to_csv(
        OUTPUT_MATCHES,
        index=False,
        compression="gzip",
    )

    reference_export = (
        preparar_referencia_exportable(
            reference_complete
        )
    )

    reference_export.to_csv(
        OUTPUT_REFERENCE,
        index=False,
    )

    full_summary.head(
        500
    ).to_csv(
        OUTPUT_TOP500,
        index=False,
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    similarities_available = (
        full_summary.loc[
            full_summary[
                "comparables_disponibles"
            ],
            "similitud_emisor_top1",
        ]
    )

    metadata = {
        "decision_date":
            DECISION_DATE.date().isoformat(),
        "operational_financial_year":
            OPERATIONAL_YEAR,
        "method":
            (
                "Nearest Neighbors con distancia "
                "euclidiana sobre percentiles anuales"
            ),
        "similarity_scale":
            "0-100",
        "similarity_formula":
            (
                "100 * "
                "(1 - distancia_euclidiana / sqrt(7))"
            ),
        "number_of_neighbors":
            N_NEIGHBORS,
        "features":
            SIMILARITY_FEATURES,
        "feature_transformation":
            (
                "Percentil anual individual por variable, "
                "escala 0-1"
            ),
        "company_type_used_in_distance":
            False,
        "province_used_in_distance":
            False,
        "target_used_in_similarity":
            False,
        "future_issuers_used_as_reference":
            False,
        "known_issuers_at_cutoff":
            known_issuer_count,
        "issuers_with_pre_issuance_profile":
            pre_profile_count,
        "complete_reference_profiles":
            int(
                len(
                    reference_complete
                )
            ),
        "incomplete_reference_profiles":
            int(
                reference_incomplete
            ),
        "operational_universe":
            int(
                len(
                    operational
                )
            ),
        "operational_with_similarity":
            int(
                len(
                    operational_complete
                )
            ),
        "operational_without_similarity":
            int(
                operational_incomplete
            ),
        "number_of_match_rows":
            int(
                len(
                    similarity_matches
                )
            ),
        "top1_similarity_min":
            float(
                similarities_available.min()
            ),
        "top1_similarity_max":
            float(
                similarities_available.max()
            ),
        "top1_similarity_mean":
            float(
                similarities_available.mean()
            ),
        "top1_similarity_median":
            float(
                similarities_available.median()
            ),
        "interpretation":
            (
                "La similitud describe parecido financiero "
                "relativo con perfiles históricos de emisores. "
                "No es una probabilidad de emisión y no se "
                "combina matemáticamente con score_afinidad."
            ),
    }

    with open(
        OUTPUT_METADATA,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2,
        )

    # --------------------------------------------------------
    # RESUMEN EN CONSOLA
    # --------------------------------------------------------

    print(
        "\n"
        "================================================="
    )
    print(
        "MOTOR DE SIMILITUD GENERADO CORRECTAMENTE"
    )
    print(
        "================================================="
    )

    print(
        f"\nEmisores conocidos al corte: "
        f"{known_issuer_count:,}"
    )

    print(
        "Referencias completas utilizadas: "
        f"{len(reference_complete):,}"
    )

    print(
        "Empresas operativas: "
        f"{len(operational):,}"
    )

    print(
        "Empresas con comparables: "
        f"{len(operational_complete):,}"
    )

    print(
        "Empresas sin comparables: "
        f"{operational_incomplete:,}"
    )

    print(
        "Filas de comparables generadas: "
        f"{len(similarity_matches):,}"
    )

    print(
        "\nSimilitud Top 1:"
    )

    print(
        "  mínimo : "
        f"{similarities_available.min():.4f}"
    )

    print(
        "  máximo : "
        f"{similarities_available.max():.4f}"
    )

    print(
        "  promedio: "
        f"{similarities_available.mean():.4f}"
    )

    print(
        "  mediana : "
        f"{similarities_available.median():.4f}"
    )

    print(
        "\nTop 10 del ranking con similitud:"
    )

    print(
        full_summary[
            [
                "ranking",
                "EXPEDIENTE_KEY",
                "NOMBRE",
                "score_afinidad",
                "similitud_emisor_top1",
                "similitud_emisores_top5_promedio",
                "estado_similitud",
            ]
        ]
        .head(
            10
        )
        .to_string(
            index=False
        )
    )

    print(
        "\nArchivos generados:"
    )

    print(
        OUTPUT_SUMMARY
    )

    print(
        OUTPUT_MATCHES
    )

    print(
        OUTPUT_REFERENCE
    )

    print(
        OUTPUT_TOP500
    )

    print(
        OUTPUT_METADATA
    )

    print(
        "\nIMPORTANTE:"
    )

    print(
        "score_afinidad y similitud_emisor "
        "son indicadores independientes."
    )

    print(
        "No se ha creado una fórmula ponderada "
        "entre ambos."
    )


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    construir_motor_similitud()