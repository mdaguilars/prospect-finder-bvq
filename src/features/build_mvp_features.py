from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "mvp_labeled_2015_2023.csv.gz"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "mvp_features_2015_2023.csv.gz"
)

SUMMARY_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "mvp_split_summary.csv"
)


# ============================================================
# VARIABLES FINANCIERAS BASE
# ============================================================

VARIABLES_MONETARIAS = [
    "ACTIVO_TOTAL",
    "ACTIVO_CORRIENTE",
    "EFECTIVO",
    "PASIVO_TOTAL",
    "PASIVO_CORRIENTE",
    "PASIVO_NO_CORRIENTE",
    "PATRIMONIO",
    "CAPITAL",
    "UTILIDAD_NETA",
]


# ============================================================
# FUNCIONES
# ============================================================

def division_segura(
    numerador,
    denominador
):
    """
    Realiza una división evitando infinitos.

    Si el denominador es cero, el resultado queda como NaN.
    """

    denominador = denominador.replace(
        0,
        np.nan
    )

    resultado = (
        numerador
        / denominador
    )

    resultado = resultado.replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan
    )

    return resultado


def log_firmado(serie):
    """
    Transformación logarítmica que admite valores negativos.

    Fórmula:

        sign(x) * log(1 + abs(x))

    Permite comprimir magnitudes financieras muy grandes
    sin eliminar empresas con valores negativos.
    """

    return (
        np.sign(serie)
        * np.log1p(
            np.abs(serie)
        )
    )


def porcentaje(
    cantidad,
    total
):
    """
    Calcula un porcentaje evitando división por cero.
    """

    if total == 0:
        return 0.0

    return (
        100
        * cantidad
        / total
    )


# ============================================================
# 1. CARGAR DATASET
# ============================================================

print("=" * 110)
print("CONSTRUCCIÓN DE FEATURES DEL MVP")
print("=" * 110)


if not INPUT_PATH.exists():

    raise FileNotFoundError(
        f"No existe:\n{INPUT_PATH}"
    )


df = pd.read_csv(
    INPUT_PATH,
    dtype={
        "RUC": str,
        "EXPEDIENTE": str,
        "CIIU": str,
        "PLAN_CONTABLE": str,
        "RAMA_ACTIVIDAD": str,
    },
    low_memory=False
)


print(
    f"\nObservaciones cargadas: "
    f"{len(df):,}"
)

print(
    f"Empresas únicas: "
    f"{df['RUC'].nunique():,}"
)

print(
    f"Positivos TARGET_24M: "
    f"{df['TARGET_24M'].sum():,}"
)


# ============================================================
# 2. VALIDAR VARIABLES
# ============================================================

faltantes = [
    variable
    for variable in VARIABLES_MONETARIAS
    if variable not in df.columns
]


if faltantes:

    raise ValueError(
        "Faltan variables financieras: "
        f"{faltantes}"
    )


# ============================================================
# 3. LOGARITMOS FIRMADOS
# ============================================================

for variable in VARIABLES_MONETARIAS:

    nueva_variable = (
        f"LOG_{variable}"
    )

    df[
        nueva_variable
    ] = log_firmado(
        df[variable]
    )


# ============================================================
# 4. RATIOS FINANCIEROS
# ============================================================

df[
    "LIQUIDEZ_CORRIENTE"
] = division_segura(
    df["ACTIVO_CORRIENTE"],
    df["PASIVO_CORRIENTE"]
)


df[
    "ENDEUDAMIENTO"
] = division_segura(
    df["PASIVO_TOTAL"],
    df["ACTIVO_TOTAL"]
)


df[
    "AUTONOMIA_FINANCIERA"
] = division_segura(
    df["PATRIMONIO"],
    df["ACTIVO_TOTAL"]
)


df[
    "ROA"
] = division_segura(
    df["UTILIDAD_NETA"],
    df["ACTIVO_TOTAL"]
)


df[
    "EFECTIVO_ACTIVOS"
] = division_segura(
    df["EFECTIVO"],
    df["ACTIVO_TOTAL"]
)


df[
    "CAPITAL_ACTIVOS"
] = division_segura(
    df["CAPITAL"],
    df["ACTIVO_TOTAL"]
)


df[
    "PASIVO_CORRIENTE_PASIVO"
] = division_segura(
    df["PASIVO_CORRIENTE"],
    df["PASIVO_TOTAL"]
)


# ============================================================
# 5. SECTOR ECONÓMICO CIIU
# ============================================================
#
# Utilizamos la primera letra del código CIIU como sección
# económica general.
#
# IMPORTANTE:
# La letra "N" es una sección CIIU válida, por lo que NO debe
# convertirse en valor nulo.
# ============================================================

df[
    "SECTOR_CIIU"
] = (
    df["CIIU"]
    .astype("string")
    .str.strip()
    .str.upper()
    .str[0]
)


# Solo cadenas realmente vacías se convierten en NA.
df[
    "SECTOR_CIIU"
] = df[
    "SECTOR_CIIU"
].replace(
    {
        "": pd.NA,
    }
)


# ============================================================
# 6. DEFINIR SPLIT TEMPORAL
# ============================================================

df[
    "SPLIT"
] = pd.NA


# ------------------------------------------------------------
# TRAIN:
# Estados financieros 2015–2020
# ------------------------------------------------------------

df.loc[
    df["ANIO"].between(
        2015,
        2020
    ),
    "SPLIT"
] = "TRAIN"


# ------------------------------------------------------------
# VALIDATION:
# Año 2021
# ------------------------------------------------------------

