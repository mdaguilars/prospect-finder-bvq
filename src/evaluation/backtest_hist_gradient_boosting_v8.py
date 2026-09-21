from pathlib import Path
import json
import platform

import numpy as np
import pandas as pd
import sklearn

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "mvp_features_temporal_v6.csv.gz"
)

METRICS_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "backtest_hist_gradient_boosting_v8_metrics.csv"
)

RANKING_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "backtest_hist_gradient_boosting_v8_ranking_metrics.csv"
)

SUMMARY_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "backtest_hist_gradient_boosting_v8_summary.csv"
)

METADATA_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "backtest_hist_gradient_boosting_v8_metadata.json"
)


# ============================================================
# PARÁMETROS
# ============================================================

RANDOM_STATE = 42
THRESHOLD = 0.50

K_VALUES = [
    50,
    100,
    200,
]


# ============================================================
# FEATURES FINANCIERAS ACTUALES
# ============================================================

FEATURES_ACTUALES = [
    "LOG_ACTIVO_TOTAL",
    "LOG_ACTIVO_CORRIENTE",
    "LOG_EFECTIVO",
    "LOG_PASIVO_TOTAL",
    "LOG_PASIVO_CORRIENTE",
    "LOG_PASIVO_NO_CORRIENTE",
    "LOG_PATRIMONIO",
    "LOG_CAPITAL",
    "LOG_UTILIDAD_NETA",
    "LIQUIDEZ_CORRIENTE",
    "ENDEUDAMIENTO",
    "AUTONOMIA_FINANCIERA",
    "ROA",
    "EFECTIVO_ACTIVOS",
    "CAPITAL_ACTIVOS",
    "PASIVO_CORRIENTE_PASIVO",
]


# ============================================================
# FEATURES TEMPORALES
# ============================================================

FEATURES_TEMPORALES = [
    "DELTA_LOG_ACTIVO_TOTAL",
    "DELTA_LOG_ACTIVO_CORRIENTE",
    "DELTA_LOG_EFECTIVO",
    "DELTA_LOG_PASIVO_TOTAL",
    "DELTA_LOG_PASIVO_CORRIENTE",
    "DELTA_LOG_PASIVO_NO_CORRIENTE",
    "DELTA_LOG_PATRIMONIO",
    "DELTA_LOG_CAPITAL",
    "DELTA_LOG_UTILIDAD_NETA",
    "DELTA_LIQUIDEZ_CORRIENTE",
    "DELTA_ENDEUDAMIENTO",
    "DELTA_AUTONOMIA_FINANCIERA",
    "DELTA_ROA",
    "DELTA_EFECTIVO_ACTIVOS",
    "DELTA_CAPITAL_ACTIVOS",
    "DELTA_PASIVO_CORRIENTE_PASIVO",
    "TIENE_T_1",
]


FEATURES = (
    FEATURES_ACTUALES
    + FEATURES_TEMPORALES
)

TARGET = "TARGET_24M"


# ============================================================
# FOLDS TEMPORALES
# ============================================================

#
# Regla de disponibilidad:
#
# Para una observación financiera del año t:
#
#   decisión del modelo: 01/05/t+1
#   target observable hasta: 30/04/t+3
#
# Por tanto, al evaluar un determinado año, solo pueden
# utilizarse como TRAIN ejercicios cuyos targets de 24 meses
# ya habrían terminado en esa fecha.
#
# Ejemplo:
#
# Evaluación 2020 -> decisión 01/05/2021
#
# El target de 2018 termina el 30/04/2021.
# El target de 2019 termina el 30/04/2022.
#
# Entonces TRAIN puede llegar únicamente hasta 2018.
#

FOLDS = [
    {
        "FOLD": 1,
        "TRAIN_INICIO": 2015,
        "TRAIN_FIN": 2016,
        "ANIO_EVALUACION": 2018,
        "ANIO_EMBARGO": 2017,
    },
    {
        "FOLD": 2,
        "TRAIN_INICIO": 2015,
        "TRAIN_FIN": 2017,
        "ANIO_EVALUACION": 2019,
        "ANIO_EMBARGO": 2018,
    },
    {
        "FOLD": 3,
        "TRAIN_INICIO": 2015,
        "TRAIN_FIN": 2018,
        "ANIO_EVALUACION": 2020,
        "ANIO_EMBARGO": 2019,
    },
]


# ============================================================
# FUNCIONES
# ============================================================

