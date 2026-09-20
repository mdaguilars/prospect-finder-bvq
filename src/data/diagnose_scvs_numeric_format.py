from pathlib import Path
from zipfile import ZipFile
import io

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

MAPPING_PATH = (
    PROJECT_ROOT
    / "config"
    / "scvs_account_mapping.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "scvs_numeric_format_diagnostic.csv"
)

ANIOS = range(2015, 2024)


# ============================================================
# FUNCIONES
# ============================================================

def decodificar_bytes(contenido):

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


def contar_lineas_catalogo(
    contenido,
    encoding
):

    texto = contenido.decode(
        encoding
    )

    lineas = [
        linea.strip()
        for linea in texto
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
        if linea.strip()
    ]

    return len(lineas)


def limpiar_base(serie):

    serie = (
        serie
        .astype("string")
        .str.strip()
    )

    return serie.replace(
        {
            "": pd.NA,
            "nan": pd.NA,
            "None": pd.NA,
            "NULL": pd.NA,
        }
    )


def parse_directo(serie):

    return pd.to_numeric(
        limpiar_base(serie),
        errors="coerce"
    )


def parse_quitar_coma(serie):
    """
    Ejemplo:
    1,234,567.89
    """

    serie = limpiar_base(
        serie
    )

    serie = serie.str.replace(
        ",",
        "",
        regex=False
    )

    return pd.to_numeric(
        serie,
        errors="coerce"
    )


