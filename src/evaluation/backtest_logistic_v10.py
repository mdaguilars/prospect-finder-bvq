from pathlib import Path
from datetime import datetime, timezone
import json
import platform
import sys

import numpy as np
import pandas as pd
import sklearn

from sklearn.compose import ColumnTransformer
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
    / "backtest_logistic_v10_metrics.csv"
)

RANKING_PATH = (
    OUTPUT_DIR
    / "backtest_logistic_v10_ranking_metrics.csv"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "backtest_logistic_v10_summary.csv"
)

METADATA_PATH = (
    OUTPUT_DIR
    / "backtest_logistic_v10_metadata.json"
)


RANDOM_STATE = 42

K_VALUES = [
    50,
    100,
    200,
]

CHUNK_SIZE = 150_000

TARGET = "TARGET_24M"


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


FEATURES_CATEGORICAS = [
    "tipo_compania",
    "provincia",
]


FEATURES_BOOLEANAS = [
    "TIENE_T_MENOS_1",
    "flag_activos_negativos",
    "flag_ventas_negativas",
    "flag_empleados_fijo",
    "flag_empleados_salto_temporal",
    "flag_empleados_anomalia_total",
]


FEATURES = (
    FEATURES_NUMERICAS
    + FEATURES_CATEGORICAS
    + FEATURES_BOOLEANAS
)


# ============================================================
# CONFIGURACIONES DE REGRESIÓN LOGÍSTICA v10
# ============================================================

CONFIGURACIONES = {
    "v10_lr": {
        "categoricas": [
            "tipo_compania",
            "provincia",
        ],
    },

    "v10_lr_no_provincia": {
        "categoricas": [
            "tipo_compania",
        ],
    },

    "v10_lr_no_categoricas": {
        "categoricas": [],
    },

    "v10_lr_no_tipo_compania": {
        "categoricas": [
            "provincia",
        ],
    },
}


# ============================================================
# FOLDS TEMPORALES v10
# ============================================================

# Estrategia rolling-origin con ventana expansiva.
#
# Cada fold utiliza:
#
# TRAIN histórico
# -> un año completo de embargo
# -> un año de evaluación
#
# Todo el backtesting se encuentra dentro del TRAIN oficial
# v10: 2012-2018.
#
# VALIDATION 2020 no participa.
# TEST 2022-2023 permanece completamente cerrado.

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
# CONTROL DEL DATASET CONGELADO
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


COLUMNAS_LECTURA = (
    [
        "ANIO",
        "SPLIT",
        TARGET,
    ]
    + FEATURES
)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def ruta_relativa(path):
    """
    Devuelve una ruta relativa al proyecto utilizando
    separadores compatibles con metadata.
    """

    return str(
        path.relative_to(PROJECT_ROOT)
    ).replace("\\", "/")


