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
    / "mvp_features_2015_2023.csv.gz"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "mvp_features_temporal_v6.csv.gz"
)

SUMMARY_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "temporal_features_v6_summary.csv"
)

AVAILABILITY_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "temporal_features_v6_availability.csv"
)


# ============================================================
# VARIABLES BASE
# ============================================================

LOG_VARIABLES = [
    "LOG_ACTIVO_TOTAL",
    "LOG_ACTIVO_CORRIENTE",
    "LOG_EFECTIVO",
    "LOG_PASIVO_TOTAL",
    "LOG_PASIVO_CORRIENTE",
    "LOG_PASIVO_NO_CORRIENTE",
    "LOG_PATRIMONIO",
    "LOG_CAPITAL",
    "LOG_UTILIDAD_NETA",
]


RATIO_VARIABLES = [
    "LIQUIDEZ_CORRIENTE",
    "ENDEUDAMIENTO",
    "AUTONOMIA_FINANCIERA",
    "ROA",
    "EFECTIVO_ACTIVOS",
    "CAPITAL_ACTIVOS",
    "PASIVO_CORRIENTE_PASIVO",
]


VARIABLES_TEMPORALES_BASE = (
    LOG_VARIABLES
    + RATIO_VARIABLES
)


# ============================================================
# FUNCIONES
# ============================================================

def porcentaje(
    parte,
    total
):
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
# 1. CARGAR DATASET BASE
# ============================================================

print("=" * 110)
print("CONSTRUCCIÓN DE FEATURES TEMPORALES V6")
print("CAMBIOS FINANCIEROS ENTRE t Y t-1")
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
        "SECTOR_CIIU": str,
        "SPLIT": str,
    },
    low_memory=False
)


df[
    "RUC"
] = (
    df[
        "RUC"
    ]
    .astype("string")
    .str.strip()
)


df[
    "ANIO"
] = pd.to_numeric(
    df[
        "ANIO"
    ],
    errors="raise"
).astype(int)


df[
    "TARGET_24M"
] = pd.to_numeric(
    df[
        "TARGET_24M"
    ],
    errors="raise"
).astype(int)


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
    f"{int(df['TARGET_24M'].sum()):,}"
)


# ============================================================
# 2. VALIDAR CLAVE EMPRESA-AÑO
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
        "El dataset base contiene "
        "duplicados RUC-ANIO."
    )


# ============================================================
# 3. VALIDAR VARIABLES NECESARIAS
# ============================================================

columnas_requeridas = (
    [
        "RUC",
        "ANIO",
        "TARGET_24M",
        "SPLIT",
    ]
    + VARIABLES_TEMPORALES_BASE
)


faltantes = [
    columna
    for columna in columnas_requeridas
    if columna not in df.columns
]


if faltantes:

    raise ValueError(
        "Faltan columnas necesarias "
        "para construir features temporales:\n"
        f"{faltantes}"
    )


for variable in VARIABLES_TEMPORALES_BASE:

    df[
        variable
    ] = pd.to_numeric(
        df[
            variable
        ],
        errors="coerce"
    )


# ============================================================
# 4. CONSTRUIR TABLA DEL AÑO ANTERIOR t-1
# ============================================================

#
# Para cada observación correspondiente al año t,
# se busca exclusivamente información de la misma
# empresa en el año t-1.
#
# Ejemplo:
#
# fila original:
# RUC X - ANIO 2020
#
# información histórica permitida:
# RUC X - ANIO 2019
#
# Nunca se utilizan años posteriores.
#

historico = df[
    [
        "RUC",
        "ANIO",
    ]
    + VARIABLES_TEMPORALES_BASE
].copy()


#
# Desplazamos ANIO una unidad hacia adelante para que:
#
# registro 2019
# pueda asociarse a
# observación 2020.
#

historico[
    "ANIO"
] = (
    historico[
        "ANIO"
    ]
    + 1
)


historico[
    "TIENE_T_1"
] = 1


renombrar = {
    variable:
        f"{variable}_T_1"
    for variable
    in VARIABLES_TEMPORALES_BASE
}


historico = historico.rename(
    columns=renombrar
)


# ============================================================
# 5. ASOCIAR INFORMACIÓN t-1
# ============================================================

df = df.merge(
    historico,
    on=[
        "RUC",
        "ANIO",
    ],
    how="left",
    validate="one_to_one"
)


df[
    "TIENE_T_1"
] = (
    df[
        "TIENE_T_1"
    ]
    .fillna(0)
    .astype(int)
)


