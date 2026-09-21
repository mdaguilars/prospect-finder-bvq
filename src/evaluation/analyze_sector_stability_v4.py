from pathlib import Path

import pandas as pd


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

OUTPUT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "sector_stability_temporal_v4.csv"
)


# ============================================================
# FUNCIONES
# ============================================================

def porcentaje(parte, total):
    """
    Calcula porcentaje evitando división por cero.
    """

    if total == 0:
        return 0.0

    return (
        100
        * parte
        / total
    )


# ============================================================
# CARGAR DATASET
# ============================================================

print("=" * 110)
print("ANÁLISIS DE ESTABILIDAD DE SECTOR_CIIU - TEMPORAL V4")
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
    f"\nObservaciones totales cargadas: "
    f"{len(df):,}"
)


# ============================================================
# EXCLUIR TEST DEL ANÁLISIS DE DECISIÓN
# ============================================================
#
# Este análisis se utiliza para decidir si SECTOR_CIIU
# debe mantenerse en los siguientes experimentos.
#
# Por esa razón se utilizan exclusivamente:
#
# TRAIN
# VALIDATION
#
# TEST permanece fuera de esta decisión.
# ============================================================

analisis = df[
    df[
        "SPLIT"
    ].isin(
        [
            "TRAIN",
            "VALIDATION",
        ]
    )
].copy()


print(
    "Observaciones utilizadas "
    "(TRAIN + VALIDATION): "
    f"{len(analisis):,}"
)


print(
    "Positivos utilizados: "
    f"{int(analisis['TARGET_24M'].sum()):,}"
)


# ============================================================
# NORMALIZAR SECTOR
# ============================================================

analisis[
    "SECTOR_CIIU"
] = (
    analisis[
        "SECTOR_CIIU"
    ]
    .astype("string")
    .str.strip()
    .str.upper()
)


analisis[
    "SECTOR_CIIU"
] = analisis[
    "SECTOR_CIIU"
].fillna(
    "SIN_SECTOR"
)


# ============================================================
# RESUMEN POR SPLIT Y SECTOR
# ============================================================

resumen = (
    analisis
    .groupby(
        [
            "SPLIT",
            "SECTOR_CIIU",
        ],
        observed=False
    )
    .agg(
        OBSERVACIONES=(
            "RUC",
            "size"
        ),
        POSITIVOS=(
            "TARGET_24M",
            "sum"
        ),
    )
    .reset_index()
)


resumen[
    "NEGATIVOS"
] = (
    resumen[
        "OBSERVACIONES"
    ]
    - resumen[
        "POSITIVOS"
    ]
)


resumen[
    "PREVALENCIA_PCT"
] = (
    100
    * resumen[
        "POSITIVOS"
    ]
    / resumen[
        "OBSERVACIONES"
    ]
)


# ============================================================
# TABLA COMPARATIVA TRAIN VS VALIDATION
# ============================================================

tabla = resumen.pivot(
    index="SECTOR_CIIU",
    columns="SPLIT",
    values=[
        "OBSERVACIONES",
        "POSITIVOS",
        "PREVALENCIA_PCT",
    ]
)


tabla.columns = [
    f"{metrica}_{split}"
    for metrica, split
    in tabla.columns
]


tabla = (
    tabla
    .reset_index()
)


# Asegurar columnas aunque algún split no tenga sector.
columnas_esperadas = [
    "OBSERVACIONES_TRAIN",
    "OBSERVACIONES_VALIDATION",
    "POSITIVOS_TRAIN",
    "POSITIVOS_VALIDATION",
    "PREVALENCIA_PCT_TRAIN",
    "PREVALENCIA_PCT_VALIDATION",
]


for columna in columnas_esperadas:

    if columna not in tabla.columns:
        tabla[columna] = 0


tabla = tabla.fillna(
    0
)


# ============================================================
# INDICADORES DE ESTABILIDAD
# ============================================================

tabla[
    "DIF_PREVALENCIA_PUNTOS"
] = (
    tabla[
        "PREVALENCIA_PCT_VALIDATION"
    ]
    - tabla[
        "PREVALENCIA_PCT_TRAIN"
    ]
)


tabla[
    "POSITIVOS_TOTAL"
] = (
    tabla[
        "POSITIVOS_TRAIN"
    ]
    + tabla[
        "POSITIVOS_VALIDATION"
    ]
)