def normalizar_booleana(serie):
    """
    Convierte diferentes representaciones booleanas a 0/1.

    Valores no reconocidos permanecen como NaN y posteriormente
    son tratados por el imputador aprendido exclusivamente
    sobre TRAIN.
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


def preparar_datos(df):
    """
    Normaliza tipos de datos sin aprender parámetros
    estadísticos del dataset.

    Imputación, escalamiento y codificación se realizan después
    dentro del pipeline y se ajustan exclusivamente con TRAIN.
    """

    df = df.copy()

    # --------------------------------------------------------
    # Año
    # --------------------------------------------------------

    df["ANIO"] = pd.to_numeric(
        df["ANIO"],
        errors="coerce",
    )

    if df["ANIO"].isna().any():
        raise ValueError(
            "Existen valores ANIO no válidos."
        )

    df["ANIO"] = df["ANIO"].astype(
        int
    )

    # --------------------------------------------------------
    # Target
    # --------------------------------------------------------

    df[TARGET] = pd.to_numeric(
        df[TARGET],
        errors="coerce",
    )

    if df[TARGET].isna().any():
        raise ValueError(
            "Existen valores TARGET_24M no válidos."
        )

    valores_target = set(
        df[TARGET].unique().tolist()
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
    # Numéricas
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
    # Categóricas
    # --------------------------------------------------------

    for variable in FEATURES_CATEGORICAS:

        df[variable] = df[
            variable
        ].astype(
            "object"
        )

        df.loc[
            pd.isna(
                df[variable]
            ),
            variable,
        ] = np.nan

    # --------------------------------------------------------
    # Booleanas
    # --------------------------------------------------------

    for variable in FEATURES_BOOLEANAS:

        df[variable] = normalizar_booleana(
            df[variable]
        )

    return df


def cargar_dataset_backtest():
    """
    Carga exclusivamente las observaciones pertenecientes
    al TRAIN oficial v10: 2012-2018.

    VALIDATION, EMBARGO_1, EMBARGO_2 y TEST no se incorporan
    al dataframe utilizado para backtesting.
    """

    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"No existe el dataset:\n{INPUT_PATH}"
        )

    # --------------------------------------------------------
    # Validar columnas
    # --------------------------------------------------------

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
            "Faltan columnas requeridas en el dataset:\n"
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

            parte = chunk.loc[
                mascara
            ].copy()

            partes.append(
                parte
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

    # --------------------------------------------------------
    # Protección temporal
    # --------------------------------------------------------

    if df["ANIO"].min() < 2012:

        raise ValueError(
            "El backtest contiene observaciones anteriores a 2012."
        )

    if df["ANIO"].max() > 2018:

        raise ValueError(
            "El backtest contiene observaciones posteriores a 2018."
        )

    # --------------------------------------------------------
    # Validación contra dataset congelado
    # --------------------------------------------------------

    total_filas = len(
        df
    )

    total_positivos = int(
        df[TARGET].sum()
    )

    if total_filas != EXPECTED_TOTAL_ROWS:

        raise ValueError(
            "El número total de filas TRAIN 2012-2018 no coincide "
            f"con el dataset congelado. "
            f"Esperado={EXPECTED_TOTAL_ROWS:,}, "
            f"observado={total_filas:,}."
        )

    if total_positivos != EXPECTED_TOTAL_POSITIVES:

        raise ValueError(
            "El número total de positivos TRAIN 2012-2018 no coincide "
            f"con el dataset congelado. "
            f"Esperado={EXPECTED_TOTAL_POSITIVES:,}, "
            f"observado={total_positivos:,}."
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
            df["ANIO"] == anio
        ]

        filas = len(
            subset
        )

        positivos = int(
            subset[TARGET].sum()
        )

        print(
            f"  {anio}: "
            f"{filas:,} filas | "
            f"{positivos} positivos"
        )

        if filas != esperado["filas"]:

            raise ValueError(
                f"Año {anio}: número de filas diferente "
                f"al dataset congelado. "
                f"Esperado={esperado['filas']:,}, "
                f"observado={filas:,}."
            )

        if positivos != esperado["positivos"]:

            raise ValueError(
                f"Año {anio}: número de positivos diferente "
                f"al dataset congelado. "
                f"Esperado={esperado['positivos']}, "
                f"observado={positivos}."
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
        "Años utilizados: 2012-2018"
    )

    print(
        "VALIDATION 2020: NO UTILIZADA"
    )

    print(
        "TEST 2022-2023: RESERVADO - SIN EVALUACIÓN"
    )

    return df


# ============================================================
# PIPELINE
# ============================================================

def crear_pipeline(
    features_categoricas,
):
    """
    Construye el pipeline de Regresión Logística v10.

    Todo parámetro aprendido se ajusta exclusivamente
    utilizando el TRAIN correspondiente a cada fold.
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

    transformers = [
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
    ]

    if features_categoricas:

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
                        handle_unknown="ignore",
                    ),
                ),
            ]
        )

        transformers.append(
            (
                "categorical",
                pipeline_categorico,
                features_categoricas,
            )
        )

    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop",
    )

    modelo = LogisticRegression(
        C=1.0,
        class_weight="balanced",
        solver="lbfgs",
        max_iter=2000,
        random_state=RANDOM_STATE,
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "model",
                modelo,
            ),
        ]
    )

    return pipeline


# ============================================================
# MÉTRICAS
# ============================================================

