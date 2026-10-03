from pathlib import Path
from datetime import datetime, timezone
import json

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_DIR = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "v10"
)


# ============================================================
# MODELOS
# ============================================================

LR_MODEL = "v10_lr_no_provincia"
HGB_MODEL = "v10_hgb"


# ============================================================
# ARCHIVOS VALIDATION
# ============================================================

LR_METRICS_PATH = (
    RESULTS_DIR
    / "v10_lr_no_provincia_metrics.csv"
)

LR_RANKING_PATH = (
    RESULTS_DIR
    / "v10_lr_no_provincia_ranking_metrics.csv"
)

HGB_METRICS_PATH = (
    RESULTS_DIR
    / "v10_hgb_metrics.csv"
)

HGB_RANKING_PATH = (
    RESULTS_DIR
    / "v10_hgb_ranking_metrics.csv"
)


# ============================================================
# ARCHIVOS BACKTEST
# ============================================================

LR_BACKTEST_METRICS_PATH = (
    RESULTS_DIR
    / "backtest_logistic_v10_metrics.csv"
)

LR_BACKTEST_RANKING_PATH = (
    RESULTS_DIR
    / "backtest_logistic_v10_ranking_metrics.csv"
)

LR_BACKTEST_SUMMARY_PATH = (
    RESULTS_DIR
    / "backtest_logistic_v10_summary.csv"
)


HGB_BACKTEST_METRICS_PATH = (
    RESULTS_DIR
    / "backtest_hist_gradient_boosting_v10_metrics.csv"
)

HGB_BACKTEST_RANKING_PATH = (
    RESULTS_DIR
    / "backtest_hist_gradient_boosting_v10_ranking_metrics.csv"
)

HGB_BACKTEST_SUMMARY_PATH = (
    RESULTS_DIR
    / "backtest_hist_gradient_boosting_v10_summary.csv"
)


# ============================================================
# SALIDAS
# ============================================================

COMPARISON_PATH = (
    RESULTS_DIR
    / "comparison_v10_lr_vs_hgb.csv"
)

BACKTEST_BY_FOLD_PATH = (
    RESULTS_DIR
    / "comparison_v10_lr_vs_hgb_backtest_by_fold.csv"
)

RANKING_BY_FOLD_PATH = (
    RESULTS_DIR
    / "comparison_v10_lr_vs_hgb_ranking_by_fold.csv"
)

METADATA_PATH = (
    RESULTS_DIR
    / "comparison_v10_lr_vs_hgb_metadata.json"
)


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


