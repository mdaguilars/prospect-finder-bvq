from __future__ import annotations

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
)


# =============================================================================
# CONFIGURACIÓN
# =============================================================================

EXPECTED_TEST_N = 260_445
EXPECTED_TEST_POSITIVES = 54
EXPECTED_TEST_PR_AUC = 0.007468801
EXPECTED_TEST_ROC_AUC = 0.934603901

EXPECTED_MODEL_NAME = "v10_hgb_financial_c3"
EXPECTED_CONFIG_ID = "C3_CONSERVATIVE"

METRIC_TOLERANCE = 1e-6

TOP_K_VALUES = [
    50,
    100,
    200,
]

MIN_GROUP_SIZE_FOR_INTERPRETATION = 100

ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    ROOT
    / "data"
    / "processed"
    / "v10_features_financial_2012_2023.csv.gz"
)

MODEL_PATH = (
    ROOT
    / "models"
    / "v10"
    / "v10_hgb_financial_c3_final.joblib"
)

OUTPUT_DIR = (
    ROOT
    / "reports"
    / "results"
    / "v10"
    / "bias_risk"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_GROUP_SUMMARY = (
    OUTPUT_DIR
    / "v10_bias_group_summary.csv"
)

OUT_TOPK_EXPOSURE = (
    OUTPUT_DIR
    / "v10_bias_topk_exposure.csv"
)

OUT_RISK_REGISTER = (
    OUTPUT_DIR
    / "v10_bias_risk_register.csv"
)

OUT_METADATA = (
    OUTPUT_DIR
    / "v10_bias_risk_metadata.json"
)


# =============================================================================
# FEATURES
# =============================================================================

NUMERIC_CORE = [
    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",
    "activos_final_t1",
    "patrimonio_final_t1",
    "bi_ingresos_ventas_t1",
    "bi_n_empleados_t1",
]

BOOLEAN_CORE = [
    "TIENE_T_MENOS_1",
    "flag_activos_negativos",
    "flag_ventas_negativas",
    "flag_empleados_fijo",
    "flag_empleados_salto_temporal",
    "flag_empleados_anomalia_total",
]

FINANCIAL_NUMERIC = [
    "fin_ratio_patrimonio_activos",
    "fin_roa",
    "fin_margen_neto",
    "fin_rotacion_activos",
    "fin_roe",
    "fin_crecimiento_activos",
    "fin_crecimiento_patrimonio",
    "fin_crecimiento_ventas",
    "fin_crecimiento_empleados",
]

FINANCIAL_BOOLEAN = [
    "flag_patrimonio_no_positivo",
]

CATEGORICAL = [
    "tipo_compania",
]

NUMERIC_FEATURES = (
    NUMERIC_CORE
    + FINANCIAL_NUMERIC
)

BOOLEAN_FEATURES = (
    BOOLEAN_CORE
    + FINANCIAL_BOOLEAN
)

FEATURES = (
    NUMERIC_FEATURES
    + BOOLEAN_FEATURES
    + CATEGORICAL
)

TARGET = "TARGET_24M"


# =============================================================================
# UTILIDADES
# =============================================================================

def print_header(
    title: str,
) -> None:

    line = "=" * 120

    print()
    print(line)
    print(title)
    print(line)


def normalize_boolean(
    series: pd.Series,
) -> pd.Series:

    if pd.api.types.is_bool_dtype(
        series.dtype
    ):
        return series.astype(
            "float64"
        )

    if pd.api.types.is_numeric_dtype(
        series.dtype
    ):

        numeric = pd.to_numeric(
            series,
            errors="coerce",
        )

        numeric = numeric.where(
            numeric.isin(
                [0, 1]
            ),
            np.nan,
        )

        return numeric.astype(
            "float64"
        )

    normalized = (
        series
        .astype("string")
        .str.strip()
        .str.lower()
    )

    mapping = {
        "true": 1.0,
        "false": 0.0,
        "1": 1.0,
        "0": 0.0,
        "si": 1.0,
        "sí": 1.0,
        "yes": 1.0,
        "no": 0.0,
    }

    return (
        normalized
        .map(mapping)
        .astype("float64")
    )


def safe_ratio(
    numerator: float,
    denominator: float,
) -> float:

    if denominator == 0:
        return np.nan

    return float(
        numerator
        / denominator
    )


# =============================================================================
# ARTEFACTO FINAL
# =============================================================================

def load_final_artifact():

    artifact = joblib.load(
        MODEL_PATH
    )

    if not isinstance(
        artifact,
        dict,
    ):
        raise RuntimeError(
            "El artefacto final v10 no tiene "
            "la estructura esperada."
        )

    if "model" not in artifact:
        raise RuntimeError(
            "El artefacto no contiene "
            "la clave 'model'."
        )

    model = artifact[
        "model"
    ]

    if not hasattr(
        model,
        "predict_proba",
    ):
        raise RuntimeError(
            "El estimador almacenado no "
            "implementa predict_proba."
        )

    return (
        artifact,
        model,
    )


def validate_artifact(
    artifact: dict,
) -> None:

    model_name = artifact.get(
        "model_name"
    )

    config_id = artifact.get(
        "config_id"
    )

    target = artifact.get(
        "target"
    )

    artifact_features = artifact.get(
        "features"
    )

    print(
        f"Modelo:        {model_name}"
    )

    print(
        f"Configuración: {config_id}"
    )

    print(
        f"Target:        {target}"
    )

    print(
        f"Features:      "
        f"{len(artifact_features) if artifact_features is not None else 'N/D'}"
    )

    if model_name != EXPECTED_MODEL_NAME:

        raise RuntimeError(
            "El modelo del artefacto no coincide "
            "con v10_hgb_financial_c3."
        )

    if config_id != EXPECTED_CONFIG_ID:

        raise RuntimeError(
            "La configuración del artefacto "
            "no coincide con C3_CONSERVATIVE."
        )

    if target != TARGET:

        raise RuntimeError(
            "El target del artefacto no coincide "
            "con TARGET_24M."
        )

    if artifact_features is None:

        raise RuntimeError(
            "El artefacto no contiene features."
        )

    if list(
        artifact_features
    ) != FEATURES:

        raise RuntimeError(
            "Las features del artefacto no "
            "coinciden con este análisis."
        )


# =============================================================================
# CATEGORÍAS DE TRAIN
# =============================================================================

def load_train_categories() -> list[str]:

    categories: set[str] = set()

    for chunk in pd.read_csv(
        DATA_PATH,
        usecols=[
            "SPLIT",
            "tipo_compania",
        ],
        chunksize=200_000,
        low_memory=False,
    ):

        train_chunk = chunk.loc[
            chunk["SPLIT"].eq(
                "TRAIN"
            ),
            "tipo_compania",
        ]

        train_chunk = (
            train_chunk
            .dropna()
            .astype("string")
        )

        if not train_chunk.empty:

            categories.update(
                train_chunk.tolist()
            )

    return sorted(
        categories
    )


# =============================================================================
# CARGA TEST
# =============================================================================

def load_test(
    train_categories: list[str],
) -> pd.DataFrame:

    usecols = [
        "ANIO",
        "EXPEDIENTE_KEY",
        "provincia",
        TARGET,
        "SPLIT",
    ] + FEATURES

    frames = []

    for chunk in pd.read_csv(
        DATA_PATH,
        usecols=usecols,
        chunksize=200_000,
        low_memory=False,
    ):

        test_chunk = chunk.loc[
            chunk["SPLIT"].eq(
                "TEST"
            )
        ].copy()

        if not test_chunk.empty:

            frames.append(
                test_chunk
            )

    if not frames:

        raise RuntimeError(
            "No se encontraron filas TEST."
        )

    df = pd.concat(
        frames,
        ignore_index=True,
    )

    df["ANIO"] = (
        pd.to_numeric(
            df["ANIO"],
            errors="raise",
        )
        .astype(
            "int64"
        )
    )

    df[TARGET] = (
        pd.to_numeric(
            df[TARGET],
            errors="raise",
        )
        .astype(
            "int8"
        )
    )

    for col in NUMERIC_FEATURES:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        )

        df[col] = (
            df[col]
            .replace(
                [
                    np.inf,
                    -np.inf,
                ],
                np.nan,
            )
            .astype(
                "float64"
            )
        )

    for col in BOOLEAN_FEATURES:

        df[col] = normalize_boolean(
            df[col]
        )

    tipo = (
        df[
            "tipo_compania"
        ]
        .astype(
            "string"
        )
    )

    df[
        "tipo_compania"
    ] = pd.Categorical(
        tipo,
        categories=train_categories,
    )

    df[
        "provincia"
    ] = (
        df[
            "provincia"
        ]
        .astype(
            "string"
        )
    )

    return df


