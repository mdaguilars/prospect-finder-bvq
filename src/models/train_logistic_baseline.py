from pathlib import Path
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
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "mvp_features_2015_2023.csv.gz"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "logistic_baseline.joblib"
)

METRICS_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "baseline_logistic_metrics.csv"
)

RANKING_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "baseline_logistic_ranking_metrics.csv"
)

COEFFICIENTS_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "baseline_logistic_coefficients.csv"
)

METADATA_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "baseline_logistic_metadata.json"
)


# ============================================================
# PARÁMETROS REPRODUCIBLES
# ============================================================

RANDOM_STATE = 42

THRESHOLD = 0.50

K_VALUES = [
    50,
    100,
    200,
]


# ============================================================
# VARIABLES DEL MODELO
# ============================================================

FEATURES_NUMERICAS = [
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

FEATURES_CATEGORICAS = [
    "SECTOR_CIIU",
]

TARGET = "TARGET_24M"


# ============================================================
# FUNCIONES
# ============================================================

def metricas_clasificacion(
    y_true,
    probabilidades,
    threshold
):
    """
    Calcula métricas generales del clasificador
    para un umbral determinado.
    """

    predicciones = (
        probabilidades
        >= threshold
    ).astype(int)

    pr_auc = average_precision_score(
        y_true,
        probabilidades
    )

    roc_auc = roc_auc_score(
        y_true,
        probabilidades
    )

    precision = precision_score(
        y_true,
        predicciones,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        predicciones,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        predicciones,
        zero_division=0
    )

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predicciones,
        labels=[0, 1]
    ).ravel()

    return {
        "PR_AUC": pr_auc,
        "ROC_AUC": roc_auc,
        "PRECISION": precision,
        "RECALL": recall,
        "F1": f1,
        "TN": int(tn),
        "FP": int(fp),
        "FN": int(fn),
        "TP": int(tp),
        "THRESHOLD": threshold,
    }


def metricas_ranking(
    y_true,
    probabilidades,
    k_values
):
    """
    Calcula métricas orientadas a priorización comercial.

    Precision@K:
        proporción de emisores reales dentro del Top K.

    Recall@K:
        proporción del total de futuros emisores capturados
        dentro del Top K.

    Lift@K:
        cuántas veces mejora Precision@K respecto de
        seleccionar empresas aleatoriamente.
    """

    temporal = pd.DataFrame(
        {
            "TARGET": np.asarray(
                y_true
            ),
            "PROBABILIDAD": np.asarray(
                probabilidades
            ),
        }
    )

    temporal = (
        temporal
        .sort_values(
            "PROBABILIDAD",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )

    positivos_totales = int(
        temporal[
            "TARGET"
        ].sum()
    )

    prevalencia = (
        positivos_totales
        / len(temporal)
    )

    resultados = []

    for k in k_values:

        k_real = min(
            k,
            len(temporal)
        )

        top_k = temporal.head(
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

        if positivos_totales > 0:

            recall_k = (
                positivos_top_k
                / positivos_totales
            )

        else:

            recall_k = 0.0

        if prevalencia > 0:

            lift_k = (
                precision_k
                / prevalencia
            )

        else:

            lift_k = np.nan

        resultados.append(
            {
                "K": k_real,
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
# CARGAR DATASET
# ============================================================

print("=" * 110)
print("REGRESIÓN LOGÍSTICA BASELINE")
print("=" * 110)


if not INPUT_PATH.exists():

    raise FileNotFoundError(
        f"No existe el dataset:\n{INPUT_PATH}"
    )


df = pd.read_csv(
    INPUT_PATH,
    dtype={
        "RUC": str,
        "CIIU": str,
        "SECTOR_CIIU": str,
        "SPLIT": str,
    },
    low_memory=False
)


print(
    f"\nObservaciones: "
    f"{len(df):,}"
)

print(
    f"Positivos totales: "
    f"{int(df[TARGET].sum()):,}"
)


# ============================================================
# VALIDAR VARIABLES
# ============================================================

features = (
    FEATURES_NUMERICAS
    + FEATURES_CATEGORICAS
)


columnas_requeridas = (
    features
    + [
        TARGET,
        "SPLIT",
    ]
)


faltantes = [
    columna
    for columna in columnas_requeridas
    if columna not in df.columns
]


if faltantes:

    raise ValueError(
        "Faltan columnas necesarias para "
        "el entrenamiento:\n"
        f"{faltantes}"
    )


# ============================================================
# SPLIT TEMPORAL
# ============================================================

train = df[
    df["SPLIT"] == "TRAIN"
].copy()


validation = df[
    df["SPLIT"] == "VALIDATION"
].copy()


test = df[
    df["SPLIT"] == "TEST"
].copy()


print(
    "\nSplit temporal:"
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
    f"TEST        "
    f"{len(test):>10,} | "
    f"positivos: "
    f"{int(test[TARGET].sum()):>4,}"
)


# ============================================================
# VALIDAR SPLIT
# ============================================================

if len(train) == 0:
    raise ValueError(
        "TRAIN está vacío."
    )


if len(validation) == 0:
    raise ValueError(
        "VALIDATION está vacío."
    )


if len(test) == 0:
    raise ValueError(
        "TEST está vacío."
    )


# ============================================================
# MATRICES DEL MODELO
# ============================================================

X_train = train[
    features
]

y_train = train[
    TARGET
].astype(int)


X_validation = validation[
    features
]

y_validation = validation[
    TARGET
].astype(int)


X_test = test[
    features
]

y_test = test[
    TARGET
].astype(int)


# ============================================================
# PREPROCESAMIENTO NUMÉRICO
# ============================================================
#
# Los valores faltantes se imputan con la mediana calculada
# EXCLUSIVAMENTE sobre TRAIN.
#
# StandardScaler también se ajusta únicamente sobre TRAIN.
#
# Esto evita contaminación temporal.
# ============================================================

pipeline_numerico = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
        ),
        (
            "scaler",
            StandardScaler()
        ),
    ]
)


# ============================================================
# PREPROCESAMIENTO CATEGÓRICO
# ============================================================
#
# SECTOR_CIIU se imputa y codifica usando One-Hot Encoding.
#
# handle_unknown="ignore" permite evaluar sectores que
# eventualmente no aparezcan en TRAIN.
# ============================================================

pipeline_categorico = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore"
            )
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
            FEATURES_NUMERICAS
        ),
        (
            "categorical",
            pipeline_categorico,
            FEATURES_CATEGORICAS
        ),
    ]
)


