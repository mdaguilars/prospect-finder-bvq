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

BACKTEST_SUMMARY_PATH = (
    RESULTS_DIR
    / "backtest_logistic_v10_summary.csv"
)

OUTPUT_COMPARISON_PATH = (
    RESULTS_DIR
    / "comparison_logistic_v10_variants.csv"
)

OUTPUT_METADATA_PATH = (
    RESULTS_DIR
    / "comparison_logistic_v10_variants_metadata.json"
)


# ============================================================
# MODELOS
# ============================================================

MODELOS = {
    "v10_lr": {
        "metrics":
            RESULTS_DIR
            / "v10_lr_metrics.csv",
    },

    "v10_lr_no_provincia": {
        "metrics":
            RESULTS_DIR
            / "v10_lr_no_provincia_metrics.csv",
    },

    "v10_lr_no_categoricas": {
        "metrics":
            RESULTS_DIR
            / "v10_lr_no_categoricas_metrics.csv",
    },

    "v10_lr_no_tipo_compania": {
        "metrics":
            RESULTS_DIR
            / "v10_lr_no_tipo_compania_metrics.csv",
    },
}


MODELO_BASELINE_SELECCIONADO = (
    "v10_lr_no_provincia"
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


def cargar_validation_metrics(
    modelo,
    path,
):
    """
    Obtiene la fila VALIDATION del experimento correspondiente.
    """

    validar_archivo(
        path
    )

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
            f"{modelo}: faltan columnas en metrics:\n"
            + "\n".join(
                faltantes
            )
        )

    mascara = (
        df["SPLIT"]
        .astype("string")
        .str.strip()
        .str.upper()
        .eq(
            "VALIDATION"
        )
    )

    validation = df[
        mascara
    ].copy()

    if len(validation) != 1:

        raise ValueError(
            f"{modelo}: se esperaba exactamente una fila "
            f"VALIDATION y se encontraron {len(validation)}."
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
# CARGAR BACKTEST
# ============================================================

def cargar_backtest():
    """
    Carga y valida el resumen del backtesting temporal v10.
    """

    validar_archivo(
        BACKTEST_SUMMARY_PATH
    )

    df = pd.read_csv(
        BACKTEST_SUMMARY_PATH
    )

    columnas_requeridas = [
        "MODELO",
        "N_FOLDS",
        "PR_AUC_MEDIA",
        "PR_AUC_MEDIANA",
        "PR_AUC_STD",
        "PR_AUC_MIN",
        "PR_AUC_MAX",
        "ROC_AUC_MEDIA",
        "LIFT_AT_50_MEDIA",
        "LIFT_AT_100_MEDIA",
        "LIFT_AT_200_MEDIA",
        "POSITIVOS_TOP_50_TOTAL",
        "POSITIVOS_TOP_100_TOTAL",
        "POSITIVOS_TOP_200_TOTAL",
    ]

    faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df.columns
    ]

    if faltantes:

        raise ValueError(
            "Faltan columnas requeridas en el resumen "
            "de backtesting:\n"
            + "\n".join(
                faltantes
            )
        )

    modelos_backtest = set(
        df["MODELO"]
        .astype(str)
        .tolist()
    )

    modelos_esperados = set(
        MODELOS.keys()
    )

    if modelos_backtest != modelos_esperados:

        raise ValueError(
            "Los modelos del backtesting no coinciden "
            "exactamente con las cuatro configuraciones v10."
        )

    return df


# ============================================================
# CONSTRUIR COMPARACIÓN
# ============================================================

