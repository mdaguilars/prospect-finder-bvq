from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FINANCIALS_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "scvs_financials_harmonized_2015_2023.csv.gz"
)

VALIDATION_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "scvs_accounting_validation_detail.csv"
)

EMISORES_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "scvs"
    / "mercado_valores"
    / "listado_entes_65001_1789908466941.xlsx"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "mvp_labeled_2015_2023.csv.gz"
)

SUMMARY_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "target_24m_summary.csv"
)

POSITIVES_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "target_24m_positive_cases.csv"
)


# ============================================================
# FUNCIONES
# ============================================================

def normalizar_ruc(serie):

    return (
        serie
        .astype("string")
        .str.strip()
    )


def porcentaje(
    cantidad,
    total
):

    if total == 0:
        return 0.0

    return (
        100
        * cantidad
        / total
    )


# ============================================================
# 1. CARGAR DATASET FINANCIERO
# ============================================================

print("=" * 110)
print("CONSTRUCCIÓN DEL TARGET A 24 MESES")
print("CONTROL TEMPORAL BASADO EN DISPONIBILIDAD NORMATIVA")
print("=" * 110)


if not FINANCIALS_PATH.exists():

    raise FileNotFoundError(
        f"No existe:\n{FINANCIALS_PATH}"
    )


df = pd.read_csv(
    FINANCIALS_PATH,
    dtype={
        "RUC": str,
        "EXPEDIENTE": str,
        "CIIU": str,
        "PLAN_CONTABLE": str,
    },
    low_memory=False
)


df["RUC"] = normalizar_ruc(
    df["RUC"]
)


df["ANIO"] = pd.to_numeric(
    df["ANIO"],
    errors="raise"
).astype(int)


print(
    f"\nObservaciones financieras: "
    f"{len(df):,}"
)

print(
    f"Empresas únicas: "
    f"{df['RUC'].nunique():,}"
)


# ============================================================
# 2. INCORPORAR CONTROLES DE CALIDAD CONTABLE
# ============================================================

if not VALIDATION_PATH.exists():

    raise FileNotFoundError(
        f"No existe:\n{VALIDATION_PATH}"
    )


validation = pd.read_csv(
    VALIDATION_PATH,
    dtype={
        "RUC": str,
        "PLAN_CONTABLE": str,
    },
    low_memory=False
)


validation["RUC"] = normalizar_ruc(
    validation["RUC"]
)


validation["ANIO"] = pd.to_numeric(
    validation["ANIO"],
    errors="raise"
).astype(int)


columnas_calidad = [
    "ANIO",
    "RUC",
    "DIF_BALANCE_ABS",
    "DIF_BALANCE_REL",
    "DIF_PASIVO_ABS",
    "DIF_PASIVO_REL",
    "BALANCE_OK_REL_001",
    "PASIVO_OK_REL_001",
    "PATRIMONIO_NEGATIVO",
    "ACTIVO_CORRIENTE_MAYOR_TOTAL",
]


validation = validation[
    columnas_calidad
].copy()


if validation.duplicated(
    subset=[
        "RUC",
        "ANIO",
    ]
).any():

    raise ValueError(
        "El archivo de validación contiene "
        "duplicados RUC-ANIO."
    )


df = df.merge(
    validation,
    on=[
        "RUC",
        "ANIO",
    ],
    how="left",
    validate="one_to_one"
)


faltantes_calidad = (
    df[
        "BALANCE_OK_REL_001"
    ]
    .isna()
    .sum()
)


if faltantes_calidad > 0:

    raise ValueError(
        "Existen observaciones sin control "
        "de calidad contable: "
        f"{faltantes_calidad:,}"
    )


# ============================================================
# 3. CARGAR HISTÓRICO DE EMISORES
# ============================================================

print("\nCargando histórico de emisores SCVS...")


emisores = pd.read_excel(
    EMISORES_PATH,
    header=4
)


columnas_requeridas = [
    "IDENTIFICACIÓN",
    "FECHA INSCRIPCIÓN",
]


faltantes = [
    columna
    for columna in columnas_requeridas
    if columna not in emisores.columns
]


if faltantes:

    raise ValueError(
        "Faltan columnas en listado de emisores: "
        f"{faltantes}"
    )


emisores["RUC"] = normalizar_ruc(
    emisores[
        "IDENTIFICACIÓN"
    ]
)


emisores = emisores[
    emisores[
        "RUC"
    ]
    .str.fullmatch(
        r"\d{13}",
        na=False
    )
].copy()


emisores[
    "FECHA_INSCRIPCION"
] = pd.to_datetime(
    emisores[
        "FECHA INSCRIPCIÓN"
    ],
    errors="coerce",
    dayfirst=True
)


emisores_validos = emisores[
    emisores[
        "FECHA_INSCRIPCION"
    ]
    .notna()
].copy()


primera_inscripcion = (
    emisores_validos
    .groupby(
        "RUC",
        as_index=False
    )
    .agg(
        FECHA_PRIMERA_INSCRIPCION=(
            "FECHA_INSCRIPCION",
            "min"
        )
    )
)


