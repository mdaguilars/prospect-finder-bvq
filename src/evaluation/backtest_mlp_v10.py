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
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
)
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.class_weight import compute_sample_weight


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
    / "backtest_mlp_v10_metrics.csv"
)

RANKING_PATH = (
    OUTPUT_DIR
    / "backtest_mlp_v10_ranking_metrics.csv"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "backtest_mlp_v10_summary.csv"
)

METADATA_PATH = (
    OUTPUT_DIR
    / "backtest_mlp_v10_metadata.json"
)


MODEL_NAME = "v10_mlp"

TARGET = "TARGET_24M"

RANDOM_STATE = 42

CHUNK_SIZE = 150_000

K_VALUES = [
    50,
    100,
    200,
]


# ============================================================
# FEATURES v10
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
# CONFIGURACIÓN MLP
# ============================================================

MODEL_PARAMS = {
    "hidden_layer_sizes": (
        64,
        32,
    ),
    "activation": "relu",
    "solver": "adam",
    "alpha": 0.01,
    "batch_size": 512,
    "learning_rate": "constant",
    "learning_rate_init": 0.001,
    "max_iter": 200,
    "shuffle": True,
    "random_state": RANDOM_STATE,
    "tol": 1e-4,
    "early_stopping": False,
    "n_iter_no_change": 10,
    "verbose": False,
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
    Normaliza tipos sin aprender parámetros estadísticos.
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
        ] = np.where(
            serie.isna(),
            np.nan,
            serie.astype(
                object
            ),
        )

    return df


# ============================================================
# CARGAR DATASET BACKTEST
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
    Verifica el TRAIN v10 congelado.
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
# PREPROCESAMIENTO POR FOLD
# ============================================================

def construir_preprocesador():
    """
    Todo el preprocesamiento se aprende exclusivamente
    desde TRAIN de cada fold.

    Numéricas:
        mediana + StandardScaler.

    Booleanas:
        imputación más frecuente.

    Categóricas:
        categoría faltante explícita + One-Hot Encoding.
    """

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
                    fill_value="__MISSING__",
                ),
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                    dtype=np.float64,
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
        sparse_threshold=0,
        verbose_feature_names_out=True,
    )


# ============================================================
# MÉTRICAS
# ============================================================

