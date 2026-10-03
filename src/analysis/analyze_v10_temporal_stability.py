from __future__ import annotations

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
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

PSI_EPSILON = 1e-6
PSI_NUMERIC_BINS = 10

TOP_K_VALUES = [
    50,
    100,
    200,
]

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
    / "temporal_stability"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_YEAR_METRICS = (
    OUTPUT_DIR
    / "v10_temporal_year_metrics.csv"
)

OUT_TOPK = (
    OUTPUT_DIR
    / "v10_temporal_topk_metrics.csv"
)

OUT_SCORE_PROFILE = (
    OUTPUT_DIR
    / "v10_score_distribution_by_year.csv"
)

OUT_SCORE_DRIFT = (
    OUTPUT_DIR
    / "v10_score_drift_2022_2023.csv"
)

OUT_FEATURE_DRIFT = (
    OUTPUT_DIR
    / "v10_feature_drift_2022_2023.csv"
)

OUT_MISSINGNESS = (
    OUTPUT_DIR
    / "v10_missingness_by_year.csv"
)

OUT_POSITIVE_RANK = (
    OUTPUT_DIR
    / "v10_positive_rank_summary.csv"
)

OUT_METADATA = (
    OUTPUT_DIR
    / "v10_temporal_stability_metadata.json"
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
            "coinciden con el análisis."
        )


