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
    / "v10_features_core_2012_2023.csv.gz"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "v10"
)

METRICS_PATH = (
    OUTPUT_DIR
    / "backtest_hist_gradient_boosting_v10_metrics.csv"
)

RANKING_PATH = (
    OUTPUT_DIR
    / "backtest_hist_gradient_boosting_v10_ranking_metrics.csv"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "backtest_hist_gradient_boosting_v10_summary.csv"
)

METADATA_PATH = (
    OUTPUT_DIR
    / "backtest_hist_gradient_boosting_v10_metadata.json"
)


MODEL_NAME = "v10_hgb"

TARGET = "TARGET_24M"

RANDOM_STATE = 42

CHUNK_SIZE = 150_000

K_VALUES = [
    50,
    100,
    200,
]


# ============================================================
# FEATURES
# ============================================================

FEATURES_NUMERICAS = [
    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",
    "activos_final_t1",
    "patrimonio_final_t1",
    "bi_ingresos_ventas_t1",
    "bi_n_empleados_t1",
]


FEATURES_BOOLEANAS = [
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


FEATURES = (
    FEATURES_NUMERICAS
    + FEATURES_BOOLEANAS
    + FEATURES_CATEGORICAS
)


COLUMNAS_LECTURA = (
    [
        "ANIO",
        "SPLIT",
        TARGET,
    ]
    + FEATURES
)


# ============================================================
# CONFIGURACIÓN DEL MODELO
# ============================================================

# Configuración regularizada heredada de v8.
#
# No se realiza tuning durante este backtesting.
#
# Es exactamente la misma configuración utilizada en el
# experimento inicial HistGradientBoosting v10.

MODEL_PARAMS = {
    "loss": "log_loss",
    "learning_rate": 0.05,
    "max_iter": 150,
    "max_leaf_nodes": 7,
    "max_depth": 3,
    "min_samples_leaf": 100,
    "l2_regularization": 1.0,
    "early_stopping": False,
    "random_state": RANDOM_STATE,
    "class_weight": "balanced",
    "categorical_features": "from_dtype",
}


# ============================================================
# FOLDS TEMPORALES v10
# ============================================================

FOLDS = [
    {
        "FOLD": 1,
        "TRAIN_INICIO": 2012,
        "TRAIN_FIN": 2013,
        "ANIO_EMBARGO": 2014,
        "ANIO_EVALUACION": 2015,
    },

    {
        "FOLD": 2,
        "TRAIN_INICIO": 2012,
        "TRAIN_FIN": 2014,
        "ANIO_EMBARGO": 2015,
        "ANIO_EVALUACION": 2016,
    },

    {
        "FOLD": 3,
        "TRAIN_INICIO": 2012,
        "TRAIN_FIN": 2015,
        "ANIO_EMBARGO": 2016,
        "ANIO_EVALUACION": 2017,
    },

    {
        "FOLD": 4,
        "TRAIN_INICIO": 2012,
        "TRAIN_FIN": 2016,
        "ANIO_EMBARGO": 2017,
        "ANIO_EVALUACION": 2018,
    },
]


# ============================================================
# UNIVERSO CONGELADO v10
# ============================================================

EXPECTED_YEAR_COUNTS = {
    2012: {
        "filas": 42158,
        "positivos": 55,
    },
    2013: {
        "filas": 47140,
        "positivos": 49,
    },
    2014: {
        "filas": 52528,
        "positivos": 39,
    },
    2015: {
        "filas": 76468,
        "positivos": 43,
    },
    2016: {
        "filas": 79503,
        "positivos": 73,
    },
    2017: {
        "filas": 83107,
        "positivos": 89,
    },
    2018: {
        "filas": 89818,
        "positivos": 59,
    },
}


EXPECTED_TOTAL_ROWS = 470_722
EXPECTED_TOTAL_POSITIVES = 407


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def ruta_relativa(path):
    """
    Devuelve una ruta relativa al proyecto.
    """

    return str(
        path.relative_to(PROJECT_ROOT)
    ).replace("\\", "/")


def normalizar_booleana(serie):
    """
    Convierte distintas representaciones booleanas a 0/1.
    """

    texto = (
        serie
        .astype("string")
        .str.strip()
        .str.lower()
    )

    mapa = {
        "true": 1.0,
        "false": 0.0,
        "1": 1.0,
        "0": 0.0,
        "1.0": 1.0,
        "0.0": 0.0,
        "si": 1.0,
        "sí": 1.0,
        "no": 0.0,
        "yes": 1.0,
        "verdadero": 1.0,
        "falso": 0.0,
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
# PREPARAR DATOS
# ============================================================

def preparar_datos(df):
    """
    Normaliza tipos de forma determinística.

    No aprende parámetros estadísticos desde los años
    de evaluación.
    """

    df = df.copy()

    # --------------------------------------------------------
    # ANIO
    # --------------------------------------------------------

    df["ANIO"] = pd.to_numeric(
        df["ANIO"],
        errors="coerce",
    )

    if df["ANIO"].isna().any():

        raise ValueError(
            "Existen valores ANIO inválidos."
        )

    df["ANIO"] = df["ANIO"].astype(
        int
    )

    # --------------------------------------------------------
    # TARGET
    # --------------------------------------------------------

    df[TARGET] = pd.to_numeric(
        df[TARGET],
        errors="coerce",
    )

    if df[TARGET].isna().any():

        raise ValueError(
            "Existen valores TARGET_24M inválidos."
        )

    valores_target = set(
        df[TARGET]
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

    df[TARGET] = df[TARGET].astype(
        int
    )

    # --------------------------------------------------------
    # NUMÉRICAS
    # --------------------------------------------------------

    for variable in FEATURES_NUMERICAS:

        df[variable] = pd.to_numeric(
            df[variable],
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

        df[variable] = normalizar_booleana(
            df[variable]
        )

    # --------------------------------------------------------
    # CATEGÓRICA
    # --------------------------------------------------------

    for variable in FEATURES_CATEGORICAS:

        df[variable] = df[
            variable
        ].astype(
            "string"
        )

    return df


# ============================================================
# CARGAR DATASET DE BACKTEST
# ============================================================

def cargar_dataset_backtest():
    """
    Carga exclusivamente TRAIN oficial 2012-2018.

    VALIDATION 2020 y TEST 2022-2023 no se incorporan.
    """

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

    columnas_faltantes = [
        columna
        for columna in COLUMNAS_LECTURA
        if columna not in columnas_disponibles
    ]

    if columnas_faltantes:

        raise ValueError(
            "Faltan columnas requeridas:\n"
            + "\n".join(
                columnas_faltantes
            )
        )

    print(
        "\nCargando dataset v10..."
    )

    print(
        f"Fuente: {INPUT_PATH}"
    )

    partes = []

    for chunk in pd.read_csv(
        INPUT_PATH,
        usecols=COLUMNAS_LECTURA,
        chunksize=CHUNK_SIZE,
        low_memory=False,
        dtype={
            "SPLIT": "string",
            "tipo_compania": "string",
        },
    ):

        chunk["ANIO"] = pd.to_numeric(
            chunk["ANIO"],
            errors="coerce",
        )

        split_normalizado = (
            chunk["SPLIT"]
            .astype("string")
            .str.strip()
            .str.upper()
        )

        mascara = (
            chunk["ANIO"].between(
                2012,
                2018,
                inclusive="both",
            )
            &
            split_normalizado.eq(
                "TRAIN"
            ).fillna(
                False
            )
        )

        if mascara.any():

            partes.append(
                chunk.loc[
                    mascara
                ].copy()
            )

    if not partes:

        raise ValueError(
            "No se encontraron observaciones TRAIN 2012-2018."
        )

    df = pd.concat(
        partes,
        ignore_index=True,
    )

    df = preparar_datos(
        df
    )

    validar_dataset_congelado(
        df
    )

    return df


# ============================================================
# VALIDAR DATASET CONGELADO
# ============================================================

def validar_dataset_congelado(df):
    """
    Verifica que el universo coincida exactamente con
    el TRAIN v10 congelado.
    """

    total_filas = len(
        df
    )

    total_positivos = int(
        df[TARGET].sum()
    )

    if total_filas != EXPECTED_TOTAL_ROWS:

        raise ValueError(
            "Número total de filas distinto al esperado. "
            f"Esperado={EXPECTED_TOTAL_ROWS:,}, "
            f"observado={total_filas:,}."
        )

    if total_positivos != EXPECTED_TOTAL_POSITIVES:

        raise ValueError(
            "Número total de positivos distinto al esperado. "
            f"Esperado={EXPECTED_TOTAL_POSITIVES}, "
            f"observado={total_positivos}."
        )

    print(
        "\nValidación anual:"
    )

    for anio in sorted(
        EXPECTED_YEAR_COUNTS
    ):

        esperado = EXPECTED_YEAR_COUNTS[
            anio
        ]

        subset = df[
            df["ANIO"]
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

        print(
            f"  {anio}: "
            f"{filas:,} filas | "
            f"{positivos} positivos"
        )

        if filas != esperado["filas"]:

            raise ValueError(
                f"Año {anio}: filas diferentes al universo "
                "congelado."
            )

        if positivos != esperado["positivos"]:

            raise ValueError(
                f"Año {anio}: positivos diferentes al universo "
                "congelado."
            )

    print(
        "\nDataset de backtesting validado."
    )

    print(
        f"Filas: {total_filas:,}"
    )

    print(
        f"Positivos: {total_positivos:,}"
    )

    print(
        "VALIDATION 2020: NO UTILIZADA"
    )

    print(
        "TEST 2022-2023: RESERVADO - SIN EVALUACIÓN"
    )


# ============================================================
# PREPARACIÓN CATEGÓRICA POR FOLD
# ============================================================

def preparar_categorias_fold(
    train,
    evaluacion,
):
    """
    Aprende categorías exclusivamente desde TRAIN del fold.

    Categorías nuevas en evaluación se convierten en missing.
    """

    train = train.copy()
    evaluacion = evaluacion.copy()

    categorias_por_variable = {}
    desconocidos_evaluacion = {}

    for variable in FEATURES_CATEGORICAS:

        categorias_train = (
            train[
                variable
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        categorias_train = sorted(
            categorias_train
        )

        if len(categorias_train) > 255:

            raise ValueError(
                f"{variable} tiene más de 255 categorías."
            )

        categorias_por_variable[
            variable
        ] = categorias_train

        desconocidos = (
            evaluacion[
                variable
            ].notna()
            &
            ~evaluacion[
                variable
            ]
            .astype(str)
            .isin(
                categorias_train
            )
        )

        desconocidos_evaluacion[
            variable
        ] = int(
            desconocidos.sum()
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

    return (
        train,
        evaluacion,
        categorias_por_variable,
        desconocidos_evaluacion,
    )


# ============================================================
# MÉTRICAS
# ============================================================

def calcular_pr_auc(
    y_true,
    scores,
):
    """
    Calcula Average Precision como PR-AUC operacional.
    """

    return float(
        average_precision_score(
            y_true,
            scores,
        )
    )


def calcular_roc_auc(
    y_true,
    scores,
):
    """
    Calcula ROC-AUC.
    """

    if len(
        np.unique(
            y_true
        )
    ) < 2:

        return np.nan

    return float(
        roc_auc_score(
            y_true,
            scores,
        )
    )


def metricas_ranking(
    y_true,
    scores,
):
    """
    Calcula Precision@K, Recall@K y Lift@K.
    """

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

    total = len(
        tabla
    )

    positivos = int(
        tabla[
            "TARGET"
        ].sum()
    )

    prevalencia = (
        positivos / total
        if total > 0
        else np.nan
    )

    resultados = []

    for k in K_VALUES:

        k_real = min(
            k,
            total,
        )

        top = tabla.head(
            k_real
        )

        positivos_top = int(
            top[
                "TARGET"
            ].sum()
        )

        precision_k = (
            positivos_top
            / k_real
            if k_real > 0
            else np.nan
        )

        recall_k = (
            positivos_top
            / positivos
            if positivos > 0
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
                    int(
                        k
                    ),

                "K_REAL":
                    int(
                        k_real
                    ),

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

                "PREVALENCIA_EVALUACION":
                    float(
                        prevalencia
                    ),
            }
        )

    return resultados


# ============================================================
# VALIDAR FOLD
# ============================================================

def validar_fold(
    fold,
    train,
    evaluacion,
):
    """
    Verifica separación temporal y clases.
    """

    numero_fold = fold[
        "FOLD"
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

    if train.empty:

        raise ValueError(
            f"TRAIN vacío en fold {numero_fold}."
        )

    if evaluacion.empty:

        raise ValueError(
            f"Evaluación vacía en fold {numero_fold}."
        )

    if train["ANIO"].max() != train_fin:

        raise ValueError(
            f"Fold {numero_fold}: TRAIN_FIN inconsistente."
        )

    if not (
        train_fin
        < anio_embargo
        < anio_evaluacion
    ):

        raise ValueError(
            f"Fold {numero_fold}: secuencia temporal inválida."
        )

    if anio_embargo in train["ANIO"].unique():

        raise ValueError(
            f"Fold {numero_fold}: embargo presente en TRAIN."
        )

    if anio_embargo in evaluacion["ANIO"].unique():

        raise ValueError(
            f"Fold {numero_fold}: embargo presente en evaluación."
        )

    if train[TARGET].nunique() < 2:

        raise ValueError(
            f"Fold {numero_fold}: TRAIN no contiene ambas clases."
        )

    if evaluacion[TARGET].nunique() < 2:

        raise ValueError(
            f"Fold {numero_fold}: evaluación no contiene ambas clases."
        )


# ============================================================
# EJECUTAR BACKTEST
# ============================================================

def ejecutar_backtest(df):
    """
    Ejecuta HistGradientBoosting v10 sobre los cuatro folds.
    """

    metricas_resultados = []
    ranking_resultados = []

    categorias_metadata = []

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

        print(
            "\n"
            + "=" * 110
        )

        print(
            f"FOLD {numero_fold}"
        )

        print(
            "=" * 110
        )

        print(
            f"TRAIN: {train_inicio}-{train_fin}"
        )

        print(
            f"EMBARGO: {anio_embargo}"
        )

        print(
            f"EVALUACIÓN: {anio_evaluacion}"
        )

        # ----------------------------------------------------
        # TRAIN
        # ----------------------------------------------------

        train = df[
            (
                df["ANIO"]
                >= train_inicio
            )
            &
            (
                df["ANIO"]
                <= train_fin
            )
        ].copy()

        # ----------------------------------------------------
        # EVALUACIÓN
        # ----------------------------------------------------

        evaluacion = df[
            df["ANIO"]
            == anio_evaluacion
        ].copy()

        validar_fold(
            fold,
            train,
            evaluacion,
        )

        # ----------------------------------------------------
        # CATEGORÍAS
        # ----------------------------------------------------

        (
            train,
            evaluacion,
            categorias,
            desconocidos,
        ) = preparar_categorias_fold(
            train,
            evaluacion,
        )

        categorias_metadata.append(
            {
                "fold":
                    numero_fold,

                "categorias_train":
                    categorias,

                "categorias_desconocidas_evaluacion":
                    desconocidos,
            }
        )

        # ----------------------------------------------------
        # X / y
        # ----------------------------------------------------

        X_train = train[
            FEATURES
        ].copy()

        y_train = train[
            TARGET
        ].astype(
            int
        )

        X_eval = evaluacion[
            FEATURES
        ].copy()

        y_eval = evaluacion[
            TARGET
        ].astype(
            int
        )

        print(
            f"TRAIN filas: {len(train):,} | "
            f"positivos: {int(y_train.sum()):,}"
        )

        print(
            f"EVAL filas: {len(evaluacion):,} | "
            f"positivos: {int(y_eval.sum()):,}"
        )

        print(
            f"Categorías tipo_compania TRAIN: "
            f"{len(categorias['tipo_compania'])}"
        )

        print(
            f"Categorías desconocidas EVAL: "
            f"{desconocidos['tipo_compania']}"
        )

        # ----------------------------------------------------
        # MODELO
        # ----------------------------------------------------

        modelo = HistGradientBoostingClassifier(
            **MODEL_PARAMS
        )

        modelo.fit(
            X_train,
            y_train,
        )

        # ----------------------------------------------------
        # SCORES
        # ----------------------------------------------------

        scores_train = modelo.predict_proba(
            X_train
        )[:, 1]

        scores_eval = modelo.predict_proba(
            X_eval
        )[:, 1]

        # ----------------------------------------------------
        # MÉTRICAS
        # ----------------------------------------------------

        pr_auc_train = calcular_pr_auc(
            y_train,
            scores_train,
        )

        roc_auc_train = calcular_roc_auc(
            y_train,
            scores_train,
        )

        pr_auc_eval = calcular_pr_auc(
            y_eval,
            scores_eval,
        )

        roc_auc_eval = calcular_roc_auc(
            y_eval,
            scores_eval,
        )

        gap_pr_auc = (
            pr_auc_train
            - pr_auc_eval
        )

        metricas_resultados.append(
            {
                "MODELO":
                    MODEL_NAME,

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
                    len(
                        train
                    ),

                "POSITIVOS_TRAIN":
                    int(
                        y_train.sum()
                    ),

                "N_EVALUACION":
                    len(
                        evaluacion
                    ),

                "POSITIVOS_EVALUACION":
                    int(
                        y_eval.sum()
                    ),

                "PREVALENCIA_EVALUACION":
                    float(
                        y_eval.mean()
                    ),

                "NUMERO_FEATURES_FISICAS":
                    len(
                        FEATURES
                    ),

                "PR_AUC_TRAIN":
                    pr_auc_train,

                "ROC_AUC_TRAIN":
                    roc_auc_train,

                "PR_AUC_EVALUACION":
                    pr_auc_eval,

                "ROC_AUC_EVALUACION":
                    roc_auc_eval,

                "GAP_PR_AUC":
                    gap_pr_auc,

                "N_ITER":
                    int(
                        modelo.n_iter_
                    ),
            }
        )

        # ----------------------------------------------------
        # RANKING
        # ----------------------------------------------------

        ranking_fold = metricas_ranking(
            y_eval,
            scores_eval,
        )

        for resultado in ranking_fold:

            ranking_resultados.append(
                {
                    "MODELO":
                        MODEL_NAME,

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

                    "N_EVALUACION":
                        len(
                            evaluacion
                        ),

                    "POSITIVOS_EVALUACION":
                        int(
                            y_eval.sum()
                        ),

                    **resultado,
                }
            )

        # ----------------------------------------------------
        # MOSTRAR
        # ----------------------------------------------------

        print(
            f"\nPR-AUC TRAIN: "
            f"{pr_auc_train:.9f}"
        )

        print(
            f"PR-AUC EVAL:  "
            f"{pr_auc_eval:.9f}"
        )

        print(
            f"ROC-AUC EVAL: "
            f"{roc_auc_eval:.9f}"
        )

        for resultado in ranking_fold:

            print(
                f"Top {resultado['K']:>3}: "
                f"{resultado['POSITIVOS_TOP_K']} positivos | "
                f"Precision={resultado['PRECISION_AT_K']:.6f} | "
                f"Recall={resultado['RECALL_AT_K']:.6f} | "
                f"Lift={resultado['LIFT_AT_K']:.6f}"
            )

    metricas_df = pd.DataFrame(
        metricas_resultados
    )

    ranking_df = pd.DataFrame(
        ranking_resultados
    )

    return (
        metricas_df,
        ranking_df,
        categorias_metadata,
    )


# ============================================================
# RESUMEN
# ============================================================

def construir_resumen(
    metricas_df,
    ranking_df,
):
    """
    Resume estabilidad temporal del HGB v10.
    """

    pr_auc = metricas_df[
        "PR_AUC_EVALUACION"
    ]

    roc_auc = metricas_df[
        "ROC_AUC_EVALUACION"
    ]

    gap_pr_auc = metricas_df[
        "GAP_PR_AUC"
    ]

    fila = {
        "MODELO":
            MODEL_NAME,

        "N_FOLDS":
            len(
                metricas_df
            ),

        "PR_AUC_MEDIA":
            float(
                pr_auc.mean()
            ),

        "PR_AUC_MEDIANA":
            float(
                pr_auc.median()
            ),

        "PR_AUC_STD":
            float(
                pr_auc.std(
                    ddof=1
                )
            ),

        "PR_AUC_MIN":
            float(
                pr_auc.min()
            ),

        "PR_AUC_MAX":
            float(
                pr_auc.max()
            ),

        "ROC_AUC_MEDIA":
            float(
                roc_auc.mean()
            ),

        "ROC_AUC_MEDIANA":
            float(
                roc_auc.median()
            ),

        "ROC_AUC_STD":
            float(
                roc_auc.std(
                    ddof=1
                )
            ),

        "ROC_AUC_MIN":
            float(
                roc_auc.min()
            ),

        "ROC_AUC_MAX":
            float(
                roc_auc.max()
            ),

        "GAP_PR_AUC_MEDIO":
            float(
                gap_pr_auc.mean()
            ),
    }

    for k in K_VALUES:

        ranking_k = ranking_df[
            ranking_df[
                "K"
            ]
            == k
        ].copy()

        fila[
            f"POSITIVOS_TOP_{k}_TOTAL"
        ] = int(
            ranking_k[
                "POSITIVOS_TOP_K"
            ].sum()
        )

        fila[
            f"PRECISION_AT_{k}_MEDIA"
        ] = float(
            ranking_k[
                "PRECISION_AT_K"
            ].mean()
        )

        fila[
            f"RECALL_AT_{k}_MEDIA"
        ] = float(
            ranking_k[
                "RECALL_AT_K"
            ].mean()
        )

        fila[
            f"LIFT_AT_{k}_MEDIA"
        ] = float(
            ranking_k[
                "LIFT_AT_K"
            ].mean()
        )

        fila[
            f"LIFT_AT_{k}_STD"
        ] = float(
            ranking_k[
                "LIFT_AT_K"
            ].std(
                ddof=1
            )
        )

        fila[
            f"LIFT_AT_{k}_MIN"
        ] = float(
            ranking_k[
                "LIFT_AT_K"
            ].min()
        )

        fila[
            f"LIFT_AT_{k}_MAX"
        ] = float(
            ranking_k[
                "LIFT_AT_K"
            ].max()
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
    df,
    metricas_df,
    categorias_metadata,
):
    """
    Construye metadata reproducible del experimento.
    """

    metadata = {
        "experimento":
            "Backtesting temporal HistGradientBoosting v10",

        "modelo":
            "HistGradientBoostingClassifier",

        "nombre_modelo":
            MODEL_NAME,

        "fecha_ejecucion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "objetivo":
            (
                "Evaluar la estabilidad temporal de "
                "HistGradientBoosting v10 utilizando exactamente "
                "el mismo protocolo rolling-origin utilizado "
                "para las variantes Logistic Regression v10."
            ),

        "dataset":
            ruta_relativa(
                INPUT_PATH
            ),

        "target":
            TARGET,

        "horizonte_target":
            "24 meses",

        "periodo_backtest":
            "2012-2018",

        "validation_2020_utilizada":
            False,

        "test_2022_2023_utilizado":
            False,

        "test_estado":
            "RESERVADO - SIN EVALUACION",

        "numero_observaciones_backtest":
            int(
                len(
                    df
                )
            ),

        "numero_positivos_backtest":
            int(
                df[
                    TARGET
                ].sum()
            ),

        "folds":
            FOLDS,

        "features_numericas":
            FEATURES_NUMERICAS,

        "features_booleanas":
            FEATURES_BOOLEANAS,

        "features_categoricas":
            FEATURES_CATEGORICAS,

        "numero_features_fisicas":
            len(
                FEATURES
            ),

        "provincia_utilizada_como_predictor":
            False,

        "baseline_comparacion":
            "v10_lr_no_provincia",

        "configuracion_modelo":
            MODEL_PARAMS,

        "origen_configuracion":
            (
                "Configuracion regularizada heredada de v8. "
                "No se realiza tuning durante este backtesting."
            ),

        "manejo_missing_numerico":
            (
                "Nativo de HistGradientBoostingClassifier."
            ),

        "escalamiento":
            False,

        "categorical_features":
            "from_dtype",

        "categorias_aprendidas_por_fold":
            categorias_metadata,

        "metricas_principales": [
            "PR-AUC",
            "Precision@50",
            "Precision@100",
            "Precision@200",
            "Recall@50",
            "Recall@100",
            "Recall@200",
            "Lift@50",
            "Lift@100",
            "Lift@200",
        ],

        "metrica_complementaria":
            "ROC-AUC",

        "numero_folds_ejecutados":
            int(
                len(
                    metricas_df
                )
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
            "metricas":
                ruta_relativa(
                    METRICS_PATH
                ),

            "ranking":
                ruta_relativa(
                    RANKING_PATH
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

        "notas": [
            (
                "El backtesting utiliza exclusivamente "
                "observaciones pertenecientes al TRAIN oficial "
                "v10 2012-2018."
            ),
            (
                "Cada fold mantiene un año completo de embargo."
            ),
            (
                "Las categorias de tipo_compania se aprenden "
                "exclusivamente desde TRAIN de cada fold."
            ),
            (
                "VALIDATION 2020 no participa en este backtesting."
            ),
            (
                "TEST 2022-2023 permanece completamente cerrado."
            ),
        ],
    }

    return metadata


# ============================================================
# GUARDAR
# ============================================================

def guardar_resultados(
    metricas_df,
    ranking_df,
    resumen_df,
    metadata,
):
    """
    Guarda resultados agregados y metadata.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metricas_df.to_csv(
        METRICS_PATH,
        index=False,
    )

    ranking_df.to_csv(
        RANKING_PATH,
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


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        + "=" * 110
    )

    print(
        "PROSPECT FINDER BVQ"
    )

    print(
        "BACKTEST TEMPORAL - HISTGRADIENTBOOSTING v10"
    )

    print(
        "=" * 110
    )

    print(
        "\nProtocolo:"
    )

    print(
        "TRAIN interno 2012-2018"
    )

    print(
        "4 folds rolling-origin"
    )

    print(
        "1 año de embargo por fold"
    )

    print(
        "VALIDATION 2020 fuera del backtesting"
    )

    print(
        "TEST 2022-2023 cerrado"
    )

    print(
        f"Features físicas: {len(FEATURES)}"
    )

    print(
        "Provincia como predictor: NO"
    )

    print(
        "tipo_compania: categórica nativa"
    )

    # --------------------------------------------------------
    # DATASET
    # --------------------------------------------------------

    df = cargar_dataset_backtest()

    # --------------------------------------------------------
    # BACKTEST
    # --------------------------------------------------------

    (
        metricas_df,
        ranking_df,
        categorias_metadata,
    ) = ejecutar_backtest(
        df
    )

    # --------------------------------------------------------
    # RESUMEN
    # --------------------------------------------------------

    resumen_df = construir_resumen(
        metricas_df,
        ranking_df,
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    metadata = construir_metadata(
        df,
        metricas_df,
        categorias_metadata,
    )

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    guardar_resultados(
        metricas_df,
        ranking_df,
        resumen_df,
        metadata,
    )

    # --------------------------------------------------------
    # MOSTRAR RESUMEN
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 110
    )

    print(
        "RESUMEN DE ESTABILIDAD"
    )

    print(
        "=" * 110
    )

    columnas = [
        "MODELO",
        "N_FOLDS",
        "PR_AUC_MEDIA",
        "PR_AUC_MEDIANA",
        "PR_AUC_STD",
        "PR_AUC_MIN",
        "PR_AUC_MAX",
        "LIFT_AT_50_MEDIA",
        "LIFT_AT_100_MEDIA",
        "LIFT_AT_200_MEDIA",
    ]

    print(
        resumen_df[
            columnas
        ].to_string(
            index=False
        )
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
        METADATA_PATH
    )

    print(
        "\nVALIDATION 2020:"
    )

    print(
        "NO UTILIZADA EN ESTE BACKTEST"
    )

    print(
        "\nTEST 2022-2023:"
    )

    print(
        "RESERVADO - SIN EVALUACIÓN"
    )

    print(
        "\nBacktesting HistGradientBoosting v10 finalizado."
    )


if __name__ == "__main__":
    main()