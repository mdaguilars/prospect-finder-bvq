from pathlib import Path
from zipfile import ZipFile
import io

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCVS_ROOT = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "scvs"
    / "estados_financieros"
)

ARCHIVOS = [
    (
        2015,
        "balances_2015_3.txt",
    ),
    (
        2016,
        "balances_2016_2.txt",
    ),
]

CUENTAS = [
    "CUENTA_499",   # Total del activo
    "CUENTA_599",   # Total del pasivo
    "CUENTA_698",   # Total patrimonio
    "CUENTA_699",   # Total pasivo y patrimonio
]


# ============================================================
# FUNCIONES
# ============================================================

def detectar_encoding(contenido):
    """
    Detecta una codificación válida para el archivo.
    """

    for encoding in [
        "utf-8-sig",
        "utf-8",
        "latin-1",
        "cp1252",
    ]:

        try:
            contenido.decode(encoding)
            return encoding

        except UnicodeDecodeError:
            continue

    raise ValueError(
        "No fue posible determinar la codificación."
    )


def convertir_numero(serie):
    """
    Convierte los valores financieros SCVS.

    SCVS utiliza coma como separador decimal.
    Ejemplo:

        49578263,43 -> 49578263.43
    """

    serie = (
        serie
        .astype("string")
        .str.strip()
    )

    serie = serie.replace(
        {
            "": pd.NA,
            "nan": pd.NA,
            "None": pd.NA,
            "NULL": pd.NA,
        }
    )

    serie = serie.str.replace(
        ",",
        ".",
        regex=False
    )

    return pd.to_numeric(
        serie,
        errors="coerce"
    )


def diferencia_relativa(a, b):
    """
    Calcula la diferencia relativa entre dos valores.
    """

    denominador = np.maximum(
        np.abs(a),
        np.abs(b)
    )

    diferencia = np.abs(
        a - b
    )

    return np.where(
        denominador > 0,
        diferencia / denominador,
        np.where(
            diferencia == 0,
            0.0,
            np.nan
        )
    )


def porcentaje(cantidad, total):
    """
    Calcula porcentaje evitando división por cero.
    """

    if total == 0:
        return 0.0

    return (
        100
        * cantidad
        / total
    )


# ============================================================
# CARGAR PLAN_807
# ============================================================

datasets = []


for anio, archivo in ARCHIVOS:

    zip_path = (
        SCVS_ROOT
        / str(anio)
        / f"estadosFinancieros_{anio}.zip"
    )

    if not zip_path.exists():

        raise FileNotFoundError(
            f"No existe:\n{zip_path}"
        )

    with ZipFile(
        zip_path,
        "r"
    ) as z:

        contenido = z.read(
            archivo
        )

    encoding = detectar_encoding(
        contenido
    )

    columnas = [
        "RUC",
        "NOMBRE",
        *CUENTAS,
    ]

    df = pd.read_csv(
        io.BytesIO(contenido),
        sep="\t",
        encoding=encoding,
        dtype=str,
        usecols=columnas,
        low_memory=False
    )

    # --------------------------------------------------------
    # NORMALIZAR Y VALIDAR RUC
    # --------------------------------------------------------

    df["RUC"] = (
        df["RUC"]
        .astype("string")
        .str.strip()
    )

    filas_originales = len(df)

    df = df[
        df["RUC"].str.fullmatch(
            r"\d{13}",
            na=False
        )
    ].copy()

    print(
        f"{anio}: "
        f"{filas_originales:,} filas originales | "
        f"{len(df):,} RUC válidos"
    )

    df["ANIO"] = anio

    # --------------------------------------------------------
    # CONVERTIR CUENTAS
    # --------------------------------------------------------

    for columna in CUENTAS:

        df[columna] = (
            convertir_numero(
                df[columna]
            )
        )

    datasets.append(
        df
    )


df = pd.concat(
    datasets,
    ignore_index=True
)


# ============================================================
# VALIDAR CLAVE
# ============================================================

if df.duplicated(
    subset=[
        "RUC",
        "ANIO",
    ]
).any():

    duplicados = df[
        df.duplicated(
            subset=[
                "RUC",
                "ANIO",
            ],
            keep=False
        )
    ]

    raise ValueError(
        "Existen duplicados RUC-ANIO "
        "en PLAN_807:\n"
        f"{duplicados.head(20)}"
    )


# ============================================================
# COMPARACIONES CONTABLES
# ============================================================

df[
    "PASIVO_MAS_PATRIMONIO"
] = (
    df["CUENTA_599"]
    + df["CUENTA_698"]
)


