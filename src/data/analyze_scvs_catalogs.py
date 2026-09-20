from pathlib import Path
from zipfile import ZipFile
import hashlib


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

ANIOS = range(2015, 2026)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def decodificar_contenido(contenido_bytes):
    """
    Intenta decodificar los catálogos utilizando las
    codificaciones más probables.
    """

    codificaciones = [
        "utf-8-sig",
        "utf-8",
        "latin-1",
        "cp1252",
    ]

    for codificacion in codificaciones:
        try:
            return contenido_bytes.decode(codificacion), codificacion
        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        "No fue posible decodificar el archivo"
    )


def normalizar_texto(texto):
    """
    Normaliza saltos de línea y espacios exteriores
    para comparar catálogos entre años.
    """

    lineas = [
        linea.strip()
        for linea in texto.replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
        if linea.strip()
    ]

    return "\n".join(lineas)


def obtener_hash(texto):
    """
    Genera SHA-256 del contenido normalizado.
    """

    return hashlib.sha256(
        texto.encode("utf-8")
    ).hexdigest()


# ============================================================
# ANÁLISIS DE CATÁLOGOS
# ============================================================

registros = []

print("=" * 100)
print("ANÁLISIS DE CATÁLOGOS SCVS 2015-2025")
print("=" * 100)


for anio in ANIOS:

    zip_path = (
        SCVS_ROOT
        / str(anio)
        / f"estadosFinancieros_{anio}.zip"
    )

    with ZipFile(zip_path, "r") as z:

        catalogos = sorted(
            nombre
            for nombre in z.namelist()
            if "catalogo" in nombre.lower()
            and not nombre.endswith("/")
        )

        for nombre in catalogos:

            contenido_bytes = z.read(nombre)

            texto, codificacion = decodificar_contenido(
                contenido_bytes
            )

            texto_normalizado = normalizar_texto(
                texto
            )

            hash_catalogo = obtener_hash(
                texto_normalizado
            )

            lineas = texto_normalizado.split("\n")

            registros.append(
                {
                    "anio": anio,
                    "archivo": nombre,
                    "hash": hash_catalogo,
                    "lineas": len(lineas),
                    "codificacion": codificacion,
                }
            )


# ============================================================
# AGRUPACIÓN DE CATÁLOGOS IDÉNTICOS
# ============================================================

grupos = {}

for registro in registros:

    hash_catalogo = registro["hash"]

    if hash_catalogo not in grupos:
        grupos[hash_catalogo] = []

    grupos[hash_catalogo].append(registro)


# ============================================================
# RESULTADOS
# ============================================================

print(
    f"\nCatálogos analizados: {len(registros)}"
)

print(
    f"Catálogos estructuralmente distintos: {len(grupos)}"
)

print("\n" + "=" * 100)
print("GRUPOS DE CATÁLOGOS IDÉNTICOS")
print("=" * 100)


for numero, (hash_catalogo, elementos) in enumerate(
    sorted(
        grupos.items(),
        key=lambda x: (
            min(item["anio"] for item in x[1]),
            len(x[1])
        )
    ),
    start=1
):

    print(f"\nPLAN {numero}")
    print("-" * 100)

    print(
        f"Hash: {hash_catalogo[:16]}..."
    )

    print(
        f"Número de líneas del catálogo: "
        f"{elementos[0]['lineas']}"
    )

    print(
        f"Cantidad de archivos que utilizan este plan: "
        f"{len(elementos)}"
    )

    print("Aparece en:")

    for item in elementos:

        print(
            f"  {item['anio']} | "
            f"{item['archivo']} | "
            f"{item['codificacion']}"
        )


# ============================================================
# RESUMEN POR AÑO
# ============================================================

print("\n" + "=" * 100)
print("RESUMEN POR AÑO")
print("=" * 100)

for anio in ANIOS:

    catalogos_anio = [
        r
        for r in registros
        if r["anio"] == anio
    ]

    planes_anio = {
        r["hash"]
        for r in catalogos_anio
    }

    print(
        f"{anio}: "
        f"{len(catalogos_anio)} catálogos | "
        f"{len(planes_anio)} estructuras distintas"
    )


print("\nAnálisis finalizado correctamente.")