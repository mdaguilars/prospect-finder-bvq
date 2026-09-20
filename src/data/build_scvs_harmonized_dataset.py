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
    / "data"
    / "interim"
    / "scvs_financials_harmonized_2015_2023.csv.gz"
)

SUMMARY_PATH = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "scvs_harmonization_summary.csv"
)

ANIOS = range(2015, 2024)

COLUMNAS_IDENTIFICACION = [
    "AÑO",
    "EXPEDIENTE",
    "RUC",
    "NOMBRE",
    "RAMA_ACTIVIDAD",
    "DESCRIPCION_RAMA",
    "CIIU",
]


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def decodificar_bytes(contenido):
    """
    Detecta una codificación válida para los archivos SCVS.
    """

    codificaciones = [
        "utf-8-sig",
        "utf-8",
        "latin-1",
        "cp1252",
    ]

    for codificacion in codificaciones:
        try:
            contenido.decode(codificacion)
            return codificacion
        except UnicodeDecodeError:
            continue

    raise ValueError(
        "No fue posible determinar la codificación."
    )


def contar_lineas_catalogo(contenido, encoding):
    """
    Determina el plan según el número de líneas del catálogo.
    """

    texto = contenido.decode(encoding)

    lineas = [
        linea.strip()
        for linea in texto
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
        if linea.strip()
    ]

    return len(lineas)


def columna_cuenta(codigo):
    """
    Convierte el código contable en el nombre de la columna
    utilizada dentro del archivo de balances.
    """

    codigo = str(codigo).strip()

    if not codigo:
        return None

    return f"CUENTA_{codigo}"


