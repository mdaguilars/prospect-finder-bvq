from pathlib import Path

import joblib
import numpy as np
import pandas as pd


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
    500,
    1000,
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

FEATURES_CATEGORICAS = [
    "SECTOR_CIIU",
]

FEATURES = (
    FEATURES_NUMERICAS
    + FEATURES_CATEGORICAS
)

TARGET = "TARGET_24M"


# ============================================================
# CARGAR DATOS Y MODELO
# ============================================================

print("=" * 110)
print("ANÁLISIS DETALLADO DE ERRORES — BASELINE V1")
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


RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


print(
    f"\nObservaciones cargadas: "
    f"{len(df):,}"
)


# ============================================================
# SOLO VALIDATION Y TEST
# ============================================================
#
# VALIDATION:
# análisis principal para entender comportamiento.
#
# TEST:
# análisis descriptivo del Baseline v1 ya evaluado.
#
# No se utilizarán estos resultados para modificar o
# seleccionar retrospectivamente el Baseline v1.
# ============================================================

splits_analizar = [
    "VALIDATION",
    "TEST",
]


resumen_errores = []
ranking_positivos = []
sectores_errores = []
perfil_errores = []


# ============================================================
# PROCESAR CADA SPLIT
# ============================================================

for nombre_split in splits_analizar:

    print(
        "\n" + "=" * 110
    )

    print(
        f"ANÁLISIS — {nombre_split}"
    )

    print("=" * 110)


    subset = df[
        df["SPLIT"]
        == nombre_split
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


    subset[
        "PROBABILIDAD_MODELO"
    ] = probabilidades


    subset[
        "PREDICCION"
    ] = predicciones


    # --------------------------------------------------------
    # TIPO DE RESULTADO
    # --------------------------------------------------------

    condiciones = [
        (
            (subset[TARGET] == 1)
            & (subset["PREDICCION"] == 1)
        ),
        (
            (subset[TARGET] == 1)
            & (subset["PREDICCION"] == 0)
        ),
        (
            (subset[TARGET] == 0)
            & (subset["PREDICCION"] == 1)
        ),
        (
            (subset[TARGET] == 0)
            & (subset["PREDICCION"] == 0)
        ),
    ]


    etiquetas = [
        "TP",
        "FN",
        "FP",
        "TN",
    ]


    subset[
        "TIPO_ERROR"
    ] = np.select(
        condiciones,
        etiquetas,
        default="OTRO"
    )


    # --------------------------------------------------------
    # RANKING GLOBAL
    # --------------------------------------------------------

    subset = (
        subset
        .sort_values(
            "PROBABILIDAD_MODELO",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )


    subset[
        "RANK"
    ] = (
        np.arange(
            1,
            len(subset) + 1
        )
    )


    positivos = subset[
        subset[TARGET]
        == 1
    ].copy()


    # --------------------------------------------------------
    # RESUMEN GENERAL
    # --------------------------------------------------------

    conteos = (
        subset[
            "TIPO_ERROR"
        ]
        .value_counts()
    )


    tp = int(
        conteos.get(
            "TP",
            0
        )
    )

    fn = int(
        conteos.get(
            "FN",
            0
        )
    )

    fp = int(
        conteos.get(
            "FP",
            0
        )
    )

    tn = int(
        conteos.get(
            "TN",
            0
        )
    )


    resumen_errores.append(
        {
            "SPLIT":
                nombre_split,

            "OBSERVACIONES":
                len(subset),

            "POSITIVOS":
                int(
                    y.sum()
                ),

            "TP":
                tp,

            "FN":
                fn,

            "FP":
                fp,

            "TN":
                tn,

            "POSITIVOS_CAPTURADOS_THRESHOLD_PCT":
                (
                    100
                    * tp
                    / (tp + fn)
                    if (tp + fn) > 0
                    else 0
                ),

            "MEDIANA_RANK_POSITIVOS":
                float(
                    positivos[
                        "RANK"
                    ].median()
                ),

            "MEJOR_RANK_POSITIVO":
                int(
                    positivos[
                        "RANK"
                    ].min()
                ),

            "PEOR_RANK_POSITIVO":
                int(
                    positivos[
                        "RANK"
                    ].max()
                ),

            "MEDIANA_SCORE_POSITIVOS":
                float(
                    positivos[
                        "PROBABILIDAD_MODELO"
                    ].median()
                ),
        }
    )


    # --------------------------------------------------------
    # POSITIVOS CAPTURADOS POR K
    # --------------------------------------------------------

    print(
        "\nPositivos por posición del ranking:"
    )


    for k in K_VALUES:

        positivos_k = int(
            (
                positivos[
                    "RANK"
                ]
                <= k
            ).sum()
        )


        recall_k = (
            positivos_k
            / len(positivos)
            if len(positivos) > 0
            else 0
        )


        ranking_positivos.append(
            {
                "SPLIT":
                    nombre_split,

                "K":
                    k,

                "POSITIVOS_CAPTURADOS":
                    positivos_k,

                "POSITIVOS_TOTALES":
                    len(positivos),

                "RECALL_AT_K":
                    recall_k,
            }
        )


        print(
            f"  Top {k:>4}: "
            f"{positivos_k:>3} de "
            f"{len(positivos):>3} positivos "
            f"| Recall={recall_k:.4f}"
        )


    # --------------------------------------------------------
    # DISTRIBUCIÓN DE RANK DE POSITIVOS
    # --------------------------------------------------------

    print(
        "\nRanking de futuros emisores:"
    )


    print(
        f"  Mejor posición:   "
        f"{int(positivos['RANK'].min()):,}"
    )

    print(
        f"  Mediana posición: "
        f"{int(positivos['RANK'].median()):,}"
    )

    print(
        f"  Peor posición:    "
        f"{int(positivos['RANK'].max()):,}"
    )


    # --------------------------------------------------------
    # SECTOR POR TIPO DE ERROR
    # --------------------------------------------------------

    sector_temp = subset[
        [
            "SECTOR_CIIU",
            "TIPO_ERROR",
        ]
    ].copy()


    sector_temp[
        "SECTOR_CIIU"
    ] = (
        sector_temp[
            "SECTOR_CIIU"
        ]
        .astype("string")
        .str.strip()
        .str.upper()
        .fillna(
            "SIN_SECTOR"
        )
    )


    sector_resumen = (
        sector_temp
        .groupby(
            [
                "SECTOR_CIIU",
                "TIPO_ERROR",
            ],
            observed=False
        )
        .size()
        .reset_index(
            name="OBSERVACIONES"
        )
    )


    sector_resumen[
        "SPLIT"
    ] = nombre_split


    sectores_errores.append(
        sector_resumen
    )


    # --------------------------------------------------------
    # PERFIL NUMÉRICO TP / FN / FP / TN
    # --------------------------------------------------------

    for tipo in [
        "TP",
        "FN",
        "FP",
        "TN",
    ]:

        bloque = subset[
            subset[
                "TIPO_ERROR"
            ]
            == tipo
        ]


        if bloque.empty:
            continue


        for feature in FEATURES_NUMERICAS:

            serie = pd.to_numeric(
                bloque[
                    feature
                ],
                errors="coerce"
            )


            perfil_errores.append(
                {
                    "SPLIT":
                        nombre_split,

                    "TIPO_ERROR":
                        tipo,

                    "FEATURE":
                        feature,

                    "OBSERVACIONES":
                        int(
                            serie.notna().sum()
                        ),

                    "MEDIANA":
                        float(
                            serie.median()
                        ),

                    "MEDIA":
                        float(
                            serie.mean()
                        ),

                    "Q25":
                        float(
                            serie.quantile(
                                0.25
                            )
                        ),

                    "Q75":
                        float(
                            serie.quantile(
                                0.75
                            )
                        ),
                }
            )


    # --------------------------------------------------------
    # RESUMEN THRESHOLD
    # --------------------------------------------------------

    print(
        "\nErrores con threshold = 0.50:"
    )

    print(
        f"  TP: {tp:,}"
    )

    print(
        f"  FN: {fn:,}"
    )

    print(
        f"  FP: {fp:,}"
    )

    print(
        f"  TN: {tn:,}"
    )


    # --------------------------------------------------------
    # SECTORES DE LOS FALSOS NEGATIVOS
    # --------------------------------------------------------

    falsos_negativos = subset[
        subset[
            "TIPO_ERROR"
        ]
        == "FN"
    ].copy()


    if not falsos_negativos.empty:

        fn_sector = (
            falsos_negativos[
                "SECTOR_CIIU"
            ]
            .astype("string")
            .str.upper()
            .fillna(
                "SIN_SECTOR"
            )
            .value_counts()
        )


        print(
            "\nSectores de los falsos negativos:"
        )

        print(
            fn_sector.to_string()
        )

    else:

        print(
            "\nNo existen falsos negativos."
        )


# ============================================================
# CONSOLIDAR RESULTADOS
# ============================================================

resumen_df = pd.DataFrame(
    resumen_errores
)


ranking_df = pd.DataFrame(
    ranking_positivos
)


sectores_df = pd.concat(
    sectores_errores,
    ignore_index=True
)


perfil_df = pd.DataFrame(
    perfil_errores
)


# ============================================================
# GUARDAR SOLO INFORMACIÓN AGREGADA
# ============================================================

RESUMEN_PATH = (
    RESULTS_DIR
    / "baseline_detailed_error_summary.csv"
)


RANKING_PATH = (
    RESULTS_DIR
    / "baseline_positive_ranking_analysis.csv"
)


SECTORES_PATH = (
    RESULTS_DIR
    / "baseline_error_sector_summary.csv"
)


PERFIL_PATH = (
    RESULTS_DIR
    / "baseline_error_feature_profiles.csv"
)


resumen_df.to_csv(
    RESUMEN_PATH,
    index=False
)


ranking_df.to_csv(
    RANKING_PATH,
    index=False
)


sectores_df.to_csv(
    SECTORES_PATH,
    index=False
)


perfil_df.to_csv(
    PERFIL_PATH,
    index=False
)


# ============================================================
# MOSTRAR RESUMEN GENERAL
# ============================================================

print(
    "\n" + "=" * 110
)

print(
    "RESUMEN GENERAL DE ERRORES"
)

print("=" * 110)


print(
    resumen_df.to_string(
        index=False,
        formatters={
            "POSITIVOS_CAPTURADOS_THRESHOLD_PCT":
                "{:.2f}".format,

            "MEDIANA_RANK_POSITIVOS":
                "{:.1f}".format,

            "MEDIANA_SCORE_POSITIVOS":
                "{:.6f}".format,
        }
    )
)


# ============================================================
# MOSTRAR RANKING POSITIVOS
# ============================================================

print(
    "\n" + "=" * 110
)

print(
    "COBERTURA DE POSITIVOS POR TOP-K"
)

print("=" * 110)


print(
    ranking_df.to_string(
        index=False,
        formatters={
            "RECALL_AT_K":
                "{:.4f}".format,
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
    "ANÁLISIS DETALLADO DE ERRORES FINALIZADO CORRECTAMENTE"
)

print("=" * 110)


print(
    "\nArchivos agregados generados:"
)

print(
    RESUMEN_PATH
)

print(
    RANKING_PATH
)

print(
    SECTORES_PATH
)

print(
    PERFIL_PATH
)


print(
    "\nNo se exportaron RUC, nombres ni predicciones "
    "individuales."
)