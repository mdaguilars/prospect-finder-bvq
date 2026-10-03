from pathlib import Path
from datetime import datetime, timezone
import json
import platform
import sys

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]

RESULTS_DIR = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "v10"
)


# ============================================================
# ARCHIVOS DE ENTRADA
# ============================================================

CORE_COMPARISON_PATH = (
    RESULTS_DIR
    / "comparison_v10_models.csv"
)

LR_FINANCIAL_METRICS_PATH = (
    RESULTS_DIR
    / "v10_lr_financial_metrics.csv"
)

LR_FINANCIAL_RANKING_PATH = (
    RESULTS_DIR
    / "v10_lr_financial_ranking_metrics.csv"
)

LR_FINANCIAL_BACKTEST_PATH = (
    RESULTS_DIR
    / "backtest_lr_financial_v10_summary.csv"
)

MLP_FINANCIAL_METRICS_PATH = (
    RESULTS_DIR
    / "v10_mlp_financial_metrics.csv"
)

MLP_FINANCIAL_RANKING_PATH = (
    RESULTS_DIR
    / "v10_mlp_financial_ranking_metrics.csv"
)

MLP_FINANCIAL_BACKTEST_PATH = (
    RESULTS_DIR
    / "backtest_mlp_financial_v10_summary.csv"
)

HGB_TUNING_PATH = (
    RESULTS_DIR
    / "tune_hgb_financial_v10_summary.csv"
)


# ============================================================
# ARCHIVOS DE SALIDA
# ============================================================

COMPARISON_PATH = (
    RESULTS_DIR
    / "comparison_v10_final_candidates.csv"
)

FAMILY_DELTA_PATH = (
    RESULTS_DIR
    / "comparison_v10_final_candidates_family_delta.csv"
)

FAMILY_CANDIDATES_PATH = (
    RESULTS_DIR
    / "comparison_v10_family_candidates.csv"
)

METADATA_PATH = (
    RESULTS_DIR
    / "comparison_v10_final_candidates_metadata.json"
)


# ============================================================
# UNIVERSO DE VALIDACIÓN CONGELADO
# ============================================================

VALIDATION_N = 98_471
VALIDATION_POSITIVES = 34

VALIDATION_PREVALENCE = (
    VALIDATION_POSITIVES
    / VALIDATION_N
)


# ============================================================
# MODELOS A COMPARAR
# ============================================================

CORE_MODELS = [
    "v10_lr_no_provincia",
    "v10_hgb",
    "v10_mlp",
]

HGB_FINANCIAL_CONFIG = (
    "C3_CONSERVATIVE"
)


# ============================================================
# SELECCIÓN PREVIA POR FAMILIA
# ============================================================

#
# Esta selección NO es el modelo final del proyecto.
#
# Únicamente identifica qué variante de cada familia
# pasa a la comparación final previa a TEST.
#

