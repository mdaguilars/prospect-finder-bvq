from pathlib import Path
import hashlib

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURACION
# ============================================================

INPUT_FILE = Path(
    "data/processed/v10_base_integrated_2012_2023.csv.gz"
)

OUTPUT_FILE = Path(
    "data/processed/v10_features_core_2012_2023.csv.gz"
)

REPORT_FILE = Path(
    "salida_paso197.txt"
)

FEATURE_VERSION = "v10-core"


# ============================================================
# VARIABLES CONGELADAS
# ============================================================

FEATURES_T = [
    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",
]

FEATURES_T1 = [
    "activos_final_t1",
    "patrimonio_final_t1",
    "bi_ingresos_ventas_t1",
    "bi_n_empleados_t1",
]

FEATURES_CAT = [
    "tipo_compania",
    "provincia",
]

FEATURES_CORE = (
    FEATURES_T
    + FEATURES_T1
    + FEATURES_CAT
)

ADMIN_COLUMNS = [
    "ANIO",
    "EXPEDIENTE_KEY",
    "RUC",
    "NOMBRE",
    "TARGET_24M",
    "SPLIT",
]

AUDIT_COLUMNS = [
    "TIENE_T_MENOS_1",
    "flag_activos_negativos",
    "flag_ventas_negativas",
    "flag_empleados_fijo",
    "flag_empleados_salto_temporal",
    "flag_empleados_anomalia_total",
]


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)

    return h.hexdigest()


def asignar_split(anio: int) -> str:
    if 2012 <= anio <= 2018:
        return "TRAIN"

    if anio == 2019:
        return "EMBARGO_1"

    if anio == 2020:
        return "VALIDATION"

    if anio == 2021:
        return "EMBARGO_2"

    if 2022 <= anio <= 2023:
        return "TEST"

    return "FUERA"


# ============================================================
# CARGA
# ============================================================

print("=" * 80)
print("CONSTRUCCION FEATURE SET V10-CORE")
print("=" * 80)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"No existe el dataset base: {INPUT_FILE}"
    )

columnas_entrada = [
    "ANIO",
    "EXPEDIENTE_KEY",
    "RUC",
    "NOMBRE",
    "TARGET_24M",
    "tipo_compania",
    "provincia",
    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",
]

df = pd.read_csv(
    INPUT_FILE,
    usecols=columnas_entrada,
    low_memory=False,
)

print(f"Filas cargadas: {len(df):,}")


# ============================================================
# VALIDACIONES DEL DATASET BASE
# ============================================================

assert len(df) == 1_030_671, (
    f"Filas inesperadas: {len(df):,}"
)

assert int(df["TARGET_24M"].sum()) == 568, (
    "El número de positivos no coincide con el freeze v10."
)

duplicados = df.duplicated(
    subset=["EXPEDIENTE_KEY", "ANIO"]
).sum()

assert duplicados == 0, (
    f"Existen {duplicados:,} duplicados empresa-año."
)

assert df["ANIO"].min() == 2012
assert df["ANIO"].max() == 2023


# ============================================================
# ORDEN TEMPORAL DETERMINISTICO
# ============================================================

df = (
    df.sort_values(
        ["EXPEDIENTE_KEY", "ANIO"],
        kind="mergesort",
    )
    .reset_index(drop=True)
)


# ============================================================
# CONVERSION NUMERICA
# ============================================================

numericas = [
    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",
]

for col in numericas:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce",
    )


# ============================================================
# REGLA 1 - ACTIVOS NEGATIVOS
# ============================================================

df["flag_activos_negativos"] = (
    df["activos_final"] < 0
)

n_activos_negativos = int(
    df["flag_activos_negativos"].sum()
)

assert n_activos_negativos == 7, (
    "El conteo de activos negativos cambió respecto "
    "de la auditoría congelada."
)

df.loc[
    df["flag_activos_negativos"],
    "activos_final",
] = np.nan


# ============================================================
# REGLA 2 - VENTAS NEGATIVAS
# ============================================================

df["flag_ventas_negativas"] = (
    df["bi_ingresos_ventas"] < 0
)

n_ventas_negativas = int(
    df["flag_ventas_negativas"].sum()
)

