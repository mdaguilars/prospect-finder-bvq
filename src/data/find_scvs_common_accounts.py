from pathlib import Path
from zipfile import ZipFile
import re


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

# 2015 contiene los 8 planes.
ANIO_REFERENCIA = 2015


# ============================================================
# CONCEPTOS QUE QUEREMOS HOMOLOGAR
# ============================================================

CONCEPTOS = {
    "ACTIVO_TOTAL": [
        r"^ACTIVO$",
        r"TOTAL ACTIVO$",
        r"TOTAL ACTIVOS$",
    ],

    "ACTIVO_CORRIENTE": [
        r"^ACTIVO CORRIENTE$",
        r"TOTAL ACTIVO CORRIENTE",
    ],

    "EFECTIVO": [
        r"^EFECTIVO Y EQUIVALENTES",
        r"^EFECTIVO Y EQUIVALENTES AL EFECTIVO",
    ],

    "PASIVO_TOTAL": [
        r"^PASIVO$",
        r"TOTAL PASIVO$",
        r"TOTAL PASIVOS$",
    ],

    "PASIVO_CORRIENTE": [
        r"^PASIVO CORRIENTE$",
        r"TOTAL PASIVO CORRIENTE",
    ],

    "PASIVO_NO_CORRIENTE": [
        r"^PASIVO NO CORRIENTE$",
        r"TOTAL PASIVO NO CORRIENTE",
    ],

    "PATRIMONIO": [
        r"^PATRIMONIO NETO$",
        r"TOTAL PATRIMONIO",
        r"TOTAL PATRIMONIO NETO",
    ],

    "CAPITAL": [
        r"^CAPITAL$",
        r"^CAPITAL SOCIAL$",
    ],

    "INVENTARIOS": [
        r"^INVENTARIOS$",
        r"TOTAL INVENTARIOS",
    ],

    "INGRESOS": [
        r"INGRESOS DE ACTIVIDADES ORDINARIAS$",
        r"TOTAL INGRESOS ACTIVIDADES ORDINARIAS",
        r"TOTAL INGRESOS$",
    ],

    "COSTO_VENTAS": [
        r"^COSTO DE VENTAS",
        r"TOTAL COSTO DE VENTAS",
    ],

    "GASTOS_ADMINISTRATIVOS": [
        r"GASTOS ADMINISTRATIVOS",
    ],

    "GASTOS_FINANCIEROS": [
        r"GASTOS FINANCIEROS",
    ],

    "UTILIDAD_BRUTA": [
        r"UTILIDAD BRUTA",
        r"GANANCIA BRUTA",
    ],

    "UTILIDAD_OPERACIONAL": [
        r"UTILIDAD OPERACIONAL",
        r"UTILIDAD OPERATIVA",
        r"GANANCIA OPERACIONAL",
    ],

    "UTILIDAD_NETA": [
        r"GANANCIA NETA DEL PERIODO",
        r"UTILIDAD NETA",
        r"UTILIDAD DESPUES DE IMPUESTO",
        r"UTILIDAD DESPUÉS DE IMPUESTO",
    ],
}


# ============================================================
# FUNCIONES
# ============================================================

def decodificar(contenido):
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

    raise ValueError("No fue posible decodificar.")


def normalizar(texto):
    texto = texto.upper()

    reemplazos = {
        "Á": "A",
        "É": "E",
        "Í": "I",
        "Ó": "O",
        "Ú": "U",
        "Ñ": "N",
    }

    for origen, destino in reemplazos.items():
        texto = texto.replace(origen, destino)

    texto = re.sub(
        r"\s+",
        " ",
        texto
    ).strip()

    return texto


def obtener_lineas(texto):
    return [
        linea.strip()
        for linea in texto
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
        if linea.strip()
    ]


# ============================================================
# LECTURA DE LOS 8 CATÁLOGOS
# ============================================================

zip_path = (
    SCVS_ROOT
    / str(ANIO_REFERENCIA)
    / f"estadosFinancieros_{ANIO_REFERENCIA}.zip"
)

with ZipFile(zip_path, "r") as z:

    catalogos = sorted(
        nombre
        for nombre in z.namelist()
        if "catalogo" in nombre.lower()
        and not nombre.endswith("/")
    )

    for catalogo in catalogos:

        texto = decodificar(
            z.read(catalogo)
        )

        lineas = obtener_lineas(
            texto
        )

        plan = f"PLAN_{len(lineas)}"

        print("\n" + "=" * 110)
        print(f"{plan} | {catalogo}")
        print("=" * 110)

        cuentas = []

        for linea in lineas:

            partes = linea.split(
                None,
                1
            )

            if len(partes) != 2:
                continue

            codigo = partes[0].strip()
            descripcion = partes[1].strip()

            cuentas.append(
                (
                    codigo,
                    descripcion,
                    normalizar(descripcion),
                )
            )

        for concepto, patrones in CONCEPTOS.items():

            encontrados = []

            for codigo, descripcion, descripcion_norm in cuentas:

                for patron in patrones:

                    patron_norm = normalizar(
                        patron
                    )

                    if re.search(
                        patron_norm,
                        descripcion_norm
                    ):
                        encontrados.append(
                            (
                                codigo,
                                descripcion
                            )
                        )
                        break

            print(f"\n{concepto}")

            if encontrados:

                for codigo, descripcion in encontrados[:15]:

                    print(
                        f"  {codigo:<15} "
                        f"{descripcion}"
                    )

            else:

                print(
                    "  -- SIN COINCIDENCIA AUTOMÁTICA --"
                )