def calcular_pr_auc(
    y_true,
    scores,
):
    """
    Average Precision como PR-AUC operacional.
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
    Verifica la separación temporal y presencia de ambas clases.
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
    Ejecuta el MLP v10 en los cuatro folds temporales.
    """

    metricas_resultados = []
    ranking_resultados = []
    preprocesamiento_metadata = []

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
        # X / y
        # ----------------------------------------------------

        X_train_raw = train[
            FEATURES
        ].copy()

        y_train = train[
            TARGET
        ].astype(
            int
        )

        X_eval_raw = evaluacion[
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

        # ----------------------------------------------------
        # PREPROCESAMIENTO
        # ----------------------------------------------------

        preprocesador = construir_preprocesador()

        X_train = preprocesador.fit_transform(
            X_train_raw
        )

        X_eval = preprocesador.transform(
            X_eval_raw
        )

        nombres_transformados = (
            preprocesador
            .get_feature_names_out()
            .tolist()
        )

        print(
            f"Features transformadas: "
            f"{X_train.shape[1]}"
        )

        # ----------------------------------------------------
        # PESOS
        # ----------------------------------------------------

        sample_weights = compute_sample_weight(
            class_weight="balanced",
            y=y_train,
        )

        pesos_clase_0 = sample_weights[
            y_train.to_numpy()
            == 0
        ]

        pesos_clase_1 = sample_weights[
            y_train.to_numpy()
            == 1
        ]

        print(
            f"Peso clase 0: "
            f"{pesos_clase_0[0]:.6f}"
        )

        print(
            f"Peso clase 1: "
            f"{pesos_clase_1[0]:.6f}"
        )

        # ----------------------------------------------------
        # MODELO
        # ----------------------------------------------------

        modelo = MLPClassifier(
            **MODEL_PARAMS
        )

        convergence_warning = False

        with warnings.catch_warnings(
            record=True
        ) as advertencias:

            warnings.simplefilter(
                "always"
            )

            modelo.fit(
                X_train,
                y_train,
                sample_weight=sample_weights,
            )

            convergence_warning = any(
                issubclass(
                    advertencia.category,
                    ConvergenceWarning,
                )
                for advertencia in advertencias
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

                "NUMERO_FEATURES_TRANSFORMADAS":
                    int(
                        X_train.shape[
                            1
                        ]
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

                "LOSS_FINAL":
                    float(
                        modelo.loss_
                    ),

                "CONVERGENCE_WARNING":
                    bool(
                        convergence_warning
                    ),

                "PESO_CLASE_0":
                    float(
                        pesos_clase_0[
                            0
                        ]
                    ),

                "PESO_CLASE_1":
                    float(
                        pesos_clase_1[
                            0
                        ]
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
        # METADATA PREPROCESAMIENTO
        # ----------------------------------------------------

        preprocesamiento_metadata.append(
            {
                "fold":
                    numero_fold,

                "numero_features_transformadas":
                    int(
                        X_train.shape[
                            1
                        ]
                    ),

                "features_transformadas":
                    nombres_transformados,

                "peso_clase_0":
                    float(
                        pesos_clase_0[
                            0
                        ]
                    ),

                "peso_clase_1":
                    float(
                        pesos_clase_1[
                            0
                        ]
                    ),

                "iteraciones":
                    int(
                        modelo.n_iter_
                    ),

                "loss_final":
                    float(
                        modelo.loss_
                    ),

                "convergence_warning":
                    bool(
                        convergence_warning
                    ),
            }
        )

        # ----------------------------------------------------
        # MOSTRAR
        # ----------------------------------------------------

        print(
            f"\nIteraciones: "
            f"{modelo.n_iter_}"
        )

        print(
            f"Loss final: "
            f"{modelo.loss_:.9f}"
        )

        print(
            f"ConvergenceWarning: "
            f"{convergence_warning}"
        )

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
        preprocesamiento_metadata,
    )


# ============================================================
# RESUMEN
# ============================================================

def construir_resumen(
    metricas_df,
    ranking_df,
):
    """
    Resume estabilidad temporal del MLP v10.
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

    n_iter = metricas_df[
        "N_ITER"
    ]

    loss = metricas_df[
        "LOSS_FINAL"
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

        "N_ITER_MEDIA":
            float(
                n_iter.mean()
            ),

        "N_ITER_MIN":
            int(
                n_iter.min()
            ),

        "N_ITER_MAX":
            int(
                n_iter.max()
            ),

        "LOSS_FINAL_MEDIA":
            float(
                loss.mean()
            ),

        "CONVERGENCE_WARNINGS_TOTAL":
            int(
                metricas_df[
                    "CONVERGENCE_WARNING"
                ].sum()
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
    preprocesamiento_metadata,
):
    """
    Construye metadata reproducible.
    """

    metadata = {
        "experimento":
            "Backtesting temporal MLP v10",

        "modelo":
            "MLPClassifier",

        "nombre_modelo":
            MODEL_NAME,

        "fecha_ejecucion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "objetivo":
            (
                "Evaluar estabilidad temporal del MLP v10 "
                "utilizando exactamente el mismo protocolo "
                "rolling-origin empleado en Logistic Regression "
                "y HistGradientBoosting v10."
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

        "preprocesamiento": {
            "numericas":
                (
                    "Imputacion por mediana y StandardScaler "
                    "aprendidos exclusivamente con TRAIN "
                    "de cada fold."
                ),

            "booleanas":
                (
                    "Imputacion most_frequent aprendida "
                    "exclusivamente con TRAIN de cada fold."
                ),

            "categoricas":
                (
                    "Imputacion de categoria faltante y "
                    "OneHotEncoder(handle_unknown='ignore') "
                    "aprendidos exclusivamente con TRAIN "
                    "de cada fold."
                ),
        },

        "configuracion_modelo":
            {
                "hidden_layer_sizes":
                    [
                        64,
                        32,
                    ],

                "activation":
                    "relu",

                "solver":
                    "adam",

                "alpha":
                    0.01,

                "batch_size":
                    512,

                "learning_rate":
                    "constant",

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
            },

        "origen_configuracion":
            (
                "Arquitectura controlada heredada de v9. "
                "No se realiza tuning durante este backtesting."
            ),

        "manejo_desbalance":
            (
                "sample_weight balanceado calculado "
                "exclusivamente a partir del TRAIN "
                "de cada fold."
            ),

        "preprocesamiento_por_fold":
            preprocesamiento_metadata,

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

        "comparadores_v10": [
            "v10_lr_no_provincia",
            "v10_hgb",
        ],

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
                "observaciones pertenecientes al TRAIN "
                "oficial v10 2012-2018."
            ),
            (
                "Cada fold mantiene un año completo "
                "de embargo."
            ),
            (
                "Todo el preprocesamiento se ajusta "
                "exclusivamente dentro del TRAIN de cada fold."
            ),
            (
                "Los pesos de clase se calculan "
                "exclusivamente con TRAIN de cada fold."
            ),
            (
                "VALIDATION 2020 no participa en "
                "este backtesting."
            ),
            (
                "TEST 2022-2023 permanece completamente "
                "cerrado."
            ),
        ],
    }

    return metadata


# ============================================================
# GUARDAR RESULTADOS
# ============================================================

def guardar_resultados(
    metricas_df,
    ranking_df,
    resumen_df,
    metadata,
):
    """
    Guarda resultados del backtesting.
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
        "BACKTEST TEMPORAL - MLP v10"
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
        "tipo_compania: One-Hot Encoding por fold"
    )

    print(
        "Arquitectura MLP: 64 -> 32"
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
        preprocesamiento_metadata,
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
        preprocesamiento_metadata,
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
        "CONVERGENCE_WARNINGS_TOTAL",
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
        "\nBacktesting MLP v10 finalizado."
    )


if __name__ == "__main__":
    main()