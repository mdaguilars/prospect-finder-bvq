from pathlib import Path
from datetime import datetime, timezone
import json
import platform
import sys
import warnings

import joblib
import numpy as np
import pandas as pd
import sklearn

from sklearn.compose import ColumnTransformer
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
)
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)
from sklearn.utils.class_weight import (
    compute_sample_weight,
)


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "v10_features_financial_2012_2023.csv.gz"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "v10"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
    / "v10"
)

METRICS_PATH = (
    OUTPUT_DIR
    / "v10_mlp_financial_metrics.csv"
)

RANKING_PATH = (
    OUTPUT_DIR
    / "v10_mlp_financial_ranking_metrics.csv"
)

CAPPING_PATH = (
    OUTPUT_DIR
    / "v10_mlp_financial_capping.csv"
)

TOP500_PATH = (
    OUTPUT_DIR
    / "v10_mlp_financial_validation_top500.csv"
)

METADATA_PATH = (
    OUTPUT_DIR
    / "v10_mlp_financial_metadata.json"
)

MODEL_PATH = (
    MODEL_DIR
    / "v10_mlp_financial.joblib"
)

TARGET = "TARGET_24M"

RANDOM_STATE = 42

CHUNK_SIZE = 150_000

K_VALUES = [
    50,
    100,
    200,
]

TOP_N_EXPORT = 500

CAPPING_LOWER_QUANTILE = 0.01

CAPPING_UPPER_QUANTILE = 0.99


# ============================================================
# FEATURES CORE
# ============================================================

FEATURES_NUMERICAS_CORE = [
    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",
    "activos_final_t1",
    "patrimonio_final_t1",
    "bi_ingresos_ventas_t1",
    "bi_n_empleados_t1",
]


FEATURES_BOOLEANAS_CORE = [
    "TIENE_T_MENOS_1",
    "flag_activos_negativos",
    "flag_ventas_negativas",
    "flag_empleados_fijo",
    "flag_empleados_salto_temporal",
    "flag_empleados_anomalia_total",
]


FEATURES_CATEGORICAS = [
    "tipo_compania",
]


# ============================================================
# FEATURES FINANCIERAS
# ============================================================