def crear_modelo():
    """
    Crea exactamente la configuración regularizada de v8.
    """

    return HistGradientBoostingClassifier(
        loss="log_loss",
        learning_rate=0.05,
        max_iter=150,
        max_leaf_nodes=7,
        max_depth=3,
        min_samples_leaf=100,
        l2_regularization=1.0,
        early_stopping=False,
        random_state=RANDOM_STATE,
        class_weight="balanced",
    )


def metricas_clasificacion(
    y_true,
    scores,
    threshold
):
    """
    Calcula métricas generales.

    predict_proba se utiliza como score de ranking.
    No se interpreta como probabilidad calibrada.
    """

    predicciones = (
        scores >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predicciones,
        labels=[0, 1]
    ).ravel()

    return {
        "PR_AUC":
            average_precision_score(
                y_true,
                scores
            ),

        "ROC_AUC":
            roc_auc_score(
                y_true,
                scores
            ),

        "PRECISION":
            precision_score(
                y_true,
                predicciones,
                zero_division=0
            ),

        "RECALL":
            recall_score(
                y_true,
                predicciones,
                zero_division=0
            ),

        "F1":
            f1_score(
                y_true,
                predicciones,
                zero_division=0
            ),

        "TN":
            int(tn),

        "FP":
            int(fp),

        "FN":
            int(fn),

        "TP":
            int(tp),

        "THRESHOLD":
            threshold,
    }


