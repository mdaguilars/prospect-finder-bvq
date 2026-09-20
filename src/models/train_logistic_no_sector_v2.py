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
    / "mvp_features_2015_2023.csv.gz"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "logistic_no_sector_v2.joblib"
)

METRICS_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "logistic_no_sector_v2_metrics_train_validation.csv"
)

RANKING_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "logistic_no_sector_v2_ranking_train_validation.csv"
)

COEFFICIENTS_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "logistic_no_sector_v2_coefficients.csv"
)

METADATA_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "logistic_no_sector_v2_metadata.json"
)


RANDOM_STATE = 42
THRESHOLD = 0.50

K_VALUES = [
    50,
    100,
    200,
]


# ============================================================
# VARIABLES
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

TARGET = "TARGET_24M"


# ============================================================
# FUNCIONES
# ============================================================

def metricas_clasificacion(
    y_true,
    probabilidades,
    threshold
):

    predicciones = (
        probabilidades
        >= threshold
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
                probabilidades
            ),

        "ROC_AUC":
            roc_auc_score(
                y_true,
                probabilidades
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

        "TN": int(tn),
        "FP": int(fp),
        "FN": int(fn),
        "TP": int(tp),

        "THRESHOLD":
            threshold,
    }


def metricas_ranking(
    y_true,
    probabilidades,
    k_values
):

    tabla = pd.DataFrame(
        {
            "TARGET":
                np.asarray(y_true),

            "PROBABILIDAD":
                np.asarray(probabilidades),
        }
    )

    tabla = (
        tabla
        .sort_values(
            "PROBABILIDAD",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )

    positivos_totales = int(
        tabla["TARGET"].sum()
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
# CARGAR DATOS
# ============================================================

print("=" * 110)
print("BASELINE V2 — REGRESIÓN LOGÍSTICA SIN SECTOR CIIU")
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
    f"Positivos totales disponibles: "
    f"{int(df[TARGET].sum()):,}"
)


# ============================================================
# VALIDAR VARIABLES
# ============================================================

columnas_requeridas = (
    FEATURES_NUMERICAS
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
        "Faltan columnas necesarias: "
        f"{faltantes}"
    )


# ============================================================
# SPLITS
# ============================================================

train = df[
    df["SPLIT"]
    == "TRAIN"
].copy()


validation = df[
    df["SPLIT"]
    == "VALIDATION"
].copy()


print(
    "\nConjuntos utilizados en esta etapa:"
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
    "\nTEST NO SE EVALÚA EN ESTE EXPERIMENTO "
    "DURANTE LA FASE DE SELECCIÓN."
)


# ============================================================
# MATRICES
# ============================================================

X_train = train[
    FEATURES_NUMERICAS
]

y_train = train[
    TARGET
].astype(int)


X_validation = validation[
    FEATURES_NUMERICAS
]

y_validation = validation[
    TARGET
].astype(int)


# ============================================================
# PREPROCESAMIENTO
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


preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            pipeline_numerico,
            FEATURES_NUMERICAS
        ),
    ]
)


# ============================================================
# MODELO
# ============================================================
#
# Baseline v2:
# mismo enfoque que v1, eliminando únicamente SECTOR_CIIU.
#
# Se omite el parámetro penalty debido a su deprecación
# en scikit-learn 1.9.
#
# l1_ratio=0 representa regularización L2.
# ============================================================

modelo = LogisticRegression(
    C=1.0,
    class_weight="balanced",
    solver="lbfgs",
    max_iter=2000,
    random_state=RANDOM_STATE,
    l1_ratio=0,
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
# ENTRENAMIENTO
# ============================================================

print(
    "\nEntrenando Baseline v2..."
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
# EVALUACIÓN SOLO TRAIN + VALIDATION
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
}


metricas_generales = []
ranking_resultados = []


print(
    "\n" + "=" * 110
)

print(
    "MÉTRICAS GENERALES — SIN UTILIZAR TEST"
)

print("=" * 110)


for nombre_split, (
    X_split,
    y_split
) in datasets_evaluacion.items():

    probabilidades = (
        pipeline
        .predict_proba(
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

    print(
        "  Matriz:      "
        f"TN={resultado['TN']:,} | "
        f"FP={resultado['FP']:,} | "
        f"FN={resultado['FN']:,} | "
        f"TP={resultado['TP']:,}"
    )


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

        ranking_resultados.append(
            fila
        )


# ============================================================
# RANKING
# ============================================================

ranking_df = pd.DataFrame(
    ranking_resultados
)


print(
    "\n" + "=" * 110
)

print(
    "MÉTRICAS DE RANKING — SIN UTILIZAR TEST"
)

print("=" * 110)


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

    for _, fila in (
        bloque.iterrows()
    ):

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
    "COEFICIENTES — VARIABLES FINANCIERAS"
)

print("=" * 110)


print(
    coeficientes_df.to_string(
        index=False
    )
)


# ============================================================
# GUARDAR RESULTADOS
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


metricas_df.to_csv(
    METRICS_PATH,
    index=False
)


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
# METADATOS
# ============================================================

metadata = {
    "experimento":
        "Baseline v2",

    "modelo":
        "LogisticRegression",

    "descripcion":
        (
            "Regresión logística equivalente al "
            "Baseline v1 eliminando SECTOR_CIIU."
        ),

    "objetivo":
        (
            "Evaluar si la variable sectorial genera "
            "inestabilidad temporal."
        ),

    "random_state":
        RANDOM_STATE,

    "threshold":
        THRESHOLD,

    "C":
        1.0,

    "class_weight":
        "balanced",

    "solver":
        "lbfgs",

    "l1_ratio":
        0,

    "regularizacion":
        "L2",

    "max_iter":
        2000,

    "features":
        FEATURES_NUMERICAS,

    "sector_ciiu_utilizado":
        False,

    "train":
        "2015-2020",

    "validation":
        "2021",

    "test_evaluado_en_fase_seleccion":
        False,

    "k_values":
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
    "BASELINE V2 FINALIZADO CORRECTAMENTE"
)

print("=" * 110)


print(
    "\nIMPORTANTE:"
)

print(
    "El conjunto TEST no fue evaluado."
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