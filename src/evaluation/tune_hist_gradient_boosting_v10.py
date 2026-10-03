from pathlib import Path
from datetime import datetime, timezone
import json
import platform
import sys

import numpy as np
import pandas as pd
import sklearn

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
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


VALIDATION_RESULTS_PATH = (
    OUTPUT_DIR
    / "tune_hgb_financial_v10_validation.csv"
)

BACKTEST_METRICS_PATH = (
    OUTPUT_DIR
    / "tune_hgb_financial_v10_backtest_metrics.csv"
)

BACKTEST_RANKING_PATH = (
    OUTPUT_DIR
    / "tune_hgb_financial_v10_backtest_ranking_metrics.csv"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "tune_hgb_financial_v10_summary.csv"
)

METADATA_PATH = (
    OUTPUT_DIR
    / "tune_hgb_financial_v10_metadata.json"
)


TARGET = "TARGET_24M"

RANDOM_STATE = 42

CHUNK_SIZE = 150_000

K_VALUES = [
    50,
    100,
    200,
]


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
# CONFIGURACIONES CONTROLADAS
# ============================================================

#
# El objetivo NO es hacer un GridSearch exhaustivo.
#
# Se evalúan cuatro configuraciones justificadas:
#
# C0_BASELINE
#   Configuración exacta utilizada en HGB_FINANCIAL.
#
# C1_REGULARIZED
#   Reduce complejidad del árbol y aumenta regularización.
#
# C2_SLOW_LEARNING
#   Reduce learning_rate y aumenta número de iteraciones.
#
# C3_CONSERVATIVE
#   Combina menor profundidad, hojas mayores y mayor L2.
#
# TEST 2022-2023 permanece completamente fuera del proceso.
#

CONFIGURACIONES = [
    {
        "CONFIG_ID":
            "C0_BASELINE",

        "DESCRIPCION":
            "Configuracion HGB financial v10 actual",

        "PARAMS": {
            "loss":
                "log_loss",

            "learning_rate":
                0.05,

            "max_iter":
                150,

            "max_leaf_nodes":
                7,

            "max_depth":
                3,

            "min_samples_leaf":
                100,

            "l2_regularization":
                1.0,

            "early_stopping":
                False,

            "random_state":
                RANDOM_STATE,

            "class_weight":
                "balanced",

            "categorical_features":
                "from_dtype",
        },
    },

    {
        "CONFIG_ID":
            "C1_REGULARIZED",

        "DESCRIPCION":
            "Mayor regularizacion y menor complejidad",

        "PARAMS": {
            "loss":
                "log_loss",

            "learning_rate":
                0.05,

            "max_iter":
                150,

            "max_leaf_nodes":
                5,

            "max_depth":
                2,

            "min_samples_leaf":
                150,

            "l2_regularization":
                2.0,

            "early_stopping":
                False,

            "random_state":
                RANDOM_STATE,

            "class_weight":
                "balanced",

            "categorical_features":
                "from_dtype",
        },
    },

    {
        "CONFIG_ID":
            "C2_SLOW_LEARNING",

        "DESCRIPCION":
            "Menor learning rate con mas iteraciones",

        "PARAMS": {
            "loss":
                "log_loss",

            "learning_rate":
                0.03,

            "max_iter":
                250,

            "max_leaf_nodes":
                7,

            "max_depth":
                3,

            "min_samples_leaf":
                150,

            "l2_regularization":
                2.0,

            "early_stopping":
                False,

            "random_state":
                RANDOM_STATE,

            "class_weight":
                "balanced",

            "categorical_features":
                "from_dtype",
        },
    },

    {
        "CONFIG_ID":
            "C3_CONSERVATIVE",

        "DESCRIPCION":
            "Configuracion conservadora con mayor regularizacion",

        "PARAMS": {
            "loss":
                "log_loss",

            "learning_rate":
                0.03,

            "max_iter":
                250,

            "max_leaf_nodes":
                5,

            "max_depth":
                2,

            "min_samples_leaf":
                200,

            "l2_regularization":
                3.0,

            "early_stopping":
                False,

            "random_state":
                RANDOM_STATE,

            "class_weight":
                "balanced",

            "categorical_features":
                "from_dtype",
        },
    },
]


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

