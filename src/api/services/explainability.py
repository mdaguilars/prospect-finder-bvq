"""
Servicio de explicabilidad de Prospect Finder BVQ.

Este módulo permite generar explicaciones SHAP locales bajo demanda
para las empresas del universo operativo 2023.

Principios metodológicos
------------------------
1. Utiliza el modelo final congelado v10.
2. No reentrena ni modifica el modelo.
3. Utiliza las mismas 25 variables del modelo.
4. Las categorías se aprenden exclusivamente desde TRAIN.
5. El background de SHAP se construye exclusivamente desde TRAIN.
6. Se utiliza SHAP PermutationExplainer, igual que en el análisis
   post-test previamente validado.
7. Se valida que SHAP reconstruya correctamente el score del modelo.
8. El score se interpreta como indicador de priorización y no como
   probabilidad calibrada.
9. La explicación se calcula únicamente cuando se solicita.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import shap

from src.product.build_operational_ranking_v10 import (
    FINANCIAL_DATA_PATH,
    OPERATIONAL_YEAR,
    cargar_modelo,
    obtener_categorias_train,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

ROOT = Path(__file__).resolve().parents[3]

GLOBAL_SHAP_PATH = (
    ROOT
    / "reports"
    / "results"
    / "v10"
    / "explainability"
    / "shap_lime"
    / "v10_shap_global_importance.csv"
)

RANDOM_STATE = 42

TRAIN_REFERENCE_SIZE = 5_000
TRAIN_SAMPLE_PER_CHUNK = 2_000

SHAP_BACKGROUND_SIZE = 75

SHAP_MISSING_SENTINEL = (
    -9_876_543_210_123.0
)

SHAP_LOCAL_TOLERANCE = 1e-4

SCORE_TOLERANCE = 1e-9


# ============================================================
# ETIQUETAS AMIGABLES
# ============================================================

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
        "Ingresos por ventas del año anterior",
    "bi_n_empleados_t1":
        "Número de empleados del año anterior",
    "fin_ratio_patrimonio_activos":
        "Relación patrimonio / activos",
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
        "Disponibilidad de información histórica",
    "flag_activos_negativos":
        "Bandera de activos negativos",
    "flag_ventas_negativas":
        "Bandera de ventas negativas",
    "flag_empleados_fijo":
        "Bandera de empleados con valor fijo",
    "flag_empleados_salto_temporal":
        "Bandera de salto temporal en empleados",
    "flag_empleados_anomalia_total":
        "Bandera de anomalía en empleados",
    "flag_patrimonio_no_positivo":
        "Bandera de patrimonio no positivo",
    "tipo_compania":
        "Tipo de compañía",
}


# ============================================================
# EXCEPCIONES
# ============================================================

class ExplainabilityError(
    RuntimeError
):
    """
    Error controlado del servicio de explicabilidad.
    """


# ============================================================
# UTILIDADES
# ============================================================

def _clean_text(
    value,
):
    """
    Normaliza valores de texto.
    """

    if value is None:
        return None

    if pd.isna(value):
        return None

    return " ".join(
        str(value).split()
    )


def _json_value(
    value,
):
    """
    Convierte valores NumPy/Pandas a tipos compatibles
    con respuestas JSON.
    """

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(
        value,
        np.bool_,
    ):
        return bool(value)

    if isinstance(
        value,
        np.integer,
    ):
        return int(value)

    if isinstance(
        value,
        np.floating,
    ):
        return float(value)

    if isinstance(
        value,
        pd.Timestamp,
    ):
        return value.isoformat()

    if isinstance(
        value,
        str,
    ):
        return _clean_text(
            value
        )

    if isinstance(
        value,
        (
            bool,
            int,
            float,
        ),
    ):
        return value

    return str(value)


def _validate_required_files() -> None:
    """
    Valida los insumos necesarios para explicar el modelo.
    """

    required = [
        FINANCIAL_DATA_PATH,
    ]

    missing = [
        path
        for path in required
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "No se encontraron los archivos "
            "requeridos para explicabilidad:\n"
            + "\n".join(
                str(path)
                for path in missing
            )
        )


# ============================================================
# PREPARACIÓN DE FEATURES
# ============================================================

def _prepare_feature_frame(
    dataframe: pd.DataFrame,
    artifact: dict,
    train_categories: dict[
        str,
        list[str],
    ],
) -> pd.DataFrame:
    """
    Prepara las variables exactamente en el orden esperado
    por el modelo congelado.
    """

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

    missing = [
        feature
        for feature in features
        if feature
        not in dataframe.columns
    ]

    if missing:
        raise ExplainabilityError(
            "Faltan variables requeridas por el modelo: "
            f"{missing}"
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
            feature in numeric_features
            or feature in boolean_features
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


# ============================================================
# REFERENCIA TRAIN
# ============================================================

def _load_train_reference(
    artifact: dict,
    train_categories: dict[
        str,
        list[str],
    ],
) -> pd.DataFrame:
    """
    Construye una muestra reproducible exclusivamente
    desde TRAIN.

    Replica el procedimiento utilizado en el análisis
    SHAP post-test.
    """

    features = list(
        artifact[
            "features"
        ]
    )

    usecols = [
        "SPLIT",
        *features,
    ]

    frames: list[
        pd.DataFrame
    ] = []

    for chunk_index, chunk in enumerate(
        pd.read_csv(
            FINANCIAL_DATA_PATH,
            usecols=usecols,
            chunksize=200_000,
            low_memory=False,
        )
    ):

        train_chunk = chunk.loc[
            chunk[
                "SPLIT"
            ].eq(
                "TRAIN"
            ),
            features,
        ].copy()

        if train_chunk.empty:
            continue

        sample_size = min(
            TRAIN_SAMPLE_PER_CHUNK,
            len(
                train_chunk
            ),
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
        raise ExplainabilityError(
            "No se encontraron observaciones TRAIN "
            "para construir la referencia SHAP."
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

    reference = (
        _prepare_feature_frame(
            reference,
            artifact,
            train_categories,
        )
    )

    return reference.reset_index(
        drop=True
    )


# ============================================================
# UNIVERSO OPERATIVO
# ============================================================

def _load_operational_features(
    artifact: dict,
    train_categories: dict[
        str,
        list[str],
    ],
) -> pd.DataFrame:
    """
    Carga las 25 variables del modelo para el universo
    operativo 2023.

    Se utiliza lectura por bloques para reducir el uso
    temporal de memoria.
    """

    features = list(
        artifact[
            "features"
        ]
    )

    identification_columns = [
        "ANIO",
        "EXPEDIENTE_KEY",
        "RUC",
        "NOMBRE",
    ]

    usecols = list(
        dict.fromkeys(
            identification_columns
            + features
        )
    )

    frames: list[
        pd.DataFrame
    ] = []

    for chunk in pd.read_csv(
        FINANCIAL_DATA_PATH,
        usecols=usecols,
        dtype={
            "RUC": "string",
            "NOMBRE": "string",
        },
        chunksize=200_000,
        low_memory=False,
    ):

        operational_chunk = (
            chunk.loc[
                chunk[
                    "ANIO"
                ].eq(
                    OPERATIONAL_YEAR
                )
            ]
            .copy()
        )

        if not operational_chunk.empty:
            frames.append(
                operational_chunk
            )

    if not frames:
        raise ExplainabilityError(
            "No existen observaciones para el "
            f"universo operativo {OPERATIONAL_YEAR}."
        )

    operational = pd.concat(
        frames,
        ignore_index=True,
    )

    duplicates = (
        operational[
            "EXPEDIENTE_KEY"
        ]
        .duplicated()
        .sum()
    )

    if duplicates:
        raise ExplainabilityError(
            "El universo operativo contiene "
            f"{duplicates} expedientes duplicados."
        )

    prepared_features = (
        _prepare_feature_frame(
            operational[
                features
            ],
            artifact,
            train_categories,
        )
    )

    result = operational[
        identification_columns
    ].copy()

    for feature in features:
        result[
            feature
        ] = prepared_features[
            feature
        ]

    result = result.set_index(
        "EXPEDIENTE_KEY",
        drop=False,
    )

    return result


# ============================================================
# CODIFICACIÓN SHAP
# ============================================================

def _encode_for_shap(
    dataframe: pd.DataFrame,
    artifact: dict,
) -> np.ndarray:
    """
    Convierte las variables del modelo a una matriz numérica
    compatible con SHAP.
    """

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

    for feature_index, feature in enumerate(
        features
    ):

        if feature in categorical_features:

            series = dataframe[
                feature
            ]

            if not isinstance(
                series.dtype,
                pd.CategoricalDtype,
            ):
                raise ExplainabilityError(
                    "La variable categórica "
                    f"{feature} no fue preparada "
                    "correctamente."
                )

            codes = (
                series
                .cat
                .codes
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
            ] = (
                SHAP_MISSING_SENTINEL
            )

            matrix[
                :,
                feature_index,
            ] = values

    return matrix


def _decode_shap_matrix(
    matrix,
    artifact: dict,
    train_categories: dict[
        str,
        list[str],
    ],
) -> pd.DataFrame:
    """
    Reconstruye el DataFrame esperado por el modelo
    a partir de la representación numérica de SHAP.
    """

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

    array = np.asarray(
        matrix,
        dtype="float64",
    )

    if array.ndim == 1:
        array = array.reshape(
            1,
            -1,
        )

    if (
        array.shape[
            1
        ]
        != len(
            features
        )
    ):
        raise ExplainabilityError(
            "La matriz SHAP no contiene "
            "el número esperado de variables."
        )

    data: dict[
        str,
        object,
    ] = {}

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

            labels: list[
                object
            ] = []

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


# ============================================================
# RUNTIME SHAP
# ============================================================

@lru_cache(
    maxsize=1
)
def _get_runtime() -> dict:
    """
    Inicializa y conserva en memoria los componentes que
    pueden reutilizarse entre solicitudes.

    La primera explicación puede tomar algunos segundos
    debido a la carga del modelo y construcción del
    background TRAIN. Las siguientes reutilizan el runtime.
    """

    _validate_required_files()

    artifact = cargar_modelo()

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

    train_categories = (
        obtener_categorias_train(
            categorical_features
        )
    )

    train_reference = (
        _load_train_reference(
            artifact,
            train_categories,
        )
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

    background_matrix = (
        _encode_for_shap(
            background[
                features
            ],
            artifact,
        )
    )

    def predict_positive(
        matrix,
    ) -> np.ndarray:

        frame = (
            _decode_shap_matrix(
                matrix,
                artifact,
                train_categories,
            )
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

    operational = (
        _load_operational_features(
            artifact,
            train_categories,
        )
    )

    return {
        "artifact":
            artifact,
        "model":
            model,
        "features":
            features,
        "train_categories":
            train_categories,
        "background_size":
            len(
                background_matrix
            ),
        "explainer":
            explainer,
        "operational":
            operational,
    }


# ============================================================
# EXPLICACIÓN LOCAL
# ============================================================

def explain_prospect(
    expediente_key: int,
    expected_score: float | None = None,
    top_n: int = 10,
) -> dict:
    """
    Genera una explicación SHAP local para una empresa.

    Parameters
    ----------
    expediente_key:
        Identificador de la empresa.

    expected_score:
        Score almacenado en el ranking operativo. Si se entrega,
        se valida contra el score reproducido directamente por
        el modelo.

    top_n:
        Número de variables con mayor impacto absoluto a devolver.
    """

    if top_n < 1:
        raise ValueError(
            "top_n debe ser mayor o igual a 1."
        )

    runtime = _get_runtime()

    artifact = runtime[
        "artifact"
    ]

    model = runtime[
        "model"
    ]

    features = runtime[
        "features"
    ]

    explainer = runtime[
        "explainer"
    ]

    operational = runtime[
        "operational"
    ]

    if (
        expediente_key
        not in operational.index
    ):
        raise KeyError(
            "El expediente solicitado no pertenece "
            "al universo operativo 2023."
        )

    row = (
        operational.loc[
            [
                expediente_key
            ]
        ]
        .copy()
    )

    feature_frame = row[
        features
    ]

    model_score = float(
        model.predict_proba(
            feature_frame
        )[
            0,
            1,
        ]
    )

    if expected_score is not None:

        score_difference = abs(
            model_score
            - float(
                expected_score
            )
        )

        if (
            score_difference
            > SCORE_TOLERANCE
        ):
            raise ExplainabilityError(
                "El score reproducido por el modelo "
                "no coincide con el ranking operativo. "
                f"Diferencia={score_difference:.12f}"
            )

    shap_matrix = (
        _encode_for_shap(
            feature_frame,
            artifact,
        )
    )

    max_evals = (
        2
        * len(
            features
        )
        + 1
    )

    shap_result = explainer(
        shap_matrix,
        max_evals=max_evals,
    )

    shap_values = np.asarray(
        shap_result.values[
            0
        ],
        dtype="float64",
    )

    base_value = float(
        np.asarray(
            shap_result.base_values
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

    if (
        local_error
        > SHAP_LOCAL_TOLERANCE
    ):
        raise ExplainabilityError(
            "SHAP no reconstruyó correctamente "
            "el score de la empresa. "
            f"Error={local_error:.12f}"
        )

    explanations: list[
        dict
    ] = []

    for feature_index, feature in enumerate(
        features
    ):

        shap_value = float(
            shap_values[
                feature_index
            ]
        )

        raw_value = (
            feature_frame[
                feature
            ].iloc[
                0
            ]
        )

        if shap_value > 0:
            direction = (
                "aumenta_afinidad"
            )
        elif shap_value < 0:
            direction = (
                "reduce_afinidad"
            )
        else:
            direction = (
                "sin_impacto"
            )

        explanations.append(
            {
                "feature":
                    feature,
                "label":
                    FEATURE_LABELS.get(
                        feature,
                        feature,
                    ),
                "value":
                    _json_value(
                        raw_value
                    ),
                "shap_value":
                    shap_value,
                "abs_shap_value":
                    abs(
                        shap_value
                    ),
                "direction":
                    direction,
            }
        )

    explanations.sort(
        key=lambda item: (
            item[
                "abs_shap_value"
            ]
        ),
        reverse=True,
    )

    top_n_effective = min(
        top_n,
        len(
            explanations
        ),
    )

    top_explanations = (
        explanations[
            :top_n_effective
        ]
    )

    positive_factors = [
        item
        for item in explanations
        if item[
            "shap_value"
        ] > 0
    ]

    negative_factors = [
        item
        for item in explanations
        if item[
            "shap_value"
        ] < 0
    ]

    return {
        "empresa": {
            "expediente_key":
                int(
                    expediente_key
                ),
            "ruc":
                _clean_text(
                    row[
                        "RUC"
                    ].iloc[
                        0
                    ]
                ),
            "nombre":
                _clean_text(
                    row[
                        "NOMBRE"
                    ].iloc[
                        0
                    ]
                ),
            "anio":
                int(
                    row[
                        "ANIO"
                    ].iloc[
                        0
                    ]
                ),
        },
        "score": {
            "modelo":
                model_score,
            "ranking_operativo":
                (
                    float(
                        expected_score
                    )
                    if expected_score
                    is not None
                    else None
                ),
            "diferencia":
                (
                    abs(
                        model_score
                        - float(
                            expected_score
                        )
                    )
                    if expected_score
                    is not None
                    else None
                ),
            "nota": (
                "El score es un indicador de "
                "priorización y no una probabilidad "
                "calibrada."
            ),
        },
        "shap": {
            "base_value":
                base_value,
            "reconstructed_score":
                reconstructed_score,
            "local_error":
                local_error,
            "background_train_size":
                runtime[
                    "background_size"
                ],
            "max_evals":
                max_evals,
            "method":
                (
                    "SHAP model-agnostic mediante "
                    "PermutationExplainer"
                ),
            "reference":
                (
                    "Background construido "
                    "exclusivamente desde TRAIN"
                ),
        },
        "principales_factores":
            top_explanations,
        "factores_que_aumentan_afinidad":
            positive_factors[
                :5
            ],
        "factores_que_reducen_afinidad":
            negative_factors[
                :5
            ],
        "metadata": {
            "model_name":
                artifact[
                    "model_name"
                ],
            "config_id":
                artifact[
                    "config_id"
                ],
            "features_total":
                len(
                    features
                ),
            "top_n":
                top_n_effective,
            "interpretation": (
                "Un valor SHAP positivo aumenta el "
                "score respecto al valor base; un "
                "valor SHAP negativo lo reduce."
            ),
        },
    }


# ============================================================
# IMPORTANCIA GLOBAL
# ============================================================

@lru_cache(
    maxsize=1
)
def _load_global_importance() -> pd.DataFrame:
    """
    Carga el resultado SHAP global ya validado
    durante el análisis post-test.
    """

    if not GLOBAL_SHAP_PATH.exists():
        raise FileNotFoundError(
            "No existe el archivo de importancia "
            "global SHAP esperado:\n"
            f"{GLOBAL_SHAP_PATH}"
        )

    dataframe = pd.read_csv(
        GLOBAL_SHAP_PATH
    )

    required_columns = {
        "RANK",
        "FEATURE",
        "MEAN_ABS_SHAP",
    }

    missing_columns = (
        required_columns
        - set(
            dataframe.columns
        )
    )

    if missing_columns:
        raise ExplainabilityError(
            "El archivo SHAP global no contiene "
            "las columnas esperadas: "
            f"{sorted(missing_columns)}"
        )

    return dataframe


def get_global_importance(
    limit: int = 15,
) -> dict:
    """
    Devuelve la importancia global SHAP ya calculada
    y validada sobre la muestra TEST.
    """

    if limit < 1:
        raise ValueError(
            "limit debe ser mayor o igual a 1."
        )

    dataframe = (
        _load_global_importance()
        .head(
            limit
        )
        .copy()
    )

    items = []

    for _, row in dataframe.iterrows():

        feature = str(
            row[
                "FEATURE"
            ]
        )

        items.append(
            {
                "rank":
                    int(
                        row[
                            "RANK"
                        ]
                    ),
                "feature":
                    feature,
                "label":
                    FEATURE_LABELS.get(
                        feature,
                        feature,
                    ),
                "mean_abs_shap":
                    float(
                        row[
                            "MEAN_ABS_SHAP"
                        ]
                    ),
            }
        )

    return {
        "method":
            (
                "SHAP model-agnostic mediante "
                "PermutationExplainer"
            ),
        "scope":
            (
                "Importancia global obtenida durante "
                "el análisis post-test del modelo "
                "congelado v10."
            ),
        "reference":
            (
                "Background construido exclusivamente "
                "desde TRAIN."
            ),
        "items":
            items,
    }