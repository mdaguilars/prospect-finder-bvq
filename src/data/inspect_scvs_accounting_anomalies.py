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


# PLAN_807 aparece como catalogo_2015_3
# PLAN_622 es catalogo_2015_6 y se mantiene hasta años recientes.

ARCHIVOS = [
    (
        2015,
        "catalogo_2015_3.txt",
        "PLAN_807"
    ),
    (
        2015,
        "catalogo_2015_6.txt",
        "PLAN_622"
    ),
]


# ============================================================
# FUNCIONES
# ============================================================

def decodificar(contenido):

    for encoding in [
        "utf-8-sig",
        "utf-8",
        "latin-1",
        "cp1252",
    ]:

        try:
            return contenido.decode(
                encoding
            )

        except UnicodeDecodeError:
            continue

    raise ValueError(
        "No fue posible decodificar."
    )


def separar_linea(linea):

    partes = linea.strip().split(
        None,
        1
    )

    if len(partes) != 2:
        return None, None

    return (
        partes[0].strip(),
        partes[1].strip()
    )


# ============================================================
# INSPECCIÓN
# ============================================================

for anio, archivo, plan in ARCHIVOS:

    zip_path = (
        SCVS_ROOT
        / str(anio)
        / f"estadosFinancieros_{anio}.zip"
    )

    with ZipFile(
        zip_path,
        "r"
    ) as z:

        texto = decodificar(
            z.read(archivo)
        )

    lineas = [
        linea.strip()
        for linea in texto
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
        if linea.strip()
    ]

    print("\n" + "=" * 110)
    print(
        f"{plan} | {archivo}"
    )
    print("=" * 110)

    registros = []

    for linea in lineas:

        codigo, descripcion = (
            separar_linea(linea)
        )

        if codigo is None:
            continue

        registros.append(
            (
                codigo,
                descripcion
            )
        )

    # ========================================================
    # CUENTAS RELACIONADAS CON ACTIVOS
    # ========================================================

    print(
        "\nCUENTAS CON 'TOTAL' Y 'ACTIV':"
    )

    for codigo, descripcion in registros:

        texto_busqueda = (
            descripcion.upper()
        )

        if (
            "TOTAL" in texto_busqueda
            and "ACTIV" in texto_busqueda
        ):

            print(
                f"{codigo:<15} "
                f"{descripcion}"
            )

    # ========================================================
    # CUENTAS RELACIONADAS CON PASIVOS
    # ========================================================

    print(
        "\nCUENTAS CON 'TOTAL' Y 'PASIV':"
    )

    for codigo, descripcion in registros:

        texto_busqueda = (
            descripcion.upper()
        )

        if (
            "TOTAL" in texto_busqueda
            and "PASIV" in texto_busqueda
        ):

            print(
                f"{codigo:<15} "
                f"{descripcion}"
            )

    # ========================================================
    # CUENTAS PRINCIPALES 2xx
    # ========================================================

    print(
        "\nCUENTAS 2xx DE NIVEL SUPERIOR:"
    )

    for codigo, descripcion in registros:

        if (
            codigo.isdigit()
            and codigo.startswith("2")
            and len(codigo) <= 4
        ):

            print(
                f"{codigo:<15} "
                f"{descripcion}"
            )

    # ========================================================
    # CUENTAS ENTRE 350 Y 699
    # ========================================================

    print(
        "\nTOTALES ENTRE CÓDIGOS 350 Y 699:"
    )

    for codigo, descripcion in registros:

        if not codigo.isdigit():
            continue

        numero = int(codigo)

        if (
            350 <= numero <= 699
            and "TOTAL"
            in descripcion.upper()
        ):

            print(
                f"{codigo:<15} "
                f"{descripcion}"
            )