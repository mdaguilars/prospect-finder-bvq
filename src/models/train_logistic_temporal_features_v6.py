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
from sklearn.preprocessing import StandardScaler


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

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "logistic_temporal_features_v6.joblib"
)

METRICS_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "baseline_logistic_temporal_features_v6_metrics.csv"
)

RANKING_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "baseline_logistic_temporal_features_v6_ranking_metrics.csv"
)

COEFFICIENTS_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "baseline_logistic_temporal_features_v6_coefficients.csv"
)

METADATA_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "baseline_logistic_temporal_features_v6_metadata.json"
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
# FUNCIONES
# ============================================================

def metricas_clasificacion(
    y_true,
    scores,
    threshold
):

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

        positivos_top = int(
            top_k[
                "TARGET"
            ].sum()
        )

        precision_k = (
            positivos_top
            / k_real
        )

        recall_k = (
            positivos_top
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
                    positivos_top,

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
# 1. CARGAR DATOS
# ============================================================

print("=" * 110)
print("BASELINE V6 - REGRESIÓN LOGÍSTICA CON FEATURES TEMPORALES")
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
    f"\nObservaciones totales: "
    f"{len(df):,}"
)

print(
    f"Positivos totales: "
    f"{int(df[TARGET].sum()):,}"
)


# ============================================================
# 2. VALIDAR VARIABLES
# ============================================================

columnas_requeridas = (
    FEATURES
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
        "Faltan columnas necesarias:\n"
        f"{faltantes}"
    )


# ============================================================
# 3. VALIDAR SPLITS
# ============================================================

splits_esperados = {
    "TRAIN",
    "EMBARGO_VALIDATION",
    "VALIDATION",
    "EMBARGO_TEST",
    "TEST",
}


splits_encontrados = set(
    df[
        "SPLIT"
    ]
    .dropna()
    .unique()
    .tolist()
)


faltan_splits = (
    splits_esperados
    - splits_encontrados
)


if faltan_splits:

    raise ValueError(
        "Faltan splits esperados: "
        f"{sorted(faltan_splits)}"
    )


# ============================================================
# 4. TRAIN Y VALIDATION
# ============================================================

train = df[
    df[
        "SPLIT"
    ]
    == "TRAIN"
].copy()


validation = df[
    df[
        "SPLIT"
    ]
    == "VALIDATION"
].copy()


test_reservado = df[
    df[
        "SPLIT"
    ]
    == "TEST"
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
    f"{len(test_reservado):>10,} | "
    "RESERVADO - SIN EVALUACIÓN"
)


# ============================================================
# 5. VALIDACIONES
# ============================================================

if len(train) == 0:

    raise ValueError(
        "TRAIN está vacío."
    )


if len(validation) == 0:

    raise ValueError(
        "VALIDATION está vacío."
    )


if len(test_reservado) == 0:

    raise ValueError(
        "TEST está vacío."
    )


if train[TARGET].nunique() < 2:

    raise ValueError(
        "TRAIN no contiene ambas clases."
    )


if validation[TARGET].nunique() < 2:

    raise ValueError(
        "VALIDATION no contiene ambas clases."
    )


# ============================================================
# 6. MATRICES
# ============================================================

X_train = train[
    FEATURES
]

y_train = train[
    TARGET
].astype(int)


X_validation = validation[
    FEATURES
]

y_validation = validation[
    TARGET
].astype(int)


# ============================================================
# 7. PREPROCESAMIENTO
# ============================================================

#
# Todos los parámetros del preprocesamiento se aprenden
# exclusivamente utilizando TRAIN.
#
# Las features temporales faltantes se imputan con la
# mediana observada en TRAIN.
#
# TIENE_T_1 permite al modelo distinguir si una fila
# realmente dispone de historia financiera.
#

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


preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            pipeline_numerico,
            FEATURES
        ),
    ]
)


# ============================================================
# 8. MODELO
# ============================================================

