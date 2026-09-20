from pathlib import Path
import csv
import hashlib

import pandas as pd


# ============================================================
# 1. CONFIGURACIÓN GENERAL
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCVS_EMISORES_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "scvs"
    / "mercado_valores"
    / "listado_entes_65001_1789908466941.xlsx"
)

BALANCE_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "bvq"
    / "dwh"
    / "V_BALANCE_LINEAS_RESUMEN_202609172129.csv"
)

RESULTADOS_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "bvq"
    / "dwh"
    / "V_RESULTADOS_LINEAS_RESUMEN_202609171929.csv"
)


# Años utilizados para el MVP preliminar.
ANIOS_MVP = {"2022", "2023"}


# ============================================================
# 2. VARIABLES FINANCIERAS INICIALES DEL MVP
# ============================================================

LINEAS_BALANCE_MVP = {
    "TOTAL ACTIVOS",
    "Activos Corrientes",
    "Pasivos Corrientes",
    "Total Pasivo No Corriente",
    "Total Patrimonio",
    "Efectivo y equivalentes",
    "Inventarios",
    "Cuentas x Cobrar-Cartera",
    "Deuda Bancaria C.P.",
    "Deuda Bancaria L.P.",
    "Proveedores",
    "Capital Social",
    "Resultados Ejercicicio",
}

LINEAS_RESULTADOS_MVP = {
    "Ingreso por Actividad",
    "Costo de Ventas",
    "Gastos Administrativos",
    "Gastos Financieros",
    "Gastos de Venta",
    "UTILIDAD BRUTA",
    "UTILIDAD OPERATIVA",
    "UTILIDAD NETA",
}


# ============================================================
# 3. CARGA DEL HISTÓRICO DE EMISORES SCVS
# ============================================================

print("=" * 70)
print("CARGA DEL HISTÓRICO DE EMISORES SCVS")
print("=" * 70)

df_emisores = pd.read_excel(
    SCVS_EMISORES_PATH,
    header=4
)

print(f"Filas originales: {len(df_emisores):,}")


# ============================================================
# 4. LIMPIEZA DEL IDENTIFICADOR SCVS
# ============================================================

df_emisores["RUC"] = (
    df_emisores["IDENTIFICACIÓN"]
    .astype("string")
    .str.strip()
)

# Para el MVP se consideran únicamente RUC de 13 dígitos.
ruc_valido = df_emisores["RUC"].str.fullmatch(
    r"\d{13}",
    na=False
)

df_emisores = df_emisores.loc[ruc_valido].copy()

print(f"Registros con RUC válido: {len(df_emisores):,}")
print(f"RUC únicos: {df_emisores['RUC'].nunique():,}")


# ============================================================
# 5. NORMALIZACIÓN DE FECHA DE INSCRIPCIÓN
# ============================================================

df_emisores["FECHA_INSCRIPCION"] = pd.to_datetime(
    df_emisores["FECHA INSCRIPCIÓN"],
    errors="coerce"
)

print(
    "Registros sin fecha de inscripción:",
    df_emisores["FECHA_INSCRIPCION"].isna().sum()
)


# ============================================================
# 6. PRIMERA INSCRIPCIÓN HISTÓRICA POR RUC
# ============================================================

df_primera_inscripcion = (
    df_emisores
    .groupby("RUC", as_index=False)
    .agg(
        FECHA_PRIMERA_INSCRIPCION=(
            "FECHA_INSCRIPCION",
            "min"
        )
    )
)

print(
    f"Empresas históricas identificadas: "
    f"{len(df_primera_inscripcion):,}"
)

print("\nPrimeros registros:")

print(
    df_primera_inscripcion
    .sort_values("FECHA_PRIMERA_INSCRIPCION")
    .head(10)
    .to_string(index=False)
)

print("\nPreparación SCVS completada correctamente.")


# ============================================================
# 7. FUNCIÓN PARA GENERAR FIRMA DE FILA
# ============================================================

def generar_firma_fila(fila, columnas):
    """
    Genera una firma SHA-256 a partir del contenido de todas
    las columnas de una fila.

    Se utiliza para verificar que dos registros con la misma
    clave RUC + ANIO + LINEA sean realmente duplicados.

    Se eliminan únicamente espacios exteriores de cada campo.
    """

    contenido = "\x1f".join(
        fila.get(columna, "").strip()
        for columna in columnas
    )

    return hashlib.sha256(
        contenido.encode("utf-8")
    ).digest()


# ============================================================
# 8. FUNCIÓN PARA EXTRAER VARIABLES FINANCIERAS
# ============================================================