FEATURES_FINANCIERAS_NUMERICAS = [
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


FEATURES_FINANCIERAS_BOOLEANAS = [
    "flag_patrimonio_no_positivo",
]


# ============================================================
# CONJUNTO TOTAL DE FEATURES
# ============================================================

FEATURES_NUMERICAS = (
    FEATURES_NUMERICAS_CORE
    + FEATURES_FINANCIERAS_NUMERICAS
)


FEATURES_BOOLEANAS = (
    FEATURES_BOOLEANAS_CORE
    + FEATURES_FINANCIERAS_BOOLEANAS
)


FEATURES = (
    FEATURES_NUMERICAS
    + FEATURES_BOOLEANAS
    + FEATURES_CATEGORICAS
)


ID_COLUMNS = [
    "ANIO",
    "EXPEDIENTE_KEY",
    "RUC",
    "NOMBRE",
]


COLUMNAS_LECTURA = list(
    dict.fromkeys(
        ID_COLUMNS
        + [
            "SPLIT",
            TARGET,
        ]
        + FEATURES
    )
)


# ============================================================
# CONFIGURACIÓN MLP
# ============================================================

#
# Se mantiene la arquitectura utilizada
# en el MLP core v10.
#
# No se realiza tuning en este experimento.
#

MLP_PARAMS = {
    "hidden_layer_sizes":
        (
            64,
            32,
        ),

    "activation":
        "relu",

    "solver":
        "adam",

    "alpha":
        0.01,

    "batch_size":
        512,

    "learning_rate_init":
        0.001,

    "max_iter":
        200,

    "shuffle":
        True,

    "random_state":
        RANDOM_STATE,

    "tol":
        1e-4,

    "early_stopping":
        False,

    "n_iter_no_change":
        10,
}


# ============================================================
# UNIVERSO CONGELADO
# ============================================================

EXPECTED = {
    "TRAIN": {
        "filas":
            470_722,

        "positivos":
            407,
    },

    "VALIDATION": {
        "filas":
            98_471,

        "positivos":
            34,
    },
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def ruta_relativa(
    path,
):

    return str(
        path.relative_to(
            PROJECT_ROOT
        )
    ).replace(
        "\\",
        "/",
    )


def normalizar_booleana(
    serie,
):

    texto = (
        serie
        .astype(
            "string"
        )
        .str.strip()
        .str.lower()
    )

    mapa = {
        "true":
            1.0,

        "false":
            0.0,

        "1":
            1.0,

        "0":
            0.0,

        "1.0":
            1.0,

        "0.0":
            0.0,

        "si":
            1.0,

        "sí":
            1.0,

        "no":
            0.0,

        "yes":
            1.0,

        "verdadero":
            1.0,

        "falso":
            0.0,
    }

    por_texto = texto.map(
        mapa
    )

    por_numero = pd.to_numeric(
        serie,
        errors="coerce",
    )

    por_numero = por_numero.where(
        por_numero.isin(
            [
                0,
                1,
            ]
        )
    )

    resultado = por_texto.fillna(
        por_numero
    )

    return resultado.astype(
        "float64"
    )


# ============================================================
# PREPARACIÓN DE TIPOS
# ============================================================

def preparar_tipos(
    dataframe,
):

    df = dataframe.copy()

    # --------------------------------------------------------
    # AÑO
    # --------------------------------------------------------

    df[
        "ANIO"
    ] = pd.to_numeric(
        df[
            "ANIO"
        ],
        errors="coerce",
    )

    if df[
        "ANIO"
    ].isna().any():

        raise ValueError(
            "Existen valores ANIO inválidos."
        )

    df[
        "ANIO"
    ] = df[
        "ANIO"
    ].astype(
        "int64"
    )

    # --------------------------------------------------------
    # TARGET
    # --------------------------------------------------------

    df[
        TARGET
    ] = pd.to_numeric(
        df[
            TARGET
        ],
        errors="coerce",
    )

    if df[
        TARGET
    ].isna().any():

        raise ValueError(
            "Existen valores "
            "TARGET_24M inválidos."
        )

    valores_target = set(
        df[
            TARGET
        ]
        .unique()
        .tolist()
    )

    if not valores_target.issubset(
        {
            0,
            1,
        }
    ):

        raise ValueError(
            "TARGET_24M contiene "
            "valores distintos de 0 y 1."
        )

    df[
        TARGET
    ] = df[
        TARGET
    ].astype(
        "int64"
    )

    # --------------------------------------------------------
    # NUMÉRICAS
    # --------------------------------------------------------

    for variable in FEATURES_NUMERICAS:

        df[
            variable
        ] = pd.to_numeric(
            df[
                variable
            ],
            errors="coerce",
        )

    df[
        FEATURES_NUMERICAS
    ] = df[
        FEATURES_NUMERICAS
    ].replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )

    # --------------------------------------------------------
    # BOOLEANAS
    # --------------------------------------------------------

    for variable in FEATURES_BOOLEANAS:

        df[
            variable
        ] = normalizar_booleana(
            df[
                variable
            ]
        )

    # --------------------------------------------------------
    # CATEGÓRICAS
    # --------------------------------------------------------

    for variable in FEATURES_CATEGORICAS:

        serie = df[
            variable
        ].astype(
            "string"
        )

        df[
            variable
        ] = serie.astype(
            object
        )

        df.loc[
            serie.isna(),
            variable,
        ] = np.nan

    return df


# ============================================================
# CARGA TRAIN + VALIDATION
# ============================================================

def cargar_datos():

    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"No existe el dataset:\n"
            f"{INPUT_PATH}"
        )

    encabezado = pd.read_csv(
        INPUT_PATH,
        nrows=0,
    )

    disponibles = set(
        encabezado.columns
    )

    faltantes = [
        columna
        for columna in COLUMNAS_LECTURA
        if columna not in disponibles
    ]

    if faltantes:

        raise ValueError(
            "Faltan columnas requeridas:\n"
            + "\n".join(
                faltantes
            )
        )

    print(
        "\nCargando exclusivamente "
        "TRAIN y VALIDATION..."
    )

    print(
        INPUT_PATH
    )

    partes = []

    dtype_lectura = {
        "SPLIT":
            "string",

        "tipo_compania":
            "string",

        "EXPEDIENTE_KEY":
            "string",

        "RUC":
            "string",

        "NOMBRE":
            "string",
    }

    for chunk in pd.read_csv(
        INPUT_PATH,
        usecols=COLUMNAS_LECTURA,
        chunksize=CHUNK_SIZE,
        low_memory=False,
        dtype=dtype_lectura,
    ):

        split_normalizado = (
            chunk[
                "SPLIT"
            ]
            .astype(
                "string"
            )
            .str.strip()
            .str.upper()
        )

        mascara = split_normalizado.isin(
            [
                "TRAIN",
                "VALIDATION",
            ]
        )

        if mascara.any():

            bloque = chunk.loc[
                mascara
            ].copy()

            bloque[
                "SPLIT"
            ] = (
                split_normalizado.loc[
                    mascara
                ]
                .astype(
                    "string"
                )
            )

            partes.append(
                bloque
            )

    if not partes:

        raise ValueError(
            "No se encontraron observaciones "
            "TRAIN o VALIDATION."
        )

    dataframe = pd.concat(
        partes,
        ignore_index=True,
    )

    return preparar_tipos(
        dataframe
    )


