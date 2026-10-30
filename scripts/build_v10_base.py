import pandas as pd
import numpy as np
from pathlib import Path
import hashlib

# ============================================================
# CONSTRUCCION REPRODUCIBLE DE LA BASE INTEGRADA V10
# ============================================================

RUTA_OLD = Path(
    r".\data\interim\scvs_financials_harmonized_2015_2023.csv.gz"
)

RUTA_BI = Path(
    r".\data\raw\scvs\ranking\bi_ranking.csv"
)

RUTA_COMPANIAS = Path(
    r".\data\raw\scvs\catalogos\bi_compania.csv"
)

RUTA_TARGET = Path(
    r".\data\raw\scvs\mercado_valores\listado_entes_65001_1789908466941.xlsx"
)

RUTA_SALIDA = Path(
    r".\data\processed\v10_base_integrated_2012_2023.csv.gz"
)

RUTA_REPORTE = Path(
    r".\salida_paso179.txt"
)


# ============================================================
# CONSTANTES DEL UNIVERSO CONGELADO
# ============================================================

ESPERADO_UNION_TOTAL = 1035294
ESPERADO_SIN_RUC = 535
ESPERADO_ELEGIBLES = 1030671
ESPERADO_POSITIVOS = 568
ESPERADO_RUC_POSITIVOS = 310
ESPERADO_TARGET_RUC = 619


# ============================================================
# FUNCIONES
# ============================================================

def normalizar_ruc_historico(serie):

    s = (
        serie.astype("string")
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .str.replace(r"\D", "", regex=True)
    )

    largo = s.str.len()

    s = s.where(
        largo.isin([12, 13])
    )

    return s.str.zfill(13)


def sha256_archivo(ruta):

    h = hashlib.sha256()

    with open(ruta, "rb") as f:

        for bloque in iter(
            lambda: f.read(1024 * 1024),
            b""
        ):
            h.update(bloque)

    return h.hexdigest()


# ============================================================
# 1. HISTORICO 2015-2023
# ============================================================

old = pd.read_csv(
    RUTA_OLD,
    usecols=[
        "ANIO",
        "EXPEDIENTE",
        "RUC",
        "NOMBRE",
        "PLAN_CONTABLE",
        "ACTIVO_TOTAL",
        "PATRIMONIO",
        "UTILIDAD_NETA"
    ],
    dtype={
        "RUC": "string"
    }
)

old["ANIO"] = pd.to_numeric(
    old["ANIO"],
    errors="coerce"
).astype("Int64")

old["EXPEDIENTE_KEY"] = pd.to_numeric(
    old["EXPEDIENTE"],
    errors="coerce"
).astype("Int64")

old = old[
    old["ANIO"].between(2015, 2023)
    & old["EXPEDIENTE_KEY"].notna()
].copy()

old = old.drop_duplicates(
    ["ANIO", "EXPEDIENTE_KEY"]
)

old["ruc_old_fila"] = normalizar_ruc_historico(
    old["RUC"]
)

old = old.rename(
    columns={

        "NOMBRE": "nombre_old",
        "PLAN_CONTABLE": "plan_contable_old",
        "ACTIVO_TOTAL": "activos_old",
        "PATRIMONIO": "patrimonio_old",
        "UTILIDAD_NETA": "utilidad_neta_old_auditoria"
    }
)

old["fuente_old"] = True

old = old[
    [
        "ANIO",
        "EXPEDIENTE_KEY",
        "ruc_old_fila",
        "nombre_old",
        "plan_contable_old",
        "activos_old",
        "patrimonio_old",
        "utilidad_neta_old_auditoria",
        "fuente_old"
    ]
]


# ============================================================
# 2. MAPA HISTORICO GLOBAL EXPEDIENTE -> RUC
# ============================================================

old_ruc_valid = old[
    old["ruc_old_fila"].notna()
].copy()

conteo_ruc_hist = (
    old_ruc_valid
    .groupby("EXPEDIENTE_KEY")["ruc_old_fila"]
    .nunique()
    .rename("n_ruc_hist")
    .reset_index()
)

mapa_ruc_hist = (
    old_ruc_valid
    .groupby("EXPEDIENTE_KEY")
    .agg(
        ruc_hist_primero=(
            "ruc_old_fila",
            "first"
        )
    )
    .reset_index()
    .merge(
        conteo_ruc_hist,
        on="EXPEDIENTE_KEY",
        how="left"
    )
)