EXPECTED_VALIDATION_ROWS = 98_471
EXPECTED_VALIDATION_POSITIVES = 34


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

    resultado_texto = texto.map(
        mapa
    )

    resultado_numerico = pd.to_numeric(
        serie,
        errors="coerce",
    )

    resultado_numerico = resultado_numerico.where(
        resultado_numerico.isin(
            [
                0,
                1,
            ]
        )
    )

    resultado = resultado_texto.fillna(
        resultado_numerico
    )

    return resultado.astype(
        "float64"
    )


# ============================================================
# PREPARACIÓN DE DATOS
# ============================================================

def preparar_datos(
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
            "Existen valores ANIO invalidos."
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
            "Existen valores TARGET_24M invalidos."
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
            "TARGET_24M contiene valores distintos de 0 y 1."
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

        df[
            variable
        ] = df[
            variable
        ].astype(
            "string"
        )

    return df


# ============================================================
# CARGA DEL DATASET
# ============================================================

def cargar_dataset():

    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"No existe el dataset:\n{INPUT_PATH}"
        )

    encabezado = pd.read_csv(
        INPUT_PATH,
        nrows=0,
    )

    columnas_disponibles = set(
        encabezado.columns
    )

    faltantes = [
        columna
        for columna in COLUMNAS_LECTURA
        if columna not in columnas_disponibles
    ]

    if faltantes:

        raise ValueError(
            "Faltan columnas requeridas:\n"
            + "\n".join(
                faltantes
            )
        )

    print(
        "\nCargando dataset financiero v10..."
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

        #
        # TEST y embargos no se cargan.
        #

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
            ] = split_normalizado.loc[
                mascara
            ]

            partes.append(
                bloque
            )

    if not partes:

        raise ValueError(
            "No se encontraron observaciones TRAIN/VALIDATION."
        )

    dataframe = pd.concat(
        partes,
        ignore_index=True,
    )

    return preparar_datos(
        dataframe
    )


# ============================================================
# VALIDACIÓN DEL UNIVERSO
# ============================================================

def validar_universo(
    train,
    validation,
):

    print(
        "\nValidando universo congelado..."
    )

    train_rows = len(
        train
    )

    train_positives = int(
        train[
            TARGET
        ].sum()
    )

    validation_rows = len(
        validation
    )

    validation_positives = int(
        validation[
            TARGET
        ].sum()
    )

    print(
        f"TRAIN:      "
        f"{train_rows:,} filas | "
        f"{train_positives} positivos"
    )

    print(
        f"VALIDATION: "
        f"{validation_rows:,} filas | "
        f"{validation_positives} positivos"
    )

    if train_rows != EXPECTED_TRAIN_ROWS:

        raise ValueError(
            "Filas TRAIN distintas al universo congelado."
        )

    if train_positives != EXPECTED_TRAIN_POSITIVES:

        raise ValueError(
            "Positivos TRAIN distintos al universo congelado."
        )

    if validation_rows != EXPECTED_VALIDATION_ROWS:

        raise ValueError(
            "Filas VALIDATION distintas al universo congelado."
        )

    if validation_positives != EXPECTED_VALIDATION_POSITIVES:

        raise ValueError(
            "Positivos VALIDATION distintos al universo congelado."
        )