#
# El modelo mantiene exactamente la misma configuración
# conceptual que v5.
#
# La modificación principal de v6 es incorporar
# información de evolución financiera t vs t-1.
#
# SECTOR_CIIU continúa excluido.
#

modelo = LogisticRegression(
    C=1.0,
    class_weight="balanced",
    solver="lbfgs",
    max_iter=2000,
    random_state=RANDOM_STATE
)


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
# 9. ENTRENAMIENTO
# ============================================================

print(
    "\nEntrenando Baseline v6..."
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
# 10. EVALUACIÓN
# ============================================================

#
# TEST permanece completamente reservado.
#

datasets_evaluacion = {

    "TRAIN": (
        X_train,
        y_train
    ),

    "VALIDATION": (
        X_validation,
        y_validation
    ),
}


metricas_generales = []

ranking_resultados = []


print(
    "\n" + "=" * 110
)

print(
    "MÉTRICAS GENERALES"
)

print(
    "=" * 110
)


for nombre_split, (
    X_split,
    y_split
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


    ranking_split = (
        metricas_ranking(
            y_split,
            scores,
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

        ranking_resultados.append(
            fila
        )


# ============================================================
# 11. RANKING
# ============================================================

ranking_df = pd.DataFrame(
    ranking_resultados
)


print(
    "\n" + "=" * 110
)

print(
    "MÉTRICAS DE RANKING"
)

print(
    "=" * 110
)


for nombre_split in [
    "TRAIN",
    "VALIDATION",
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
# 12. COEFICIENTES
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
    "15 COEFICIENTES DE MAYOR MAGNITUD"
)

print(
    "=" * 110
)


print(
    coeficientes_df
    .head(
        15
    )
    .to_string(
        index=False
    )
)


# ============================================================
# 13. GUARDAR RESULTADOS
# ============================================================

MODEL_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


METRICS_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


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


coeficientes_df.to_csv(
    COEFFICIENTS_PATH,
    index=False
)


joblib.dump(
    pipeline,
    MODEL_PATH
)


# ============================================================
# 14. METADATOS
# ============================================================

metadata = {

    "experimento":
        "baseline_logistic_temporal_features_v6",

    "modelo":
        "LogisticRegression",

    "descripcion":
        (
            "Regresión logística basada en v5 e incorporando "
            "features de evolución financiera entre t y t-1."
        ),

    "comparacion_principal":
        "Baseline temporal v5 sin sector",

    "random_state":
        RANDOM_STATE,

    "threshold_evaluacion":
        THRESHOLD,

    "class_weight":
        "balanced",

    "regularizacion":
        "L2",

    "C":
        1.0,

    "solver":
        "lbfgs",

    "max_iter":
        2000,

    "features_actuales":
        FEATURES_ACTUALES,

    "features_temporales":
        FEATURES_TEMPORALES,

    "numero_features":
        len(FEATURES),

    "sector_ciiu_utilizado":
        False,

    "definicion_features_temporales":
        (
            "Diferencias entre las variables financieras "
            "del ejercicio t y las de la misma empresa "
            "en el ejercicio t-1."
        ),

    "split_temporal": {

        "train":
            "2015-2018",

        "embargo_validation":
            "2019",

        "validation":
            "2020",

        "embargo_test":
            "2021",

        "test":
            "2022-2023",
    },

    "test_evaluado":
        False,

    "nota_test":
        (
            "TEST 2022-2023 permanece reservado. "
            "No se generan predicciones ni métricas "
            "sobre TEST en v6."
        ),

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

    "scores_calibrados":
        False,

    "nota_calibracion":
        (
            "Los scores del modelo no representan "
            "probabilidades calibradas para el "
            "Índice de Afinidad Bursátil."
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
    "BASELINE V6 ENTRENADO CORRECTAMENTE"
)

print(
    "=" * 110
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


print(
    "\nTEST 2022-2023:"
)

print(
    "RESERVADO - NO EVALUADO EN BASELINE V6"
)