from pathlib import Path
import json
import platform

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_DIR = (
    PROJECT_ROOT
    / "reports"
    / "results"
)


# ------------------------------------------------------------
# Archivos de entrada
# ------------------------------------------------------------

V6_METRICS_PATH = (
    RESULTS_DIR
    / "backtest_logistic_v6_metrics.csv"
)

V6_RANKING_PATH = (
    RESULTS_DIR
    / "backtest_logistic_v6_ranking_metrics.csv"
)

V8_METRICS_PATH = (
    RESULTS_DIR
    / "backtest_hist_gradient_boosting_v8_metrics.csv"
)

V8_RANKING_PATH = (
    RESULTS_DIR
    / "backtest_hist_gradient_boosting_v8_ranking_metrics.csv"
)


# ------------------------------------------------------------
# Archivos de salida
# ------------------------------------------------------------

METRICS_COMPARISON_PATH = (
    RESULTS_DIR
    / "comparison_v6_v8_metrics_by_year.csv"
)

RANKING_COMPARISON_PATH = (
    RESULTS_DIR
    / "comparison_v6_v8_ranking_by_year.csv"
)

STABILITY_SUMMARY_PATH = (
    RESULTS_DIR
    / "comparison_v6_v8_stability_summary.csv"
)

MODEL_SUMMARY_PATH = (
    RESULTS_DIR
    / "comparison_v6_v8_model_summary.csv"
)

METADATA_PATH = (
    RESULTS_DIR
    / "comparison_v6_v8_metadata.json"
)


# ============================================================
# FUNCIONES
# ============================================================