# ============================================================
# VALIDACIÓN DEL UNIVERSO
# ============================================================

def validar_universo(
    dataframe,
):

    print(
        "\nValidando universo congelado..."
    )

    splits_presentes = set(
        dataframe[
            "SPLIT"
        ]
        .unique()
        .tolist()
    )

    if splits_presentes != {
        "TRAIN",
        "VALIDATION",
    }:

        raise ValueError(
            "Se cargaron splits distintos "
            "de TRAIN y VALIDATION."
        )

    for split, esperado in EXPECTED.items():

        subset = dataframe[
            dataframe[
                "SPLIT"
            ]
            == split
        ]

        filas = len(
            subset
        )

        positivos = int(
            subset[
                TARGET
            ].sum()
        )

        print(
            f"{split}: "
            f"{filas:,} filas | "
            f"{positivos} positivos"
        )

        if filas != esperado[
            "filas"
        ]:

            raise ValueError(
                f"{split}: número de "
                f"filas incorrecto."
            )

        if positivos != esperado[
            "positivos"
        ]:

            raise ValueError(
                f"{split}: número de "
                f"positivos incorrecto."
            )


# ============================================================
# CAPPING TRAIN-ONLY
# ============================================================

def aprender_limites_capping(
    train,
):

    limites = {}

    filas = []

    for variable in (
        FEATURES_FINANCIERAS_NUMERICAS
    ):

        serie = pd.to_numeric(
            train[
                variable
            ],
            errors="coerce",
        ).replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )

        validos = serie.dropna()

        if validos.empty:

            raise ValueError(
                f"{variable} no contiene "
                "valores válidos en TRAIN."
            )

        lower = float(
            validos.quantile(
                CAPPING_LOWER_QUANTILE
            )
        )

        upper = float(
            validos.quantile(
                CAPPING_UPPER_QUANTILE
            )
        )

        if not np.isfinite(
            lower
        ):

            raise ValueError(
                f"Lower inválido para "
                f"{variable}."
            )

        if not np.isfinite(
            upper
        ):

            raise ValueError(
                f"Upper inválido para "
                f"{variable}."
            )

        if lower > upper:

            raise ValueError(
                f"Límites invertidos para "
                f"{variable}."
            )

        limites[
            variable
        ] = {
            "lower":
                lower,

            "upper":
                upper,
        }

        filas.append(
            {
                "VARIABLE":
                    variable,

                "QUANTILE_LOWER":
                    CAPPING_LOWER_QUANTILE,

                "QUANTILE_UPPER":
                    CAPPING_UPPER_QUANTILE,

                "LOWER_BOUND":
                    lower,

                "UPPER_BOUND":
                    upper,

                "TRAIN_NO_NULOS":
                    int(
                        serie.notna().sum()
                    ),

                "TRAIN_DEBAJO_LIMITE":
                    int(
                        (
                            serie
                            < lower
                        ).sum()
                    ),

                "TRAIN_SOBRE_LIMITE":
                    int(
                        (
                            serie
                            > upper
                        ).sum()
                    ),
            }
        )

    return (
        limites,
        pd.DataFrame(
            filas
        ),
    )


