from pathlib import Path
import json
import platform

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
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "mvp_features_2015_2023.csv.gz"
)

RESULTS_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "logistic_regularization_v3_validation.csv"
)

METADATA_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "logistic_regularization_v3_metadata.json"
)


RANDOM_STATE = 42

# C menor = regularización más fuerte
C_VALUES = [
    0.001,
    0.01,
    0.1,
    1.0,
    10.0,
]

K_VALUES = [
    50,
    100,
    200,
]


# ============================================================
# FEATURES
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

FEATURES = (
    FEATURES_NUMERICAS
    + FEATURES_CATEGORICAS
)

TARGET = "TARGET_24M"


# ============================================================
# FUNCIÓN DE RANKING
# ============================================================

def calcular_ranking(
    y_true,
    probabilidades,
    k
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

    k_real = min(
        k,
        len(tabla)
    )

    top_k = tabla.head(
        k_real
    )

    positivos_totales = int(
        tabla[
            "TARGET"
        ].sum()
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

    prevalencia = (
        positivos_totales
        / len(tabla)
    )

    lift_k = (
        precision_k
        / prevalencia
        if prevalencia > 0
        else np.nan
    )

    return {
        "POSITIVOS_TOP":
            positivos_top,

        "PRECISION":
            precision_k,

        "RECALL":
            recall_k,

        "LIFT":
            lift_k,
    }


# ============================================================
# CARGAR DATOS
# ============================================================

print("=" * 110)
print("EXPERIMENTO V3 — REGULARIZACIÓN DE REGRESIÓN LOGÍSTICA")
print("=" * 110)


if not INPUT_PATH.exists():

    raise FileNotFoundError(
        f"No existe:\n{INPUT_PATH}"
    )


df = pd.read_csv(
    INPUT_PATH,
    dtype={
        "RUC": str,
        "SECTOR_CIIU": str,
        "SPLIT": str,
    },
    low_memory=False
)


print(
    f"\nObservaciones disponibles: "
    f"{len(df):,}"
)


# ============================================================
# VALIDAR COLUMNAS
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
        "Faltan columnas necesarias: "
        f"{faltantes}"
    )


# ============================================================
# TRAIN / VALIDATION
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
    "\nTEST NO SE UTILIZA EN ESTE EXPERIMENTO."
)


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
# FUNCIÓN PARA CONSTRUIR PIPELINE
# ============================================================

