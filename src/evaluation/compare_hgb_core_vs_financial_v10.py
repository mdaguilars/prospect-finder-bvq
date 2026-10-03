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


VALIDATION_OUTPUT_PATH = (
    OUTPUT_DIR
    / "comparison_hgb_core_vs_financial_v10_validation.csv"
)

BACKTEST_OUTPUT_PATH = (
    OUTPUT_DIR
    / "comparison_hgb_core_vs_financial_v10_backtest_metrics.csv"
)

RANKING_OUTPUT_PATH = (
    OUTPUT_DIR
    / "comparison_hgb_core_vs_financial_v10_ranking_metrics.csv"
)

SUMMARY_OUTPUT_PATH = (
    OUTPUT_DIR
    / "comparison_hgb_core_vs_financial_v10_summary.csv"
)

METADATA_OUTPUT_PATH = (
    OUTPUT_DIR
    / "comparison_hgb_core_vs_financial_v10_metadata.json"
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


FEATURES_CORE = (
    FEATURES_NUMERICAS_CORE
    + FEATURES_BOOLEANAS_CORE
    + FEATURES_CATEGORICAS
)


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


FEATURES_FINANCIERAS = (
    FEATURES_FINANCIERAS_NUMERICAS
    + FEATURES_FINANCIERAS_BOOLEANAS
)


FEATURES_EXTENDIDAS = (
    FEATURES_CORE
    + FEATURES_FINANCIERAS
)


# ============================================================
# ESCENARIOS
# ============================================================

ESCENARIOS = [
    {
        "MODELO":
            "HGB_CORE",

        "DESCRIPCION":
            "HGB con conjunto core v10",

        "FEATURES":
            FEATURES_CORE,

        "NUMERICAS":
            FEATURES_NUMERICAS_CORE,

        "BOOLEANAS":
            FEATURES_BOOLEANAS_CORE,
    },

    {
        "MODELO":
            "HGB_FINANCIAL",

        "DESCRIPCION":
            "HGB core v10 mas 10 features financieras",

        "FEATURES":
            FEATURES_EXTENDIDAS,

        "NUMERICAS":
            (
                FEATURES_NUMERICAS_CORE
                + FEATURES_FINANCIERAS_NUMERICAS
            ),

        "BOOLEANAS":
            (
                FEATURES_BOOLEANAS_CORE
                + FEATURES_FINANCIERAS_BOOLEANAS
            ),
    },
]


# ============================================================
# HIPERPARÁMETROS HGB
# ============================================================

#
# IMPORTANTE:
#
# Se utiliza exactamente la configuración HGB v10 existente.
#
# No existe tuning en este experimento.
# El objetivo es aislar exclusivamente el efecto de las
# nuevas variables financieras.
#

HGB_PARAMS = {
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
# COLUMNAS A LEER
# ============================================================

COLUMNAS_LECTURA = list(
    dict.fromkeys(
        [
            "ANIO",
            "SPLIT",
            TARGET,
        ]
        + FEATURES_EXTENDIDAS
    )
)


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

    convertido_texto = texto.map(
        mapa
    )

    convertido_numerico = pd.to_numeric(
        serie,
        errors="coerce",
    )

    convertido_numerico = convertido_numerico.where(
        convertido_numerico.isin(
            [
                0,
                1,
            ]
        )
    )

    resultado = convertido_texto.fillna(
        convertido_numerico
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

    todas_numericas = list(
        dict.fromkeys(
            FEATURES_NUMERICAS_CORE
            + FEATURES_FINANCIERAS_NUMERICAS
        )
    )

    for variable in todas_numericas:

        df[
            variable
        ] = pd.to_numeric(
            df[
                variable
            ],
            errors="coerce",
        )

    df[
        todas_numericas
    ] = df[
        todas_numericas
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

    todas_booleanas = list(
        dict.fromkeys(
            FEATURES_BOOLEANAS_CORE
            + FEATURES_FINANCIERAS_BOOLEANAS
        )
    )

    for variable in todas_booleanas:

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
        "\nCargando capa financiera v10..."
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
        # Se cargan únicamente TRAIN y VALIDATION.
        #
        # TEST no se incorpora al dataframe del experimento.
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
            "No se encontraron observaciones "
            "TRAIN o VALIDATION."
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
        "\nValidando universo..."
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
            "Número de filas TRAIN incorrecto."
        )

    if train_positives != EXPECTED_TRAIN_POSITIVES:

        raise ValueError(
            "Número de positivos TRAIN incorrecto."
        )

    if validation_rows != EXPECTED_VALIDATION_ROWS:

        raise ValueError(
            "Número de filas VALIDATION incorrecto."
        )

    if (
        validation_positives
        != EXPECTED_VALIDATION_POSITIVES
    ):

        raise ValueError(
            "Número de positivos VALIDATION incorrecto."
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

def preparar_categoria(
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
                f"{variable} supera 255 categorías."
            )

        mascara_desconocidas = (
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

        dtype_categoria = pd.CategoricalDtype(
            categories=categorias_train
        )

        train[
            variable
        ] = train[
            variable
        ].astype(
            dtype_categoria
        )

        evaluacion[
            variable
        ] = evaluacion[
            variable
        ].astype(
            dtype_categoria
        )

        metadata[
            variable
        ] = {
            "numero_categorias_train":
                len(
                    categorias_train
                ),

            "desconocidas_evaluacion":
                int(
                    mascara_desconocidas.sum()
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

    ranking = pd.DataFrame(
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

    ranking = ranking.sort_values(
        "SCORE",
        ascending=False,
        kind="mergesort",
    ).reset_index(
        drop=True
    )

    positivos_totales = int(
        ranking[
            "TARGET"
        ].sum()
    )

    prevalencia = (
        positivos_totales
        / len(
            ranking
        )
    )

    resultados = []

    for k in K_VALUES:

        top = ranking.head(
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
# ENTRENAR UN ESCENARIO
# ============================================================

def entrenar_evaluar(
    train,
    evaluacion,
    features,
):

    train_preparado, eval_preparado, categorias = (
        preparar_categoria(
            train,
            evaluacion,
        )
    )

    X_train = train_preparado[
        features
    ].copy()

    y_train = train_preparado[
        TARGET
    ].astype(
        int
    )

    X_eval = eval_preparado[
        features
    ].copy()

    y_eval = eval_preparado[
        TARGET
    ].astype(
        int
    )

    modelo = HistGradientBoostingClassifier(
        **HGB_PARAMS
    )

    modelo.fit(
        X_train,
        y_train,
    )

    score_train = modelo.predict_proba(
        X_train
    )[:, 1]

    score_eval = modelo.predict_proba(
        X_eval
    )[:, 1]

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

    return {
        "modelo":
            modelo,

        "metricas_train":
            metricas_train,

        "metricas_eval":
            metricas_eval,

        "ranking_eval":
            ranking_eval,

        "categorias":
            categorias,

        "n_train":
            len(
                train_preparado
            ),

        "positivos_train":
            int(
                y_train.sum()
            ),

        "n_eval":
            len(
                eval_preparado
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

    filas = []

    print(
        "\n"
        + "=" * 110
    )

    print(
        "COMPARACIÓN EN VALIDATION 2020"
    )

    print(
        "=" * 110
    )

    for escenario in ESCENARIOS:

        nombre = escenario[
            "MODELO"
        ]

        descripcion = escenario[
            "DESCRIPCION"
        ]

        features = escenario[
            "FEATURES"
        ]

        print(
            "\n"
            + "-" * 110
        )

        print(
            nombre
        )

        print(
            descripcion
        )

        print(
            f"Features físicas: "
            f"{len(features)}"
        )

        resultado = entrenar_evaluar(
            train,
            validation,
            features,
        )

        metricas_train = resultado[
            "metricas_train"
        ]

        metricas_eval = resultado[
            "metricas_eval"
        ]

        fila = {
            "MODELO":
                nombre,

            "DESCRIPCION":
                descripcion,

            "N_FEATURES":
                len(
                    features
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
                metricas_eval[
                    "PR_AUC"
                ],

            "VALIDATION_ROC_AUC":
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

        for ranking in resultado[
            "ranking_eval"
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

        filas.append(
            fila
        )

        print(
            f"TRAIN PR-AUC:      "
            f"{metricas_train['PR_AUC']:.9f}"
        )

        print(
            f"VALIDATION PR-AUC: "
            f"{metricas_eval['PR_AUC']:.9f}"
        )

        print(
            f"VALIDATION ROC:    "
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

    return pd.DataFrame(
        filas
    )


# ============================================================
# BACKTEST TEMPORAL
# ============================================================

def ejecutar_backtest(
    train_completo,
):

    filas_metricas = []
    filas_ranking = []

    print(
        "\n"
        + "=" * 110
    )

    print(
        "BACKTEST TEMPORAL CORE VS FINANCIAL"
    )

    print(
        "=" * 110
    )

    for escenario in ESCENARIOS:

        nombre = escenario[
            "MODELO"
        ]

        descripcion = escenario[
            "DESCRIPCION"
        ]

        features = escenario[
            "FEATURES"
        ]

        print(
            "\n"
            + "#" * 110
        )

        print(
            nombre
        )

        print(
            descripcion
        )

        print(
            f"Features físicas: "
            f"{len(features)}"
        )

        print(
            "#" * 110
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
                    f"{nombre} fold {numero_fold}: "
                    f"TRAIN vacío."
                )

            if eval_fold.empty:

                raise ValueError(
                    f"{nombre} fold {numero_fold}: "
                    f"evaluación vacía."
                )

            if (
                anio_embargo
                in train_fold[
                    "ANIO"
                ].unique()
            ):

                raise ValueError(
                    f"{nombre} fold {numero_fold}: "
                    f"el año de embargo está dentro de TRAIN."
                )

            resultado = entrenar_evaluar(
                train_fold,
                eval_fold,
                features,
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
                        nombre,

                    "DESCRIPCION":
                        descripcion,

                    "N_FEATURES":
                        len(
                            features
                        ),

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
                "ranking_eval"
            ]:

                filas_ranking.append(
                    {
                        "MODELO":
                            nombre,

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
            filas_metricas
        ),
        pd.DataFrame(
            filas_ranking
        ),
    )


# ============================================================
# RESUMEN
# ============================================================

def construir_resumen(
    validation_df,
    backtest_df,
    ranking_df,
):

    filas = []

    for escenario in ESCENARIOS:

        nombre = escenario[
            "MODELO"
        ]

        descripcion = escenario[
            "DESCRIPCION"
        ]

        validation = validation_df[
            validation_df[
                "MODELO"
            ]
            == nombre
        ].iloc[
            0
        ]

        backtest = backtest_df[
            backtest_df[
                "MODELO"
            ]
            == nombre
        ].copy()

        ranking = ranking_df[
            ranking_df[
                "MODELO"
            ]
            == nombre
        ].copy()

        pr = backtest[
            "PR_AUC_EVALUACION"
        ]

        roc = backtest[
            "ROC_AUC_EVALUACION"
        ]

        fila = {
            "MODELO":
                nombre,

            "DESCRIPCION":
                descripcion,

            "N_FEATURES":
                int(
                    validation[
                        "N_FEATURES"
                    ]
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
                    pr.mean()
                ),

            "BACKTEST_PR_AUC_MEDIANA":
                float(
                    pr.median()
                ),

            "BACKTEST_PR_AUC_STD":
                float(
                    pr.std(
                        ddof=1
                    )
                ),

            "BACKTEST_PR_AUC_MIN":
                float(
                    pr.min()
                ),

            "BACKTEST_PR_AUC_MAX":
                float(
                    pr.max()
                ),

            "BACKTEST_ROC_AUC_MEDIA":
                float(
                    roc.mean()
                ),

            "BACKTEST_GAP_PR_AUC_MEDIO":
                float(
                    backtest[
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
    resumen,
):

    return {
        "experimento":
            "Comparacion HGB core vs HGB financial v10",

        "fecha_ejecucion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "objetivo":
            (
                "Aislar el efecto de las nuevas features "
                "financieras manteniendo exactamente la misma "
                "configuracion del modelo "
                "HistGradientBoostingClassifier."
            ),

        "dataset":
            ruta_relativa(
                INPUT_PATH
            ),

        "target":
            TARGET,

        "horizonte_target":
            "24 meses",

        "escenarios": {
            "HGB_CORE": {
                "numero_features":
                    len(
                        FEATURES_CORE
                    ),

                "features":
                    FEATURES_CORE,
            },

            "HGB_FINANCIAL": {
                "numero_features":
                    len(
                        FEATURES_EXTENDIDAS
                    ),

                "features_core":
                    FEATURES_CORE,

                "features_financieras":
                    FEATURES_FINANCIERAS,

                "features_totales":
                    FEATURES_EXTENDIDAS,
            },
        },

        "hgb_parametros":
            HGB_PARAMS,

        "tuning_realizado":
            False,

        "provincia_utilizada":
            False,

        "validation": {
            "anio":
                2020,

            "rol":
                "comparacion de desarrollo",
        },

        "backtest": {
            "numero_folds":
                4,

            "periodo":
                "2012-2018",

            "embargo":
                "1 año fiscal entre TRAIN y evaluacion",
        },

        "tratamiento_features_financieras": {
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
                    "Categoria nativa. Las categorias se "
                    "aprenden exclusivamente desde TRAIN "
                    "en cada evaluacion."
                ),
        },

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

        "seleccion_final_realizada":
            False,

        "nota":
            (
                "Este experimento no selecciona automaticamente "
                "un modelo final. La comparacion debe revisarse "
                "considerando PR-AUC, estabilidad temporal, "
                "ranking y brecha TRAIN-evaluacion."
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
                    VALIDATION_OUTPUT_PATH
                ),

            "backtest":
                ruta_relativa(
                    BACKTEST_OUTPUT_PATH
                ),

            "ranking":
                ruta_relativa(
                    RANKING_OUTPUT_PATH
                ),

            "summary":
                ruta_relativa(
                    SUMMARY_OUTPUT_PATH
                ),

            "metadata":
                ruta_relativa(
                    METADATA_OUTPUT_PATH
                ),
        },

        "resumen":
            resumen.to_dict(
                orient="records"
            ),
    }


# ============================================================
# MOSTRAR RESUMEN
# ============================================================

def mostrar_resumen(
    resumen,
    backtest,
):

    print(
        "\n"
        + "=" * 120
    )

    print(
        "RESUMEN HGB CORE VS HGB FINANCIAL"
    )

    print(
        "=" * 120
    )

    columnas = [
        "MODELO",
        "N_FEATURES",
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
        resumen[
            columnas
        ].to_string(
            index=False
        )
    )

    print(
        "\nPR-AUC por fold:"
    )

    tabla_folds = backtest.pivot(
        index=[
            "FOLD",
            "ANIO_EVALUACION",
        ],
        columns="MODELO",
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
        + "=" * 120
    )

    print(
        "PROSPECT FINDER BVQ"
    )

    print(
        "HGB CORE VS HGB FINANCIAL - v10"
    )

    print(
        "=" * 120
    )

    print(
        "\nObjetivo:"
    )

    print(
        "Medir exclusivamente el aporte de las nuevas "
        "features financieras."
    )

    print(
        "\nConfiguración HGB:"
    )

    print(
        "Sin cambios respecto al HGB v10 existente."
    )

    print(
        "\nEscenarios:"
    )

    print(
        f"HGB_CORE:      "
        f"{len(FEATURES_CORE)} features"
    )

    print(
        f"HGB_FINANCIAL: "
        f"{len(FEATURES_EXTENDIDAS)} features"
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
        backtest_df,
        ranking_df,
    ) = ejecutar_backtest(
        train
    )

    # --------------------------------------------------------
    # RESUMEN
    # --------------------------------------------------------

    resumen_df = construir_resumen(
        validation_df,
        backtest_df,
        ranking_df,
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
        VALIDATION_OUTPUT_PATH,
        index=False,
    )

    backtest_df.to_csv(
        BACKTEST_OUTPUT_PATH,
        index=False,
    )

    ranking_df.to_csv(
        RANKING_OUTPUT_PATH,
        index=False,
    )

    resumen_df.to_csv(
        SUMMARY_OUTPUT_PATH,
        index=False,
    )

    with open(
        METADATA_OUTPUT_PATH,
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
        backtest_df,
    )

    print(
        "\nArchivos generados:"
    )

    print(
        VALIDATION_OUTPUT_PATH
    )

    print(
        BACKTEST_OUTPUT_PATH
    )

    print(
        RANKING_OUTPUT_PATH
    )

    print(
        SUMMARY_OUTPUT_PATH
    )

    print(
        METADATA_OUTPUT_PATH
    )

    print(
        "\nComparación finalizada correctamente."
    )


if __name__ == "__main__":
    main()