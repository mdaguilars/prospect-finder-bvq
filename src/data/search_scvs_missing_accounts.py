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

ANIO = 2015


# ============================================================
# TÉRMINOS A BUSCAR
# ============================================================

BUSQUEDAS = [
    "TOTAL ACTIVO",
    "ACTIVO CORRIENTE",
    "TOTAL PASIVO",
    "PASIVO CORRIENTE",
    "PASIVO NO CORRIENTE",
    "TOTAL PATRIMONIO",
    "INVENTARIO",
    "COSTO DE VENTAS",
    "GASTOS ADMINISTRATIVOS",
    "GASTOS FINANCIEROS",
    "UTILIDAD BRUTA",
    "UTILIDAD OPERACIONAL",
    "UTILIDAD OPERATIVA",
    "UTILIDAD NETA",
    "GANANCIA NETA",
    "TOTAL INGRESOS",
]


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
            return contenido.decode(
                codificacion
            )

        except UnicodeDecodeError:
            continue

    raise ValueError(
        "No fue posible decodificar."
    )


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
        texto = texto.replace(
            origen,
            destino
        )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


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
# LECTURA
# ============================================================

zip_path = (
    SCVS_ROOT
    / str(ANIO)
    / f"estadosFinancieros_{ANIO}.zip"
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

        # PLAN_413 no se analiza para el MVP.
        if plan == "PLAN_413":
            continue

        print(
            "\n"
            + "=" * 110
        )

        print(
            f"{plan} | {catalogo}"
        )

        print(
            "=" * 110
        )

        registros = []

        for linea in lineas:

            partes = linea.split(
                None,
                1
            )

            if len(partes) != 2:
                continue

            codigo = partes[0].strip()

            descripcion = (
                partes[1].strip()
            )

            descripcion_norm = normalizar(
                descripcion
            )

            registros.append(
                (
                    codigo,
                    descripcion,
                    descripcion_norm,
                )
            )

        for busqueda in BUSQUEDAS:

            busqueda_norm = normalizar(
                busqueda
            )

            encontrados = [
                (
                    codigo,
                    descripcion
                )
                for (
                    codigo,
                    descripcion,
                    descripcion_norm
                )
                in registros
                if busqueda_norm
                in descripcion_norm
            ]

            print(
                f"\nBUSCAR: {busqueda}"
            )

            if encontrados:

                for (
                    codigo,
                    descripcion
                ) in encontrados[:20]:

                    print(
                        f"  {codigo:<15} "
                        f"{descripcion}"
                    )

            else:

                print(
                    "  -- SIN RESULTADOS --"
                )