print(
    "Emisores históricos con fecha válida: "
    f"{len(primera_inscripcion):,}"
)


# ============================================================
# 4. ASOCIAR PRIMERA INSCRIPCIÓN
# ============================================================

df = df.merge(
    primera_inscripcion,
    on="RUC",
    how="left",
    validate="many_to_one"
)


# ============================================================
# 5. DEFINIR DISPONIBILIDAD TEMPORAL
# ============================================================

#
# Supuesto metodológico:
#
# Los estados financieros correspondientes al ejercicio t
# tienen como plazo ordinario de presentación hasta el
# 30 de abril del año t+1.
#
# Debido a que los archivos públicos utilizados no contienen
# la fecha efectiva de presentación de cada compañía, el MVP
# utiliza el plazo normativo como aproximación conservadora
# de disponibilidad.
#
# Ejemplo:
#
# Estados financieros:        2020
# Fecha límite presentación:  30/04/2021
# Fecha de decisión:           01/05/2021
# Fin horizonte 24 meses:      30/04/2023
#
# El modelo nunca intenta predecir un evento ocurrido antes
# de la fecha en que se presume disponible la información.
#

df[
    "FECHA_LIMITE_PRESENTACION"
] = pd.to_datetime(
    (
        df["ANIO"]
        + 1
    )
    .astype(str)
    + "-04-30"
)


df[
    "FECHA_DECISION"
] = (
    df[
        "FECHA_LIMITE_PRESENTACION"
    ]
    + pd.Timedelta(days=1)
)


df[
    "FECHA_FIN_HORIZONTE"
] = pd.to_datetime(
    (
        df["ANIO"]
        + 3
    )
    .astype(str)
    + "-04-30"
)


print(
    "\nRegla temporal utilizada:"
)

print(
    "Ejercicio t -> límite 30/04/t+1 "
    "-> decisión 01/05/t+1 "
    "-> horizonte hasta 30/04/t+3"
)


# ============================================================
# 6. IDENTIFICAR EMPRESAS YA EMISORAS
# ============================================================

#
# Una empresa no es elegible si ya se había inscrito
# como emisor antes de la fecha de decisión.
#
# Esto incluye cualquier inscripción ocurrida hasta
# el 30 de abril del año t+1.
#

df[
    "ERA_EMISOR_ANTES_DECISION"
] = (
    df[
        "FECHA_PRIMERA_INSCRIPCION"
    ]
    .notna()
    &
    (
        df[
            "FECHA_PRIMERA_INSCRIPCION"
        ]
        < df[
            "FECHA_DECISION"
        ]
    )
)


cantidad_ya_emisor = int(
    df[
        "ERA_EMISOR_ANTES_DECISION"
    ].sum()
)


print(
    "\nObservaciones correspondientes "
    "a empresas que ya eran emisoras "
    "antes de la fecha de decisión:"
)

print(
    f"{cantidad_ya_emisor:,}"
)


# ============================================================
# 7. ELIMINAR EMPRESAS YA EMISORAS
# ============================================================

mvp = df[
    ~df[
        "ERA_EMISOR_ANTES_DECISION"
    ]
].copy()


print(
    "\nObservaciones elegibles para predicción:"
)

print(
    f"{len(mvp):,}"
)


# ============================================================
# 8. CREAR TARGET A 24 MESES
# ============================================================

#
# TARGET_24M = 1 cuando la primera inscripción ocurre:
#
# - desde la FECHA_DECISION, inclusive;
# - hasta FECHA_FIN_HORIZONTE, inclusive.
#
# Ejemplo para estados financieros 2020:
#
# Inicio: 01/05/2021
# Fin:    30/04/2023
#

mvp[
    "TARGET_24M"
] = (
    mvp[
        "FECHA_PRIMERA_INSCRIPCION"
    ]
    .notna()
    &
    (
        mvp[
            "FECHA_PRIMERA_INSCRIPCION"
        ]
        >= mvp[
            "FECHA_DECISION"
        ]
    )
    &
    (
        mvp[
            "FECHA_PRIMERA_INSCRIPCION"
        ]
        <= mvp[
            "FECHA_FIN_HORIZONTE"
        ]
    )
).astype(int)


# ============================================================
# 9. RESUMEN POR AÑO
# ============================================================