# =============================================================================
# CATEGORÍAS TRAIN
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
        .astype("int64")
    )

    df[TARGET] = (
        pd.to_numeric(
            df[TARGET],
            errors="raise",
        )
        .astype("int8")
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
            .astype("float64")
        )

    for col in BOOLEAN_FEATURES:

        df[col] = normalize_boolean(
            df[col]
        )

    tipo = (
        df["tipo_compania"]
        .astype("string")
    )

    df["tipo_compania"] = pd.Categorical(
        tipo,
        categories=train_categories,
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
        df[TARGET].sum()
    )

    years = sorted(
        df["ANIO"]
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
# MÉTRICAS POR AÑO
# =============================================================================

def calculate_year_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:

    rows = []

    for year in [
        2022,
        2023,
    ]:

        year_df = df.loc[
            df["ANIO"].eq(
                year
            )
        ].copy()

        y = year_df[
            TARGET
        ]

        scores = year_df[
            "SCORE"
        ]

        pr_auc = float(
            average_precision_score(
                y,
                scores,
            )
        )

        roc_auc = float(
            roc_auc_score(
                y,
                scores,
            )
        )

        rows.append(
            {
                "ANIO": year,
                "N": int(
                    len(
                        year_df
                    )
                ),
                "POSITIVOS": int(
                    y.sum()
                ),
                "PREVALENCIA": float(
                    y.mean()
                ),
                "PR_AUC": pr_auc,
                "ROC_AUC": roc_auc,
                "SCORE_MEAN": float(
                    scores.mean()
                ),
                "SCORE_MEDIAN": float(
                    scores.median()
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


# =============================================================================
# TOP K POR AÑO
# =============================================================================

def calculate_topk_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:

    rows = []

    for year in [
        2022,
        2023,
    ]:

        year_df = df.loc[
            df["ANIO"].eq(
                year
            )
        ].copy()

        year_df[
            "EXPEDIENTE_SORT"
        ] = (
            year_df[
                "EXPEDIENTE_KEY"
            ]
            .astype("string")
        )

        ranking = (
            year_df
            .sort_values(
                [
                    "SCORE",
                    "EXPEDIENTE_SORT",
                ],
                ascending=[
                    False,
                    True,
                ],
                kind="mergesort",
            )
            .reset_index(
                drop=True
            )
        )

        n = len(
            ranking
        )

        positives_total = int(
            ranking[
                TARGET
            ].sum()
        )

        prevalence = (
            positives_total / n
            if n > 0
            else np.nan
        )

        for k in TOP_K_VALUES:

            effective_k = min(
                k,
                n,
            )

            top = ranking.head(
                effective_k
            )

            positives_top = int(
                top[
                    TARGET
                ].sum()
            )

            precision = (
                positives_top
                / effective_k
                if effective_k > 0
                else np.nan
            )

            recall = (
                positives_top
                / positives_total
                if positives_total > 0
                else np.nan
            )

            lift = (
                precision
                / prevalence
                if prevalence > 0
                else np.nan
            )

            score_threshold = float(
                top[
                    "SCORE"
                ].iloc[-1]
            )

            rows.append(
                {
                    "ANIO": year,
                    "N": int(
                        n
                    ),
                    "POSITIVOS": (
                        positives_total
                    ),
                    "K": int(
                        k
                    ),
                    "POSITIVOS_TOP_K": (
                        positives_top
                    ),
                    "PRECISION_AT_K": float(
                        precision
                    ),
                    "RECALL_AT_K": float(
                        recall
                    ),
                    "LIFT_AT_K": float(
                        lift
                    ),
                    "SCORE_THRESHOLD_AT_K": (
                        score_threshold
                    ),
                }
            )

    return pd.DataFrame(
        rows
    )


# =============================================================================
# RANKING DE POSITIVOS
# =============================================================================

def calculate_positive_rank_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:

    rows = []

    for year in [
        2022,
        2023,
    ]:

        year_df = df.loc[
            df["ANIO"].eq(
                year
            )
        ].copy()

        year_df[
            "EXPEDIENTE_SORT"
        ] = (
            year_df[
                "EXPEDIENTE_KEY"
            ]
            .astype("string")
        )

        ranking = (
            year_df
            .sort_values(
                [
                    "SCORE",
                    "EXPEDIENTE_SORT",
                ],
                ascending=[
                    False,
                    True,
                ],
                kind="mergesort",
            )
            .reset_index(
                drop=True
            )
        )

        ranking[
            "RANK"
        ] = np.arange(
            1,
            len(
                ranking
            ) + 1,
        )

        positives = ranking.loc[
            ranking[
                TARGET
            ].eq(
                1
            )
        ].copy()

        positive_ranks = (
            positives[
                "RANK"
            ]
            .astype(
                "float64"
            )
        )

        positive_scores = (
            positives[
                "SCORE"
            ]
            .astype(
                "float64"
            )
        )

        rows.append(
            {
                "ANIO": year,
                "POSITIVOS": int(
                    len(
                        positives
                    )
                ),
                "MEJOR_RANK_POSITIVO": int(
                    positive_ranks.min()
                ),
                "MEDIANA_RANK_POSITIVO": float(
                    positive_ranks.median()
                ),
                "MEDIA_RANK_POSITIVO": float(
                    positive_ranks.mean()
                ),
                "PEOR_RANK_POSITIVO": int(
                    positive_ranks.max()
                ),
                "SCORE_MAX_POSITIVO": float(
                    positive_scores.max()
                ),
                "SCORE_MEDIAN_POSITIVO": float(
                    positive_scores.median()
                ),
                "SCORE_MEAN_POSITIVO": float(
                    positive_scores.mean()
                ),
                "SCORE_MIN_POSITIVO": float(
                    positive_scores.min()
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


# =============================================================================
# PERFIL DE SCORE
# =============================================================================

def calculate_score_profile(
    df: pd.DataFrame,
) -> pd.DataFrame:

    quantiles = [
        0.00,
        0.01,
        0.05,
        0.10,
        0.25,
        0.50,
        0.75,
        0.90,
        0.95,
        0.99,
        1.00,
    ]

    rows = []

    for year in [
        2022,
        2023,
    ]:

        scores = (
            df.loc[
                df["ANIO"].eq(
                    year
                ),
                "SCORE",
            ]
            .astype(
                "float64"
            )
        )

        for q in quantiles:

            rows.append(
                {
                    "ANIO": year,
                    "STATISTIC": (
                        f"Q{int(q * 100):02d}"
                    ),
                    "VALUE": float(
                        scores.quantile(
                            q
                        )
                    ),
                }
            )

        rows.extend(
            [
                {
                    "ANIO": year,
                    "STATISTIC": "MEAN",
                    "VALUE": float(
                        scores.mean()
                    ),
                },
                {
                    "ANIO": year,
                    "STATISTIC": "STD",
                    "VALUE": float(
                        scores.std()
                    ),
                },
            ]
        )

    return pd.DataFrame(
        rows
    )


# =============================================================================
# PSI NUMÉRICO
# =============================================================================

def numeric_psi(
    reference: pd.Series,
    comparison: pd.Series,
    bins: int = PSI_NUMERIC_BINS,
) -> float:

    reference = pd.to_numeric(
        reference,
        errors="coerce",
    )

    comparison = pd.to_numeric(
        comparison,
        errors="coerce",
    )

    reference_nonmissing = (
        reference
        .dropna()
        .astype(
            "float64"
        )
    )

    comparison_nonmissing = (
        comparison
        .dropna()
        .astype(
            "float64"
        )
    )

    if reference_nonmissing.empty:
        return np.nan

    quantiles = np.linspace(
        0,
        1,
        bins + 1,
    )

    edges = np.unique(
        reference_nonmissing.quantile(
            quantiles
        ).to_numpy()
    )

    if len(
        edges
    ) < 2:
        return np.nan

    edges = edges.astype(
        "float64"
    )

    edges[0] = -np.inf
    edges[-1] = np.inf

    reference_bins = pd.cut(
        reference_nonmissing,
        bins=edges,
        include_lowest=True,
        duplicates="drop",
    )

    comparison_bins = pd.cut(
        comparison_nonmissing,
        bins=edges,
        include_lowest=True,
        duplicates="drop",
    )

    categories = (
        reference_bins
        .cat
        .categories
    )

    ref_counts = (
        reference_bins
        .value_counts(
            sort=False
        )
        .reindex(
            categories,
            fill_value=0,
        )
        .astype(
            "float64"
        )
    )

    cmp_counts = (
        comparison_bins
        .value_counts(
            sort=False
        )
        .reindex(
            categories,
            fill_value=0,
        )
        .astype(
            "float64"
        )
    )

    ref_missing = float(
        reference.isna().sum()
    )

    cmp_missing = float(
        comparison.isna().sum()
    )

    ref_vector = np.append(
        ref_counts.to_numpy(),
        ref_missing,
    )

    cmp_vector = np.append(
        cmp_counts.to_numpy(),
        cmp_missing,
    )

    ref_prop = (
        ref_vector
        + PSI_EPSILON
    )

    cmp_prop = (
        cmp_vector
        + PSI_EPSILON
    )

    ref_prop = (
        ref_prop
        / ref_prop.sum()
    )

    cmp_prop = (
        cmp_prop
        / cmp_prop.sum()
    )

    psi = np.sum(
        (
            cmp_prop
            - ref_prop
        )
        * np.log(
            cmp_prop
            / ref_prop
        )
    )

    return float(
        psi
    )


# =============================================================================
# PSI CATEGÓRICO
# =============================================================================

def categorical_psi(
    reference: pd.Series,
    comparison: pd.Series,
) -> tuple[float, float]:

    ref = (
        reference
        .astype("string")
        .fillna(
            "MISSING"
        )
    )

    cmp = (
        comparison
        .astype("string")
        .fillna(
            "MISSING"
        )
    )

    categories = sorted(
        set(
            ref.unique().tolist()
        )
        | set(
            cmp.unique().tolist()
        )
    )

    ref_counts = (
        ref
        .value_counts()
        .reindex(
            categories,
            fill_value=0,
        )
        .astype(
            "float64"
        )
    )

    cmp_counts = (
        cmp
        .value_counts()
        .reindex(
            categories,
            fill_value=0,
        )
        .astype(
            "float64"
        )
    )

    ref_prop = (
        ref_counts.to_numpy()
        + PSI_EPSILON
    )

    cmp_prop = (
        cmp_counts.to_numpy()
        + PSI_EPSILON
    )

    ref_prop = (
        ref_prop
        / ref_prop.sum()
    )

    cmp_prop = (
        cmp_prop
        / cmp_prop.sum()
    )

    psi = np.sum(
        (
            cmp_prop
            - ref_prop
        )
        * np.log(
            cmp_prop
            / ref_prop
        )
    )

    total_variation = (
        0.5
        * np.abs(
            cmp_prop
            - ref_prop
        ).sum()
    )

    return (
        float(
            psi
        ),
        float(
            total_variation
        ),
    )


# =============================================================================
# CLASIFICACIÓN DESCRIPTIVA PSI
# =============================================================================

def psi_level(
    psi: float,
) -> str:

    if pd.isna(
        psi
    ):
        return "NO_CALCULABLE"

    if psi < 0.10:
        return "BAJO"

    if psi < 0.25:
        return "MODERADO"

    return "ALTO"


# =============================================================================
# DRIFT DE SCORE
# =============================================================================

def calculate_score_drift(
    df: pd.DataFrame,
) -> pd.DataFrame:

    scores_2022 = (
        df.loc[
            df["ANIO"].eq(
                2022
            ),
            "SCORE",
        ]
        .astype(
            "float64"
        )
    )

    scores_2023 = (
        df.loc[
            df["ANIO"].eq(
                2023
            ),
            "SCORE",
        ]
        .astype(
            "float64"
        )
    )

    psi = numeric_psi(
        reference=scores_2022,
        comparison=scores_2023,
    )

    ks_result = ks_2samp(
        scores_2022,
        scores_2023,
        alternative="two-sided",
        method="asymp",
    )

    result = pd.DataFrame(
        [
            {
                "VARIABLE": "SCORE",
                "REFERENCE_YEAR": 2022,
                "COMPARISON_YEAR": 2023,
                "PSI": float(
                    psi
                ),
                "PSI_LEVEL_HEURISTIC": (
                    psi_level(
                        psi
                    )
                ),
                "KS_STATISTIC": float(
                    ks_result.statistic
                ),
                "KS_PVALUE": float(
                    ks_result.pvalue
                ),
                "MEAN_2022": float(
                    scores_2022.mean()
                ),
                "MEAN_2023": float(
                    scores_2023.mean()
                ),
                "MEDIAN_2022": float(
                    scores_2022.median()
                ),
                "MEDIAN_2023": float(
                    scores_2023.median()
                ),
                "STD_2022": float(
                    scores_2022.std()
                ),
                "STD_2023": float(
                    scores_2023.std()
                ),
            }
        ]
    )

    return result


# =============================================================================
# DRIFT DE FEATURES
# =============================================================================

def calculate_feature_drift(
    df: pd.DataFrame,
) -> pd.DataFrame:

    reference = df.loc[
        df["ANIO"].eq(
            2022
        )
    ].copy()

    comparison = df.loc[
        df["ANIO"].eq(
            2023
        )
    ].copy()

    rows = []

    for feature in NUMERIC_FEATURES:

        ref = reference[
            feature
        ]

        cmp = comparison[
            feature
        ]

        psi = numeric_psi(
            ref,
            cmp,
        )

        ref_valid = (
            ref
            .dropna()
            .astype(
                "float64"
            )
        )

        cmp_valid = (
            cmp
            .dropna()
            .astype(
                "float64"
            )
        )

        if (
            len(
                ref_valid
            ) > 0
            and len(
                cmp_valid
            ) > 0
        ):
            ks_result = ks_2samp(
                ref_valid,
                cmp_valid,
                alternative="two-sided",
                method="asymp",
            )

            ks_statistic = float(
                ks_result.statistic
            )

            ks_pvalue = float(
                ks_result.pvalue
            )

        else:
            ks_statistic = np.nan
            ks_pvalue = np.nan

        rows.append(
            {
                "FEATURE": feature,
                "TYPE": "NUMERIC",
                "PSI": float(
                    psi
                )
                if not pd.isna(
                    psi
                )
                else np.nan,
                "PSI_LEVEL_HEURISTIC": (
                    psi_level(
                        psi
                    )
                ),
                "KS_STATISTIC": (
                    ks_statistic
                ),
                "KS_PVALUE": (
                    ks_pvalue
                ),
                "TOTAL_VARIATION": (
                    np.nan
                ),
                "MISSING_RATE_2022": float(
                    ref.isna().mean()
                ),
                "MISSING_RATE_2023": float(
                    cmp.isna().mean()
                ),
                "MISSING_DELTA": float(
                    cmp.isna().mean()
                    - ref.isna().mean()
                ),
                "MEAN_2022": float(
                    ref_valid.mean()
                )
                if len(
                    ref_valid
                ) > 0
                else np.nan,
                "MEAN_2023": float(
                    cmp_valid.mean()
                )
                if len(
                    cmp_valid
                ) > 0
                else np.nan,
                "MEDIAN_2022": float(
                    ref_valid.median()
                )
                if len(
                    ref_valid
                ) > 0
                else np.nan,
                "MEDIAN_2023": float(
                    cmp_valid.median()
                )
                if len(
                    cmp_valid
                ) > 0
                else np.nan,
            }
        )

    for feature in (
        BOOLEAN_FEATURES
        + CATEGORICAL
    ):

        ref = reference[
            feature
        ]

        cmp = comparison[
            feature
        ]

        (
            psi,
            total_variation,
        ) = categorical_psi(
            ref,
            cmp,
        )

        feature_type = (
            "BOOLEAN"
            if feature in BOOLEAN_FEATURES
            else "CATEGORICAL"
        )

        rows.append(
            {
                "FEATURE": feature,
                "TYPE": feature_type,
                "PSI": float(
                    psi
                ),
                "PSI_LEVEL_HEURISTIC": (
                    psi_level(
                        psi
                    )
                ),
                "KS_STATISTIC": (
                    np.nan
                ),
                "KS_PVALUE": (
                    np.nan
                ),
                "TOTAL_VARIATION": float(
                    total_variation
                ),
                "MISSING_RATE_2022": float(
                    ref.isna().mean()
                ),
                "MISSING_RATE_2023": float(
                    cmp.isna().mean()
                ),
                "MISSING_DELTA": float(
                    cmp.isna().mean()
                    - ref.isna().mean()
                ),
                "MEAN_2022": (
                    np.nan
                ),
                "MEAN_2023": (
                    np.nan
                ),
                "MEDIAN_2022": (
                    np.nan
                ),
                "MEDIAN_2023": (
                    np.nan
                ),
            }
        )

    result = pd.DataFrame(
        rows
    )

    result = (
        result
        .sort_values(
            [
                "PSI",
                "FEATURE",
            ],
            ascending=[
                False,
                True,
            ],
            na_position="last",
        )
        .reset_index(
            drop=True
        )
    )

    result.insert(
        0,
        "RANK_PSI",
        np.arange(
            1,
            len(
                result
            ) + 1,
        ),
    )

    return result


# =============================================================================
# MISSINGNESS
# =============================================================================

def calculate_missingness(
    df: pd.DataFrame,
) -> pd.DataFrame:

    rows = []

    for feature in FEATURES:

        row = {
            "FEATURE": feature,
        }

        rates = {}

        counts = {}

        for year in [
            2022,
            2023,
        ]:

            series = df.loc[
                df["ANIO"].eq(
                    year
                ),
                feature,
            ]

            rates[
                year
            ] = float(
                series.isna().mean()
            )

            counts[
                year
            ] = int(
                series.isna().sum()
            )

        row.update(
            {
                "MISSING_N_2022": (
                    counts[
                        2022
                    ]
                ),
                "MISSING_RATE_2022": (
                    rates[
                        2022
                    ]
                ),
                "MISSING_N_2023": (
                    counts[
                        2023
                    ]
                ),
                "MISSING_RATE_2023": (
                    rates[
                        2023
                    ]
                ),
                "MISSING_DELTA": (
                    rates[
                        2023
                    ]
                    - rates[
                        2022
                    ]
                ),
                "ABS_MISSING_DELTA": abs(
                    rates[
                        2023
                    ]
                    - rates[
                        2022
                    ]
                ),
            }
        )

        rows.append(
            row
        )

    result = pd.DataFrame(
        rows
    )

    return (
        result
        .sort_values(
            [
                "ABS_MISSING_DELTA",
                "FEATURE",
            ],
            ascending=[
                False,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
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
            "ESTABILIDAD TEMPORAL POST-TEST v10"
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
            "- El análisis compara 2022 y 2023."
        )

        print(
            "- Drift observado NO implica "
            "automáticamente concept drift."
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
            "de TRAIN..."
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
            "Generando scores con el "
            "modelo final congelado..."
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
            "Reproduciendo métricas "
            "oficiales..."
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

        print_header(
            "DESEMPEÑO POR AÑO"
        )

        year_metrics = (
            calculate_year_metrics(
                test
            )
        )

        print(
            year_metrics.to_string(
                index=False
            )
        )

        print_header(
            "RANKING TOP K POR AÑO"
        )

        topk_metrics = (
            calculate_topk_metrics(
                test
            )
        )

        print(
            topk_metrics.to_string(
                index=False
            )
        )

        positive_rank = (
            calculate_positive_rank_summary(
                test
            )
        )

        print_header(
            "POSICIÓN DE LOS POSITIVOS"
        )

        print(
            positive_rank.to_string(
                index=False
            )
        )

        print_header(
            "DRIFT DEL SCORE"
        )

        score_profile = (
            calculate_score_profile(
                test
            )
        )

        score_drift = (
            calculate_score_drift(
                test
            )
        )

        print(
            score_drift.to_string(
                index=False
            )
        )

        print_header(
            "DRIFT DE FEATURES"
        )

        feature_drift = (
            calculate_feature_drift(
                test
            )
        )

        print(
            "Top 15 variables por PSI "
            "2022 -> 2023:"
        )

        print()

        print(
            feature_drift[
                [
                    "RANK_PSI",
                    "FEATURE",
                    "TYPE",
                    "PSI",
                    "PSI_LEVEL_HEURISTIC",
                    "KS_STATISTIC",
                    "TOTAL_VARIATION",
                    "MISSING_DELTA",
                ]
            ]
            .head(
                15
            )
            .to_string(
                index=False
            )
        )

        print_header(
            "CAMBIOS DE MISSING"
        )

        missingness = (
            calculate_missingness(
                test
            )
        )

        print(
            missingness[
                [
                    "FEATURE",
                    "MISSING_RATE_2022",
                    "MISSING_RATE_2023",
                    "MISSING_DELTA",
                ]
            ]
            .head(
                15
            )
            .to_string(
                index=False
            )
        )

        year_metrics.to_csv(
            OUT_YEAR_METRICS,
            index=False,
            encoding="utf-8-sig",
        )

        topk_metrics.to_csv(
            OUT_TOPK,
            index=False,
            encoding="utf-8-sig",
        )

        score_profile.to_csv(
            OUT_SCORE_PROFILE,
            index=False,
            encoding="utf-8-sig",
        )

        score_drift.to_csv(
            OUT_SCORE_DRIFT,
            index=False,
            encoding="utf-8-sig",
        )

        feature_drift.to_csv(
            OUT_FEATURE_DRIFT,
            index=False,
            encoding="utf-8-sig",
        )

        missingness.to_csv(
            OUT_MISSINGNESS,
            index=False,
            encoding="utf-8-sig",
        )

        positive_rank.to_csv(
            OUT_POSITIVE_RANK,
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
            "post_test_temporal_stability"
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
        "comparison": {
            "reference_year": (
                2022
            ),
            "comparison_year": (
                2023
            ),
        },
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
        "drift_methods": {
            "numeric_features": [
                "PSI",
                "Kolmogorov-Smirnov statistic",
                "missing-rate delta",
            ],
            "categorical_features": [
                "PSI",
                "total variation distance",
                "missing-rate delta",
            ],
            "score": [
                "PSI",
                "Kolmogorov-Smirnov statistic",
                "distribution quantiles",
            ],
        },
        "psi_interpretation": {
            "note": (
                "Los niveles se utilizan como "
                "heurística descriptiva, no como "
                "regla universal."
            ),
            "low": (
                "PSI < 0.10"
            ),
            "moderate": (
                "0.10 <= PSI < 0.25"
            ),
            "high": (
                "PSI >= 0.25"
            ),
        },
        "important_methodological_note": (
            "Este análisis puede identificar "
            "data drift, score drift y cambios "
            "de desempeño. Por sí solo no prueba "
            "la existencia de concept drift."
        ),
        "outputs": [
            str(
                OUT_YEAR_METRICS.relative_to(
                    ROOT
                )
            ),
            str(
                OUT_TOPK.relative_to(
                    ROOT
                )
            ),
            str(
                OUT_SCORE_PROFILE.relative_to(
                    ROOT
                )
            ),
            str(
                OUT_SCORE_DRIFT.relative_to(
                    ROOT
                )
            ),
            str(
                OUT_FEATURE_DRIFT.relative_to(
                    ROOT
                )
            ),
            str(
                OUT_MISSINGNESS.relative_to(
                    ROOT
                )
            ),
            str(
                OUT_POSITIVE_RANK.relative_to(
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
        OUT_YEAR_METRICS,
        OUT_TOPK,
        OUT_SCORE_PROFILE,
        OUT_SCORE_DRIFT,
        OUT_FEATURE_DRIFT,
        OUT_MISSINGNESS,
        OUT_POSITIVE_RANK,
        OUT_METADATA,
    ]:

        print(
            path
        )

    print_header(
        "ANÁLISIS DE ESTABILIDAD "
        "TEMPORAL v10 COMPLETADO"
    )

    print()
    print(
        "El modelo v10 no fue modificado."
    )

    print(
        "Los resultados permiten estudiar "
        "cambios entre 2022 y 2023 sin "
        "reabrir la selección del modelo."
    )


if __name__ == "__main__":
    main()