print(
    "\nObservaciones con información t-1: "
    f"{int(df['TIENE_T_1'].sum()):,} / "
    f"{len(df):,} "
    f"("
    f"{porcentaje(df['TIENE_T_1'].sum(), len(df)):.2f}%"
    f")"
)


# ============================================================
# 6. CAMBIOS EN VARIABLES MONETARIAS
# ============================================================

#
# Las variables monetarias ya fueron transformadas mediante
# logaritmo firmado:
#
# sign(x) * log(1 + abs(x))
#
# La nueva variable temporal se calcula como:
#
# DELTA_LOG_X =
#     LOG_X(t) - LOG_X(t-1)
#
# Esto evita utilizar tasas porcentuales convencionales
# problemáticas cuando existen valores cero o negativos.
#

DELTA_LOG_VARIABLES = []


for variable in LOG_VARIABLES:

    nombre_delta = (
        f"DELTA_{variable}"
    )

    variable_t_1 = (
        f"{variable}_T_1"
    )

    df[
        nombre_delta
    ] = (
        df[
            variable
        ]
        - df[
            variable_t_1
        ]
    )

    DELTA_LOG_VARIABLES.append(
        nombre_delta
    )


# ============================================================
# 7. CAMBIOS EN RATIOS FINANCIEROS
# ============================================================

#
# Para los ratios se utiliza diferencia absoluta:
#
# DELTA_RATIO =
#     RATIO(t) - RATIO(t-1)
#
# Ejemplos:
#
# DELTA_ROA
# DELTA_ENDEUDAMIENTO
# DELTA_LIQUIDEZ_CORRIENTE
#
# Si alguno de los ratios no está disponible por denominador
# cero, el cambio permanece como NaN.
#

DELTA_RATIO_VARIABLES = []


for variable in RATIO_VARIABLES:

    nombre_delta = (
        f"DELTA_{variable}"
    )

    variable_t_1 = (
        f"{variable}_T_1"
    )

    df[
        nombre_delta
    ] = (
        df[
            variable
        ]
        - df[
            variable_t_1
        ]
    )

    DELTA_RATIO_VARIABLES.append(
        nombre_delta
    )


FEATURES_TEMPORALES = (
    DELTA_LOG_VARIABLES
    + DELTA_RATIO_VARIABLES
    + [
        "TIENE_T_1",
    ]
)


# ============================================================
# 8. VALIDAR QUE NO EXISTA INFORMACIÓN FUTURA
# ============================================================

#
# El merge se construyó desplazando exclusivamente registros
# desde t-1 hacia t.
#
# Adicionalmente verificamos que las filas sin historial
# no tengan deltas financieros generados artificialmente.
#

sin_historial = (
    df[
        "TIENE_T_1"
    ]
    == 0
)


columnas_delta = (
    DELTA_LOG_VARIABLES
    + DELTA_RATIO_VARIABLES
)


deltas_sin_historial = (
    df.loc[
        sin_historial,
        columnas_delta
    ]
    .notna()
    .sum()
    .sum()
)


if deltas_sin_historial != 0:

    raise ValueError(
        "Se detectaron features temporales "
        "en observaciones sin información t-1."
    )


print(
    "\nValidación de historial t-1: OK"
)


# ============================================================
# 9. RESUMEN DE COBERTURA POR SPLIT
# ============================================================

df[
    "POSITIVO_CON_T_1"
] = (
    df[
        "TARGET_24M"
    ]
    * df[
        "TIENE_T_1"
    ]
)


resumen = (
    df
    .groupby(
        "SPLIT",
        observed=True
    )
    .agg(
        OBSERVACIONES=(
            "RUC",
            "size"
        ),
        CON_T_1=(
            "TIENE_T_1",
            "sum"
        ),
        POSITIVOS=(
            "TARGET_24M",
            "sum"
        ),
        POSITIVOS_CON_T_1=(
            "POSITIVO_CON_T_1",
            "sum"
        ),
    )
    .reset_index()
)


resumen[
    "COBERTURA_T_1_PCT"
] = (
    100
    * resumen[
        "CON_T_1"
    ]
    / resumen[
        "OBSERVACIONES"
    ]
)


resumen[
    "COBERTURA_POSITIVOS_PCT"
] = np.where(
    resumen[
        "POSITIVOS"
    ]
    > 0,
    (
        100
        * resumen[
            "POSITIVOS_CON_T_1"
        ]
        / resumen[
            "POSITIVOS"
        ]
    ),
    0.0
)


orden_split = pd.CategoricalDtype(
    categories=[
        "TRAIN",
        "EMBARGO_VALIDATION",
        "VALIDATION",
        "EMBARGO_TEST",
        "TEST",
    ],
    ordered=True
)


