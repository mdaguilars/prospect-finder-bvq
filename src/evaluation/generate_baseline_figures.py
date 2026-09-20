from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.metrics import (
    ConfusionMatrixDisplay,
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
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

FIGURES_DIR = (
    PROJECT_ROOT
    / "reports"
    / "figures"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "reports"
    / "results"
)


THRESHOLD = 0.50

K_VALUES = [
    50,
    100,
    200,
]


# ============================================================
# VARIABLES DEL BASELINE V1
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
# FUNCIONES
# ============================================================

def guardar_figura(nombre):
    """
    Guarda la figura actual y la cierra.
    """

    ruta = FIGURES_DIR / nombre

    plt.tight_layout()

    plt.savefig(
        ruta,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Generada: {ruta}"
    )


def calcular_ranking(
    y_true,
    probabilidades,
    k_values
):
    """
    Calcula positivos, Precision@K, Recall@K y Lift@K.
    """

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

        top = tabla.head(
            k_real
        )

        positivos_top = int(
            top["TARGET"].sum()
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

    return pd.DataFrame(
        resultados
    )


# ============================================================
# PREPARAR DIRECTORIOS
# ============================================================

FIGURES_DIR.mkdir(
    parents=True,
    exist_ok=True
)

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CARGAR DATOS
# ============================================================

print("=" * 110)
print("GENERACIÓN DE FIGURAS — BASELINE V1")
print("=" * 110)


if not DATA_PATH.exists():

    raise FileNotFoundError(
        f"No existe el dataset:\n{DATA_PATH}"
    )


if not MODEL_PATH.exists():

    raise FileNotFoundError(
        f"No existe el modelo:\n{MODEL_PATH}"
    )


df = pd.read_csv(
    DATA_PATH,
    dtype={
        "RUC": str,
        "SECTOR_CIIU": str,
        "SPLIT": str,
    },
    low_memory=False
)


modelo = joblib.load(
    MODEL_PATH
)


print(
    f"\nObservaciones cargadas: "
    f"{len(df):,}"
)


# ============================================================
# PREPARAR SPLITS
# ============================================================

splits = {}


for nombre in [
    "TRAIN",
    "VALIDATION",
    "TEST",
]:

    subset = df[
        df["SPLIT"]
        == nombre
    ].copy()

    X = subset[
        FEATURES
    ]

    y = subset[
        TARGET
    ].astype(int)

    probabilidades = (
        modelo
        .predict_proba(
            X
        )[:, 1]
    )

    predicciones = (
        probabilidades
        >= THRESHOLD
    ).astype(int)

    splits[
        nombre
    ] = {
        "data":
            subset,

        "X":
            X,

        "y":
            y,

        "prob":
            probabilidades,

        "pred":
            predicciones,
    }


    print(
        f"{nombre:<11} "
        f"{len(subset):>10,} | "
        f"positivos: "
        f"{int(y.sum()):>4,}"
    )


# ============================================================
# FIGURA 1
# DISTRIBUCIÓN DE CLASES
# ============================================================

print(
    "\nGenerando distribución de clases..."
)


nombres = []
negativos = []
positivos = []


for nombre, datos in splits.items():

    y = datos[
        "y"
    ]

    nombres.append(
        nombre
    )

    positivos.append(
        int(
            y.sum()
        )
    )

    negativos.append(
        int(
            len(y)
            - y.sum()
        )
    )


x = np.arange(
    len(nombres)
)

ancho = 0.35


plt.figure(
    figsize=(9, 6)
)


plt.bar(
    x - ancho / 2,
    negativos,
    ancho,
    label="Negativos"
)


plt.bar(
    x + ancho / 2,
    positivos,
    ancho,
    label="Positivos"
)


plt.yscale(
    "log"
)


plt.xticks(
    x,
    nombres
)


plt.ylabel(
    "Número de observaciones (escala logarítmica)"
)


plt.title(
    "Distribución de clases por conjunto temporal"
)


plt.legend()


plt.grid(
    axis="y",
    alpha=0.25
)


guardar_figura(
    "baseline_01_distribucion_clases.png"
)


# ============================================================
# FIGURA 2
# PRECISION–RECALL
# ============================================================

print(
    "\nGenerando curvas Precision–Recall..."
)


plt.figure(
    figsize=(9, 6)
)


for nombre, datos in splits.items():

    y = datos[
        "y"
    ]

    probabilidades = datos[
        "prob"
    ]


    precision, recall, _ = (
        precision_recall_curve(
            y,
            probabilidades
        )
    )


    pr_auc = (
        average_precision_score(
            y,
            probabilidades
        )
    )


    plt.plot(
        recall,
        precision,
        label=(
            f"{nombre} "
            f"(PR-AUC={pr_auc:.4f})"
        )
    )


plt.xlabel(
    "Recall"
)


plt.ylabel(
    "Precision"
)


plt.title(
    "Curvas Precision–Recall — Baseline v1"
)


plt.legend()


plt.grid(
    alpha=0.25
)


guardar_figura(
    "baseline_02_precision_recall.png"
)


# ============================================================
# FIGURA 3
# MATRIZ DE CONFUSIÓN VALIDATION
# ============================================================

print(
    "\nGenerando matriz de confusión de VALIDATION..."
)


plt.figure(
    figsize=(7, 6)
)


ConfusionMatrixDisplay.from_predictions(
    splits[
        "VALIDATION"
    ][
        "y"
    ],
    splits[
        "VALIDATION"
    ][
        "pred"
    ],
    display_labels=[
        "No emisor",
        "Futuro emisor",
    ],
    values_format=",d",
)


plt.title(
    "Matriz de confusión — VALIDATION\n"
    "Baseline v1 | Threshold = 0.50"
)


guardar_figura(
    "baseline_03_confusion_matrix_validation.png"
)


# ============================================================
# FIGURA 4
# MATRIZ DE CONFUSIÓN TEST
# ============================================================

print(
    "\nGenerando matriz de confusión de TEST..."
)


plt.figure(
    figsize=(7, 6)
)


ConfusionMatrixDisplay.from_predictions(
    splits[
        "TEST"
    ][
        "y"
    ],
    splits[
        "TEST"
    ][
        "pred"
    ],
    display_labels=[
        "No emisor",
        "Futuro emisor",
    ],
    values_format=",d",
)


plt.title(
    "Matriz de confusión — TEST\n"
    "Baseline v1 | Threshold = 0.50"
)


guardar_figura(
    "baseline_04_confusion_matrix_test.png"
)


# ============================================================
# RANKING POR SPLIT
# ============================================================

ranking_todos = []


for nombre, datos in splits.items():

    ranking = calcular_ranking(
        datos[
            "y"
        ],
        datos[
            "prob"
        ],
        K_VALUES
    )


    ranking[
        "SPLIT"
    ] = nombre


    ranking_todos.append(
        ranking
    )


ranking_df = pd.concat(
    ranking_todos,
    ignore_index=True
)


# ============================================================
# FIGURA 5
# POSITIVOS EN TOP K
# ============================================================

print(
    "\nGenerando gráfico de positivos Top-K..."
)


plt.figure(
    figsize=(9, 6)
)


for nombre in [
    "TRAIN",
    "VALIDATION",
    "TEST",
]:

    bloque = ranking_df[
        ranking_df[
            "SPLIT"
        ]
        == nombre
    ]


    plt.plot(
        bloque[
            "K"
        ],
        bloque[
            "POSITIVOS_TOP_K"
        ],
        marker="o",
        label=nombre
    )


plt.xlabel(
    "Número de empresas priorizadas (K)"
)


plt.ylabel(
    "Futuros emisores identificados"
)


plt.title(
    "Futuros emisores identificados en el Top-K"
)


plt.xticks(
    K_VALUES
)


plt.legend()


plt.grid(
    alpha=0.25
)


guardar_figura(
    "baseline_05_positivos_top_k.png"
)


# ============================================================
# FIGURA 6
# LIFT@K
# ============================================================

print(
    "\nGenerando gráfico Lift@K..."
)


plt.figure(
    figsize=(9, 6)
)


for nombre in [
    "TRAIN",
    "VALIDATION",
    "TEST",
]:

    bloque = ranking_df[
        ranking_df[
            "SPLIT"
        ]
        == nombre
    ]


    plt.plot(
        bloque[
            "K"
        ],
        bloque[
            "LIFT_AT_K"
        ],
        marker="o",
        label=nombre
    )


plt.xlabel(
    "Número de empresas priorizadas (K)"
)


plt.ylabel(
    "Lift"
)


plt.title(
    "Lift del ranking — Baseline v1"
)


plt.xticks(
    K_VALUES
)


plt.legend()


plt.grid(
    alpha=0.25
)


guardar_figura(
    "baseline_06_lift_top_k.png"
)


# ============================================================
# FIGURA 7
# PRECISION@K
# ============================================================

print(
    "\nGenerando gráfico Precision@K..."
)


plt.figure(
    figsize=(9, 6)
)


for nombre in [
    "TRAIN",
    "VALIDATION",
    "TEST",
]:

    bloque = ranking_df[
        ranking_df[
            "SPLIT"
        ]
        == nombre
    ]


    plt.plot(
        bloque[
            "K"
        ],
        bloque[
            "PRECISION_AT_K"
        ],
        marker="o",
        label=nombre
    )


plt.xlabel(
    "Número de empresas priorizadas (K)"
)


plt.ylabel(
    "Precision@K"
)


plt.title(
    "Precision@K — Baseline v1"
)


plt.xticks(
    K_VALUES
)


plt.legend()


plt.grid(
    alpha=0.25
)


guardar_figura(
    "baseline_07_precision_top_k.png"
)


# ============================================================
# RESUMEN DE ERRORES
# ============================================================

print(
    "\nGenerando resumen de errores..."
)


errores = []


for nombre, datos in splits.items():

    y = np.asarray(
        datos[
            "y"
        ]
    )

    pred = np.asarray(
        datos[
            "pred"
        ]
    )


    tn, fp, fn, tp = confusion_matrix(
        y,
        pred,
        labels=[
            0,
            1,
        ]
    ).ravel()


    pr_auc = average_precision_score(
        y,
        datos[
            "prob"
        ]
    )


    roc_auc = roc_auc_score(
        y,
        datos[
            "prob"
        ]
    )


    errores.append(
        {
            "SPLIT":
                nombre,

            "OBSERVACIONES":
                len(y),

            "POSITIVOS":
                int(
                    y.sum()
                ),

            "PREVALENCIA":
                float(
                    y.mean()
                ),

            "PR_AUC":
                pr_auc,

            "ROC_AUC":
                roc_auc,

            "TN":
                int(tn),

            "FP":
                int(fp),

            "FN":
                int(fn),

            "TP":
                int(tp),

            "THRESHOLD":
                THRESHOLD,
        }
    )


errores_df = pd.DataFrame(
    errores
)


ERRORS_PATH = (
    RESULTS_DIR
    / "baseline_error_summary.csv"
)


errores_df.to_csv(
    ERRORS_PATH,
    index=False
)


RANKING_PATH = (
    RESULTS_DIR
    / "baseline_ranking_figures_data.csv"
)


ranking_df.to_csv(
    RANKING_PATH,
    index=False
)


# ============================================================
# MOSTRAR RESUMEN
# ============================================================

print(
    "\n" + "=" * 110
)

print(
    "RESUMEN DE ERRORES"
)

print("=" * 110)


print(
    errores_df[
        [
            "SPLIT",
            "OBSERVACIONES",
            "POSITIVOS",
            "PR_AUC",
            "ROC_AUC",
            "TN",
            "FP",
            "FN",
            "TP",
        ]
    ]
    .to_string(
        index=False,
        formatters={
            "PR_AUC":
                "{:.6f}".format,

            "ROC_AUC":
                "{:.6f}".format,
        }
    )
)


print(
    "\n" + "=" * 110
)

print(
    "RANKING"
)

print("=" * 110)


print(
    ranking_df[
        [
            "SPLIT",
            "K",
            "POSITIVOS_TOP_K",
            "PRECISION_AT_K",
            "RECALL_AT_K",
            "LIFT_AT_K",
        ]
    ]
    .to_string(
        index=False,
        formatters={
            "PRECISION_AT_K":
                "{:.4f}".format,

            "RECALL_AT_K":
                "{:.4f}".format,

            "LIFT_AT_K":
                "{:.2f}".format,
        }
    )
)


# ============================================================
# FINAL
# ============================================================

print(
    "\n" + "=" * 110
)

print(
    "FIGURAS DEL BASELINE V1 GENERADAS CORRECTAMENTE"
)

print("=" * 110)


print(
    "\nDirectorio de figuras:"
)

print(
    FIGURES_DIR
)


print(
    "\nResumen de errores:"
)

print(
    ERRORS_PATH
)


print(
    "\nDatos de ranking:"
)

print(
    RANKING_PATH
)