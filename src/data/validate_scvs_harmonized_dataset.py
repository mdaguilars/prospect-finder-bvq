from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "scvs_financials_harmonized_2015_2023.csv.gz"
)

OUTPUT_DETAIL_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "scvs_accounting_validation_detail.csv"
)

OUTPUT_SUMMARY_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "scvs_accounting_validation_summary.csv"
)


# ============================================================
# FUNCIONES
# ============================================================

def diferencia_relativa(
    valor_a,
    valor_b
):
    """
    Calcula diferencia relativa entre dos valores.

    Usa como denominador el mayor valor absoluto entre
    ambos lados para evitar divisiones inestables.
    """

    denominador = np.maximum(
        np.abs(valor_a),
        np.abs(valor_b)
    )

    diferencia = np.abs(
        valor_a - valor_b
    )

    resultado = np.where(
        denominador > 0,
        diferencia / denominador,
        np.where(
            diferencia == 0,
            0.0,
            np.nan
        )
    )

    return resultado


def porcentaje(cantidad, total):

    if total == 0:
        return 0.0

    return (
        100
        * cantidad
        / total
    )


# ============================================================
# CARGAR DATASET
# ============================================================

print("=" * 110)
print("VALIDACIÓN CONTABLE DEL DATASET HOMOLOGADO SCVS")
print("=" * 110)


if not DATASET_PATH.exists():

    raise FileNotFoundError(
        f"No existe el dataset:\n{DATASET_PATH}"
    )