def construir_pipeline(c_value):

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


    modelo = LogisticRegression(
        C=c_value,
        class_weight="balanced",
        solver="lbfgs",
        max_iter=2000,
        random_state=RANDOM_STATE,
        l1_ratio=0,
    )


    return Pipeline(
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
# ENTRENAR DIFERENTES NIVELES DE REGULARIZACIÓN
# ============================================================

resultados = []


print(
    "\n" + "=" * 110
)

print(
    "RESULTADOS DE VALIDATION"
)

print("=" * 110)


for c_value in C_VALUES:

    print(
        f"\nEntrenando C={c_value}..."
    )

    pipeline = construir_pipeline(
        c_value
    )

    pipeline.fit(
        X_train,
        y_train
    )


    prob_train = (
        pipeline
        .predict_proba(
            X_train
        )[:, 1]
    )


    prob_validation = (
        pipeline
        .predict_proba(
            X_validation
        )[:, 1]
    )


    # --------------------------------------------------------
    # MÉTRICAS GENERALES
    # --------------------------------------------------------

    train_pr_auc = (
        average_precision_score(
            y_train,
            prob_train
        )
    )


    validation_pr_auc = (
        average_precision_score(
            y_validation,
            prob_validation
        )
    )


    train_roc_auc = (
        roc_auc_score(
            y_train,
            prob_train
        )
    )


    validation_roc_auc = (
        roc_auc_score(
            y_validation,
            prob_validation
        )
    )


    resultado = {
        "C":
            c_value,

        "TRAIN_PR_AUC":
            train_pr_auc,

        "VALIDATION_PR_AUC":
            validation_pr_auc,

        "TRAIN_ROC_AUC":
            train_roc_auc,

        "VALIDATION_ROC_AUC":
            validation_roc_auc,

        "ITERACIONES":
            int(
                pipeline
                .named_steps[
                    "model"
                ]
                .n_iter_[0]
            ),
    }


    # --------------------------------------------------------
    # MÉTRICAS DE RANKING VALIDATION
    # --------------------------------------------------------

    for k in K_VALUES:

        ranking = calcular_ranking(
            y_validation,
            prob_validation,
            k
        )

        resultado[
            f"POSITIVOS_AT_{k}"
        ] = ranking[
            "POSITIVOS_TOP"
        ]

        resultado[
            f"PRECISION_AT_{k}"
        ] = ranking[
            "PRECISION"
        ]

        resultado[
            f"RECALL_AT_{k}"
        ] = ranking[
            "RECALL"
        ]

        resultado[
            f"LIFT_AT_{k}"
        ] = ranking[
            "LIFT"
        ]


    resultados.append(
        resultado
    )


    print(
        f"  Train PR-AUC:       "
        f"{train_pr_auc:.6f}"
    )

    print(
        f"  Validation PR-AUC:  "
        f"{validation_pr_auc:.6f}"
    )

    print(
        f"  Validation ROC-AUC: "
        f"{validation_roc_auc:.6f}"
    )

    print(
        f"  Top 50:  "
        f"{resultado['POSITIVOS_AT_50']} positivos | "
        f"Precision="
        f"{resultado['PRECISION_AT_50']:.4f} | "
        f"Recall="
        f"{resultado['RECALL_AT_50']:.4f}"
    )

    print(
        f"  Top 100: "
        f"{resultado['POSITIVOS_AT_100']} positivos | "
        f"Precision="
        f"{resultado['PRECISION_AT_100']:.4f} | "
        f"Recall="
        f"{resultado['RECALL_AT_100']:.4f}"
    )

    print(
        f"  Top 200: "
        f"{resultado['POSITIVOS_AT_200']} positivos | "
        f"Precision="
        f"{resultado['PRECISION_AT_200']:.4f} | "
        f"Recall="
        f"{resultado['RECALL_AT_200']:.4f}"
    )


# ============================================================
# RESULTADOS CONSOLIDADOS
# ============================================================

resultados_df = pd.DataFrame(
    resultados
)


resultados_df = (
    resultados_df
    .sort_values(
        [
            "VALIDATION_PR_AUC",
            "PRECISION_AT_50",
            "RECALL_AT_50",
        ],
        ascending=[
            False,
            False,
            False,
        ]
    )
    .reset_index(
        drop=True
    )
)


print(
    "\n" + "=" * 110
)

print(
    "COMPARACIÓN FINAL V3 — VALIDATION"
)

print("=" * 110)


columnas_mostrar = [
    "C",
    "TRAIN_PR_AUC",
    "VALIDATION_PR_AUC",
    "VALIDATION_ROC_AUC",
    "POSITIVOS_AT_50",
    "PRECISION_AT_50",
    "RECALL_AT_50",
    "POSITIVOS_AT_100",
    "PRECISION_AT_100",
    "RECALL_AT_100",
    "POSITIVOS_AT_200",
    "PRECISION_AT_200",
    "RECALL_AT_200",
]


print(
    resultados_df[
        columnas_mostrar
    ]
    .to_string(
        index=False,
        formatters={
            "TRAIN_PR_AUC":
                "{:.6f}".format,

            "VALIDATION_PR_AUC":
                "{:.6f}".format,

            "VALIDATION_ROC_AUC":
                "{:.6f}".format,

            "PRECISION_AT_50":
                "{:.4f}".format,

            "RECALL_AT_50":
                "{:.4f}".format,

            "PRECISION_AT_100":
                "{:.4f}".format,

            "RECALL_AT_100":
                "{:.4f}".format,

            "PRECISION_AT_200":
                "{:.4f}".format,

            "RECALL_AT_200":
                "{:.4f}".format,
        }
    )
)


# ============================================================
# GUARDAR RESULTADOS
# ============================================================

RESULTS_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


resultados_df.to_csv(
    RESULTS_PATH,
    index=False
)


# ============================================================
# METADATOS
# ============================================================

metadata = {
    "experimento":
        "v3_regularizacion_logistica",

    "modelo":
        "LogisticRegression",

    "objetivo":
        (
            "Evaluar mayor o menor regularización "
            "manteniendo SECTOR_CIIU."
        ),

    "C_values":
        C_VALUES,

    "criterio_primario":
        "VALIDATION_PR_AUC",

    "criterios_secundarios": [
        "Precision@50",
        "Recall@50",
        "Precision@100",
        "Recall@100",
        "Precision@200",
        "Recall@200",
    ],

    "random_state":
        RANDOM_STATE,

    "class_weight":
        "balanced",

    "regularizacion":
        "L2",

    "sector_ciiu":
        True,

    "train":
        "2015-2020",

    "validation":
        "2021",

    "test_utilizado":
        False,

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
    "EXPERIMENTO V3 FINALIZADO CORRECTAMENTE"
)

print("=" * 110)


print(
    "\nResultados:"
)

print(
    RESULTS_PATH
)


print(
    "\nMetadatos:"
)

print(
    METADATA_PATH
)


print(
    "\nTEST permanece sin utilizar "
    "durante esta selección."
)