def aplicar_capping(
    dataframe,
    limites,
):

    df = dataframe.copy()

    for variable in (
        FEATURES_FINANCIERAS_NUMERICAS
    ):

        lower = limites[
            variable
        ][
            "lower"
        ]

        upper = limites[
            variable
        ][
            "upper"
        ]

        serie = pd.to_numeric(
            df[
                variable
            ],
            errors="coerce",
        ).replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )

        df[
            variable
        ] = serie.clip(
            lower=lower,
            upper=upper,
        )

    return df


# ============================================================
# PREPROCESAMIENTO
# ============================================================

def construir_preprocesador():

    pipeline_numerico = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
        ]
    )

    pipeline_booleano = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                ),
            ),
        ]
    )

    pipeline_categorico = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="constant",
                    fill_value="MISSING",
                ),
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                pipeline_numerico,
                FEATURES_NUMERICAS,
            ),
            (
                "boolean",
                pipeline_booleano,
                FEATURES_BOOLEANAS,
            ),
            (
                "categorical",
                pipeline_categorico,
                FEATURES_CATEGORICAS,
            ),
        ],
        remainder="drop",
    )


def construir_modelo():

    return Pipeline(
        steps=[
            (
                "preprocessor",
                construir_preprocesador(),
            ),
            (
                "classifier",
                MLPClassifier(
                    **MLP_PARAMS
                ),
            ),
        ]
    )


# ============================================================
# MÉTRICAS
# ============================================================

def calcular_metricas(
    y_true,
    scores,
):

    return {
        "PR_AUC":
            float(
                average_precision_score(
                    y_true,
                    scores,
                )
            ),

        "ROC_AUC":
            float(
                roc_auc_score(
                    y_true,
                    scores,
                )
            ),
    }


def calcular_ranking(
    y_true,
    scores,
):

    tabla = pd.DataFrame(
        {
            "TARGET":
                np.asarray(
                    y_true
                ),

            "SCORE":
                np.asarray(
                    scores
                ),
        }
    )

    tabla = tabla.sort_values(
        "SCORE",
        ascending=False,
        kind="mergesort",
    ).reset_index(
        drop=True
    )

    positivos_totales = int(
        tabla[
            "TARGET"
        ].sum()
    )

    prevalencia = (
        positivos_totales
        / len(
            tabla
        )
    )

    resultados = []

    for k in K_VALUES:

        top = tabla.head(
            k
        )

        positivos_top = int(
            top[
                "TARGET"
            ].sum()
        )

        precision_k = (
            positivos_top
            / k
        )

        recall_k = (
            positivos_top
            / positivos_totales
            if positivos_totales > 0
            else np.nan
        )

        lift_k = (
            precision_k
            / prevalencia
            if prevalencia > 0
            else np.nan
        )

        resultados.append(
            {
                "K":
                    k,

                "POSITIVOS_TOP_K":
                    positivos_top,

                "PRECISION_AT_K":
                    float(
                        precision_k
                    ),

                "RECALL_AT_K":
                    float(
                        recall_k
                    ),

                "LIFT_AT_K":
                    float(
                        lift_k
                    ),
            }
        )

    return pd.DataFrame(
        resultados
    )


