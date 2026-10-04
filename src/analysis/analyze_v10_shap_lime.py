from __future__ import annotations

import importlib.metadata as package_metadata
import json
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from lime.lime_tabular import LimeTabularExplainer
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
)

from analyze_v10_explainability import (
    BOOLEAN_FEATURES,
    CATEGORICAL,
    DATA_PATH,
    EXPECTED_CONFIG_ID,
    EXPECTED_MODEL_NAME,
    EXPECTED_TEST_N,
    EXPECTED_TEST_POSITIVES,
    EXPECTED_TEST_PR_AUC,
    EXPECTED_TEST_ROC_AUC,
    FEATURES,
    MODEL_PATH,
    NUMERIC_FEATURES,
    RANDOM_STATE,
    ROOT,
    TARGET,
    load_final_artifact,
    load_test,
    load_train_categories,
    normalize_boolean,
    validate_artifact,
    validate_test_universe,
)


# =============================================================================
# CONFIGURACIÓN
# =============================================================================

TRAIN_REFERENCE_SIZE = 5_000
TRAIN_SAMPLE_PER_CHUNK = 2_000

SHAP_BACKGROUND_SIZE = 75
SHAP_GLOBAL_SIZE = 150

SHAP_MISSING_SENTINEL = (
    -9_876_543_210_123.0
)

SHAP_MAX_EVALS = (
    2 * len(FEATURES)
    + 1
)

LIME_NUM_SAMPLES = 5_000

METRIC_TOLERANCE = 1e-6
SHAP_LOCAL_TOLERANCE = 1e-4


