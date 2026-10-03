from pathlib import Path
from datetime import datetime, timezone
import json
import platform
import sys
import warnings

import numpy as np
import pandas as pd
import sklearn

from sklearn.compose import ColumnTransformer
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

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


METRICS_PATH = (
    OUTPUT_DIR
    / "backtest_lr_financial_v10_metrics.csv"
)

RANKING_PATH = (
    OUTPUT_DIR
    / "backtest_lr_financial_v10_ranking_metrics.csv"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "backtest_lr_financial_v10_summary.csv"
)

CAPPING_PATH = (
    OUTPUT_DIR
    / "backtest_lr_financial_v10_capping.csv"
)

METADATA_PATH = (
    OUTPUT_DIR
    / "backtest_lr_financial_v10_metadata.json"
)


TARGET = "TARGET_24M"

RANDOM_STATE = 42

CHUNK_SIZE = 150_000

K_VALUES = [
    50,
    100,
    200,
]

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
# CONJUNTO TOTAL
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


# ============================================================
# COLUMNAS A LEER
# ============================================================

COLUMNAS_LECTURA = list(
    dict.fromkeys(
        [
            "ANIO",
            "SPLIT",
            TARGET,
        ]
        + FEATURES
    )
)


# ============================================================
# PARÁMETROS DEL MODELO
# ============================================================

#
# Misma configuración utilizada en:
# v10_lr_no_provincia
# y
# v10_lr_financial
#

LOGISTIC_PARAMS = {
    "penalty":
        "l2",

    "C":
        1.0,

    "solver":
        "lbfgs",

    "max_iter":
        2000,

    "class_weight":
        "balanced",

    "random_state":
        RANDOM_STATE,
}


# ============================================================
# FOLDS TEMPORALES CONGELADOS
# ============================================================

FOLDS = [
    {
        "FOLD":
            1,

        "TRAIN_INICIO":
            2012,

        "TRAIN_FIN":
            2013,

        "ANIO_EMBARGO":
            2014,

        "ANIO_EVALUACION":
            2015,
    },

    {
        "FOLD":
            2,

        "TRAIN_INICIO":
            2012,

        "TRAIN_FIN":
            2014,

        "ANIO_EMBARGO":
            2015,

        "ANIO_EVALUACION":
            2016,
    },

    {
        "FOLD":
            3,

        "TRAIN_INICIO":
            2012,

        "TRAIN_FIN":
            2015,

        "ANIO_EMBARGO":
            2016,

        "ANIO_EVALUACION":
            2017,
    },

    {
        "FOLD":
            4,

        "TRAIN_INICIO":
            2012,

        "TRAIN_FIN":
            2016,

        "ANIO_EMBARGO":
            2017,

        "ANIO_EVALUACION":
            2018,
    },
]


# ============================================================
# UNIVERSO ESPERADO
# ============================================================

EXPECTED_TRAIN_ROWS = 470_722
EXPECTED_TRAIN_POSITIVES = 407