assert n_ventas_negativas == 6, (
    "El conteo de ventas negativas cambió respecto "
    "de la auditoría congelada."
)

df.loc[
    df["flag_ventas_negativas"],
    "bi_ingresos_ventas",
] = np.nan


# ============================================================
# REGLA 3 - EMPLEADOS
#
# IMPORTANTE:
# La mediana histórica se reproduce según la auditoría
# congelada: utiliza observaciones anteriores no negativas.
# ============================================================

empleados_raw = df["bi_n_empleados"].copy()

df["flag_empleados_fijo"] = (
    (empleados_raw < 0)
    | (empleados_raw > 50_000)
)

prior_mediana = np.full(
    len(df),
    np.nan,
    dtype=float,
)

prior_conteo = np.zeros(
    len(df),
    dtype=np.int32,
)

historial = {}

for i, (expediente, valor) in enumerate(
    zip(
        df["EXPEDIENTE_KEY"].to_numpy(),
        empleados_raw.to_numpy(),
    )
):
    valores = historial.get(expediente)

    if valores:
        prior_mediana[i] = float(
            np.median(valores)
        )
        prior_conteo[i] = len(valores)

    if pd.notna(valor) and valor >= 0:
        if valores is None:
            historial[expediente] = [
                float(valor)
            ]
        else:
            valores.append(
                float(valor)
            )


df["_empleados_mediana_previa"] = prior_mediana
df["_empleados_n_previos"] = prior_conteo

df["flag_empleados_salto_temporal"] = (
    (df["_empleados_n_previos"] >= 2)
    & (empleados_raw >= 1_000)
    & df["_empleados_mediana_previa"].notna()
    & (
        empleados_raw
        >= (
            100
            * df["_empleados_mediana_previa"]
        )
    )
)

df["flag_empleados_anomalia_total"] = (
    df["flag_empleados_fijo"]
    | df["flag_empleados_salto_temporal"]
)

n_emp_fijo = int(
    df["flag_empleados_fijo"].sum()
)

n_emp_salto = int(
    df["flag_empleados_salto_temporal"].sum()
)

n_emp_total = int(
    df["flag_empleados_anomalia_total"].sum()
)

assert n_emp_fijo == 24, (
    f"Empleados regla fija: {n_emp_fijo}, esperado 24."
)

assert n_emp_salto == 153, (
    f"Empleados salto temporal: {n_emp_salto}, esperado 153."
)

assert n_emp_total == 165, (
    f"Empleados anomalía total: {n_emp_total}, esperado 165."
)

df.loc[
    df["flag_empleados_anomalia_total"],
    "bi_n_empleados",
] = np.nan


# ============================================================
# VALIDACION DE IMPACTO SOBRE POSITIVOS
# ============================================================

alguna_anomalia_core = (
    df["flag_activos_negativos"]
    | df["flag_ventas_negativas"]
    | df["flag_empleados_anomalia_total"]
)

positivos_afectados = int(
    df.loc[
        alguna_anomalia_core,
        "TARGET_24M",
    ].sum()
)

assert positivos_afectados == 0, (
    "Una regla de calidad core afecta una observación positiva."
)


# ============================================================
# CONSTRUCCION DE LAGS EXACTOS t-1
# ============================================================

anio_prev = (
    df.groupby("EXPEDIENTE_KEY")["ANIO"]
    .shift(1)
)

df["TIENE_T_MENOS_1"] = (
    anio_prev
    == (df["ANIO"] - 1)
)

for col in FEATURES_T:

    lag = (
        df.groupby("EXPEDIENTE_KEY")[col]
        .shift(1)
    )

    df[f"{col}_t1"] = lag.where(
        df["TIENE_T_MENOS_1"]
    )


# ============================================================
# VALIDACION DE LAGS
# ============================================================

n_t1 = int(
    df["TIENE_T_MENOS_1"].sum()
)

assert n_t1 == 863_163, (
    f"Filas con t-1 exacto: {n_t1:,}; esperado 863,163."
)

positivos_t1 = int(
    (
        (df["TARGET_24M"] == 1)
        & df["TIENE_T_MENOS_1"]
    ).sum()
)