mapa_ruc_hist["ruc_hist_unico"] = np.where(
    mapa_ruc_hist["n_ruc_hist"] == 1,
    mapa_ruc_hist["ruc_hist_primero"],
    pd.NA
)


# ============================================================
# 3. BI_RANKING 2012-2023
# ============================================================

columnas_bi = [
    "anio",
    "expediente",

    "ingresos_ventas",
    "activos",
    "patrimonio",
    "utilidad_an_imp",
    "impuesto_renta",
    "n_empleados",
    "ingresos_totales",
    "utilidad_ejercicio",
    "utilidad_neta",

    "cod_segmento",
    "ciiu_n1",
    "ciiu_n6",

    "liquidez_corriente",
    "prueba_acida",
    "end_activo",
    "end_patrimonial",
    "end_activo_fijo",
    "end_corto_plazo",
    "end_largo_plazo",
    "cobertura_interes",
    "apalancamiento",
    "apalancamiento_financiero",
    "end_patrimonial_ct",
    "end_patrimonial_nct",
    "apalancamiento_c_l_plazo",
    "rot_cartera",
    "rot_activo_fijo",
    "rot_ventas",
    "per_med_cobranza",
    "per_med_pago",
    "impac_gasto_a_v",
    "impac_carga_finan",
    "rent_neta_activo",
    "margen_bruto",
    "margen_operacional",
    "rent_neta_ventas",
    "rent_ope_patrimonio",
    "rent_ope_activo",
    "roe",
    "roa",
    "fortaleza_patrimonial",

    "gastos_financieros",
    "gastos_admin_ventas",
    "depreciaciones",
    "amortizaciones",
    "costos_ventas_prod",
    "deuda_total",
    "deuda_total_c_plazo",
    "total_gastos"
]

bi = pd.read_csv(
    RUTA_BI,
    usecols=columnas_bi,
    dtype={
        "ciiu_n1": "string",
        "ciiu_n6": "string"
    }
)

bi["ANIO"] = pd.to_numeric(
    bi["anio"],
    errors="coerce"
).astype("Int64")

bi["EXPEDIENTE_KEY"] = pd.to_numeric(
    bi["expediente"],
    errors="coerce"
).astype("Int64")

bi = bi[
    bi["ANIO"].between(2012, 2023)
    & bi["EXPEDIENTE_KEY"].notna()
].copy()

bi = bi.drop_duplicates(
    ["ANIO", "EXPEDIENTE_KEY"]
)

bi = bi.drop(
    columns=[
        "anio",
        "expediente"
    ]
)

renombrar_bi = {
    c: f"bi_{c}"
    for c in bi.columns
    if c not in [
        "ANIO",
        "EXPEDIENTE_KEY"
    ]
}

bi = bi.rename(
    columns=renombrar_bi
)

bi["fuente_bi"] = True


# ============================================================
# 4. UNION DE FUENTES
# ============================================================

u = bi.merge(
    old,
    on=[
        "ANIO",
        "EXPEDIENTE_KEY"
    ],
    how="outer"
)

u["fuente_bi"] = (
    u["fuente_bi"]
    .fillna(False)
    .astype(bool)
)

u["fuente_old"] = (
    u["fuente_old"]
    .fillna(False)
    .astype(bool)
)

u["tipo_fuente"] = np.select(
    [
        u["fuente_bi"] & u["fuente_old"],
        u["fuente_bi"] & ~u["fuente_old"],
        ~u["fuente_bi"] & u["fuente_old"]
    ],
    [
        "AMBAS",
        "SOLO_BI",
        "SOLO_HISTORICO"
    ],
    default="ERROR"
)

assert len(u) == ESPERADO_UNION_TOTAL, (
    f"ERROR: unión={len(u)}; "
    f"esperado={ESPERADO_UNION_TOTAL}"
)

assert (
    u.duplicated(
        ["ANIO", "EXPEDIENTE_KEY"]
    ).sum()
    == 0
), "ERROR: existen duplicados empresa-año."


# ============================================================
# 5. CATALOGO DE COMPAÑIAS
# ============================================================

companias = pd.read_csv(
    RUTA_COMPANIAS,
    dtype={
        "expediente": "string",
        "ruc": "string"
    }
)

