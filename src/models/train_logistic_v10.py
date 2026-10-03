from pathlib import Path
from datetime import datetime, timezone
import json
import platform

import joblib
import numpy as np
import pandas as pd
import sklearn

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

RANDOM_STATE = 42

THRESHOLD = 0.50

K_VALUES = [
    50,
    100,
    200,
]


ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


INPUT_PATH = (
    ROOT
    / "data"
    / "processed"
    / "v10_features_core_2012_2023.csv.gz"
)


RESULTS_DIR = (
    ROOT
    / "reports"
    / "results"
    / "v10"
)


MODEL_DIR = (
    ROOT
    / "models"
    / "v10"
)


METRICS_PATH = (
    RESULTS_DIR
    / "v10_lr_metrics.csv"
)


RANKING_PATH = (
    RESULTS_DIR
    / "v10_lr_ranking_metrics.csv"
)


COEFFICIENTS_PATH = (
    RESULTS_DIR
    / "v10_lr_coefficients.csv"
)


VALIDATION_TOP_PATH = (
    RESULTS_DIR
    / "v10_lr_validation_top500.csv"
)


METADATA_PATH = (
    RESULTS_DIR
    / "v10_lr_metadata.json"
)


MODEL_PATH = (
    MODEL_DIR
    / "v10_lr.joblib"
)


# ============================================================
# FEATURE SET V10
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


TARGET = "TARGET_24M"


COLUMNAS_CONTROL = [
    "ANIO",
    "EXPEDIENTE_KEY",
    "RUC",
    "NOMBRE",
    TARGET,
    "SPLIT",
]


COLUMNAS_REQUERIDAS = (
    COLUMNAS_CONTROL
    + FEATURES
)


# ============================================================
# FUNCIONES
# ============================================================

def metricas_clasificacion(
    y_true,
    scores,
    threshold=0.50,
):

    y_true = np.asarray(
        y_true
    )

    scores = np.asarray(
        scores
    )


    pred = (
        scores >= threshold
    ).astype(
        int
    )


    tn, fp, fn, tp = (
        confusion_matrix(
            y_true,
            pred,
            labels=[
                0,
                1,
            ],
        )
        .ravel()
    )


    return {

        "OBSERVACIONES":
            int(
                len(
                    y_true
                )
            ),

        "POSITIVOS":
            int(
                y_true.sum()
            ),

        "PREVALENCIA":
            float(
                y_true.mean()
            ),

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

        "THRESHOLD":
            float(
                threshold
            ),

        "PRECISION":
            float(
                precision_score(
                    y_true,
                    pred,
                    zero_division=0,
                )
            ),

        "RECALL":
            float(
                recall_score(
                    y_true,
                    pred,
                    zero_division=0,
                )
            ),

        "F1":
            float(
                f1_score(
                    y_true,
                    pred,
                    zero_division=0,
                )
            ),

        "TN":
            int(
                tn
            ),

        "FP":
            int(
                fp
            ),

        "FN":
            int(
                fn
            ),

        "TP":
            int(
                tp
            ),
    }