resumen[
    "SPLIT"
] = resumen[
    "SPLIT"
].astype(
    orden_split
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
    "COBERTURA DE HISTORIAL t-1"
)

print(
    "=" * 110
)


print(
    resumen.to_string(
        index=False,
        formatters={
            "COBERTURA_T_1_PCT":
                "{:.2f}".format,
            "COBERTURA_POSITIVOS_PCT":
                "{:.2f}".format,
        }
    )
)


# ============================================================
# 10. DISPONIBILIDAD DE FEATURES TEMPORALES
# ============================================================

disponibilidad = []


for split in [
    "TRAIN",
    "EMBARGO_VALIDATION",
    "VALIDATION",
    "EMBARGO_TEST",
    "TEST",
]:

    bloque = df[
        df[
            "SPLIT"
        ]
        == split
    ]

    for variable in (
        DELTA_LOG_VARIABLES
        + DELTA_RATIO_VARIABLES
    ):

        disponibles = int(
            bloque[
                variable
            ]
            .notna()
            .sum()
        )

        total = len(
            bloque
        )

        disponibilidad.append(
            {
                "SPLIT":
                    split,

                "FEATURE":
                    variable,

                "OBSERVACIONES":
                    total,

                "DISPONIBLES":
                    disponibles,

                "COBERTURA_PCT":
                    porcentaje(
                        disponibles,
                        total
                    ),
            }
        )


disponibilidad_df = pd.DataFrame(
    disponibilidad
)


print(
    "\n" + "=" * 110
)

print(
    "DISPONIBILIDAD DE FEATURES TEMPORALES"
)

print(
    "=" * 110
)


for split in [
    "TRAIN",
    "VALIDATION",
    "TEST",
]:

    print(
        f"\n{split}"
    )

    bloque = disponibilidad_df[
        disponibilidad_df[
            "SPLIT"
        ]
        == split
    ]

    print(
        bloque[
            [
                "FEATURE",
                "DISPONIBLES",
                "COBERTURA_PCT",
            ]
        ]
        .to_string(
            index=False,
            formatters={
                "COBERTURA_PCT":
                    "{:.2f}".format,
            }
        )
    )


# ============================================================
# 11. ELIMINAR COLUMNAS AUXILIARES t-1
# ============================================================

#
# Los valores originales t-1 fueron necesarios únicamente
# para calcular los cambios.
#
# No se conservan en el dataset final para evitar duplicar
# información y reducir el tamaño del archivo.
#

columnas_auxiliares_t_1 = [
    f"{variable}_T_1"
    for variable
    in VARIABLES_TEMPORALES_BASE
]


df = df.drop(
    columns=(
        columnas_auxiliares_t_1
        + [
            "POSITIVO_CON_T_1",
        ]
    )
)


# ============================================================
# 12. VALIDACIONES FINALES
# ============================================================

if df.duplicated(
    subset=[
        "RUC",
        "ANIO",
    ]
).any():

    raise ValueError(
        "El dataset temporal contiene "
        "duplicados RUC-ANIO."
    )


if int(
    df[
        "TARGET_24M"
    ].sum()
) != 423:

    raise ValueError(
        "El número de positivos TARGET_24M "
        "cambió durante la construcción "
        "de features temporales."
    )


if len(
    df
) != 883988:

    raise ValueError(
        "El número de observaciones cambió "
        "durante la construcción "
        "de features temporales."
    )


print(
    "\nValidaciones finales: OK"
)


# ============================================================
# 13. MOSTRAR FEATURES CREADAS
# ============================================================

print(
    "\n" + "=" * 110
)

print(
    "NUEVAS FEATURES TEMPORALES"
)

print(
    "=" * 110
)


for variable in FEATURES_TEMPORALES:

    print(
        f"  {variable}"
    )


print(
    f"\nTotal nuevas features: "
    f"{len(FEATURES_TEMPORALES)}"
)


# ============================================================
# 14. GUARDAR RESULTADOS
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


disponibilidad_df.to_csv(
    AVAILABILITY_PATH,
    index=False
)


# ============================================================
# FINAL
# ============================================================

print(
    "\n" + "=" * 110
)

print(
    "FEATURES TEMPORALES V6 CONSTRUIDAS CORRECTAMENTE"
)

print(
    "=" * 110
)


print(
    "\nDataset:"
)

print(
    OUTPUT_PATH
)


print(
    "\nResumen de cobertura:"
)

print(
    SUMMARY_PATH
)


print(
    "\nDisponibilidad de features:"
)

print(
    AVAILABILITY_PATH
)