def extraer_variables_financieras(
    archivo,
    lineas_seleccionadas,
    prefijo
):
    """
    Recorre un CSV grande en modo streaming.

    Conserva únicamente:
    - años definidos para el MVP;
    - RUC válidos de 13 dígitos;
    - líneas financieras seleccionadas.

    La unidad resultante es:
        RUC + ANIO

    Para cada combinación:
        RUC + ANIO + LINEA

    se valida que los registros repetidos sean duplicados
    exactos considerando todas las columnas del archivo.

    Si aparece una misma clave con contenido diferente,
    el proceso se detiene para evitar consolidar datos
    inconsistentes de manera silenciosa.
    """

    registros = {}

    firmas_por_clave = {}

    duplicados_exactos = 0
    conflictos = 0

    lineas_encontradas = set()

    print("\n" + "=" * 70)
    print(f"PROCESANDO {prefijo}")
    print("=" * 70)

    with open(
        archivo,
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        lector = csv.DictReader(f)

        columnas = lector.fieldnames

        if columnas is None:
            raise ValueError(
                f"No fue posible identificar las columnas de {archivo}"
            )

        for fila in lector:

            anio = fila.get("ANIO", "").strip()
            ruc = fila.get("RUC", "").strip()
            linea = fila.get("LINEA", "").strip()

            # ------------------------------------------------
            # Solo años definidos para el MVP
            # ------------------------------------------------

            if anio not in ANIOS_MVP:
                continue

            # ------------------------------------------------
            # Solo RUC válidos
            # ------------------------------------------------

            if not (
                len(ruc) == 13
                and ruc.isdigit()
            ):
                continue

            # ------------------------------------------------
            # Solo variables seleccionadas
            # ------------------------------------------------

            if linea not in lineas_seleccionadas:
                continue

            lineas_encontradas.add(linea)

            clave_empresa = (
                ruc,
                anio
            )

            clave_linea = (
                ruc,
                anio,
                linea
            )

            # ------------------------------------------------
            # VALIDACIÓN DE DUPLICADOS
            # ------------------------------------------------

            firma_fila = generar_firma_fila(
                fila,
                columnas
            )

            if clave_linea in firmas_por_clave:

                firma_anterior = (
                    firmas_por_clave[clave_linea]
                )

                if firma_anterior == firma_fila:

                    duplicados_exactos += 1

                    # El duplicado exacto no aporta
                    # nueva información.
                    continue

                conflictos += 1

                raise ValueError(
                    "\nCONFLICTO DE DATOS DETECTADO\n"
                    f"RUC   : {ruc}\n"
                    f"ANIO  : {anio}\n"
                    f"LINEA : {linea}\n\n"
                    "Existen dos registros con la misma "
                    "clave RUC + ANIO + LINEA, pero con "
                    "contenido diferente."
                )

            firmas_por_clave[clave_linea] = (
                firma_fila
            )

            # ------------------------------------------------
            # CREACIÓN DEL REGISTRO EMPRESA-AÑO
            # ------------------------------------------------

            if clave_empresa not in registros:

                registros[clave_empresa] = {
                    "RUC": ruc,
                    "ANIO": int(anio),

                    "EMISOR": (
                        fila
                        .get("EMISOR", "")
                        .strip()
                    ),

                    "CIIU": (
                        fila
                        .get("CIIU", "")
                        .strip()
                    ),

                    "RAMA_ACTIVIDAD": (
                        fila
                        .get(
                            "RAMA_ACTIVIDAD",
                            ""
                        )
                        .strip()
                    ),

                    "DESCRIPCION_RAMA": (
                        fila
                        .get(
                            "DESCRIPCION_RAMA",
                            ""
                        )
                        .strip()
                    ),
                }

            # ------------------------------------------------
            # CONVERSIÓN DEL VALOR FINANCIERO
            # ------------------------------------------------

            valor_texto = (
                fila
                .get("VALOR", "")
                .strip()
            )

            try:

                valor = (
                    float(valor_texto)
                    if valor_texto
                    else None
                )

            except ValueError:

                valor = None

            nombre_variable = (
                f"{prefijo}_{linea}"
            )

            registros[
                clave_empresa
            ][nombre_variable] = valor

    # ========================================================
    # CONVERSIÓN A DATAFRAME
    # ========================================================

    df = pd.DataFrame(
        registros.values()
    )

    print(
        f"Empresas-año obtenidas: "
        f"{len(df):,}"
    )

    print(
        f"Variables esperadas: "
        f"{len(lineas_seleccionadas)}"
    )

    print(
        f"Variables encontradas: "
        f"{len(lineas_encontradas)}"
    )

    print(
        f"Duplicados exactos descartados: "
        f"{duplicados_exactos:,}"
    )

    print(
        f"Conflictos detectados: "
        f"{conflictos:,}"
    )

    faltantes = (
        lineas_seleccionadas
        - lineas_encontradas
    )

    if faltantes:

        print("\nVariables NO encontradas:")

        for linea in sorted(faltantes):

            print(
                f" - {linea}"
            )

    else:

        print(
            "Todas las variables seleccionadas "
            "fueron encontradas."
        )

    return df


# ============================================================
# 9. EXTRACCIÓN DE BALANCE
# ============================================================

df_balance = extraer_variables_financieras(
    BALANCE_PATH,
    LINEAS_BALANCE_MVP,
    "BAL"
)


# ============================================================
# 10. EXTRACCIÓN DE RESULTADOS
# ============================================================

df_resultados = extraer_variables_financieras(
    RESULTADOS_PATH,
    LINEAS_RESULTADOS_MVP,
    "RES"
)


# ============================================================
# 11. RESUMEN DE EXTRACCIÓN
# ============================================================

print("\n" + "=" * 70)
print("RESUMEN DE EXTRACCIÓN")
print("=" * 70)

print("\nBalance:")

print(
    df_balance
    .groupby("ANIO")["RUC"]
    .nunique()
)

print("\nResultados:")

print(
    df_resultados
    .groupby("ANIO")["RUC"]
    .nunique()
)

print("\nProceso completado correctamente.")