def metricas_ranking(
    y_true,
    scores,
    k_values
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

    tabla = (
        tabla
        .sort_values(
            "SCORE",
            ascending=False
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
        / len(tabla)
    )

    resultados = []

    for k in k_values:

        k_real = min(
            k,
            len(tabla)
        )

        top_k = tabla.head(
            k_real
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
                    k_real,

                "POSITIVOS_TOP_K":
                    positivos_top_k,

                "PRECISION_AT_K":
                    precision_k,

                "RECALL_AT_K":
                    recall_k,

                "LIFT_AT_K":
                    lift_k,
            }
        )

    return resultados


# ============================================================
# 1. CARGAR DATASET
# ============================================================

print("=" * 110)
print("BACKTEST TEMPORAL - HIST GRADIENT BOOSTING V8")
print("=" * 110)


if not INPUT_PATH.exists():

    raise FileNotFoundError(
        f"No existe:\n{INPUT_PATH}"
    )


df = pd.read_csv(
    INPUT_PATH,
    dtype={
        "RUC": str,
        "SPLIT": str,
    },
    low_memory=False
)


print(
    f"\nObservaciones dataset completo: "
    f"{len(df):,}"
)

print(
    f"Positivos dataset completo: "
    f"{int(df[TARGET].sum()):,}"
)


# ============================================================
# 2. VALIDAR COLUMNAS
# ============================================================

columnas_requeridas = (
    FEATURES
    + [
        TARGET,
        "ANIO",
    ]
)


faltantes = [
    columna
    for columna in columnas_requeridas
    if columna not in df.columns
]


if faltantes:

    raise ValueError(
        "Faltan columnas necesarias:\n"
        f"{faltantes}"
    )


# ============================================================
# 3. NORMALIZAR TIPOS
# ============================================================

df[
    "ANIO"
] = pd.to_numeric(
    df[
        "ANIO"
    ],
    errors="raise"
).astype(int)


for variable in FEATURES:

    df[
        variable
    ] = pd.to_numeric(
        df[
            variable
        ],
        errors="coerce"
    )


df[
    FEATURES
] = df[
    FEATURES
].replace(
    [
        np.inf,
        -np.inf,
    ],
    np.nan
)


# ============================================================
# 4. AISLAR UNIVERSO DEL BACKTEST
# ============================================================

#
# Ninguna observación de 2021, 2022 o 2023 se utilizará
# en este ejercicio.
#

df_backtest = df[
    df[
        "ANIO"
    ]
    <= 2020
].copy()


if (
    df_backtest[
        "ANIO"
    ].max()
    > 2020
):

    raise ValueError(
        "El backtest contiene datos posteriores a 2020."
    )


print(
    f"\nObservaciones disponibles para backtest "
    f"2015-2020: {len(df_backtest):,}"
)


# ============================================================
# 5. EJECUTAR FOLDS
# ============================================================

metricas_resultados = []
ranking_resultados = []


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

    anio_evaluacion = fold[
        "ANIO_EVALUACION"
    ]

    anio_embargo = fold[
        "ANIO_EMBARGO"
    ]


    print(
        "\n" + "=" * 110
    )

    print(
        f"FOLD {numero_fold}"
    )

    print(
        "=" * 110
    )


    print(
        f"TRAIN:      "
        f"{train_inicio}-{train_fin}"
    )

    print(
        f"EMBARGO:    "
        f"{anio_embargo}"
    )

    print(
        f"EVALUACIÓN: "
        f"{anio_evaluacion}"
    )


    # ========================================================
    # TRAIN
    # ========================================================

    train = df_backtest[
        (
            df_backtest[
                "ANIO"
            ]
            >= train_inicio
        )
        &
        (
            df_backtest[
                "ANIO"
            ]
            <= train_fin
        )
    ].copy()


    # ========================================================
    # EVALUACIÓN
    # ========================================================

    evaluacion = df_backtest[
        df_backtest[
            "ANIO"
        ]
        == anio_evaluacion
    ].copy()


    # ========================================================
    # VALIDACIONES TEMPORALES
    # ========================================================

    if len(train) == 0:

        raise ValueError(
            f"TRAIN vacío en fold {numero_fold}."
        )


    if len(evaluacion) == 0:

        raise ValueError(
            f"Evaluación vacía en fold {numero_fold}."
        )


    if (
        train[
            "ANIO"
        ].max()
        != train_fin
    ):

        raise ValueError(
            f"TRAIN_FIN incorrecto en fold {numero_fold}."
        )


    if (
        evaluacion[
            "ANIO"
        ].nunique()
        != 1
    ):

        raise ValueError(
            f"Evaluación contiene más de un año "
            f"en fold {numero_fold}."
        )


    if (
        evaluacion[
            "ANIO"
        ].iloc[0]
        != anio_evaluacion
    ):

        raise ValueError(
            f"Año de evaluación incorrecto "
            f"en fold {numero_fold}."
        )


    if train[TARGET].nunique() < 2:

        raise ValueError(
            f"TRAIN no contiene ambas clases "
            f"en fold {numero_fold}."
        )


    if evaluacion[TARGET].nunique() < 2:

        raise ValueError(
            f"Evaluación no contiene ambas clases "
            f"en fold {numero_fold}."
        )


    print(
        f"\nTRAIN observaciones: "
        f"{len(train):,}"
    )

    print(
        f"TRAIN positivos:     "
        f"{int(train[TARGET].sum()):,}"
    )

    print(
        f"EVALUACIÓN obs.:     "
        f"{len(evaluacion):,}"
    )

    print(
        f"EVALUACIÓN positivos:"
        f" {int(evaluacion[TARGET].sum()):,}"
    )


    # ========================================================
    # MATRICES
    # ========================================================

    X_train = train[
        FEATURES
    ].copy()


    y_train = train[
        TARGET
    ].astype(int)


    X_eval = evaluacion[
        FEATURES
    ].copy()


    y_eval = evaluacion[
        TARGET
    ].astype(int)


    # ========================================================
    # MODELO
    # ========================================================

    modelo = crear_modelo()


    print(
        "\nEntrenando modelo..."
    )


    modelo.fit(
        X_train,
        y_train
    )


    print(
        "Entrenamiento finalizado."
    )

    print(
        "Iteraciones utilizadas: "
        f"{modelo.n_iter_}"
    )


    # ========================================================
    # SCORE ÚNICAMENTE DEL AÑO DE EVALUACIÓN
    # ========================================================

    scores = (
        modelo.predict_proba(
            X_eval
        )[:, 1]
    )


    # ========================================================
    # MÉTRICAS GENERALES
    # ========================================================

    resultado = metricas_clasificacion(
        y_eval,
        scores,
        THRESHOLD
    )


    resultado.update(
        {
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

            "OBS_TRAIN":
                len(train),

            "POSITIVOS_TRAIN":
                int(
                    y_train.sum()
                ),

            "OBS_EVALUACION":
                len(evaluacion),

            "POSITIVOS_EVALUACION":
                int(
                    y_eval.sum()
                ),

            "PREVALENCIA_EVALUACION":
                float(
                    y_eval.mean()
                ),
        }
    )


    metricas_resultados.append(
        resultado
    )


    print(
        "\nMétricas:"
    )

    print(
        f"  Prevalencia: "
        f"{100 * y_eval.mean():.4f}%"
    )

    print(
        f"  PR-AUC:      "
        f"{resultado['PR_AUC']:.6f}"
    )

    print(
        f"  ROC-AUC:     "
        f"{resultado['ROC_AUC']:.6f}"
    )

    print(
        f"  Precision:   "
        f"{resultado['PRECISION']:.6f}"
    )

    print(
        f"  Recall:      "
        f"{resultado['RECALL']:.6f}"
    )

    print(
        f"  F1:          "
        f"{resultado['F1']:.6f}"
    )


    # ========================================================
    # RANKING
    # ========================================================

    ranking_fold = metricas_ranking(
        y_eval,
        scores,
        K_VALUES
    )


    print(
        "\nRanking:"
    )


    for fila in ranking_fold:

        fila.update(
            {
                "FOLD":
                    numero_fold,

                "TRAIN_INICIO":
                    train_inicio,

                "TRAIN_FIN":
                    train_fin,

                "ANIO_EVALUACION":
                    anio_evaluacion,

                "POSITIVOS_TOTALES":
                    int(
                        y_eval.sum()
                    ),

                "PREVALENCIA":
                    float(
                        y_eval.mean()
                    ),
            }
        )


        ranking_resultados.append(
            fila
        )


        print(
            f"  K={int(fila['K']):>3} | "
            f"Positivos="
            f"{int(fila['POSITIVOS_TOP_K']):>3} | "
            f"Precision@K="
            f"{fila['PRECISION_AT_K']:.4f} | "
            f"Recall@K="
            f"{fila['RECALL_AT_K']:.4f} | "
            f"Lift@K="
            f"{fila['LIFT_AT_K']:.2f}"
        )


# ============================================================
# 6. DATAFRAMES DE RESULTADOS
# ============================================================

metricas_df = pd.DataFrame(
    metricas_resultados
)


metricas_df = metricas_df[
    [
        "FOLD",
        "TRAIN_INICIO",
        "TRAIN_FIN",
        "ANIO_EMBARGO",
        "ANIO_EVALUACION",
        "OBS_TRAIN",
        "POSITIVOS_TRAIN",
        "OBS_EVALUACION",
        "POSITIVOS_EVALUACION",
        "PREVALENCIA_EVALUACION",
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
        "FOLD",
        "TRAIN_INICIO",
        "TRAIN_FIN",
        "ANIO_EVALUACION",
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
# 7. RESUMEN DE ESTABILIDAD
# ============================================================

resumen_general = pd.DataFrame(
    [
        {
            "METRICA":
                "PR_AUC",

            "PROMEDIO":
                metricas_df[
                    "PR_AUC"
                ].mean(),

            "MEDIANA":
                metricas_df[
                    "PR_AUC"
                ].median(),

            "MINIMO":
                metricas_df[
                    "PR_AUC"
                ].min(),

            "MAXIMO":
                metricas_df[
                    "PR_AUC"
                ].max(),
        },

        {
            "METRICA":
                "ROC_AUC",

            "PROMEDIO":
                metricas_df[
                    "ROC_AUC"
                ].mean(),

            "MEDIANA":
                metricas_df[
                    "ROC_AUC"
                ].median(),

            "MINIMO":
                metricas_df[
                    "ROC_AUC"
                ].min(),

            "MAXIMO":
                metricas_df[
                    "ROC_AUC"
                ].max(),
        },
    ]
)


for k in K_VALUES:

    bloque_k = ranking_df[
        ranking_df[
            "K"
        ]
        == k
    ]


    resumen_k = pd.DataFrame(
        [
            {
                "METRICA":
                    f"POSITIVOS_TOP_{k}",

                "PROMEDIO":
                    bloque_k[
                        "POSITIVOS_TOP_K"
                    ].mean(),

                "MEDIANA":
                    bloque_k[
                        "POSITIVOS_TOP_K"
                    ].median(),

                "MINIMO":
                    bloque_k[
                        "POSITIVOS_TOP_K"
                    ].min(),

                "MAXIMO":
                    bloque_k[
                        "POSITIVOS_TOP_K"
                    ].max(),
            },

            {
                "METRICA":
                    f"LIFT_AT_{k}",

                "PROMEDIO":
                    bloque_k[
                        "LIFT_AT_K"
                    ].mean(),

                "MEDIANA":
                    bloque_k[
                        "LIFT_AT_K"
                    ].median(),

                "MINIMO":
                    bloque_k[
                        "LIFT_AT_K"
                    ].min(),

                "MAXIMO":
                    bloque_k[
                        "LIFT_AT_K"
                    ].max(),
            },
        ]
    )


    resumen_general = pd.concat(
        [
            resumen_general,
            resumen_k,
        ],
        ignore_index=True
    )


# ============================================================
# 8. MOSTRAR RESUMEN
# ============================================================

print(
    "\n" + "=" * 110
)

print(
    "RESUMEN DEL BACKTEST"
)

print(
    "=" * 110
)


for _, fila in metricas_df.iterrows():

    print(
        f"\nAño {int(fila['ANIO_EVALUACION'])}"
    )

    print(
        f"  PR-AUC:  "
        f"{fila['PR_AUC']:.6f}"
    )

    print(
        f"  ROC-AUC: "
        f"{fila['ROC_AUC']:.6f}"
    )


    ranking_anio = ranking_df[
        ranking_df[
            "ANIO_EVALUACION"
        ]
        == fila[
            "ANIO_EVALUACION"
        ]
    ]


    for _, ranking_fila in ranking_anio.iterrows():

        print(
            f"  Top {int(ranking_fila['K']):>3}: "
            f"{int(ranking_fila['POSITIVOS_TOP_K'])} positivos | "
            f"Lift="
            f"{ranking_fila['LIFT_AT_K']:.2f}"
        )


print(
    "\nPromedio PR-AUC: "
    f"{metricas_df['PR_AUC'].mean():.6f}"
)

print(
    "Mediana PR-AUC:  "
    f"{metricas_df['PR_AUC'].median():.6f}"
)


# ============================================================
# 9. GUARDAR RESULTADOS
# ============================================================

METRICS_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


metricas_df.to_csv(
    METRICS_PATH,
    index=False
)


ranking_df.to_csv(
    RANKING_PATH,
    index=False
)


resumen_general.to_csv(
    SUMMARY_PATH,
    index=False
)


# ============================================================
# 10. METADATOS
# ============================================================

metadata = {

    "experimento":
        "backtest_hist_gradient_boosting_v8",

    "objetivo":
        (
            "Evaluar la estabilidad temporal de la "
            "configuración v8 mediante múltiples cortes "
            "históricos sin utilizar información cuyo "
            "target aún no habría madurado."
        ),

    "modelo":
        "HistGradientBoostingClassifier",

    "configuracion_modelo": {
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

        "class_weight":
            "balanced",

        "early_stopping":
            False,

        "random_state":
            RANDOM_STATE,
    },

    "numero_features":
        len(FEATURES),

    "features_actuales":
        FEATURES_ACTUALES,

    "features_temporales":
        FEATURES_TEMPORALES,

    "folds":
        FOLDS,

    "regla_disponibilidad_target":
        (
            "Para el ejercicio financiero t se asume "
            "disponibilidad ordinaria desde 01/05/t+1. "
            "TARGET_24M cubre hasta 30/04/t+3. "
            "Cada fold entrena únicamente con años cuyo "
            "horizonte objetivo completo habría sido "
            "observable al momento de la evaluación."
        ),

    "anio_maximo_utilizado":
        2020,

    "anios_no_utilizados":
        [
            2021,
            2022,
            2023,
        ],

    "test_2022_2023_evaluado":
        False,

    "nota_test":
        (
            "TEST 2022-2023 permanece reservado. "
            "No se generan scores, predicciones ni métricas "
            "sobre esos años durante este backtest."
        ),

    "scores_calibrados":
        False,

    "nota_calibracion":
        (
            "predict_proba se utiliza únicamente como score "
            "de ordenamiento. No representa una probabilidad "
            "calibrada del Índice de Afinidad Bursátil."
        ),

    "python_version":
        platform.python_version(),

    "pandas_version":
        pd.__version__,

    "numpy_version":
        np.__version__,

    "scikit_learn_version":
        sklearn.__version__,
}


with open(
    METADATA_PATH,
    "w",
    encoding="utf-8"
) as archivo:

    json.dump(
        metadata,
        archivo,
        indent=4,
        ensure_ascii=False
    )


# ============================================================
# FINAL
# ============================================================

print(
    "\n" + "=" * 110
)

print(
    "BACKTEST TEMPORAL V8 FINALIZADO CORRECTAMENTE"
)

print(
    "=" * 110
)


print(
    "\nMétricas por fold:"
)

print(
    METRICS_PATH
)


print(
    "\nRanking por fold:"
)

print(
    RANKING_PATH
)


print(
    "\nResumen:"
)

print(
    SUMMARY_PATH
)


print(
    "\nMetadatos:"
)

print(
    METADATA_PATH
)


print(
    "\nAños 2021-2023:"
)

print(
    "NO UTILIZADOS"
)


print(
    "\nTEST 2022-2023:"
)

print(
    "RESERVADO - NO EVALUADO"
)