# ============================================================
# MODELO BASELINE
# ============================================================
#
# Regresión logística regularizada L2.
#
# class_weight="balanced":
# utilizado debido al desbalance extremo del target.
#
# C=1.0:
# valor inicial del baseline. No se ha realizado tuning.
#
# IMPORTANTE:
# predict_proba() no se interpretará todavía como una
# probabilidad calibrada para construir el IAB.
# ============================================================

modelo = LogisticRegression(
    penalty="l2",
    C=1.0,
    class_weight="balanced",
    solver="lbfgs",
    max_iter=2000,
    random_state=RANDOM_STATE
)


# ============================================================
# PIPELINE COMPLETO
# ============================================================

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            modelo
        ),
    ]
)


# ============================================================
# ENTRENAMIENTO
# ============================================================

print(
    "\nEntrenando regresión logística..."
)


pipeline.fit(
    X_train,
    y_train
)


modelo_entrenado = (
    pipeline.named_steps[
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

datasets_evaluacion = {
    "TRAIN": (
        X_train,
        y_train
    ),
    "VALIDATION": (
        X_validation,
        y_validation
    ),
    "TEST": (
        X_test,
        y_test
    ),
}


metricas_generales = []
metricas_ranking_resultados = []


print(
    "\n" + "=" * 110
)

print(
    "MÉTRICAS GENERALES"
)

print("=" * 110)


for nombre_split, (
    X_split,
    y_split
) in datasets_evaluacion.items():

    probabilidades = (
        pipeline.predict_proba(
            X_split
        )[:, 1]
    )

    resultado = (
        metricas_clasificacion(
            y_split,
            probabilidades,
            THRESHOLD
        )
    )

    resultado[
        "SPLIT"
    ] = nombre_split

    resultado[
        "OBSERVACIONES"
    ] = len(
        y_split
    )

    resultado[
        "POSITIVOS"
    ] = int(
        y_split.sum()
    )

    resultado[
        "PREVALENCIA"
    ] = float(
        y_split.mean()
    )

    metricas_generales.append(
        resultado
    )

    print(
        f"\n{nombre_split}"
    )

    print(
        f"  Observaciones: "
        f"{len(y_split):,}"
    )

    print(
        f"  Positivos:     "
        f"{int(y_split.sum()):,}"
    )

    print(
        f"  Prevalencia:   "
        f"{100 * y_split.mean():.4f}%"
    )

    print(
        f"  PR-AUC:        "
        f"{resultado['PR_AUC']:.6f}"
    )

    print(
        f"  ROC-AUC:       "
        f"{resultado['ROC_AUC']:.6f}"
    )

    print(
        f"  Precision:     "
        f"{resultado['PRECISION']:.6f}"
    )

    print(
        f"  Recall:        "
        f"{resultado['RECALL']:.6f}"
    )

    print(
        f"  F1:            "
        f"{resultado['F1']:.6f}"
    )

    print(
        "  Matriz:        "
        f"TN={resultado['TN']:,} | "
        f"FP={resultado['FP']:,} | "
        f"FN={resultado['FN']:,} | "
        f"TP={resultado['TP']:,}"
    )


    # ========================================================
    # MÉTRICAS DE RANKING
    # ========================================================

    ranking_split = (
        metricas_ranking(
            y_split,
            probabilidades,
            K_VALUES
        )
    )

    for fila in ranking_split:

        fila[
            "SPLIT"
        ] = nombre_split

        fila[
            "POSITIVOS_TOTALES"
        ] = int(
            y_split.sum()
        )

        fila[
            "PREVALENCIA"
        ] = float(
            y_split.mean()
        )

        metricas_ranking_resultados.append(
            fila
        )


# ============================================================
# MOSTRAR MÉTRICAS DE RANKING
# ============================================================

ranking_df = pd.DataFrame(
    metricas_ranking_resultados
)


print(
    "\n" + "=" * 110
)

print(
    "MÉTRICAS DE RANKING"
)

print("=" * 110)


for nombre_split in [
    "TRAIN",
    "VALIDATION",
    "TEST",
]:

    print(
        f"\n{nombre_split}"
    )

    bloque = ranking_df[
        ranking_df[
            "SPLIT"
        ]
        == nombre_split
    ]

    for _, fila in bloque.iterrows():

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
# COEFICIENTES DEL MODELO
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
        "ABS_COEFICIENTE":
            np.abs(
                coeficientes
            ),
    }
)