# Indicador descriptivo.
#
# No elimina automáticamente ningún sector.
tabla[
    "POCOS_POSITIVOS_TRAIN"
] = (
    tabla[
        "POSITIVOS_TRAIN"
    ]
    < 5
)


tabla[
    "SIN_POSITIVOS_VALIDATION"
] = (
    tabla[
        "POSITIVOS_VALIDATION"
    ]
    == 0
)


# ============================================================
# ORDENAR
# ============================================================

tabla = tabla.sort_values(
    [
        "POSITIVOS_TRAIN",
        "OBSERVACIONES_TRAIN",
    ],
    ascending=[
        False,
        False,
    ]
).reset_index(
    drop=True
)


# ============================================================
# MOSTRAR RESULTADOS
# ============================================================

print(
    "\n" + "=" * 110
)

print(
    "POSITIVOS POR SECTOR — TRAIN"
)

print("=" * 110)


train_sector = resumen[
    resumen[
        "SPLIT"
    ]
    == "TRAIN"
].sort_values(
    [
        "POSITIVOS",
        "OBSERVACIONES",
    ],
    ascending=[
        False,
        False,
    ]
)


print(
    train_sector[
        [
            "SECTOR_CIIU",
            "OBSERVACIONES",
            "POSITIVOS",
            "PREVALENCIA_PCT",
        ]
    ]
    .to_string(
        index=False,
        formatters={
            "PREVALENCIA_PCT":
                "{:.4f}".format,
        }
    )
)


print(
    "\n" + "=" * 110
)

print(
    "POSITIVOS POR SECTOR — VALIDATION"
)

print("=" * 110)


validation_sector = resumen[
    resumen[
        "SPLIT"
    ]
    == "VALIDATION"
].sort_values(
    [
        "POSITIVOS",
        "OBSERVACIONES",
    ],
    ascending=[
        False,
        False,
    ]
)


print(
    validation_sector[
        [
            "SECTOR_CIIU",
            "OBSERVACIONES",
            "POSITIVOS",
            "PREVALENCIA_PCT",
        ]
    ]
    .to_string(
        index=False,
        formatters={
            "PREVALENCIA_PCT":
                "{:.4f}".format,
        }
    )
)


# ============================================================
# SECTORES CON POCOS POSITIVOS
# ============================================================

print(
    "\n" + "=" * 110
)

print(
    "SECTORES CON MENOS DE 5 POSITIVOS EN TRAIN"
)

print("=" * 110)


pocos = tabla[
    tabla[
        "POCOS_POSITIVOS_TRAIN"
    ]
]


if pocos.empty:

    print(
        "Ningún sector."
    )

else:

    print(
        pocos[
            [
                "SECTOR_CIIU",
                "OBSERVACIONES_TRAIN",
                "POSITIVOS_TRAIN",
                "OBSERVACIONES_VALIDATION",
                "POSITIVOS_VALIDATION",
            ]
        ]
        .to_string(
            index=False
        )
    )


# ============================================================
# SECTORES SIN POSITIVOS EN VALIDATION
# ============================================================

print(
    "\n" + "=" * 110
)

print(
    "SECTORES SIN POSITIVOS EN VALIDATION"
)

print("=" * 110)


sin_validation = tabla[
    tabla[
        "SIN_POSITIVOS_VALIDATION"
    ]
]


if sin_validation.empty:

    print(
        "Ningún sector."
    )

else:

    print(
        sin_validation[
            [
                "SECTOR_CIIU",
                "POSITIVOS_TRAIN",
                "POSITIVOS_VALIDATION",
                "PREVALENCIA_PCT_TRAIN",
                "PREVALENCIA_PCT_VALIDATION",
            ]
        ]
        .to_string(
            index=False,
            formatters={
                "PREVALENCIA_PCT_TRAIN":
                    "{:.4f}".format,
                "PREVALENCIA_PCT_VALIDATION":
                    "{:.4f}".format,
            }
        )
    )


# ============================================================
# GUARDAR RESULTADO
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


tabla.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# FINAL
# ============================================================

print(
    "\n" + "=" * 110
)

print(
    "ANÁLISIS DE SECTOR FINALIZADO CORRECTAMENTE"
)

print("=" * 110)


print(
    "\nResultado:"
)

print(
    OUTPUT_PATH
)


print(
    "\nIMPORTANTE:"
)

print(
    "TEST no fue utilizado para tomar decisiones "
    "sobre SECTOR_CIIU."
)