resumen = (
    mvp
    .groupby(
        "ANIO"
    )
    .agg(
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
        BALANCE_OK=(
            "BALANCE_OK_REL_001",
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
# 10. POSITIVOS Y CALIDAD CONTABLE
# ============================================================

positivos = mvp[
    mvp[
        "TARGET_24M"
    ]
    == 1
].copy()


positivos_balance_ok = int(
    positivos[
        "BALANCE_OK_REL_001"
    ].sum()
)


positivos_pasivo_ok = int(
    positivos[
        "PASIVO_OK_REL_001"
    ].sum()
)


print("\n" + "=" * 110)
print("RESULTADO DEL TARGET")
print("=" * 110)


print(
    f"Observaciones elegibles: "
    f"{len(mvp):,}"
)


print(
    f"Positivos TARGET_24M: "
    f"{len(positivos):,}"
)


print(
    f"Negativos TARGET_24M: "
    f"{len(mvp) - len(positivos):,}"
)


print(
    "Prevalencia global: "
    f"{porcentaje(len(positivos), len(mvp)):.4f}%"
)


print(
    "\nPositivos con ecuación contable "
    "válida <= 0.01%:"
)

print(
    f"{positivos_balance_ok:,} / "
    f"{len(positivos):,} "
    f"("
    f"{porcentaje(positivos_balance_ok, len(positivos)):.2f}%"
    f")"
)


print(
    "\nPositivos con validación de "
    "componentes del pasivo <= 0.01%:"
)

print(
    f"{positivos_pasivo_ok:,} / "
    f"{len(positivos):,} "
    f"("
    f"{porcentaje(positivos_pasivo_ok, len(positivos)):.2f}%"
    f")"
)


# ============================================================
# 11. MOSTRAR RESUMEN POR AÑO
# ============================================================

print("\n" + "=" * 110)
print("DISTRIBUCIÓN DEL TARGET POR AÑO")
print("=" * 110)


print(
    resumen[
        [
            "ANIO",
            "OBSERVACIONES",
            "POSITIVOS",
            "NEGATIVOS",
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
# 12. POSITIVOS POR PLAN CONTABLE
# ============================================================

print("\n" + "=" * 110)
print("POSITIVOS POR PLAN CONTABLE")
print("=" * 110)


positivos_plan = (
    positivos
    .groupby(
        "PLAN_CONTABLE"
    )
    .size()
    .sort_values(
        ascending=False
    )
)


print(
    positivos_plan.to_string()
)


# ============================================================
# 13. PREPARAR DATASET DE MODELADO
# ============================================================

#
# Las fechas relacionadas con el evento futuro
# NO deben utilizarse como variables predictoras.
#
# También eliminamos las fechas auxiliares empleadas
# exclusivamente para garantizar coherencia temporal.
#

columnas_eliminar_modelo = [
    "FECHA_PRIMERA_INSCRIPCION",
    "FECHA_LIMITE_PRESENTACION",
    "FECHA_DECISION",
    "FECHA_FIN_HORIZONTE",
    "ERA_EMISOR_ANTES_DECISION",
]


mvp_modelo = mvp.drop(
    columns=columnas_eliminar_modelo
)


# ============================================================
# 14. VALIDAR CLAVE FINAL
# ============================================================

if mvp_modelo.duplicated(
    subset=[
        "RUC",
        "ANIO",
    ]
).any():

    raise ValueError(
        "El dataset etiquetado contiene "
        "duplicados RUC-ANIO."
    )


# ============================================================
# 15. CREAR DIRECTORIOS
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

SUMMARY_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 16. GUARDAR DATASET
# ============================================================

mvp_modelo.to_csv(
    OUTPUT_PATH,
    index=False,
    compression="gzip"
)


resumen.to_csv(
    SUMMARY_PATH,
    index=False
)


# ============================================================
# 17. GUARDAR AUDITORÍA DE POSITIVOS
# ============================================================

positivos_auditoria = positivos[
    [
        "ANIO",
        "RUC",
        "NOMBRE",
        "CIIU",
        "PLAN_CONTABLE",
        "FECHA_LIMITE_PRESENTACION",
        "FECHA_DECISION",
        "FECHA_PRIMERA_INSCRIPCION",
        "FECHA_FIN_HORIZONTE",
        "TARGET_24M",
        "BALANCE_OK_REL_001",
        "PASIVO_OK_REL_001",
    ]
].copy()


positivos_auditoria.to_csv(
    POSITIVES_PATH,
    index=False
)


# ============================================================
# 18. VALIDACIÓN TEMPORAL FINAL
# ============================================================

errores_temporales = positivos[
    (
        positivos[
            "FECHA_PRIMERA_INSCRIPCION"
        ]
        < positivos[
            "FECHA_DECISION"
        ]
    )
    |
    (
        positivos[
            "FECHA_PRIMERA_INSCRIPCION"
        ]
        > positivos[
            "FECHA_FIN_HORIZONTE"
        ]
    )
]


if len(errores_temporales) > 0:

    raise ValueError(
        "Se detectaron positivos fuera "
        "del horizonte temporal definido."
    )


print(
    "\nValidación temporal de positivos: OK"
)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 110)
print("DATASET MVP ETIQUETADO CONSTRUIDO CORRECTAMENTE")
print("=" * 110)


print(
    "\nDataset:"
)

print(
    OUTPUT_PATH
)


print(
    "\nResumen del target:"
)

print(
    SUMMARY_PATH
)


print(
    "\nAuditoría de positivos:"
)

print(
    POSITIVES_PATH
)