def metricas_ranking(
    y_true,
    scores,
    k_values,
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


    tabla = (
        tabla
        .sort_values(
            "SCORE",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
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


    for k in k_values:

        k_real = min(
            k,
            len(
                tabla
            ),
        )


        top_k = (
            tabla
            .head(
                k_real
            )
        )


        positivos_top_k = int(
            top_k[
                "TARGET"
            ].sum()
        )


        precision_k = (
            positivos_top_k
            / k_real
        )


        recall_k = (

            positivos_top_k
            / positivos_totales

            if positivos_totales > 0

            else 0.0
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
                        k_real
                    ),

                "POSITIVOS_TOP_K":
                    positivos_top_k,

                "POSITIVOS_TOTALES":
                    positivos_totales,

                "PREVALENCIA":
                    float(
                        prevalencia
                    ),

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
# INICIO
# ============================================================

print(
    "=" * 110
)

print(
    "PROSPECT FINDER BVQ"
)

print(
    "V10-LR - REGRESIÓN LOGÍSTICA BASELINE"
)

print(
    "=" * 110
)


# ============================================================
# VALIDAR ARCHIVO
# ============================================================

if not INPUT_PATH.exists():

    raise FileNotFoundError(
        "No existe el dataset:\n"
        f"{INPUT_PATH}"
    )


RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# CARGAR ÚNICAMENTE TRAIN Y VALIDATION
# ============================================================
#
# TEST existe físicamente en el dataset,
# pero no se incorpora al dataframe de desarrollo.
#
# TEST no será utilizado para:
#
# - entrenamiento;
# - ajuste;
# - selección;
# - predicción;
# - métricas.
#
# ============================================================

print(
    "\nCargando únicamente "
    "TRAIN y VALIDATION..."
)


partes_desarrollo = []

splits_observados = set()

columnas_archivo = None


for chunk in pd.read_csv(

    INPUT_PATH,

    dtype={

        "RUC":
            str,

        "NOMBRE":
            "string",

        "SPLIT":
            str,

        "tipo_compania":
            "string",

        "provincia":
            "string",
    },

    chunksize=150_000,

    low_memory=False,
):


    if columnas_archivo is None:

        columnas_archivo = (
            chunk
            .columns
            .tolist()
        )


        faltantes = [

            columna

            for columna
            in COLUMNAS_REQUERIDAS

            if columna
            not in columnas_archivo
        ]


        if faltantes:

            raise ValueError(
                "Faltan columnas requeridas "
                "en el Feature Set v10:\n"
                f"{faltantes}"
            )


    splits_observados.update(

        chunk[
            "SPLIT"
        ]
        .dropna()
        .unique()
        .tolist()
    )


    desarrollo_chunk = (

        chunk[
            chunk[
                "SPLIT"
            ]
            .isin(
                [
                    "TRAIN",
                    "VALIDATION",
                ]
            )
        ]
        .copy()
    )


    if not desarrollo_chunk.empty:

        partes_desarrollo.append(
            desarrollo_chunk
        )


if not partes_desarrollo:

    raise ValueError(
        "No se encontraron observaciones "
        "de TRAIN o VALIDATION."
    )


df = pd.concat(
    partes_desarrollo,
    ignore_index=True,
)


del partes_desarrollo


print(
    "\nFilas de desarrollo cargadas: "
    f"{len(df):,}"
)


# ============================================================
# VALIDAR SPLITS
# ============================================================

for split_necesario in [
    "TRAIN",
    "VALIDATION",
]:

    if (
        split_necesario
        not in splits_observados
    ):

        raise ValueError(
            "No se encontró el split "
            f"{split_necesario}."
        )


if (
    "TEST"
    not in splits_observados
):

    raise ValueError(
        "No se encontró TEST "
        "en el dataset."
    )


# ============================================================
# NORMALIZAR VARIABLES CATEGÓRICAS
# ============================================================
#
# pandas StringDtype utiliza pd.NA.
#
# SimpleImputer trabaja de forma más estable
# utilizando np.nan.
#
# Por esta razón convertimos explícitamente
# los faltantes categóricos antes del pipeline.
#
# ============================================================

for columna in FEATURES_CATEGORICAS:

    df[
        columna
    ] = (
        df[
            columna
        ]
        .astype(
            object
        )
    )


    df.loc[
        df[
            columna
        ].isna(),
        columna,
    ] = np.nan


# ============================================================
# NORMALIZAR VARIABLES BOOLEANAS
# ============================================================
#
# Se convierten a valores numéricos:
#
# True  -> 1
# False -> 0
#
# Los faltantes, si existieran, permanecen como np.nan.
#
# ============================================================

for columna in FEATURES_BOOLEANAS:

    df[
        columna
    ] = (
        df[
            columna
        ]
        .map(
            {
                True: 1.0,
                False: 0.0,
                1: 1.0,
                0: 0.0,
            }
        )
        .astype(
            float
        )
    )


# ============================================================
# SEPARAR TRAIN Y VALIDATION
# ============================================================

train = (

    df[
        df[
            "SPLIT"
        ]
        == "TRAIN"
    ]
    .copy()
)


validation = (

    df[
        df[
            "SPLIT"
        ]
        == "VALIDATION"
    ]
    .copy()
)


# ============================================================
# VALIDACIONES
# ============================================================

if train.empty:

    raise ValueError(
        "TRAIN está vacío."
    )


if validation.empty:

    raise ValueError(
        "VALIDATION está vacío."
    )


if (
    train[
        TARGET
    ].nunique()
    < 2
):

    raise ValueError(
        "TRAIN no contiene "
        "ambas clases."
    )


if (
    validation[
        TARGET
    ].nunique()
    < 2
):

    raise ValueError(
        "VALIDATION no contiene "
        "ambas clases."
    )


# ============================================================
# INFORMACIÓN DEL SPLIT
# ============================================================

print(
    "\nConjuntos utilizados:"
)


print(
    f"TRAIN       "
    f"{len(train):>10,} | "
    f"positivos: "
    f"{int(train[TARGET].sum()):>4,}"
)


print(
    f"VALIDATION  "
    f"{len(validation):>10,} | "
    f"positivos: "
    f"{int(validation[TARGET].sum()):>4,}"
)


print(
    "\nTEST 2022-2023: "
    "RESERVADO - SIN EVALUACIÓN"
)


print(
    "\nAños observados:"
)


print(
    "TRAIN      : "
    f"{sorted(train['ANIO'].unique().tolist())}"
)


print(
    "VALIDATION : "
    f"{sorted(validation['ANIO'].unique().tolist())}"
)


# ============================================================
# MATRICES
# ============================================================

X_train = (
    train[
        FEATURES
    ]
)


y_train = (
    train[
        TARGET
    ]
    .astype(
        int
    )
)


X_validation = (
    validation[
        FEATURES
    ]
)


y_validation = (
    validation[
        TARGET
    ]
    .astype(
        int
    )
)


# ============================================================
# PREPROCESAMIENTO NUMÉRICO
# ============================================================
#
# La mediana se calcula únicamente con TRAIN.
#
# StandardScaler se ajusta únicamente con TRAIN.
#
# ============================================================

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


# ============================================================
# PREPROCESAMIENTO CATEGÓRICO
# ============================================================
#
# Los faltantes se imputan con la categoría
# más frecuente observada en TRAIN.
#
# OneHotEncoder se aprende únicamente con TRAIN.
#
# handle_unknown="ignore" permite procesar
# categorías nuevas en VALIDATION.
#
# ============================================================

pipeline_categorico = Pipeline(
    steps=[
        (
            "imputer",

            SimpleImputer(
                strategy="most_frequent",
                missing_values=np.nan,
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


# ============================================================
# PREPROCESAMIENTO BOOLEANO
# ============================================================

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


# ============================================================
# PREPROCESADOR GENERAL
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            pipeline_numerico,
            FEATURES_NUMERICAS,
        ),

        (
            "categorical",
            pipeline_categorico,
            FEATURES_CATEGORICAS,
        ),

        (
            "boolean",
            pipeline_booleano,
            FEATURES_BOOLEANAS,
        ),
    ]
)


# ============================================================
# MODELO V10-LR
# ============================================================
#
# Baseline lineal simple.
#
# class_weight="balanced":
# controla el fuerte desbalance.
#
# C=1.0:
# configuración base.
#
# solver="lbfgs":
# optimizador para regresión logística.
#
# ============================================================

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


# ============================================================
# ENTRENAMIENTO
# ============================================================

print(
    "\nEntrenando v10-LR..."
)


pipeline.fit(
    X_train,
    y_train,
)


modelo_entrenado = (
    pipeline
    .named_steps[
        "model"
    ]
)


print(
    "Entrenamiento finalizado."
)


print(
    "Iteraciones utilizadas: "
    f"{modelo_entrenado.n_iter_.tolist()}"
)


# ============================================================
# EVALUACIÓN
# ============================================================
#
# Solo se evalúan:
#
# TRAIN
# VALIDATION
#
# TEST permanece reservado.
#
# ============================================================

datasets_evaluacion = {

    "TRAIN": (
        X_train,
        y_train,
    ),

    "VALIDATION": (
        X_validation,
        y_validation,
    ),
}


metricas_generales = []

ranking_resultados = []


print(
    "\n"
    + "=" * 110
)


print(
    "MÉTRICAS GENERALES"
)


print(
    "=" * 110
)


for nombre_split, (
    X_split,
    y_split,
) in datasets_evaluacion.items():


    scores = (

        pipeline
        .predict_proba(
            X_split
        )[:, 1]
    )


    resultado = (
        metricas_clasificacion(
            y_split,
            scores,
            THRESHOLD,
        )
    )


    resultado[
        "SPLIT"
    ] = nombre_split


    metricas_generales.append(
        resultado
    )


    ranking_split = (
        metricas_ranking(
            y_split,
            scores,
            K_VALUES,
        )
    )


    for fila in ranking_split:

        fila[
            "SPLIT"
        ] = nombre_split

        ranking_resultados.append(
            fila
        )


    print(
        f"\n{nombre_split}"
    )


    print(
        "PR-AUC : "
        f"{resultado['PR_AUC']:.6f}"
    )


    print(
        "ROC-AUC: "
        f"{resultado['ROC_AUC']:.6f}"
    )


# ============================================================
# DATAFRAMES DE RESULTADOS
# ============================================================

metricas_df = pd.DataFrame(
    metricas_generales
)


metricas_df = metricas_df[
    [
        "SPLIT",
        "OBSERVACIONES",
        "POSITIVOS",
        "PREVALENCIA",
        "PR_AUC",
        "ROC_AUC",
        "THRESHOLD",
        "PRECISION",
        "RECALL",
        "F1",
        "TN",
        "FP",
        "FN",
        "TP",
    ]
]


ranking_df = pd.DataFrame(
    ranking_resultados
)


ranking_df = ranking_df[
    [
        "SPLIT",
        "K",
        "POSITIVOS_TOP_K",
        "POSITIVOS_TOTALES",
        "PREVALENCIA",
        "PRECISION_AT_K",
        "RECALL_AT_K",
        "LIFT_AT_K",
    ]
]


# ============================================================
# COEFICIENTES
# ============================================================

feature_names = (

    pipeline
    .named_steps[
        "preprocessor"
    ]
    .get_feature_names_out()
)


coeficientes = (

    pipeline
    .named_steps[
        "model"
    ]
    .coef_[0]
)


coeficientes_df = pd.DataFrame(
    {

        "FEATURE":
            feature_names,

        "COEFICIENTE":
            coeficientes,
    }
)


coeficientes_df[
    "ABS_COEFICIENTE"
] = (

    coeficientes_df[
        "COEFICIENTE"
    ]
    .abs()
)


coeficientes_df = (

    coeficientes_df
    .sort_values(
        "ABS_COEFICIENTE",
        ascending=False,
    )
    .reset_index(
        drop=True
    )
)


# ============================================================
# RANKING VALIDATION TOP 500
# ============================================================

validation_scores = (

    pipeline
    .predict_proba(
        X_validation
    )[:, 1]
)


validation_ranking = (

    validation[
        [
            "ANIO",
            "EXPEDIENTE_KEY",
            "RUC",
            "NOMBRE",
            TARGET,
            "tipo_compania",
            "provincia",
        ]
    ]
    .copy()
)


validation_ranking[
    "SCORE_V10_LR"
] = validation_scores


validation_ranking = (

    validation_ranking
    .sort_values(
        "SCORE_V10_LR",
        ascending=False,
    )
    .reset_index(
        drop=True
    )
)


validation_ranking[
    "RANK"
] = np.arange(
    1,
    len(
        validation_ranking
    )
    + 1,
)


validation_top500 = (

    validation_ranking
    .head(
        500
    )
    .copy()
)


# ============================================================
# GUARDAR RESULTADOS
# ============================================================

metricas_df.to_csv(
    METRICS_PATH,
    index=False,
)


ranking_df.to_csv(
    RANKING_PATH,
    index=False,
)


coeficientes_df.to_csv(
    COEFFICIENTS_PATH,
    index=False,
)


validation_top500.to_csv(
    VALIDATION_TOP_PATH,
    index=False,
)


joblib.dump(
    pipeline,
    MODEL_PATH,
)


# ============================================================
# METADATA
# ============================================================

metadata = {

    "experimento":
        "v10-LR",

    "modelo":
        "LogisticRegression",

    "dataset":
        str(
            INPUT_PATH.relative_to(
                ROOT
            )
        ),

    "descripcion":
        (
            "Baseline lineal de la generación v10 "
            "utilizando el Feature Set Core v10."
        ),

    "target":
        TARGET,

    "features_numericas":
        FEATURES_NUMERICAS,

    "features_categoricas":
        FEATURES_CATEGORICAS,

    "features_booleanas":
        FEATURES_BOOLEANAS,

    "numero_features_fisicas":
        len(
            FEATURES
        ),

    "numero_features_despues_encoding":
        int(
            len(
                feature_names
            )
        ),

    "variables_excluidas_modelo": [
        "ANIO",
        "EXPEDIENTE_KEY",
        "RUC",
        "NOMBRE",
        "SPLIT",
    ],

    "random_state":
        RANDOM_STATE,

    "class_weight":
        "balanced",

    "C":
        1.0,

    "regularizacion":
        "L2",

    "solver":
        "lbfgs",

    "max_iter":
        2000,

    "threshold_evaluacion":
        THRESHOLD,

    "k_ranking":
        K_VALUES,

    "train_anios": [

        int(
            x
        )

        for x
        in sorted(
            train[
                "ANIO"
            ]
            .unique()
            .tolist()
        )
    ],

    "validation_anios": [

        int(
            x
        )

        for x
        in sorted(
            validation[
                "ANIO"
            ]
            .unique()
            .tolist()
        )
    ],

    "train_observaciones":
        int(
            len(
                train
            )
        ),

    "train_positivos":
        int(
            y_train.sum()
        ),

    "validation_observaciones":
        int(
            len(
                validation
            )
        ),

    "validation_positivos":
        int(
            y_validation.sum()
        ),

    "test_evaluado":
        False,

    "test_utilizado_para_fit":
        False,

    "nota_test":
        (
            "TEST 2022-2023 permanece reservado. "
            "v10-LR no genera predicciones, "
            "scores ni métricas sobre TEST."
        ),

    "scores_calibrados":
        False,

    "nota_scores":
        (
            "Los scores se utilizan para ranking "
            "y no deben interpretarse como "
            "probabilidades calibradas."
        ),

    "python_version":
        platform.python_version(),

    "pandas_version":
        pd.__version__,

    "numpy_version":
        np.__version__,

    "scikit_learn_version":
        sklearn.__version__,

    "fecha_ejecucion_utc":
        datetime.now(
            timezone.utc
        ).isoformat(),
}


with open(

    METADATA_PATH,

    "w",

    encoding="utf-8",

) as archivo:


    json.dump(

        metadata,

        archivo,

        indent=4,

        ensure_ascii=False,
    )


# ============================================================
# MOSTRAR RANKING
# ============================================================

print(
    "\n"
    + "=" * 110
)


print(
    "RANKING TOP-K"
)


print(
    "=" * 110
)


print(
    ranking_df.to_string(
        index=False
    )
)


# ============================================================
# FINAL
# ============================================================

print(
    "\n"
    + "=" * 110
)


print(
    "V10-LR COMPLETADO CORRECTAMENTE"
)


print(
    "=" * 110
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
    COEFFICIENTS_PATH
)


print(
    VALIDATION_TOP_PATH
)


print(
    METADATA_PATH
)


print(
    MODEL_PATH
)


print(
    "\nTEST 2022-2023:"
)


print(
    "RESERVADO - NO EVALUADO"
)