companias["EXPEDIENTE_KEY"] = pd.to_numeric(
    companias["expediente"],
    errors="coerce"
).astype("Int64")

companias["ruc_catalogo"] = (
    companias["ruc"]
    .astype("string")
    .str.strip()
)

companias["ruc_catalogo"] = (
    companias["ruc_catalogo"]
    .where(
        companias["ruc_catalogo"]
        .str.fullmatch(
            r"\d{13}",
            na=False
        )
    )
)

companias = companias.rename(
    columns={
        "nombre": "nombre_catalogo",
        "tipo": "tipo_compania",
        "pro_codigo": "codigo_provincia",
        "provincia": "provincia"
    }
)

companias = companias[
    companias["EXPEDIENTE_KEY"].notna()
][
    [
        "EXPEDIENTE_KEY",
        "ruc_catalogo",
        "nombre_catalogo",
        "tipo_compania",
        "codigo_provincia",
        "provincia"
    ]
].drop_duplicates(
    "EXPEDIENTE_KEY"
)

u = u.merge(
    companias,
    on="EXPEDIENTE_KEY",
    how="left"
)

u = u.merge(
    mapa_ruc_hist[
        [
            "EXPEDIENTE_KEY",
            "ruc_hist_unico",
            "n_ruc_hist"
        ]
    ],
    on="EXPEDIENTE_KEY",
    how="left"
)


# ============================================================
# 6. IDENTIDAD FINAL
# ============================================================

u["RUC"] = u["ruc_catalogo"]

mask_ruc_hist_exp = (
    u["RUC"].isna()
    & u["ruc_hist_unico"].notna()
)

u.loc[
    mask_ruc_hist_exp,
    "RUC"
] = u.loc[
    mask_ruc_hist_exp,
    "ruc_hist_unico"
]

mask_ruc_hist_fila = (
    u["RUC"].isna()
    & u["ruc_old_fila"].notna()
)

u.loc[
    mask_ruc_hist_fila,
    "RUC"
] = u.loc[
    mask_ruc_hist_fila,
    "ruc_old_fila"
]

u["fuente_ruc"] = np.select(
    [
        u["ruc_catalogo"].notna(),

        u["ruc_catalogo"].isna()
        & u["ruc_hist_unico"].notna(),

        u["ruc_catalogo"].isna()
        & u["ruc_hist_unico"].isna()
        & u["ruc_old_fila"].notna()
    ],
    [
        "BI_COMPANIA",
        "HISTORICO_EXPEDIENTE",
        "HISTORICO_FILA"
    ],
    default="SIN_RUC"
)

u["ruc_difiere"] = (
    u["ruc_catalogo"].notna()
    & u["ruc_old_fila"].notna()
    & (
        u["ruc_catalogo"]
        != u["ruc_old_fila"]
    )
)

u["NOMBRE"] = u["nombre_catalogo"]

mask_nombre = (
    u["NOMBRE"].isna()
    & u["nombre_old"].notna()
)

u.loc[
    mask_nombre,
    "NOMBRE"
] = u.loc[
    mask_nombre,
    "nombre_old"
]


# ============================================================
# 7. EXCLUIR IDENTIDAD NO VERIFICABLE
# ============================================================

sin_ruc = u[
    u["RUC"].isna()
].copy()

assert len(sin_ruc) == ESPERADO_SIN_RUC, (
    f"ERROR: sin RUC={len(sin_ruc)}; "
    f"esperado={ESPERADO_SIN_RUC}"
)

base = u[
    u["RUC"].notna()
].copy()


# ============================================================
# 8. TARGET OFICIAL
# ============================================================

target = pd.read_excel(
    RUTA_TARGET,
    sheet_name="ListadoEntes",
    header=4,
    dtype={
        "IDENTIFICACIÓN": "string"
    }
)

target.columns = [
    str(c).strip()
    for c in target.columns
]

target["RUC"] = (
    target["IDENTIFICACIÓN"]
    .astype("string")
    .str.strip()
)

target = target[
    target["RUC"].str.fullmatch(
        r"\d{13}",
        na=False
    )
].copy()

target["fecha_primera_inscripcion"] = pd.to_datetime(
    target["FECHA INSCRIPCIÓN"],
    errors="coerce"
)

target = target[
    target["fecha_primera_inscripcion"].notna()
].copy()

