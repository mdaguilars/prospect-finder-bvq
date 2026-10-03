from pathlib import Path
from datetime import datetime, timezone
import json

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
MLP_MODEL = "v10_mlp"

MODELOS = [
    LR_MODEL,
    HGB_MODEL,
    MLP_MODEL,
]


# ============================================================
# ARCHIVOS VALIDATION
# ============================================================

VALIDATION_METRICS_PATHS = {
    LR_MODEL:
        RESULTS_DIR
        / "v10_lr_no_provincia_metrics.csv",

    HGB_MODEL:
        RESULTS_DIR
        / "v10_hgb_metrics.csv",

    MLP_MODEL:
        RESULTS_DIR
        / "v10_mlp_metrics.csv",
}


VALIDATION_RANKING_PATHS = {
    LR_MODEL:
        RESULTS_DIR
        / "v10_lr_no_provincia_ranking_metrics.csv",

    HGB_MODEL:
        RESULTS_DIR
        / "v10_hgb_ranking_metrics.csv",

    MLP_MODEL:
        RESULTS_DIR
        / "v10_mlp_ranking_metrics.csv",
}


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


MLP_BACKTEST_METRICS_PATH = (
    RESULTS_DIR
    / "backtest_mlp_v10_metrics.csv"
)

MLP_BACKTEST_RANKING_PATH = (
    RESULTS_DIR
    / "backtest_mlp_v10_ranking_metrics.csv"
)

MLP_BACKTEST_SUMMARY_PATH = (
    RESULTS_DIR
    / "backtest_mlp_v10_summary.csv"
)


BACKTEST_METRICS_PATHS = {
    LR_MODEL:
        LR_BACKTEST_METRICS_PATH,

    HGB_MODEL:
        HGB_BACKTEST_METRICS_PATH,

    MLP_MODEL:
        MLP_BACKTEST_METRICS_PATH,
}


BACKTEST_RANKING_PATHS = {
    LR_MODEL:
        LR_BACKTEST_RANKING_PATH,

    HGB_MODEL:
        HGB_BACKTEST_RANKING_PATH,

    MLP_MODEL:
        MLP_BACKTEST_RANKING_PATH,
}


BACKTEST_SUMMARY_PATHS = {
    LR_MODEL:
        LR_BACKTEST_SUMMARY_PATH,

    HGB_MODEL:
        HGB_BACKTEST_SUMMARY_PATH,

    MLP_MODEL:
        MLP_BACKTEST_SUMMARY_PATH,
}


# ============================================================
# SALIDAS
# ============================================================

COMPARISON_PATH = (
    RESULTS_DIR
    / "comparison_v10_models.csv"
)

BACKTEST_BY_FOLD_PATH = (
    RESULTS_DIR
    / "comparison_v10_models_backtest_by_fold.csv"
)

RANKING_BY_FOLD_PATH = (
    RESULTS_DIR
    / "comparison_v10_models_ranking_by_fold.csv"
)

METADATA_PATH = (
    RESULTS_DIR
    / "comparison_v10_models_metadata.json"
)


# ============================================================
# DESCRIPCIÓN DE FAMILIAS
# ============================================================

