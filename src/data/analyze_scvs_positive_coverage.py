from pathlib import Path
from zipfile import ZipFile
import csv
import io

import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCVS_FINANCIALS_ROOT = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "scvs"
    / "estados_financieros"
)

SCVS_EMISORES_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "scvs"
    / "mercado_valores"
    / "listado_entes_65001_1789908466941.xlsx"
)

ANIOS = range(2015, 2024)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def decodificar(contenido):
    """
    Decodifica archivos históricos de SCVS.
    """

    for codificacion in [
        "utf-8-sig",
        "utf-8",
        "latin-1",
        "cp1252",
    ]:

        try:
            return contenido.decode(codificacion)

        except UnicodeDecodeError:
            continue

    raise ValueError(
        "No fue posible decodificar el archivo."
    )


def detectar_delimitador(texto):
    """
    Detecta el delimitador utilizado en el TXT.
    """

    primera_linea = texto.splitlines()[0]

    candidatos = [
        "\t",
        ";",
        "|",
        ",",
    ]

    conteos = {
        delimitador: primera_linea.count(delimitador)
        for delimitador in candidatos
    }

    return max(
        conteos,
        key=conteos.get
    )


def contar_lineas_catalogo(texto):
    """
    Obtiene el número de registros reales del catálogo.
    """

    lineas = [
        linea.strip()
        for linea in texto
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
        if linea.strip()
    ]

    return len(lineas)


# ============================================================
# 1. HISTÓRICO DE EMISORES
# ============================================================

print("=" * 100)
print("COBERTURA DE FUTUROS EMISORES POR PLAN CONTABLE")
print("=" * 100)

emisores = pd.read_excel(
    SCVS_EMISORES_PATH,
    header=4
)

emisores["RUC"] = (
    emisores["IDENTIFICACIÓN"]
    .astype("string")
    .str.strip()
)

emisores = emisores[
    emisores["RUC"].str.fullmatch(
        r"\d{13}",
        na=False
    )
].copy()

emisores["FECHA_INSCRIPCION"] = pd.to_datetime(
    emisores["FECHA INSCRIPCIÓN"],
    errors="coerce"
)

primera_inscripcion = (
    emisores
    .groupby("RUC")["FECHA_INSCRIPCION"]
    .min()
    .to_dict()
)

print(
    f"Emisores históricos identificados: "
    f"{len(primera_inscripcion):,}"
)


# ============================================================
# 2. RECORRIDO DE BALANCES
# ============================================================

resumen = []

for anio in ANIOS:

    print("\n" + "=" * 100)
    print(f"COHORTE {anio}")
    print("=" * 100)

    zip_path = (
        SCVS_FINANCIALS_ROOT
        / str(anio)
        / f"estadosFinancieros_{anio}.zip"
    )

    fecha_inicio_evento = pd.Timestamp(
        year=anio + 1,
        month=1,
        day=1
    )

    fecha_fin_evento = pd.Timestamp(
        year=anio + 2,
        month=12,
        day=31
    )

    positivos_teoricos = {
        ruc
        for ruc, fecha in primera_inscripcion.items()
        if (
            fecha_inicio_evento
            <= fecha
            <= fecha_fin_evento
        )
    }

    print(
        f"Futuros emisores teóricos "
        f"{anio + 1}-{anio + 2}: "
        f"{len(positivos_teoricos)}"
    )

    rucs_totales_anio = set()
    positivos_encontrados_anio = set()

    with ZipFile(zip_path, "r") as z:

        balances = sorted(
            nombre
            for nombre in z.namelist()
            if "balances" in nombre.lower()
            and not nombre.endswith("/")
        )

        for balance in balances:

            catalogo = balance.replace(
                "balances_",
                "catalogo_"
            )

            # --------------------------------------------
            # IDENTIFICAR EL PLAN POR NÚMERO DE CUENTAS
            # --------------------------------------------

            catalogo_texto = decodificar(
                z.read(catalogo)
            )

            numero_cuentas = contar_lineas_catalogo(
                catalogo_texto
            )

            plan = f"PLAN_{numero_cuentas}"

            # --------------------------------------------
            # LEER RUC DEL BALANCE
            # --------------------------------------------

            balance_texto = decodificar(
                z.read(balance)
            )

            delimitador = detectar_delimitador(
                balance_texto
            )

            lector = csv.DictReader(
                io.StringIO(balance_texto),
                delimiter=delimitador
            )

            columnas = lector.fieldnames or []

            columna_ruc = None

            for columna in columnas:

                if columna.strip().upper() == "RUC":
                    columna_ruc = columna
                    break

            if columna_ruc is None:

                raise ValueError(
                    f"No se encontró RUC en {balance}"
                )

            rucs_plan = set()

            for fila in lector:

                ruc = (
                    fila.get(
                        columna_ruc,
                        ""
                    )
                    or ""
                ).strip()

                if (
                    len(ruc) == 13
                    and ruc.isdigit()
                ):
                    rucs_plan.add(ruc)

            positivos_plan = (
                rucs_plan
                & positivos_teoricos
            )

            rucs_totales_anio.update(
                rucs_plan
            )

            positivos_encontrados_anio.update(
                positivos_plan
            )

            porcentaje_positivos = (
                100
                * len(positivos_plan)
                / len(positivos_teoricos)
                if positivos_teoricos
                else 0
            )

            resumen.append(
                {
                    "ANIO": anio,
                    "PLAN": plan,
                    "RUC": len(rucs_plan),
                    "POSITIVOS": len(
                        positivos_plan
                    ),
                }
            )

            print(
                f"{plan:<10} | "
                f"RUC: {len(rucs_plan):>7,} | "
                f"Positivos: "
                f"{len(positivos_plan):>3} | "
                f"{porcentaje_positivos:6.2f}% "
                f"de los positivos teóricos"
            )

    cobertura = (
        100
        * len(positivos_encontrados_anio)
        / len(positivos_teoricos)
        if positivos_teoricos
        else 0
    )

    print(
        f"\nRUC financieros totales: "
        f"{len(rucs_totales_anio):,}"
    )

    print(
        f"Positivos encontrados: "
        f"{len(positivos_encontrados_anio)}"
    )

    print(
        f"Positivos sin información financiera: "
        f"{len(positivos_teoricos - positivos_encontrados_anio)}"
    )

    print(
        f"Cobertura positiva total: "
        f"{cobertura:.2f}%"
    )


# ============================================================
# 3. RESUMEN ACUMULADO POR PLAN
# ============================================================

df_resumen = pd.DataFrame(
    resumen
)

print("\n" + "=" * 100)
print("POSITIVOS ACUMULADOS POR PLAN")
print("=" * 100)

acumulado = (
    df_resumen
    .groupby("PLAN")
    .agg(
        OBSERVACIONES_EMPRESA_ANIO=(
            "RUC",
            "sum"
        ),
        POSITIVOS=(
            "POSITIVOS",
            "sum"
        )
    )
    .sort_values(
        "POSITIVOS",
        ascending=False
    )
)

print(
    acumulado.to_string()
)

print(
    "\nAnálisis finalizado correctamente."
)