target = (
    target.sort_values(
        [
            "RUC",
            "fecha_primera_inscripcion"
        ]
    )
    .drop_duplicates(
        "RUC",
        keep="first"
    )
    [
        [
            "RUC",
            "fecha_primera_inscripcion"
        ]
    ]
)

assert target["RUC"].nunique() == ESPERADO_TARGET_RUC, (
    f"ERROR: target RUC={target['RUC'].nunique()}; "
    f"esperado={ESPERADO_TARGET_RUC}"
)


# ============================================================
# 9. ETIQUETADO TEMPORAL
# ============================================================

base = base.merge(
    target,
    on="RUC",
    how="left"
)

base["fecha_decision"] = pd.to_datetime(
    (
        base["ANIO"] + 1
    )
    .astype("Int64")
    .astype("string")
    + "-05-01",
    errors="coerce"
)

base["fin_ventana_24m"] = (
    base["fecha_decision"]
    + pd.DateOffset(years=2)
    - pd.Timedelta(days=1)
)

base["ya_emisor"] = (
    base["fecha_primera_inscripcion"].notna()
    & (
        base["fecha_primera_inscripcion"]
        < base["fecha_decision"]
    )
)

e = base[
    ~base["ya_emisor"]
].copy()

e["TARGET_24M"] = (
    e["fecha_primera_inscripcion"].notna()
    & (
        e["fecha_primera_inscripcion"]
        >= e["fecha_decision"]
    )
    & (
        e["fecha_primera_inscripcion"]
        <= e["fin_ventana_24m"]
    )
).astype("int8")


# ============================================================
# 10. BLOQUE FINANCIERO BI
# ============================================================

financieras_bi = [
    "bi_activos",
    "bi_patrimonio",
    "bi_ingresos_ventas",
    "bi_ingresos_totales",
    "bi_utilidad_an_imp",
    "bi_impuesto_renta",
    "bi_utilidad_ejercicio",
    "bi_utilidad_neta"
]

for c in financieras_bi:
    e[c] = pd.to_numeric(
        e[c],
        errors="coerce"
    )

e["bi_8_finanzas_cero"] = False

mask_bi = e["fuente_bi"]

e.loc[
    mask_bi,
    "bi_8_finanzas_cero"
] = (
    e.loc[
        mask_bi,
        financieras_bi
    ]
    .fillna(0)
    .abs()
    .le(0.01)
    .all(axis=1)
)


# ============================================================
# 11. ACTIVOS FINAL
# ============================================================

e["activos_final"] = pd.to_numeric(
    e["bi_activos"],
    errors="coerce"
)

e.loc[
    e["fuente_bi"]
    & e["bi_8_finanzas_cero"],
    "activos_final"
] = np.nan

e["activos_fallback_old"] = (
    e["fuente_old"]
    & e["activos_old"].notna()
    & (
        ~e["fuente_bi"]
        | e["bi_8_finanzas_cero"]
    )
)

e.loc[
    e["activos_fallback_old"],
    "activos_final"
] = pd.to_numeric(
    e.loc[
        e["activos_fallback_old"],
        "activos_old"
    ],
    errors="coerce"
)


# ============================================================
# 12. PATRIMONIO FINAL
# ============================================================

e["patrimonio_final"] = pd.to_numeric(
    e["bi_patrimonio"],
    errors="coerce"
)

e.loc[
    e["fuente_bi"]
    & e["bi_8_finanzas_cero"],
    "patrimonio_final"
] = np.nan

e["patrimonio_fallback_old"] = (
    e["fuente_old"]
    & e["patrimonio_old"].notna()
    & (
        ~e["fuente_bi"]
        | e["bi_8_finanzas_cero"]
    )
)

e.loc[
    e["patrimonio_fallback_old"],
    "patrimonio_final"
] = pd.to_numeric(
    e.loc[
        e["patrimonio_fallback_old"],
        "patrimonio_old"
    ],
    errors="coerce"
)


# ============================================================
# 13. UTILIDAD NETA FINAL
# ============================================================

e["utilidad_neta_final"] = np.nan

mask_utilidad = (
    e["fuente_bi"]
    & ~e["bi_8_finanzas_cero"]
)

e.loc[
    mask_utilidad,
    "utilidad_neta_final"
] = pd.to_numeric(
    e.loc[
        mask_utilidad,
        "bi_utilidad_neta"
    ],
    errors="coerce"
)