# =============================================================================
# VALIDACIONES
# =============================================================================

def validate_test_universe(
    df: pd.DataFrame,
) -> None:

    n = len(
        df
    )

    positives = int(
        df[
            TARGET
        ].sum()
    )

    years = sorted(
        df[
            "ANIO"
        ]
        .unique()
        .tolist()
    )

    print(
        f"TEST: {n:,} filas | "
        f"{positives} positivos | "
        f"años={years}"
    )

    if n != EXPECTED_TEST_N:

        raise RuntimeError(
            "El tamaño de TEST no coincide "
            "con el universo congelado."
        )

    if positives != EXPECTED_TEST_POSITIVES:

        raise RuntimeError(
            "Los positivos de TEST no coinciden "
            "con el universo congelado."
        )

    if years != [
        2022,
        2023,
    ]:

        raise RuntimeError(
            "TEST no contiene exclusivamente "
            "2022 y 2023."
        )


def validate_official_metrics(
    y_true: pd.Series,
    scores: np.ndarray,
) -> tuple[float, float]:

    pr_auc = float(
        average_precision_score(
            y_true,
            scores,
        )
    )

    roc_auc = float(
        roc_auc_score(
            y_true,
            scores,
        )
    )

    print(
        f"PR-AUC reproducida:  "
        f"{pr_auc:.9f}"
    )

    print(
        f"ROC-AUC reproducida: "
        f"{roc_auc:.9f}"
    )

    if not np.isclose(
        pr_auc,
        EXPECTED_TEST_PR_AUC,
        atol=METRIC_TOLERANCE,
        rtol=0,
    ):

        raise RuntimeError(
            "PR-AUC no coincide con "
            "la evaluación oficial."
        )

    if not np.isclose(
        roc_auc,
        EXPECTED_TEST_ROC_AUC,
        atol=METRIC_TOLERANCE,
        rtol=0,
    ):

        raise RuntimeError(
            "ROC-AUC no coincide con "
            "la evaluación oficial."
        )

    return (
        pr_auc,
        roc_auc,
    )


