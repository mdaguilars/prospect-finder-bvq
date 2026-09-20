from pathlib import Path
from zipfile import ZipFile


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


# Usamos 2015 porque contiene los 8 planes.
ANIO = 2015


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

    raise ValueError(
        "No fue posible decodificar el archivo."
    )


def lineas_validas(texto):
    return [
        linea.strip()
        for linea in texto
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
        if linea.strip()
    ]


# ============================================================
# LECTURA DE CATÁLOGOS
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

        lineas = lineas_validas(
            texto
        )

        plan = f"PLAN_{len(lineas)}"

        print("\n" + "=" * 110)
        print(
            f"{plan} | {catalogo}"
        )
        print("=" * 110)

        print(
            f"Total de líneas: {len(lineas)}"
        )

        print("\nPRIMERAS 35 LÍNEAS DEL CATÁLOGO:\n")

        for linea in lineas[:35]:
            print(linea)