# ------------------------------------------------------------
# A. ACTIVO TOTAL VS TOTAL PASIVO Y PATRIMONIO
# ------------------------------------------------------------

df[
    "DIF_499_699"
] = diferencia_relativa(
    df["CUENTA_499"],
    df["CUENTA_699"]
)


# ------------------------------------------------------------
# B. TOTAL PASIVO Y PATRIMONIO VS COMPONENTES
# ------------------------------------------------------------

df[
    "DIF_699_COMPONENTES"
] = diferencia_relativa(
    df["CUENTA_699"],
    df[
        "PASIVO_MAS_PATRIMONIO"
    ]
)


# ------------------------------------------------------------
# C. ACTIVO TOTAL VS PASIVO + PATRIMONIO
# ------------------------------------------------------------

df[
    "DIF_499_COMPONENTES"
] = diferencia_relativa(
    df["CUENTA_499"],
    df[
        "PASIVO_MAS_PATRIMONIO"
    ]
)


# ============================================================
# RESULTADOS
# ============================================================

print("\n" + "=" * 100)
print("DIAGNÓSTICO CONTABLE PLAN_807")
print("=" * 100)

print(
    f"\nObservaciones válidas: "
    f"{len(df):,}"
)


comparaciones = [
    (
        "499 TOTAL ACTIVO vs "
        "699 TOTAL PASIVO Y PATRIMONIO",
        "DIF_499_699"
    ),
    (
        "699 vs 599 PASIVO + "
        "698 PATRIMONIO",
        "DIF_699_COMPONENTES"
    ),
    (
        "499 ACTIVO vs 599 PASIVO + "
        "698 PATRIMONIO",
        "DIF_499_COMPONENTES"
    ),
]


for descripcion, columna in comparaciones:

    serie_valida = df[
        columna
    ].notna()

    total_validos = int(
        serie_valida.sum()
    )

    coincidencias = int(
        (
            df.loc[
                serie_valida,
                columna
            ]
            <= 0.0001
        ).sum()
    )

    print(
        "\n"
        + descripcion
    )

    print(
        f"  Casos comparables: "
        f"{total_validos:,}"
    )

    print(
        f"  Coincidencia <= 0.01%: "
        f"{coincidencias:,} "
        f"("
        f"{porcentaje(coincidencias, total_validos):.2f}%"
        f")"
    )

    print(
        "  Mediana diferencia relativa: "
        f"{df[columna].median():.10f}"
    )

    print(
        "  P99 diferencia relativa: "
        f"{df[columna].quantile(0.99):.10f}"
    )


# ============================================================
# CLASIFICAR ORIGEN DE LAS DIFERENCIAS
# ============================================================

df[
    "499_699_OK"
] = (
    df["DIF_499_699"]
    <= 0.0001
)


df[
    "699_COMPONENTES_OK"
] = (
    df["DIF_699_COMPONENTES"]
    <= 0.0001
)


print(
    "\n" + "=" * 100
)

print(
    "CLASIFICACIÓN DE LOS CASOS"
)

print("=" * 100)


clasificacion = (
    df
    .groupby(
        [
            "499_699_OK",
            "699_COMPONENTES_OK",
        ],
        dropna=False
    )
    .size()
    .reset_index(
        name="OBSERVACIONES"
    )
)


clasificacion[
    "PORCENTAJE"
] = (
    100
    * clasificacion[
        "OBSERVACIONES"
    ]
    / len(df)
)


print(
    clasificacion.to_string(
        index=False,
        formatters={
            "PORCENTAJE":
                "{:.4f}".format,
        }
    )
)


# ============================================================
# CASOS CON MAYOR DIFERENCIA
# ============================================================

print(
    "\n" + "=" * 100
)

print(
    "MAYORES DIFERENCIAS"
)

print("=" * 100)


peores = (
    df
    .sort_values(
        "DIF_499_COMPONENTES",
        ascending=False
    )
    [
        [
            "ANIO",
            "RUC",
            "NOMBRE",
            "CUENTA_499",
            "CUENTA_599",
            "CUENTA_698",
            "CUENTA_699",
            "DIF_499_699",
            "DIF_699_COMPONENTES",
            "DIF_499_COMPONENTES",
        ]
    ]
    .head(25)
)


print(
    peores.to_string(
        index=False
    )
)


# ============================================================
# RESULTADO FINAL
# ============================================================

print(
    "\n" + "=" * 100
)

print(
    "DIAGNÓSTICO PLAN_807 FINALIZADO CORRECTAMENTE"
)

print("=" * 100)