def validar_universo_anual(
    train,
):

    print(
        "\nValidando universo anual TRAIN..."
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

        filas = len(
            subset
        )

        positivos = int(
            subset[
                TARGET
            ].sum()
        )

        esperado = EXPECTED_YEAR_COUNTS[
            anio
        ]

        print(
            f"{anio}: "
            f"{filas:,} filas | "
            f"{positivos} positivos"
        )

        if filas != esperado[
            "filas"
        ]:

            raise ValueError(
                f"Año {anio}: filas incorrectas."
            )

        if positivos != esperado[
            "positivos"
        ]:

            raise ValueError(
                f"Año {anio}: positivos incorrectos."
            )


# ============================================================
# CATEGORÍA NATIVA TRAIN-ONLY
# ============================================================

def preparar_categorias(
    train,
    evaluacion,
):

    train = train.copy()
    evaluacion = evaluacion.copy()

    metadata = {}

    for variable in FEATURES_CATEGORICAS:

        categorias_train = (
            train[
                variable
            ]
            .dropna()
            .astype(
                str
            )
            .unique()
            .tolist()
        )

        categorias_train = sorted(
            categorias_train
        )

        if len(
            categorias_train
        ) > 255:

            raise ValueError(
                f"{variable} supera 255 categorias."
            )

        desconocidas = (
            evaluacion[
                variable
            ].notna()
            &
            ~evaluacion[
                variable
            ]
            .astype(
                str
            )
            .isin(
                categorias_train
            )
        )

        dtype_categorico = pd.CategoricalDtype(
            categories=categorias_train
        )

        train[
            variable
        ] = train[
            variable
        ].astype(
            dtype_categorico
        )

        evaluacion[
            variable
        ] = evaluacion[
            variable
        ].astype(
            dtype_categorico
        )

        metadata[
            variable
        ] = {
            "numero_categorias_train":
                len(
                    categorias_train
                ),

            "categorias_desconocidas_evaluacion":
                int(
                    desconocidas.sum()
                ),
        }

    return (
        train,
        evaluacion,
        metadata,
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
# ENTRENAR Y EVALUAR UNA CONFIGURACIÓN
# ============================================================

def entrenar_evaluar(
    train,
    evaluacion,
    params,
):

    train_cat, eval_cat, categorias = preparar_categorias(
        train,
        evaluacion,
    )

    X_train = train_cat[
        FEATURES
    ].copy()

    y_train = train_cat[
        TARGET
    ].astype(
        int
    )

    X_eval = eval_cat[
        FEATURES
    ].copy()

    y_eval = eval_cat[
        TARGET
    ].astype(
        int
    )

    modelo = HistGradientBoostingClassifier(
        **params
    )

    modelo.fit(
        X_train,
        y_train,
    )

    scores_train = modelo.predict_proba(
        X_train
    )[:, 1]

    scores_eval = modelo.predict_proba(
        X_eval
    )[:, 1]

    metricas_train = calcular_metricas(
        y_train,
        scores_train,
    )

    metricas_eval = calcular_metricas(
        y_eval,
        scores_eval,
    )

    ranking = calcular_ranking(
        y_eval,
        scores_eval,
    )

    return {
        "modelo":
            modelo,

        "metricas_train":
            metricas_train,

        "metricas_eval":
            metricas_eval,

        "ranking":
            ranking,

        "categorias":
            categorias,

        "n_train":
            len(
                train_cat
            ),

        "positivos_train":
            int(
                y_train.sum()
            ),

        "n_eval":
            len(
                eval_cat
            ),

        "positivos_eval":
            int(
                y_eval.sum()
            ),
    }


# ============================================================
# VALIDATION 2020
# ============================================================

def evaluar_validation(
    train,
    validation,
):

    resultados = []

    print(
        "\n"
        + "=" * 120
    )

    print(
        "TUNING CONTROLADO - VALIDATION 2020"
    )

    print(
        "=" * 120
    )

    for config in CONFIGURACIONES:

        config_id = config[
            "CONFIG_ID"
        ]

        descripcion = config[
            "DESCRIPCION"
        ]

        params = config[
            "PARAMS"
        ]

        print(
            "\n"
            + "-" * 120
        )

        print(
            config_id
        )

        print(
            descripcion
        )

        resultado = entrenar_evaluar(
            train,
            validation,
            params,
        )

        metricas_train = resultado[
            "metricas_train"
        ]

        metricas_validation = resultado[
            "metricas_eval"
        ]

        fila = {
            "CONFIG_ID":
                config_id,

            "DESCRIPCION":
                descripcion,

            "N_FEATURES":
                len(
                    FEATURES
                ),

            "TRAIN_PR_AUC":
                metricas_train[
                    "PR_AUC"
                ],

            "TRAIN_ROC_AUC":
                metricas_train[
                    "ROC_AUC"
                ],

            "VALIDATION_PR_AUC":
                metricas_validation[
                    "PR_AUC"
                ],

            "VALIDATION_ROC_AUC":
                metricas_validation[
                    "ROC_AUC"
                ],

            "GAP_PR_AUC":
                (
                    metricas_train[
                        "PR_AUC"
                    ]
                    - metricas_validation[
                        "PR_AUC"
                    ]
                ),

            "N_ITER":
                int(
                    resultado[
                        "modelo"
                    ].n_iter_
                ),
        }

        for ranking in resultado[
            "ranking"
        ]:

            k = ranking[
                "K"
            ]

            fila[
                f"POSITIVOS_TOP_{k}"
            ] = ranking[
                "POSITIVOS_TOP_K"
            ]

            fila[
                f"PRECISION_AT_{k}"
            ] = ranking[
                "PRECISION_AT_K"
            ]

            fila[
                f"RECALL_AT_{k}"
            ] = ranking[
                "RECALL_AT_K"
            ]

            fila[
                f"LIFT_AT_{k}"
            ] = ranking[
                "LIFT_AT_K"
            ]

        resultados.append(
            fila
        )

        print(
            f"TRAIN PR-AUC:      "
            f"{metricas_train['PR_AUC']:.9f}"
        )

        print(
            f"VALIDATION PR-AUC: "
            f"{metricas_validation['PR_AUC']:.9f}"
        )

        print(
            f"VALIDATION ROC:    "
            f"{metricas_validation['ROC_AUC']:.9f}"
        )

        for ranking in resultado[
            "ranking"
        ]:

            print(
                f"Top {ranking['K']:>3}: "
                f"{ranking['POSITIVOS_TOP_K']} positivos | "
                f"Lift={ranking['LIFT_AT_K']:.6f}"
            )

    return pd.DataFrame(
        resultados
    )


# ============================================================
# BACKTEST TEMPORAL
# ============================================================

def ejecutar_backtest(
    train_completo,
):

    metricas_resultados = []
    ranking_resultados = []

    print(
        "\n"
        + "=" * 120
    )

    print(
        "BACKTEST TEMPORAL DEL TUNING CONTROLADO"
    )

    print(
        "=" * 120
    )

    for config in CONFIGURACIONES:

        config_id = config[
            "CONFIG_ID"
        ]

        descripcion = config[
            "DESCRIPCION"
        ]

        params = config[
            "PARAMS"
        ]

        print(
            "\n"
            + "#" * 120
        )

        print(
            config_id
        )

        print(
            descripcion
        )

        print(
            "#" * 120
        )

        for fold in FOLDS:

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
                    f"{config_id} fold {numero_fold}: "
                    f"TRAIN vacio."
                )

            if eval_fold.empty:

                raise ValueError(
                    f"{config_id} fold {numero_fold}: "
                    f"EVAL vacio."
                )

            if (
                anio_embargo
                in train_fold[
                    "ANIO"
                ].unique()
            ):

                raise ValueError(
                    f"{config_id} fold {numero_fold}: "
                    f"embargo presente en TRAIN."
                )

            resultado = entrenar_evaluar(
                train_fold,
                eval_fold,
                params,
            )

            metricas_train = resultado[
                "metricas_train"
            ]

            metricas_eval = resultado[
                "metricas_eval"
            ]

            metricas_resultados.append(
                {
                    "CONFIG_ID":
                        config_id,

                    "DESCRIPCION":
                        descripcion,

                    "FOLD":
                        numero_fold,

                    "TRAIN_INICIO":
                        train_inicio,

                    "TRAIN_FIN":
                        train_fin,

                    "ANIO_EMBARGO":
                        anio_embargo,

                    "ANIO_EVALUACION":
                        anio_evaluacion,

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
                            - metricas_eval[
                                "PR_AUC"
                            ]
                        ),

                    "N_ITER":
                        int(
                            resultado[
                                "modelo"
                            ].n_iter_
                        ),
                }
            )

            for ranking in resultado[
                "ranking"
            ]:

                ranking_resultados.append(
                    {
                        "CONFIG_ID":
                            config_id,

                        "DESCRIPCION":
                            descripcion,

                        "FOLD":
                            numero_fold,

                        "ANIO_EVALUACION":
                            anio_evaluacion,

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

            print(
                f"Fold {numero_fold} | "
                f"Eval {anio_evaluacion} | "
                f"PR-AUC="
                f"{metricas_eval['PR_AUC']:.9f} | "
                f"ROC="
                f"{metricas_eval['ROC_AUC']:.9f}"
            )

    return (
        pd.DataFrame(
            metricas_resultados
        ),
        pd.DataFrame(
            ranking_resultados
        ),
    )


# ============================================================
# RESUMEN
# ============================================================

def construir_resumen(
    validation_df,
    backtest_metrics_df,
    backtest_ranking_df,
):

    filas = []

    for config in CONFIGURACIONES:

        config_id = config[
            "CONFIG_ID"
        ]

        descripcion = config[
            "DESCRIPCION"
        ]

        validation = validation_df[
            validation_df[
                "CONFIG_ID"
            ]
            == config_id
        ].iloc[
            0
        ]

        metricas = backtest_metrics_df[
            backtest_metrics_df[
                "CONFIG_ID"
            ]
            == config_id
        ].copy()

        ranking = backtest_ranking_df[
            backtest_ranking_df[
                "CONFIG_ID"
            ]
            == config_id
        ].copy()

        pr_auc = metricas[
            "PR_AUC_EVALUACION"
        ]

        roc_auc = metricas[
            "ROC_AUC_EVALUACION"
        ]

        fila = {
            "CONFIG_ID":
                config_id,

            "DESCRIPCION":
                descripcion,

            "N_FEATURES":
                len(
                    FEATURES
                ),

            "VALIDATION_PR_AUC":
                float(
                    validation[
                        "VALIDATION_PR_AUC"
                    ]
                ),

            "VALIDATION_ROC_AUC":
                float(
                    validation[
                        "VALIDATION_ROC_AUC"
                    ]
                ),

            "VALIDATION_GAP_PR_AUC":
                float(
                    validation[
                        "GAP_PR_AUC"
                    ]
                ),

            "VALIDATION_POSITIVOS_TOP_50":
                int(
                    validation[
                        "POSITIVOS_TOP_50"
                    ]
                ),

            "VALIDATION_POSITIVOS_TOP_100":
                int(
                    validation[
                        "POSITIVOS_TOP_100"
                    ]
                ),

            "VALIDATION_POSITIVOS_TOP_200":
                int(
                    validation[
                        "POSITIVOS_TOP_200"
                    ]
                ),

            "BACKTEST_PR_AUC_MEDIA":
                float(
                    pr_auc.mean()
                ),

            "BACKTEST_PR_AUC_MEDIANA":
                float(
                    pr_auc.median()
                ),

            "BACKTEST_PR_AUC_STD":
                float(
                    pr_auc.std(
                        ddof=1
                    )
                ),

            "BACKTEST_PR_AUC_MIN":
                float(
                    pr_auc.min()
                ),

            "BACKTEST_PR_AUC_MAX":
                float(
                    pr_auc.max()
                ),

            "BACKTEST_ROC_AUC_MEDIA":
                float(
                    roc_auc.mean()
                ),

            "BACKTEST_GAP_PR_AUC_MEDIO":
                float(
                    metricas[
                        "GAP_PR_AUC"
                    ].mean()
                ),
        }

        for k in K_VALUES:

            bloque = ranking[
                ranking[
                    "K"
                ]
                == k
            ]

            fila[
                f"BACKTEST_POSITIVOS_TOP_{k}_TOTAL"
            ] = int(
                bloque[
                    "POSITIVOS_TOP_K"
                ].sum()
            )

            fila[
                f"BACKTEST_LIFT_AT_{k}_MEDIA"
            ] = float(
                bloque[
                    "LIFT_AT_K"
                ].mean()
            )

            fila[
                f"BACKTEST_LIFT_AT_{k}_STD"
            ] = float(
                bloque[
                    "LIFT_AT_K"
                ].std(
                    ddof=1
                )
            )

        filas.append(
            fila
        )

    return pd.DataFrame(
        filas
    )


# ============================================================
# METADATA
# ============================================================

def construir_metadata(
    resumen_df,
):

    configuraciones_metadata = []

    for config in CONFIGURACIONES:

        configuraciones_metadata.append(
            {
                "config_id":
                    config[
                        "CONFIG_ID"
                    ],

                "descripcion":
                    config[
                        "DESCRIPCION"
                    ],

                "parametros":
                    config[
                        "PARAMS"
                    ],
            }
        )

    return {
        "experimento":
            "Tuning controlado HGB financial v10",

        "fecha_ejecucion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "objetivo":
            (
                "Evaluar un conjunto reducido de configuraciones "
                "HGB sobre el conjunto core mas features "
                "financieras, sin utilizar TEST."
            ),

        "dataset":
            ruta_relativa(
                INPUT_PATH
            ),

        "target":
            TARGET,

        "horizonte_target":
            "24 meses",

        "numero_features":
            len(
                FEATURES
            ),

        "features_core_numericas":
            FEATURES_NUMERICAS_CORE,

        "features_financieras_numericas":
            FEATURES_FINANCIERAS_NUMERICAS,

        "features_booleanas":
            FEATURES_BOOLEANAS,

        "features_categoricas":
            FEATURES_CATEGORICAS,

        "features_totales":
            FEATURES,

        "numero_configuraciones":
            len(
                CONFIGURACIONES
            ),

        "busqueda_exhaustiva":
            False,

        "configuraciones":
            configuraciones_metadata,

        "validation": {
            "anio":
                2020,

            "utilizada":
                True,

            "rol":
                "desarrollo y comparacion controlada",
        },

        "backtesting": {
            "periodo":
                "2012-2018",

            "numero_folds":
                4,

            "embargo":
                "1 año fiscal entre TRAIN y evaluacion",
        },

        "tratamiento_financieras": {
            "capping":
                False,

            "winsorizacion":
                False,

            "imputacion_externa":
                False,

            "manejo_missing":
                (
                    "Tratamiento nativo de "
                    "HistGradientBoostingClassifier."
                ),
        },

        "categorica": {
            "variable":
                "tipo_compania",

            "tratamiento":
                (
                    "Categoria nativa con categorias "
                    "aprendidas exclusivamente desde TRAIN "
                    "de cada evaluacion."
                ),
        },

        "provincia_utilizada":
            False,

        "seleccion_automatica":
            False,

        "test": {
            "periodo":
                "2022-2023",

            "cargado":
                False,

            "evaluado":
                False,

            "estado":
                "RESERVADO",
        },

        "nota_seleccion":
            (
                "La comparacion no declara automaticamente "
                "un modelo final. Debe revisarse PR-AUC, "
                "estabilidad temporal, ranking y brecha "
                "TRAIN-evaluacion antes de seleccionar."
            ),

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

        "archivos_salida": {
            "validation":
                ruta_relativa(
                    VALIDATION_RESULTS_PATH
                ),

            "backtest_metricas":
                ruta_relativa(
                    BACKTEST_METRICS_PATH
                ),

            "backtest_ranking":
                ruta_relativa(
                    BACKTEST_RANKING_PATH
                ),

            "resumen":
                ruta_relativa(
                    SUMMARY_PATH
                ),

            "metadata":
                ruta_relativa(
                    METADATA_PATH
                ),
        },

        "resultados_resumen":
            resumen_df.to_dict(
                orient="records"
            ),
    }


# ============================================================
# MOSTRAR RESUMEN
# ============================================================

def mostrar_resumen(
    resumen_df,
    backtest_metrics_df,
):

    print(
        "\n"
        + "=" * 125
    )

    print(
        "RESUMEN TUNING HGB FINANCIAL v10"
    )

    print(
        "=" * 125
    )

    columnas = [
        "CONFIG_ID",
        "VALIDATION_PR_AUC",
        "VALIDATION_ROC_AUC",
        "VALIDATION_POSITIVOS_TOP_50",
        "VALIDATION_POSITIVOS_TOP_100",
        "VALIDATION_POSITIVOS_TOP_200",
        "BACKTEST_PR_AUC_MEDIA",
        "BACKTEST_PR_AUC_MEDIANA",
        "BACKTEST_PR_AUC_STD",
        "BACKTEST_LIFT_AT_50_MEDIA",
        "BACKTEST_LIFT_AT_100_MEDIA",
        "BACKTEST_LIFT_AT_200_MEDIA",
    ]

    print(
        resumen_df[
            columnas
        ].to_string(
            index=False
        )
    )

    print(
        "\nPR-AUC por fold:"
    )

    tabla_folds = backtest_metrics_df.pivot(
        index=[
            "FOLD",
            "ANIO_EVALUACION",
        ],
        columns="CONFIG_ID",
        values="PR_AUC_EVALUACION",
    ).reset_index()

    print(
        tabla_folds.to_string(
            index=False
        )
    )

    print(
        "\nSelección automática:"
    )

    print(
        "NO REALIZADA"
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
        + "=" * 125
    )

    print(
        "PROSPECT FINDER BVQ"
    )

    print(
        "TUNING CONTROLADO HGB FINANCIAL v10"
    )

    print(
        "=" * 125
    )

    print(
        "\nDataset:"
    )

    print(
        INPUT_PATH
    )

    print(
        "\nFeatures:"
    )

    print(
        f"{len(FEATURES)} variables físicas"
    )

    print(
        "\nConfiguraciones:"
    )

    for config in CONFIGURACIONES:

        print(
            f"- {config['CONFIG_ID']}: "
            f"{config['DESCRIPCION']}"
        )

    print(
        "\nVALIDATION:"
    )

    print(
        "2020"
    )

    print(
        "\nBACKTEST:"
    )

    print(
        "4 folds temporales con embargo anual"
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

    dataframe = cargar_dataset()

    train = dataframe[
        dataframe[
            "SPLIT"
        ]
        == "TRAIN"
    ].copy()

    validation = dataframe[
        dataframe[
            "SPLIT"
        ]
        == "VALIDATION"
    ].copy()

    # --------------------------------------------------------
    # VALIDACIONES
    # --------------------------------------------------------

    validar_universo(
        train,
        validation,
    )

    validar_universo_anual(
        train
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    validation_df = evaluar_validation(
        train,
        validation,
    )

    # --------------------------------------------------------
    # BACKTEST
    # --------------------------------------------------------

    (
        backtest_metrics_df,
        backtest_ranking_df,
    ) = ejecutar_backtest(
        train
    )

    # --------------------------------------------------------
    # RESUMEN
    # --------------------------------------------------------

    resumen_df = construir_resumen(
        validation_df,
        backtest_metrics_df,
        backtest_ranking_df,
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    metadata = construir_metadata(
        resumen_df
    )

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    validation_df.to_csv(
        VALIDATION_RESULTS_PATH,
        index=False,
    )

    backtest_metrics_df.to_csv(
        BACKTEST_METRICS_PATH,
        index=False,
    )

    backtest_ranking_df.to_csv(
        BACKTEST_RANKING_PATH,
        index=False,
    )

    resumen_df.to_csv(
        SUMMARY_PATH,
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
        resumen_df,
        backtest_metrics_df,
    )

    print(
        "\nArchivos generados:"
    )

    print(
        VALIDATION_RESULTS_PATH
    )

    print(
        BACKTEST_METRICS_PATH
    )

    print(
        BACKTEST_RANKING_PATH
    )

    print(
        SUMMARY_PATH
    )

    print(
        METADATA_PATH
    )

    print(
        "\nTuning controlado finalizado correctamente."
    )


if __name__ == "__main__":
    main()