assert positivos_t1 == 494, (
    f"Positivos con t-1: {positivos_t1}; esperado 494."
)


# ============================================================
# SPLIT TEMPORAL CONGELADO
# ============================================================

df["SPLIT"] = (
    df["ANIO"]
    .astype(int)
    .map(asignar_split)
)

assert not (
    df["SPLIT"] == "FUERA"
).any()


# ============================================================
# VALIDACION DEL SPLIT
# ============================================================

esperado_split = {
    "TRAIN": (470_722, 407),
    "EMBARGO_1": (91_934, 34),
    "VALIDATION": (98_471, 34),
    "EMBARGO_2": (109_099, 39),
    "TEST": (260_445, 54),
}

for split, (
    filas_esperadas,
    positivos_esperados,
) in esperado_split.items():

    g = df[df["SPLIT"] == split]

    filas = len(g)
    positivos = int(
        g["TARGET_24M"].sum()
    )

    assert filas == filas_esperadas, (
        f"{split}: filas={filas:,}; "
        f"esperado={filas_esperadas:,}"
    )

    assert positivos == positivos_esperados, (
        f"{split}: positivos={positivos}; "
        f"esperado={positivos_esperados}"
    )


# ============================================================
# DATASET FINAL
# ============================================================

columnas_salida = (
    ADMIN_COLUMNS
    + FEATURES_CORE
    + AUDIT_COLUMNS
)

out = df[
    columnas_salida
].copy()


# ============================================================
# VALIDACIONES DEL FEATURE SET
# ============================================================

assert len(FEATURES_CORE) == 10

assert FEATURES_CORE == [
    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",
    "activos_final_t1",
    "patrimonio_final_t1",
    "bi_ingresos_ventas_t1",
    "bi_n_empleados_t1",
    "tipo_compania",
    "provincia",
]

assert len(out) == 1_030_671

assert out.duplicated(
    ["EXPEDIENTE_KEY", "ANIO"]
).sum() == 0

assert int(
    out["TARGET_24M"].sum()
) == 568


# ============================================================
# ORDEN FINAL DETERMINISTICO
# ============================================================

out = (
    out.sort_values(
        ["ANIO", "EXPEDIENTE_KEY"],
        kind="mergesort",
    )
    .reset_index(drop=True)
)


# ============================================================
# GUARDADO
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

out.to_csv(
    OUTPUT_FILE,
    index=False,
    compression="gzip",
)

hash_salida = sha256_file(
    OUTPUT_FILE
)


# ============================================================
# REPORTE DE VALIDACION
# ============================================================

