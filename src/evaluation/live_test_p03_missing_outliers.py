"""
P03 · Datos faltantes y atípicos
Prospect Finder BVQ

Objetivo
--------
Evaluar el comportamiento del modelo v10 frente a:

1. una empresa de ensayo con datos financieros faltantes;
2. una empresa de ensayo con una razón financiera extrema.

La prueba mide:

- score original;
- score después de introducir faltantes;
- score después de introducir un valor extremo;
- detección explícita de las perturbaciones;
- cambio absoluto y relativo del score;
- capacidad del modelo para responder sin error silencioso.

IMPORTANTE
----------
Esta prueba:

- NO modifica el dataset congelado;
- NO modifica TEST;
- NO reentrena el modelo;
- NO modifica hiperparámetros;
- NO modifica el ranking oficial;
- NO modifica PostgreSQL.

Todos los archivos de evidencia se generan únicamente en:

    reports/live_tests/P03/
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


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
    / "P03"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =============================================================================
# FEATURES QUE ALTERAREMOS
# =============================================================================

MISSING_FEATURES = [
    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",
    "fin_ratio_patrimonio_activos",
    "fin_roa",
    "fin_margen_neto",
    "fin_rotacion_activos",
    "fin_roe",
]

EXTREME_FEATURE = (
    "fin_ratio_patrimonio_activos"
)


# =============================================================================
# UTILIDADES
# =============================================================================

def header(
    title: str,
) -> None:

    print()
    print("=" * 100)
    print(title)
    print("=" * 100)
    print()


def safe_float(
    value,
) -> float | None:

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (
        TypeError,
        ValueError,
    ):
        pass

    return float(
        value
    )


def percent_change(
    original: float,
    new: float,
) -> float | None:

    if original == 0:
        return None

    return (
        (
            new
            - original
        )
        / abs(
            original
        )
        * 100.0
    )


# =============================================================================
# CARGA DEL ARTEFACTO
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

    required_keys = [
        "model",
        "features",
        "numeric_features",
        "boolean_features",
        "categorical_features",
    ]

    missing = [
        key
        for key in required_keys
        if key not in artifact
    ]

    if missing:

        raise RuntimeError(
            "Faltan claves en el artefacto:\n"
            + "\n".join(
                f"  - {key}"
                for key in missing
            )
        )

    return artifact


# =============================================================================
# CATEGORÍAS APRENDIDAS DESDE TRAIN
# =============================================================================

def load_train_categories(
    categorical_features: list[str],
) -> dict[str, list[str]]:

    categories: dict[
        str,
        set[str],
    ] = {
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

            categories[
                feature
            ].update(
                values.tolist()
            )

    output: dict[
        str,
        list[str],
    ] = {}

    for feature in categorical_features:

        output[
            feature
        ] = sorted(
            categories[
                feature
            ]
        )

    return output


# =============================================================================
# PREPARACIÓN DE FEATURES
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

    missing_columns = [
        feature
        for feature in features
        if feature
        not in dataframe.columns
    ]

    if missing_columns:

        raise RuntimeError(
            "Faltan variables requeridas "
            "por el modelo:\n"
            + "\n".join(
                missing_columns
            )
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

            values = (
                output[
                    feature
                ]
                .astype(
                    "string"
                )
            )

            output[
                feature
            ] = pd.Categorical(
                values,
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
# SELECCIÓN DE UNA FILA TEST COMPLETA
# =============================================================================

def load_complete_test_case(
    features: list[str],
) -> pd.DataFrame:

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

    candidates: list[
        pd.DataFrame
    ] = []

    for chunk in pd.read_csv(
        DATA_PATH,
        usecols=usecols,
        chunksize=100_000,
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

        if test.empty:
            continue

        completeness = (
            test[
                features
            ]
            .notna()
            .sum(
                axis=1
            )
        )

        test[
            "_N_AVAILABLE"
        ] = completeness

        complete = test[
            test[
                "_N_AVAILABLE"
            ].eq(
                len(
                    features
                )
            )
        ].copy()

        if not complete.empty:

            candidates.append(
                complete
            )

            break

    if not candidates:

        raise RuntimeError(
            "No se encontró una observación "
            "TEST 2023 completa para P03."
        )

    selected = (
        candidates[
            0
        ]
        .head(
            1
        )
        .drop(
            columns=[
                "_N_AVAILABLE"
            ]
        )
        .copy()
    )

    return selected


# =============================================================================
# DISTRIBUCIÓN TRAIN PARA VARIABLE EXTREMA
# =============================================================================

def load_train_distribution(
    feature: str,
) -> pd.Series:

    values: list[
        pd.Series
    ] = []

    for chunk in pd.read_csv(
        DATA_PATH,
        usecols=[
            "SPLIT",
            feature,
        ],
        chunksize=200_000,
        low_memory=False,
    ):

        train = chunk[
            chunk[
                "SPLIT"
            ].eq(
                "TRAIN"
            )
        ].copy()

        if train.empty:
            continue

        numeric = pd.to_numeric(
            train[
                feature
            ],
            errors="coerce",
        )

        numeric = numeric.replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )

        numeric = numeric.dropna()

        if not numeric.empty:

            values.append(
                numeric
            )

    if not values:

        raise RuntimeError(
            f"No hay valores TRAIN "
            f"para {feature}."
        )

    return pd.concat(
        values,
        ignore_index=True,
    )


# =============================================================================
# PREDICCIÓN
# =============================================================================

def predict_score(
    model,
    dataframe: pd.DataFrame,
) -> float:

    probabilities = (
        model.predict_proba(
            dataframe
        )
    )

    score = float(
        probabilities[
            0,
            1,
        ]
    )

    return score


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    header(
        "P03 · DATOS FALTANTES Y ATÍPICOS"
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
        "Dataset:"
    )
    print(
        DATA_PATH
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

    categorical_features = list(
        artifact[
            "categorical_features"
        ]
    )

    print()

    print(
        "Features congeladas:"
    )
    print(
        len(
            features
        )
    )

    # =========================================================================
    # CATEGORÍAS TRAIN
    # =========================================================================

    train_categories = (
        load_train_categories(
            categorical_features
        )
    )

    print()

    for feature in categorical_features:

        print(
            f"Categorías TRAIN de "
            f"{feature}: "
            f"{len(train_categories[feature])}"
        )

    # =========================================================================
    # CASO ORIGINAL
    # =========================================================================

    original_raw = (
        load_complete_test_case(
            features
        )
    )

    original_prepared = (
        prepare_feature_frame(
            original_raw,
            artifact,
            train_categories,
        )
    )

    original_score = (
        predict_score(
            model,
            original_prepared,
        )
    )

    row = (
        original_raw
        .iloc[
            0
        ]
    )

    header(
        "EMPRESA BASE DE ENSAYO"
    )

    print(
        "ANIO:"
    )
    print(
        row[
            "ANIO"
        ]
    )

    print()

    print(
        "EXPEDIENTE_KEY:"
    )
    print(
        row[
            "EXPEDIENTE_KEY"
        ]
    )

    print()

    print(
        "Empresa:"
    )
    print(
        row[
            "NOMBRE"
        ]
    )

    print()

    print(
        "RUC:"
    )
    print(
        row[
            "RUC"
        ]
    )

    print()

    print(
        "TARGET_24M:"
    )
    print(
        row[
            "TARGET_24M"
        ]
    )

    print()

    print(
        "Score original:"
    )
    print(
        f"{original_score:.9f}"
    )

    # =========================================================================
    # CASO A · DATOS FALTANTES
    # =========================================================================

    missing_raw = (
        original_raw.copy()
    )

    for feature in MISSING_FEATURES:

        if feature in missing_raw.columns:

            missing_raw.loc[
                :,
                feature,
            ] = np.nan

    missing_count_before = int(
        original_raw[
            features
        ]
        .isna()
        .sum(
            axis=1
        )
        .iloc[
            0
        ]
    )

    missing_count_after = int(
        missing_raw[
            features
        ]
        .isna()
        .sum(
            axis=1
        )
        .iloc[
            0
        ]
    )

    missing_detected = (
        missing_count_after
        > missing_count_before
    )

    missing_error = None

    missing_score = None

    try:

        missing_prepared = (
            prepare_feature_frame(
                missing_raw,
                artifact,
                train_categories,
            )
        )

        missing_score = (
            predict_score(
                model,
                missing_prepared,
            )
        )

        missing_prediction_ok = bool(
            np.isfinite(
                missing_score
            )
        )

    except Exception as exc:

        missing_error = (
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        missing_prediction_ok = False

    header(
        "CASO A · EMPRESA CON DATOS FALTANTES"
    )

    print(
        "Variables convertidas a faltantes:"
    )

    for feature in MISSING_FEATURES:

        print(
            f"  - {feature}"
        )

    print()

    print(
        "Faltantes antes:"
    )
    print(
        missing_count_before
    )

    print()

    print(
        "Faltantes después:"
    )
    print(
        missing_count_after
    )

    print()

    print(
        "¿La perturbación fue detectada?"
    )
    print(
        missing_detected
    )

    print()

    print(
        "¿El modelo respondió sin excepción?"
    )
    print(
        missing_prediction_ok
    )

    if missing_score is not None:

        missing_absolute_change = (
            missing_score
            - original_score
        )

        missing_relative_change = (
            percent_change(
                original_score,
                missing_score,
            )
        )

        print()

        print(
            "Score original:"
        )
        print(
            f"{original_score:.9f}"
        )

        print()

        print(
            "Score con faltantes:"
        )
        print(
            f"{missing_score:.9f}"
        )

        print()

        print(
            "Cambio absoluto:"
        )
        print(
            f"{missing_absolute_change:+.9f}"
        )

        print()

        print(
            "Cambio relativo:"
        )

        if (
            missing_relative_change
            is not None
        ):

            print(
                f"{missing_relative_change:+.2f}%"
            )

        else:

            print(
                "No calculable"
            )

    else:

        missing_absolute_change = None

        missing_relative_change = None

        print()

        print(
            "Error:"
        )
        print(
            missing_error
        )

    print()

    print(
        "ADVERTENCIA DE CALIDAD:"
    )
    print(
        "La observación contiene información "
        "financiera incompleta. El score puede "
        "calcularse si el estimador admite valores "
        "faltantes, pero debe interpretarse con "
        "menor confianza y con la limitación "
        "documentada."
    )

    # =========================================================================
    # CASO B · RAZÓN FINANCIERA EXTREMA
    # =========================================================================

    train_distribution = (
        load_train_distribution(
            EXTREME_FEATURE
        )
    )

    q01 = float(
        train_distribution.quantile(
            0.01
        )
    )

    q50 = float(
        train_distribution.quantile(
            0.50
        )
    )

    q99 = float(
        train_distribution.quantile(
            0.99
        )
    )

    extreme_value = max(
        10.0,
        abs(
            q99
        )
        * 10.0,
    )

    extreme_raw = (
        original_raw.copy()
    )

    original_extreme_feature_value = (
        safe_float(
            extreme_raw[
                EXTREME_FEATURE
            ].iloc[
                0
            ]
        )
    )

    extreme_raw.loc[
        :,
        EXTREME_FEATURE,
    ] = extreme_value

    extreme_detected = bool(
        (
            extreme_value
            > q99
        )
        or
        (
            extreme_value
            < q01
        )
    )

    extreme_error = None

    extreme_score = None

    try:

        extreme_prepared = (
            prepare_feature_frame(
                extreme_raw,
                artifact,
                train_categories,
            )
        )

        extreme_score = (
            predict_score(
                model,
                extreme_prepared,
            )
        )

        extreme_prediction_ok = bool(
            np.isfinite(
                extreme_score
            )
        )

    except Exception as exc:

        extreme_error = (
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        extreme_prediction_ok = False

    header(
        "CASO B · RAZÓN FINANCIERA EXTREMA"
    )

    print(
        "Variable:"
    )
    print(
        EXTREME_FEATURE
    )

    print()

    print(
        "Valor original:"
    )
    print(
        original_extreme_feature_value
    )

    print()

    print(
        "Distribución TRAIN:"
    )

    print(
        f"P01 = {q01:.6f}"
    )

    print(
        f"P50 = {q50:.6f}"
    )

    print(
        f"P99 = {q99:.6f}"
    )

    print()

    print(
        "Valor extremo introducido:"
    )
    print(
        f"{extreme_value:.6f}"
    )

    print()

    print(
        "¿El valor está fuera del rango "
        "central observado en TRAIN?"
    )
    print(
        extreme_detected
    )

    print()

    print(
        "¿El modelo respondió sin excepción?"
    )
    print(
        extreme_prediction_ok
    )

    if extreme_score is not None:

        extreme_absolute_change = (
            extreme_score
            - original_score
        )

        extreme_relative_change = (
            percent_change(
                original_score,
                extreme_score,
            )
        )

        print()

        print(
            "Score original:"
        )
        print(
            f"{original_score:.9f}"
        )

        print()

        print(
            "Score con valor extremo:"
        )
        print(
            f"{extreme_score:.9f}"
        )

        print()

        print(
            "Cambio absoluto:"
        )
        print(
            f"{extreme_absolute_change:+.9f}"
        )

        print()

        print(
            "Cambio relativo:"
        )

        if (
            extreme_relative_change
            is not None
        ):

            print(
                f"{extreme_relative_change:+.2f}%"
            )

        else:

            print(
                "No calculable"
            )

    else:

        extreme_absolute_change = None

        extreme_relative_change = None

        print()

        print(
            "Error:"
        )
        print(
            extreme_error
        )

    print()

    print(
        "ADVERTENCIA DE ATÍPICO:"
    )
    print(
        "El valor introducido está fuera del "
        "rango de referencia observado en TRAIN. "
        "El resultado debe marcarse como caso "
        "atípico y no interpretarse como una "
        "observación financiera ordinaria."
    )

    # =========================================================================
    # RESULTADO
    # =========================================================================

    p03_pass = all(
        [
            missing_detected,
            missing_prediction_ok,
            extreme_detected,
            extreme_prediction_ok,
        ]
    )

    header(
        "RESULTADO P03"
    )

    if p03_pass:

        print(
            "CUMPLE"
        )

        print()

        print(
            "El modelo procesó ambos casos sin "
            "fallo silencioso y la prueba dejó "
            "documentadas las condiciones de "
            "datos faltantes y valor atípico."
        )

    else:

        print(
            "PARCIAL / REVISAR"
        )

        print()

        print(
            "Al menos uno de los casos no pudo "
            "ser procesado o detectado de forma "
            "controlada."
        )

    # =========================================================================
    # EVIDENCIA
    # =========================================================================

    results = pd.DataFrame(
        [
            {
                "caso":
                    "ORIGINAL",

                "expediente_key":
                    row[
                        "EXPEDIENTE_KEY"
                    ],

                "nombre":
                    row[
                        "NOMBRE"
                    ],

                "score_original":
                    original_score,

                "score_alterado":
                    original_score,

                "cambio_absoluto":
                    0.0,

                "cambio_relativo_pct":
                    0.0,

                "perturbacion_detectada":
                    True,

                "prediccion_exitosa":
                    True,

                "observacion":
                    "Caso base",
            },

            {
                "caso":
                    "FALTANTES",

                "expediente_key":
                    row[
                        "EXPEDIENTE_KEY"
                    ],

                "nombre":
                    row[
                        "NOMBRE"
                    ],

                "score_original":
                    original_score,

                "score_alterado":
                    missing_score,

                "cambio_absoluto":
                    missing_absolute_change,

                "cambio_relativo_pct":
                    missing_relative_change,

                "perturbacion_detectada":
                    missing_detected,

                "prediccion_exitosa":
                    missing_prediction_ok,

                "observacion":
                    (
                        "Información financiera "
                        "incompleta; interpretar "
                        "con menor confianza."
                    ),
            },

            {
                "caso":
                    "ATIPICO",

                "expediente_key":
                    row[
                        "EXPEDIENTE_KEY"
                    ],

                "nombre":
                    row[
                        "NOMBRE"
                    ],

                "score_original":
                    original_score,

                "score_alterado":
                    extreme_score,

                "cambio_absoluto":
                    extreme_absolute_change,

                "cambio_relativo_pct":
                    extreme_relative_change,

                "perturbacion_detectada":
                    extreme_detected,

                "prediccion_exitosa":
                    extreme_prediction_ok,

                "observacion":
                    (
                        "Razón financiera extrema "
                        "fuera del rango de referencia "
                        "TRAIN."
                    ),
            },
        ]
    )

    results_path = (
        OUTPUT_DIR
        / "p03_results.csv"
    )

    results.to_csv(
        results_path,
        index=False,
    )

    original_export = (
        original_raw.copy()
    )

    original_export[
        "CASO_PRUEBA"
    ] = "ORIGINAL"

    original_export.to_csv(
        OUTPUT_DIR
        / "p03_input_original.csv",
        index=False,
    )

    missing_export = (
        missing_raw.copy()
    )

    missing_export[
        "CASO_PRUEBA"
    ] = "FALTANTES"

    missing_export.to_csv(
        OUTPUT_DIR
        / "p03_input_missing.csv",
        index=False,
    )

    extreme_export = (
        extreme_raw.copy()
    )

    extreme_export[
        "CASO_PRUEBA"
    ] = "ATIPICO"

    extreme_export.to_csv(
        OUTPUT_DIR
        / "p03_input_extreme.csv",
        index=False,
    )

    distribution = {
        "feature":
            EXTREME_FEATURE,

        "train_p01":
            q01,

        "train_p50":
            q50,

        "train_p99":
            q99,

        "original_value":
            original_extreme_feature_value,

        "extreme_test_value":
            extreme_value,
    }

    with (
        OUTPUT_DIR
        / "p03_extreme_reference.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            distribution,
            file,
            indent=2,
            ensure_ascii=False,
        )

    metadata = {
        "test_id":
            "P03",

        "model":
            "v10_hgb_financial_c3",

        "config":
            "C3_CONSERVATIVE",

        "source_split":
            "TEST",

        "source_year":
            int(
                row[
                    "ANIO"
                ]
            ),

        "source_expediente":
            int(
                row[
                    "EXPEDIENTE_KEY"
                ]
            ),

        "missing_features":
            MISSING_FEATURES,

        "extreme_feature":
            EXTREME_FEATURE,

        "extreme_value":
            extreme_value,

        "result":
            (
                "CUMPLE"
                if p03_pass
                else "PARCIAL / REVISAR"
            ),
    }

    with (
        OUTPUT_DIR
        / "p03_metadata.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()

    print(
        "Evidencias generadas:"
    )

    print(
        OUTPUT_DIR
        / "p03_results.csv"
    )

    print(
        OUTPUT_DIR
        / "p03_input_original.csv"
    )

    print(
        OUTPUT_DIR
        / "p03_input_missing.csv"
    )

    print(
        OUTPUT_DIR
        / "p03_input_extreme.csv"
    )

    print(
        OUTPUT_DIR
        / "p03_extreme_reference.json"
    )

    print(
        OUTPUT_DIR
        / "p03_metadata.json"
    )

    print()


if __name__ == "__main__":
    main()