FAMILIAS = {
    LR_MODEL:
        "LogisticRegression",

    HGB_MODEL:
        "HistGradientBoostingClassifier",

    MLP_MODEL:
        "MLPClassifier",
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def ruta_relativa(path):
    """
    Devuelve ruta relativa al proyecto.
    """

    return str(
        path.relative_to(PROJECT_ROOT)
    ).replace("\\", "/")


def validar_archivo(path):
    """
    Verifica existencia de archivo requerido.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"No existe el archivo requerido:\n{path}"
        )


def validar_archivos():
    """
    Verifica todos los insumos.
    """

    archivos = []

    archivos.extend(
        VALIDATION_METRICS_PATHS.values()
    )

    archivos.extend(
        VALIDATION_RANKING_PATHS.values()
    )

    archivos.extend(
        BACKTEST_METRICS_PATHS.values()
    )

    archivos.extend(
        BACKTEST_RANKING_PATHS.values()
    )

    archivos.extend(
        BACKTEST_SUMMARY_PATHS.values()
    )

    for archivo in archivos:

        validar_archivo(
            archivo
        )


# ============================================================
# VALIDATION 2020 - MÉTRICAS
# ============================================================

def cargar_validation_metrics(
    modelo,
):
    """
    Obtiene métricas de VALIDATION 2020.
    """

    path = VALIDATION_METRICS_PATHS[
        modelo
    ]

    df = pd.read_csv(
        path
    )

    columnas_requeridas = [
        "SPLIT",
        "OBSERVACIONES",
        "POSITIVOS",
        "PREVALENCIA",
        "PR_AUC",
        "ROC_AUC",
    ]

    faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df.columns
    ]

    if faltantes:

        raise ValueError(
            f"{modelo}: faltan columnas en métricas VALIDATION:\n"
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


# ============================================================
# VALIDATION 2020 - RANKING
# ============================================================

def cargar_validation_ranking(
    modelo,
):
    """
    Obtiene Top-K sobre VALIDATION 2020.
    """

    path = VALIDATION_RANKING_PATHS[
        modelo
    ]

    df = pd.read_csv(
        path
    )

    columnas_requeridas = [
        "SPLIT",
        "K",
        "POSITIVOS_TOP_K",
        "PRECISION_AT_K",
        "RECALL_AT_K",
        "LIFT_AT_K",
    ]

    faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df.columns
    ]

    if faltantes:

        raise ValueError(
            f"{modelo}: faltan columnas en ranking VALIDATION:\n"
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
# BACKTEST - RESUMEN
# ============================================================

def cargar_backtest_summary(
    modelo,
):
    """
    Carga la fila resumen correspondiente al modelo.
    """

    path = BACKTEST_SUMMARY_PATHS[
        modelo
    ]

    df = pd.read_csv(
        path
    )

    if "MODELO" not in df.columns:

        raise ValueError(
            f"{modelo}: falta columna MODELO en resumen."
        )

    fila = df[
        df[
            "MODELO"
        ]
        == modelo
    ]

    if len(fila) != 1:

        raise ValueError(
            f"{modelo}: se esperaba exactamente una fila "
            "en el resumen de backtesting."
        )

    return fila.iloc[
        0
    ]


def extraer_backtest_summary(
    fila,
):
    """
    Extrae las métricas comparables comunes.
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

        "BACKTEST_ROC_AUC_MEDIANA":
            float(
                fila[
                    "ROC_AUC_MEDIANA"
                ]
            ),

        "BACKTEST_ROC_AUC_STD":
            float(
                fila[
                    "ROC_AUC_STD"
                ]
            ),

        "BACKTEST_GAP_PR_AUC_MEDIO":
            float(
                fila[
                    "GAP_PR_AUC_MEDIO"
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
    Integra VALIDATION y backtesting de los tres modelos.
    """

    filas = []

    for modelo in MODELOS:

        validation_metrics = cargar_validation_metrics(
            modelo
        )

        validation_ranking = cargar_validation_ranking(
            modelo
        )

        backtest_summary = extraer_backtest_summary(
            cargar_backtest_summary(
                modelo
            )
        )

        filas.append(
            {
                "MODELO":
                    modelo,

                "FAMILIA":
                    FAMILIAS[
                        modelo
                    ],

                **validation_metrics,

                **validation_ranking,

                **backtest_summary,
            }
        )

    comparacion = pd.DataFrame(
        filas
    )

    return comparacion


# ============================================================
# CARGAR MÉTRICAS DE BACKTEST POR MODELO
# ============================================================

def cargar_metricas_backtest(
    modelo,
):
    """
    Carga y filtra métricas por fold.
    """

    path = BACKTEST_METRICS_PATHS[
        modelo
    ]

    df = pd.read_csv(
        path
    )

    if "MODELO" not in df.columns:

        raise ValueError(
            f"{modelo}: falta columna MODELO en backtest."
        )

    df = df[
        df[
            "MODELO"
        ]
        == modelo
    ].copy()

    if len(df) != 4:

        raise ValueError(
            f"{modelo}: se esperaban 4 folds y se encontraron "
            f"{len(df)}."
        )

    return df


# ============================================================
# COMPARACIÓN POR FOLD
# ============================================================

def construir_comparacion_por_fold():
    """
    Compara PR-AUC y ROC-AUC de los tres modelos por fold.
    """

    datos_modelos = {
        modelo:
            cargar_metricas_backtest(
                modelo
            )
        for modelo in MODELOS
    }

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

    control_base = (
        datos_modelos[
            LR_MODEL
        ][
            columnas_control
        ]
        .sort_values(
            "FOLD"
        )
        .reset_index(
            drop=True
        )
    )

    for modelo in [
        HGB_MODEL,
        MLP_MODEL,
    ]:

        control_modelo = (
            datos_modelos[
                modelo
            ][
                columnas_control
            ]
            .sort_values(
                "FOLD"
            )
            .reset_index(
                drop=True
            )
        )

        if not control_base.equals(
            control_modelo
        ):

            raise ValueError(
                f"Los folds de {modelo} no coinciden "
                "exactamente con el baseline LR."
            )

    comparacion = control_base.copy()

    prefijos = {
        LR_MODEL:
            "LR",

        HGB_MODEL:
            "HGB",

        MLP_MODEL:
            "MLP",
    }

    for modelo in MODELOS:

        prefijo = prefijos[
            modelo
        ]

        df = datos_modelos[
            modelo
        ][
            [
                "FOLD",
                "PR_AUC_TRAIN",
                "ROC_AUC_TRAIN",
                "PR_AUC_EVALUACION",
                "ROC_AUC_EVALUACION",
                "GAP_PR_AUC",
            ]
        ].copy()

        df = df.rename(
            columns={
                "PR_AUC_TRAIN":
                    f"{prefijo}_PR_AUC_TRAIN",

                "ROC_AUC_TRAIN":
                    f"{prefijo}_ROC_AUC_TRAIN",

                "PR_AUC_EVALUACION":
                    f"{prefijo}_PR_AUC_EVALUACION",

                "ROC_AUC_EVALUACION":
                    f"{prefijo}_ROC_AUC_EVALUACION",

                "GAP_PR_AUC":
                    f"{prefijo}_GAP_PR_AUC",
            }
        )

        comparacion = comparacion.merge(
            df,
            on="FOLD",
            how="inner",
        )

    comparacion[
        "DIF_HGB_MENOS_LR_PR_AUC"
    ] = (
        comparacion[
            "HGB_PR_AUC_EVALUACION"
        ]
        - comparacion[
            "LR_PR_AUC_EVALUACION"
        ]
    )

    comparacion[
        "DIF_MLP_MENOS_LR_PR_AUC"
    ] = (
        comparacion[
            "MLP_PR_AUC_EVALUACION"
        ]
        - comparacion[
            "LR_PR_AUC_EVALUACION"
        ]
    )

    comparacion[
        "DIF_MLP_MENOS_HGB_PR_AUC"
    ] = (
        comparacion[
            "MLP_PR_AUC_EVALUACION"
        ]
        - comparacion[
            "HGB_PR_AUC_EVALUACION"
        ]
    )

    return comparacion


# ============================================================
# CARGAR RANKING BACKTEST
# ============================================================

def cargar_ranking_backtest(
    modelo,
):
    """
    Carga ranking por fold de un modelo.
    """

    path = BACKTEST_RANKING_PATHS[
        modelo
    ]

    df = pd.read_csv(
        path
    )

    if "MODELO" not in df.columns:

        raise ValueError(
            f"{modelo}: falta columna MODELO en ranking."
        )

    df = df[
        df[
            "MODELO"
        ]
        == modelo
    ].copy()

    if len(df) != 12:

        raise ValueError(
            f"{modelo}: se esperaban 12 filas de ranking "
            "(4 folds x 3 K). "
            f"Se encontraron {len(df)}."
        )

    return df


# ============================================================
# COMPARACIÓN DE RANKING POR FOLD
# ============================================================

def construir_ranking_por_fold():
    """
    Compara Top 50, 100 y 200 en los cuatro folds.
    """

    datos = {
        modelo:
            cargar_ranking_backtest(
                modelo
            )
        for modelo in MODELOS
    }

    claves_control = [
        "FOLD",
        "ANIO_EVALUACION",
        "K",
        "N_EVALUACION",
        "POSITIVOS_EVALUACION",
    ]

    control_base = (
        datos[
            LR_MODEL
        ][
            claves_control
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

    for modelo in [
        HGB_MODEL,
        MLP_MODEL,
    ]:

        control_modelo = (
            datos[
                modelo
            ][
                claves_control
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

        if not control_base.equals(
            control_modelo
        ):

            raise ValueError(
                f"Los universos de ranking de {modelo} "
                "no coinciden con LR."
            )

    comparacion = control_base.copy()

    prefijos = {
        LR_MODEL:
            "LR",

        HGB_MODEL:
            "HGB",

        MLP_MODEL:
            "MLP",
    }

    for modelo in MODELOS:

        prefijo = prefijos[
            modelo
        ]

        df = datos[
            modelo
        ][
            [
                "FOLD",
                "ANIO_EVALUACION",
                "K",
                "POSITIVOS_TOP_K",
                "PRECISION_AT_K",
                "RECALL_AT_K",
                "LIFT_AT_K",
            ]
        ].copy()

        df = df.rename(
            columns={
                "POSITIVOS_TOP_K":
                    f"{prefijo}_POSITIVOS_TOP_K",

                "PRECISION_AT_K":
                    f"{prefijo}_PRECISION_AT_K",

                "RECALL_AT_K":
                    f"{prefijo}_RECALL_AT_K",

                "LIFT_AT_K":
                    f"{prefijo}_LIFT_AT_K",
            }
        )

        comparacion = comparacion.merge(
            df,
            on=[
                "FOLD",
                "ANIO_EVALUACION",
                "K",
            ],
            how="inner",
        )

    comparacion[
        "DIF_HGB_MENOS_LR_POSITIVOS"
    ] = (
        comparacion[
            "HGB_POSITIVOS_TOP_K"
        ]
        - comparacion[
            "LR_POSITIVOS_TOP_K"
        ]
    )

    comparacion[
        "DIF_MLP_MENOS_LR_POSITIVOS"
    ] = (
        comparacion[
            "MLP_POSITIVOS_TOP_K"
        ]
        - comparacion[
            "LR_POSITIVOS_TOP_K"
        ]
    )

    comparacion[
        "DIF_MLP_MENOS_HGB_POSITIVOS"
    ] = (
        comparacion[
            "MLP_POSITIVOS_TOP_K"
        ]
        - comparacion[
            "HGB_POSITIVOS_TOP_K"
        ]
    )

    return comparacion


# ============================================================
# METADATA
# ============================================================

def construir_metadata(
    comparacion,
    comparacion_fold,
):
    """
    Registra comparación de las tres familias.

    No selecciona modelo final.
    """

    datos_modelos = {}

    for modelo in MODELOS:

        fila = comparacion[
            comparacion[
                "MODELO"
            ]
            == modelo
        ].iloc[
            0
        ]

        datos_modelos[
            modelo
        ] = {
            "familia":
                FAMILIAS[
                    modelo
                ],

            "validation_pr_auc":
                float(
                    fila[
                        "VALIDATION_PR_AUC"
                    ]
                ),

            "validation_roc_auc":
                float(
                    fila[
                        "VALIDATION_ROC_AUC"
                    ]
                ),

            "validation_positivos_top_50":
                int(
                    fila[
                        "VALIDATION_POSITIVOS_TOP_50"
                    ]
                ),

            "validation_positivos_top_100":
                int(
                    fila[
                        "VALIDATION_POSITIVOS_TOP_100"
                    ]
                ),

            "validation_positivos_top_200":
                int(
                    fila[
                        "VALIDATION_POSITIVOS_TOP_200"
                    ]
                ),

            "backtest_pr_auc_media":
                float(
                    fila[
                        "BACKTEST_PR_AUC_MEDIA"
                    ]
                ),

            "backtest_pr_auc_std":
                float(
                    fila[
                        "BACKTEST_PR_AUC_STD"
                    ]
                ),

            "backtest_lift_50_media":
                float(
                    fila[
                        "BACKTEST_LIFT_AT_50_MEDIA"
                    ]
                ),

            "backtest_lift_100_media":
                float(
                    fila[
                        "BACKTEST_LIFT_AT_100_MEDIA"
                    ]
                ),

            "backtest_lift_200_media":
                float(
                    fila[
                        "BACKTEST_LIFT_AT_200_MEDIA"
                    ]
                ),
        }

    metadata = {
        "experimento":
            "Comparacion integral modelos v10",

        "fecha_ejecucion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "modelos_comparados":
            MODELOS,

        "familias":
            FAMILIAS,

        "objetivo":
            (
                "Comparar Logistic Regression, "
                "HistGradientBoosting y MLP bajo el mismo "
                "dataset, VALIDATION 2020 y protocolo "
                "temporal rolling-origin v10."
            ),

        "dataset_logico":
            "v10_features_core_2012_2023.csv.gz",

        "validation":
            {
                "anio":
                    2020,

                "utilizada_para_desarrollo":
                    True,
            },

        "backtesting":
            {
                "periodo":
                    "2012-2018",

                "numero_folds":
                    4,

                "embargo":
                    "1 año entre TRAIN y evaluación",
            },

        "resultados_por_modelo":
            datos_modelos,

        "criterios_principales": [
            "PR-AUC VALIDATION",
            "PR-AUC media backtest",
            "PR-AUC mediana backtest",
            "variabilidad temporal PR-AUC",
            "Precision@50",
            "Precision@100",
            "Precision@200",
            "Recall@50",
            "Recall@100",
            "Recall@200",
            "Lift@50",
            "Lift@100",
            "Lift@200",
            "comportamiento por fold",
            "gap TRAIN vs evaluación",
            "interpretabilidad",
            "riesgo de sobreajuste",
        ],

        "numero_folds_comparados":
            int(
                len(
                    comparacion_fold
                )
            ),

        "seleccion_modelo_final_realizada":
            False,

        "motivo_no_seleccion_final":
            (
                "La comparación corresponde todavía a la fase "
                "de desarrollo. Antes de cerrar el modelo final "
                "deben evaluarse los resultados conjuntamente, "
                "realizar interpretabilidad, analizar sesgos "
                "y decidir si procede ajuste controlado."
            ),

        "test":
            {
                "periodo":
                    "2022-2023",

                "utilizado":
                    False,

                "estado":
                    "RESERVADO - SIN EVALUACION",
            },

        "archivos_salida":
            {
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
# MOSTRAR TABLA GENERAL
# ============================================================

def mostrar_comparacion_general(
    comparacion,
):
    """
    Presenta principales resultados de forma compacta.
    """

    columnas = [
        "MODELO",
        "VALIDATION_PR_AUC",
        "VALIDATION_ROC_AUC",
        "VALIDATION_POSITIVOS_TOP_50",
        "VALIDATION_POSITIVOS_TOP_100",
        "VALIDATION_POSITIVOS_TOP_200",
        "BACKTEST_PR_AUC_MEDIA",
        "BACKTEST_PR_AUC_MEDIANA",
        "BACKTEST_PR_AUC_STD",
        "BACKTEST_LIFT_AT_50_MEDIA",
        "BACKTEST_LIFT_AT_100_MEDIA",
        "BACKTEST_LIFT_AT_200_MEDIA",
    ]

    print(
        comparacion[
            columnas
        ].to_string(
            index=False
        )
    )


# ============================================================
# MOSTRAR COMPARACIÓN POR FOLD
# ============================================================

def mostrar_comparacion_fold(
    comparacion_fold,
):
    """
    Presenta PR-AUC de los tres modelos para cada año.
    """

    columnas = [
        "FOLD",
        "ANIO_EVALUACION",
        "LR_PR_AUC_EVALUACION",
        "HGB_PR_AUC_EVALUACION",
        "MLP_PR_AUC_EVALUACION",
    ]

    print(
        comparacion_fold[
            columnas
        ].to_string(
            index=False
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        + "=" * 120
    )

    print(
        "PROSPECT FINDER BVQ"
    )

    print(
        "COMPARACIÓN INTEGRAL DE MODELOS v10"
    )

    print(
        "=" * 120
    )

    print(
        "\nModelos:"
    )

    print(
        f"1. {LR_MODEL}"
    )

    print(
        f"2. {HGB_MODEL}"
    )

    print(
        f"3. {MLP_MODEL}"
    )

    print(
        "\nVALIDATION: 2020"
    )

    print(
        "BACKTEST: 4 folds temporales"
    )

    print(
        "TEST 2022-2023: RESERVADO - SIN EVALUACIÓN"
    )

    # --------------------------------------------------------
    # VALIDAR ARCHIVOS
    # --------------------------------------------------------

    validar_archivos()

    # --------------------------------------------------------
    # COMPARACIÓN GENERAL
    # --------------------------------------------------------

    comparacion = construir_comparacion_general()

    # --------------------------------------------------------
    # COMPARACIÓN POR FOLD
    # --------------------------------------------------------

    comparacion_fold = construir_comparacion_por_fold()

    # --------------------------------------------------------
    # RANKING POR FOLD
    # --------------------------------------------------------

    ranking_fold = construir_ranking_por_fold()

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    metadata = construir_metadata(
        comparacion,
        comparacion_fold,
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

    comparacion_fold.to_csv(
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
    # MOSTRAR
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 120
    )

    print(
        "COMPARACIÓN GENERAL"
    )

    print(
        "=" * 120
    )

    mostrar_comparacion_general(
        comparacion
    )

    print(
        "\n"
        + "=" * 120
    )

    print(
        "PR-AUC POR FOLD"
    )

    print(
        "=" * 120
    )

    mostrar_comparacion_fold(
        comparacion_fold
    )

    # --------------------------------------------------------
    # CONTADORES DESCRIPTIVOS
    # --------------------------------------------------------

    lr_mejor = (
        (
            comparacion_fold[
                "LR_PR_AUC_EVALUACION"
            ]
            >
            comparacion_fold[
                "HGB_PR_AUC_EVALUACION"
            ]
        )
        &
        (
            comparacion_fold[
                "LR_PR_AUC_EVALUACION"
            ]
            >
            comparacion_fold[
                "MLP_PR_AUC_EVALUACION"
            ]
        )
    ).sum()

    hgb_mejor = (
        (
            comparacion_fold[
                "HGB_PR_AUC_EVALUACION"
            ]
            >
            comparacion_fold[
                "LR_PR_AUC_EVALUACION"
            ]
        )
        &
        (
            comparacion_fold[
                "HGB_PR_AUC_EVALUACION"
            ]
            >
            comparacion_fold[
                "MLP_PR_AUC_EVALUACION"
            ]
        )
    ).sum()

    mlp_mejor = (
        (
            comparacion_fold[
                "MLP_PR_AUC_EVALUACION"
            ]
            >
            comparacion_fold[
                "LR_PR_AUC_EVALUACION"
            ]
        )
        &
        (
            comparacion_fold[
                "MLP_PR_AUC_EVALUACION"
            ]
            >
            comparacion_fold[
                "HGB_PR_AUC_EVALUACION"
            ]
        )
    ).sum()

    print(
        "\nModelo con mayor PR-AUC por fold:"
    )

    print(
        f"LR:  {int(lr_mejor)} folds"
    )

    print(
        f"HGB: {int(hgb_mejor)} folds"
    )

    print(
        f"MLP: {int(mlp_mejor)} folds"
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
        "\nComparación integral v10 finalizada."
    )


if __name__ == "__main__":
    main()