df.loc[
    df["ANIO"] == 2021,
    "SPLIT"
] = "VALIDATION"


# ------------------------------------------------------------
# TEST:
# Años 2022–2023
# ------------------------------------------------------------

df.loc[
    df["ANIO"].between(
        2022,
        2023
    ),
    "SPLIT"
] = "TEST"


if df[
    "SPLIT"
].isna().any():

    anios_sin_split = sorted(
        df.loc[
            df["SPLIT"].isna(),
            "ANIO"
        ]
        .drop_duplicates()
        .tolist()
    )

    raise ValueError(
        "Existen años sin split asignado: "
        f"{anios_sin_split}"
    )


# ============================================================
# 7. VARIABLES PROPUESTAS PARA EL BASELINE
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


print(
    "\nFeatures numéricas propuestas:"
)

for variable in FEATURES_NUMERICAS:

    print(
        f"  {variable}"
    )


print(
    "\nFeatures categóricas propuestas:"
)

for variable in FEATURES_CATEGORICAS:

    print(
        f"  {variable}"
    )


# ============================================================
# 8. DISPONIBILIDAD DEL SECTOR CIIU
# ============================================================

sector_disponible = (
    df[
        "SECTOR_CIIU"
    ]
    .notna()
    .sum()
)


print(
    "\nDisponibilidad SECTOR_CIIU:"
)

print(
    f"{sector_disponible:,} / "
    f"{len(df):,} "
    f"("
    f"{porcentaje(sector_disponible, len(df)):.2f}%"
    f")"
)


print(
    "\nSecciones CIIU encontradas:"
)

print(
    sorted(
        df[
            "SECTOR_CIIU"
        ]
        .dropna()
        .unique()
        .tolist()
    )
)


# ============================================================
# 9. DIAGNÓSTICO DE RATIOS
# ============================================================

RATIOS = [
    "LIQUIDEZ_CORRIENTE",
    "ENDEUDAMIENTO",
    "AUTONOMIA_FINANCIERA",
    "ROA",
    "EFECTIVO_ACTIVOS",
    "CAPITAL_ACTIVOS",
    "PASIVO_CORRIENTE_PASIVO",
]


print(
    "\n" + "=" * 110
)

print(
    "DISPONIBILIDAD DE RATIOS"
)

print("=" * 110)


for variable in RATIOS:

    disponibles = (
        df[
            variable
        ]
        .notna()
        .sum()
    )

    print(
        f"{variable:<30} "
        f"{disponibles:>10,} "
        f"("
        f"{porcentaje(disponibles, len(df)):6.2f}%"
        f")"
    )


# ============================================================
# 10. RESUMEN DEL SPLIT
# ============================================================

resumen = (
    df
    .groupby(
        "SPLIT",
        observed=False
    )
    .agg(
        DESDE=(
            "ANIO",
            "min"
        ),
        HASTA=(
            "ANIO",
            "max"
        ),
        OBSERVACIONES=(
            "RUC",
            "size"
        ),
        EMPRESAS_UNICAS=(
            "RUC",
            "nunique"
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


orden = pd.CategoricalDtype(
    categories=[
        "TRAIN",
        "VALIDATION",
        "TEST",
    ],
    ordered=True
)


resumen[
    "SPLIT"
] = resumen[
    "SPLIT"
].astype(
    orden
)


resumen = (
    resumen
    .sort_values(
        "SPLIT"
    )
    .reset_index(
        drop=True
    )
)


print(
    "\n" + "=" * 110
)

print(
    "SPLIT TEMPORAL"
)

print("=" * 110)


print(
    resumen.to_string(
        index=False,
        formatters={
            "PREVALENCIA_PCT":
                "{:.4f}".format,
        }
    )
)


# ============================================================
# 11. POSITIVOS POR AÑO Y SPLIT
# ============================================================

print(
    "\n" + "=" * 110
)

print(
    "POSITIVOS POR AÑO"
)

print("=" * 110)


por_anio = (
    df
    .groupby(
        [
            "ANIO",
            "SPLIT",
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


print(
    por_anio.to_string(
        index=False
    )
)


# ============================================================
# 12. VALIDACIÓN DE TARGET
# ============================================================

total_positivos = int(
    df[
        "TARGET_24M"
    ].sum()
)


positivos_split = int(
    resumen[
        "POSITIVOS"
    ].sum()
)


if (
    total_positivos
    != positivos_split
):

    raise ValueError(
        "Los positivos se modificaron "
        "durante la construcción "
        "de features."
    )


# ============================================================
# 13. VALIDAR CLAVE EMPRESA-AÑO
# ============================================================

duplicados = df[
    df.duplicated(
        subset=[
            "RUC",
            "ANIO",
        ],
        keep=False
    )
]


if not duplicados.empty:

    raise ValueError(
        "El dataset de features contiene "
        "duplicados RUC-ANIO."
    )


# ============================================================
# 14. GUARDAR DATASET
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


SUMMARY_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


df.to_csv(
    OUTPUT_PATH,
    index=False,
    compression="gzip"
)


resumen.to_csv(
    SUMMARY_PATH,
    index=False
)


# ============================================================
# FINAL
# ============================================================

print(
    "\n" + "=" * 110
)

print(
    "FEATURES CONSTRUIDAS CORRECTAMENTE"
)

print("=" * 110)


print(
    "\nDataset:"
)

print(
    OUTPUT_PATH
)


print(
    "\nResumen del split:"
)

print(
    SUMMARY_PATH
)