with REPORT_FILE.open(
    "w",
    encoding="utf-8",
) as f:

    f.write("=" * 125 + "\n")
    f.write(
        "CONSTRUCCION Y VALIDACION "
        "FEATURE SET V10-CORE\n"
    )
    f.write("=" * 125 + "\n\n")

    f.write(
        f"Version              : "
        f"{FEATURE_VERSION}\n"
    )

    f.write(
        f"Archivo entrada      : "
        f"{INPUT_FILE}\n"
    )

    f.write(
        f"Archivo salida       : "
        f"{OUTPUT_FILE}\n"
    )

    f.write(
        f"SHA256 salida        : "
        f"{hash_salida}\n\n"
    )

    f.write(
        f"Filas                : "
        f"{len(out):,}\n"
    )

    f.write(
        f"Columnas             : "
        f"{len(out.columns)}\n"
    )

    f.write(
        f"Positivos            : "
        f"{int(out['TARGET_24M'].sum()):,}\n"
    )

    f.write(
        f"Duplicados empresa-año: "
        f"{out.duplicated(['EXPEDIENTE_KEY', 'ANIO']).sum():,}\n\n"
    )

    f.write("=" * 125 + "\n")
    f.write("1. VARIABLES PREDICTORAS CORE\n")
    f.write("=" * 125 + "\n\n")

    for i, col in enumerate(
        FEATURES_CORE,
        1,
    ):
        f.write(
            f"{i:02d}. {col}\n"
        )

    f.write("\n")
    f.write(
        f"Total predictores conceptuales: "
        f"{len(FEATURES_CORE)}\n\n"
    )

    f.write("=" * 125 + "\n")
    f.write("2. REGLAS DE CALIDAD APLICADAS\n")
    f.write("=" * 125 + "\n\n")

    f.write(
        f"Activos negativos -> NaN       : "
        f"{n_activos_negativos:,}\n"
    )

    f.write(
        f"Ventas negativas -> NaN        : "
        f"{n_ventas_negativas:,}\n"
    )

    f.write(
        f"Empleados regla fija           : "
        f"{n_emp_fijo:,}\n"
    )

    f.write(
        f"Empleados salto temporal       : "
        f"{n_emp_salto:,}\n"
    )

    f.write(
        f"Empleados anomalía total -> NaN: "
        f"{n_emp_total:,}\n"
    )

    f.write(
        f"Positivos afectados            : "
        f"{positivos_afectados:,}\n\n"
    )

    f.write("=" * 125 + "\n")
    f.write("3. DISPONIBILIDAD t-1\n")
    f.write("=" * 125 + "\n\n")

    f.write(
        f"Filas con t-1 exacto     : "
        f"{n_t1:,} "
        f"({n_t1 / len(out) * 100:.2f}%)\n"
    )

    f.write(
        f"Positivos con t-1 exacto : "
        f"{positivos_t1:,} "
        f"({positivos_t1 / 568 * 100:.2f}%)\n\n"
    )

    for col in FEATURES_T1:

        total_no_nulo = int(
            out[col].notna().sum()
        )

        positivos_no_nulo = int(
            out.loc[
                out["TARGET_24M"] == 1,
                col,
            ].notna().sum()
        )

        f.write(
            f"{col:<32} | "
            f"total={total_no_nulo:>9,} | "
            f"positivos={positivos_no_nulo:>4}/568\n"
        )

    f.write("\n" + "=" * 125 + "\n")
    f.write("4. SPLIT TEMPORAL\n")
    f.write("=" * 125 + "\n\n")

    for split in [
        "TRAIN",
        "EMBARGO_1",
        "VALIDATION",
        "EMBARGO_2",
        "TEST",
    ]:

        g = out[
            out["SPLIT"] == split
        ]

        pos = int(
            g["TARGET_24M"].sum()
        )

        prevalencia = (
            pos / len(g) * 100
        )

        f.write(
            f"{split:<12} | "
            f"filas={len(g):>9,} | "
            f"positivos={pos:>4,} | "
            f"prevalencia={prevalencia:>9.6f}%\n"
        )

    f.write("\n" + "=" * 125 + "\n")
    f.write("5. COBERTURA DE PREDICTORES\n")
    f.write("=" * 125 + "\n\n")

    for col in FEATURES_CORE:

        n = int(
            out[col].notna().sum()
        )

        pct = (
            n
            / len(out)
            * 100
        )

        f.write(
            f"{col:<32} | "
            f"no_nulos={n:>9,} | "
            f"cobertura={pct:>7.2f}%\n"
        )

    f.write("\n" + "=" * 125 + "\n")
    f.write("6. COLUMNAS DEL ARCHIVO FINAL\n")
    f.write("=" * 125 + "\n\n")

    for i, col in enumerate(
        out.columns,
        1,
    ):
        f.write(
            f"{i:02d}. {col}\n"
        )

    f.write("\n" + "=" * 125 + "\n")
    f.write("7. ESTADO\n")
    f.write("=" * 125 + "\n\n")

    f.write(
        "Feature Set físico v10-core "
        "construido y validado correctamente.\n"
    )

    f.write(
        "No se realizó entrenamiento de modelos.\n"
    )

    f.write(
        "TEST permanece cerrado para evaluación predictiva.\n"
    )


# ============================================================
# SALIDA CONSOLA
# ============================================================

print()
print("Construcción completada.")
print(f"Archivo : {OUTPUT_FILE}")
print(f"Filas   : {len(out):,}")
print(f"Columnas: {len(out.columns)}")
print(f"SHA256  : {hash_salida}")
print(f"Reporte : {REPORT_FILE}")
print()
print(
    "No se entrenó ningún modelo. "
    "TEST permanece cerrado."
)
