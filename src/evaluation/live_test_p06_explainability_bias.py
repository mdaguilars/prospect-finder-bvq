"""
P06 · Explicabilidad y sesgo
Prospect Finder BVQ

Objetivo
--------
Comparar las explicaciones SHAP de dos empresas del conjunto TEST:

1. una empresa de mayor tamaño;
2. una empresa de menor tamaño.

Para mejorar la comparabilidad:

- ambas pertenecen a TEST 2023;
- ambas tienen las 25 variables disponibles;
- ambas pertenecen al mismo tipo de compañía;
- el caso grande se selecciona próximo al P90 de activos;
- el caso pequeño se selecciona próximo al P10 de activos.

La prueba utiliza:

- modelo final v10 congelado;
- 25 variables congeladas;
- categorías aprendidas exclusivamente desde TRAIN;
- background SHAP obtenido exclusivamente desde TRAIN;
- SHAP PermutationExplainer.

IMPORTANTE
----------
Los valores SHAP explican la contribución de las variables
al score generado por el modelo.

NO representan causalidad.

No debe afirmarse:

    "la empresa obtiene mayor score porque es grande"

como relación causal.

La interpretación correcta es:

    "para esta predicción, determinadas características asociadas
     con escala, actividad, crecimiento o rentabilidad contribuyeron
     al score asignado por el modelo."

Evidencias:

    reports/live_tests/P06/
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap


# =============================================================================
# CONFIGURACIÓN
# =============================================================================

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
    / "live_tests"
    / "P06"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

RANDOM_STATE = 42

TRAIN_REFERENCE_SIZE = 5_000
TRAIN_SAMPLE_PER_CHUNK = 2_000

SHAP_BACKGROUND_SIZE = 75

SHAP_MISSING_SENTINEL = (
    -9_876_543_210_123.0
)

SHAP_LOCAL_TOLERANCE = 1e-4


# =============================================================================
# ETIQUETAS
# =============================================================================

FEATURE_LABELS = {
    "activos_final":
        "Activos",

    "patrimonio_final":
        "Patrimonio",

    "bi_ingresos_ventas":
        "Ingresos por ventas",

    "bi_n_empleados":
        "Número de empleados",

    "activos_final_t1":
        "Activos del año anterior",

    "patrimonio_final_t1":
        "Patrimonio del año anterior",

    "bi_ingresos_ventas_t1":
        "Ventas del año anterior",

    "bi_n_empleados_t1":
        "Empleados del año anterior",

    "fin_ratio_patrimonio_activos":
        "Patrimonio / activos",

    "fin_roa":
        "ROA",

    "fin_margen_neto":
        "Margen neto",

    "fin_rotacion_activos":
        "Rotación de activos",

    "fin_roe":
        "ROE",

    "fin_crecimiento_activos":
        "Crecimiento de activos",

    "fin_crecimiento_patrimonio":
        "Crecimiento de patrimonio",

    "fin_crecimiento_ventas":
        "Crecimiento de ventas",

    "fin_crecimiento_empleados":
        "Crecimiento de empleados",

    "TIENE_T_MENOS_1":
        "Información histórica disponible",

    "flag_activos_negativos":
        "Bandera activos negativos",

    "flag_ventas_negativas":
        "Bandera ventas negativas",

    "flag_empleados_fijo":
        "Bandera empleados fijos",

    "flag_empleados_salto_temporal":
        "Bandera salto empleados",

    "flag_empleados_anomalia_total":
        "Bandera anomalía empleados",

    "flag_patrimonio_no_positivo":
        "Bandera patrimonio no positivo",

    "tipo_compania":
        "Tipo de compañía",
}


# =============================================================================
# UTILIDADES
# =============================================================================

def header(
    title: str,
) -> None:

    print()
    print("=" * 110)
    print(title)
    print("=" * 110)
    print()


def clean_value(
    value,
):

    if value is None:
        return None

    try:
        if pd.isna(
            value
        ):
            return None
    except (
        TypeError,
        ValueError,
    ):
        pass

    if isinstance(
        value,
        np.integer,
    ):
        return int(
            value
        )

    if isinstance(
        value,
        np.floating,
    ):
        return float(
            value
        )

    if isinstance(
        value,
        np.bool_,
    ):
        return bool(
            value
        )

    return value


# =============================================================================
# MODELO
# =============================================================================

def load_artifact() -> dict:

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"No existe el modelo:\n{MODEL_PATH}"
        )

    artifact = joblib.load(
        MODEL_PATH
    )

    if not isinstance(
        artifact,
        dict,
    ):

        raise RuntimeError(
            "El artefacto final no tiene "
            "la estructura esperada."
        )

    required = [
        "model",
        "features",
        "numeric_features",
        "boolean_features",
        "categorical_features",
    ]

    missing = [
        key
        for key in required
        if key not in artifact
    ]

    if missing:

        raise RuntimeError(
            "Faltan claves en el artefacto:\n"
            + "\n".join(
                missing
            )
        )

    return artifact


# =============================================================================
# CATEGORÍAS TRAIN
# =============================================================================

def load_train_categories(
    categorical_features: list[str],
) -> dict[str, list[str]]:

    category_sets = {
        feature: set()
        for feature
        in categorical_features
    }

    usecols = [
        "SPLIT",
        *categorical_features,
    ]

    for chunk in pd.read_csv(
        DATA_PATH,
        usecols=usecols,
        chunksize=200_000,
        low_memory=False,
    ):

        train = chunk[
            chunk[
                "SPLIT"
            ].eq(
                "TRAIN"
            )
        ]

        if train.empty:
            continue

        for feature in categorical_features:

            values = (
                train[
                    feature
                ]
                .dropna()
                .astype(
                    "string"
                )
            )

            category_sets[
                feature
            ].update(
                values.tolist()
            )

    return {
        feature:
            sorted(
                values
            )
        for feature, values
        in category_sets.items()
    }


# =============================================================================
# NORMALIZACIÓN
# =============================================================================

def prepare_feature_frame(
    dataframe: pd.DataFrame,
    artifact: dict,
    train_categories: dict[
        str,
        list[str],
    ],
) -> pd.DataFrame:

    features = list(
        artifact[
            "features"
        ]
    )

    numeric_features = set(
        artifact[
            "numeric_features"
        ]
    )

    boolean_features = set(
        artifact[
            "boolean_features"
        ]
    )

    categorical_features = set(
        artifact[
            "categorical_features"
        ]
    )

    output = dataframe[
        features
    ].copy()

    for feature in features:

        if feature in categorical_features:

            categories = (
                train_categories.get(
                    feature,
                    [],
                )
            )

            output[
                feature
            ] = pd.Categorical(
                output[
                    feature
                ].astype(
                    "string"
                ),
                categories=categories,
            )

            continue

        if (
            feature
            in numeric_features
            or feature
            in boolean_features
        ):

            output[
                feature
            ] = pd.to_numeric(
                output[
                    feature
                ],
                errors="coerce",
            )

            output[
                feature
            ] = (
                output[
                    feature
                ]
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

    return output[
        features
    ]


# =============================================================================
# TRAIN REFERENCE
# =============================================================================

def load_train_reference(
    artifact: dict,
    train_categories: dict[
        str,
        list[str],
    ],
) -> pd.DataFrame:

    features = list(
        artifact[
            "features"
        ]
    )

    usecols = [
        "SPLIT",
        *features,
    ]

    frames = []

    for chunk_index, chunk in enumerate(
        pd.read_csv(
            DATA_PATH,
            usecols=usecols,
            chunksize=200_000,
            low_memory=False,
        )
    ):

        train = chunk.loc[
            chunk[
                "SPLIT"
            ].eq(
                "TRAIN"
            ),
            features,
        ].copy()

        if train.empty:
            continue

        sample_size = min(
            TRAIN_SAMPLE_PER_CHUNK,
            len(
                train
            ),
        )

        sample = train.sample(
            n=sample_size,
            random_state=(
                RANDOM_STATE
                + chunk_index
            ),
        )

        frames.append(
            sample
        )

    if not frames:

        raise RuntimeError(
            "No se encontraron observaciones TRAIN."
        )

    reference = pd.concat(
        frames,
        ignore_index=True,
    )

    if (
        len(
            reference
        )
        > TRAIN_REFERENCE_SIZE
    ):

        reference = reference.sample(
            n=TRAIN_REFERENCE_SIZE,
            random_state=RANDOM_STATE,
        )

    return (
        prepare_feature_frame(
            reference,
            artifact,
            train_categories,
        )
        .reset_index(
            drop=True
        )
    )


# =============================================================================
# TEST
# =============================================================================

def load_test_cases(
    artifact: dict,
) -> pd.DataFrame:

    features = list(
        artifact[
            "features"
        ]
    )

    identification = [
        "ANIO",
        "EXPEDIENTE_KEY",
        "RUC",
        "NOMBRE",
        "TARGET_24M",
        "SPLIT",
    ]

    usecols = list(
        dict.fromkeys(
            [
                *identification,
                *features,
            ]
        )
    )

    frames = []

    for chunk in pd.read_csv(
        DATA_PATH,
        usecols=usecols,
        chunksize=200_000,
        low_memory=False,
    ):

        test = chunk[
            (
                chunk[
                    "SPLIT"
                ].eq(
                    "TEST"
                )
            )
            &
            (
                chunk[
                    "ANIO"
                ].eq(
                    2023
                )
            )
        ].copy()

        if not test.empty:

            frames.append(
                test
            )

    if not frames:

        raise RuntimeError(
            "No existen observaciones TEST 2023."
        )

    return pd.concat(
        frames,
        ignore_index=True,
    )


# =============================================================================
# SELECCIÓN GRANDE / PEQUEÑA
# =============================================================================

def select_large_small_cases(
    raw_test: pd.DataFrame,
    prepared_test: pd.DataFrame,
    features: list[str],
) -> pd.DataFrame:

    complete_mask = (
        prepared_test[
            features
        ]
        .notna()
        .all(
            axis=1
        )
    )

    base = raw_test.loc[
        complete_mask
    ].copy()

    if base.empty:

        raise RuntimeError(
            "No existen casos completos TEST 2023."
        )

    # -------------------------------------------------------------------------
    # Seleccionamos el tipo de compañía con mayor número
    # de observaciones completas para evitar comparar categorías muy distintas.
    # -------------------------------------------------------------------------

    dominant_type = (
        base[
            "tipo_compania"
        ]
        .astype(
            "string"
        )
        .value_counts()
        .idxmax()
    )

    comparable = base[
        base[
            "tipo_compania"
        ]
        .astype(
            "string"
        )
        .eq(
            dominant_type
        )
    ].copy()

    comparable[
        "activos_numeric"
    ] = pd.to_numeric(
        comparable[
            "activos_final"
        ],
        errors="coerce",
    )

    comparable = comparable[
        comparable[
            "activos_numeric"
        ].notna()
        &
        np.isfinite(
            comparable[
                "activos_numeric"
            ]
        )
        &
        comparable[
            "activos_numeric"
        ].gt(
            0
        )
    ].copy()

    if len(
        comparable
    ) < 100:

        raise RuntimeError(
            "No existen suficientes observaciones "
            "comparables para seleccionar P10/P90."
        )

    p10 = float(
        comparable[
            "activos_numeric"
        ].quantile(
            0.10
        )
    )

    p50 = float(
        comparable[
            "activos_numeric"
        ].quantile(
            0.50
        )
    )

    p90 = float(
        comparable[
            "activos_numeric"
        ].quantile(
            0.90
        )
    )

    comparable[
        "DIST_P10"
    ] = (
        comparable[
            "activos_numeric"
        ]
        - p10
    ).abs()

    comparable[
        "DIST_P90"
    ] = (
        comparable[
            "activos_numeric"
        ]
        - p90
    ).abs()

    small_index = (
        comparable[
            "DIST_P10"
        ]
        .idxmin()
    )

    large_index = (
        comparable[
            "DIST_P90"
        ]
        .idxmin()
    )

    cases = pd.concat(
        [
            raw_test.loc[
                [
                    large_index
                ]
            ],
            raw_test.loc[
                [
                    small_index
                ]
            ],
        ]
    ).copy()

    cases.insert(
        0,
        "CASE_ID",
        [
            "EMPRESA_GRANDE",
            "EMPRESA_PEQUENA",
        ],
    )

    cases[
        "SEGMENTO_REFERENCIA"
    ] = [
        "Aproximadamente P90 de activos",
        "Aproximadamente P10 de activos",
    ]

    cases[
        "TIPO_CONTROLADO"
    ] = dominant_type

    cases[
        "P10_ACTIVOS_GRUPO"
    ] = p10

    cases[
        "P50_ACTIVOS_GRUPO"
    ] = p50

    cases[
        "P90_ACTIVOS_GRUPO"
    ] = p90

    return cases.reset_index(
        drop=True
    )


# =============================================================================
# SHAP ENCODE
# =============================================================================

def encode_for_shap(
    dataframe: pd.DataFrame,
    features: list[str],
    categorical_features: set[str],
) -> np.ndarray:

    matrix = np.empty(
        (
            len(
                dataframe
            ),
            len(
                features
            ),
        ),
        dtype="float64",
    )

    for index, feature in enumerate(
        features
    ):

        if feature in categorical_features:

            values = (
                dataframe[
                    feature
                ]
                .cat.codes
                .to_numpy(
                    dtype="float64",
                    copy=True,
                )
            )

            matrix[
                :,
                index,
            ] = values

        else:

            values = pd.to_numeric(
                dataframe[
                    feature
                ],
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
                index,
            ] = values

    return matrix


# =============================================================================
# SHAP DECODE
# =============================================================================

def decode_shap_matrix(
    matrix,
    features: list[str],
    categorical_features: set[str],
    train_categories: dict[
        str,
        list[str],
    ],
) -> pd.DataFrame:

    array = np.asarray(
        matrix,
        dtype="float64",
    )

    if array.ndim == 1:

        array = array.reshape(
            1,
            -1,
        )

    data = {}

    for feature_index, feature in enumerate(
        features
    ):

        values = array[
            :,
            feature_index,
        ].copy()

        if feature in categorical_features:

            categories = (
                train_categories.get(
                    feature,
                    [],
                )
            )

            labels = []

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
                        categories
                    )
                ):

                    labels.append(
                        pd.NA
                    )

                else:

                    labels.append(
                        categories[
                            code
                        ]
                    )

            data[
                feature
            ] = pd.Categorical(
                labels,
                categories=categories,
            )

        else:

            values[
                values
                == SHAP_MISSING_SENTINEL
            ] = np.nan

            data[
                feature
            ] = values.astype(
                "float64"
            )

    return pd.DataFrame(
        data,
        columns=features,
    )


# =============================================================================
# GRÁFICO
# =============================================================================

def create_plot(
    explanation_df: pd.DataFrame,
    case_id: str,
    company_name: str,
    output_path: Path,
) -> None:

    plot_df = (
        explanation_df
        .sort_values(
            "ABS_SHAP_VALUE",
            ascending=False,
        )
        .head(
            10
        )
        .sort_values(
            "ABS_SHAP_VALUE",
            ascending=True,
        )
    )

    plt.figure(
        figsize=(
            11,
            7,
        )
    )

    plt.barh(
        plot_df[
            "FEATURE_LABEL"
        ],
        plot_df[
            "SHAP_VALUE"
        ],
    )

    plt.axvline(
        0,
        linewidth=1,
    )

    plt.xlabel(
        "Contribución SHAP al score"
    )

    plt.ylabel(
        "Variable"
    )

    plt.title(
        f"{case_id} · {company_name}"
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close()


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    header(
        "P06 · EXPLICABILIDAD Y SESGO"
    )

    print(
        "Modelo:"
    )
    print(
        "v10_hgb_financial_c3"
    )

    print()

    print(
        "Configuración:"
    )
    print(
        "C3_CONSERVATIVE"
    )

    print()

    print(
        "Método:"
    )
    print(
        "SHAP PermutationExplainer"
    )

    # =========================================================================
    # MODELO
    # =========================================================================

    artifact = load_artifact()

    model = artifact[
        "model"
    ]

    features = list(
        artifact[
            "features"
        ]
    )

    categorical_features = set(
        artifact[
            "categorical_features"
        ]
    )

    # =========================================================================
    # TRAIN CATEGORIES
    # =========================================================================

    print()

    print(
        "Cargando categorías desde TRAIN..."
    )

    train_categories = (
        load_train_categories(
            list(
                categorical_features
            )
        )
    )

    # =========================================================================
    # TRAIN REFERENCE
    # =========================================================================

    print(
        "Construyendo referencia TRAIN..."
    )

    train_reference = (
        load_train_reference(
            artifact,
            train_categories,
        )
    )

    print(
        f"Referencia TRAIN: "
        f"{len(train_reference):,}"
    )

    # =========================================================================
    # TEST
    # =========================================================================

    print(
        "Cargando TEST 2023..."
    )

    raw_test = (
        load_test_cases(
            artifact
        )
    )

    prepared_test = (
        prepare_feature_frame(
            raw_test,
            artifact,
            train_categories,
        )
    )

    # =========================================================================
    # SELECCIÓN
    # =========================================================================

    cases = (
        select_large_small_cases(
            raw_test,
            prepared_test,
            features,
        )
    )

    header(
        "CASOS SELECCIONADOS"
    )

    print(
        cases[
            [
                "CASE_ID",
                "NOMBRE",
                "tipo_compania",
                "activos_final",
                "patrimonio_final",
                "bi_ingresos_ventas",
                "bi_n_empleados",
                "TARGET_24M",
                "SEGMENTO_REFERENCIA",
            ]
        ].to_string(
            index=False
        )
    )

    print()

    print(
        "Tipo de compañía controlado:"
    )

    print(
        cases[
            "TIPO_CONTROLADO"
        ].iloc[
            0
        ]
    )

    print()

    print(
        "Referencia de activos dentro del grupo:"
    )

    print(
        "P10 = "
        f"{cases['P10_ACTIVOS_GRUPO'].iloc[0]:,.2f}"
    )

    print(
        "P50 = "
        f"{cases['P50_ACTIVOS_GRUPO'].iloc[0]:,.2f}"
    )

    print(
        "P90 = "
        f"{cases['P90_ACTIVOS_GRUPO'].iloc[0]:,.2f}"
    )

    # =========================================================================
    # BACKGROUND SHAP
    # =========================================================================

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

    background_matrix = (
        encode_for_shap(
            background[
                features
            ],
            features,
            categorical_features,
        )
    )

    def predict_positive(
        matrix,
    ) -> np.ndarray:

        frame = decode_shap_matrix(
            matrix,
            features,
            categorical_features,
            train_categories,
        )

        return (
            model.predict_proba(
                frame[
                    features
                ]
            )[
                :,
                1,
            ]
        )

    explainer = shap.Explainer(
        predict_positive,
        background_matrix,
        algorithm="permutation",
        feature_names=features,
    )

    max_evals = (
        2
        * len(
            features
        )
        + 1
    )

    # =========================================================================
    # EXPLICACIONES
    # =========================================================================

    explanation_rows = []
    summary_rows = []

    for _, case in cases.iterrows():

        case_id = str(
            case[
                "CASE_ID"
            ]
        )

        company_name = str(
            case[
                "NOMBRE"
            ]
        )

        case_frame_raw = pd.DataFrame(
            [
                {
                    feature:
                        case[
                            feature
                        ]
                    for feature
                    in features
                }
            ]
        )

        case_frame = (
            prepare_feature_frame(
                case_frame_raw,
                artifact,
                train_categories,
            )
        )

        model_score = float(
            model.predict_proba(
                case_frame[
                    features
                ]
            )[
                0,
                1,
            ]
        )

        case_matrix = (
            encode_for_shap(
                case_frame[
                    features
                ],
                features,
                categorical_features,
            )
        )

        shap_result = explainer(
            case_matrix,
            max_evals=max_evals,
        )

        shap_values = (
            shap_result
            .values[
                0
            ]
        )

        base_value = float(
            np.asarray(
                shap_result
                .base_values
            )
            .reshape(
                -1
            )[
                0
            ]
        )

        reconstructed_score = float(
            base_value
            + shap_values.sum()
        )

        local_error = abs(
            model_score
            - reconstructed_score
        )

        header(
            f"{case_id} · {company_name}"
        )

        print(
            "Activos:"
        )
        print(
            f"{float(case['activos_final']):,.2f}"
        )

        print()

        print(
            "Score modelo:"
        )
        print(
            f"{model_score:.9f}"
        )

        print()

        print(
            "Score reconstruido SHAP:"
        )
        print(
            f"{reconstructed_score:.9f}"
        )

        print()

        print(
            "Error reconstrucción:"
        )
        print(
            f"{local_error:.10f}"
        )

        if (
            local_error
            > SHAP_LOCAL_TOLERANCE
        ):

            raise RuntimeError(
                f"SHAP no reconstruye correctamente "
                f"el score de {case_id}."
            )

        case_rows = []

        for feature_index, feature in enumerate(
            features
        ):

            row = {
                "CASE_ID":
                    case_id,

                "NOMBRE":
                    company_name,

                "EXPEDIENTE_KEY":
                    case[
                        "EXPEDIENTE_KEY"
                    ],

                "TARGET_24M":
                    case[
                        "TARGET_24M"
                    ],

                "ACTIVOS":
                    case[
                        "activos_final"
                    ],

                "MODEL_SCORE":
                    model_score,

                "SHAP_BASE_VALUE":
                    base_value,

                "SHAP_RECONSTRUCTED_SCORE":
                    reconstructed_score,

                "SHAP_LOCAL_ERROR":
                    local_error,

                "FEATURE":
                    feature,

                "FEATURE_LABEL":
                    FEATURE_LABELS.get(
                        feature,
                        feature,
                    ),

                "FEATURE_VALUE":
                    str(
                        case[
                            feature
                        ]
                    ),

                "SHAP_VALUE":
                    float(
                        shap_values[
                            feature_index
                        ]
                    ),

                "ABS_SHAP_VALUE":
                    float(
                        abs(
                            shap_values[
                                feature_index
                            ]
                        )
                    ),
            }

            case_rows.append(
                row
            )

            explanation_rows.append(
                row
            )

        case_df = pd.DataFrame(
            case_rows
        )

        top = (
            case_df
            .sort_values(
                "ABS_SHAP_VALUE",
                ascending=False,
            )
            .head(
                10
            )
        )

        print()

        print(
            "10 variables con mayor influencia:"
        )

        print(
            top[
                [
                    "FEATURE_LABEL",
                    "FEATURE_VALUE",
                    "SHAP_VALUE",
                ]
            ].to_string(
                index=False
            )
        )

        positive_count = int(
            (
                case_df[
                    "SHAP_VALUE"
                ]
                > 0
            ).sum()
        )

        negative_count = int(
            (
                case_df[
                    "SHAP_VALUE"
                ]
                < 0
            ).sum()
        )

        summary_rows.append(
            {
                "CASE_ID":
                    case_id,

                "NOMBRE":
                    company_name,

                "EXPEDIENTE_KEY":
                    case[
                        "EXPEDIENTE_KEY"
                    ],

                "TIPO_COMPANIA":
                    case[
                        "tipo_compania"
                    ],

                "ACTIVOS":
                    case[
                        "activos_final"
                    ],

                "PATRIMONIO":
                    case[
                        "patrimonio_final"
                    ],

                "VENTAS":
                    case[
                        "bi_ingresos_ventas"
                    ],

                "EMPLEADOS":
                    case[
                        "bi_n_empleados"
                    ],

                "TARGET_24M":
                    case[
                        "TARGET_24M"
                    ],

                "MODEL_SCORE":
                    model_score,

                "SHAP_RECONSTRUCTED_SCORE":
                    reconstructed_score,

                "SHAP_LOCAL_ERROR":
                    local_error,

                "FACTORES_SHAP_POSITIVOS":
                    positive_count,

                "FACTORES_SHAP_NEGATIVOS":
                    negative_count,

                "TOP_FEATURE_1":
                    top.iloc[
                        0
                    ][
                        "FEATURE_LABEL"
                    ],

                "TOP_FEATURE_1_SHAP":
                    top.iloc[
                        0
                    ][
                        "SHAP_VALUE"
                    ],

                "TOP_FEATURE_2":
                    top.iloc[
                        1
                    ][
                        "FEATURE_LABEL"
                    ],

                "TOP_FEATURE_2_SHAP":
                    top.iloc[
                        1
                    ][
                        "SHAP_VALUE"
                    ],

                "TOP_FEATURE_3":
                    top.iloc[
                        2
                    ][
                        "FEATURE_LABEL"
                    ],

                "TOP_FEATURE_3_SHAP":
                    top.iloc[
                        2
                    ][
                        "SHAP_VALUE"
                    ],
            }
        )

        plot_path = (
            OUTPUT_DIR
            / (
                "p06_shap_"
                + case_id.lower()
                + ".png"
            )
        )

        create_plot(
            case_df,
            case_id,
            company_name,
            plot_path,
        )

    # =========================================================================
    # COMPARACIÓN
    # =========================================================================

    explanation_df = pd.DataFrame(
        explanation_rows
    )

    summary_df = pd.DataFrame(
        summary_rows
    )

    header(
        "COMPARACIÓN GRANDE VS. PEQUEÑA"
    )

    print(
        summary_df[
            [
                "CASE_ID",
                "NOMBRE",
                "ACTIVOS",
                "MODEL_SCORE",
                "TOP_FEATURE_1",
                "TOP_FEATURE_1_SHAP",
                "TOP_FEATURE_2",
                "TOP_FEATURE_2_SHAP",
                "TOP_FEATURE_3",
                "TOP_FEATURE_3_SHAP",
            ]
        ].to_string(
            index=False
        )
    )

    # =========================================================================
    # VARIABLES DE ESCALA
    # =========================================================================

    scale_features = {
        "activos_final",
        "patrimonio_final",
        "bi_ingresos_ventas",
        "bi_n_empleados",
        "activos_final_t1",
        "patrimonio_final_t1",
        "bi_ingresos_ventas_t1",
        "bi_n_empleados_t1",
    }

    scale_analysis = (
        explanation_df[
            explanation_df[
                "FEATURE"
            ].isin(
                scale_features
            )
        ]
        .groupby(
            "CASE_ID"
        )
        .agg(
            SHAP_ESCALA_ABS=(
                "ABS_SHAP_VALUE",
                "sum",
            ),
            SHAP_ESCALA_NETO=(
                "SHAP_VALUE",
                "sum",
            ),
        )
        .reset_index()
    )

    total_analysis = (
        explanation_df
        .groupby(
            "CASE_ID"
        )
        .agg(
            SHAP_TOTAL_ABS=(
                "ABS_SHAP_VALUE",
                "sum",
            )
        )
        .reset_index()
    )

    size_analysis = (
        scale_analysis
        .merge(
            total_analysis,
            on="CASE_ID",
            how="left",
        )
    )

    size_analysis[
        "PCT_INFLUENCIA_ABS_ESCALA"
    ] = (
        100.0
        * size_analysis[
            "SHAP_ESCALA_ABS"
        ]
        / size_analysis[
            "SHAP_TOTAL_ABS"
        ]
    )

    print()

    print(
        "Peso relativo de variables de escala "
        "en la explicación local:"
    )

    print(
        size_analysis.to_string(
            index=False
        )
    )

    # =========================================================================
    # INTERPRETACIÓN
    # =========================================================================

    header(
        "INTERPRETACIÓN DE SESGO / TAMAÑO"
    )

    print(
        "1. Las explicaciones SHAP muestran "
        "qué variables influyeron en cada "
        "predicción concreta."
    )

    print()

    print(
        "2. Una diferencia entre empresa grande "
        "y pequeña no demuestra por sí sola un "
        "sesgo injusto."
    )

    print()

    print(
        "3. Si las variables de escala tienen "
        "mayor peso en la empresa grande, "
        "esto indica dependencia predictiva "
        "de características de tamaño en ese "
        "caso; no demuestra causalidad."
    )

    print()

    print(
        "4. La conclusión correcta es que el "
        "modelo utiliza características de escala "
        "junto con crecimiento, rentabilidad, "
        "actividad y calidad de información."
    )

    print()

    print(
        "5. Esta comparación debe utilizarse "
        "como señal para monitorear desempeño "
        "por tamaño y no como evidencia automática "
        "de discriminación."
    )

    # =========================================================================
    # RESULTADO
    # =========================================================================

    reconstruction_ok = bool(
        (
            summary_df[
                "SHAP_LOCAL_ERROR"
            ]
            <= SHAP_LOCAL_TOLERANCE
        ).all()
    )

    two_cases_ok = (
        len(
            summary_df
        )
        == 2
    )

    different_size_ok = bool(
        summary_df[
            "ACTIVOS"
        ].max()
        >
        summary_df[
            "ACTIVOS"
        ].min()
    )

    p06_pass = all(
        [
            reconstruction_ok,
            two_cases_ok,
            different_size_ok,
        ]
    )

    header(
        "RESULTADO P06"
    )

    if p06_pass:

        print(
            "CUMPLE"
        )

        print()

        print(
            "Se compararon explicaciones SHAP "
            "de una empresa grande y una pequeña, "
            "controlando año y tipo de compañía."
        )

        print()

        print(
            "Las explicaciones reconstruyen "
            "correctamente los scores del modelo."
        )

        print()

        print(
            "Las diferencias se documentan "
            "sin atribuir causalidad a SHAP."
        )

    else:

        print(
            "PARCIAL / REVISAR"
        )

    # =========================================================================
    # EVIDENCIAS
    # =========================================================================

    cases_path = (
        OUTPUT_DIR
        / "p06_cases.csv"
    )

    cases.to_csv(
        cases_path,
        index=False,
    )

    explanation_path = (
        OUTPUT_DIR
        / "p06_shap_explanations.csv"
    )

    explanation_df.to_csv(
        explanation_path,
        index=False,
    )

    summary_path = (
        OUTPUT_DIR
        / "p06_comparison_summary.csv"
    )

    summary_df.to_csv(
        summary_path,
        index=False,
    )

    size_path = (
        OUTPUT_DIR
        / "p06_size_analysis.csv"
    )

    size_analysis.to_csv(
        size_path,
        index=False,
    )

    metadata = {
        "test_id":
            "P06",

        "model":
            "v10_hgb_financial_c3",

        "config":
            "C3_CONSERVATIVE",

        "method":
            "SHAP PermutationExplainer",

        "background_source":
            "TRAIN exclusivamente",

        "background_size":
            len(
                background_matrix
            ),

        "selection":
            (
                "TEST 2023, registros completos, "
                "mismo tipo de compañía, "
                "aproximación P90 vs P10 de activos"
            ),

        "causality_warning":
            (
                "SHAP explica contribuciones al "
                "score; no demuestra causalidad."
            ),

        "result":
            (
                "CUMPLE"
                if p06_pass
                else "PARCIAL / REVISAR"
            ),
    }

    metadata_path = (
        OUTPUT_DIR
        / "p06_metadata.json"
    )

    with metadata_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()

    print(
        "Evidencias generadas:"
    )

    print(
        cases_path
    )

    print(
        explanation_path
    )

    print(
        summary_path
    )

    print(
        size_path
    )

    print(
        OUTPUT_DIR
        / "p06_shap_empresa_grande.png"
    )

    print(
        OUTPUT_DIR
        / "p06_shap_empresa_pequena.png"
    )

    print(
        metadata_path
    )

    print()


if __name__ == "__main__":
    main()