def construir_comparacion():
    """
    Integra VALIDATION 2020 y backtesting temporal.
    """

    backtest = cargar_backtest()

    resultados = []

    for modelo, configuracion in MODELOS.items():

        validation = cargar_validation_metrics(
            modelo,
            configuracion[
                "metrics"
            ],
        )

        fila_backtest = backtest[
            backtest["MODELO"]
            == modelo
        ]

        if len(fila_backtest) != 1:

            raise ValueError(
                f"{modelo}: se esperaba exactamente una fila "
                "en el resumen de backtesting."
            )

        bt = fila_backtest.iloc[
            0
        ]

        resultado = {
            "MODELO":
                modelo,

            **validation,

            "BACKTEST_N_FOLDS":
                int(
                    bt[
                        "N_FOLDS"
                    ]
                ),

            "BACKTEST_PR_AUC_MEDIA":
                float(
                    bt[
                        "PR_AUC_MEDIA"
                    ]
                ),

            "BACKTEST_PR_AUC_MEDIANA":
                float(
                    bt[
                        "PR_AUC_MEDIANA"
                    ]
                ),

            "BACKTEST_PR_AUC_STD":
                float(
                    bt[
                        "PR_AUC_STD"
                    ]
                ),

            "BACKTEST_PR_AUC_MIN":
                float(
                    bt[
                        "PR_AUC_MIN"
                    ]
                ),

            "BACKTEST_PR_AUC_MAX":
                float(
                    bt[
                        "PR_AUC_MAX"
                    ]
                ),

            "BACKTEST_ROC_AUC_MEDIA":
                float(
                    bt[
                        "ROC_AUC_MEDIA"
                    ]
                ),

            "BACKTEST_POSITIVOS_TOP_50_TOTAL":
                int(
                    bt[
                        "POSITIVOS_TOP_50_TOTAL"
                    ]
                ),

            "BACKTEST_LIFT_AT_50_MEDIA":
                float(
                    bt[
                        "LIFT_AT_50_MEDIA"
                    ]
                ),

            "BACKTEST_POSITIVOS_TOP_100_TOTAL":
                int(
                    bt[
                        "POSITIVOS_TOP_100_TOTAL"
                    ]
                ),

            "BACKTEST_LIFT_AT_100_MEDIA":
                float(
                    bt[
                        "LIFT_AT_100_MEDIA"
                    ]
                ),

            "BACKTEST_POSITIVOS_TOP_200_TOTAL":
                int(
                    bt[
                        "POSITIVOS_TOP_200_TOTAL"
                    ]
                ),

            "BACKTEST_LIFT_AT_200_MEDIA":
                float(
                    bt[
                        "LIFT_AT_200_MEDIA"
                    ]
                ),

            "BASELINE_LOGISTICO_SELECCIONADO":
                (
                    modelo
                    == MODELO_BASELINE_SELECCIONADO
                ),
        }

        resultados.append(
            resultado
        )

    comparacion = pd.DataFrame(
        resultados
    )

    return comparacion


# ============================================================
# VALIDAR DECISIÓN
# ============================================================

def validar_decision(
    comparacion,
):
    """
    Valida que la decisión documentada sea coherente
    con la evidencia obtenida.

    La selección no se basa exclusivamente en una métrica:
    VALIDATION constituye la comparación oficial y el
    backtesting aporta evidencia de estabilidad temporal.
    """

    seleccionado = comparacion[
        comparacion[
            "MODELO"
        ]
        == MODELO_BASELINE_SELECCIONADO
    ]

    if len(seleccionado) != 1:

        raise ValueError(
            "No se encontró exactamente una fila para "
            "el baseline logístico seleccionado."
        )

    seleccionado = seleccionado.iloc[
        0
    ]

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    mejor_validation_pr_auc = comparacion[
        "VALIDATION_PR_AUC"
    ].max()

    if not np.isclose(
        seleccionado[
            "VALIDATION_PR_AUC"
        ],
        mejor_validation_pr_auc,
    ):

        raise ValueError(
            "La configuración documentada como baseline "
            "no posee la mayor PR-AUC en VALIDATION."
        )

    # --------------------------------------------------------
    # Backtesting
    # --------------------------------------------------------

    mejor_backtest_idx = comparacion[
        "BACKTEST_PR_AUC_MEDIA"
    ].idxmax()

    mejor_backtest = comparacion.loc[
        mejor_backtest_idx
    ]

    if (
        seleccionado[
            "BACKTEST_PR_AUC_MEDIA"
        ]
        <= 0
    ):

        raise ValueError(
            "PR-AUC media de backtesting inválida."
        )

    # --------------------------------------------------------
    # Diferencia respecto al máximo de backtesting
    # --------------------------------------------------------

    gap_absoluto = (
        mejor_backtest[
            "BACKTEST_PR_AUC_MEDIA"
        ]
        - seleccionado[
            "BACKTEST_PR_AUC_MEDIA"
        ]
    )

    gap_relativo = (
        gap_absoluto
        / mejor_backtest[
            "BACKTEST_PR_AUC_MEDIA"
        ]
    )

    evidencia = {
        "modelo_seleccionado":
            MODELO_BASELINE_SELECCIONADO,

        "modelo_mayor_pr_auc_validation":
            comparacion.loc[
                comparacion[
                    "VALIDATION_PR_AUC"
                ].idxmax(),
                "MODELO",
            ],

        "modelo_mayor_pr_auc_media_backtest":
            mejor_backtest[
                "MODELO"
            ],

        "validation_pr_auc_seleccionado":
            float(
                seleccionado[
                    "VALIDATION_PR_AUC"
                ]
            ),

        "backtest_pr_auc_media_seleccionado":
            float(
                seleccionado[
                    "BACKTEST_PR_AUC_MEDIA"
                ]
            ),

        "backtest_pr_auc_std_seleccionado":
            float(
                seleccionado[
                    "BACKTEST_PR_AUC_STD"
                ]
            ),

        "backtest_lift50_medio_seleccionado":
            float(
                seleccionado[
                    "BACKTEST_LIFT_AT_50_MEDIA"
                ]
            ),

        "backtest_lift100_medio_seleccionado":
            float(
                seleccionado[
                    "BACKTEST_LIFT_AT_100_MEDIA"
                ]
            ),

        "backtest_lift200_medio_seleccionado":
            float(
                seleccionado[
                    "BACKTEST_LIFT_AT_200_MEDIA"
                ]
            ),

        "gap_absoluto_pr_auc_backtest_vs_maximo":
            float(
                gap_absoluto
            ),

        "gap_relativo_pr_auc_backtest_vs_maximo":
            float(
                gap_relativo
            ),
    }

    return evidencia


