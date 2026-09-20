from pathlib import Path
from zipfile import ZipFile
import csv
import hashlib
import io


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

def decodificar(contenido):
    """
    Intenta decodificar archivos SCVS con las codificaciones
    encontradas en las fuentes históricas.
    """

    for codificacion in [
        "utf-8-sig",
        "utf-8",
        "latin-1",
        "cp1252",
    ]:
        try:
            return contenido.decode(codificacion), codificacion
        except UnicodeDecodeError:
            continue

    raise ValueError("No fue posible decodificar el archivo.")


def normalizar_catalogo(texto):
    """
    Normaliza el catálogo para identificar planes iguales
    utilizados en diferentes años.
    """

    lineas = [
        linea.strip()
        for linea in texto.replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
        if linea.strip()
    ]

    return "\n".join(lineas)


def hash_catalogo(texto):
    return hashlib.sha256(
        texto.encode("utf-8")
    ).hexdigest()


def detectar_delimitador(texto):
    """
    Detecta delimitador del TXT.
    """

    primera_linea = texto.splitlines()[0]

    candidatos = ["\t", ";", "|", ","]

    conteos = {
        delimitador: primera_linea.count(delimitador)
        for delimitador in candidatos
    }

    return max(
        conteos,
        key=conteos.get
    )


# ============================================================
# PRIMERA ETAPA:
# IDENTIFICAR LOS 8 PLANES
# ============================================================

hashes_ordenados = []

catalogos = []

for anio in ANIOS:

    zip_path = (
        SCVS_ROOT
        / str(anio)
        / f"estadosFinancieros_{anio}.zip"
    )

    with ZipFile(zip_path, "r") as z:

        nombres_catalogos = sorted(
            nombre
            for nombre in z.namelist()
            if "catalogo" in nombre.lower()
            and not nombre.endswith("/")
        )

        for nombre in nombres_catalogos:

            contenido = z.read(nombre)

            texto, _ = decodificar(contenido)

            texto = normalizar_catalogo(texto)

            h = hash_catalogo(texto)

            catalogos.append(
                {
                    "anio": anio,
                    "archivo": nombre,
                    "hash": h,
                }
            )

            if h not in hashes_ordenados:
                hashes_ordenados.append(h)


# Asignación PLAN 1, PLAN 2, etc.
mapa_plan = {
    h: numero
    for numero, h in enumerate(
        hashes_ordenados,
        start=1
    )
}


# ============================================================
# SEGUNDA ETAPA:
# ANALIZAR LOS BALANCES ASOCIADOS
# ============================================================

resultados = []

print("=" * 105)
print("DISTRIBUCIÓN DE EMPRESAS POR PLAN CONTABLE SCVS")
print("=" * 105)


for anio in ANIOS:

    zip_path = (
        SCVS_ROOT
        / str(anio)
        / f"estadosFinancieros_{anio}.zip"
    )

    with ZipFile(zip_path, "r") as z:

        nombres = z.namelist()

        balances = sorted(
            nombre
            for nombre in nombres
            if "balances" in nombre.lower()
            and not nombre.endswith("/")
        )

        catalogos_anio = {
            item["archivo"]: item["hash"]
            for item in catalogos
            if item["anio"] == anio
        }

        print("\n" + "=" * 105)
        print(f"AÑO {anio}")
        print("=" * 105)

        total_ruc_anio = set()

        for balance in balances:

            # Ejemplo:
            # balances_2015_3.txt
            # -> catalogo_2015_3.txt

            catalogo = balance.replace(
                "balances_",
                "catalogo_"
            )

            if catalogo not in catalogos_anio:

                print(
                    f"ADVERTENCIA: no existe catálogo "
                    f"para {balance}"
                )

                continue

            h = catalogos_anio[catalogo]

            plan = mapa_plan[h]

            contenido = z.read(balance)

            texto, codificacion = decodificar(
                contenido
            )

            delimitador = detectar_delimitador(
                texto
            )

            lector = csv.DictReader(
                io.StringIO(texto),
                delimiter=delimitador
            )

            rucs = set()

            filas = 0

            columnas = lector.fieldnames or []

            columna_ruc = None

            for columna in columnas:

                if columna.strip().upper() == "RUC":
                    columna_ruc = columna
                    break

            if columna_ruc is None:

                print(
                    f"ERROR: {balance} no contiene "
                    "una columna RUC reconocible."
                )

                continue

            for fila in lector:

                filas += 1

                ruc = (
                    fila.get(columna_ruc, "")
                    or ""
                ).strip()

                if (
                    len(ruc) == 13
                    and ruc.isdigit()
                ):
                    rucs.add(ruc)

            total_ruc_anio.update(rucs)

            resultados.append(
                {
                    "anio": anio,
                    "balance": balance,
                    "catalogo": catalogo,
                    "plan": plan,
                    "filas": filas,
                    "ruc_unicos": len(rucs),
                    "columnas": len(columnas),
                    "codificacion": codificacion,
                }
            )

            print(
                f"PLAN {plan} | "
                f"{balance:<25} | "
                f"RUC: {len(rucs):>7,} | "
                f"Filas: {filas:>7,} | "
                f"Columnas: {len(columnas):>4}"
            )

        print(
            f"\nTOTAL RUC ÚNICOS {anio}: "
            f"{len(total_ruc_anio):,}"
        )


# ============================================================
# RESUMEN GENERAL POR PLAN
# ============================================================

print("\n" + "=" * 105)
print("RESUMEN GENERAL POR PLAN")
print("=" * 105)

for plan in sorted(
    {r["plan"] for r in resultados}
):

    registros_plan = [
        r
        for r in resultados
        if r["plan"] == plan
    ]

    total = sum(
        r["ruc_unicos"]
        for r in registros_plan
    )

    anios = sorted(
        {
            r["anio"]
            for r in registros_plan
        }
    )

    print(
        f"PLAN {plan}: "
        f"{total:,} observaciones empresa-año "
        f"| años: {anios}"
    )


# ============================================================
# DISTRIBUCIÓN POR AÑO Y PLAN
# ============================================================

print("\n" + "=" * 105)
print("DISTRIBUCIÓN POR AÑO Y PLAN")
print("=" * 105)

for anio in ANIOS:

    registros_anio = [
        r
        for r in resultados
        if r["anio"] == anio
    ]

    total = sum(
        r["ruc_unicos"]
        for r in registros_anio
    )

    print(f"\n{anio} | Total: {total:,}")

    for r in sorted(
        registros_anio,
        key=lambda x: x["plan"]
    ):

        porcentaje = (
            100 * r["ruc_unicos"] / total
            if total
            else 0
        )

        print(
            f"  PLAN {r['plan']}: "
            f"{r['ruc_unicos']:>7,} "
            f"({porcentaje:6.2f}%)"
        )


print("\nAnálisis finalizado correctamente.")