EXPECTED_YEAR_COUNTS = {
    2012: {
        "filas":
            42_158,

        "positivos":
            55,
    },

    2013: {
        "filas":
            47_140,

        "positivos":
            49,
    },

    2014: {
        "filas":
            52_528,

        "positivos":
            39,
    },

    2015: {
        "filas":
            76_468,

        "positivos":
            43,
    },

    2016: {
        "filas":
            79_503,

        "positivos":
            73,
    },

    2017: {
        "filas":
            83_107,

        "positivos":
            89,
    },

    2018: {
        "filas":
            89_818,

        "positivos":
            59,
    },
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def ruta_relativa(path):

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
    # ANIO
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
            "Existen TARGET_24M inválidos."
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
            "TARGET_24M contiene valores "
            "distintos de 0 y 1."
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
    # CATEGÓRICA
    # --------------------------------------------------------

    for variable in FEATURES_CATEGORICAS:

        serie = df[
            variable
        ].astype(
            "string"
        )

        df[
            variable
        ] = np.where(
            serie.isna(),
            np.nan,
            serie.astype(
                object
            ),
        )

    return df


# ============================================================
# CARGA DEL DATASET
# ============================================================

def cargar_train():

    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"No existe el dataset:\n{INPUT_PATH}"
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
        "\nCargando exclusivamente SPLIT=TRAIN..."
    )

    print(
        INPUT_PATH
    )

    partes = []

    for chunk in pd.read_csv(
        INPUT_PATH,
        usecols=COLUMNAS_LECTURA,
        chunksize=CHUNK_SIZE,
        low_memory=False,
        dtype={
            "SPLIT":
                "string",

            "tipo_compania":
                "string",
        },
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

        mascara = (
            split_normalizado
            == "TRAIN"
        )

        if mascara.any():

            bloque = chunk.loc[
                mascara
            ].copy()

            bloque[
                "SPLIT"
            ] = "TRAIN"

            partes.append(
                bloque
            )

    if not partes:

        raise ValueError(
            "No se encontraron observaciones TRAIN."
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
    train,
):

    print(
        "\nValidando universo congelado TRAIN..."
    )

    filas = len(
        train
    )

    positivos = int(
        train[
            TARGET
        ].sum()
    )

    print(
        f"TRAIN: "
        f"{filas:,} filas | "
        f"{positivos} positivos"
    )

    if filas != EXPECTED_TRAIN_ROWS:

        raise ValueError(
            "Número de filas TRAIN incorrecto."
        )

    if positivos != EXPECTED_TRAIN_POSITIVES:

        raise ValueError(
            "Número de positivos TRAIN incorrecto."
        )

    print(
        "\nValidando distribución anual..."
    )

    for anio in sorted(
        EXPECTED_YEAR_COUNTS
    ):

        subset = train[
            train[
                "ANIO"
            ]
            == anio
        ]

        filas_anio = len(
            subset
        )

        positivos_anio = int(
            subset[
                TARGET
            ].sum()
        )

        esperado = EXPECTED_YEAR_COUNTS[
            anio
        ]

        print(
            f"{anio}: "
            f"{filas_anio:,} filas | "
            f"{positivos_anio} positivos"
        )

        if filas_anio != esperado[
            "filas"
        ]:

            raise ValueError(
                f"Año {anio}: número de filas incorrecto."
            )

        if positivos_anio != esperado[
            "positivos"
        ]:

            raise ValueError(
                f"Año {anio}: número de positivos incorrecto."
            )


# ============================================================
# CAPPING TRAIN-ONLY
# ============================================================

def aprender_limites_capping(
    train_fold,
    numero_fold,
):

    limites = {}

    filas = []

    for variable in FEATURES_FINANCIERAS_NUMERICAS:

        serie = pd.to_numeric(
            train_fold[
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
                f"Fold {numero_fold}: "
                f"{variable} no contiene valores válidos."
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
                f"Fold {numero_fold}: "
                f"lower inválido para {variable}."
            )

        if not np.isfinite(
            upper
        ):

            raise ValueError(
                f"Fold {numero_fold}: "
                f"upper inválido para {variable}."
            )

        if lower > upper:

            raise ValueError(
                f"Fold {numero_fold}: "
                f"límites invertidos para {variable}."
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
                "FOLD":
                    numero_fold,

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
        filas,
    )


def aplicar_capping(
    dataframe,
    limites,
):

    df = dataframe.copy()

    for variable in FEATURES_FINANCIERAS_NUMERICAS:

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
                    strategy="most_frequent"
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
                LogisticRegression(
                    **LOGISTIC_PARAMS
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

    return resultados


# ============================================================
# EJECUTAR UN FOLD
# ============================================================

def ejecutar_fold(
    train_completo,
    fold,
):

    numero_fold = fold[
        "FOLD"
    ]

    train_inicio = fold[
        "TRAIN_INICIO"
    ]

    train_fin = fold[
        "TRAIN_FIN"
    ]

    anio_embargo = fold[
        "ANIO_EMBARGO"
    ]

    anio_evaluacion = fold[
        "ANIO_EVALUACION"
    ]

    # --------------------------------------------------------
    # SELECCIÓN TEMPORAL
    # --------------------------------------------------------

    train_fold = train_completo[
        (
            train_completo[
                "ANIO"
            ]
            >= train_inicio
        )
        &
        (
            train_completo[
                "ANIO"
            ]
            <= train_fin
        )
    ].copy()

    eval_fold = train_completo[
        train_completo[
            "ANIO"
        ]
        == anio_evaluacion
    ].copy()

    if train_fold.empty:

        raise ValueError(
            f"Fold {numero_fold}: TRAIN vacío."
        )

    if eval_fold.empty:

        raise ValueError(
            f"Fold {numero_fold}: evaluación vacía."
        )

    if (
        anio_embargo
        in train_fold[
            "ANIO"
        ].unique()
    ):

        raise ValueError(
            f"Fold {numero_fold}: "
            f"año de embargo dentro de TRAIN."
        )

    # --------------------------------------------------------
    # CAPPING APRENDIDO SOLO EN TRAIN DEL FOLD
    # --------------------------------------------------------

    (
        limites,
        filas_capping,
    ) = aprender_limites_capping(
        train_fold,
        numero_fold,
    )

    train_cap = aplicar_capping(
        train_fold,
        limites,
    )

    eval_cap = aplicar_capping(
        eval_fold,
        limites,
    )

    # --------------------------------------------------------
    # MATRICES
    # --------------------------------------------------------

    X_train = train_cap[
        FEATURES
    ].copy()

    y_train = train_cap[
        TARGET
    ].astype(
        int
    )

    X_eval = eval_cap[
        FEATURES
    ].copy()

    y_eval = eval_cap[
        TARGET
    ].astype(
        int
    )

    # --------------------------------------------------------
    # MODELO
    # --------------------------------------------------------

    modelo = construir_modelo()

    convergence_warning = False
    warning_messages = []

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
    # SCORES
    # --------------------------------------------------------

    score_train = modelo.predict_proba(
        X_train
    )[:, 1]

    score_eval = modelo.predict_proba(
        X_eval
    )[:, 1]

    # --------------------------------------------------------
    # MÉTRICAS
    # --------------------------------------------------------

    metricas_train = calcular_metricas(
        y_train,
        score_train,
    )

    metricas_eval = calcular_metricas(
        y_eval,
        score_eval,
    )

    ranking_eval = calcular_ranking(
        y_eval,
        score_eval,
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

    return {
        "fold":
            numero_fold,

        "train_inicio":
            train_inicio,

        "train_fin":
            train_fin,

        "anio_embargo":
            anio_embargo,

        "anio_evaluacion":
            anio_evaluacion,

        "n_train":
            len(
                train_fold
            ),

        "positivos_train":
            int(
                y_train.sum()
            ),

        "n_eval":
            len(
                eval_fold
            ),

        "positivos_eval":
            int(
                y_eval.sum()
            ),

        "metricas_train":
            metricas_train,

        "metricas_eval":
            metricas_eval,

        "ranking_eval":
            ranking_eval,

        "convergence_warning":
            convergence_warning,

        "warning_messages":
            warning_messages,

        "n_features_transformadas":
            n_features_transformadas,

        "filas_capping":
            filas_capping,
    }


# ============================================================
# BACKTEST COMPLETO
# ============================================================

def ejecutar_backtest(
    train_completo,
):

    filas_metricas = []
    filas_ranking = []
    filas_capping = []

    resultados_folds = []

    print(
        "\n"
        + "=" * 120
    )

    print(
        "BACKTEST TEMPORAL - LR FINANCIAL v10"
    )

    print(
        "=" * 120
    )

    for fold in FOLDS:

        print(
            "\n"
            + "-" * 120
        )

        print(
            f"FOLD {fold['FOLD']}"
        )

        print(
            f"TRAIN: "
            f"{fold['TRAIN_INICIO']}-"
            f"{fold['TRAIN_FIN']}"
        )

        print(
            f"EMBARGO: "
            f"{fold['ANIO_EMBARGO']}"
        )

        print(
            f"EVALUACIÓN: "
            f"{fold['ANIO_EVALUACION']}"
        )

        resultado = ejecutar_fold(
            train_completo,
            fold,
        )

        resultados_folds.append(
            resultado
        )

        metricas_train = resultado[
            "metricas_train"
        ]

        metricas_eval = resultado[
            "metricas_eval"
        ]

        filas_metricas.append(
            {
                "MODELO":
                    "v10_lr_financial",

                "FOLD":
                    resultado[
                        "fold"
                    ],

                "TRAIN_INICIO":
                    resultado[
                        "train_inicio"
                    ],

                "TRAIN_FIN":
                    resultado[
                        "train_fin"
                    ],

                "ANIO_EMBARGO":
                    resultado[
                        "anio_embargo"
                    ],

                "ANIO_EVALUACION":
                    resultado[
                        "anio_evaluacion"
                    ],

                "N_TRAIN":
                    resultado[
                        "n_train"
                    ],

                "POSITIVOS_TRAIN":
                    resultado[
                        "positivos_train"
                    ],

                "N_EVALUACION":
                    resultado[
                        "n_eval"
                    ],

                "POSITIVOS_EVALUACION":
                    resultado[
                        "positivos_eval"
                    ],

                "PR_AUC_TRAIN":
                    metricas_train[
                        "PR_AUC"
                    ],

                "ROC_AUC_TRAIN":
                    metricas_train[
                        "ROC_AUC"
                    ],

                "PR_AUC_EVALUACION":
                    metricas_eval[
                        "PR_AUC"
                    ],

                "ROC_AUC_EVALUACION":
                    metricas_eval[
                        "ROC_AUC"
                    ],

                "GAP_PR_AUC":
                    (
                        metricas_train[
                            "PR_AUC"
                        ]
                        -
                        metricas_eval[
                            "PR_AUC"
                        ]
                    ),

                "N_FEATURES_FISICAS":
                    len(
                        FEATURES
                    ),

                "N_FEATURES_TRANSFORMADAS":
                    resultado[
                        "n_features_transformadas"
                    ],

                "CONVERGENCE_WARNING":
                    resultado[
                        "convergence_warning"
                    ],
            }
        )

        for ranking in resultado[
            "ranking_eval"
        ]:

            filas_ranking.append(
                {
                    "MODELO":
                        "v10_lr_financial",

                    "FOLD":
                        resultado[
                            "fold"
                        ],

                    "ANIO_EVALUACION":
                        resultado[
                            "anio_evaluacion"
                        ],

                    "N_EVALUACION":
                        resultado[
                            "n_eval"
                        ],

                    "POSITIVOS_EVALUACION":
                        resultado[
                            "positivos_eval"
                        ],

                    **ranking,
                }
            )

        filas_capping.extend(
            resultado[
                "filas_capping"
            ]
        )

        print(
            f"TRAIN PR-AUC: "
            f"{metricas_train['PR_AUC']:.9f}"
        )

        print(
            f"EVAL PR-AUC:  "
            f"{metricas_eval['PR_AUC']:.9f}"
        )

        print(
            f"EVAL ROC-AUC: "
            f"{metricas_eval['ROC_AUC']:.9f}"
        )

        for ranking in resultado[
            "ranking_eval"
        ]:

            print(
                f"Top {ranking['K']:>3}: "
                f"{ranking['POSITIVOS_TOP_K']} positivos | "
                f"Lift={ranking['LIFT_AT_K']:.6f}"
            )

        print(
            f"ConvergenceWarning: "
            f"{resultado['convergence_warning']}"
        )

    return (
        pd.DataFrame(
            filas_metricas
        ),
        pd.DataFrame(
            filas_ranking
        ),
        pd.DataFrame(
            filas_capping
        ),
        resultados_folds,
    )


# ============================================================
# RESUMEN
# ============================================================

def construir_resumen(
    metrics_df,
    ranking_df,
):

    pr = metrics_df[
        "PR_AUC_EVALUACION"
    ]

    roc = metrics_df[
        "ROC_AUC_EVALUACION"
    ]

    fila = {
        "MODELO":
            "v10_lr_financial",

        "N_FOLDS":
            len(
                metrics_df
            ),

        "PR_AUC_MEDIA":
            float(
                pr.mean()
            ),

        "PR_AUC_MEDIANA":
            float(
                pr.median()
            ),

        "PR_AUC_STD":
            float(
                pr.std(
                    ddof=1
                )
            ),

        "PR_AUC_MIN":
            float(
                pr.min()
            ),

        "PR_AUC_MAX":
            float(
                pr.max()
            ),

        "ROC_AUC_MEDIA":
            float(
                roc.mean()
            ),

        "ROC_AUC_MEDIANA":
            float(
                roc.median()
            ),

        "GAP_PR_AUC_MEDIO":
            float(
                metrics_df[
                    "GAP_PR_AUC"
                ].mean()
            ),

        "CONVERGENCE_WARNINGS":
            int(
                metrics_df[
                    "CONVERGENCE_WARNING"
                ].sum()
            ),
    }

    for k in K_VALUES:

        bloque = ranking_df[
            ranking_df[
                "K"
            ]
            == k
        ]

        fila[
            f"POSITIVOS_TOP_{k}_TOTAL"
        ] = int(
            bloque[
                "POSITIVOS_TOP_K"
            ].sum()
        )

        fila[
            f"LIFT_AT_{k}_MEDIA"
        ] = float(
            bloque[
                "LIFT_AT_K"
            ].mean()
        )

        fila[
            f"LIFT_AT_{k}_STD"
        ] = float(
            bloque[
                "LIFT_AT_K"
            ].std(
                ddof=1
            )
        )

    return pd.DataFrame(
        [
            fila
        ]
    )


# ============================================================
# METADATA
# ============================================================

def construir_metadata(
    metrics_df,
    ranking_df,
    summary_df,
    resultados_folds,
):

    warnings_por_fold = []

    for resultado in resultados_folds:

        warnings_por_fold.append(
            {
                "fold":
                    resultado[
                        "fold"
                    ],

                "convergence_warning":
                    resultado[
                        "convergence_warning"
                    ],

                "warning_messages":
                    resultado[
                        "warning_messages"
                    ],
            }
        )

    return {
        "experimento":
            "Backtest temporal Regresion Logistica financiera v10",

        "fecha_ejecucion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "dataset":
            ruta_relativa(
                INPUT_PATH
            ),

        "modelo":
            "LogisticRegression",

        "nombre_modelo":
            "v10_lr_financial",

        "baseline_referencia":
            "v10_lr_no_provincia",

        "target":
            TARGET,

        "horizonte_target":
            "24 meses",

        "numero_features_fisicas":
            len(
                FEATURES
            ),

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
            LOGISTIC_PARAMS,

        "backtest": {
            "numero_folds":
                len(
                    FOLDS
                ),

            "folds":
                FOLDS,

            "periodo":
                "2012-2018",

            "tipo":
                "rolling-origin expanding window",

            "embargo":
                "1 año fiscal entre TRAIN y evaluación",
        },

        "capping": {
            "aplicado":
                True,

            "variables":
                FEATURES_FINANCIERAS_NUMERICAS,

            "percentil_inferior":
                CAPPING_LOWER_QUANTILE,

            "percentil_superior":
                CAPPING_UPPER_QUANTILE,

            "regla":
                (
                    "Los limites se aprenden exclusivamente "
                    "desde el TRAIN de cada fold y luego se "
                    "aplican sin recalcular al año de evaluación."
                ),
        },

        "preprocesamiento": {
            "numericas":
                (
                    "Mediana y StandardScaler aprendidos "
                    "exclusivamente desde TRAIN de cada fold."
                ),

            "booleanas":
                (
                    "SimpleImputer most_frequent aprendido "
                    "desde TRAIN de cada fold."
                ),

            "categoricas":
                (
                    "SimpleImputer most_frequent + "
                    "OneHotEncoder(handle_unknown='ignore') "
                    "aprendidos desde TRAIN de cada fold."
                ),
        },

        "class_imbalance":
            "class_weight='balanced'",

        "convergencia":
            warnings_por_fold,

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

        "resultados_por_fold":
            metrics_df.to_dict(
                orient="records"
            ),

        "ranking_por_fold":
            ranking_df.to_dict(
                orient="records"
            ),

        "resumen":
            summary_df.to_dict(
                orient="records"
            ),

        "archivos_salida": {
            "metricas":
                ruta_relativa(
                    METRICS_PATH
                ),

            "ranking":
                ruta_relativa(
                    RANKING_PATH
                ),

            "summary":
                ruta_relativa(
                    SUMMARY_PATH
                ),

            "capping":
                ruta_relativa(
                    CAPPING_PATH
                ),

            "metadata":
                ruta_relativa(
                    METADATA_PATH
                ),
        },

        "entorno": {
            "python":
                sys.version.split()[0],

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


# ============================================================
# MOSTRAR RESUMEN
# ============================================================

def mostrar_resumen(
    metrics_df,
    summary_df,
):

    resumen = summary_df.iloc[
        0
    ]

    print(
        "\n"
        + "=" * 120
    )

    print(
        "RESUMEN BACKTEST - LR FINANCIAL v10"
    )

    print(
        "=" * 120
    )

    print(
        f"\nPR-AUC media:   "
        f"{resumen['PR_AUC_MEDIA']:.9f}"
    )

    print(
        f"PR-AUC mediana: "
        f"{resumen['PR_AUC_MEDIANA']:.9f}"
    )

    print(
        f"PR-AUC std:     "
        f"{resumen['PR_AUC_STD']:.9f}"
    )

    print(
        f"PR-AUC min:     "
        f"{resumen['PR_AUC_MIN']:.9f}"
    )

    print(
        f"PR-AUC max:     "
        f"{resumen['PR_AUC_MAX']:.9f}"
    )

    print(
        f"ROC-AUC media:  "
        f"{resumen['ROC_AUC_MEDIA']:.9f}"
    )

    print(
        "\nPR-AUC por fold:"
    )

    print(
        metrics_df[
            [
                "FOLD",
                "ANIO_EVALUACION",
                "PR_AUC_EVALUACION",
                "ROC_AUC_EVALUACION",
            ]
        ].to_string(
            index=False
        )
    )

    print(
        "\nRanking promedio:"
    )

    for k in K_VALUES:

        print(
            f"Top {k:>3}: "
            f"positivos totales="
            f"{int(resumen[f'POSITIVOS_TOP_{k}_TOTAL'])} | "
            f"Lift medio="
            f"{resumen[f'LIFT_AT_{k}_MEDIA']:.6f}"
        )

    print(
        "\nConvergenceWarnings:"
    )

    print(
        int(
            resumen[
                "CONVERGENCE_WARNINGS"
            ]
        )
    )

    print(
        "\nTEST 2022-2023:"
    )

    print(
        "RESERVADO - NO CARGADO - NO EVALUADO"
    )


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
        "BACKTEST REGRESIÓN LOGÍSTICA FINANCIERA v10"
    )

    print(
        "=" * 120
    )

    print(
        "\nModelo:"
    )

    print(
        "LogisticRegression"
    )

    print(
        "\nConfiguración:"
    )

    print(
        "L2 | C=1.0 | solver=lbfgs | "
        "max_iter=2000 | class_weight=balanced"
    )

    print(
        "\nFeatures:"
    )

    print(
        f"{len(FEATURES)} variables físicas"
    )

    print(
        "\nCapping:"
    )

    print(
        "P01-P99 sobre las 9 features financieras numéricas."
    )

    print(
        "Se aprende nuevamente dentro del TRAIN de cada fold."
    )

    print(
        "\nFolds:"
    )

    for fold in FOLDS:

        print(
            f"Fold {fold['FOLD']}: "
            f"TRAIN "
            f"{fold['TRAIN_INICIO']}-"
            f"{fold['TRAIN_FIN']} | "
            f"Embargo {fold['ANIO_EMBARGO']} | "
            f"Eval {fold['ANIO_EVALUACION']}"
        )

    print(
        "\nTEST 2022-2023:"
    )

    print(
        "RESERVADO - NO SE CARGARÁ"
    )

    # --------------------------------------------------------
    # CARGA
    # --------------------------------------------------------

    train_completo = cargar_train()

    # --------------------------------------------------------
    # VALIDACIÓN
    # --------------------------------------------------------

    validar_universo(
        train_completo
    )

    # --------------------------------------------------------
    # BACKTEST
    # --------------------------------------------------------

    (
        metrics_df,
        ranking_df,
        capping_df,
        resultados_folds,
    ) = ejecutar_backtest(
        train_completo
    )

    # --------------------------------------------------------
    # RESUMEN
    # --------------------------------------------------------

    summary_df = construir_resumen(
        metrics_df,
        ranking_df,
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    metadata = construir_metadata(
        metrics_df,
        ranking_df,
        summary_df,
        resultados_folds,
    )

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics_df.to_csv(
        METRICS_PATH,
        index=False,
    )

    ranking_df.to_csv(
        RANKING_PATH,
        index=False,
    )

    summary_df.to_csv(
        SUMMARY_PATH,
        index=False,
    )

    capping_df.to_csv(
        CAPPING_PATH,
        index=False,
    )

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
    # MOSTRAR
    # --------------------------------------------------------

    mostrar_resumen(
        metrics_df,
        summary_df,
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
        SUMMARY_PATH
    )

    print(
        CAPPING_PATH
    )

    print(
        METADATA_PATH
    )

    print(
        "\nBacktest finalizado correctamente."
    )


if __name__ == "__main__":
    main()