# =============================================================================
# VARIABLES DE AUDITORÍA
# =============================================================================

def add_audit_groups(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    # -------------------------------------------------------------------------
    # DISPONIBILIDAD HISTÓRICA
    # -------------------------------------------------------------------------

    history = result[
        "TIENE_T_MENOS_1"
    ]

    result[
        "AUDIT_HISTORY"
    ] = np.select(
        [
            history.eq(
                1
            ),
            history.eq(
                0
            ),
        ],
        [
            "CON_HISTORIA",
            "SIN_HISTORIA",
        ],
        default="MISSING",
    )

    # -------------------------------------------------------------------------
    # TAMAÑO POR ACTIVOS
    # -------------------------------------------------------------------------

    result[
        "AUDIT_ASSET_SIZE"
    ] = "MISSING"

    valid_assets = result[
        "activos_final"
    ].notna()

    if valid_assets.any():

        bins = pd.qcut(
            result.loc[
                valid_assets,
                "activos_final",
            ],
            q=5,
            labels=False,
            duplicates="drop",
        )

        result.loc[
            valid_assets,
            "AUDIT_ASSET_SIZE",
        ] = (
            bins
            .astype(
                "int64"
            )
            .add(
                1
            )
            .map(
                lambda x: (
                    f"Q{x}"
                )
            )
        )

    # -------------------------------------------------------------------------
    # PATRIMONIO
    # -------------------------------------------------------------------------

    patrimonio_flag = result[
        "flag_patrimonio_no_positivo"
    ]

    result[
        "AUDIT_PATRIMONY"
    ] = np.select(
        [
            patrimonio_flag.eq(
                0
            ),
            patrimonio_flag.eq(
                1
            ),
        ],
        [
            "PATRIMONIO_POSITIVO",
            "PATRIMONIO_NO_POSITIVO",
        ],
        default="MISSING",
    )

    # -------------------------------------------------------------------------
    # CARGA DE MISSING
    # -------------------------------------------------------------------------

    result[
        "AUDIT_MISSING_COUNT"
    ] = (
        result[
            FEATURES
        ]
        .isna()
        .sum(
            axis=1
        )
    )

    result[
        "AUDIT_MISSINGNESS"
    ] = pd.cut(
        result[
            "AUDIT_MISSING_COUNT"
        ],
        bins=[
            -1,
            0,
            2,
            5,
            np.inf,
        ],
        labels=[
            "0_MISSING",
            "1_2_MISSING",
            "3_5_MISSING",
            "6_PLUS_MISSING",
        ],
    ).astype(
        "string"
    )

    # -------------------------------------------------------------------------
    # TIPO DE COMPAÑÍA
    # -------------------------------------------------------------------------

    result[
        "AUDIT_COMPANY_TYPE"
    ] = (
        result[
            "tipo_compania"
        ]
        .astype(
            "string"
        )
        .fillna(
            "MISSING"
        )
    )

    # -------------------------------------------------------------------------
    # PROVINCIA
    #
    # Provincia NO fue utilizada como predictor del modelo seleccionado.
    # Se audita para detectar posibles concentraciones indirectas.
    # -------------------------------------------------------------------------

    result[
        "AUDIT_PROVINCE"
    ] = (
        result[
            "provincia"
        ]
        .astype(
            "string"
        )
        .fillna(
            "MISSING"
        )
    )

    return result


# =============================================================================
# RESUMEN DE GRUPOS
# =============================================================================

def calculate_group_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:

    group_definitions = {
        "ASSET_SIZE": (
            "AUDIT_ASSET_SIZE"
        ),
        "HISTORY_AVAILABILITY": (
            "AUDIT_HISTORY"
        ),
        "PATRIMONY_STATUS": (
            "AUDIT_PATRIMONY"
        ),
        "MISSINGNESS": (
            "AUDIT_MISSINGNESS"
        ),
        "COMPANY_TYPE": (
            "AUDIT_COMPANY_TYPE"
        ),
        "PROVINCE": (
            "AUDIT_PROVINCE"
        ),
    }

    total_n = len(
        df
    )

    total_positive = int(
        df[
            TARGET
        ].sum()
    )

    rows = []

    for (
        dimension,
        group_col,
    ) in group_definitions.items():

        for (
            group_value,
            group,
        ) in df.groupby(
            group_col,
            dropna=False,
        ):

            n = len(
                group
            )

            positives = int(
                group[
                    TARGET
                ].sum()
            )

            rows.append(
                {
                    "DIMENSION": (
                        dimension
                    ),
                    "GROUP": str(
                        group_value
                    ),
                    "N": int(
                        n
                    ),
                    "POPULATION_SHARE": safe_ratio(
                        n,
                        total_n,
                    ),
                    "POSITIVES": (
                        positives
                    ),
                    "POSITIVE_SHARE": safe_ratio(
                        positives,
                        total_positive,
                    ),
                    "PREVALENCE": float(
                        group[
                            TARGET
                        ].mean()
                    ),
                    "SCORE_MEAN": float(
                        group[
                            "SCORE"
                        ].mean()
                    ),
                    "SCORE_MEDIAN": float(
                        group[
                            "SCORE"
                        ].median()
                    ),
                    "SMALL_GROUP": bool(
                        n
                        < MIN_GROUP_SIZE_FOR_INTERPRETATION
                    ),
                }
            )

    result = pd.DataFrame(
        rows
    )

    return (
        result
        .sort_values(
            [
                "DIMENSION",
                "N",
            ],
            ascending=[
                True,
                False,
            ],
        )
        .reset_index(
            drop=True
        )
    )


# =============================================================================
# EXPOSICIÓN TOP K
# =============================================================================

def calculate_topk_exposure(
    df: pd.DataFrame,
) -> pd.DataFrame:

    group_definitions = {
        "ASSET_SIZE": (
            "AUDIT_ASSET_SIZE"
        ),
        "HISTORY_AVAILABILITY": (
            "AUDIT_HISTORY"
        ),
        "PATRIMONY_STATUS": (
            "AUDIT_PATRIMONY"
        ),
        "MISSINGNESS": (
            "AUDIT_MISSINGNESS"
        ),
        "COMPANY_TYPE": (
            "AUDIT_COMPANY_TYPE"
        ),
        "PROVINCE": (
            "AUDIT_PROVINCE"
        ),
    }

    ranked = df.copy()

    ranked[
        "EXPEDIENTE_SORT"
    ] = (
        ranked[
            "EXPEDIENTE_KEY"
        ]
        .astype(
            "string"
        )
    )

    ranked = (
        ranked
        .sort_values(
            [
                "SCORE",
                "ANIO",
                "EXPEDIENTE_SORT",
            ],
            ascending=[
                False,
                True,
                True,
            ],
            kind="mergesort",
        )
        .reset_index(
            drop=True
        )
    )

    total_n = len(
        ranked
    )

    rows = []

    for (
        dimension,
        group_col,
    ) in group_definitions.items():

        population_counts = (
            ranked[
                group_col
            ]
            .astype(
                "string"
            )
            .fillna(
                "MISSING"
            )
            .value_counts(
                dropna=False
            )
        )

        all_groups = (
            population_counts
            .index
            .tolist()
        )

        for k in TOP_K_VALUES:

            effective_k = min(
                k,
                total_n,
            )

            top = ranked.head(
                effective_k
            )

            for group_value in all_groups:

                population_n = int(
                    population_counts.loc[
                        group_value
                    ]
                )

                population_share = safe_ratio(
                    population_n,
                    total_n,
                )

                group_mask_top = (
                    top[
                        group_col
                    ]
                    .astype(
                        "string"
                    )
                    .fillna(
                        "MISSING"
                    )
                    .eq(
                        group_value
                    )
                )

                selected_n = int(
                    group_mask_top.sum()
                )

                top_share = safe_ratio(
                    selected_n,
                    effective_k,
                )

                exposure_ratio = (
                    safe_ratio(
                        top_share,
                        population_share,
                    )
                    if not pd.isna(
                        population_share
                    )
                    and population_share > 0
                    else np.nan
                )

                positives_total_group = int(
                    ranked.loc[
                        ranked[
                            group_col
                        ]
                        .astype(
                            "string"
                        )
                        .fillna(
                            "MISSING"
                        )
                        .eq(
                            group_value
                        ),
                        TARGET,
                    ].sum()
                )

                positives_top_group = int(
                    top.loc[
                        group_mask_top,
                        TARGET,
                    ].sum()
                )

                positive_capture = (
                    safe_ratio(
                        positives_top_group,
                        positives_total_group,
                    )
                    if positives_total_group > 0
                    else np.nan
                )

                rows.append(
                    {
                        "DIMENSION": (
                            dimension
                        ),
                        "GROUP": str(
                            group_value
                        ),
                        "K": int(
                            k
                        ),
                        "POPULATION_N": (
                            population_n
                        ),
                        "POPULATION_SHARE": (
                            population_share
                        ),
                        "SELECTED_N": (
                            selected_n
                        ),
                        "TOP_K_SHARE": (
                            top_share
                        ),
                        "EXPOSURE_RATIO": (
                            exposure_ratio
                        ),
                        "GROUP_SELECTION_RATE": safe_ratio(
                            selected_n,
                            population_n,
                        ),
                        "POSITIVES_GROUP": (
                            positives_total_group
                        ),
                        "POSITIVES_TOP_K_GROUP": (
                            positives_top_group
                        ),
                        "POSITIVE_CAPTURE_WITHIN_GROUP": (
                            positive_capture
                        ),
                        "SMALL_GROUP": bool(
                            population_n
                            < MIN_GROUP_SIZE_FOR_INTERPRETATION
                        ),
                    }
                )

    return pd.DataFrame(
        rows
    )


# =============================================================================
# REGISTRO DE RIESGOS
# =============================================================================

def build_risk_register(
    df: pd.DataFrame,
    group_summary: pd.DataFrame,
    topk_exposure: pd.DataFrame,
) -> pd.DataFrame:

    risks = []

    # -------------------------------------------------------------------------
    # R1 - CONCENTRACIÓN POR TAMAÑO
    # -------------------------------------------------------------------------

    size_top200 = topk_exposure.loc[
        (
            topk_exposure[
                "DIMENSION"
            ].eq(
                "ASSET_SIZE"
            )
        )
        & (
            topk_exposure[
                "K"
            ].eq(
                200
            )
        )
        & (
            topk_exposure[
                "GROUP"
            ].eq(
                "Q5"
            )
        )
    ]

    if not size_top200.empty:

        exposure = float(
            size_top200[
                "EXPOSURE_RATIO"
            ].iloc[
                0
            ]
        )

        top_share = float(
            size_top200[
                "TOP_K_SHARE"
            ].iloc[
                0
            ]
        )

    else:

        exposure = np.nan
        top_share = np.nan

    risks.append(
        {
            "RISK_ID": (
                "R1"
            ),
            "RISK": (
                "Concentración por tamaño empresarial"
            ),
            "CATEGORY": (
                "Representación / uso"
            ),
            "EVIDENCE": (
                f"En Top 200, el quintil Q5 de activos "
                f"tiene exposure_ratio={exposure:.3f} "
                f"y representa {top_share:.3%} del ranking."
            )
            if not pd.isna(
                exposure
            )
            else (
                "No fue posible calcular "
                "la concentración de Q5."
            ),
            "INTERPRETATION": (
                "El modelo puede priorizar de forma "
                "muy marcada a empresas grandes. "
                "Esto puede ser parcialmente coherente "
                "con el objetivo comercial, pero debe "
                "evitar convertirse en una regla automática "
                "que excluya empresas medianas con potencial."
            ),
            "RISK_LEVEL": (
                "ALTO"
                if (
                    not pd.isna(
                        exposure
                    )
                    and exposure >= 3
                )
                else "MODERADO"
            ),
            "CONTROL": (
                "Presentar el score como prioridad relativa; "
                "mantener revisión humana y considerar listas "
                "complementarias por segmentos de tamaño."
            ),
        }
    )

    # -------------------------------------------------------------------------
    # R2 - DISPONIBILIDAD HISTÓRICA
    # -------------------------------------------------------------------------

    history_summary = group_summary.loc[
        group_summary[
            "DIMENSION"
        ].eq(
            "HISTORY_AVAILABILITY"
        )
    ]

    history_text = []

    for _, row in history_summary.iterrows():

        history_text.append(
            (
                f"{row['GROUP']}: "
                f"N={int(row['N'])}, "
                f"positivos={int(row['POSITIVES'])}, "
                f"score_medio={row['SCORE_MEAN']:.4f}"
            )
        )

    risks.append(
        {
            "RISK_ID": (
                "R2"
            ),
            "RISK": (
                "Ventaja para empresas con historial financiero"
            ),
            "CATEGORY": (
                "Cobertura de datos"
            ),
            "EVIDENCE": (
                " | ".join(
                    history_text
                )
            ),
            "INTERPRETATION": (
                "Empresas con información histórica disponible "
                "pueden recibir mejores scores porque el modelo "
                "dispone de más señales temporales. La falta de "
                "historia puede representar ausencia de datos y "
                "no necesariamente menor potencial."
            ),
            "RISK_LEVEL": (
                "MODERADO"
            ),
            "CONTROL": (
                "Mostrar explícitamente la cobertura histórica; "
                "no interpretar un score bajo por falta de datos "
                "como evidencia suficiente de bajo potencial."
            ),
        }
    )

    # -------------------------------------------------------------------------
    # R3 - TIPO DE COMPAÑÍA
    # -------------------------------------------------------------------------

    type_top200 = topk_exposure.loc[
        (
            topk_exposure[
                "DIMENSION"
            ].eq(
                "COMPANY_TYPE"
            )
        )
        & (
            topk_exposure[
                "K"
            ].eq(
                200
            )
        )
        & (
            ~topk_exposure[
                "SMALL_GROUP"
            ]
        )
    ].copy()

    if not type_top200.empty:

        type_top200 = (
            type_top200
            .sort_values(
                "EXPOSURE_RATIO",
                ascending=False,
            )
        )

        max_type = type_top200.iloc[
            0
        ]

        type_evidence = (
            f"Mayor exposición Top 200 entre grupos "
            f"con N>={MIN_GROUP_SIZE_FOR_INTERPRETATION}: "
            f"{max_type['GROUP']} con "
            f"exposure_ratio="
            f"{max_type['EXPOSURE_RATIO']:.3f}."
        )

    else:

        type_evidence = (
            "No existe grupo suficiente "
            "para interpretación."
        )

    risks.append(
        {
            "RISK_ID": (
                "R3"
            ),
            "RISK": (
                "Concentración por tipo de compañía"
            ),
            "CATEGORY": (
                "Representación / proxy"
            ),
            "EVIDENCE": (
                type_evidence
            ),
            "INTERPRETATION": (
                "La forma societaria está incluida como predictor. "
                "Las diferencias de score deben interpretarse junto "
                "con características financieras y no como una regla "
                "de elegibilidad por tipo societario."
            ),
            "RISK_LEVEL": (
                "MODERADO"
            ),
            "CONTROL": (
                "Monitorear exposición por tipo societario y "
                "mantener criterios comerciales independientes "
                "del score cuando exista justificación."
            ),
        }
    )

    # -------------------------------------------------------------------------
    # R4 - CONCENTRACIÓN GEOGRÁFICA INDIRECTA
    # -------------------------------------------------------------------------

    province_top200 = topk_exposure.loc[
        (
            topk_exposure[
                "DIMENSION"
            ].eq(
                "PROVINCE"
            )
        )
        & (
            topk_exposure[
                "K"
            ].eq(
                200
            )
        )
        & (
            ~topk_exposure[
                "SMALL_GROUP"
            ]
        )
    ].copy()

    if not province_top200.empty:

        province_top200 = (
            province_top200
            .sort_values(
                "EXPOSURE_RATIO",
                ascending=False,
            )
        )

        province_row = (
            province_top200.iloc[
                0
            ]
        )

        province_evidence = (
            f"Mayor exposición geográfica Top 200: "
            f"{province_row['GROUP']} con "
            f"exposure_ratio="
            f"{province_row['EXPOSURE_RATIO']:.3f}."
        )

    else:

        province_evidence = (
            "No existe grupo geográfico suficiente "
            "para interpretación."
        )

    risks.append(
        {
            "RISK_ID": (
                "R4"
            ),
            "RISK": (
                "Concentración geográfica indirecta"
            ),
            "CATEGORY": (
                "Proxy / cobertura"
            ),
            "EVIDENCE": (
                province_evidence
            ),
            "INTERPRETATION": (
                "Provincia no fue utilizada por el modelo final, "
                "pero otras variables financieras pueden producir "
                "concentraciones geográficas indirectas."
            ),
            "RISK_LEVEL": (
                "MODERADO"
            ),
            "CONTROL": (
                "Auditar periódicamente la distribución provincial "
                "del ranking y evitar interpretar concentración "
                "geográfica como criterio de elegibilidad."
            ),
        }
    )

    # -------------------------------------------------------------------------
    # R5 - MISSING
    # -------------------------------------------------------------------------

    missing_summary = group_summary.loc[
        group_summary[
            "DIMENSION"
        ].eq(
            "MISSINGNESS"
        )
    ].copy()

    if not missing_summary.empty:

        high_missing = missing_summary.loc[
            missing_summary[
                "GROUP"
            ].eq(
                "6_PLUS_MISSING"
            )
        ]

        if not high_missing.empty:

            missing_evidence = (
                f"6_PLUS_MISSING: "
                f"N={int(high_missing['N'].iloc[0])}, "
                f"positivos="
                f"{int(high_missing['POSITIVES'].iloc[0])}, "
                f"score_medio="
                f"{high_missing['SCORE_MEAN'].iloc[0]:.4f}."
            )

        else:

            missing_evidence = (
                "No se observó grupo 6_PLUS_MISSING."
            )

    else:

        missing_evidence = (
            "No fue posible construir "
            "el perfil de missing."
        )

    risks.append(
        {
            "RISK_ID": (
                "R5"
            ),
            "RISK": (
                "Impacto de información faltante"
            ),
            "CATEGORY": (
                "Calidad de datos"
            ),
            "EVIDENCE": (
                missing_evidence
            ),
            "INTERPRETATION": (
                "La ausencia de información financiera puede "
                "cambiar el score. Missing no siempre significa "
                "ausencia económica del atributo."
            ),
            "RISK_LEVEL": (
                "MODERADO"
            ),
            "CONTROL": (
                "Mostrar calidad/cobertura de datos junto al score "
                "y establecer validaciones de fuente antes de "
                "acciones comerciales relevantes."
            ),
        }
    )

    # -------------------------------------------------------------------------
    # R6 - EVENTO EXTREMADAMENTE RARO
    # -------------------------------------------------------------------------

    prevalence = float(
        df[
            TARGET
        ].mean()
    )

    risks.append(
        {
            "RISK_ID": (
                "R6"
            ),
            "RISK": (
                "Target extremadamente raro"
            ),
            "CATEGORY": (
                "Riesgo estadístico"
            ),
            "EVIDENCE": (
                f"TEST contiene "
                f"{EXPECTED_TEST_POSITIVES} positivos "
                f"entre {EXPECTED_TEST_N:,} observaciones; "
                f"prevalencia={prevalence:.8f}."
            ),
            "INTERPRETATION": (
                "Pequeños cambios en unos pocos positivos "
                "pueden alterar materialmente PR-AUC, Recall@K "
                "y Lift@K."
            ),
            "RISK_LEVEL": (
                "ALTO"
            ),
            "CONTROL": (
                "Usar múltiples métricas, backtesting temporal, "
                "intervalos de seguimiento y revisión humana; "
                "evitar decisiones automáticas basadas en un "
                "único corte."
            ),
        }
    )

    # -------------------------------------------------------------------------
    # R7 - SCORE NO ES PROBABILIDAD CALIBRADA
    # -------------------------------------------------------------------------

    risks.append(
        {
            "RISK_ID": (
                "R7"
            ),
            "RISK": (
                "Interpretación incorrecta del score"
            ),
            "CATEGORY": (
                "Uso responsable"
            ),
            "EVIDENCE": (
                "El modelo fue diseñado y evaluado "
                "principalmente como motor de ranking; "
                "no se ha establecido calibración probabilística."
            ),
            "INTERPRETATION": (
                "Un score de 0.80 no debe comunicarse como "
                "'80 % de probabilidad de convertirse en emisor'."
            ),
            "RISK_LEVEL": (
                "ALTO"
            ),
            "CONTROL": (
                "Mostrar score o nivel de prioridad, no probabilidad; "
                "documentar expresamente esta limitación en la interfaz "
                "y manual de uso."
            ),
        }
    )

    # -------------------------------------------------------------------------
    # R8 - AUTOMATIZACIÓN DE DECISIÓN
    # -------------------------------------------------------------------------

    risks.append(
        {
            "RISK_ID": (
                "R8"
            ),
            "RISK": (
                "Uso del ranking como decisión automática"
            ),
            "CATEGORY": (
                "Gobernanza"
            ),
            "EVIDENCE": (
                "TEST mostró 0 positivos en Top 50, "
                "0 en Top 100 y 1 en Top 200 conjunto."
            ),
            "INTERPRETATION": (
                "El modelo posee señal útil de priorización, "
                "pero no tiene precisión suficiente para sustituir "
                "el análisis comercial especializado."
            ),
            "RISK_LEVEL": (
                "ALTO"
            ),
            "CONTROL": (
                "Mantener human-in-the-loop. El ranking debe "
                "generar prospectos para análisis, no aprobar, "
                "descartar o contactar automáticamente empresas."
            ),
        }
    )

    # -------------------------------------------------------------------------
    # R9 - CAMBIO TEMPORAL
    # -------------------------------------------------------------------------

    year_rows = []

    for year in [
        2022,
        2023,
    ]:

        year_df = df.loc[
            df[
                "ANIO"
            ].eq(
                year
            )
        ]

        year_rows.append(
            (
                year,
                float(
                    average_precision_score(
                        year_df[
                            TARGET
                        ],
                        year_df[
                            "SCORE"
                        ],
                    )
                ),
                float(
                    roc_auc_score(
                        year_df[
                            TARGET
                        ],
                        year_df[
                            "SCORE"
                        ],
                    )
                ),
            )
        )

    risks.append(
        {
            "RISK_ID": (
                "R9"
            ),
            "RISK": (
                "Variación temporal del desempeño"
            ),
            "CATEGORY": (
                "Monitoreo"
            ),
            "EVIDENCE": (
                f"2022 PR-AUC={year_rows[0][1]:.6f}, "
                f"ROC-AUC={year_rows[0][2]:.6f}; "
                f"2023 PR-AUC={year_rows[1][1]:.6f}, "
                f"ROC-AUC={year_rows[1][2]:.6f}."
            ),
            "INTERPRETATION": (
                "La capacidad de priorización cambia entre años, "
                "aunque el análisis previo no mostró data drift "
                "generalizado."
            ),
            "RISK_LEVEL": (
                "ALTO"
            ),
            "CONTROL": (
                "Monitorear desempeño por corte temporal y definir "
                "criterios formales de revisión del modelo."
            ),
        }
    )

    return pd.DataFrame(
        risks
    )


# =============================================================================
# EJECUCIÓN
# =============================================================================

def main() -> None:

    warnings_list = []

    with warnings.catch_warnings(
        record=True
    ) as caught:

        warnings.simplefilter(
            "always"
        )

        print_header(
            "PROSPECT FINDER BVQ - "
            "SESGOS, RIESGOS Y USO RESPONSABLE v10"
        )

        print()
        print(
            "Regla metodológica:"
        )

        print(
            "- v10 permanece congelado."
        )

        print(
            "- El modelo NO será reentrenado."
        )

        print(
            "- Este análisis no modifica "
            "features ni hiperparámetros."
        )

        print(
            "- Las diferencias entre grupos "
            "son descriptivas y no constituyen "
            "por sí mismas evidencia de discriminación."
        )

        if not DATA_PATH.exists():

            raise FileNotFoundError(
                "No existe el dataset esperado:"
                f"\n{DATA_PATH}"
            )

        if not MODEL_PATH.exists():

            raise FileNotFoundError(
                "No existe el modelo final:"
                f"\n{MODEL_PATH}"
            )

        print()
        print(
            "Cargando artefacto final..."
        )

        (
            artifact,
            model,
        ) = load_final_artifact()

        validate_artifact(
            artifact
        )

        print(
            "Artefacto confirmado."
        )

        print()
        print(
            "Recuperando categorías "
            "desde TRAIN..."
        )

        train_categories = (
            load_train_categories()
        )

        print(
            f"Categorías TRAIN: "
            f"{len(train_categories)}"
        )

        print()
        print(
            "Cargando TEST 2022-2023..."
        )

        test = load_test(
            train_categories
        )

        validate_test_universe(
            test
        )

        print()
        print(
            "Generando scores con "
            "el modelo congelado..."
        )

        test[
            "SCORE"
        ] = model.predict_proba(
            test[
                FEATURES
            ]
        )[:, 1]

        print()
        print(
            "Reproduciendo métricas oficiales..."
        )

        (
            official_pr_auc,
            official_roc_auc,
        ) = validate_official_metrics(
            test[
                TARGET
            ],
            test[
                "SCORE"
            ].to_numpy(),
        )

        print()
        print(
            "Integridad confirmada."
        )

        print()
        print(
            "Construyendo grupos de auditoría..."
        )

        audit_df = add_audit_groups(
            test
        )

        print_header(
            "RESUMEN DE GRUPOS"
        )

        group_summary = (
            calculate_group_summary(
                audit_df
            )
        )

        print(
            group_summary.loc[
                group_summary[
                    "DIMENSION"
                ].isin(
                    [
                        "ASSET_SIZE",
                        "HISTORY_AVAILABILITY",
                        "PATRIMONY_STATUS",
                        "MISSINGNESS",
                    ]
                )
            ]
            .to_string(
                index=False
            )
        )

        print_header(
            "EXPOSICIÓN TOP 200"
        )

        topk_exposure = (
            calculate_topk_exposure(
                audit_df
            )
        )

        print(
            topk_exposure.loc[
                (
                    topk_exposure[
                        "K"
                    ].eq(
                        200
                    )
                )
                & (
                    topk_exposure[
                        "DIMENSION"
                    ].isin(
                        [
                            "ASSET_SIZE",
                            "HISTORY_AVAILABILITY",
                            "PATRIMONY_STATUS",
                            "MISSINGNESS",
                        ]
                    )
                )
            ][
                [
                    "DIMENSION",
                    "GROUP",
                    "POPULATION_N",
                    "POPULATION_SHARE",
                    "SELECTED_N",
                    "TOP_K_SHARE",
                    "EXPOSURE_RATIO",
                    "POSITIVES_GROUP",
                    "POSITIVES_TOP_K_GROUP",
                ]
            ]
            .to_string(
                index=False
            )
        )

        print_header(
            "REGISTRO DE RIESGOS"
        )

        risk_register = (
            build_risk_register(
                audit_df,
                group_summary,
                topk_exposure,
            )
        )

        print(
            risk_register[
                [
                    "RISK_ID",
                    "RISK",
                    "CATEGORY",
                    "RISK_LEVEL",
                ]
            ]
            .to_string(
                index=False
            )
        )

        group_summary.to_csv(
            OUT_GROUP_SUMMARY,
            index=False,
            encoding="utf-8-sig",
        )

        topk_exposure.to_csv(
            OUT_TOPK_EXPOSURE,
            index=False,
            encoding="utf-8-sig",
        )

        risk_register.to_csv(
            OUT_RISK_REGISTER,
            index=False,
            encoding="utf-8-sig",
        )

        warnings_list = [
            str(
                warning.message
            )
            for warning in caught
        ]

    metadata = {
        "project": (
            "Prospect Finder BVQ"
        ),
        "version": (
            "v10"
        ),
        "analysis": (
            "post_test_bias_risk"
        ),
        "model": (
            EXPECTED_MODEL_NAME
        ),
        "configuration": (
            EXPECTED_CONFIG_ID
        ),
        "model_retrained": (
            False
        ),
        "purpose": (
            "Analizar concentración del ranking, "
            "riesgos de representación, cobertura "
            "de datos y condiciones para uso "
            "responsable del modelo."
        ),
        "integrity_check": {
            "expected_test_n": (
                EXPECTED_TEST_N
            ),
            "expected_test_positives": (
                EXPECTED_TEST_POSITIVES
            ),
            "reproduced_pr_auc": (
                official_pr_auc
            ),
            "reproduced_roc_auc": (
                official_roc_auc
            ),
            "passed": (
                True
            ),
        },
        "audit_dimensions": [
            "asset_size",
            "history_availability",
            "patrimony_status",
            "missingness",
            "company_type",
            "province",
        ],
        "important_notes": [
            (
                "Provincia no fue utilizada como "
                "predictor del modelo final; se audita "
                "para detectar concentración indirecta."
            ),
            (
                "Las diferencias entre grupos son "
                "descriptivas y no constituyen por sí "
                "mismas evidencia de discriminación."
            ),
            (
                "El score no ha sido calibrado como "
                "probabilidad de emisión."
            ),
            (
                "El modelo debe utilizarse como apoyo "
                "a priorización comercial con revisión humana."
            ),
        ],
        "outputs": [
            str(
                OUT_GROUP_SUMMARY.relative_to(
                    ROOT
                )
            ),
            str(
                OUT_TOPK_EXPOSURE.relative_to(
                    ROOT
                )
            ),
            str(
                OUT_RISK_REGISTER.relative_to(
                    ROOT
                )
            ),
            str(
                OUT_METADATA.relative_to(
                    ROOT
                )
            ),
        ],
        "warnings": (
            warnings_list
        ),
    }

    with open(
        OUT_METADATA,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print_header(
        "ARCHIVOS GENERADOS"
    )

    for path in [
        OUT_GROUP_SUMMARY,
        OUT_TOPK_EXPOSURE,
        OUT_RISK_REGISTER,
        OUT_METADATA,
    ]:

        print(
            path
        )

    print_header(
        "ANÁLISIS DE SESGOS Y "
        "RIESGOS v10 COMPLETADO"
    )

    print()
    print(
        "Este análisis no modifica "
        "el modelo v10."
    )

    print(
        "Las métricas de representación "
        "deben interpretarse como señales "
        "para gobernanza y monitoreo, "
        "no como evidencia automática "
        "de discriminación."
    )


if __name__ == "__main__":
    main()