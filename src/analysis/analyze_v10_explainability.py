from __future__ import annotations

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import average_precision_score, roc_auc_score


# =============================================================================
# CONFIGURACIÓN
# =============================================================================

RANDOM_STATE = 42
NEGATIVE_SAMPLE_SIZE = 50_000
N_REPEATS = 5

EXPECTED_TEST_N = 260_445
EXPECTED_TEST_POSITIVES = 54
EXPECTED_TEST_PR_AUC = 0.007468801
EXPECTED_TEST_ROC_AUC = 0.934603901

METRIC_TOLERANCE = 1e-6

EXPECTED_MODEL_NAME = "v10_hgb_financial_c3"
EXPECTED_CONFIG_ID = "C3_CONSERVATIVE"

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
    / "explainability"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_IMPORTANCE = (
    OUTPUT_DIR
    / "v10_permutation_importance.csv"
)

OUT_NUMERIC_PROFILE = (
    OUTPUT_DIR
    / "v10_numeric_score_profiles.csv"
)

OUT_BOOLEAN_PROFILE = (
    OUTPUT_DIR
    / "v10_boolean_score_profiles.csv"
)

OUT_CATEGORICAL_PROFILE = (
    OUTPUT_DIR
    / "v10_tipo_compania_score_profile.csv"
)

OUT_METADATA = (
    OUTPUT_DIR
    / "v10_explainability_metadata.json"
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
# FUNCIONES GENERALES
# =============================================================================

def print_header(title: str) -> None:
    line = "=" * 120

    print()
    print(line)
    print(title)
    print(line)


def normalize_boolean(
    series: pd.Series,
) -> pd.Series:
    """
    Convierte variables booleanas a float64.

    Valores finales permitidos:
    0.0
    1.0
    NaN
    """

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
# CARGA DEL ARTEFACTO FINAL
# =============================================================================

def load_final_artifact():
    """
    El archivo joblib de v10 no contiene solamente
    el estimador.

    Contiene un diccionario con:
    - model
    - model_name
    - config_id
    - features
    - numeric_features
    - boolean_features
    - categorical_features
    - target
    - train_period
    - test_period

    Esta función extrae el modelo sin modificarlo.
    """

    artifact = joblib.load(
        MODEL_PATH
    )

    if not isinstance(
        artifact,
        dict,
    ):
        raise RuntimeError(
            "El artefacto final v10 no tiene "
            "la estructura esperada de diccionario."
        )

    if "model" not in artifact:
        raise RuntimeError(
            "El artefacto final no contiene "
            "la clave 'model'."
        )

    model = artifact["model"]

    if not hasattr(
        model,
        "predict_proba",
    ):
        raise RuntimeError(
            "El objeto almacenado en la clave "
            "'model' no implementa predict_proba."
        )

    return artifact, model


# =============================================================================
# VALIDACIÓN DEL ARTEFACTO
# =============================================================================

def validate_artifact(
    artifact: dict,
) -> None:

    model_name = artifact.get(
        "model_name"
    )

    config_id = artifact.get(
        "config_id"
    )

    artifact_features = artifact.get(
        "features"
    )

    artifact_target = artifact.get(
        "target"
    )

    print(
        f"Modelo artefacto: "
        f"{model_name}"
    )

    print(
        f"Configuración:    "
        f"{config_id}"
    )

    print(
        f"Target:           "
        f"{artifact_target}"
    )

    print(
        f"Features:         "
        f"{len(artifact_features) if artifact_features is not None else 'N/D'}"
    )

    if model_name != EXPECTED_MODEL_NAME:
        raise RuntimeError(
            "El model_name del artefacto "
            "no coincide con el modelo "
            "v10 congelado."
        )

    if config_id != EXPECTED_CONFIG_ID:
        raise RuntimeError(
            "El config_id del artefacto "
            "no coincide con C3_CONSERVATIVE."
        )

    if artifact_target != TARGET:
        raise RuntimeError(
            "El target almacenado en el artefacto "
            "no coincide con TARGET_24M."
        )

    if artifact_features is None:
        raise RuntimeError(
            "El artefacto no contiene "
            "la lista de features."
        )

    if list(
        artifact_features
    ) != FEATURES:
        raise RuntimeError(
            "El orden de features del artefacto "
            "no coincide con el esperado por "
            "el análisis."
        )


# =============================================================================
# CATEGORÍAS APRENDIDAS DESDE TRAIN
# =============================================================================

def load_train_categories() -> list[str]:
    """
    Obtiene las categorías de tipo_compania
    únicamente desde TRAIN.

    TEST no participa en la construcción
    del vocabulario categórico.
    """

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
# CARGA DE TEST
# =============================================================================

def load_test(
    train_categories: list[str],
) -> pd.DataFrame:
    """
    Carga exclusivamente TEST 2022-2023.

    TRAIN únicamente se usa para recuperar
    las categorías válidas de tipo_compania.
    """

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
            "No se encontraron observaciones "
            "con SPLIT='TEST'."
        )

    df = pd.concat(
        frames,
        ignore_index=True,
    )

    df["ANIO"] = (
        pd.to_numeric(
            df["ANIO"],
            errors="coerce",
        )
        .astype("Int64")
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
            .astype(
                "float64"
            )
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
# VALIDACIÓN DEL UNIVERSO TEST
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
        .dropna()
        .astype(int)
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
            "TEST no coincide con el universo "
            "congelado. "
            f"Esperado={EXPECTED_TEST_N:,}, "
            f"encontrado={n:,}."
        )

    if positives != EXPECTED_TEST_POSITIVES:
        raise RuntimeError(
            "Los positivos de TEST no coinciden "
            "con el universo congelado. "
            f"Esperado={EXPECTED_TEST_POSITIVES}, "
            f"encontrado={positives}."
        )

    if years != [
        2022,
        2023,
    ]:
        raise RuntimeError(
            "Años inesperados en TEST. "
            "Esperado=[2022, 2023], "
            f"encontrado={years}."
        )