# ============================================================
# METADATA
# ============================================================

def construir_metadata(
    comparacion,
    evidencia,
):
    """
    Construye metadata de la comparación y de la decisión.
    """

    seleccionado = comparacion[
        comparacion[
            "MODELO"
        ]
        == MODELO_BASELINE_SELECCIONADO
    ].iloc[
        0
    ]

    modelo_mejor_backtest = evidencia[
        "modelo_mayor_pr_auc_media_backtest"
    ]

    mejor_backtest = comparacion[
        comparacion[
            "MODELO"
        ]
        == modelo_mejor_backtest
    ].iloc[
        0
    ]

    metadata = {
        "experimento":
            "Comparacion de variantes Logistic Regression v10",

        "fecha_ejecucion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "objetivo":
            (
                "Contrastar las cuatro configuraciones de "
                "Regresion Logistica v10 utilizando conjuntamente "
                "VALIDATION 2020 y el backtesting temporal interno "
                "a TRAIN 2012-2018."
            ),

        "modelos_comparados":
            list(
                MODELOS.keys()
            ),

        "validation":
            {
                "anio":
                    2020,

                "funcion":
                    (
                        "Conjunto oficial de comparacion durante "
                        "la fase de desarrollo."
                    ),

                "metrica_principal":
                    "PR-AUC",
            },

        "backtesting":
            {
                "periodo":
                    "2012-2018",

                "numero_folds":
                    4,

                "tipo":
                    "rolling-origin con ventana expansiva",

                "embargo":
                    "1 ejercicio completo entre TRAIN y evaluacion",

                "funcion":
                    "Evaluar estabilidad temporal.",
            },

        "baseline_logistico_seleccionado":
            MODELO_BASELINE_SELECCIONADO,

        "alcance_seleccion":
            (
                "Baseline seleccionado dentro de la familia "
                "de Regresion Logistica v10. "
                "No constituye el modelo final de Prospect Finder BVQ."
            ),

        "criterio_decision":
            [
                (
                    "PR-AUC de VALIDATION 2020 se utiliza como "
                    "evidencia principal de comparacion durante "
                    "la fase de desarrollo."
                ),
                (
                    "El backtesting temporal se utiliza como "
                    "evidencia complementaria de estabilidad."
                ),
                (
                    "Se consideran adicionalmente Lift@K y "
                    "variabilidad temporal."
                ),
                (
                    "No se selecciona una configuracion por "
                    "ROC-AUC de manera aislada."
                ),
                (
                    "TEST 2022-2023 no participa en la decision."
                ),
            ],

        "evidencia_seleccion":
            evidencia,

        "comparacion_con_mejor_backtest":
            {
                "modelo":
                    modelo_mejor_backtest,

                "pr_auc_media":
                    float(
                        mejor_backtest[
                            "BACKTEST_PR_AUC_MEDIA"
                        ]
                    ),

                "pr_auc_std":
                    float(
                        mejor_backtest[
                            "BACKTEST_PR_AUC_STD"
                        ]
                    ),

                "lift50_medio":
                    float(
                        mejor_backtest[
                            "BACKTEST_LIFT_AT_50_MEDIA"
                        ]
                    ),

                "lift100_medio":
                    float(
                        mejor_backtest[
                            "BACKTEST_LIFT_AT_100_MEDIA"
                        ]
                    ),

                "lift200_medio":
                    float(
                        mejor_backtest[
                            "BACKTEST_LIFT_AT_200_MEDIA"
                        ]
                    ),
            },

        "baseline_seleccionado_resultados":
            {
                "validation_pr_auc":
                    float(
                        seleccionado[
                            "VALIDATION_PR_AUC"
                        ]
                    ),

                "validation_roc_auc":
                    float(
                        seleccionado[
                            "VALIDATION_ROC_AUC"
                        ]
                    ),

                "backtest_pr_auc_media":
                    float(
                        seleccionado[
                            "BACKTEST_PR_AUC_MEDIA"
                        ]
                    ),

                "backtest_pr_auc_mediana":
                    float(
                        seleccionado[
                            "BACKTEST_PR_AUC_MEDIANA"
                        ]
                    ),

                "backtest_pr_auc_std":
                    float(
                        seleccionado[
                            "BACKTEST_PR_AUC_STD"
                        ]
                    ),

                "backtest_lift50_medio":
                    float(
                        seleccionado[
                            "BACKTEST_LIFT_AT_50_MEDIA"
                        ]
                    ),

                "backtest_lift100_medio":
                    float(
                        seleccionado[
                            "BACKTEST_LIFT_AT_100_MEDIA"
                        ]
                    ),

                "backtest_lift200_medio":
                    float(
                        seleccionado[
                            "BACKTEST_LIFT_AT_200_MEDIA"
                        ]
                    ),
            },

        "test":
            {
                "periodo":
                    "2022-2023",

                "utilizado":
                    False,

                "estado":
                    "RESERVADO - SIN EVALUACION",
            },

        "archivos_fuente":
            {
                "backtest_summary":
                    ruta_relativa(
                        BACKTEST_SUMMARY_PATH
                    ),

                "validation_metrics":
                    {
                        modelo:
                            ruta_relativa(
                                configuracion[
                                    "metrics"
                                ]
                            )
                        for modelo, configuracion
                        in MODELOS.items()
                    },
            },

        "archivos_salida":
            {
                "comparacion":
                    ruta_relativa(
                        OUTPUT_COMPARISON_PATH
                    ),

                "metadata":
                    ruta_relativa(
                        OUTPUT_METADATA_PATH
                    ),
            },
    }

    return metadata