df = pd.read_csv(
    DATASET_PATH,
    dtype={
        "RUC": str,
        "EXPEDIENTE": str,
        "CIIU": str,
        "PLAN_CONTABLE": str,
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


# ============================================================
# 1. VALIDACIÓN ACTIVO = PASIVO + PATRIMONIO
# ============================================================

df[
    "PASIVO_MAS_PATRIMONIO"
] = (
    df["PASIVO_TOTAL"]
    + df["PATRIMONIO"]
)


df[
    "DIF_BALANCE_ABS"
] = np.abs(
    df["ACTIVO_TOTAL"]
    - df["PASIVO_MAS_PATRIMONIO"]
)


df[
    "DIF_BALANCE_REL"
] = diferencia_relativa(
    df["ACTIVO_TOTAL"],
    df["PASIVO_MAS_PATRIMONIO"]
)


# Tolerancias:
#
# 1 centavo
# 1 dólar
# 0.01 %
# 0.10 %

df[
    "BALANCE_OK_001"
] = (
    df["DIF_BALANCE_ABS"]
    <= 0.01
)

df[
    "BALANCE_OK_1"
] = (
    df["DIF_BALANCE_ABS"]
    <= 1.00
)

df[
    "BALANCE_OK_REL_001"
] = (
    df["DIF_BALANCE_REL"]
    <= 0.0001
)

df[
    "BALANCE_OK_REL_01"
] = (
    df["DIF_BALANCE_REL"]
    <= 0.001
)


# ============================================================
# 2. VALIDACIÓN PASIVO TOTAL
# ============================================================

df[
    "PASIVO_COMPONENTES"
] = (
    df["PASIVO_CORRIENTE"]
    + df["PASIVO_NO_CORRIENTE"]
)


df[
    "DIF_PASIVO_ABS"
] = np.abs(
    df["PASIVO_TOTAL"]
    - df["PASIVO_COMPONENTES"]
)


df[
    "DIF_PASIVO_REL"
] = diferencia_relativa(
    df["PASIVO_TOTAL"],
    df["PASIVO_COMPONENTES"]
)


df[
    "PASIVO_OK_1"
] = (
    df["DIF_PASIVO_ABS"]
    <= 1.00
)

df[
    "PASIVO_OK_REL_001"
] = (
    df["DIF_PASIVO_REL"]
    <= 0.0001
)


# ============================================================
# 3. CONTROLES DE COHERENCIA BÁSICA
# ============================================================

df[
    "ACTIVO_NEGATIVO"
] = (
    df["ACTIVO_TOTAL"]
    < 0
)

df[
    "PATRIMONIO_NEGATIVO"
] = (
    df["PATRIMONIO"]
    < 0
)

df[
    "PASIVO_NEGATIVO"
] = (
    df["PASIVO_TOTAL"]
    < 0
)

df[
    "ACTIVO_CORRIENTE_MAYOR_TOTAL"
] = (
    df["ACTIVO_CORRIENTE"]
    > df["ACTIVO_TOTAL"]
)


# ============================================================
# 4. RESUMEN GENERAL
# ============================================================

total = len(df)

print("\n" + "=" * 110)
print("1. ECUACIÓN CONTABLE: ACTIVO = PASIVO + PATRIMONIO")
print("=" * 110)


controles_balance = [
    (
        "Diferencia absoluta <= USD 0.01",
        "BALANCE_OK_001"
    ),
    (
        "Diferencia absoluta <= USD 1",
        "BALANCE_OK_1"
    ),
    (
        "Diferencia relativa <= 0.01%",
        "BALANCE_OK_REL_001"
    ),
    (
        "Diferencia relativa <= 0.10%",
        "BALANCE_OK_REL_01"
    ),
]


for descripcion, columna in controles_balance:

    cantidad = int(
        df[columna].sum()
    )

    print(
        f"{descripcion:<42} "
        f"{cantidad:>10,} "
        f"({porcentaje(cantidad, total):6.2f}%)"
    )


print("\nDistribución diferencia relativa:")

print(
    df[
        "DIF_BALANCE_REL"
    ]
    .describe(
        percentiles=[
            0.50,
            0.90,
            0.95,
            0.99,
            0.999,
        ]
    )
    .to_string()
)


# ============================================================
# 5. VALIDACIÓN PASIVOS
# ============================================================

print("\n" + "=" * 110)
print(
    "2. PASIVO TOTAL = PASIVO CORRIENTE "
    "+ PASIVO NO CORRIENTE"
)
print("=" * 110)


cantidad = int(
    df[
        "PASIVO_OK_1"
    ].sum()
)

print(
    f"Diferencia absoluta <= USD 1: "
    f"{cantidad:,} "
    f"({porcentaje(cantidad, total):.2f}%)"
)


cantidad = int(
    df[
        "PASIVO_OK_REL_001"
    ].sum()
)

print(
    f"Diferencia relativa <= 0.01%: "
    f"{cantidad:,} "
    f"({porcentaje(cantidad, total):.2f}%)"
)


# ============================================================
# 6. COHERENCIA GENERAL
# ============================================================

print("\n" + "=" * 110)
print("3. CONTROLES DE COHERENCIA")
print("=" * 110)


controles = [
    (
        "Activo total negativo",
        "ACTIVO_NEGATIVO"
    ),
    (
        "Pasivo total negativo",
        "PASIVO_NEGATIVO"
    ),
    (
        "Patrimonio negativo",
        "PATRIMONIO_NEGATIVO"
    ),
    (
        "Activo corriente > activo total",
        "ACTIVO_CORRIENTE_MAYOR_TOTAL"
    ),
]


for descripcion, columna in controles:

    cantidad = int(
        df[columna].sum()
    )

    print(
        f"{descripcion:<40} "
        f"{cantidad:>10,} "
        f"({porcentaje(cantidad, total):6.2f}%)"
    )


# ============================================================
# 7. RESULTADOS POR PLAN CONTABLE
# ============================================================

print("\n" + "=" * 110)
print("4. VALIDACIÓN POR PLAN CONTABLE")
print("=" * 110)


resumen_plan = (
    df
    .groupby(
        "PLAN_CONTABLE"
    )
    .agg(
        OBSERVACIONES=(
            "RUC",
            "size"
        ),
        BALANCE_OK=(
            "BALANCE_OK_REL_001",
            "sum"
        ),
        PASIVO_OK=(
            "PASIVO_OK_REL_001",
            "sum"
        ),
        MEDIANA_DIF_BALANCE=(
            "DIF_BALANCE_REL",
            "median"
        ),
        P99_DIF_BALANCE=(
            "DIF_BALANCE_REL",
            lambda x: x.quantile(0.99)
        ),
        PATRIMONIO_NEGATIVO=(
            "PATRIMONIO_NEGATIVO",
            "sum"
        ),
    )
    .reset_index()
)


resumen_plan[
    "BALANCE_OK_PCT"
] = (
    100
    * resumen_plan[
        "BALANCE_OK"
    ]
    / resumen_plan[
        "OBSERVACIONES"
    ]
)


resumen_plan[
    "PASIVO_OK_PCT"
] = (
    100
    * resumen_plan[
        "PASIVO_OK"
    ]
    / resumen_plan[
        "OBSERVACIONES"
    ]
)


columnas_mostrar = [
    "PLAN_CONTABLE",
    "OBSERVACIONES",
    "BALANCE_OK_PCT",
    "PASIVO_OK_PCT",
    "MEDIANA_DIF_BALANCE",
    "P99_DIF_BALANCE",
]


print(
    resumen_plan[
        columnas_mostrar
    ]
    .to_string(
        index=False,
        formatters={
            "BALANCE_OK_PCT":
                "{:.2f}".format,
            "PASIVO_OK_PCT":
                "{:.2f}".format,
            "MEDIANA_DIF_BALANCE":
                "{:.8f}".format,
            "P99_DIF_BALANCE":
                "{:.8f}".format,
        }
    )
)


# ============================================================
# 8. VALIDACIÓN POR AÑO
# ============================================================

print("\n" + "=" * 110)
print("5. VALIDACIÓN POR AÑO")
print("=" * 110)


resumen_anio = (
    df
    .groupby(
        "ANIO"
    )
    .agg(
        OBSERVACIONES=(
            "RUC",
            "size"
        ),
        BALANCE_OK=(
            "BALANCE_OK_REL_001",
            "sum"
        ),
        PASIVO_OK=(
            "PASIVO_OK_REL_001",
            "sum"
        ),
    )
    .reset_index()
)


resumen_anio[
    "BALANCE_OK_PCT"
] = (
    100
    * resumen_anio[
        "BALANCE_OK"
    ]
    / resumen_anio[
        "OBSERVACIONES"
    ]
)


resumen_anio[
    "PASIVO_OK_PCT"
] = (
    100
    * resumen_anio[
        "PASIVO_OK"
    ]
    / resumen_anio[
        "OBSERVACIONES"
    ]
)


print(
    resumen_anio[
        [
            "ANIO",
            "OBSERVACIONES",
            "BALANCE_OK_PCT",
            "PASIVO_OK_PCT",
        ]
    ]
    .to_string(
        index=False,
        formatters={
            "BALANCE_OK_PCT":
                "{:.2f}".format,
            "PASIVO_OK_PCT":
                "{:.2f}".format,
        }
    )
)


# ============================================================
# 9. CASOS CON MAYOR DIFERENCIA
# ============================================================

print("\n" + "=" * 110)
print("6. MAYORES DIFERENCIAS EN ECUACIÓN CONTABLE")
print("=" * 110)


peores = (
    df[
        [
            "ANIO",
            "RUC",
            "NOMBRE",
            "PLAN_CONTABLE",
            "ACTIVO_TOTAL",
            "PASIVO_TOTAL",
            "PATRIMONIO",
            "DIF_BALANCE_ABS",
            "DIF_BALANCE_REL",
        ]
    ]
    .sort_values(
        "DIF_BALANCE_REL",
        ascending=False
    )
    .head(20)
)


print(
    peores.to_string(
        index=False
    )
)


# ============================================================
# 10. GUARDAR RESULTADOS
# ============================================================

OUTPUT_DETAIL_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


detalle = df[
    [
        "ANIO",
        "RUC",
        "PLAN_CONTABLE",
        "DIF_BALANCE_ABS",
        "DIF_BALANCE_REL",
        "DIF_PASIVO_ABS",
        "DIF_PASIVO_REL",
        "BALANCE_OK_REL_001",
        "PASIVO_OK_REL_001",
        "PATRIMONIO_NEGATIVO",
        "ACTIVO_CORRIENTE_MAYOR_TOTAL",
    ]
]


detalle.to_csv(
    OUTPUT_DETAIL_PATH,
    index=False
)


resumen_plan.to_csv(
    OUTPUT_SUMMARY_PATH,
    index=False
)


print("\n" + "=" * 110)
print("VALIDACIÓN FINALIZADA")
print("=" * 110)

print(
    "\nDetalle guardado en:"
)

print(
    OUTPUT_DETAIL_PATH
)

print(
    "\nResumen por plan guardado en:"
)

print(
    OUTPUT_SUMMARY_PATH
)