OUTPUT_DIR = (
    ROOT
    / "reports"
    / "results"
    / "v10"
    / "explainability"
    / "shap_lime"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_SHAP_GLOBAL = (
    OUTPUT_DIR
    / "v10_shap_global_importance.csv"
)

OUT_SHAP_LOCAL = (
    OUTPUT_DIR
    / "v10_shap_local_explanations.csv"
)

OUT_SHAP_PLOT = (
    OUTPUT_DIR
    / "v10_shap_global_importance.png"
)

OUT_LIME_LOCAL = (
    OUTPUT_DIR
    / "v10_lime_local_explanations.csv"
)

OUT_CASES = (
    OUTPUT_DIR
    / "v10_explainability_local_cases.csv"
)

OUT_METADATA = (
    OUTPUT_DIR
    / "v10_shap_lime_metadata.json"
)


# =============================================================================
# FUNCIONES GENERALES
# =============================================================================


def print_header(
    title: str,
) -> None:

    line = "=" * 120

    print()
    print(line)
    print(title)
    print(line)


# =============================================================================
# NORMALIZACIÓN
# =============================================================================


def normalize_feature_frame(
    df: pd.DataFrame,
    train_categories: list[str],
) -> pd.DataFrame:
    """
    Replica la preparación utilizada por
    analyze_v10_explainability.py.

    No se modifica ninguna variable del
    modelo v10.
    """

    out = df.copy()

    for col in NUMERIC_FEATURES:

        out[col] = pd.to_numeric(
            out[col],
            errors="coerce",
        )

        out[col] = (
            out[col]
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

        out[col] = normalize_boolean(
            out[col]
        )

    tipo = (
        out["tipo_compania"]
        .astype("string")
    )

    out["tipo_compania"] = (
        pd.Categorical(
            tipo,
            categories=train_categories,
        )
    )

    return out


# =============================================================================
# MUESTRA DE REFERENCIA TRAIN
# =============================================================================


def load_train_reference(
    train_categories: list[str],
) -> pd.DataFrame:
    """
    Construye una muestra reproducible
    exclusivamente desde TRAIN.

    TRAIN se utiliza como referencia
    para SHAP y LIME.

    TEST no participa en la construcción
    de esta referencia.
    """

    frames: list[pd.DataFrame] = []

    usecols = [
        "SPLIT",
    ] + FEATURES

    for chunk_index, chunk in enumerate(
        pd.read_csv(
            DATA_PATH,
            usecols=usecols,
            chunksize=200_000,
            low_memory=False,
        )
    ):

        train_chunk = chunk.loc[
            chunk["SPLIT"].eq(
                "TRAIN"
            ),
            FEATURES,
        ].copy()

        if train_chunk.empty:
            continue

        sample_size = min(
            TRAIN_SAMPLE_PER_CHUNK,
            len(train_chunk),
        )

        sampled = train_chunk.sample(
            n=sample_size,
            random_state=(
                RANDOM_STATE
                + chunk_index
            ),
        )

        frames.append(
            sampled
        )

    if not frames:

        raise RuntimeError(
            "No se encontraron "
            "observaciones TRAIN."
        )

    reference = pd.concat(
        frames,
        ignore_index=True,
    )

    if len(reference) > TRAIN_REFERENCE_SIZE:

        reference = reference.sample(
            n=TRAIN_REFERENCE_SIZE,
            random_state=RANDOM_STATE,
        )

    reference = (
        normalize_feature_frame(
            reference,
            train_categories,
        )
    )

    reference = reference.reset_index(
        drop=True
    )

    return reference


# =============================================================================
# CODIFICACIÓN PARA SHAP
# =============================================================================


def encode_for_shap(
    df: pd.DataFrame,
) -> np.ndarray:
    """
    Convierte las 25 variables a una
    representación numérica compatible
    con SHAP.

    Los NaN se representan temporalmente
    mediante un sentinel.

    Antes de predecir se restauran
    nuevamente como NaN.
    """

    matrix = np.empty(
        (
            len(df),
            len(FEATURES),
        ),
        dtype="float64",
    )

    for feature_index, feature in enumerate(
        FEATURES
    ):

        if feature in CATEGORICAL:

            codes = (
                df[feature]
                .cat.codes
                .to_numpy(
                    dtype="float64",
                    copy=True,
                )
            )

            matrix[
                :,
                feature_index,
            ] = codes

        else:

            values = pd.to_numeric(
                df[feature],
                errors="coerce",
            ).to_numpy(
                dtype="float64",
                copy=True,
            )

            values[
                np.isnan(
                    values
                )
            ] = SHAP_MISSING_SENTINEL

            matrix[
                :,
                feature_index,
            ] = values

    return matrix


def decode_shap_matrix(
    matrix,
    train_categories: list[str],
) -> pd.DataFrame:
    """
    Reconstruye el DataFrame original
    esperado por el modelo v10.
    """

    arr = np.asarray(
        matrix,
        dtype="float64",
    )

    if arr.ndim == 1:

        arr = arr.reshape(
            1,
            -1,
        )

    if arr.shape[1] != len(FEATURES):

        raise ValueError(
            "La matriz SHAP no contiene "
            "el número esperado de variables."
        )

    data: dict[str, object] = {}

    for feature_index, feature in enumerate(
        FEATURES
    ):

        values = arr[
            :,
            feature_index,
        ].copy()

        if feature in CATEGORICAL:

            labels: list[object] = []

            for raw_value in values:

                if not np.isfinite(
                    raw_value
                ):

                    labels.append(
                        pd.NA
                    )

                    continue

                code = int(
                    round(
                        float(
                            raw_value
                        )
                    )
                )

                if (
                    code < 0
                    or code
                    >= len(
                        train_categories
                    )
                ):

                    labels.append(
                        pd.NA
                    )

                else:

                    labels.append(
                        train_categories[
                            code
                        ]
                    )

            data[feature] = (
                pd.Categorical(
                    labels,
                    categories=train_categories,
                )
            )

        else:

            values[
                values
                == SHAP_MISSING_SENTINEL
            ] = np.nan

            data[feature] = (
                values.astype(
                    "float64"
                )
            )

    return pd.DataFrame(
        data,
        columns=FEATURES,
    )


# =============================================================================
# CODIFICACIÓN PARA LIME
# =============================================================================


def build_lime_reference(
    train_reference: pd.DataFrame,
    train_categories: list[str],
):
    """
    LIME necesita una matriz numérica
    sin valores NaN.

    Para su referencia interna se
    utilizan medianas calculadas
    exclusivamente desde TRAIN.

    Los casos locales se seleccionan
    entre registros completos de TEST
    para no alterar su score original.
    """

    medians: dict[str, float] = {}

    matrix = np.empty(
        (
            len(train_reference),
            len(FEATURES),
        ),
        dtype="float64",
    )

    for feature_index, feature in enumerate(
        FEATURES
    ):

        if feature in CATEGORICAL:

            codes = (
                train_reference[
                    feature
                ]
                .cat.codes
                .to_numpy(
                    dtype="float64",
                    copy=True,
                )
            )

            missing_code = float(
                len(
                    train_categories
                )
            )

            codes[
                codes < 0
            ] = missing_code

            matrix[
                :,
                feature_index,
            ] = codes

        else:

            values = pd.to_numeric(
                train_reference[
                    feature
                ],
                errors="coerce",
            ).to_numpy(
                dtype="float64",
                copy=True,
            )

            finite = values[
                np.isfinite(
                    values
                )
            ]

            if finite.size == 0:

                median = 0.0

            else:

                median = float(
                    np.median(
                        finite
                    )
                )

            medians[
                feature
            ] = median

            values[
                ~np.isfinite(
                    values
                )
            ] = median

            matrix[
                :,
                feature_index,
            ] = values

    categorical_index = (
        FEATURES.index(
            "tipo_compania"
        )
    )

    categorical_names = {
        categorical_index: (
            train_categories
            + [
                "<MISSING>",
            ]
        )
    }

    return (
        matrix,
        medians,
        categorical_index,
        categorical_names,
    )


def encode_row_for_lime(
    row: pd.Series,
    medians: dict[str, float],
    train_categories: list[str],
) -> np.ndarray:

    values: list[float] = []

    category_to_code = {
        category: index
        for index, category in enumerate(
            train_categories
        )
    }

    missing_category_code = float(
        len(
            train_categories
        )
    )

    for feature in FEATURES:

        value = row[
            feature
        ]

        if feature in CATEGORICAL:

            if pd.isna(
                value
            ):

                values.append(
                    missing_category_code
                )

            else:

                code = category_to_code.get(
                    str(value)
                )

                if code is None:

                    values.append(
                        missing_category_code
                    )

                else:

                    values.append(
                        float(
                            code
                        )
                    )

        else:

            numeric = pd.to_numeric(
                pd.Series(
                    [value]
                ),
                errors="coerce",
            ).iloc[0]

            if pd.isna(
                numeric
            ):

                numeric = medians[
                    feature
                ]

            values.append(
                float(
                    numeric
                )
            )

    return np.asarray(
        values,
        dtype="float64",
    )


def decode_lime_matrix(
    matrix,
    train_categories: list[str],
) -> pd.DataFrame:

    arr = np.asarray(
        matrix,
        dtype="float64",
    )

    if arr.ndim == 1:

        arr = arr.reshape(
            1,
            -1,
        )

    if arr.shape[1] != len(FEATURES):

        raise ValueError(
            "La matriz LIME no contiene "
            "el número esperado de variables."
        )

    data: dict[str, object] = {}

    categorical_index = (
        FEATURES.index(
            "tipo_compania"
        )
    )

    for feature_index, feature in enumerate(
        FEATURES
    ):

        values = arr[
            :,
            feature_index,
        ].copy()

        if feature_index == categorical_index:

            labels: list[object] = []

            for raw_value in values:

                if not np.isfinite(
                    raw_value
                ):

                    labels.append(
                        pd.NA
                    )

                    continue

                code = int(
                    round(
                        float(
                            raw_value
                        )
                    )
                )

                if (
                    code < 0
                    or code
                    >= len(
                        train_categories
                    )
                ):

                    labels.append(
                        pd.NA
                    )

                else:

                    labels.append(
                        train_categories[
                            code
                        ]
                    )

            data[feature] = (
                pd.Categorical(
                    labels,
                    categories=train_categories,
                )
            )

        else:

            data[feature] = (
                values.astype(
                    "float64"
                )
            )

    return pd.DataFrame(
        data,
        columns=FEATURES,
    )


# =============================================================================
# VALIDACIÓN DEL MODELO
# =============================================================================


def reproduce_official_metrics(
    model,
    test: pd.DataFrame,
) -> np.ndarray:

    x_test = test[
        FEATURES
    ]

    y_test = (
        test[
            TARGET
        ]
        .to_numpy(
            dtype="int8"
        )
    )

    scores = (
        model.predict_proba(
            x_test
        )[
            :,
            1,
        ]
    )

    pr_auc = (
        average_precision_score(
            y_test,
            scores,
        )
    )

    roc_auc = (
        roc_auc_score(
            y_test,
            scores,
        )
    )

    print(
        f"PR-AUC TEST reproducido:  "
        f"{pr_auc:.9f}"
    )

    print(
        f"ROC-AUC TEST reproducido: "
        f"{roc_auc:.9f}"
    )

    if abs(
        pr_auc
        - EXPECTED_TEST_PR_AUC
    ) > METRIC_TOLERANCE:

        raise RuntimeError(
            "La PR-AUC reproducida no "
            "coincide con el resultado "
            "oficial de v10."
        )

    if abs(
        roc_auc
        - EXPECTED_TEST_ROC_AUC
    ) > METRIC_TOLERANCE:

        raise RuntimeError(
            "La ROC-AUC reproducida no "
            "coincide con el resultado "
            "oficial de v10."
        )

    return scores


# =============================================================================
# CASOS PARA EXPLICABILIDAD LOCAL
# =============================================================================


def complete_case_mask(
    test: pd.DataFrame,
) -> pd.Series:

    mask = pd.Series(
        True,
        index=test.index,
    )

    for feature in FEATURES:

        if feature in CATEGORICAL:

            mask &= (
                test[
                    feature
                ]
                .notna()
            )

        else:

            values = pd.to_numeric(
                test[
                    feature
                ],
                errors="coerce",
            )

            mask &= (
                values.notna()
            )

    return mask


def select_local_cases(
    test: pd.DataFrame,
    scores: np.ndarray,
) -> pd.DataFrame:
    """
    Selecciona tres casos completos:

    1. mayor score entre casos completos;
    2. mejor positivo real entre casos completos;
    3. caso cercano a la mediana del score.

    La selección se realiza después de
    cerrado v10 y únicamente con fines
    de explicación.
    """

    base = test[
        [
            "ANIO",
            "EXPEDIENTE_KEY",
            TARGET,
        ]
        + FEATURES
    ].copy()

    base[
        "SCORE_V10"
    ] = scores

    base[
        "COMPLETE_CASE"
    ] = complete_case_mask(
        test
    )

    eligible = base.loc[
        base[
            "COMPLETE_CASE"
        ]
    ].copy()

    if eligible.empty:

        raise RuntimeError(
            "No existen casos completos "
            "en TEST."
        )

    chosen_indices: list[int] = []

    labels: dict[
        int,
        str,
    ] = {}

    # -------------------------------------------------------------------------
    # Caso 1: mayor score completo
    # -------------------------------------------------------------------------

    top_index = (
        eligible[
            "SCORE_V10"
        ]
        .idxmax()
    )

    chosen_indices.append(
        top_index
    )

    labels[
        top_index
    ] = (
        "TOP_SCORE_COMPLETO_TEST"
    )

    # -------------------------------------------------------------------------
    # Caso 2: mejor positivo real
    # -------------------------------------------------------------------------

    positives = (
        eligible.loc[
            eligible[
                TARGET
            ].eq(1)
        ]
        .sort_values(
            "SCORE_V10",
            ascending=False,
        )
    )

    for positive_index in positives.index:

        if (
            positive_index
            not in chosen_indices
        ):

            chosen_indices.append(
                positive_index
            )

            labels[
                positive_index
            ] = (
                "MEJOR_POSITIVO_COMPLETO_TEST"
            )

            break

    # -------------------------------------------------------------------------
    # Caso 3: score cercano a mediana
    # -------------------------------------------------------------------------

    target_median = float(
        eligible[
            "SCORE_V10"
        ].median()
    )

    candidates = (
        eligible
        .assign(
            DIST_MEDIANA=lambda frame: (
                frame[
                    "SCORE_V10"
                ]
                - target_median
            ).abs()
        )
        .sort_values(
            "DIST_MEDIANA"
        )
    )

    for median_index in candidates.index:

        if (
            median_index
            not in chosen_indices
        ):

            chosen_indices.append(
                median_index
            )

            labels[
                median_index
            ] = (
                "SCORE_MEDIANO_COMPLETO_TEST"
            )

            break

    # -------------------------------------------------------------------------
    # Fallback
    # -------------------------------------------------------------------------

    if len(chosen_indices) < 3:

        for fallback_index in (
            eligible
            .sort_values(
                "SCORE_V10",
                ascending=False,
            )
            .index
        ):

            if (
                fallback_index
                in chosen_indices
            ):

                continue

            chosen_indices.append(
                fallback_index
            )

            labels[
                fallback_index
            ] = (
                "CASO_ADICIONAL_"
                f"{len(chosen_indices)}"
            )

            if len(chosen_indices) >= 3:
                break

    cases = base.loc[
        chosen_indices
    ].copy()

    cases.insert(
        0,
        "CASE_ID",
        [
            labels[
                index
            ]
            for index
            in chosen_indices
        ],
    )

    cases = cases.reset_index(
        names="TEST_INDEX"
    )

    return cases


# =============================================================================
# SHAP
# =============================================================================


def run_shap(
    model,
    train_reference: pd.DataFrame,
    test: pd.DataFrame,
    local_cases: pd.DataFrame,
    train_categories: list[str],
):
    """
    SHAP model-agnostic mediante
    PermutationExplainer.

    Esto evita alterar o reconstruir
    internamente el modelo congelado v10.
    """

    print_header(
        "SHAP - EXPLICACIÓN GLOBAL"
    )

    background = (
        train_reference.sample(
            n=min(
                SHAP_BACKGROUND_SIZE,
                len(
                    train_reference
                ),
            ),
            random_state=RANDOM_STATE,
        )
    )

    global_sample = test.sample(
        n=min(
            SHAP_GLOBAL_SIZE,
            len(test),
        ),
        random_state=RANDOM_STATE,
    )

    background_matrix = (
        encode_for_shap(
            background[
                FEATURES
            ]
        )
    )

    global_matrix = (
        encode_for_shap(
            global_sample[
                FEATURES
            ]
        )
    )

    def predict_positive(
        matrix,
    ) -> np.ndarray:

        frame = decode_shap_matrix(
            matrix,
            train_categories,
        )

        return (
            model.predict_proba(
                frame
            )[
                :,
                1,
            ]
        )

    explainer = shap.Explainer(
        predict_positive,
        background_matrix,
        algorithm="permutation",
        feature_names=FEATURES,
    )

    print(
        f"Background TRAIN: "
        f"{len(background_matrix):,}"
    )

    print(
        f"Muestra global TEST: "
        f"{len(global_matrix):,}"
    )

    shap_values_global = (
        explainer(
            global_matrix,
            max_evals=SHAP_MAX_EVALS,
        )
    )

    mean_abs_shap = np.mean(
        np.abs(
            shap_values_global.values
        ),
        axis=0,
    )

    global_df = pd.DataFrame(
        {
            "FEATURE": FEATURES,
            "MEAN_ABS_SHAP": (
                mean_abs_shap
            ),
        }
    )

    global_df = global_df.sort_values(
        "MEAN_ABS_SHAP",
        ascending=False,
    )

    global_df.insert(
        0,
        "RANK",
        np.arange(
            1,
            len(global_df) + 1,
        ),
    )

    global_df.to_csv(
        OUT_SHAP_GLOBAL,
        index=False,
    )

    # -------------------------------------------------------------------------
    # Gráfico global
    # -------------------------------------------------------------------------

    plot_df = (
        global_df
        .head(15)
        .sort_values(
            "MEAN_ABS_SHAP",
            ascending=True,
        )
    )

    plt.figure(
        figsize=(
            10,
            7,
        )
    )

    plt.barh(
        plot_df[
            "FEATURE"
        ],
        plot_df[
            "MEAN_ABS_SHAP"
        ],
    )

    plt.xlabel(
        "Promedio de |SHAP|"
    )

    plt.ylabel(
        "Variable"
    )

    plt.title(
        "v10 - Importancia global SHAP"
    )

    plt.tight_layout()

    plt.savefig(
        OUT_SHAP_PLOT,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close()

    # =========================================================================
    # SHAP LOCAL
    # =========================================================================

    print_header(
        "SHAP - EXPLICACIONES LOCALES"
    )

    local_rows: list[dict] = []

    for _, case in (
        local_cases.iterrows()
    ):

        case_id = str(
            case[
                "CASE_ID"
            ]
        )

        case_frame = pd.DataFrame(
            [
                {
                    feature: (
                        case[
                            feature
                        ]
                    )
                    for feature
                    in FEATURES
                }
            ]
        )

        case_frame = (
            normalize_feature_frame(
                case_frame,
                train_categories,
            )
        )

        case_matrix = (
            encode_for_shap(
                case_frame[
                    FEATURES
                ]
            )
        )

        case_values = explainer(
            case_matrix,
            max_evals=SHAP_MAX_EVALS,
        )

        values = (
            case_values
            .values[
                0
            ]
        )

        base_value = float(
            np.asarray(
                case_values
                .base_values
            )
            .reshape(
                -1
            )[
                0
            ]
        )

        model_score = float(
            model.predict_proba(
                case_frame[
                    FEATURES
                ]
            )[
                0,
                1,
            ]
        )

        reconstructed_score = float(
            base_value
            + values.sum()
        )

        local_error = abs(
            model_score
            - reconstructed_score
        )

        print()
        print(
            f"{case_id}"
        )

        print(
            f"Score modelo: "
            f"{model_score:.9f}"
        )

        print(
            f"Score reconstruido SHAP: "
            f"{reconstructed_score:.9f}"
        )

        print(
            f"Error local: "
            f"{local_error:.10f}"
        )

        if (
            local_error
            > SHAP_LOCAL_TOLERANCE
        ):

            raise RuntimeError(
                "SHAP no reconstruye "
                "correctamente el score "
                f"del caso {case_id}."
            )

        for (
            feature_index,
            feature,
        ) in enumerate(
            FEATURES
        ):

            local_rows.append(
                {
                    "CASE_ID": case_id,
                    "TEST_INDEX": int(
                        case[
                            "TEST_INDEX"
                        ]
                    ),
                    "ANIO": int(
                        case[
                            "ANIO"
                        ]
                    ),
                    "EXPEDIENTE_KEY": str(
                        case[
                            "EXPEDIENTE_KEY"
                        ]
                    ),
                    "TARGET_24M": int(
                        case[
                            TARGET
                        ]
                    ),
                    "MODEL_SCORE": (
                        model_score
                    ),
                    "SHAP_BASE_VALUE": (
                        base_value
                    ),
                    "SHAP_RECONSTRUCTED_SCORE": (
                        reconstructed_score
                    ),
                    "SHAP_LOCAL_ERROR": (
                        local_error
                    ),
                    "FEATURE": feature,
                    "FEATURE_VALUE": str(
                        case[
                            feature
                        ]
                    ),
                    "SHAP_VALUE": float(
                        values[
                            feature_index
                        ]
                    ),
                    "ABS_SHAP_VALUE": float(
                        abs(
                            values[
                                feature_index
                            ]
                        )
                    ),
                }
            )

    local_df = pd.DataFrame(
        local_rows
    )

    local_df = local_df.sort_values(
        [
            "CASE_ID",
            "ABS_SHAP_VALUE",
        ],
        ascending=[
            True,
            False,
        ],
    )

    local_df.to_csv(
        OUT_SHAP_LOCAL,
        index=False,
    )

    print()
    print(
        "Top 10 variables SHAP:"
    )

    print(
        global_df
        .head(10)
        .to_string(
            index=False
        )
    )

    return (
        global_df,
        local_df,
    )


# =============================================================================
# LIME
# =============================================================================


def run_lime(
    model,
    train_reference: pd.DataFrame,
    local_cases: pd.DataFrame,
    train_categories: list[str],
):
    """
    LIME se utiliza como técnica local
    complementaria a SHAP.

    No modifica el modelo v10.
    """

    print_header(
        "LIME - EXPLICACIONES LOCALES"
    )

    (
        lime_reference,
        medians,
        categorical_index,
        categorical_names,
    ) = build_lime_reference(
        train_reference,
        train_categories,
    )

    explainer = (
        LimeTabularExplainer(
            training_data=(
                lime_reference
            ),
            feature_names=FEATURES,
            class_names=[
                "No emisor 24m",
                "Emisor 24m",
            ],
            categorical_features=[
                categorical_index,
            ],
            categorical_names=(
                categorical_names
            ),
            mode="classification",
            discretize_continuous=True,
            random_state=RANDOM_STATE,
        )
    )

    def predict_proba(
        matrix,
    ) -> np.ndarray:

        frame = decode_lime_matrix(
            matrix,
            train_categories,
        )

        return model.predict_proba(
            frame
        )

    rows: list[dict] = []

    for _, case in (
        local_cases.iterrows()
    ):

        case_id = str(
            case[
                "CASE_ID"
            ]
        )

        case_vector = (
            encode_row_for_lime(
                case,
                medians,
                train_categories,
            )
        )

        reconstructed_frame = (
            decode_lime_matrix(
                case_vector,
                train_categories,
            )
        )

        reconstructed_score = float(
            model.predict_proba(
                reconstructed_frame
            )[
                0,
                1,
            ]
        )

        original_score = float(
            case[
                "SCORE_V10"
            ]
        )

        score_error = abs(
            reconstructed_score
            - original_score
        )

        if (
            score_error
            > METRIC_TOLERANCE
        ):

            raise RuntimeError(
                "La transformación utilizada "
                "para LIME alteró el score "
                f"del caso {case_id}. "
                f"Error={score_error:.10f}"
            )

        explanation = (
            explainer.explain_instance(
                data_row=case_vector,
                predict_fn=predict_proba,
                labels=[
                    1,
                ],
                num_features=len(
                    FEATURES
                ),
                num_samples=(
                    LIME_NUM_SAMPLES
                ),
            )
        )

        local_prediction = None

        if (
            explanation.local_pred
            is not None
        ):

            local_array = (
                np.asarray(
                    explanation.local_pred
                )
                .reshape(
                    -1
                )
            )

            if len(local_array) > 0:

                local_prediction = (
                    float(
                        local_array[
                            0
                        ]
                    )
                )

        print()
        print(
            case_id
        )

        print(
            f"Score v10: "
            f"{original_score:.9f}"
        )

        if (
            local_prediction
            is not None
        ):

            print(
                "Aproximación local LIME: "
                f"{local_prediction:.9f}"
            )

        for rank, (
            term,
            weight,
        ) in enumerate(
            explanation.as_list(
                label=1
            ),
            start=1,
        ):

            rows.append(
                {
                    "CASE_ID": case_id,
                    "TEST_INDEX": int(
                        case[
                            "TEST_INDEX"
                        ]
                    ),
                    "ANIO": int(
                        case[
                            "ANIO"
                        ]
                    ),
                    "EXPEDIENTE_KEY": str(
                        case[
                            "EXPEDIENTE_KEY"
                        ]
                    ),
                    "TARGET_24M": int(
                        case[
                            TARGET
                        ]
                    ),
                    "MODEL_SCORE": (
                        original_score
                    ),
                    "LIME_LOCAL_PREDICTION": (
                        local_prediction
                    ),
                    "LIME_RANK": rank,
                    "LIME_TERM": term,
                    "LIME_WEIGHT": float(
                        weight
                    ),
                    "ABS_LIME_WEIGHT": float(
                        abs(
                            weight
                        )
                    ),
                }
            )

        html_path = (
            OUTPUT_DIR
            / (
                "v10_lime_"
                + case_id.lower()
                + ".html"
            )
        )

        explanation.save_to_file(
            str(
                html_path
            )
        )

    lime_df = pd.DataFrame(
        rows
    )

    lime_df = lime_df.sort_values(
        [
            "CASE_ID",
            "ABS_LIME_WEIGHT",
        ],
        ascending=[
            True,
            False,
        ],
    )

    lime_df.to_csv(
        OUT_LIME_LOCAL,
        index=False,
    )

    return lime_df


# =============================================================================
# METADATA
# =============================================================================


def save_metadata(
    train_reference: pd.DataFrame,
    test: pd.DataFrame,
    local_cases: pd.DataFrame,
    shap_global: pd.DataFrame,
    shap_local: pd.DataFrame,
    lime_local: pd.DataFrame,
) -> None:

    result = {
        "analysis": (
            "v10_post_test_shap_lime"
        ),
        "model_name": (
            EXPECTED_MODEL_NAME
        ),
        "config_id": (
            EXPECTED_CONFIG_ID
        ),
        "purpose": (
            "Analisis post-test de "
            "explicabilidad. No modifica "
            "modelo, variables, "
            "hiperparametros ni decisiones "
            "de seleccion."
        ),
        "model_path": str(
            MODEL_PATH.relative_to(
                ROOT
            )
        ),
        "data_path": str(
            DATA_PATH.relative_to(
                ROOT
            )
        ),
        "methodology": {
            "shap": (
                "SHAP model-agnostic mediante "
                "PermutationExplainer. "
                "El background se obtiene "
                "exclusivamente desde TRAIN."
            ),
            "lime": (
                "LIME Tabular utilizado como "
                "tecnica complementaria para "
                "explicaciones locales. "
                "La referencia se obtiene "
                "exclusivamente desde TRAIN."
            ),
            "test_role": (
                "TEST se utiliza únicamente "
                "para explicar predicciones "
                "del modelo v10 ya congelado."
            ),
            "lime_missing_values": (
                "LIME requiere una matriz "
                "interna sin NaN. Las medianas "
                "se calculan exclusivamente "
                "desde TRAIN. Los casos locales "
                "se seleccionan entre registros "
                "completos de TEST."
            ),
        },
        "versions": {
            "shap": (
                package_metadata.version(
                    "shap"
                )
            ),
            "lime": (
                package_metadata.version(
                    "lime"
                )
            ),
            "numpy": (
                package_metadata.version(
                    "numpy"
                )
            ),
            "pandas": (
                package_metadata.version(
                    "pandas"
                )
            ),
            "scikit_learn": (
                package_metadata.version(
                    "scikit-learn"
                )
            ),
        },
        "sample_sizes": {
            "train_reference": int(
                len(
                    train_reference
                )
            ),
            "shap_background": int(
                min(
                    SHAP_BACKGROUND_SIZE,
                    len(
                        train_reference
                    ),
                )
            ),
            "shap_global_test": int(
                min(
                    SHAP_GLOBAL_SIZE,
                    len(
                        test
                    ),
                )
            ),
            "local_cases": int(
                len(
                    local_cases
                )
            ),
            "lime_num_samples_per_case": (
                LIME_NUM_SAMPLES
            ),
        },
        "features": FEATURES,
        "local_cases": [
            {
                "case_id": str(
                    row[
                        "CASE_ID"
                    ]
                ),
                "test_index": int(
                    row[
                        "TEST_INDEX"
                    ]
                ),
                "anio": int(
                    row[
                        "ANIO"
                    ]
                ),
                "expediente_key": str(
                    row[
                        "EXPEDIENTE_KEY"
                    ]
                ),
                "target_24m": int(
                    row[
                        TARGET
                    ]
                ),
                "score_v10": float(
                    row[
                        "SCORE_V10"
                    ]
                ),
            }
            for _, row
            in local_cases.iterrows()
        ],
        "outputs": {
            "shap_global": str(
                OUT_SHAP_GLOBAL.relative_to(
                    ROOT
                )
            ),
            "shap_local": str(
                OUT_SHAP_LOCAL.relative_to(
                    ROOT
                )
            ),
            "shap_plot": str(
                OUT_SHAP_PLOT.relative_to(
                    ROOT
                )
            ),
            "lime_local": str(
                OUT_LIME_LOCAL.relative_to(
                    ROOT
                )
            ),
            "cases": str(
                OUT_CASES.relative_to(
                    ROOT
                )
            ),
        },
        "rows_generated": {
            "shap_global": int(
                len(
                    shap_global
                )
            ),
            "shap_local": int(
                len(
                    shap_local
                )
            ),
            "lime_local": int(
                len(
                    lime_local
                )
            ),
        },
    }

    with OUT_METADATA.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False,
        )


# =============================================================================
# MAIN
# =============================================================================


def main() -> None:

    warnings.filterwarnings(
        "ignore",
        category=FutureWarning,
    )

    print_header(
        "V10 - ANÁLISIS SHAP + LIME"
    )

    print(
        "Análisis exclusivamente "
        "post-test."
    )

    print(
        "El modelo v10 permanece "
        "congelado."
    )

    # =========================================================================
    # Archivos
    # =========================================================================

    if not DATA_PATH.exists():

        raise FileNotFoundError(
            "No existe el dataset "
            f"esperado:\n{DATA_PATH}"
        )

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            "No existe el modelo "
            f"esperado:\n{MODEL_PATH}"
        )

    # =========================================================================
    # Modelo
    # =========================================================================

    print_header(
        "VALIDACIÓN DEL ARTEFACTO"
    )

    artifact, model = (
        load_final_artifact()
    )

    validate_artifact(
        artifact
    )

    # =========================================================================
    # Categorías TRAIN
    # =========================================================================

    print_header(
        "CATEGORÍAS APRENDIDAS EN TRAIN"
    )

    train_categories = (
        load_train_categories()
    )

    print(
        "Número de categorías "
        f"tipo_compania: "
        f"{len(train_categories)}"
    )

    # =========================================================================
    # TEST
    # =========================================================================

    print_header(
        "CARGA DEL UNIVERSO TEST"
    )

    test = load_test(
        train_categories
    )

    validate_test_universe(
        test
    )

    if (
        len(test)
        != EXPECTED_TEST_N
    ):

        raise RuntimeError(
            "El número de filas TEST "
            "no coincide con v10."
        )

    if (
        int(
            test[
                TARGET
            ].sum()
        )
        != EXPECTED_TEST_POSITIVES
    ):

        raise RuntimeError(
            "El número de positivos "
            "TEST no coincide con v10."
        )

    # =========================================================================
    # Integridad predictiva
    # =========================================================================

    print_header(
        "CONTROL DE INTEGRIDAD"
    )

    scores = (
        reproduce_official_metrics(
            model,
            test,
        )
    )

    # =========================================================================
    # Referencia TRAIN
    # =========================================================================

    print_header(
        "REFERENCIA PARA EXPLICABILIDAD"
    )

    train_reference = (
        load_train_reference(
            train_categories
        )
    )

    print(
        "Muestra TRAIN: "
        f"{len(train_reference):,}"
    )

    # =========================================================================
    # Casos locales
    # =========================================================================

    print_header(
        "CASOS PARA EXPLICACIÓN LOCAL"
    )

    local_cases = (
        select_local_cases(
            test,
            scores,
        )
    )

    local_cases[
        [
            "CASE_ID",
            "TEST_INDEX",
            "ANIO",
            "EXPEDIENTE_KEY",
            TARGET,
            "SCORE_V10",
        ]
    ].to_csv(
        OUT_CASES,
        index=False,
    )

    print(
        local_cases[
            [
                "CASE_ID",
                "ANIO",
                "EXPEDIENTE_KEY",
                TARGET,
                "SCORE_V10",
            ]
        ].to_string(
            index=False
        )
    )

    # =========================================================================
    # SHAP
    # =========================================================================

    (
        shap_global,
        shap_local,
    ) = run_shap(
        model,
        train_reference,
        test,
        local_cases,
        train_categories,
    )

    # =========================================================================
    # LIME
    # =========================================================================

    lime_local = run_lime(
        model,
        train_reference,
        local_cases,
        train_categories,
    )

    # =========================================================================
    # Metadata
    # =========================================================================

    save_metadata(
        train_reference,
        test,
        local_cases,
        shap_global,
        shap_local,
        lime_local,
    )

    # =========================================================================
    # Fin
    # =========================================================================

    print_header(
        "ANÁLISIS FINALIZADO"
    )

    print(
        "Resultados guardados en:"
    )

    print(
        OUTPUT_DIR
    )

    print()

    print(
        OUT_SHAP_GLOBAL.name
    )

    print(
        OUT_SHAP_LOCAL.name
    )

    print(
        OUT_SHAP_PLOT.name
    )

    print(
        OUT_LIME_LOCAL.name
    )

    print(
        OUT_CASES.name
    )

    print(
        OUT_METADATA.name
    )


if __name__ == "__main__":
    main()