coeficientes_df = (
    coeficientes_df
    .sort_values(
        "ABS_COEFICIENTE",
        ascending=False
    )
    .reset_index(
        drop=True
    )
)


print(
    "\n" + "=" * 110
)

print(
    "10 COEFICIENTES DE MAYOR MAGNITUD"
)

print("=" * 110)


print(
    coeficientes_df.head(
        10
    ).to_string(
        index=False
    )
)


# ============================================================
# CREAR DIRECTORIOS
# ============================================================

MODEL_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

METRICS_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# GUARDAR MÉTRICAS GENERALES
# ============================================================

metricas_df = pd.DataFrame(
    metricas_generales
)


orden_columnas_metricas = [
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


metricas_df = metricas_df[
    orden_columnas_metricas
]


metricas_df.to_csv(
    METRICS_PATH,
    index=False
)


# ============================================================
# GUARDAR MÉTRICAS DE RANKING
# ============================================================

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


ranking_df.to_csv(
    RANKING_PATH,
    index=False
)


# ============================================================
# GUARDAR COEFICIENTES
# ============================================================

coeficientes_df.to_csv(
    COEFFICIENTS_PATH,
    index=False
)


# ============================================================
# GUARDAR MODELO
# ============================================================

joblib.dump(
    pipeline,
    MODEL_PATH
)


# ============================================================
# METADATOS REPRODUCIBLES DEL EXPERIMENTO
# ============================================================

metadata = {
    "modelo":
        "LogisticRegression",

    "descripcion":
        "Baseline interpretable para TARGET_24M",

    "random_state":
        RANDOM_STATE,

    "threshold_evaluacion":
        THRESHOLD,

    "class_weight":
        "balanced",

    "penalty":
        "l2",

    "C":
        1.0,

    "solver":
        "lbfgs",

    "max_iter":
        2000,

    "features_numericas":
        FEATURES_NUMERICAS,

    "features_categoricas":
        FEATURES_CATEGORICAS,

    "split_temporal": {
        "train":
            "2015-2020",
        "validation":
            "2021",
        "test":
            "2022-2023",
    },

    "k_ranking":
        K_VALUES,

    "python_version":
        platform.python_version(),

    "pandas_version":
        pd.__version__,

    "numpy_version":
        np.__version__,

    "scikit_learn_version":
        sklearn.__version__,

    "probabilidades_calibradas":
        False,

    "nota_calibracion":
        (
            "El uso de class_weight='balanced' implica que "
            "las salidas de predict_proba no deben "
            "interpretarse todavía como probabilidades "
            "calibradas para el Índice de Afinidad Bursátil."
        ),
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
    "BASELINE ENTRENADO CORRECTAMENTE"
)

print("=" * 110)


print(
    "\nModelo:"
)

print(
    MODEL_PATH
)


print(
    "\nMétricas:"
)

print(
    METRICS_PATH
)


print(
    "\nRanking:"
)

print(
    RANKING_PATH
)


print(
    "\nCoeficientes:"
)

print(
    COEFFICIENTS_PATH
)


print(
    "\nMetadatos:"
)

print(
    METADATA_PATH
)