def parse_decimal_coma(serie):
    """
    Ejemplo:
    1234567,89
    """

    serie = limpiar_base(
        serie
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


def parse_europeo(serie):
    """
    Ejemplo:
    1.234.567,89
    """

    serie = limpiar_base(
        serie
    )

    serie = serie.str.replace(
        ".",
        "",
        regex=False
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
# CARGAR MAPPING
# ============================================================

mapping = pd.read_csv(
    MAPPING_PATH,
    dtype=str,
    keep_default_na=False
)

planes_incluidos = set(
    mapping["PLAN"]
)

resultados = []


print("=" * 110)
print("DIAGNÓSTICO DE FORMATOS NUMÉRICOS SCVS")
print("=" * 110)


# ============================================================
# RECORRER FUENTES
# ============================================================

for anio in ANIOS:

    zip_path = (
        SCVS_ROOT
        / str(anio)
        / f"estadosFinancieros_{anio}.zip"
    )

    with ZipFile(
        zip_path,
        "r"
    ) as z:

        nombres = z.namelist()

        balances = sorted(
            nombre
            for nombre in nombres
            if "balances" in nombre.lower()
            and not nombre.endswith("/")
        )

        for balance in balances:

            catalogo = balance.replace(
                "balances_",
                "catalogo_"
            )

            catalogo_bytes = z.read(
                catalogo
            )

            encoding_catalogo = (
                decodificar_bytes(
                    catalogo_bytes
                )
            )

            numero_lineas = (
                contar_lineas_catalogo(
                    catalogo_bytes,
                    encoding_catalogo
                )
            )

            plan = (
                f"PLAN_{numero_lineas}"
            )

            if plan not in planes_incluidos:
                continue

            mapping_plan = mapping[
                mapping["PLAN"]
                == plan
            ].copy()

            codigos = set()

            for _, fila in (
                mapping_plan.iterrows()
            ):

                if fila["CODIGO_1"].strip():

                    codigos.add(
                        fila["CODIGO_1"]
                        .strip()
                    )

                if fila["CODIGO_2"].strip():

                    codigos.add(
                        fila["CODIGO_2"]
                        .strip()
                    )

            columnas_cuenta = [
                f"CUENTA_{codigo}"
                for codigo in sorted(
                    codigos
                )
            ]

            balance_bytes = z.read(
                balance
            )

            encoding_balance = (
                decodificar_bytes(
                    balance_bytes
                )
            )

            df = pd.read_csv(
                io.BytesIO(
                    balance_bytes
                ),
                sep="\t",
                encoding=encoding_balance,
                dtype=str,
                usecols=columnas_cuenta,
                low_memory=False
            )

            for _, fila_mapping in (
                mapping_plan.iterrows()
            ):

                variable = (
                    fila_mapping[
                        "VARIABLE"
                    ].strip()
                )

                codigos_variable = [
                    fila_mapping[
                        "CODIGO_1"
                    ].strip(),
                    fila_mapping[
                        "CODIGO_2"
                    ].strip(),
                ]

                codigos_variable = [
                    codigo
                    for codigo
                    in codigos_variable
                    if codigo
                ]

                for codigo in (
                    codigos_variable
                ):

                    columna = (
                        f"CUENTA_{codigo}"
                    )

                    serie = limpiar_base(
                        df[columna]
                    )

                    no_vacios = (
                        serie.notna().sum()
                    )

                    directo = (
                        parse_directo(
                            serie
                        )
                        .notna()
                        .sum()
                    )

                    quitar_coma = (
                        parse_quitar_coma(
                            serie
                        )
                        .notna()
                        .sum()
                    )

                    decimal_coma = (
                        parse_decimal_coma(
                            serie
                        )
                        .notna()
                        .sum()
                    )

                    europeo = (
                        parse_europeo(
                            serie
                        )
                        .notna()
                        .sum()
                    )

                    fallidos_directo = (
                        serie[
                            serie.notna()
                            & parse_directo(
                                serie
                            ).isna()
                        ]
                        .drop_duplicates()
                        .head(5)
                        .tolist()
                    )

                    resultados.append(
                        {
                            "ANIO": anio,
                            "PLAN": plan,
                            "ARCHIVO": balance,
                            "VARIABLE":
                                variable,
                            "CODIGO":
                                codigo,
                            "NO_VACIOS":
                                no_vacios,
                            "DIRECTO_OK":
                                directo,
                            "DIRECTO_PCT":
                                porcentaje(
                                    directo,
                                    no_vacios
                                ),
                            "QUITAR_COMA_OK":
                                quitar_coma,
                            "QUITAR_COMA_PCT":
                                porcentaje(
                                    quitar_coma,
                                    no_vacios
                                ),
                            "DECIMAL_COMA_OK":
                                decimal_coma,
                            "DECIMAL_COMA_PCT":
                                porcentaje(
                                    decimal_coma,
                                    no_vacios
                                ),
                            "EUROPEO_OK":
                                europeo,
                            "EUROPEO_PCT":
                                porcentaje(
                                    europeo,
                                    no_vacios
                                ),
                            "EJEMPLOS_FALLIDOS":
                                " | ".join(
                                    map(
                                        str,
                                        fallidos_directo
                                    )
                                ),
                        }
                    )


# ============================================================
# GUARDAR RESULTADO
# ============================================================

diagnostico = pd.DataFrame(
    resultados
)

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

diagnostico.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# RESUMEN
# ============================================================

print(
    "\nRESUMEN DE CONVERSIÓN "
    "POR VARIABLE"
)

print("-" * 110)

resumen = (
    diagnostico
    .groupby(
        "VARIABLE"
    )
    .agg(
        NO_VACIOS=(
            "NO_VACIOS",
            "sum"
        ),
        DIRECTO_OK=(
            "DIRECTO_OK",
            "sum"
        ),
        QUITAR_COMA_OK=(
            "QUITAR_COMA_OK",
            "sum"
        ),
        DECIMAL_COMA_OK=(
            "DECIMAL_COMA_OK",
            "sum"
        ),
        EUROPEO_OK=(
            "EUROPEO_OK",
            "sum"
        ),
    )
)

for variable, fila in (
    resumen.iterrows()
):

    total = fila[
        "NO_VACIOS"
    ]

    print(
        f"\n{variable}"
    )

    print(
        f"  Valores originales no vacíos: "
        f"{int(total):,}"
    )

    for nombre in [
        "DIRECTO_OK",
        "QUITAR_COMA_OK",
        "DECIMAL_COMA_OK",
        "EUROPEO_OK",
    ]:

        cantidad = int(
            fila[nombre]
        )

        pct = porcentaje(
            cantidad,
            total
        )

        print(
            f"  {nombre:<20} "
            f"{cantidad:>10,} "
            f"({pct:6.2f}%)"
        )


print(
    "\n" + "=" * 110
)

print(
    "EJEMPLOS DE VALORES QUE FALLAN "
    "CON LA CONVERSIÓN DIRECTA"
)

print("=" * 110)


fallos = diagnostico[
    diagnostico[
        "EJEMPLOS_FALLIDOS"
    ].ne("")
][
    [
        "ANIO",
        "PLAN",
        "VARIABLE",
        "CODIGO",
        "EJEMPLOS_FALLIDOS",
    ]
]


print(
    fallos
    .head(40)
    .to_string(
        index=False
    )
)


print(
    "\nDiagnóstico guardado en:"
)

print(
    OUTPUT_PATH
)