# ============================================================
# GUARDAR RESULTADOS
# ============================================================

def guardar_resultados(
    comparacion,
    metadata,
):
    """
    Guarda comparación y metadata.
    """

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    comparacion.to_csv(
        OUTPUT_COMPARISON_PATH,
        index=False,
    )

    with open(
        OUTPUT_METADATA_PATH,
        "w",
        encoding="utf-8",
    ) as archivo:

        json.dump(
            metadata,
            archivo,
            ensure_ascii=False,
            indent=2,
        )


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
        "COMPARACIÓN DE VARIANTES LOGISTIC REGRESSION v10"
    )

    print(
        "=" * 110
    )

    comparacion = construir_comparacion()

    evidencia = validar_decision(
        comparacion
    )

    metadata = construir_metadata(
        comparacion,
        evidencia,
    )

    guardar_resultados(
        comparacion,
        metadata,
    )

    columnas_salida = [
        "MODELO",
        "VALIDATION_PR_AUC",
        "VALIDATION_ROC_AUC",
        "BACKTEST_PR_AUC_MEDIA",
        "BACKTEST_PR_AUC_STD",
        "BACKTEST_LIFT_AT_50_MEDIA",
        "BACKTEST_LIFT_AT_100_MEDIA",
        "BACKTEST_LIFT_AT_200_MEDIA",
        "BASELINE_LOGISTICO_SELECCIONADO",
    ]

    print(
        "\nComparación:"
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
        "DECISIÓN"
    )

    print(
        "=" * 110
    )

    print(
        "\nBaseline logístico v10 seleccionado:"
    )

    print(
        MODELO_BASELINE_SELECCIONADO
    )

    print(
        "\nAlcance:"
    )

    print(
        "Baseline seleccionado dentro de Logistic Regression v10."
    )

    print(
        "NO constituye todavía el modelo final de Prospect Finder BVQ."
    )

    print(
        "\nVALIDATION 2020:"
    )

    print(
        "UTILIZADA PARA COMPARACIÓN DE DESARROLLO"
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
        OUTPUT_COMPARISON_PATH
    )

    print(
        OUTPUT_METADATA_PATH
    )

    print(
        "\nComparación finalizada."
    )


if __name__ == "__main__":
    main()