def convertir_numerico(serie):
    """
    Convierte valores financieros SCVS a formato numérico.

    Los archivos históricos SCVS utilizan coma como
    separador decimal, por ejemplo:

        49578263,43

    Por lo tanto:
        49578263,43 -> 49578263.43

    Los valores vacíos o no interpretables quedan como NaN.
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


def validar_duplicados(df, archivo):
    """
    Verifica que un mismo RUC no tenga registros diferentes
    dentro de un mismo archivo.

    Las filas completamente idénticas pueden eliminarse.
    Los registros distintos para un mismo RUC detienen
    el procesamiento.
    """

    duplicados = df[
        df.duplicated(
            subset=["RUC"],
            keep=False
        )
    ].copy()

    if duplicados.empty:
        return df, 0

    cantidad_original = len(df)

    df = df.drop_duplicates()

    duplicados_restantes = df[
        df.duplicated(
            subset=["RUC"],
            keep=False
        )
    ]

    if not duplicados_restantes.empty:

        rucs_conflictivos = (
            duplicados_restantes["RUC"]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "\nSe encontraron registros distintos "
            f"para el mismo RUC en {archivo}.\n"
            f"RUC conflictivos: "
            f"{rucs_conflictivos[:20]}"
        )

    eliminados = (
        cantidad_original
        - len(df)
    )

    return df, eliminados


# ============================================================
# CARGAR TABLA DE HOMOLOGACIÓN
# ============================================================

print("=" * 100)
print(
    "CONSTRUCCIÓN DEL DATASET FINANCIERO "
    "HOMOLOGADO SCVS"
)
print("=" * 100)

if not MAPPING_PATH.exists():

    raise FileNotFoundError(
        "No existe el archivo de homologación:\n"
        f"{MAPPING_PATH}"
    )


mapping = pd.read_csv(
    MAPPING_PATH,
    dtype=str,
    keep_default_na=False
)


columnas_mapping_requeridas = [
    "PLAN",
    "VARIABLE",
    "OPERACION",
    "CODIGO_1",
    "CODIGO_2",
    "CALIDAD",
    "NOTA",
]


faltantes_mapping = [
    columna
    for columna in columnas_mapping_requeridas
    if columna not in mapping.columns
]


if faltantes_mapping:

    raise ValueError(
        "Faltan columnas en "
        "scvs_account_mapping.csv: "
        f"{faltantes_mapping}"
    )


if mapping.duplicated(
    subset=[
        "PLAN",
        "VARIABLE",
    ]
).any():

    duplicados = mapping[
        mapping.duplicated(
            subset=[
                "PLAN",
                "VARIABLE",
            ],
            keep=False
        )
    ]

    raise ValueError(
        "Existen combinaciones PLAN-VARIABLE "
        "duplicadas en el mapping:\n"
        f"{duplicados}"
    )


planes_mapping = sorted(
    mapping["PLAN"]
    .drop_duplicates()
    .tolist()
)


variables_homologadas = sorted(
    mapping["VARIABLE"]
    .drop_duplicates()
    .tolist()
)


print(
    f"Planes incluidos en el MVP: "
    f"{len(planes_mapping)}"
)

print(
    "Planes:",
    ", ".join(planes_mapping)
)

print(
    f"Variables financieras homologadas: "
    f"{len(variables_homologadas)}"
)

print(
    "Variables:",
    ", ".join(
        variables_homologadas
    )
)


# ============================================================
# PROCESAR AÑOS Y FORMATOS
# ============================================================

datasets = []
resumen = []


for anio in ANIOS:

    print("\n" + "=" * 100)
    print(f"AÑO {anio}")
    print("=" * 100)

    zip_path = (
        SCVS_ROOT
        / str(anio)
        / f"estadosFinancieros_{anio}.zip"
    )

    if not zip_path.exists():

        raise FileNotFoundError(
            f"No existe:\n{zip_path}"
        )

    datasets_anio = []

    with ZipFile(zip_path, "r") as z:

        nombres_zip = z.namelist()

        balances = sorted(
            nombre
            for nombre in nombres_zip
            if "balances" in nombre.lower()
            and not nombre.endswith("/")
        )

        for balance in balances:

            catalogo = balance.replace(
                "balances_",
                "catalogo_"
            )

            if catalogo not in nombres_zip:

                raise ValueError(
                    "No existe el catálogo "
                    f"para {balance}"
                )

            # =================================================
            # IDENTIFICAR PLAN
            # =================================================

            catalogo_bytes = z.read(
                catalogo
            )

            catalogo_encoding = (
                decodificar_bytes(
                    catalogo_bytes
                )
            )

            numero_lineas = (
                contar_lineas_catalogo(
                    catalogo_bytes,
                    catalogo_encoding
                )
            )

            plan = (
                f"PLAN_{numero_lineas}"
            )

            # =================================================
            # OMITIR PLANES FUERA DEL MVP
            # =================================================

            if plan not in planes_mapping:

                print(
                    f"{plan:<10} | "
                    f"{balance:<25} | "
                    "OMITIDO DEL MVP"
                )

                resumen.append(
                    {
                        "ANIO": anio,
                        "PLAN": plan,
                        "ARCHIVO": balance,
                        "ESTADO": "OMITIDO",
                        "FILAS_ORIGINALES": 0,
                        "RUC_VALIDOS": 0,
                        "DUPLICADOS_EXACTOS_ELIMINADOS": 0,
                    }
                )

                continue

            mapping_plan = mapping[
                mapping["PLAN"] == plan
            ].copy()

            # =================================================
            # DETERMINAR CUENTAS NECESARIAS
            # =================================================

            codigos = set()

            for _, fila_mapping in (
                mapping_plan.iterrows()
            ):

                codigo_1 = (
                    fila_mapping[
                        "CODIGO_1"
                    ]
                    .strip()
                )

                codigo_2 = (
                    fila_mapping[
                        "CODIGO_2"
                    ]
                    .strip()
                )

                if codigo_1:

                    codigos.add(
                        columna_cuenta(
                            codigo_1
                        )
                    )

                if codigo_2:

                    codigos.add(
                        columna_cuenta(
                            codigo_2
                        )
                    )

            # =================================================
            # LEER ARCHIVO BALANCE
            # =================================================

            balance_bytes = z.read(
                balance
            )

            balance_encoding = (
                decodificar_bytes(
                    balance_bytes
                )
            )

            # Primera lectura únicamente para
            # conocer los nombres de columnas.
            cabecera = pd.read_csv(
                io.BytesIO(
                    balance_bytes
                ),
                sep="\t",
                encoding=balance_encoding,
                nrows=0
            )

            columnas_disponibles = (
                cabecera.columns.tolist()
            )

            # =================================================
            # VALIDAR METADATOS
            # =================================================

            columnas_id_disponibles = [
                columna
                for columna
                in COLUMNAS_IDENTIFICACION
                if columna
                in columnas_disponibles
            ]

            if (
                "RUC"
                not in columnas_id_disponibles
            ):

                raise ValueError(
                    f"{balance} no contiene "
                    "columna RUC."
                )

            # =================================================
            # VALIDAR CUENTAS DEL MAPPING
            # =================================================

            cuentas_faltantes = sorted(
                cuenta
                for cuenta in codigos
                if cuenta
                not in columnas_disponibles
            )

            if cuentas_faltantes:

                raise ValueError(
                    f"\n{balance} ({plan}) "
                    "no contiene cuentas requeridas "
                    "por el mapping:\n"
                    f"{cuentas_faltantes}"
                )

            columnas_lectura = (
                columnas_id_disponibles
                + sorted(codigos)
            )

            # =================================================
            # LEER SOLO COLUMNAS NECESARIAS
            # =================================================

            df = pd.read_csv(
                io.BytesIO(
                    balance_bytes
                ),
                sep="\t",
                encoding=balance_encoding,
                dtype=str,
                usecols=columnas_lectura,
                low_memory=False
            )

            filas_originales = len(df)

            # =================================================
            # NORMALIZAR RUC
            # =================================================

            df["RUC"] = (
                df["RUC"]
                .astype("string")
                .str.strip()
            )

            df = df[
                df["RUC"]
                .str.fullmatch(
                    r"\d{13}",
                    na=False
                )
            ].copy()

            # =================================================
            # VALIDAR DUPLICADOS
            # =================================================

            (
                df,
                duplicados_eliminados
            ) = validar_duplicados(
                df,
                balance
            )

            # =================================================
            # CREAR DATASET HOMOLOGADO
            # =================================================
            #
            # IMPORTANTE:
            # Se crea el DataFrame con el mismo índice de df.
            # De esta forma ANIO se asigna correctamente
            # a todas las observaciones.
            # =================================================

            salida = pd.DataFrame(
                index=df.index.copy()
            )

            salida["ANIO"] = anio

            for columna in [
                "EXPEDIENTE",
                "RUC",
                "NOMBRE",
                "RAMA_ACTIVIDAD",
                "DESCRIPCION_RAMA",
                "CIIU",
            ]:

                if columna in df.columns:

                    salida[columna] = (
                        df[columna]
                    )

                else:

                    salida[columna] = pd.NA

            # PLAN_CONTABLE se conserva únicamente
            # para trazabilidad.
            #
            # NO se utilizará como predictor.
            salida[
                "PLAN_CONTABLE"
            ] = plan

            # =================================================
            # HOMOLOGAR VARIABLES
            # =================================================

            for _, fila_mapping in (
                mapping_plan.iterrows()
            ):

                variable = (
                    fila_mapping[
                        "VARIABLE"
                    ]
                    .strip()
                )

                operacion = (
                    fila_mapping[
                        "OPERACION"
                    ]
                    .strip()
                    .upper()
                )

                codigo_1 = (
                    fila_mapping[
                        "CODIGO_1"
                    ]
                    .strip()
                )

                codigo_2 = (
                    fila_mapping[
                        "CODIGO_2"
                    ]
                    .strip()
                )

                columna_1 = (
                    columna_cuenta(
                        codigo_1
                    )
                )

                valor_1 = (
                    convertir_numerico(
                        df[columna_1]
                    )
                )

                if operacion == "DIRECTA":

                    salida[
                        variable
                    ] = valor_1

                elif operacion == "SUMA":

                    if not codigo_2:

                        raise ValueError(
                            f"{plan} - "
                            f"{variable}: "
                            "operación SUMA "
                            "sin CODIGO_2."
                        )

                    columna_2 = (
                        columna_cuenta(
                            codigo_2
                        )
                    )

                    valor_2 = (
                        convertir_numerico(
                            df[columna_2]
                        )
                    )

                    salida[
                        variable
                    ] = (
                        valor_1.fillna(0)
                        + valor_2.fillna(0)
                    )

                    ambos_vacios = (
                        valor_1.isna()
                        & valor_2.isna()
                    )

                    salida.loc[
                        ambos_vacios,
                        variable
                    ] = pd.NA

                else:

                    raise ValueError(
                        "Operación desconocida: "
                        f"{operacion}"
                    )

            # Normalizar índice antes de incorporar
            # el bloque al histórico.
            salida = (
                salida
                .reset_index(
                    drop=True
                )
            )

            # Validación explícita de ANIO.
            if salida[
                "ANIO"
            ].isna().any():

                raise ValueError(
                    f"{balance}: se generaron "
                    "valores ANIO vacíos."
                )

            datasets_anio.append(
                salida
            )

            print(
                f"{plan:<10} | "
                f"{balance:<25} | "
                f"Filas: "
                f"{filas_originales:>7,} | "
                f"RUC válidos: "
                f"{len(salida):>7,} | "
                "Duplicados eliminados: "
                f"{duplicados_eliminados}"
            )

            resumen.append(
                {
                    "ANIO": anio,
                    "PLAN": plan,
                    "ARCHIVO": balance,
                    "ESTADO": "INCLUIDO",
                    "FILAS_ORIGINALES":
                        filas_originales,
                    "RUC_VALIDOS":
                        len(salida),
                    "DUPLICADOS_EXACTOS_ELIMINADOS":
                        duplicados_eliminados,
                }
            )

    # ========================================================
    # VALIDAR RUC ENTRE PLANES DEL MISMO AÑO
    # ========================================================

    if not datasets_anio:

        raise ValueError(
            "No se generaron registros "
            f"para {anio}."
        )

    df_anio = pd.concat(
        datasets_anio,
        ignore_index=True
    )

    duplicados_entre_planes = (
        df_anio[
            df_anio.duplicated(
                subset=["RUC"],
                keep=False
            )
        ]
    )

    if not (
        duplicados_entre_planes.empty
    ):

        ejemplo = (
            duplicados_entre_planes[
                [
                    "RUC",
                    "PLAN_CONTABLE"
                ]
            ]
            .sort_values(
                "RUC"
            )
            .head(30)
        )

        raise ValueError(
            "\nExisten RUC presentes "
            "en más de un plan durante "
            f"{anio}:\n"
            f"{ejemplo}"
        )

    print(
        f"\nTOTAL MVP {anio}: "
        f"{len(df_anio):,} empresas"
    )

    datasets.append(
        df_anio
    )


# ============================================================
# UNIR HISTÓRICO
# ============================================================

dataset_final = pd.concat(
    datasets,
    ignore_index=True
)


# ============================================================
# VALIDAR AÑO ANTES DE CONVERTIR
# ============================================================

if dataset_final[
    "ANIO"
].isna().any():

    cantidad_anio_na = (
        dataset_final[
            "ANIO"
        ]
        .isna()
        .sum()
    )

    raise ValueError(
        "El dataset consolidado contiene "
        f"{cantidad_anio_na} valores "
        "ANIO vacíos."
    )


dataset_final[
    "ANIO"
] = pd.to_numeric(
    dataset_final["ANIO"],
    errors="raise"
).astype("int64")


dataset_final = (
    dataset_final
    .sort_values(
        [
            "ANIO",
            "RUC",
        ]
    )
    .reset_index(
        drop=True
    )
)


# ============================================================
# VALIDACIÓN CLAVE EMPRESA-AÑO
# ============================================================

duplicados_empresa_anio = (
    dataset_final[
        dataset_final.duplicated(
            subset=[
                "RUC",
                "ANIO",
            ],
            keep=False
        )
    ]
)


if not (
    duplicados_empresa_anio.empty
):

    raise ValueError(
        "El dataset final contiene "
        "claves RUC-ANIO duplicadas."
    )


# ============================================================
# CREAR DIRECTORIOS
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
# GUARDAR DATASET
# ============================================================

dataset_final.to_csv(
    OUTPUT_PATH,
    index=False,
    compression="gzip"
)


pd.DataFrame(
    resumen
).to_csv(
    SUMMARY_PATH,
    index=False
)


# ============================================================
# REPORTE FINAL
# ============================================================

print("\n" + "=" * 100)

print(
    "DATASET HOMOLOGADO "
    "CONSTRUIDO CORRECTAMENTE"
)

print("=" * 100)


print(
    "Observaciones empresa-año: "
    f"{len(dataset_final):,}"
)


print(
    "Empresas únicas: "
    f"{dataset_final['RUC'].nunique():,}"
)


print(
    "Años: "
    f"{dataset_final['ANIO'].min()} "
    "- "
    f"{dataset_final['ANIO'].max()}"
)


print(
    "\nObservaciones por año:"
)

print(
    dataset_final[
        "ANIO"
    ]
    .value_counts()
    .sort_index()
    .to_string()
)


print(
    "\nObservaciones por plan:"
)

print(
    dataset_final[
        "PLAN_CONTABLE"
    ]
    .value_counts()
    .sort_index()
    .to_string()
)


print(
    "\nValores no nulos "
    "por variable:"
)

for variable in variables_homologadas:

    if variable in (
        dataset_final.columns
    ):

        disponibles = (
            dataset_final[
                variable
            ]
            .notna()
            .sum()
        )

        porcentaje = (
            100
            * disponibles
            / len(dataset_final)
        )

        print(
            f"{variable:<25} "
            f"{disponibles:>10,} "
            f"({porcentaje:6.2f}%)"
        )


print(
    "\nDataset:"
)

print(
    OUTPUT_PATH
)


print(
    "\nResumen de procesamiento:"
)

print(
    SUMMARY_PATH
)