def validar_archivo(path):
    """
    Verifica que exista un archivo requerido.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"No existe el archivo requerido:\n{path}"
        )


def validar_archivos():
    """
    Verifica todos los insumos de la comparación.
    """

    archivos = [
        LR_METRICS_PATH,
        LR_RANKING_PATH,
        HGB_METRICS_PATH,
        HGB_RANKING_PATH,
        LR_BACKTEST_METRICS_PATH,
        LR_BACKTEST_RANKING_PATH,
        LR_BACKTEST_SUMMARY_PATH,
        HGB_BACKTEST_METRICS_PATH,
        HGB_BACKTEST_RANKING_PATH,
        HGB_BACKTEST_SUMMARY_PATH,
    ]

    for archivo in archivos:

        validar_archivo(
            archivo
        )


# ============================================================
# VALIDATION 2020
# ============================================================

def cargar_validation_metrics(
    modelo,
    path,
):
    """
    Carga la fila VALIDATION de un modelo.
    """

    df = pd.read_csv(
        path
    )

    columnas = [
        "SPLIT",
        "OBSERVACIONES",
        "POSITIVOS",
        "PREVALENCIA",
        "PR_AUC",
        "ROC_AUC",
    ]

    faltantes = [
        columna
        for columna in columnas
        if columna not in df.columns
    ]

    if faltantes:

        raise ValueError(
            f"{modelo}: faltan columnas en métricas:\n"
            + "\n".join(
                faltantes
            )
        )

    validation = df[
        df[
            "SPLIT"
        ]
        .astype("string")
        .str.strip()
        .str.upper()
        .eq(
            "VALIDATION"
        )
    ].copy()

    if len(validation) != 1:

        raise ValueError(
            f"{modelo}: se esperaba exactamente una fila "
            "VALIDATION."
        )

    fila = validation.iloc[
        0
    ]

    return {
        "VALIDATION_OBSERVACIONES":
            int(
                fila[
                    "OBSERVACIONES"
                ]
            ),

        "VALIDATION_POSITIVOS":
            int(
                fila[
                    "POSITIVOS"
                ]
            ),

        "VALIDATION_PREVALENCIA":
            float(
                fila[
                    "PREVALENCIA"
                ]
            ),

        "VALIDATION_PR_AUC":
            float(
                fila[
                    "PR_AUC"
                ]
            ),

        "VALIDATION_ROC_AUC":
            float(
                fila[
                    "ROC_AUC"
                ]
            ),
    }


def cargar_validation_ranking(
    modelo,
    path,
):
    """
    Carga métricas Top-K de VALIDATION.
    """

    df = pd.read_csv(
        path
    )

    columnas = [
        "SPLIT",
        "K",
        "POSITIVOS_TOP_K",
        "PRECISION_AT_K",
        "RECALL_AT_K",
        "LIFT_AT_K",
    ]

    faltantes = [
        columna
        for columna in columnas
        if columna not in df.columns
    ]

    if faltantes:

        raise ValueError(
            f"{modelo}: faltan columnas en ranking:\n"
            + "\n".join(
                faltantes
            )
        )

    validation = df[
        df[
            "SPLIT"
        ]
        .astype("string")
        .str.strip()
        .str.upper()
        .eq(
            "VALIDATION"
        )
    ].copy()

    resultado = {}

    for k in [
        50,
        100,
        200,
    ]:

        fila = validation[
            validation[
                "K"
            ]
            == k
        ]

        if len(fila) != 1:

            raise ValueError(
                f"{modelo}: se esperaba exactamente una fila "
                f"VALIDATION para K={k}."
            )

        fila = fila.iloc[
            0
        ]

        resultado[
            f"VALIDATION_POSITIVOS_TOP_{k}"
        ] = int(
            fila[
                "POSITIVOS_TOP_K"
            ]
        )

        resultado[
            f"VALIDATION_PRECISION_AT_{k}"
        ] = float(
            fila[
                "PRECISION_AT_K"
            ]
        )

        resultado[
            f"VALIDATION_RECALL_AT_{k}"
        ] = float(
            fila[
                "RECALL_AT_K"
            ]
        )

        resultado[
            f"VALIDATION_LIFT_AT_{k}"
        ] = float(
            fila[
                "LIFT_AT_K"
            ]
        )

    return resultado


# ============================================================
# BACKTEST RESUMEN
# ============================================================

def cargar_lr_backtest_summary():
    """
    Obtiene únicamente el baseline logístico seleccionado.
    """

    df = pd.read_csv(
        LR_BACKTEST_SUMMARY_PATH
    )

    fila = df[
        df[
            "MODELO"
        ]
        == LR_MODEL
    ]

    if len(fila) != 1:

        raise ValueError(
            "No se encontró exactamente una fila para "
            f"{LR_MODEL} en el resumen logístico."
        )

    return fila.iloc[
        0
    ]


def cargar_hgb_backtest_summary():
    """
    Carga el resumen de HGB v10.
    """

    df = pd.read_csv(
        HGB_BACKTEST_SUMMARY_PATH
    )

    fila = df[
        df[
            "MODELO"
        ]
        == HGB_MODEL
    ]

    if len(fila) != 1:

        raise ValueError(
            "No se encontró exactamente una fila para "
            f"{HGB_MODEL}."
        )

    return fila.iloc[
        0
    ]


def extraer_backtest_summary(
    fila,
):
    """
    Convierte una fila resumen en estructura comparable.
    """

    return {
        "BACKTEST_N_FOLDS":
            int(
                fila[
                    "N_FOLDS"
                ]
            ),

        "BACKTEST_PR_AUC_MEDIA":
            float(
                fila[
                    "PR_AUC_MEDIA"
                ]
            ),

        "BACKTEST_PR_AUC_MEDIANA":
            float(
                fila[
                    "PR_AUC_MEDIANA"
                ]
            ),

        "BACKTEST_PR_AUC_STD":
            float(
                fila[
                    "PR_AUC_STD"
                ]
            ),

        "BACKTEST_PR_AUC_MIN":
            float(
                fila[
                    "PR_AUC_MIN"
                ]
            ),

        "BACKTEST_PR_AUC_MAX":
            float(
                fila[
                    "PR_AUC_MAX"
                ]
            ),

        "BACKTEST_ROC_AUC_MEDIA":
            float(
                fila[
                    "ROC_AUC_MEDIA"
                ]
            ),

        "BACKTEST_LIFT_AT_50_MEDIA":
            float(
                fila[
                    "LIFT_AT_50_MEDIA"
                ]
            ),

        "BACKTEST_LIFT_AT_100_MEDIA":
            float(
                fila[
                    "LIFT_AT_100_MEDIA"
                ]
            ),

        "BACKTEST_LIFT_AT_200_MEDIA":
            float(
                fila[
                    "LIFT_AT_200_MEDIA"
                ]
            ),

        "BACKTEST_POSITIVOS_TOP_50_TOTAL":
            int(
                fila[
                    "POSITIVOS_TOP_50_TOTAL"
                ]
            ),

        "BACKTEST_POSITIVOS_TOP_100_TOTAL":
            int(
                fila[
                    "POSITIVOS_TOP_100_TOTAL"
                ]
            ),

        "BACKTEST_POSITIVOS_TOP_200_TOTAL":
            int(
                fila[
                    "POSITIVOS_TOP_200_TOTAL"
                ]
            ),
    }


# ============================================================
# COMPARACIÓN GENERAL
# ============================================================

def construir_comparacion_general():
    """
    Construye tabla general VALIDATION + backtesting.
    """

    lr_validation = cargar_validation_metrics(
        LR_MODEL,
        LR_METRICS_PATH,
    )

    lr_ranking = cargar_validation_ranking(
        LR_MODEL,
        LR_RANKING_PATH,
    )

    hgb_validation = cargar_validation_metrics(
        HGB_MODEL,
        HGB_METRICS_PATH,
    )

    hgb_ranking = cargar_validation_ranking(
        HGB_MODEL,
        HGB_RANKING_PATH,
    )

    lr_backtest = extraer_backtest_summary(
        cargar_lr_backtest_summary()
    )

    hgb_backtest = extraer_backtest_summary(
        cargar_hgb_backtest_summary()
    )

    comparacion = pd.DataFrame(
        [
            {
                "MODELO":
                    LR_MODEL,

                "FAMILIA":
                    "LogisticRegression",

                **lr_validation,

                **lr_ranking,

                **lr_backtest,
            },

            {
                "MODELO":
                    HGB_MODEL,

                "FAMILIA":
                    "HistGradientBoostingClassifier",

                **hgb_validation,

                **hgb_ranking,

                **hgb_backtest,
            },
        ]
    )

    return comparacion


# ============================================================
# COMPARACIÓN POR FOLD
# ============================================================

def construir_comparacion_por_fold():
    """
    Valida que ambos modelos usen exactamente los mismos folds
    y genera una tabla de comparación por período.
    """

    lr = pd.read_csv(
        LR_BACKTEST_METRICS_PATH
    )

    lr = lr[
        lr[
            "MODELO"
        ]
        == LR_MODEL
    ].copy()

    hgb = pd.read_csv(
        HGB_BACKTEST_METRICS_PATH
    )

    hgb = hgb[
        hgb[
            "MODELO"
        ]
        == HGB_MODEL
    ].copy()

    columnas_control = [
        "FOLD",
        "TRAIN_INICIO",
        "TRAIN_FIN",
        "ANIO_EMBARGO",
        "ANIO_EVALUACION",
        "N_TRAIN",
        "POSITIVOS_TRAIN",
        "N_EVALUACION",
        "POSITIVOS_EVALUACION",
    ]

    lr_control = (
        lr[
            columnas_control
        ]
        .sort_values(
            "FOLD"
        )
        .reset_index(
            drop=True
        )
    )

    hgb_control = (
        hgb[
            columnas_control
        ]
        .sort_values(
            "FOLD"
        )
        .reset_index(
            drop=True
        )
    )

    if not lr_control.equals(
        hgb_control
    ):

        raise ValueError(
            "Los folds de LR y HGB no son exactamente equivalentes."
        )

    lr_metricas = lr[
        [
            "FOLD",
            "PR_AUC_TRAIN",
            "ROC_AUC_TRAIN",
            "PR_AUC_EVALUACION",
            "ROC_AUC_EVALUACION",
            "GAP_PR_AUC",
        ]
    ].copy()

    lr_metricas = lr_metricas.rename(
        columns={
            "PR_AUC_TRAIN":
                "LR_PR_AUC_TRAIN",

            "ROC_AUC_TRAIN":
                "LR_ROC_AUC_TRAIN",

            "PR_AUC_EVALUACION":
                "LR_PR_AUC_EVALUACION",

            "ROC_AUC_EVALUACION":
                "LR_ROC_AUC_EVALUACION",

            "GAP_PR_AUC":
                "LR_GAP_PR_AUC",
        }
    )

    hgb_metricas = hgb[
        [
            "FOLD",
            "PR_AUC_TRAIN",
            "ROC_AUC_TRAIN",
            "PR_AUC_EVALUACION",
            "ROC_AUC_EVALUACION",
            "GAP_PR_AUC",
        ]
    ].copy()

    hgb_metricas = hgb_metricas.rename(
        columns={
            "PR_AUC_TRAIN":
                "HGB_PR_AUC_TRAIN",

            "ROC_AUC_TRAIN":
                "HGB_ROC_AUC_TRAIN",

            "PR_AUC_EVALUACION":
                "HGB_PR_AUC_EVALUACION",

            "ROC_AUC_EVALUACION":
                "HGB_ROC_AUC_EVALUACION",

            "GAP_PR_AUC":
                "HGB_GAP_PR_AUC",
        }
    )

    comparacion = (
        lr_control
        .merge(
            lr_metricas,
            on="FOLD",
            how="inner",
        )
        .merge(
            hgb_metricas,
            on="FOLD",
            how="inner",
        )
    )

    comparacion[
        "DIF_PR_AUC_HGB_MENOS_LR"
    ] = (
        comparacion[
            "HGB_PR_AUC_EVALUACION"
        ]
        - comparacion[
            "LR_PR_AUC_EVALUACION"
        ]
    )

    comparacion[
        "HGB_SUPERA_LR_PR_AUC"
    ] = (
        comparacion[
            "DIF_PR_AUC_HGB_MENOS_LR"
        ]
        > 0
    )

    return comparacion


# ============================================================
# RANKING POR FOLD
# ============================================================

def construir_ranking_por_fold():
    """
    Compara Top-K entre ambos modelos en cada fold.
    """

    lr = pd.read_csv(
        LR_BACKTEST_RANKING_PATH
    )

    lr = lr[
        lr[
            "MODELO"
        ]
        == LR_MODEL
    ].copy()

    hgb = pd.read_csv(
        HGB_BACKTEST_RANKING_PATH
    )

    hgb = hgb[
        hgb[
            "MODELO"
        ]
        == HGB_MODEL
    ].copy()

    claves = [
        "FOLD",
        "ANIO_EVALUACION",
        "K",
        "N_EVALUACION",
        "POSITIVOS_EVALUACION",
    ]

    lr_control = (
        lr[
            claves
        ]
        .sort_values(
            [
                "FOLD",
                "K",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    hgb_control = (
        hgb[
            claves
        ]
        .sort_values(
            [
                "FOLD",
                "K",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    if not lr_control.equals(
        hgb_control
    ):

        raise ValueError(
            "Los universos Top-K de LR y HGB no coinciden."
        )

    lr = lr[
        [
            "FOLD",
            "ANIO_EVALUACION",
            "K",
            "POSITIVOS_TOP_K",
            "PRECISION_AT_K",
            "RECALL_AT_K",
            "LIFT_AT_K",
        ]
    ].rename(
        columns={
            "POSITIVOS_TOP_K":
                "LR_POSITIVOS_TOP_K",

            "PRECISION_AT_K":
                "LR_PRECISION_AT_K",

            "RECALL_AT_K":
                "LR_RECALL_AT_K",

            "LIFT_AT_K":
                "LR_LIFT_AT_K",
        }
    )

    hgb = hgb[
        [
            "FOLD",
            "ANIO_EVALUACION",
            "K",
            "POSITIVOS_TOP_K",
            "PRECISION_AT_K",
            "RECALL_AT_K",
            "LIFT_AT_K",
        ]
    ].rename(
        columns={
            "POSITIVOS_TOP_K":
                "HGB_POSITIVOS_TOP_K",

            "PRECISION_AT_K":
                "HGB_PRECISION_AT_K",

            "RECALL_AT_K":
                "HGB_RECALL_AT_K",

            "LIFT_AT_K":
                "HGB_LIFT_AT_K",
        }
    )

    comparacion = lr.merge(
        hgb,
        on=[
            "FOLD",
            "ANIO_EVALUACION",
            "K",
        ],
        how="inner",
    )

    comparacion[
        "DIF_POSITIVOS_HGB_MENOS_LR"
    ] = (
        comparacion[
            "HGB_POSITIVOS_TOP_K"
        ]
        - comparacion[
            "LR_POSITIVOS_TOP_K"
        ]
    )

    comparacion[
        "DIF_LIFT_HGB_MENOS_LR"
    ] = (
        comparacion[
            "HGB_LIFT_AT_K"
        ]
        - comparacion[
            "LR_LIFT_AT_K"
        ]
    )

    return comparacion


# ============================================================
# METADATA
# ============================================================

def construir_metadata(
    comparacion,
    por_fold,
):
    """
    Registra la comparación sin seleccionar todavía
    el modelo final.
    """

    lr = comparacion[
        comparacion[
            "MODELO"
        ]
        == LR_MODEL
    ].iloc[
        0
    ]

    hgb = comparacion[
        comparacion[
            "MODELO"
        ]
        == HGB_MODEL
    ].iloc[
        0
    ]

    hgb_supera_folds = int(
        por_fold[
            "HGB_SUPERA_LR_PR_AUC"
        ].sum()
    )

    metadata = {
        "experimento":
            "Comparacion v10 Logistic Regression vs HistGradientBoosting",

        "fecha_ejecucion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "modelos_comparados": [
            LR_MODEL,
            HGB_MODEL,
        ],

        "baseline_logistico":
            LR_MODEL,

        "modelo_no_lineal":
            HGB_MODEL,

        "objetivo":
            (
                "Comparar Logistic Regression y "
                "HistGradientBoosting bajo el mismo dataset, "
                "VALIDATION y protocolo temporal v10."
            ),

        "validation": {
            "anio":
                2020,

            "lr_pr_auc":
                float(
                    lr[
                        "VALIDATION_PR_AUC"
                    ]
                ),

            "hgb_pr_auc":
                float(
                    hgb[
                        "VALIDATION_PR_AUC"
                    ]
                ),

            "lr_roc_auc":
                float(
                    lr[
                        "VALIDATION_ROC_AUC"
                    ]
                ),

            "hgb_roc_auc":
                float(
                    hgb[
                        "VALIDATION_ROC_AUC"
                    ]
                ),
        },

        "backtesting": {
            "numero_folds":
                4,

            "lr_pr_auc_media":
                float(
                    lr[
                        "BACKTEST_PR_AUC_MEDIA"
                    ]
                ),

            "hgb_pr_auc_media":
                float(
                    hgb[
                        "BACKTEST_PR_AUC_MEDIA"
                    ]
                ),

            "lr_pr_auc_std":
                float(
                    lr[
                        "BACKTEST_PR_AUC_STD"
                    ]
                ),

            "hgb_pr_auc_std":
                float(
                    hgb[
                        "BACKTEST_PR_AUC_STD"
                    ]
                ),

            "folds_hgb_supera_lr_pr_auc":
                hgb_supera_folds,

            "folds_lr_iguala_o_supera_hgb":
                int(
                    len(
                        por_fold
                    )
                    - hgb_supera_folds
                ),
        },

        "criterios_de_analisis": [
            "PR-AUC VALIDATION",
            "PR-AUC media backtest",
            "variabilidad temporal",
            "Precision@K",
            "Recall@K",
            "Lift@K",
            "comportamiento por fold",
            "riesgo de sobreajuste",
            "interpretabilidad",
        ],

        "seleccion_modelo_final_realizada":
            False,

        "motivo_no_seleccion_final":
            (
                "La comparación forma parte de la fase de "
                "desarrollo. Aún quedan evaluación de modelos, "
                "interpretabilidad y análisis de sesgo antes de "
                "cerrar la selección final."
            ),

        "test": {
            "periodo":
                "2022-2023",

            "utilizado":
                False,

            "estado":
                "RESERVADO - SIN EVALUACION",
        },

        "archivos_salida": {
            "comparacion_general":
                ruta_relativa(
                    COMPARISON_PATH
                ),

            "comparacion_por_fold":
                ruta_relativa(
                    BACKTEST_BY_FOLD_PATH
                ),

            "ranking_por_fold":
                ruta_relativa(
                    RANKING_BY_FOLD_PATH
                ),

            "metadata":
                ruta_relativa(
                    METADATA_PATH
                ),
        },
    }

    return metadata


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
        "COMPARACIÓN v10 - LOGISTIC REGRESSION vs HISTGRADIENTBOOSTING"
    )

    print(
        "=" * 110
    )

    validar_archivos()

    comparacion = construir_comparacion_general()

    por_fold = construir_comparacion_por_fold()

    ranking_fold = construir_ranking_por_fold()

    metadata = construir_metadata(
        comparacion,
        por_fold,
    )

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    comparacion.to_csv(
        COMPARISON_PATH,
        index=False,
    )

    por_fold.to_csv(
        BACKTEST_BY_FOLD_PATH,
        index=False,
    )

    ranking_fold.to_csv(
        RANKING_BY_FOLD_PATH,
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

    # --------------------------------------------------------
    # MOSTRAR COMPARACIÓN
    # --------------------------------------------------------

    columnas_salida = [
        "MODELO",
        "VALIDATION_PR_AUC",
        "VALIDATION_ROC_AUC",
        "VALIDATION_POSITIVOS_TOP_50",
        "VALIDATION_POSITIVOS_TOP_100",
        "VALIDATION_POSITIVOS_TOP_200",
        "BACKTEST_PR_AUC_MEDIA",
        "BACKTEST_PR_AUC_STD",
        "BACKTEST_LIFT_AT_50_MEDIA",
        "BACKTEST_LIFT_AT_100_MEDIA",
        "BACKTEST_LIFT_AT_200_MEDIA",
    ]

    print(
        "\nComparación general:"
    )

    print(
        comparacion[
            columnas_salida
        ].to_string(
            index=False
        )
    )

    print(
        "\n"
        + "=" * 110
    )

    print(
        "COMPARACIÓN PR-AUC POR FOLD"
    )

    print(
        "=" * 110
    )

    columnas_fold = [
        "FOLD",
        "ANIO_EVALUACION",
        "LR_PR_AUC_EVALUACION",
        "HGB_PR_AUC_EVALUACION",
        "DIF_PR_AUC_HGB_MENOS_LR",
        "HGB_SUPERA_LR_PR_AUC",
    ]

    print(
        por_fold[
            columnas_fold
        ].to_string(
            index=False
        )
    )

    print(
        "\nHGB supera a LR en PR-AUC en:"
    )

    print(
        f"{int(por_fold['HGB_SUPERA_LR_PR_AUC'].sum())} "
        f"de {len(por_fold)} folds"
    )

    print(
        "\nSelección final:"
    )

    print(
        "NO REALIZADA EN ESTA ETAPA"
    )

    print(
        "\nTEST 2022-2023:"
    )

    print(
        "RESERVADO - SIN EVALUACIÓN"
    )

    print(
        "\nArchivos generados:"
    )

    print(
        COMPARISON_PATH
    )

    print(
        BACKTEST_BY_FOLD_PATH
    )

    print(
        RANKING_BY_FOLD_PATH
    )

    print(
        METADATA_PATH
    )

    print(
        "\nComparación finalizada."
    )


if __name__ == "__main__":
    main()