# La utilidad histórica se conserva exclusivamente
# como dato de auditoría y nunca se usa como fallback.


# ============================================================
# 14. CONTROLES DEL UNIVERSO CONGELADO
# ============================================================

assert len(e) == ESPERADO_ELEGIBLES, (
    f"ERROR: elegibles={len(e)}; "
    f"esperado={ESPERADO_ELEGIBLES}"
)

assert int(e["TARGET_24M"].sum()) == ESPERADO_POSITIVOS, (
    f"ERROR: positivos={int(e['TARGET_24M'].sum())}; "
    f"esperado={ESPERADO_POSITIVOS}"
)

assert (
    e.loc[
        e["TARGET_24M"] == 1,
        "RUC"
    ].nunique()
    == ESPERADO_RUC_POSITIVOS
), "ERROR en cantidad de RUC positivos únicos."

assert (
    e.duplicated(
        ["ANIO", "EXPEDIENTE_KEY"]
    ).sum()
    == 0
), "ERROR: duplicados finales empresa-año."


# ============================================================
# 15. COLUMNAS EXCLUIDAS INTENCIONALMENTE
# ============================================================

# NO se incorporan:
#
# cia_imvalores
# id_estado_financiero
# posicion_general
#
# Motivo:
# riesgo de fuga de información, identificador técnico
# o variable de ranking no apropiada como predictor.


# ============================================================
# 16. ORDENAR DATASET
# ============================================================

columnas_inicio = [
    "ANIO",
    "EXPEDIENTE_KEY",
    "RUC",
    "NOMBRE",

    "tipo_compania",
    "codigo_provincia",
    "provincia",

    "fecha_decision",
    "fin_ventana_24m",
    "fecha_primera_inscripcion",
    "TARGET_24M",

    "tipo_fuente",
    "fuente_bi",
    "fuente_old",
    "fuente_ruc",
    "ruc_difiere",

    "bi_8_finanzas_cero",
    "activos_fallback_old",
    "patrimonio_fallback_old",

    "activos_final",
    "patrimonio_final",
    "utilidad_neta_final"
]

columnas_restantes = [
    c
    for c in e.columns
    if c not in columnas_inicio
    and c != "ya_emisor"
]

e = e[
    columnas_inicio
    + columnas_restantes
]

e = e.sort_values(
    [
        "ANIO",
        "EXPEDIENTE_KEY"
    ]
).reset_index(drop=True)


# ============================================================
# 17. GUARDAR DATASET
# ============================================================

RUTA_SALIDA.parent.mkdir(
    parents=True,
    exist_ok=True
)

e.to_csv(
    RUTA_SALIDA,
    index=False,
    encoding="utf-8",
    compression={
        "method": "gzip",
        "compresslevel": 6,
        "mtime": 0
    }
)


# ============================================================
# 18. HASH DE REPRODUCIBILIDAD
# ============================================================

hash_salida = sha256_archivo(
    RUTA_SALIDA
)


# ============================================================
# 19. RESUMEN POR AÑO
# ============================================================

res_anio = (
    e.groupby("ANIO")
    .agg(
        ELEGIBLES=(
            "EXPEDIENTE_KEY",
            "size"
        ),
        POSITIVOS=(
            "TARGET_24M",
            "sum"
        ),
        ACTIVOS_DISPONIBLES=(
            "activos_final",
            lambda x: int(x.notna().sum())
        ),
        PATRIMONIO_DISPONIBLE=(
            "patrimonio_final",
            lambda x: int(x.notna().sum())
        ),
        UTILIDAD_NETA_DISPONIBLE=(
            "utilidad_neta_final",
            lambda x: int(x.notna().sum())
        )
    )
    .reset_index()
)

# Convertir explícitamente antes de multiplicar por 100.
# Evita overflow del int8 de TARGET_24M.
res_anio["ELEGIBLES"] = (
    res_anio["ELEGIBLES"]
    .astype("int64")
)

res_anio["POSITIVOS"] = (
    res_anio["POSITIVOS"]
    .astype("int64")
)

res_anio["PREVALENCIA_PCT"] = (
    100.0
    * res_anio["POSITIVOS"].astype("float64")
    / res_anio["ELEGIBLES"].astype("float64")
)


# ============================================================
# 20. REPORTE QA
# ============================================================

