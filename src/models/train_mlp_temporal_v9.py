from pathlib import Path
import json
import platform
import warnings

import joblib
import numpy as np
import pandas as pd
import sklearn

from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_sample_weight


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
    / "mlp_temporal_v9.joblib"
)

METRICS_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "mlp_temporal_v9_metrics.csv"
)

RANKING_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "mlp_temporal_v9_ranking_metrics.csv"
)

LOSS_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "mlp_temporal_v9_loss_curve.csv"
)

METADATA_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "mlp_temporal_v9_metadata.json"
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
# FEATURES ACTUALES
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
    """
    Calcula métricas generales de clasificación.

    Los scores no se interpretan como probabilidades
    calibradas.
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
    Calcula métricas de ranking orientadas a priorización.
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
# 1. CARGAR DATOS
# ============================================================

print("=" * 110)
print("V9 - RED NEURONAL MLP CON FEATURES TEMPORALES")
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

print(
    f"Features utilizadas: "
    f"{len(FEATURES)}"
)


# ============================================================
# 2. VALIDAR COLUMNAS
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
# 3. NORMALIZAR VARIABLES
# ============================================================

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
# 4. SPLITS
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


print(
    "\nEmbargos temporales:"
)

print(
    "  2019 -> EMBARGO_VALIDATION"
)

print(
    "  2021 -> EMBARGO_TEST"
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

X_train_raw = train[
    FEATURES
].copy()


y_train = train[
    TARGET
].astype(int)


X_validation_raw = validation[
    FEATURES
].copy()


y_validation = validation[
    TARGET
].astype(int)


# ============================================================
# 7. IMPUTACIÓN
# ============================================================

#
# La mediana se aprende exclusivamente con TRAIN.
#

imputer = SimpleImputer(
    strategy="median"
)


X_train_imputed = imputer.fit_transform(
    X_train_raw
)


X_validation_imputed = imputer.transform(
    X_validation_raw
)


# ============================================================
# 8. ESCALAMIENTO
# ============================================================

#
# MLP es sensible a las escalas.
#
# StandardScaler se ajusta exclusivamente con TRAIN.
#

scaler = StandardScaler()


X_train = scaler.fit_transform(
    X_train_imputed
)


X_validation = scaler.transform(
    X_validation_imputed
)


# ============================================================
# 9. PESOS DE CLASE
# ============================================================

#
# La versión instalada de sklearn permite sample_weight
# directamente en MLPClassifier.fit().
#
# Los pesos se calculan solamente a partir de TRAIN.
#

sample_weights = compute_sample_weight(
    class_weight="balanced",
    y=y_train
)


pesos_negativos = sample_weights[
    y_train.to_numpy() == 0
]


pesos_positivos = sample_weights[
    y_train.to_numpy() == 1
]


print(
    "\nPesos de entrenamiento:"
)

print(
    f"  Peso clase 0: "
    f"{pesos_negativos[0]:.6f}"
)

print(
    f"  Peso clase 1: "
    f"{pesos_positivos[0]:.6f}"
)

print(
    f"  Media pesos:  "
    f"{sample_weights.mean():.6f}"
)


# ============================================================
# 10. MODELO MLP V9
# ============================================================

#
# Arquitectura controlada:
#
# entrada: 33 variables
# capa oculta 1: 64 neuronas ReLU
# capa oculta 2: 32 neuronas ReLU
# salida: clasificación binaria
#
# No se realiza tuning exhaustivo.
#
# early_stopping=False:
# evita crear una partición aleatoria interna de TRAIN.
#
# alpha=0.01:
# regularización L2 para limitar sobreajuste.
#

modelo = MLPClassifier(
    hidden_layer_sizes=(
        64,
        32,
    ),
    activation="relu",
    solver="adam",
    alpha=0.01,
    batch_size=512,
    learning_rate="constant",
    learning_rate_init=0.001,
    max_iter=200,
    shuffle=True,
    random_state=RANDOM_STATE,
    tol=1e-4,
    early_stopping=False,
    n_iter_no_change=10,
    verbose=False,
)


# ============================================================
# 11. ENTRENAMIENTO
# ============================================================

print(
    "\nEntrenando MLP v9..."
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
        sample_weight=sample_weights
    )


    convergence_warning = any(
        issubclass(
            advertencia.category,
            ConvergenceWarning
        )
        for advertencia in advertencias
    )


print(
    "Entrenamiento finalizado."
)


print(
    f"Iteraciones utilizadas: "
    f"{modelo.n_iter_}"
)


print(
    f"Loss final: "
    f"{modelo.loss_:.6f}"
)


print(
    f"ConvergenceWarning: "
    f"{convergence_warning}"
)


# ============================================================
# 12. EVALUACIÓN
# ============================================================

#
# ÚNICAMENTE TRAIN y VALIDATION.
#
# TEST no se transforma, no se predice y no se evalúa.
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
        modelo.predict_proba(
            X_split
        )[:, 1]
    )


    resultado = metricas_clasificacion(
        y_split,
        scores,
        THRESHOLD
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


    ranking_split = metricas_ranking(
        y_split,
        scores,
        K_VALUES
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
# 13. RANKING
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
# 14. GUARDAR RESULTADOS
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


# ============================================================
# 15. CURVA DE PÉRDIDA
# ============================================================

loss_df = pd.DataFrame(
    {
        "ITERACION":
            np.arange(
                1,
                len(
                    modelo.loss_curve_
                ) + 1
            ),

        "LOSS":
            modelo.loss_curve_,
    }
)


loss_df.to_csv(
    LOSS_PATH,
    index=False
)


# ============================================================
# 16. GUARDAR MODELO Y PREPROCESAMIENTO
# ============================================================

joblib.dump(
    {
        "imputer":
            imputer,

        "scaler":
            scaler,

        "model":
            modelo,

        "features":
            FEATURES,
    },
    MODEL_PATH
)


# ============================================================
# 17. METADATOS
# ============================================================

metadata = {
    "experimento":
        "mlp_temporal_v9",

    "modelo":
        "MLPClassifier",

    "descripcion":
        (
            "Primer modelo neuronal del esquema temporal "
            "seguro. Utiliza las mismas 33 variables "
            "financieras actuales y temporales de v8."
        ),

    "comparacion_principal":
        "HistGradientBoosting regularized v8",

    "random_state":
        RANDOM_STATE,

    "arquitectura": {
        "entrada_features":
            len(FEATURES),

        "hidden_layer_sizes":
            [
                64,
                32,
            ],

        "activation":
            "relu",

        "solver":
            "adam",
    },

    "regularizacion": {
        "alpha":
            0.01,
    },

    "entrenamiento": {
        "batch_size":
            512,

        "learning_rate":
            "constant",

        "learning_rate_init":
            0.001,

        "max_iter":
            200,

        "tol":
            0.0001,

        "early_stopping":
            False,

        "n_iter_no_change":
            10,

        "iteraciones_utilizadas":
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
    },

    "manejo_desbalance":
        (
            "sample_weight calculado mediante "
            "compute_sample_weight(class_weight='balanced') "
            "exclusivamente sobre TRAIN."
        ),

    "peso_clase_0":
        float(
            pesos_negativos[0]
        ),

    "peso_clase_1":
        float(
            pesos_positivos[0]
        ),

    "imputacion":
        (
            "SimpleImputer(strategy='median') "
            "ajustado exclusivamente con TRAIN."
        ),

    "escalamiento":
        (
            "StandardScaler ajustado exclusivamente "
            "con TRAIN."
        ),

    "numero_features":
        len(FEATURES),

    "features_actuales":
        FEATURES_ACTUALES,

    "features_temporales":
        FEATURES_TEMPORALES,

    "sector_ciiu_utilizado":
        False,

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
            "No se generan scores, predicciones ni métricas "
            "sobre TEST en v9."
        ),

    "tuning_realizado":
        False,

    "nota_tuning":
        (
            "v9 corresponde a una arquitectura neuronal "
            "controlada y no a una búsqueda exhaustiva "
            "de hiperparámetros."
        ),

    "threshold_evaluacion":
        THRESHOLD,

    "k_ranking":
        K_VALUES,

    "scores_calibrados":
        False,

    "nota_calibracion":
        (
            "predict_proba se utiliza como score de "
            "priorización y no como probabilidad calibrada "
            "del Índice de Afinidad Bursátil."
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
    "MLP V9 ENTRENADO CORRECTAMENTE"
)

print(
    "=" * 110
)


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
    "\nCurva de pérdida:"
)

print(
    LOSS_PATH
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
    "RESERVADO - NO EVALUADO EN V9"
)