# ============================================================
# TOP 500 VALIDATION
# ============================================================

def construir_top500(
    validation_original,
    scores,
):

    columnas = [
        columna
        for columna in ID_COLUMNS
        if columna
        in validation_original.columns
    ]

    top = validation_original[
        columnas
        + [
            TARGET
        ]
    ].copy()

    top[
        "SCORE"
    ] = np.asarray(
        scores
    )

    top = top.sort_values(
        "SCORE",
        ascending=False,
        kind="mergesort",
    ).head(
        TOP_N_EXPORT
    ).reset_index(
        drop=True
    )

    top.insert(
        0,
        "RANK",
        np.arange(
            1,
            len(
                top
            )
            + 1,
        ),
    )

    return top


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        + "=" * 120
    )

    print(
        "PROSPECT FINDER BVQ"
    )

    print(
        "MLP FINANCIAL v10"
    )

    print(
        "=" * 120
    )

    print(
        "\nModelo:"
    )

    print(
        "MLPClassifier"
    )

    print(
        "\nArquitectura:"
    )

    print(
        "(64, 32) | relu | adam"
    )

    print(
        "\nRegularización y entrenamiento:"
    )

    print(
        "alpha=0.01 | "
        "batch_size=512 | "
        "learning_rate_init=0.001 | "
        "max_iter=200"
    )

    print(
        "\nFeatures:"
    )

    print(
        f"{len(FEATURES)} "
        "variables físicas"
    )

    print(
        "\nCapping:"
    )

    print(
        "P01-P99 únicamente sobre las "
        "9 features financieras numéricas."
    )

    print(
        "Los límites se aprenden "
        "exclusivamente con TRAIN."
    )

    print(
        "\nDesbalance:"
    )

    print(
        "sample_weight balanceado "
        "calculado exclusivamente con TRAIN."
    )

    print(
        "\nTEST 2022-2023:"
    )

    print(
        "RESERVADO - NO SE CARGARÁ"
    )

    # --------------------------------------------------------
    # CARGA Y VALIDACIÓN
    # --------------------------------------------------------

    dataframe = cargar_datos()

    validar_universo(
        dataframe
    )

    train_original = dataframe[
        dataframe[
            "SPLIT"
        ]
        == "TRAIN"
    ].copy()

    validation_original = dataframe[
        dataframe[
            "SPLIT"
        ]
        == "VALIDATION"
    ].copy()

    # --------------------------------------------------------
    # CAPPING
    # --------------------------------------------------------

    (
        limites_capping,
        capping_df,
    ) = aprender_limites_capping(
        train_original
    )

    print(
        "\nLímites P01-P99 "
        "aprendidos desde TRAIN:"
    )

    for _, fila in capping_df.iterrows():

        print(
            f"{fila['VARIABLE']}: "
            f"["
            f"{fila['LOWER_BOUND']:.6f}, "
            f"{fila['UPPER_BOUND']:.6f}"
            f"]"
        )

    train = aplicar_capping(
        train_original,
        limites_capping,
    )

    validation = aplicar_capping(
        validation_original,
        limites_capping,
    )

    # --------------------------------------------------------
    # MATRICES
    # --------------------------------------------------------

    X_train = train[
        FEATURES
    ].copy()

    y_train = train[
        TARGET
    ].astype(
        int
    )

    X_validation = validation[
        FEATURES
    ].copy()

    y_validation = validation[
        TARGET
    ].astype(
        int
    )

    # --------------------------------------------------------
    # PESOS BALANCEADOS TRAIN-ONLY
    # --------------------------------------------------------

    sample_weights = (
        compute_sample_weight(
            class_weight="balanced",
            y=y_train,
        )
    )

    print(
        "\nPesos de clase implícitos "
        "en TRAIN:"
    )

    for clase in [
        0,
        1,
    ]:

        mascara = (
            y_train.to_numpy()
            == clase
        )

        peso_clase = float(
            sample_weights[
                mascara
            ][
                0
            ]
        )

        print(
            f"Clase {clase}: "
            f"{peso_clase:.6f}"
        )

    # --------------------------------------------------------
    # MODELO
    # --------------------------------------------------------

    modelo = construir_modelo()

    convergence_warning = False

    warning_messages = []

    print(
        "\nEntrenando MLP..."
    )

    with warnings.catch_warnings(
        record=True
    ) as warnings_capturados:

        warnings.simplefilter(
            "always",
            ConvergenceWarning,
        )

        modelo.fit(
            X_train,
            y_train,
            classifier__sample_weight=
                sample_weights,
        )

        for warning in warnings_capturados:

            if issubclass(
                warning.category,
                ConvergenceWarning,
            ):

                convergence_warning = True

                warning_messages.append(
                    str(
                        warning.message
                    )
                )

    # --------------------------------------------------------
    # FEATURES TRANSFORMADAS
    # --------------------------------------------------------

    preprocessor = modelo.named_steps[
        "preprocessor"
    ]

    try:

        n_features_transformadas = len(
            preprocessor
            .get_feature_names_out()
        )

    except Exception:

        muestra = preprocessor.transform(
            X_train.head(
                2
            )
        )

        n_features_transformadas = int(
            muestra.shape[
                1
            ]
        )

    classifier = modelo.named_steps[
        "classifier"
    ]

    n_iter = int(
        classifier.n_iter_
    )

    loss_final = float(
        classifier.loss_
    )

    # --------------------------------------------------------
    # PREDICCIONES
    # --------------------------------------------------------

    score_train = modelo.predict_proba(
        X_train
    )[
        :,
        1,
    ]

    score_validation = modelo.predict_proba(
        X_validation
    )[
        :,
        1,
    ]

    # --------------------------------------------------------
    # MÉTRICAS
    # --------------------------------------------------------

    metricas_train = calcular_metricas(
        y_train,
        score_train,
    )

    metricas_validation = calcular_metricas(
        y_validation,
        score_validation,
    )

    metrics_df = pd.DataFrame(
        [
            {
                "MODELO":
                    "v10_mlp_financial",

                "SPLIT":
                    "TRAIN",

                "N":
                    len(
                        y_train
                    ),

                "POSITIVOS":
                    int(
                        y_train.sum()
                    ),

                "PREVALENCIA":
                    float(
                        y_train.mean()
                    ),

                "PR_AUC":
                    metricas_train[
                        "PR_AUC"
                    ],

                "ROC_AUC":
                    metricas_train[
                        "ROC_AUC"
                    ],

                "N_FEATURES_FISICAS":
                    len(
                        FEATURES
                    ),

                "N_FEATURES_TRANSFORMADAS":
                    n_features_transformadas,

                "N_ITER":
                    n_iter,

                "LOSS_FINAL":
                    loss_final,

                "CONVERGENCE_WARNING":
                    convergence_warning,
            },

            {
                "MODELO":
                    "v10_mlp_financial",

                "SPLIT":
                    "VALIDATION",

                "N":
                    len(
                        y_validation
                    ),

                "POSITIVOS":
                    int(
                        y_validation.sum()
                    ),

                "PREVALENCIA":
                    float(
                        y_validation.mean()
                    ),

                "PR_AUC":
                    metricas_validation[
                        "PR_AUC"
                    ],

                "ROC_AUC":
                    metricas_validation[
                        "ROC_AUC"
                    ],

                "N_FEATURES_FISICAS":
                    len(
                        FEATURES
                    ),

                "N_FEATURES_TRANSFORMADAS":
                    n_features_transformadas,

                "N_ITER":
                    n_iter,

                "LOSS_FINAL":
                    loss_final,

                "CONVERGENCE_WARNING":
                    convergence_warning,
            },
        ]
    )

    # --------------------------------------------------------
    # RANKING
    # --------------------------------------------------------

    ranking_df = calcular_ranking(
        y_validation,
        score_validation,
    )

    ranking_df.insert(
        0,
        "MODELO",
        "v10_mlp_financial",
    )

    ranking_df.insert(
        1,
        "SPLIT",
        "VALIDATION",
    )

    ranking_df.insert(
        2,
        "N",
        len(
            y_validation
        ),
    )

    ranking_df.insert(
        3,
        "POSITIVOS",
        int(
            y_validation.sum()
        ),
    )

    # --------------------------------------------------------
    # TOP 500
    # --------------------------------------------------------

    top500_df = construir_top500(
        validation_original,
        score_validation,
    )

    # --------------------------------------------------------
    # DIRECTORIOS
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # GUARDAR RESULTADOS
    # --------------------------------------------------------

    metrics_df.to_csv(
        METRICS_PATH,
        index=False,
    )

    ranking_df.to_csv(
        RANKING_PATH,
        index=False,
    )

    capping_df.to_csv(
        CAPPING_PATH,
        index=False,
    )

    top500_df.to_csv(
        TOP500_PATH,
        index=False,
    )

    # --------------------------------------------------------
    # GUARDAR MODELO
    # --------------------------------------------------------

    bundle_modelo = {
        "model":
            modelo,

        "capping_limits":
            limites_capping,

        "features":
            FEATURES,

        "financial_numeric_features":
            FEATURES_FINANCIERAS_NUMERICAS,

        "target":
            TARGET,
    }

    joblib.dump(
        bundle_modelo,
        MODEL_PATH,
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    metadata = {
        "experimento":
            (
                "MLP financiero v10 - "
                "TRAIN vs VALIDATION"
            ),

        "fecha_ejecucion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "dataset":
            ruta_relativa(
                INPUT_PATH
            ),

        "modelo":
            "MLPClassifier",

        "nombre_modelo":
            "v10_mlp_financial",

        "baseline_referencia":
            "v10_mlp_core",

        "target":
            TARGET,

        "horizonte_target":
            "24 meses",

        "numero_features_fisicas":
            len(
                FEATURES
            ),

        "numero_features_transformadas":
            n_features_transformadas,

        "features_fisicas":
            FEATURES,

        "features_numericas_core":
            FEATURES_NUMERICAS_CORE,

        "features_financieras_numericas":
            FEATURES_FINANCIERAS_NUMERICAS,

        "features_booleanas":
            FEATURES_BOOLEANAS,

        "features_categoricas":
            FEATURES_CATEGORICAS,

        "provincia_utilizada":
            False,

        "modelo_parametros":
            MLP_PARAMS,

        "preprocesamiento": {
            "capping":
                (
                    "P01-P99 aprendido "
                    "exclusivamente desde TRAIN "
                    "para las 9 features "
                    "financieras numéricas."
                ),

            "numericas":
                (
                    "SimpleImputer(strategy='median') "
                    "+ StandardScaler, ambos "
                    "aprendidos exclusivamente "
                    "desde TRAIN."
                ),

            "booleanas":
                (
                    "SimpleImputer("
                    "strategy='most_frequent') "
                    "aprendido desde TRAIN."
                ),

            "categoricas":
                (
                    "SimpleImputer("
                    "strategy='constant', "
                    "fill_value='MISSING') + "
                    "OneHotEncoder("
                    "handle_unknown='ignore'), "
                    "aprendidos desde TRAIN."
                ),
        },

        "desbalance": {
            "metodo":
                "sample_weight balanced",

            "origen":
                (
                    "Calculado exclusivamente "
                    "desde y_train."
                ),
        },

        "entrenamiento": {
            "n_iter":
                n_iter,

            "loss_final":
                loss_final,

            "convergence_warning":
                convergence_warning,

            "warning_messages":
                warning_messages,
        },

        "resultados": {
            "train":
                metricas_train,

            "validation":
                metricas_validation,

            "ranking_validation":
                ranking_df.to_dict(
                    orient="records"
                ),
        },

        "test": {
            "periodo":
                "2022-2023",

            "cargado":
                False,

            "transformado":
                False,

            "evaluado":
                False,

            "estado":
                "RESERVADO",
        },

        "archivos_salida": {
            "metricas":
                ruta_relativa(
                    METRICS_PATH
                ),

            "ranking":
                ruta_relativa(
                    RANKING_PATH
                ),

            "capping":
                ruta_relativa(
                    CAPPING_PATH
                ),

            "validation_top500":
                ruta_relativa(
                    TOP500_PATH
                ),

            "modelo":
                ruta_relativa(
                    MODEL_PATH
                ),

            "metadata":
                ruta_relativa(
                    METADATA_PATH
                ),
        },

        "entorno": {
            "python":
                sys.version.split()[
                    0
                ],

            "platform":
                platform.platform(),

            "pandas":
                pd.__version__,

            "numpy":
                np.__version__,

            "scikit_learn":
                sklearn.__version__,
        },
    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8",
    ) as archivo:

        json.dump(
            metadata,
            archivo,
            ensure_ascii=False,
            indent=2,
        )

    # --------------------------------------------------------
    # RESULTADOS EN CONSOLA
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 120
    )

    print(
        "RESULTADOS - MLP FINANCIAL v10"
    )

    print(
        "=" * 120
    )

    print(
        f"\nFeatures físicas: "
        f"{len(FEATURES)}"
    )

    print(
        f"Features transformadas: "
        f"{n_features_transformadas}"
    )

    print(
        f"Número de iteraciones: "
        f"{n_iter}"
    )

    print(
        f"Loss final: "
        f"{loss_final:.9f}"
    )

    print(
        "\nTRAIN"
    )

    print(
        f"PR-AUC:  "
        f"{metricas_train['PR_AUC']:.9f}"
    )

    print(
        f"ROC-AUC: "
        f"{metricas_train['ROC_AUC']:.9f}"
    )

    print(
        "\nVALIDATION"
    )

    print(
        f"PR-AUC:  "
        f"{metricas_validation['PR_AUC']:.9f}"
    )

    print(
        f"ROC-AUC: "
        f"{metricas_validation['ROC_AUC']:.9f}"
    )

    print(
        "\nRanking VALIDATION:"
    )

    for _, fila in ranking_df.iterrows():

        print(
            f"Top "
            f"{int(fila['K']):>3}: "
            f"{int(fila['POSITIVOS_TOP_K'])} "
            f"positivos | "
            f"Precision="
            f"{fila['PRECISION_AT_K']:.6f} | "
            f"Recall="
            f"{fila['RECALL_AT_K']:.6f} | "
            f"Lift="
            f"{fila['LIFT_AT_K']:.6f}"
        )

    print(
        "\nConvergenceWarning:"
    )

    print(
        convergence_warning
    )

    if warning_messages:

        print(
            "\nMensajes de convergencia:"
        )

        for mensaje in warning_messages:

            print(
                mensaje
            )

    print(
        "\nTEST 2022-2023:"
    )

    print(
        "RESERVADO - NO CARGADO - NO EVALUADO"
    )

    print(
        "\nArchivos generados:"
    )

    print(
        METRICS_PATH
    )

    print(
        RANKING_PATH
    )

    print(
        CAPPING_PATH
    )

    print(
        TOP500_PATH
    )

    print(
        METADATA_PATH
    )

    print(
        MODEL_PATH
    )

    print(
        "\nExperimento finalizado correctamente."
    )


if __name__ == "__main__":
    main()