positivos_total = int(
    e["TARGET_24M"]
    .astype("int64")
    .sum()
)

prevalencia_total = (
    100.0
    * positivos_total
    / len(e)
)

salida = []

salida.append(
    "PASO 179 - RECONSTRUCCION Y VALIDACION REPRODUCIBLE V10"
)
salida.append("=" * 135)
salida.append("")

salida.append("ARCHIVO GENERADO")
salida.append("-" * 135)

salida.append(
    str(RUTA_SALIDA)
)

salida.append(
    f"SHA256: {hash_salida}"
)

salida.append("")
salida.append("CONTROL DEL UNIVERSO")
salida.append("-" * 135)

salida.append(
    f"Observaciones elegibles: {len(e)}"
)

salida.append(
    f"Columnas: {len(e.columns)}"
)

salida.append(
    f"Duplicados empresa-año: "
    f"{int(e.duplicated(['ANIO', 'EXPEDIENTE_KEY']).sum())}"
)

salida.append(
    f"Positivos: {positivos_total}"
)

salida.append(
    f"Prevalencia correcta: {prevalencia_total:.6f}%"
)

salida.append(
    "RUC positivos únicos: "
    f"{e.loc[e['TARGET_24M'] == 1, 'RUC'].nunique()}"
)

salida.append("")
salida.append("PROCEDENCIA")
salida.append("-" * 135)

salida.append(
    e["tipo_fuente"]
    .value_counts()
    .to_string()
)

salida.append("")
salida.append(
    "RUC discrepantes catálogo/histórico: "
    f"{int(e['ruc_difiere'].sum())}"
)

salida.append(
    "Bloques BI con 8 variables financieras en cero: "
    f"{int(e['bi_8_finanzas_cero'].sum())}"
)

salida.append(
    "Fallback histórico de activos: "
    f"{int(e['activos_fallback_old'].sum())}"
)

salida.append(
    "Fallback histórico de patrimonio: "
    f"{int(e['patrimonio_fallback_old'].sum())}"
)

salida.append("")
salida.append("COBERTURA FINAL")
salida.append("-" * 135)

salida.append(
    f"Activos disponibles: "
    f"{int(e['activos_final'].notna().sum())} "
    f"({100.0 * e['activos_final'].notna().mean():.2f}%)"
)

salida.append(
    f"Patrimonio disponible: "
    f"{int(e['patrimonio_final'].notna().sum())} "
    f"({100.0 * e['patrimonio_final'].notna().mean():.2f}%)"
)

salida.append(
    f"Utilidad neta disponible: "
    f"{int(e['utilidad_neta_final'].notna().sum())} "
    f"({100.0 * e['utilidad_neta_final'].notna().mean():.2f}%)"
)

salida.append("")
salida.append("=" * 135)
salida.append("DETALLE POR AÑO")
salida.append("=" * 135)
salida.append("")

salida.append(
    res_anio.to_string(
        index=False,
        formatters={
            "PREVALENCIA_PCT":
                lambda x: f"{x:.6f}"
        }
    )
)

salida.append("")
salida.append("=" * 135)
salida.append("CONTROL DE REPRODUCIBILIDAD")
salida.append("=" * 135)
salida.append("")

hash_esperado = (
    "b44f9ccf309c20a59be436953a0c6e7f"
    "9a3dc1f11cc6f2c87e41c1676a3a2a8d"
)

salida.append(
    f"SHA256 esperado: {hash_esperado}"
)

salida.append(
    f"SHA256 obtenido: {hash_salida}"
)

salida.append(
    "Hash idéntico: "
    + (
        "SI"
        if hash_salida == hash_esperado
        else "NO"
    )
)

if hash_salida != hash_esperado:
    raise AssertionError(
        "El dataset reconstruido no tiene el mismo SHA256 "
        "que el dataset validado en el Paso 178."
    )

salida.append("")
salida.append(
    "RESULTADO: DATASET V10 RECONSTRUIDO Y VALIDADO CORRECTAMENTE."
)

with open(
    RUTA_REPORTE,
    "w",
    encoding="utf-8"
) as f:
    f.write(
        "\n".join(salida)
    )

print(
    "Dataset reconstruido correctamente:"
)
print(
    RUTA_SALIDA
)

print(
    "SHA256:"
)
print(
    hash_salida
)

print(
    "Reporte creado:"
)
print(
    RUTA_REPORTE
)