FAMILY_SELECTION = {
    "LogisticRegression":
        "v10_lr_no_provincia",

    "HistGradientBoostingClassifier":
        "v10_hgb_financial_c3",

    "MLPClassifier":
        "v10_mlp",
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def ruta_relativa(
    path,
):

    return str(
        path.relative_to(
            PROJECT_ROOT
        )
    ).replace(
        "\\",
        "/",
    )


def validar_archivo(
    path,
):

    if not path.exists():

        raise FileNotFoundError(
            f"No existe el archivo requerido:\n"
            f"{path}"
        )


def a_float(
    valor,
):

    if pd.isna(
        valor
    ):

        return np.nan

    return float(
        valor
    )


def a_int(
    valor,
):

    if pd.isna(
        valor
    ):

        return np.nan

    return int(
        float(
            valor
        )
    )


# ============================================================
# VALIDAR ENTRADAS
# ============================================================

def validar_entradas():

    archivos = [
        CORE_COMPARISON_PATH,
        LR_FINANCIAL_METRICS_PATH,
        LR_FINANCIAL_RANKING_PATH,
        LR_FINANCIAL_BACKTEST_PATH,
        MLP_FINANCIAL_METRICS_PATH,
        MLP_FINANCIAL_RANKING_PATH,
        MLP_FINANCIAL_BACKTEST_PATH,
        HGB_TUNING_PATH,
    ]

    for archivo in archivos:

        validar_archivo(
            archivo
        )


# ============================================================
# EXTRAER MODELOS CORE
# ============================================================

def cargar_core():

    df = pd.read_csv(
        CORE_COMPARISON_PATH
    )

    faltantes = [
        modelo
        for modelo in CORE_MODELS
        if modelo
        not in set(
            df[
                "MODELO"
            ]
        )
    ]

    if faltantes:

        raise ValueError(
            "Faltan modelos core en "
            "comparison_v10_models.csv:\n"
            + "\n".join(
                faltantes
            )
        )

    filas = []

    for modelo in CORE_MODELS:

        row = df[
            df[
                "MODELO"
            ]
            == modelo
        ].iloc[
            0
        ]

        if modelo == "v10_lr_no_provincia":

            familia = (
                "LogisticRegression"
            )

            variante = "CORE"

            n_features = 15

        elif modelo == "v10_hgb":

            familia = (
                "HistGradientBoostingClassifier"
            )

            variante = "CORE"

            n_features = 15

        elif modelo == "v10_mlp":

            familia = (
                "MLPClassifier"
            )

            variante = "CORE"

            n_features = 15

        else:

            raise ValueError(
                f"Modelo core inesperado: "
                f"{modelo}"
            )

        filas.append(
            {
                "MODELO":
                    modelo,

                "FAMILIA":
                    familia,

                "VARIANTE":
                    variante,

                "N_FEATURES_FISICAS":
                    n_features,

                "VALIDATION_OBSERVACIONES":
                    a_int(
                        row[
                            "VALIDATION_OBSERVACIONES"
                        ]
                    ),

                "VALIDATION_POSITIVOS":
                    a_int(
                        row[
                            "VALIDATION_POSITIVOS"
                        ]
                    ),

                "VALIDATION_PREVALENCIA":
                    a_float(
                        row[
                            "VALIDATION_PREVALENCIA"
                        ]
                    ),

                "VALIDATION_PR_AUC":
                    a_float(
                        row[
                            "VALIDATION_PR_AUC"
                        ]
                    ),

                "VALIDATION_ROC_AUC":
                    a_float(
                        row[
                            "VALIDATION_ROC_AUC"
                        ]
                    ),

                "VALIDATION_POSITIVOS_TOP_50":
                    a_int(
                        row[
                            "VALIDATION_POSITIVOS_TOP_50"
                        ]
                    ),

                "VALIDATION_LIFT_AT_50":
                    a_float(
                        row[
                            "VALIDATION_LIFT_AT_50"
                        ]
                    ),

                "VALIDATION_POSITIVOS_TOP_100":
                    a_int(
                        row[
                            "VALIDATION_POSITIVOS_TOP_100"
                        ]
                    ),

                "VALIDATION_LIFT_AT_100":
                    a_float(
                        row[
                            "VALIDATION_LIFT_AT_100"
                        ]
                    ),

                "VALIDATION_POSITIVOS_TOP_200":
                    a_int(
                        row[
                            "VALIDATION_POSITIVOS_TOP_200"
                        ]
                    ),

                "VALIDATION_LIFT_AT_200":
                    a_float(
                        row[
                            "VALIDATION_LIFT_AT_200"
                        ]
                    ),

                "BACKTEST_N_FOLDS":
                    a_int(
                        row[
                            "BACKTEST_N_FOLDS"
                        ]
                    ),

                "BACKTEST_PR_AUC_MEDIA":
                    a_float(
                        row[
                            "BACKTEST_PR_AUC_MEDIA"
                        ]
                    ),

                "BACKTEST_PR_AUC_MEDIANA":
                    a_float(
                        row[
                            "BACKTEST_PR_AUC_MEDIANA"
                        ]
                    ),

                "BACKTEST_PR_AUC_STD":
                    a_float(
                        row[
                            "BACKTEST_PR_AUC_STD"
                        ]
                    ),

                "BACKTEST_PR_AUC_MIN":
                    a_float(
                        row[
                            "BACKTEST_PR_AUC_MIN"
                        ]
                    ),

                "BACKTEST_PR_AUC_MAX":
                    a_float(
                        row[
                            "BACKTEST_PR_AUC_MAX"
                        ]
                    ),

                "BACKTEST_ROC_AUC_MEDIA":
                    a_float(
                        row[
                            "BACKTEST_ROC_AUC_MEDIA"
                        ]
                    ),

                "BACKTEST_GAP_PR_AUC_MEDIO":
                    a_float(
                        row[
                            "BACKTEST_GAP_PR_AUC_MEDIO"
                        ]
                    ),

                "BACKTEST_POSITIVOS_TOP_50_TOTAL":
                    a_int(
                        row[
                            "BACKTEST_POSITIVOS_TOP_50_TOTAL"
                        ]
                    ),

                "BACKTEST_LIFT_AT_50_MEDIA":
                    a_float(
                        row[
                            "BACKTEST_LIFT_AT_50_MEDIA"
                        ]
                    ),

                "BACKTEST_POSITIVOS_TOP_100_TOTAL":
                    a_int(
                        row[
                            "BACKTEST_POSITIVOS_TOP_100_TOTAL"
                        ]
                    ),

                "BACKTEST_LIFT_AT_100_MEDIA":
                    a_float(
                        row[
                            "BACKTEST_LIFT_AT_100_MEDIA"
                        ]
                    ),

                "BACKTEST_POSITIVOS_TOP_200_TOTAL":
                    a_int(
                        row[
                            "BACKTEST_POSITIVOS_TOP_200_TOTAL"
                        ]
                    ),

                "BACKTEST_LIFT_AT_200_MEDIA":
                    a_float(
                        row[
                            "BACKTEST_LIFT_AT_200_MEDIA"
                        ]
                    ),
            }
        )

    return filas


# ============================================================
# EXTRAER LR FINANCIERA
# ============================================================

def cargar_lr_financial():

    metrics = pd.read_csv(
        LR_FINANCIAL_METRICS_PATH
    )

    ranking = pd.read_csv(
        LR_FINANCIAL_RANKING_PATH
    )

    backtest = pd.read_csv(
        LR_FINANCIAL_BACKTEST_PATH
    )

    validation = metrics[
        metrics[
            "SPLIT"
        ]
        == "VALIDATION"
    ]

    if len(
        validation
    ) != 1:

        raise ValueError(
            "No se encontró exactamente "
            "una fila VALIDATION para "
            "v10_lr_financial."
        )

    validation = validation.iloc[
        0
    ]

    backtest = backtest.iloc[
        0
    ]

    def ranking_k(
        k,
    ):

        bloque = ranking[
            ranking[
                "K"
            ]
            == k
        ]

        if len(
            bloque
        ) != 1:

            raise ValueError(
                f"LR financial: "
                f"ranking K={k} inválido."
            )

        return bloque.iloc[
            0
        ]

    r50 = ranking_k(
        50
    )

    r100 = ranking_k(
        100
    )

    r200 = ranking_k(
        200
    )

    return {
        "MODELO":
            "v10_lr_financial",

        "FAMILIA":
            "LogisticRegression",

        "VARIANTE":
            "FINANCIAL",

        "N_FEATURES_FISICAS":
            25,

        "VALIDATION_OBSERVACIONES":
            VALIDATION_N,

        "VALIDATION_POSITIVOS":
            VALIDATION_POSITIVES,

        "VALIDATION_PREVALENCIA":
            VALIDATION_PREVALENCE,

        "VALIDATION_PR_AUC":
            a_float(
                validation[
                    "PR_AUC"
                ]
            ),

        "VALIDATION_ROC_AUC":
            a_float(
                validation[
                    "ROC_AUC"
                ]
            ),

        "VALIDATION_POSITIVOS_TOP_50":
            a_int(
                r50[
                    "POSITIVOS_TOP_K"
                ]
            ),

        "VALIDATION_LIFT_AT_50":
            a_float(
                r50[
                    "LIFT_AT_K"
                ]
            ),

        "VALIDATION_POSITIVOS_TOP_100":
            a_int(
                r100[
                    "POSITIVOS_TOP_K"
                ]
            ),

        "VALIDATION_LIFT_AT_100":
            a_float(
                r100[
                    "LIFT_AT_K"
                ]
            ),

        "VALIDATION_POSITIVOS_TOP_200":
            a_int(
                r200[
                    "POSITIVOS_TOP_K"
                ]
            ),

        "VALIDATION_LIFT_AT_200":
            a_float(
                r200[
                    "LIFT_AT_K"
                ]
            ),

        "BACKTEST_N_FOLDS":
            a_int(
                backtest[
                    "N_FOLDS"
                ]
            ),

        "BACKTEST_PR_AUC_MEDIA":
            a_float(
                backtest[
                    "PR_AUC_MEDIA"
                ]
            ),

        "BACKTEST_PR_AUC_MEDIANA":
            a_float(
                backtest[
                    "PR_AUC_MEDIANA"
                ]
            ),

        "BACKTEST_PR_AUC_STD":
            a_float(
                backtest[
                    "PR_AUC_STD"
                ]
            ),

        "BACKTEST_PR_AUC_MIN":
            a_float(
                backtest[
                    "PR_AUC_MIN"
                ]
            ),

        "BACKTEST_PR_AUC_MAX":
            a_float(
                backtest[
                    "PR_AUC_MAX"
                ]
            ),

        "BACKTEST_ROC_AUC_MEDIA":
            a_float(
                backtest[
                    "ROC_AUC_MEDIA"
                ]
            ),

        "BACKTEST_GAP_PR_AUC_MEDIO":
            a_float(
                backtest[
                    "GAP_PR_AUC_MEDIO"
                ]
            ),

        "BACKTEST_POSITIVOS_TOP_50_TOTAL":
            a_int(
                backtest[
                    "POSITIVOS_TOP_50_TOTAL"
                ]
            ),

        "BACKTEST_LIFT_AT_50_MEDIA":
            a_float(
                backtest[
                    "LIFT_AT_50_MEDIA"
                ]
            ),

        "BACKTEST_POSITIVOS_TOP_100_TOTAL":
            a_int(
                backtest[
                    "POSITIVOS_TOP_100_TOTAL"
                ]
            ),

        "BACKTEST_LIFT_AT_100_MEDIA":
            a_float(
                backtest[
                    "LIFT_AT_100_MEDIA"
                ]
            ),

        "BACKTEST_POSITIVOS_TOP_200_TOTAL":
            a_int(
                backtest[
                    "POSITIVOS_TOP_200_TOTAL"
                ]
            ),

        "BACKTEST_LIFT_AT_200_MEDIA":
            a_float(
                backtest[
                    "LIFT_AT_200_MEDIA"
                ]
            ),
    }


# ============================================================
# EXTRAER MLP FINANCIERO
# ============================================================

def cargar_mlp_financial():

    metrics = pd.read_csv(
        MLP_FINANCIAL_METRICS_PATH
    )

    ranking = pd.read_csv(
        MLP_FINANCIAL_RANKING_PATH
    )

    backtest = pd.read_csv(
        MLP_FINANCIAL_BACKTEST_PATH
    )

    validation = metrics[
        metrics[
            "SPLIT"
        ]
        == "VALIDATION"
    ]

    if len(
        validation
    ) != 1:

        raise ValueError(
            "No se encontró exactamente "
            "una fila VALIDATION para "
            "v10_mlp_financial."
        )

    validation = validation.iloc[
        0
    ]

    backtest = backtest.iloc[
        0
    ]

    def ranking_k(
        k,
    ):

        bloque = ranking[
            ranking[
                "K"
            ]
            == k
        ]

        if len(
            bloque
        ) != 1:

            raise ValueError(
                f"MLP financial: "
                f"ranking K={k} inválido."
            )

        return bloque.iloc[
            0
        ]

    r50 = ranking_k(
        50
    )

    r100 = ranking_k(
        100
    )

    r200 = ranking_k(
        200
    )

    return {
        "MODELO":
            "v10_mlp_financial",

        "FAMILIA":
            "MLPClassifier",

        "VARIANTE":
            "FINANCIAL",

        "N_FEATURES_FISICAS":
            25,

        "VALIDATION_OBSERVACIONES":
            a_int(
                validation[
                    "N"
                ]
            ),

        "VALIDATION_POSITIVOS":
            a_int(
                validation[
                    "POSITIVOS"
                ]
            ),

        "VALIDATION_PREVALENCIA":
            a_float(
                validation[
                    "PREVALENCIA"
                ]
            ),

        "VALIDATION_PR_AUC":
            a_float(
                validation[
                    "PR_AUC"
                ]
            ),

        "VALIDATION_ROC_AUC":
            a_float(
                validation[
                    "ROC_AUC"
                ]
            ),

        "VALIDATION_POSITIVOS_TOP_50":
            a_int(
                r50[
                    "POSITIVOS_TOP_K"
                ]
            ),

        "VALIDATION_LIFT_AT_50":
            a_float(
                r50[
                    "LIFT_AT_K"
                ]
            ),

        "VALIDATION_POSITIVOS_TOP_100":
            a_int(
                r100[
                    "POSITIVOS_TOP_K"
                ]
            ),

        "VALIDATION_LIFT_AT_100":
            a_float(
                r100[
                    "LIFT_AT_K"
                ]
            ),

        "VALIDATION_POSITIVOS_TOP_200":
            a_int(
                r200[
                    "POSITIVOS_TOP_K"
                ]
            ),

        "VALIDATION_LIFT_AT_200":
            a_float(
                r200[
                    "LIFT_AT_K"
                ]
            ),

        "BACKTEST_N_FOLDS":
            a_int(
                backtest[
                    "N_FOLDS"
                ]
            ),

        "BACKTEST_PR_AUC_MEDIA":
            a_float(
                backtest[
                    "PR_AUC_MEDIA"
                ]
            ),

        "BACKTEST_PR_AUC_MEDIANA":
            a_float(
                backtest[
                    "PR_AUC_MEDIANA"
                ]
            ),

        "BACKTEST_PR_AUC_STD":
            a_float(
                backtest[
                    "PR_AUC_STD"
                ]
            ),

        "BACKTEST_PR_AUC_MIN":
            a_float(
                backtest[
                    "PR_AUC_MIN"
                ]
            ),

        "BACKTEST_PR_AUC_MAX":
            a_float(
                backtest[
                    "PR_AUC_MAX"
                ]
            ),

        "BACKTEST_ROC_AUC_MEDIA":
            a_float(
                backtest[
                    "ROC_AUC_MEDIA"
                ]
            ),

        "BACKTEST_GAP_PR_AUC_MEDIO":
            a_float(
                backtest[
                    "GAP_PR_AUC_MEDIO"
                ]
            ),

        "BACKTEST_POSITIVOS_TOP_50_TOTAL":
            a_int(
                backtest[
                    "POSITIVOS_TOP_50_TOTAL"
                ]
            ),

        "BACKTEST_LIFT_AT_50_MEDIA":
            a_float(
                backtest[
                    "LIFT_AT_50_MEDIA"
                ]
            ),

        "BACKTEST_POSITIVOS_TOP_100_TOTAL":
            a_int(
                backtest[
                    "POSITIVOS_TOP_100_TOTAL"
                ]
            ),

        "BACKTEST_LIFT_AT_100_MEDIA":
            a_float(
                backtest[
                    "LIFT_AT_100_MEDIA"
                ]
            ),

        "BACKTEST_POSITIVOS_TOP_200_TOTAL":
            a_int(
                backtest[
                    "POSITIVOS_TOP_200_TOTAL"
                ]
            ),

        "BACKTEST_LIFT_AT_200_MEDIA":
            a_float(
                backtest[
                    "LIFT_AT_200_MEDIA"
                ]
            ),
    }


# ============================================================
# EXTRAER HGB FINANCIERO C3
# ============================================================

def cargar_hgb_financial_c3():

    tuning = pd.read_csv(
        HGB_TUNING_PATH
    )

    bloque = tuning[
        tuning[
            "CONFIG_ID"
        ]
        == HGB_FINANCIAL_CONFIG
    ]

    if len(
        bloque
    ) != 1:

        raise ValueError(
            "No se encontró exactamente "
            "una configuración "
            "C3_CONSERVATIVE."
        )

    row = bloque.iloc[
        0
    ]

    return {
        "MODELO":
            "v10_hgb_financial_c3",

        "FAMILIA":
            "HistGradientBoostingClassifier",

        "VARIANTE":
            "FINANCIAL_C3",

        "N_FEATURES_FISICAS":
            a_int(
                row[
                    "N_FEATURES"
                ]
            ),

        "VALIDATION_OBSERVACIONES":
            VALIDATION_N,

        "VALIDATION_POSITIVOS":
            VALIDATION_POSITIVES,

        "VALIDATION_PREVALENCIA":
            VALIDATION_PREVALENCE,

        "VALIDATION_PR_AUC":
            a_float(
                row[
                    "VALIDATION_PR_AUC"
                ]
            ),

        "VALIDATION_ROC_AUC":
            a_float(
                row[
                    "VALIDATION_ROC_AUC"
                ]
            ),

        "VALIDATION_POSITIVOS_TOP_50":
            a_int(
                row[
                    "VALIDATION_POSITIVOS_TOP_50"
                ]
            ),

        "VALIDATION_LIFT_AT_50":
            np.nan,

        "VALIDATION_POSITIVOS_TOP_100":
            a_int(
                row[
                    "VALIDATION_POSITIVOS_TOP_100"
                ]
            ),

        "VALIDATION_LIFT_AT_100":
            np.nan,

        "VALIDATION_POSITIVOS_TOP_200":
            a_int(
                row[
                    "VALIDATION_POSITIVOS_TOP_200"
                ]
            ),

        "VALIDATION_LIFT_AT_200":
            np.nan,

        "BACKTEST_N_FOLDS":
            4,

        "BACKTEST_PR_AUC_MEDIA":
            a_float(
                row[
                    "BACKTEST_PR_AUC_MEDIA"
                ]
            ),

        "BACKTEST_PR_AUC_MEDIANA":
            a_float(
                row[
                    "BACKTEST_PR_AUC_MEDIANA"
                ]
            ),

        "BACKTEST_PR_AUC_STD":
            a_float(
                row[
                    "BACKTEST_PR_AUC_STD"
                ]
            ),

        "BACKTEST_PR_AUC_MIN":
            a_float(
                row[
                    "BACKTEST_PR_AUC_MIN"
                ]
            ),

        "BACKTEST_PR_AUC_MAX":
            a_float(
                row[
                    "BACKTEST_PR_AUC_MAX"
                ]
            ),

        "BACKTEST_ROC_AUC_MEDIA":
            a_float(
                row[
                    "BACKTEST_ROC_AUC_MEDIA"
                ]
            ),

        "BACKTEST_GAP_PR_AUC_MEDIO":
            a_float(
                row[
                    "BACKTEST_GAP_PR_AUC_MEDIO"
                ]
            ),

        "BACKTEST_POSITIVOS_TOP_50_TOTAL":
            a_int(
                row[
                    "BACKTEST_POSITIVOS_TOP_50_TOTAL"
                ]
            ),

        "BACKTEST_LIFT_AT_50_MEDIA":
            a_float(
                row[
                    "BACKTEST_LIFT_AT_50_MEDIA"
                ]
            ),

        "BACKTEST_POSITIVOS_TOP_100_TOTAL":
            a_int(
                row[
                    "BACKTEST_POSITIVOS_TOP_100_TOTAL"
                ]
            ),

        "BACKTEST_LIFT_AT_100_MEDIA":
            a_float(
                row[
                    "BACKTEST_LIFT_AT_100_MEDIA"
                ]
            ),

        "BACKTEST_POSITIVOS_TOP_200_TOTAL":
            a_int(
                row[
                    "BACKTEST_POSITIVOS_TOP_200_TOTAL"
                ]
            ),

        "BACKTEST_LIFT_AT_200_MEDIA":
            a_float(
                row[
                    "BACKTEST_LIFT_AT_200_MEDIA"
                ]
            ),
    }


# ============================================================
# COMPLETAR LIFT VALIDATION HGB C3
# ============================================================

def completar_lift_validation(
    dataframe,
):

    df = dataframe.copy()

    mascara = (
        df[
            "MODELO"
        ]
        == "v10_hgb_financial_c3"
    )

    for k in [
        50,
        100,
        200,
    ]:

        positivos_col = (
            f"VALIDATION_POSITIVOS_TOP_{k}"
        )

        lift_col = (
            f"VALIDATION_LIFT_AT_{k}"
        )

        positivos = df.loc[
            mascara,
            positivos_col,
        ].iloc[
            0
        ]

        precision = (
            positivos
            / k
        )

        lift = (
            precision
            / VALIDATION_PREVALENCE
        )

        df.loc[
            mascara,
            lift_col,
        ] = lift

    return df


# ============================================================
# MARCAR CANDIDATO POR FAMILIA
# ============================================================

def marcar_candidatos(
    dataframe,
):

    df = dataframe.copy()

    df[
        "CANDIDATO_FAMILIA"
    ] = False

    for familia, modelo in (
        FAMILY_SELECTION.items()
    ):

        mascara = (
            (
                df[
                    "FAMILIA"
                ]
                == familia
            )
            &
            (
                df[
                    "MODELO"
                ]
                == modelo
            )
        )

        if mascara.sum() != 1:

            raise ValueError(
                f"No se pudo identificar "
                f"el candidato de "
                f"{familia}: {modelo}"
            )

        df.loc[
            mascara,
            "CANDIDATO_FAMILIA",
        ] = True

    return df


# ============================================================
# COMPARACIÓN CORE VS FINANCIAL POR FAMILIA
# ============================================================

def construir_delta_familia(
    dataframe,
):

    pares = [
        {
            "FAMILIA":
                "LogisticRegression",

            "CORE":
                "v10_lr_no_provincia",

            "FINANCIAL":
                "v10_lr_financial",
        },

        {
            "FAMILIA":
                "HistGradientBoostingClassifier",

            "CORE":
                "v10_hgb",

            "FINANCIAL":
                "v10_hgb_financial_c3",
        },

        {
            "FAMILIA":
                "MLPClassifier",

            "CORE":
                "v10_mlp",

            "FINANCIAL":
                "v10_mlp_financial",
        },
    ]

    filas = []

    for par in pares:

        core = dataframe[
            dataframe[
                "MODELO"
            ]
            == par[
                "CORE"
            ]
        ].iloc[
            0
        ]

        financial = dataframe[
            dataframe[
                "MODELO"
            ]
            == par[
                "FINANCIAL"
            ]
        ].iloc[
            0
        ]

        pr_core = core[
            "BACKTEST_PR_AUC_MEDIA"
        ]

        pr_fin = financial[
            "BACKTEST_PR_AUC_MEDIA"
        ]

        delta_pr = (
            pr_fin
            - pr_core
        )

        if pr_core != 0:

            delta_pr_pct = (
                delta_pr
                / pr_core
            )

        else:

            delta_pr_pct = np.nan

        filas.append(
            {
                "FAMILIA":
                    par[
                        "FAMILIA"
                    ],

                "MODELO_CORE":
                    par[
                        "CORE"
                    ],

                "MODELO_FINANCIAL":
                    par[
                        "FINANCIAL"
                    ],

                "CORE_VALIDATION_PR_AUC":
                    core[
                        "VALIDATION_PR_AUC"
                    ],

                "FINANCIAL_VALIDATION_PR_AUC":
                    financial[
                        "VALIDATION_PR_AUC"
                    ],

                "DELTA_VALIDATION_PR_AUC":
                    (
                        financial[
                            "VALIDATION_PR_AUC"
                        ]
                        -
                        core[
                            "VALIDATION_PR_AUC"
                        ]
                    ),

                "CORE_BACKTEST_PR_AUC_MEDIA":
                    pr_core,

                "FINANCIAL_BACKTEST_PR_AUC_MEDIA":
                    pr_fin,

                "DELTA_BACKTEST_PR_AUC_MEDIA":
                    delta_pr,

                "DELTA_BACKTEST_PR_AUC_PCT":
                    delta_pr_pct,

                "CORE_BACKTEST_PR_AUC_STD":
                    core[
                        "BACKTEST_PR_AUC_STD"
                    ],

                "FINANCIAL_BACKTEST_PR_AUC_STD":
                    financial[
                        "BACKTEST_PR_AUC_STD"
                    ],

                "DELTA_BACKTEST_PR_AUC_STD":
                    (
                        financial[
                            "BACKTEST_PR_AUC_STD"
                        ]
                        -
                        core[
                            "BACKTEST_PR_AUC_STD"
                        ]
                    ),

                "CORE_LIFT_AT_50_MEDIA":
                    core[
                        "BACKTEST_LIFT_AT_50_MEDIA"
                    ],

                "FINANCIAL_LIFT_AT_50_MEDIA":
                    financial[
                        "BACKTEST_LIFT_AT_50_MEDIA"
                    ],

                "DELTA_LIFT_AT_50_MEDIA":
                    (
                        financial[
                            "BACKTEST_LIFT_AT_50_MEDIA"
                        ]
                        -
                        core[
                            "BACKTEST_LIFT_AT_50_MEDIA"
                        ]
                    ),

                "CORE_LIFT_AT_100_MEDIA":
                    core[
                        "BACKTEST_LIFT_AT_100_MEDIA"
                    ],

                "FINANCIAL_LIFT_AT_100_MEDIA":
                    financial[
                        "BACKTEST_LIFT_AT_100_MEDIA"
                    ],

                "DELTA_LIFT_AT_100_MEDIA":
                    (
                        financial[
                            "BACKTEST_LIFT_AT_100_MEDIA"
                        ]
                        -
                        core[
                            "BACKTEST_LIFT_AT_100_MEDIA"
                        ]
                    ),

                "CORE_LIFT_AT_200_MEDIA":
                    core[
                        "BACKTEST_LIFT_AT_200_MEDIA"
                    ],

                "FINANCIAL_LIFT_AT_200_MEDIA":
                    financial[
                        "BACKTEST_LIFT_AT_200_MEDIA"
                    ],

                "DELTA_LIFT_AT_200_MEDIA":
                    (
                        financial[
                            "BACKTEST_LIFT_AT_200_MEDIA"
                        ]
                        -
                        core[
                            "BACKTEST_LIFT_AT_200_MEDIA"
                        ]
                    ),

                "CORE_GAP_PR_AUC_MEDIO":
                    core[
                        "BACKTEST_GAP_PR_AUC_MEDIO"
                    ],

                "FINANCIAL_GAP_PR_AUC_MEDIO":
                    financial[
                        "BACKTEST_GAP_PR_AUC_MEDIO"
                    ],
            }
        )

    return pd.DataFrame(
        filas
    )


# ============================================================
# TABLA DE CANDIDATOS POR FAMILIA
# ============================================================

def construir_candidatos_familia(
    dataframe,
):

    candidatos = dataframe[
        dataframe[
            "CANDIDATO_FAMILIA"
        ]
    ].copy()

    columnas = [
        "MODELO",
        "FAMILIA",
        "VARIANTE",
        "N_FEATURES_FISICAS",
        "VALIDATION_PR_AUC",
        "VALIDATION_ROC_AUC",
        "VALIDATION_POSITIVOS_TOP_50",
        "VALIDATION_POSITIVOS_TOP_100",
        "VALIDATION_POSITIVOS_TOP_200",
        "BACKTEST_PR_AUC_MEDIA",
        "BACKTEST_PR_AUC_MEDIANA",
        "BACKTEST_PR_AUC_STD",
        "BACKTEST_PR_AUC_MIN",
        "BACKTEST_PR_AUC_MAX",
        "BACKTEST_ROC_AUC_MEDIA",
        "BACKTEST_GAP_PR_AUC_MEDIO",
        "BACKTEST_POSITIVOS_TOP_50_TOTAL",
        "BACKTEST_LIFT_AT_50_MEDIA",
        "BACKTEST_POSITIVOS_TOP_100_TOTAL",
        "BACKTEST_LIFT_AT_100_MEDIA",
        "BACKTEST_POSITIVOS_TOP_200_TOTAL",
        "BACKTEST_LIFT_AT_200_MEDIA",
    ]

    candidatos = candidatos[
        columnas
    ].copy()

    candidatos = candidatos.sort_values(
        [
            "FAMILIA",
        ]
    ).reset_index(
        drop=True
    )

    return candidatos


# ============================================================
# VALIDACIONES DE CONSISTENCIA
# ============================================================

def validar_comparacion(
    dataframe,
):

    if len(
        dataframe
    ) != 6:

        raise ValueError(
            "La comparación debe contener "
            "exactamente 6 experimentos."
        )

    if dataframe[
        "MODELO"
    ].duplicated().any():

        raise ValueError(
            "Existen modelos duplicados "
            "en la comparación."
        )

    if dataframe[
        "CANDIDATO_FAMILIA"
    ].sum() != 3:

        raise ValueError(
            "Deben existir exactamente "
            "3 candidatos por familia."
        )

    if not (
        dataframe[
            "VALIDATION_OBSERVACIONES"
        ]
        == VALIDATION_N
    ).all():

        raise ValueError(
            "No todos los modelos utilizan "
            "el mismo universo VALIDATION."
        )

    if not (
        dataframe[
            "VALIDATION_POSITIVOS"
        ]
        == VALIDATION_POSITIVES
    ).all():

        raise ValueError(
            "No todos los modelos tienen "
            "el mismo número de positivos "
            "en VALIDATION."
        )

    if not (
        dataframe[
            "BACKTEST_N_FOLDS"
        ]
        == 4
    ).all():

        raise ValueError(
            "No todos los experimentos "
            "utilizan los 4 folds "
            "temporales congelados."
        )


# ============================================================
# METADATA
# ============================================================

def construir_metadata(
    comparison_df,
    delta_df,
    candidates_df,
):

    return {
        "experimento":
            (
                "Comparacion integral v10 "
                "previa a seleccion final "
                "y apertura de TEST"
            ),

        "fecha_ejecucion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "objetivo":
            (
                "Consolidar los resultados "
                "ya obtenidos para las "
                "familias LogisticRegression, "
                "HistGradientBoostingClassifier "
                "y MLPClassifier, comparando "
                "sus variantes core y "
                "financieras."
            ),

        "modelos_comparados":
            comparison_df[
                "MODELO"
            ].tolist(),

        "candidatos_por_familia":
            candidates_df[
                [
                    "FAMILIA",
                    "MODELO",
                ]
            ].to_dict(
                orient="records"
            ),

        "seleccion_final_proyecto":
            {
                "realizada":
                    False,

                "motivo":
                    (
                        "Este paso únicamente "
                        "reduce cada familia "
                        "a un candidato. "
                        "La selección final "
                        "se realizará después "
                        "de revisar el "
                        "comparador integral "
                        "y antes de abrir TEST."
                    ),
            },

        "criterios_principales":
            [
                "PR-AUC en backtest temporal",
                "mediana PR-AUC en backtest",
                "desviacion temporal PR-AUC",
                "Lift@50",
                "Lift@100",
                "Lift@200",
                "positivos recuperados en ranking",
                "brecha TRAIN-evaluacion",
                "comportamiento en VALIDATION",
            ],

        "protocolo":
            {
                "validation":
                    {
                        "anio":
                            2020,

                        "observaciones":
                            VALIDATION_N,

                        "positivos":
                            VALIDATION_POSITIVES,
                    },

                "backtest":
                    {
                        "folds":
                            4,

                        "evaluacion":
                            [
                                2015,
                                2016,
                                2017,
                                2018,
                            ],

                        "embargo":
                            (
                                "1 año entre TRAIN "
                                "y evaluación"
                            ),
                    },
            },

        "test":
            {
                "periodo":
                    "2022-2023",

                "estado":
                    "RESERVADO",

                "cargado_por_este_script":
                    False,

                "evaluado_por_este_script":
                    False,

                "regla":
                    (
                        "TEST permanece cerrado "
                        "hasta congelar el "
                        "candidato final."
                    ),
            },

        "delta_core_vs_financial":
            delta_df.to_dict(
                orient="records"
            ),

        "archivos_entrada":
            [
                ruta_relativa(
                    CORE_COMPARISON_PATH
                ),

                ruta_relativa(
                    LR_FINANCIAL_METRICS_PATH
                ),

                ruta_relativa(
                    LR_FINANCIAL_RANKING_PATH
                ),

                ruta_relativa(
                    LR_FINANCIAL_BACKTEST_PATH
                ),

                ruta_relativa(
                    MLP_FINANCIAL_METRICS_PATH
                ),

                ruta_relativa(
                    MLP_FINANCIAL_RANKING_PATH
                ),

                ruta_relativa(
                    MLP_FINANCIAL_BACKTEST_PATH
                ),

                ruta_relativa(
                    HGB_TUNING_PATH
                ),
            ],

        "archivos_salida":
            {
                "comparacion_integral":
                    ruta_relativa(
                        COMPARISON_PATH
                    ),

                "delta_por_familia":
                    ruta_relativa(
                        FAMILY_DELTA_PATH
                    ),

                "candidatos_por_familia":
                    ruta_relativa(
                        FAMILY_CANDIDATES_PATH
                    ),

                "metadata":
                    ruta_relativa(
                        METADATA_PATH
                    ),
            },

        "entorno":
            {
                "python":
                    sys.version.split()[0],

                "platform":
                    platform.platform(),

                "pandas":
                    pd.__version__,

                "numpy":
                    np.__version__,
            },
    }


# ============================================================
# MOSTRAR COMPARACIÓN
# ============================================================

def mostrar_comparacion(
    comparison_df,
    delta_df,
    candidates_df,
):

    print(
        "\n"
        + "=" * 120
    )

    print(
        "COMPARACIÓN INTEGRAL v10"
    )

    print(
        "=" * 120
    )

    columnas_resumen = [
        "MODELO",
        "FAMILIA",
        "VARIANTE",
        "VALIDATION_PR_AUC",
        "BACKTEST_PR_AUC_MEDIA",
        "BACKTEST_PR_AUC_MEDIANA",
        "BACKTEST_PR_AUC_STD",
        "BACKTEST_LIFT_AT_50_MEDIA",
        "BACKTEST_LIFT_AT_100_MEDIA",
        "BACKTEST_LIFT_AT_200_MEDIA",
        "CANDIDATO_FAMILIA",
    ]

    print(
        "\nSeis experimentos:"
    )

    print(
        comparison_df[
            columnas_resumen
        ].to_string(
            index=False
        )
    )

    print(
        "\n"
        + "=" * 120
    )

    print(
        "EFECTO DE LAS FEATURES FINANCIERAS"
    )

    print(
        "=" * 120
    )

    columnas_delta = [
        "FAMILIA",
        "CORE_BACKTEST_PR_AUC_MEDIA",
        "FINANCIAL_BACKTEST_PR_AUC_MEDIA",
        "DELTA_BACKTEST_PR_AUC_MEDIA",
        "DELTA_BACKTEST_PR_AUC_PCT",
        "CORE_BACKTEST_PR_AUC_STD",
        "FINANCIAL_BACKTEST_PR_AUC_STD",
    ]

    print(
        delta_df[
            columnas_delta
        ].to_string(
            index=False
        )
    )

    print(
        "\n"
        + "=" * 120
    )

    print(
        "CANDIDATOS POR FAMILIA"
    )

    print(
        "=" * 120
    )

    print(
        candidates_df[
            [
                "FAMILIA",
                "MODELO",
                "VALIDATION_PR_AUC",
                "BACKTEST_PR_AUC_MEDIA",
                "BACKTEST_PR_AUC_MEDIANA",
                "BACKTEST_PR_AUC_STD",
                "BACKTEST_LIFT_AT_50_MEDIA",
                "BACKTEST_LIFT_AT_100_MEDIA",
                "BACKTEST_LIFT_AT_200_MEDIA",
            ]
        ].to_string(
            index=False
        )
    )

    print(
        "\nTEST 2022-2023:"
    )

    print(
        "RESERVADO - NO CARGADO - NO EVALUADO"
    )

    print(
        "\nNo se ha seleccionado todavía "
        "el modelo final del proyecto."
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
        "COMPARACIÓN FINAL DE CANDIDATOS v10"
    )

    print(
        "=" * 120
    )

    print(
        "\nEste script:"
    )

    print(
        "- No entrena modelos."
    )

    print(
        "- No recalcula features."
    )

    print(
        "- No carga TEST 2022-2023."
    )

    print(
        "- Consolida únicamente "
        "resultados ya generados."
    )

    # --------------------------------------------------------
    # VALIDAR ENTRADAS
    # --------------------------------------------------------

    validar_entradas()

    # --------------------------------------------------------
    # CARGAR 6 EXPERIMENTOS
    # --------------------------------------------------------

    filas = []

    filas.extend(
        cargar_core()
    )

    filas.append(
        cargar_lr_financial()
    )

    filas.append(
        cargar_hgb_financial_c3()
    )

    filas.append(
        cargar_mlp_financial()
    )

    comparison_df = pd.DataFrame(
        filas
    )

    # --------------------------------------------------------
    # COMPLETAR LIFT HGB C3
    # --------------------------------------------------------

    comparison_df = (
        completar_lift_validation(
            comparison_df
        )
    )

    # --------------------------------------------------------
    # MARCAR CANDIDATO POR FAMILIA
    # --------------------------------------------------------

    comparison_df = marcar_candidatos(
        comparison_df
    )

    # --------------------------------------------------------
    # ORDEN
    # --------------------------------------------------------

    orden_modelos = [
        "v10_lr_no_provincia",
        "v10_lr_financial",
        "v10_hgb",
        "v10_hgb_financial_c3",
        "v10_mlp",
        "v10_mlp_financial",
    ]

    comparison_df[
        "_ORDEN"
    ] = pd.Categorical(
        comparison_df[
            "MODELO"
        ],
        categories=orden_modelos,
        ordered=True,
    )

    comparison_df = (
        comparison_df
        .sort_values(
            "_ORDEN"
        )
        .drop(
            columns=[
                "_ORDEN",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    # --------------------------------------------------------
    # VALIDAR
    # --------------------------------------------------------

    validar_comparacion(
        comparison_df
    )

    # --------------------------------------------------------
    # DELTA CORE VS FINANCIAL
    # --------------------------------------------------------

    delta_df = construir_delta_familia(
        comparison_df
    )

    # --------------------------------------------------------
    # CANDIDATOS POR FAMILIA
    # --------------------------------------------------------

    candidates_df = (
        construir_candidatos_familia(
            comparison_df
        )
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    metadata = construir_metadata(
        comparison_df,
        delta_df,
        candidates_df,
    )

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    comparison_df.to_csv(
        COMPARISON_PATH,
        index=False,
    )

    delta_df.to_csv(
        FAMILY_DELTA_PATH,
        index=False,
    )

    candidates_df.to_csv(
        FAMILY_CANDIDATES_PATH,
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

    mostrar_comparacion(
        comparison_df,
        delta_df,
        candidates_df,
    )

    print(
        "\nArchivos generados:"
    )

    print(
        COMPARISON_PATH
    )

    print(
        FAMILY_DELTA_PATH
    )

    print(
        FAMILY_CANDIDATES_PATH
    )

    print(
        METADATA_PATH
    )

    print(
        "\nComparación finalizada correctamente."
    )


if __name__ == "__main__":
    main()