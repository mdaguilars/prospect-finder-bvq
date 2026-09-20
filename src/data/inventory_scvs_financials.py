from pathlib import Path
from zipfile import ZipFile, BadZipFile


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

ANIOS = range(2015, 2026)


# ============================================================
# FUNCIÓN DE CLASIFICACIÓN
# ============================================================

def clasificar_archivo(nombre):
    """
    Clasifica de forma preliminar los archivos internos
    encontrados dentro de cada ZIP.
    """

    nombre_lower = nombre.lower()

    if "catalogo" in nombre_lower:
        return "CATALOGO"

    if "balance" in nombre_lower:
        return "BALANCE"

    return "OTRO"


# ============================================================
# INVENTARIO
# ============================================================

print("=" * 90)
print("INVENTARIO DE ESTADOS FINANCIEROS SCVS 2015-2025")
print("=" * 90)

total_archivos = 0
total_balances = 0
total_catalogos = 0
total_otros = 0


for anio in ANIOS:

    carpeta = SCVS_FINANCIALS_ROOT / str(anio)

    zip_path = (
        carpeta
        / f"estadosFinancieros_{anio}.zip"
    )

    print("\n" + "=" * 90)
    print(f"AÑO {anio}")
    print("=" * 90)

    if not zip_path.exists():

        print(
            f"ERROR: No se encontró el archivo "
            f"{zip_path.name}"
        )

        continue

    print(
        f"ZIP: {zip_path.name}"
    )

    print(
        f"Tamaño ZIP: "
        f"{zip_path.stat().st_size / (1024 ** 2):.2f} MB"
    )

    try:

        with ZipFile(zip_path, "r") as z:

            archivos = [
                info
                for info in z.infolist()
                if not info.is_dir()
            ]

            balances = 0
            catalogos = 0
            otros = 0

            print(
                f"Archivos internos: {len(archivos)}"
            )

            print("\nCONTENIDO:")

            for info in archivos:

                tipo = clasificar_archivo(
                    info.filename
                )

                if tipo == "BALANCE":
                    balances += 1

                elif tipo == "CATALOGO":
                    catalogos += 1

                else:
                    otros += 1

                tamaño_mb = (
                    info.file_size
                    / (1024 ** 2)
                )

                print(
                    f"  [{tipo:8}] "
                    f"{info.filename} "
                    f"| {tamaño_mb:.2f} MB"
                )

            print("\nRESUMEN DEL AÑO")

            print(
                f"  Balances : {balances}"
            )

            print(
                f"  Catálogos: {catalogos}"
            )

            print(
                f"  Otros    : {otros}"
            )

            total_archivos += len(archivos)
            total_balances += balances
            total_catalogos += catalogos
            total_otros += otros

    except BadZipFile:

        print(
            "ERROR: El archivo ZIP está dañado "
            "o no tiene un formato ZIP válido."
        )


# ============================================================
# RESUMEN GENERAL
# ============================================================

print("\n" + "=" * 90)
print("RESUMEN GENERAL")
print("=" * 90)

print(
    f"Archivos internos totales: "
    f"{total_archivos}"
)

print(
    f"Archivos clasificados como BALANCE: "
    f"{total_balances}"
)

print(
    f"Archivos clasificados como CATALOGO: "
    f"{total_catalogos}"
)

print(
    f"Otros archivos: "
    f"{total_otros}"
)

print("\nInventario finalizado correctamente.")