def validar_archivo(path):
    """
    Verifica que exista un archivo requerido.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"No existe el archivo requerido:\n{path}"
        )


def mejora_porcentual(
    nuevo,
    baseline
):
    """
    Calcula el cambio porcentual de v8 respecto de v6.

    Si el baseline es cero, devuelve NaN para evitar
    una división inválida.
    """

    if baseline == 0:

        return np.nan

    return (
        (
            nuevo
            - baseline
        )
        / abs(baseline)
    ) * 100


def resumen_estabilidad(
    serie,
    modelo,
    metrica
):
    """
    Calcula medidas descriptivas de estabilidad temporal.

    La desviación estándar es muestral (ddof=1).

    Con solo tres folds no se interpreta como intervalo de
    confianza, sino como una medida descriptiva de dispersión.
    """

    serie = pd.to_numeric(
        serie,
        errors="raise"
    )

    return {
        "MODELO":
            modelo,

        "METRICA":
            metrica,

        "N_FOLDS":
            int(
                serie.count()
            ),

        "PROMEDIO":
            float(
                serie.mean()
            ),

        "MEDIANA":
            float(
                serie.median()
            ),

        "DESV_EST_MUESTRAL":
            float(
                serie.std(
                    ddof=1
                )
            ),

        "MINIMO":
            float(
                serie.min()
            ),

        "MAXIMO":
            float(
                serie.max()
            ),

        "RANGO":
            float(
                serie.max()
                - serie.min()
            ),
    }


# ============================================================
# 1. VALIDAR ARCHIVOS
# ============================================================

print("=" * 110)
print("COMPARACIÓN TEMPORAL V6 VS V8")
print("=" * 110)


archivos_requeridos = [
    V6_METRICS_PATH,
    V6_RANKING_PATH,
    V8_METRICS_PATH,
    V8_RANKING_PATH,
]


for archivo in archivos_requeridos:

    validar_archivo(
        archivo
    )


print(
    "\nArchivos requeridos encontrados correctamente."
)


# ============================================================
# 2. CARGAR RESULTADOS
# ============================================================

v6_metrics = pd.read_csv(
    V6_METRICS_PATH
)

v6_ranking = pd.read_csv(
    V6_RANKING_PATH
)

v8_metrics = pd.read_csv(
    V8_METRICS_PATH
)

v8_ranking = pd.read_csv(
    V8_RANKING_PATH
)


print(
    "\nResultados cargados:"
)

print(
    f"  v6 métricas:  {len(v6_metrics):,} filas"
)

print(
    f"  v8 métricas:  {len(v8_metrics):,} filas"
)

print(
    f"  v6 ranking:   {len(v6_ranking):,} filas"
)

print(
    f"  v8 ranking:   {len(v8_ranking):,} filas"
)


# ============================================================
# 3. VALIDAR COMPARABILIDAD DEL PROTOCOLO
# ============================================================

columnas_protocolo = [
    "FOLD",
    "TRAIN_INICIO",
    "TRAIN_FIN",
    "ANIO_EVALUACION",
    "OBS_TRAIN",
    "POSITIVOS_TRAIN",
    "OBS_EVALUACION",
    "POSITIVOS_EVALUACION",
]


for columna in columnas_protocolo:

    if columna not in v6_metrics.columns:

        raise ValueError(
            f"Falta {columna} en métricas v6."
        )

    if columna not in v8_metrics.columns:

        raise ValueError(
            f"Falta {columna} en métricas v8."
        )


protocolo_v6 = (
    v6_metrics[
        columnas_protocolo
    ]
    .sort_values(
        "FOLD"
    )
    .reset_index(
        drop=True
    )
)


protocolo_v8 = (
    v8_metrics[
        columnas_protocolo
    ]
    .sort_values(
        "FOLD"
    )
    .reset_index(
        drop=True
    )
)


if not protocolo_v6.equals(
    protocolo_v8
):

    print(
        "\nPROTOCOLO V6:"
    )

    print(
        protocolo_v6.to_string(
            index=False
        )
    )

    print(
        "\nPROTOCOLO V8:"
    )

    print(
        protocolo_v8.to_string(
            index=False
        )
    )

    raise ValueError(
        "Los backtests v6 y v8 no utilizan exactamente "
        "el mismo protocolo temporal."
    )


print(
    "\nVALIDACIÓN DE COMPARABILIDAD:"
)

print(
    "  Los folds, períodos de entrenamiento y universos "
    "de evaluación son idénticos."
)


# ============================================================
# 4. COMPARACIÓN DE MÉTRICAS GENERALES
# ============================================================

metricas_v6 = v6_metrics[
    [
        "FOLD",
        "TRAIN_INICIO",
        "TRAIN_FIN",
        "ANIO_EMBARGO",
        "ANIO_EVALUACION",
        "OBS_EVALUACION",
        "POSITIVOS_EVALUACION",
        "PREVALENCIA_EVALUACION",
        "PR_AUC",
        "ROC_AUC",
    ]
].copy()


metricas_v8 = v8_metrics[
    [
        "FOLD",
        "ANIO_EVALUACION",
        "PR_AUC",
        "ROC_AUC",
    ]
].copy()


metricas_v6 = metricas_v6.rename(
    columns={
        "PR_AUC":
            "V6_PR_AUC",

        "ROC_AUC":
            "V6_ROC_AUC",
    }
)


metricas_v8 = metricas_v8.rename(
    columns={
        "PR_AUC":
            "V8_PR_AUC",

        "ROC_AUC":
            "V8_ROC_AUC",
    }
)


comparacion_metricas = metricas_v6.merge(
    metricas_v8,
    on=[
        "FOLD",
        "ANIO_EVALUACION",
    ],
    how="inner",
    validate="one_to_one"
)


comparacion_metricas[
    "DIF_PR_AUC_V8_V6"
] = (
    comparacion_metricas[
        "V8_PR_AUC"
    ]
    - comparacion_metricas[
        "V6_PR_AUC"
    ]
)


comparacion_metricas[
    "MEJORA_PR_AUC_PCT"
] = comparacion_metricas.apply(
    lambda fila:
        mejora_porcentual(
            fila[
                "V8_PR_AUC"
            ],
            fila[
                "V6_PR_AUC"
            ]
        ),
    axis=1
)


comparacion_metricas[
    "DIF_ROC_AUC_V8_V6"
] = (
    comparacion_metricas[
        "V8_ROC_AUC"
    ]
    - comparacion_metricas[
        "V6_ROC_AUC"
    ]
)


comparacion_metricas[
    "MEJORA_ROC_AUC_PCT"
] = comparacion_metricas.apply(
    lambda fila:
        mejora_porcentual(
            fila[
                "V8_ROC_AUC"
            ],
            fila[
                "V6_ROC_AUC"
            ]
        ),
    axis=1
)


# ============================================================
# 5. COMPARACIÓN DE RANKING
# ============================================================

columnas_ranking = [
    "FOLD",
    "ANIO_EVALUACION",
    "K",
    "POSITIVOS_TOP_K",
    "POSITIVOS_TOTALES",
    "PREVALENCIA",
    "PRECISION_AT_K",
    "RECALL_AT_K",
    "LIFT_AT_K",
]


for columna in columnas_ranking:

    if columna not in v6_ranking.columns:

        raise ValueError(
            f"Falta {columna} en ranking v6."
        )

    if columna not in v8_ranking.columns:

        raise ValueError(
            f"Falta {columna} en ranking v8."
        )


ranking_v6 = v6_ranking[
    columnas_ranking
].copy()


ranking_v8 = v8_ranking[
    columnas_ranking
].copy()


ranking_v6 = ranking_v6.rename(
    columns={
        "POSITIVOS_TOP_K":
            "V6_POSITIVOS_TOP_K",

        "PRECISION_AT_K":
            "V6_PRECISION_AT_K",

        "RECALL_AT_K":
            "V6_RECALL_AT_K",

        "LIFT_AT_K":
            "V6_LIFT_AT_K",
    }
)


ranking_v8 = ranking_v8.rename(
    columns={
        "POSITIVOS_TOP_K":
            "V8_POSITIVOS_TOP_K",

        "PRECISION_AT_K":
            "V8_PRECISION_AT_K",

        "RECALL_AT_K":
            "V8_RECALL_AT_K",

        "LIFT_AT_K":
            "V8_LIFT_AT_K",
    }
)


comparacion_ranking = ranking_v6.merge(
    ranking_v8[
        [
            "FOLD",
            "ANIO_EVALUACION",
            "K",
            "V8_POSITIVOS_TOP_K",
            "V8_PRECISION_AT_K",
            "V8_RECALL_AT_K",
            "V8_LIFT_AT_K",
        ]
    ],
    on=[
        "FOLD",
        "ANIO_EVALUACION",
        "K",
    ],
    how="inner",
    validate="one_to_one"
)


comparacion_ranking[
    "DIF_POSITIVOS_V8_V6"
] = (
    comparacion_ranking[
        "V8_POSITIVOS_TOP_K"
    ]
    - comparacion_ranking[
        "V6_POSITIVOS_TOP_K"
    ]
)


comparacion_ranking[
    "DIF_PRECISION_AT_K_V8_V6"
] = (
    comparacion_ranking[
        "V8_PRECISION_AT_K"
    ]
    - comparacion_ranking[
        "V6_PRECISION_AT_K"
    ]
)


comparacion_ranking[
    "DIF_RECALL_AT_K_V8_V6"
] = (
    comparacion_ranking[
        "V8_RECALL_AT_K"
    ]
    - comparacion_ranking[
        "V6_RECALL_AT_K"
    ]
)


comparacion_ranking[
    "DIF_LIFT_AT_K_V8_V6"
] = (
    comparacion_ranking[
        "V8_LIFT_AT_K"
    ]
    - comparacion_ranking[
        "V6_LIFT_AT_K"
    ]
)


comparacion_ranking[
    "MEJORA_LIFT_AT_K_PCT"
] = comparacion_ranking.apply(
    lambda fila:
        mejora_porcentual(
            fila[
                "V8_LIFT_AT_K"
            ],
            fila[
                "V6_LIFT_AT_K"
            ]
        ),
    axis=1
)


# ============================================================
# 6. RESUMEN DE ESTABILIDAD
# ============================================================

resumen_estabilidad_filas = []


for modelo, metricas_df in [
    (
        "V6_LOGISTIC_REGRESSION",
        v6_metrics,
    ),
    (
        "V8_HIST_GRADIENT_BOOSTING",
        v8_metrics,
    ),
]:

    resumen_estabilidad_filas.append(
        resumen_estabilidad(
            metricas_df[
                "PR_AUC"
            ],
            modelo,
            "PR_AUC"
        )
    )

    resumen_estabilidad_filas.append(
        resumen_estabilidad(
            metricas_df[
                "ROC_AUC"
            ],
            modelo,
            "ROC_AUC"
        )
    )


for k in [
    50,
    100,
    200,
]:

    bloque_v6 = v6_ranking[
        v6_ranking[
            "K"
        ]
        == k
    ]

    bloque_v8 = v8_ranking[
        v8_ranking[
            "K"
        ]
        == k
    ]


    for modelo, bloque in [
        (
            "V6_LOGISTIC_REGRESSION",
            bloque_v6,
        ),
        (
            "V8_HIST_GRADIENT_BOOSTING",
            bloque_v8,
        ),
    ]:

        resumen_estabilidad_filas.append(
            resumen_estabilidad(
                bloque[
                    "POSITIVOS_TOP_K"
                ],
                modelo,
                f"POSITIVOS_TOP_{k}"
            )
        )

        resumen_estabilidad_filas.append(
            resumen_estabilidad(
                bloque[
                    "PRECISION_AT_K"
                ],
                modelo,
                f"PRECISION_AT_{k}"
            )
        )

        resumen_estabilidad_filas.append(
            resumen_estabilidad(
                bloque[
                    "RECALL_AT_K"
                ],
                modelo,
                f"RECALL_AT_{k}"
            )
        )

        resumen_estabilidad_filas.append(
            resumen_estabilidad(
                bloque[
                    "LIFT_AT_K"
                ],
                modelo,
                f"LIFT_AT_{k}"
            )
        )


resumen_estabilidad_df = pd.DataFrame(
    resumen_estabilidad_filas
)


# ============================================================
# 7. RESUMEN GENERAL DE MODELOS
# ============================================================

def obtener_promedio_ranking(
    ranking_df,
    k,
    columna
):

    return float(
        ranking_df.loc[
            ranking_df[
                "K"
            ]
            == k,
            columna
        ].mean()
    )


resumen_modelos = pd.DataFrame(
    [
        {
            "MODELO":
                "V6_LOGISTIC_REGRESSION",

            "PR_AUC_PROMEDIO":
                float(
                    v6_metrics[
                        "PR_AUC"
                    ].mean()
                ),

            "PR_AUC_MEDIANA":
                float(
                    v6_metrics[
                        "PR_AUC"
                    ].median()
                ),

            "PR_AUC_DESV_EST":
                float(
                    v6_metrics[
                        "PR_AUC"
                    ].std(
                        ddof=1
                    )
                ),

            "ROC_AUC_PROMEDIO":
                float(
                    v6_metrics[
                        "ROC_AUC"
                    ].mean()
                ),

            "POSITIVOS_TOP_50_PROMEDIO":
                obtener_promedio_ranking(
                    v6_ranking,
                    50,
                    "POSITIVOS_TOP_K"
                ),

            "POSITIVOS_TOP_100_PROMEDIO":
                obtener_promedio_ranking(
                    v6_ranking,
                    100,
                    "POSITIVOS_TOP_K"
                ),

            "POSITIVOS_TOP_200_PROMEDIO":
                obtener_promedio_ranking(
                    v6_ranking,
                    200,
                    "POSITIVOS_TOP_K"
                ),

            "LIFT_AT_50_PROMEDIO":
                obtener_promedio_ranking(
                    v6_ranking,
                    50,
                    "LIFT_AT_K"
                ),

            "LIFT_AT_100_PROMEDIO":
                obtener_promedio_ranking(
                    v6_ranking,
                    100,
                    "LIFT_AT_K"
                ),

            "LIFT_AT_200_PROMEDIO":
                obtener_promedio_ranking(
                    v6_ranking,
                    200,
                    "LIFT_AT_K"
                ),
        },

        {
            "MODELO":
                "V8_HIST_GRADIENT_BOOSTING",

            "PR_AUC_PROMEDIO":
                float(
                    v8_metrics[
                        "PR_AUC"
                    ].mean()
                ),

            "PR_AUC_MEDIANA":
                float(
                    v8_metrics[
                        "PR_AUC"
                    ].median()
                ),

            "PR_AUC_DESV_EST":
                float(
                    v8_metrics[
                        "PR_AUC"
                    ].std(
                        ddof=1
                    )
                ),

            "ROC_AUC_PROMEDIO":
                float(
                    v8_metrics[
                        "ROC_AUC"
                    ].mean()
                ),

            "POSITIVOS_TOP_50_PROMEDIO":
                obtener_promedio_ranking(
                    v8_ranking,
                    50,
                    "POSITIVOS_TOP_K"
                ),

            "POSITIVOS_TOP_100_PROMEDIO":
                obtener_promedio_ranking(
                    v8_ranking,
                    100,
                    "POSITIVOS_TOP_K"
                ),

            "POSITIVOS_TOP_200_PROMEDIO":
                obtener_promedio_ranking(
                    v8_ranking,
                    200,
                    "POSITIVOS_TOP_K"
                ),

            "LIFT_AT_50_PROMEDIO":
                obtener_promedio_ranking(
                    v8_ranking,
                    50,
                    "LIFT_AT_K"
                ),

            "LIFT_AT_100_PROMEDIO":
                obtener_promedio_ranking(
                    v8_ranking,
                    100,
                    "LIFT_AT_K"
                ),

            "LIFT_AT_200_PROMEDIO":
                obtener_promedio_ranking(
                    v8_ranking,
                    200,
                    "LIFT_AT_K"
                ),
        },
    ]
)


# ============================================================
# 8. MOSTRAR RESULTADOS PRINCIPALES
# ============================================================

print(
    "\n" + "=" * 110
)

print(
    "COMPARACIÓN PR-AUC Y ROC-AUC POR AÑO"
)

print(
    "=" * 110
)


for _, fila in comparacion_metricas.iterrows():

    print(
        f"\nAño {int(fila['ANIO_EVALUACION'])}"
    )

    print(
        f"  PR-AUC v6: "
        f"{fila['V6_PR_AUC']:.6f}"
    )

    print(
        f"  PR-AUC v8: "
        f"{fila['V8_PR_AUC']:.6f}"
    )

    print(
        f"  Diferencia: "
        f"{fila['DIF_PR_AUC_V8_V6']:+.6f}"
    )

    print(
        f"  Cambio relativo: "
        f"{fila['MEJORA_PR_AUC_PCT']:+.2f}%"
    )

    print(
        f"  ROC-AUC v6: "
        f"{fila['V6_ROC_AUC']:.6f}"
    )

    print(
        f"  ROC-AUC v8: "
        f"{fila['V8_ROC_AUC']:.6f}"
    )


print(
    "\n" + "=" * 110
)

print(
    "RESUMEN GENERAL"
)

print(
    "=" * 110
)


pr_v6_promedio = float(
    v6_metrics[
        "PR_AUC"
    ].mean()
)

pr_v8_promedio = float(
    v8_metrics[
        "PR_AUC"
    ].mean()
)


print(
    f"\nPR-AUC promedio v6: "
    f"{pr_v6_promedio:.6f}"
)

print(
    f"PR-AUC promedio v8: "
    f"{pr_v8_promedio:.6f}"
)

print(
    f"Cambio relativo promedio: "
    f"{mejora_porcentual(pr_v8_promedio, pr_v6_promedio):+.2f}%"
)


lift50_v6 = obtener_promedio_ranking(
    v6_ranking,
    50,
    "LIFT_AT_K"
)

lift50_v8 = obtener_promedio_ranking(
    v8_ranking,
    50,
    "LIFT_AT_K"
)


print(
    f"\nLift@50 promedio v6: "
    f"{lift50_v6:.2f}"
)

print(
    f"Lift@50 promedio v8: "
    f"{lift50_v8:.2f}"
)

print(
    f"Cambio relativo Lift@50: "
    f"{mejora_porcentual(lift50_v8, lift50_v6):+.2f}%"
)


std_pr_v6 = float(
    v6_metrics[
        "PR_AUC"
    ].std(
        ddof=1
    )
)

std_pr_v8 = float(
    v8_metrics[
        "PR_AUC"
    ].std(
        ddof=1
    )
)


print(
    f"\nDesv. estándar PR-AUC v6: "
    f"{std_pr_v6:.6f}"
)

print(
    f"Desv. estándar PR-AUC v8: "
    f"{std_pr_v8:.6f}"
)


# ============================================================
# 9. GUARDAR RESULTADOS
# ============================================================

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


comparacion_metricas.to_csv(
    METRICS_COMPARISON_PATH,
    index=False
)


comparacion_ranking.to_csv(
    RANKING_COMPARISON_PATH,
    index=False
)


resumen_estabilidad_df.to_csv(
    STABILITY_SUMMARY_PATH,
    index=False
)


resumen_modelos.to_csv(
    MODEL_SUMMARY_PATH,
    index=False
)


# ============================================================
# 10. METADATOS
# ============================================================

metadata = {

    "experimento":
        "comparison_v6_v8_backtests",

    "objetivo":
        (
            "Comparar Logistic Regression v6 contra "
            "HistGradientBoosting v8 bajo exactamente el mismo "
            "protocolo temporal rolling-origin."
        ),

    "baseline":
        "Logistic Regression v6",

    "modelo_ajustado":
        "HistGradientBoosting v8",

    "anios_evaluacion":
        sorted(
            comparacion_metricas[
                "ANIO_EVALUACION"
            ]
            .astype(int)
            .tolist()
        ),

    "numero_folds":
        int(
            len(
                comparacion_metricas
            )
        ),

    "metricas_generales":
        [
            "PR_AUC",
            "ROC_AUC",
        ],

    "metricas_ranking":
        [
            "POSITIVOS_TOP_K",
            "PRECISION_AT_K",
            "RECALL_AT_K",
            "LIFT_AT_K",
        ],

    "k_values":
        [
            50,
            100,
            200,
        ],

    "medidas_estabilidad":
        [
            "PROMEDIO",
            "MEDIANA",
            "DESV_EST_MUESTRAL",
            "MINIMO",
            "MAXIMO",
            "RANGO",
        ],

    "nota_variabilidad":
        (
            "La desviación estándar y el rango se utilizan como "
            "medidas descriptivas de estabilidad entre tres folds "
            "temporales. Debido al reducido número de folds, no se "
            "interpretan como intervalos de confianza formales."
        ),

    "test_2022_2023_evaluado":
        False,

    "nota_test":
        (
            "La comparación utiliza únicamente resultados de los "
            "backtests históricos 2018, 2019 y 2020. "
            "TEST 2022-2023 permanece reservado."
        ),

    "python_version":
        platform.python_version(),

    "pandas_version":
        pd.__version__,

    "numpy_version":
        np.__version__,
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
    "COMPARACIÓN V6 VS V8 FINALIZADA CORRECTAMENTE"
)

print(
    "=" * 110
)


print(
    "\nComparación de métricas:"
)

print(
    METRICS_COMPARISON_PATH
)


print(
    "\nComparación de ranking:"
)

print(
    RANKING_COMPARISON_PATH
)


print(
    "\nResumen de estabilidad:"
)

print(
    STABILITY_SUMMARY_PATH
)


print(
    "\nResumen de modelos:"
)

print(
    MODEL_SUMMARY_PATH
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
    "RESERVADO - NO EVALUADO"
)