# =============================================================================
# REPRODUCCIÓN DE MÉTRICAS OFICIALES
# =============================================================================

def validate_reproduced_metrics(
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
            "La PR-AUC reproducida no coincide "
            "con la evaluación final oficial "
            "de v10. Se detiene el análisis."
        )

    if not np.isclose(
        roc_auc,
        EXPECTED_TEST_ROC_AUC,
        atol=METRIC_TOLERANCE,
        rtol=0,
    ):
        raise RuntimeError(
            "La ROC-AUC reproducida no coincide "
            "con la evaluación final oficial "
            "de v10. Se detiene el análisis."
        )

    return (
        pr_auc,
        roc_auc,
    )


# =============================================================================
# MUESTRA PARA PERMUTATION IMPORTANCE
# =============================================================================

def build_explainability_sample(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Incluye:

    - todos los positivos de TEST;
    - 50.000 negativos seleccionados
      aleatoriamente con semilla fija.

    La prevalencia de esta muestra es distinta
    de la prevalencia real de TEST.

    Por ello ROC-AUC será la métrica primaria
    de Permutation Importance.

    Average Precision se conserva únicamente
    como métrica complementaria.
    """

    positives = df.loc[
        df[TARGET].eq(
            1
        )
    ].copy()

    negatives = df.loc[
        df[TARGET].eq(
            0
        )
    ].copy()

    n_negative = min(
        NEGATIVE_SAMPLE_SIZE,
        len(
            negatives
        ),
    )

    negative_sample = (
        negatives.sample(
            n=n_negative,
            random_state=RANDOM_STATE,
            replace=False,
        )
    )

    sample = pd.concat(
        [
            positives,
            negative_sample,
        ],
        ignore_index=True,
    )

    sample = (
        sample
        .sample(
            frac=1.0,
            random_state=RANDOM_STATE,
        )
        .reset_index(
            drop=True
        )
    )

    return sample


# =============================================================================
# PERMUTATION IMPORTANCE
# =============================================================================

def calculate_permutation_importance(
    model,
    sample: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:

    X = sample[
        FEATURES
    ]

    y = sample[
        TARGET
    ]

    baseline_scores = (
        model.predict_proba(
            X
        )[:, 1]
    )

    baseline_roc = float(
        roc_auc_score(
            y,
            baseline_scores,
        )
    )

    baseline_pr = float(
        average_precision_score(
            y,
            baseline_scores,
        )
    )

    print(
        f"Muestra explicabilidad: "
        f"{len(sample):,} observaciones"
    )

    print(
        f"Positivos incluidos:    "
        f"{int(y.sum())}"
    )

    print(
        f"Negativos incluidos:    "
        f"{int((y == 0).sum())}"
    )

    print(
        f"ROC-AUC muestra:         "
        f"{baseline_roc:.9f}"
    )

    print(
        f"PR-AUC muestra:          "
        f"{baseline_pr:.9f}"
    )

    result = permutation_importance(
        estimator=model,
        X=X,
        y=y,
        scoring={
            "roc_auc": "roc_auc",
            "average_precision": (
                "average_precision"
            ),
        },
        n_repeats=N_REPEATS,
        random_state=RANDOM_STATE,
        n_jobs=1,
    )

    importance = pd.DataFrame(
        {
            "FEATURE": FEATURES,
            "IMPORTANCE_ROC_AUC_MEAN": (
                result[
                    "roc_auc"
                ].importances_mean
            ),
            "IMPORTANCE_ROC_AUC_STD": (
                result[
                    "roc_auc"
                ].importances_std
            ),
            "IMPORTANCE_PR_AUC_MEAN": (
                result[
                    "average_precision"
                ].importances_mean
            ),
            "IMPORTANCE_PR_AUC_STD": (
                result[
                    "average_precision"
                ].importances_std
            ),
        }
    )

    importance = (
        importance
        .sort_values(
            [
                "IMPORTANCE_ROC_AUC_MEAN",
                "IMPORTANCE_PR_AUC_MEAN",
            ],
            ascending=[
                False,
                False,
            ],
        )
        .reset_index(
            drop=True
        )
    )

    importance.insert(
        0,
        "RANK",
        np.arange(
            1,
            len(
                importance
            ) + 1,
        ),
    )

    sample_metrics = {
        "n": int(
            len(
                sample
            )
        ),
        "positives": int(
            y.sum()
        ),
        "negatives": int(
            (
                y == 0
            ).sum()
        ),
        "prevalence": float(
            y.mean()
        ),
        "baseline_roc_auc": (
            baseline_roc
        ),
        "baseline_pr_auc": (
            baseline_pr
        ),
    }

    return (
        importance,
        sample_metrics,
    )


# =============================================================================
# PERFILES DE VARIABLES NUMÉRICAS
# =============================================================================

def numeric_score_profiles(
    df: pd.DataFrame,
    scores: np.ndarray,
) -> pd.DataFrame:
    """
    Divide cada variable numérica en cuantiles.

    Permite observar cómo cambia el score medio
    del modelo según diferentes rangos.

    Este análisis es descriptivo.
    No representa causalidad.
    """

    base = df[
        [
            TARGET,
        ]
        + NUMERIC_FEATURES
    ].copy()

    base["SCORE"] = scores

    rows = []

    for feature in NUMERIC_FEATURES:
        valid = base.loc[
            base[
                feature
            ].notna(),
            [
                feature,
                TARGET,
                "SCORE",
            ],
        ].copy()

        missing = base.loc[
            base[
                feature
            ].isna(),
            [
                TARGET,
                "SCORE",
            ],
        ].copy()

        if not valid.empty:
            try:
                valid["BIN"] = pd.qcut(
                    valid[
                        feature
                    ],
                    q=10,
                    duplicates="drop",
                )

                grouped = valid.groupby(
                    "BIN",
                    observed=True,
                )

                for (
                    bin_value,
                    group,
                ) in grouped:
                    rows.append(
                        {
                            "FEATURE": (
                                feature
                            ),
                            "BIN": str(
                                bin_value
                            ),
                            "IS_MISSING": (
                                False
                            ),
                            "N": int(
                                len(
                                    group
                                )
                            ),
                            "POSITIVES": int(
                                group[
                                    TARGET
                                ].sum()
                            ),
                            "PREVALENCE": float(
                                group[
                                    TARGET
                                ].mean()
                            ),
                            "VALUE_MIN": float(
                                group[
                                    feature
                                ].min()
                            ),
                            "VALUE_MAX": float(
                                group[
                                    feature
                                ].max()
                            ),
                            "VALUE_MEAN": float(
                                group[
                                    feature
                                ].mean()
                            ),
                            "VALUE_MEDIAN": float(
                                group[
                                    feature
                                ].median()
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
                        }
                    )

            except ValueError:
                rows.append(
                    {
                        "FEATURE": (
                            feature
                        ),
                        "BIN": (
                            "SIN_VARIACION_"
                            "SUFICIENTE"
                        ),
                        "IS_MISSING": (
                            False
                        ),
                        "N": int(
                            len(
                                valid
                            )
                        ),
                        "POSITIVES": int(
                            valid[
                                TARGET
                            ].sum()
                        ),
                        "PREVALENCE": float(
                            valid[
                                TARGET
                            ].mean()
                        ),
                        "VALUE_MIN": float(
                            valid[
                                feature
                            ].min()
                        ),
                        "VALUE_MAX": float(
                            valid[
                                feature
                            ].max()
                        ),
                        "VALUE_MEAN": float(
                            valid[
                                feature
                            ].mean()
                        ),
                        "VALUE_MEDIAN": float(
                            valid[
                                feature
                            ].median()
                        ),
                        "SCORE_MEAN": float(
                            valid[
                                "SCORE"
                            ].mean()
                        ),
                        "SCORE_MEDIAN": float(
                            valid[
                                "SCORE"
                            ].median()
                        ),
                    }
                )

        if not missing.empty:
            rows.append(
                {
                    "FEATURE": (
                        feature
                    ),
                    "BIN": (
                        "MISSING"
                    ),
                    "IS_MISSING": (
                        True
                    ),
                    "N": int(
                        len(
                            missing
                        )
                    ),
                    "POSITIVES": int(
                        missing[
                            TARGET
                        ].sum()
                    ),
                    "PREVALENCE": float(
                        missing[
                            TARGET
                        ].mean()
                    ),
                    "VALUE_MIN": (
                        np.nan
                    ),
                    "VALUE_MAX": (
                        np.nan
                    ),
                    "VALUE_MEAN": (
                        np.nan
                    ),
                    "VALUE_MEDIAN": (
                        np.nan
                    ),
                    "SCORE_MEAN": float(
                        missing[
                            "SCORE"
                        ].mean()
                    ),
                    "SCORE_MEDIAN": float(
                        missing[
                            "SCORE"
                        ].median()
                    ),
                }
            )

    return pd.DataFrame(
        rows
    )


# =============================================================================
# PERFILES DE VARIABLES BOOLEANAS
# =============================================================================

def boolean_score_profiles(
    df: pd.DataFrame,
    scores: np.ndarray,
) -> pd.DataFrame:

    base = df[
        [
            TARGET,
        ]
        + BOOLEAN_FEATURES
    ].copy()

    base["SCORE"] = scores

    rows = []

    for feature in BOOLEAN_FEATURES:
        values = base[
            feature
        ].copy()

        labels = (
            values
            .map(
                {
                    0.0: "0",
                    1.0: "1",
                }
            )
            .fillna(
                "MISSING"
            )
        )

        temp = pd.DataFrame(
            {
                "VALUE": labels,
                TARGET: base[
                    TARGET
                ],
                "SCORE": base[
                    "SCORE"
                ],
            }
        )

        for (
            value,
            group,
        ) in temp.groupby(
            "VALUE",
            dropna=False,
        ):
            rows.append(
                {
                    "FEATURE": (
                        feature
                    ),
                    "VALUE": str(
                        value
                    ),
                    "N": int(
                        len(
                            group
                        )
                    ),
                    "POSITIVES": int(
                        group[
                            TARGET
                        ].sum()
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
                }
            )

    return pd.DataFrame(
        rows
    )


# =============================================================================
# PERFIL DE TIPO DE COMPAÑÍA
# =============================================================================

def categorical_score_profile(
    df: pd.DataFrame,
    scores: np.ndarray,
) -> pd.DataFrame:

    tipo = (
        df[
            "tipo_compania"
        ]
        .astype("string")
        .fillna(
            "MISSING"
        )
    )

    temp = pd.DataFrame(
        {
            "TIPO_COMPANIA": (
                tipo
            ),
            TARGET: (
                df[
                    TARGET
                ].to_numpy()
            ),
            "SCORE": scores,
        }
    )

    profile = (
        temp
        .groupby(
            "TIPO_COMPANIA",
            dropna=False,
        )
        .agg(
            N=(
                TARGET,
                "size",
            ),
            POSITIVOS=(
                TARGET,
                "sum",
            ),
            PREVALENCIA=(
                TARGET,
                "mean",
            ),
            SCORE_MEAN=(
                "SCORE",
                "mean",
            ),
            SCORE_MEDIAN=(
                "SCORE",
                "median",
            ),
        )
        .reset_index()
        .sort_values(
            [
                "SCORE_MEAN",
                "N",
            ],
            ascending=[
                False,
                False,
            ],
        )
        .reset_index(
            drop=True
        )
    )

    return profile


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
            "EXPLICABILIDAD POST-TEST v10"
        )

        print()
        print(
            "Regla metodológica:"
        )

        print(
            "- El modelo v10 NO será "
            "reentrenado."
        )

        print(
            "- TEST NO se utilizará para "
            "modificar features ni "
            "hiperparámetros."
        )

        print(
            "- El análisis es exclusivamente "
            "descriptivo e interpretativo."
        )

        if not DATA_PATH.exists():
            raise FileNotFoundError(
                "No existe el dataset esperado:"
                f"\n{DATA_PATH}"
            )

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "No existe el modelo final esperado:"
                f"\n{MODEL_PATH}"
            )

        print()
        print(
            "Cargando artefacto final congelado..."
        )

        (
            artifact,
            model,
        ) = load_final_artifact()

        print(
            "Artefacto cargado."
        )

        print()
        print(
            "Validando identidad del artefacto..."
        )

        validate_artifact(
            artifact
        )

        print(
            "Artefacto confirmado."
        )

        print()
        print(
            "Recuperando categorías de "
            "tipo_compania exclusivamente "
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

        print()
        print(
            "Validando universo..."
        )

        validate_test_universe(
            test
        )

        print()
        print(
            "Reproduciendo métricas oficiales "
            "antes de interpretar el modelo..."
        )

        X_test = test[
            FEATURES
        ]

        y_test = test[
            TARGET
        ]

        test_scores = (
            model.predict_proba(
                X_test
            )[:, 1]
        )

        (
            full_pr_auc,
            full_roc_auc,
        ) = validate_reproduced_metrics(
            y_true=y_test,
            scores=test_scores,
        )

        print()
        print(
            "Integridad confirmada: "
            "las métricas coinciden con "
            "la evaluación final v10."
        )

        print_header(
            "PERMUTATION IMPORTANCE"
        )

        sample = (
            build_explainability_sample(
                test
            )
        )

        (
            importance,
            sample_metrics,
        ) = calculate_permutation_importance(
            model=model,
            sample=sample,
        )

        importance.to_csv(
            OUT_IMPORTANCE,
            index=False,
            encoding="utf-8-sig",
        )

        print()
        print(
            "Top 15 variables por caída media "
            "de ROC-AUC al permutar:"
        )

        print(
            importance[
                [
                    "RANK",
                    "FEATURE",
                    "IMPORTANCE_ROC_AUC_MEAN",
                    "IMPORTANCE_ROC_AUC_STD",
                    "IMPORTANCE_PR_AUC_MEAN",
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
            "PERFILES DESCRIPTIVOS DE SCORE"
        )

        numeric_profile = (
            numeric_score_profiles(
                test,
                test_scores,
            )
        )

        boolean_profile = (
            boolean_score_profiles(
                test,
                test_scores,
            )
        )

        categorical_profile = (
            categorical_score_profile(
                test,
                test_scores,
            )
        )

        numeric_profile.to_csv(
            OUT_NUMERIC_PROFILE,
            index=False,
            encoding="utf-8-sig",
        )

        boolean_profile.to_csv(
            OUT_BOOLEAN_PROFILE,
            index=False,
            encoding="utf-8-sig",
        )

        categorical_profile.to_csv(
            OUT_CATEGORICAL_PROFILE,
            index=False,
            encoding="utf-8-sig",
        )

        warnings_list = [
            str(
                w.message
            )
            for w in caught
        ]

    metadata = {
        "project": (
            "Prospect Finder BVQ"
        ),
        "version": (
            "v10"
        ),
        "analysis": (
            "post_test_explainability"
        ),
        "model": (
            EXPECTED_MODEL_NAME
        ),
        "configuration": (
            EXPECTED_CONFIG_ID
        ),
        "artifact_structure": (
            "joblib dictionary containing "
            "the estimator under key 'model'"
        ),
        "model_retrained": (
            False
        ),
        "test_used_for_model_selection": (
            False
        ),
        "purpose": (
            "Interpretar el modelo v10 ya "
            "cerrado sin modificar features, "
            "hiperparametros ni decisiones "
            "de seleccion."
        ),
        "integrity_check": {
            "expected_test_n": (
                EXPECTED_TEST_N
            ),
            "expected_test_positives": (
                EXPECTED_TEST_POSITIVES
            ),
            "expected_pr_auc": (
                EXPECTED_TEST_PR_AUC
            ),
            "expected_roc_auc": (
                EXPECTED_TEST_ROC_AUC
            ),
            "reproduced_pr_auc": (
                full_pr_auc
            ),
            "reproduced_roc_auc": (
                full_roc_auc
            ),
            "tolerance": (
                METRIC_TOLERANCE
            ),
            "passed": (
                True
            ),
        },
        "permutation_importance": {
            "primary_scoring": (
                "roc_auc"
            ),
            "secondary_scoring": (
                "average_precision"
            ),
            "random_state": (
                RANDOM_STATE
            ),
            "n_repeats": (
                N_REPEATS
            ),
            "negative_sample_size_requested": (
                NEGATIVE_SAMPLE_SIZE
            ),
            "sampling_rule": (
                "All TEST positives plus "
                "a fixed random sample "
                "of TEST negatives."
            ),
            "note": (
                "ROC-AUC is the primary "
                "permutation metric because "
                "the explainability sample "
                "deliberately changes prevalence. "
                "PR-AUC importance is "
                "complementary and must not "
                "be compared numerically with "
                "the official full-TEST PR-AUC."
            ),
            **sample_metrics,
        },
        "score_profiles": {
            "numeric_features": (
                len(
                    NUMERIC_FEATURES
                )
            ),
            "boolean_features": (
                len(
                    BOOLEAN_FEATURES
                )
            ),
            "categorical_features": (
                len(
                    CATEGORICAL
                )
            ),
            "numeric_binning": (
                "TEST deciles using pandas "
                "qcut with duplicate edges "
                "dropped"
            ),
            "interpretation": (
                "Descriptive association "
                "with model score; "
                "not causal effects."
            ),
        },
        "features": (
            FEATURES
        ),
        "outputs": [
            str(
                OUT_IMPORTANCE.relative_to(
                    ROOT
                )
            ),
            str(
                OUT_NUMERIC_PROFILE.relative_to(
                    ROOT
                )
            ),
            str(
                OUT_BOOLEAN_PROFILE.relative_to(
                    ROOT
                )
            ),
            str(
                OUT_CATEGORICAL_PROFILE.relative_to(
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

    print(
        OUT_IMPORTANCE
    )

    print(
        OUT_NUMERIC_PROFILE
    )

    print(
        OUT_BOOLEAN_PROFILE
    )

    print(
        OUT_CATEGORICAL_PROFILE
    )

    print(
        OUT_METADATA
    )

    print_header(
        "ANÁLISIS DE EXPLICABILIDAD "
        "v10 COMPLETADO"
    )

    print()
    print(
        "Este análisis no modifica el "
        "modelo final ni los resultados "
        "oficiales de TEST."
    )


if __name__ == "__main__":
    main()