def calcular_pr_auc(
    y_true,
    scores,
):
    """
    Average Precision utilizada como PR-AUC operacional
    del proyecto.
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
    Calcula ROC-AUC cuando existen ambas clases.
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
    k_values,
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
        by="SCORE",
        ascending=False,
        kind="mergesort",
    ).reset_index(
        drop=True
    )

    total = len(
        tabla
    )

    total_positivos = int(
        tabla["TARGET"].sum()
    )

    prevalencia = (
        total_positivos / total
        if total > 0
        else np.nan
    )

    resultados = []

    for k in k_values:

        k_real = min(
            k,
            total,
        )

        top_k = tabla.head(
            k_real
        )

        positivos_top_k = int(
            top_k["TARGET"].sum()
        )

        precision_k = (
            positivos_top_k / k_real
            if k_real > 0
            else np.nan
        )

        recall_k = (
            positivos_top_k / total_positivos
            if total_positivos > 0
            else np.nan
        )

        lift_k = (
            precision_k / prevalencia
            if (
                prevalencia is not np.nan
                and prevalencia > 0
            )
            else np.nan
        )

        resultados.append(
            {
                "K":
                    int(k),

                "K_REAL":
                    int(k_real),

                "POSITIVOS_TOP_K":
                    positivos_top_k,

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
# VALIDACIONES DEL FOLD
# ============================================================

def validar_fold(
    fold,
    train,
    evaluacion,
):
    """
    Valida separación temporal y presencia de ambas clases.
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
            f"Fold {numero_fold}: el año de embargo aparece en TRAIN."
        )

    if anio_embargo in evaluacion["ANIO"].unique():

        raise ValueError(
            f"Fold {numero_fold}: el año de embargo aparece en evaluación."
        )

    if evaluacion["ANIO"].nunique() != 1:

        raise ValueError(
            f"Fold {numero_fold}: evaluación contiene más de un año."
        )

    if int(
        evaluacion["ANIO"].iloc[0]
    ) != anio_evaluacion:

        raise ValueError(
            f"Fold {numero_fold}: año de evaluación inconsistente."
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
# EJECUCIÓN DEL BACKTEST
# ============================================================

def ejecutar_backtest(
    df,
):
    """
    Ejecuta las cuatro configuraciones de Regresión Logística
    sobre los cuatro folds temporales congelados.
    """

    metricas_resultados = []
    ranking_resultados = []

    for nombre_modelo, configuracion in CONFIGURACIONES.items():

        features_categoricas = configuracion[
            "categoricas"
        ]

        features_modelo = (
            FEATURES_NUMERICAS
            + features_categoricas
            + FEATURES_BOOLEANAS
        )

        print(
            "\n"
            + "=" * 110
        )

        print(
            f"CONFIGURACIÓN: {nombre_modelo}"
        )

        print(
            "=" * 110
        )

        print(
            f"Features físicas utilizadas: "
            f"{len(features_modelo)}"
        )

        print(
            "Categóricas: "
            + (
                ", ".join(
                    features_categoricas
                )
                if features_categoricas
                else "NINGUNA"
            )
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

            print(
                "\n"
                + "-" * 110
            )

            print(
                f"FOLD {numero_fold}"
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

            # ------------------------------------------------
            # TRAIN
            # ------------------------------------------------

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

            # ------------------------------------------------
            # EVALUACIÓN
            # ------------------------------------------------

            evaluacion = df[
                df["ANIO"]
                == anio_evaluacion
            ].copy()

            validar_fold(
                fold,
                train,
                evaluacion,
            )

            X_train = train[
                features_modelo
            ].copy()

            y_train = train[
                TARGET
            ].astype(
                int
            )

            X_eval = evaluacion[
                features_modelo
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

            # ------------------------------------------------
            # Modelo
            # ------------------------------------------------

            pipeline = crear_pipeline(
                features_categoricas
            )

            pipeline.fit(
                X_train,
                y_train,
            )

            scores_train = pipeline.predict_proba(
                X_train
            )[:, 1]

            scores_eval = pipeline.predict_proba(
                X_eval
            )[:, 1]

            # ------------------------------------------------
            # Métricas TRAIN
            # ------------------------------------------------

            pr_auc_train = calcular_pr_auc(
                y_train,
                scores_train,
            )

            roc_auc_train = calcular_roc_auc(
                y_train,
                scores_train,
            )

            # ------------------------------------------------
            # Métricas evaluación
            # ------------------------------------------------

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

            modelo_lr = pipeline.named_steps[
                "model"
            ]

            n_iter = int(
                np.max(
                    modelo_lr.n_iter_
                )
            )

            metricas_resultados.append(
                {
                    "MODELO":
                        nombre_modelo,

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
                        len(train),

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
                            features_modelo
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
                        n_iter,
                }
            )

            # ------------------------------------------------
            # Ranking evaluación
            # ------------------------------------------------

            ranking_fold = metricas_ranking(
                y_eval,
                scores_eval,
                K_VALUES,
            )

            for resultado in ranking_fold:

                ranking_resultados.append(
                    {
                        "MODELO":
                            nombre_modelo,

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

            print(
                f"PR-AUC TRAIN: "
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
    )


# ============================================================
# RESUMEN DE ESTABILIDAD
# ============================================================

def construir_resumen(
    metricas_df,
    ranking_df,
):
    """
    Construye un resumen por configuración utilizando
    exclusivamente métricas de evaluación de los folds.
    """

    filas = []

    for nombre_modelo in CONFIGURACIONES:

        metricas_modelo = metricas_df[
            metricas_df["MODELO"]
            == nombre_modelo
        ].copy()

        pr_auc = metricas_modelo[
            "PR_AUC_EVALUACION"
        ]

        roc_auc = metricas_modelo[
            "ROC_AUC_EVALUACION"
        ]

        gap_pr_auc = metricas_modelo[
            "GAP_PR_AUC"
        ]

        fila = {
            "MODELO":
                nombre_modelo,

            "N_FOLDS":
                len(
                    metricas_modelo
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
                (
                    ranking_df["MODELO"]
                    == nombre_modelo
                )
                &
                (
                    ranking_df["K"]
                    == k
                )
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
    df,
    metricas_df,
):
    """
    Registra parámetros y condiciones necesarias para
    reproducir el experimento.
    """

    configuraciones_metadata = {}

    for nombre, configuracion in CONFIGURACIONES.items():

        categoricas = configuracion[
            "categoricas"
        ]

        features_modelo = (
            FEATURES_NUMERICAS
            + categoricas
            + FEATURES_BOOLEANAS
        )

        configuraciones_metadata[
            nombre
        ] = {
            "features_numericas":
                FEATURES_NUMERICAS,

            "features_categoricas":
                categoricas,

            "features_booleanas":
                FEATURES_BOOLEANAS,

            "numero_features_fisicas":
                len(
                    features_modelo
                ),
        }

    metadata = {
        "experimento":
            "Backtesting temporal Regresion Logistica v10",

        "fecha_ejecucion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "objetivo":
            (
                "Evaluar estabilidad temporal de cuatro "
                "configuraciones de Regresion Logistica v10 "
                "utilizando exclusivamente folds internos "
                "al TRAIN oficial 2012-2018."
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
                df[TARGET].sum()
            ),

        "folds":
            FOLDS,

        "configuraciones":
            configuraciones_metadata,

        "configuracion_modelo": {
            "modelo":
                "LogisticRegression",

            "C":
                1.0,

            "penalty":
                "l2",

            "class_weight":
                "balanced",

            "solver":
                "lbfgs",

            "max_iter":
                2000,

            "random_state":
                RANDOM_STATE,
        },

        "preprocesamiento": {
            "numericas":
                (
                    "SimpleImputer(strategy='median') "
                    "+ StandardScaler(), ajustados solo con TRAIN."
                ),

            "categoricas":
                (
                    "SimpleImputer(strategy='most_frequent') "
                    "+ OneHotEncoder(handle_unknown='ignore'), "
                    "ajustados solo con TRAIN."
                ),

            "booleanas":
                (
                    "Normalizacion deterministica a 0/1 y "
                    "SimpleImputer(strategy='most_frequent') "
                    "ajustado solo con TRAIN."
                ),
        },

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

        "numero_modelos_folds_ejecutados":
            int(
                len(
                    metricas_df
                )
            ),

        "expected_year_counts":
            EXPECTED_YEAR_COUNTS,

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
                "ANIO, EXPEDIENTE_KEY, RUC, NOMBRE y SPLIT "
                "no se utilizan como predictores."
            ),
            (
                "Los años de embargo no se utilizan para ajuste "
                "ni para evaluación dentro de cada fold."
            ),
            (
                "Las cuatro configuraciones utilizan exactamente "
                "los mismos folds."
            ),
            (
                "VALIDATION 2020 se mantiene fuera del backtesting "
                "y conserva su función de conjunto oficial de "
                "comparación durante desarrollo."
            ),
            (
                "TEST 2022-2023 permanece cerrado durante esta fase."
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
        "BACKTEST TEMPORAL - REGRESIÓN LOGÍSTICA v10"
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
        "4 configuraciones de Regresión Logística"
    )

    print(
        "VALIDATION 2020 fuera del backtesting"
    )

    print(
        "TEST 2022-2023 cerrado"
    )

    # --------------------------------------------------------
    # Dataset
    # --------------------------------------------------------

    df = cargar_dataset_backtest()

    # --------------------------------------------------------
    # Backtesting
    # --------------------------------------------------------

    metricas_df, ranking_df = ejecutar_backtest(
        df
    )

    # --------------------------------------------------------
    # Resumen
    # --------------------------------------------------------

    resumen_df = construir_resumen(
        metricas_df,
        ranking_df,
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata = construir_metadata(
        df,
        metricas_df,
    )

    # --------------------------------------------------------
    # Guardar
    # --------------------------------------------------------

    guardar_resultados(
        metricas_df,
        ranking_df,
        resumen_df,
        metadata,
    )

    # --------------------------------------------------------
    # Resultados
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

    columnas_resumen = [
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
            columnas_resumen
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
        "\nBacktesting v10 finalizado."
    )


if __name__ == "__main__":
    main()