from pathlib import Path
from zipfile import ZipFile
import csv
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

ANIOS = range(2015, 2024)


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


def detectar_delimitador(texto):
    primera = texto.splitlines()[0]

    candidatos = ["\t", ";", "|", ","]

    return max(
        candidatos,
        key=lambda d: primera.count(d)
    )


def contar_lineas_catalogo(texto):
    return len(
        [
            x.strip()
            for x in texto
            .replace("\r\n", "\n")
            .replace("\r", "\n")
            .split("\n")
            if x.strip()
        ]
    )


# ============================================================
# INSPECCIÓN
# ============================================================

muestras_por_plan = {}

for anio in ANIOS:

    zip_path = (
        SCVS_ROOT
        / str(anio)
        / f"estadosFinancieros_{anio}.zip"
    )

    with ZipFile(zip_path, "r") as z:

        balances = sorted(
            x
            for x in z.namelist()
            if "balances" in x.lower()
            and not x.endswith("/")
        )

        for balance in balances:

            catalogo = balance.replace(
                "balances_",
                "catalogo_"
            )

            texto_catalogo = decodificar(
                z.read(catalogo)
            )

            numero_cuentas = contar_lineas_catalogo(
                texto_catalogo
            )

            plan = f"PLAN_{numero_cuentas}"

            texto_balance = decodificar(
                z.read(balance)
            )

            delimitador = detectar_delimitador(
                texto_balance
            )

            lector = csv.DictReader(
                io.StringIO(texto_balance),
                delimiter=delimitador
            )

            columnas = lector.fieldnames or []

            if plan not in muestras_por_plan:
                muestras_por_plan[plan] = {
                    "columnas": columnas,
                    "filas": [],
                }

            for fila in lector:

                if len(
                    muestras_por_plan[plan]["filas"]
                ) >= 10:
                    break

                muestra = {}

                for campo in [
                    "AÑO",
                    "ANIO",
                    "EXPEDIENTE",
                    "RUC",
                    "NOMBRE",
                    "RAMA_ACTIVIDAD",
                    "DESCRIPCION_RAMA",
                    "CIIU",
                ]:

                    if campo in fila:
                        muestra[campo] = fila[campo]

                muestras_por_plan[plan][
                    "filas"
                ].append(muestra)


# ============================================================
# RESULTADOS
# ============================================================

for plan in sorted(muestras_por_plan):

    print("\n" + "=" * 100)
    print(plan)
    print("=" * 100)

    print(
        "Número de columnas:",
        len(muestras_por_plan[plan]["columnas"])
    )

    print("\nPrimeras columnas:")

    print(
        muestras_por_plan[plan]["columnas"][:20]
    )

    print("\nEjemplos de empresas:")

    for fila in muestras_por_plan[plan]["filas"]:

        print(fila)