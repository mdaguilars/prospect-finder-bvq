from pathlib import Path
from datetime import datetime, timezone
import json

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CORE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "v10_features_core_2012_2023.csv.gz"
)

BASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "v10_base_integrated_2012_2023.csv.gz"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "v10_features_financial_2012_2023.csv.gz"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "v10"
)

PROFILE_PATH = (
    REPORT_DIR
    / "v10_financial_features_profile.csv"
)

METADATA_PATH = (
    REPORT_DIR
    / "v10_financial_features_metadata.json"
)


# ============================================================
# UNIVERSO CONGELADO V10
# ============================================================

EXPECTED_TOTAL_ROWS = 1_030_671

EXPECTED_SPLIT_COUNTS = {
    "TRAIN": 470_722,
    "EMBARGO_1": 91_934,
    "VALIDATION": 98_471,
    "EMBARGO_2": 109_099,
    "TEST": 260_445,
}


# ============================================================
# CLAVES
# ============================================================

KEY_COLUMNS = [
    "ANIO",
    "EXPEDIENTE_KEY",
]


# ============================================================
# VARIABLES REQUERIDAS DEL CORE
# ============================================================

CORE_REQUIRED_COLUMNS = [
    "ANIO",
    "EXPEDIENTE_KEY",
    "RUC",
    "NOMBRE",
    "TARGET_24M",
    "SPLIT",

    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",

    "activos_final_t1",
    "patrimonio_final_t1",
    "bi_ingresos_ventas_t1",
    "bi_n_empleados_t1",
]


# ============================================================
# VARIABLES REQUERIDAS DE LA BASE
# ============================================================

BASE_REQUIRED_COLUMNS = [
    "ANIO",
    "EXPEDIENTE_KEY",
    "utilidad_neta_final",
]


# ============================================================
# NUEVAS VARIABLES FINANCIERAS
# ============================================================

FINANCIAL_RATIO_FEATURES = [
    "fin_ratio_patrimonio_activos",
    "fin_roa",
    "fin_margen_neto",
    "fin_rotacion_activos",
    "fin_roe",
]


FINANCIAL_GROWTH_FEATURES = [
    "fin_crecimiento_activos",
    "fin_crecimiento_patrimonio",
    "fin_crecimiento_ventas",
    "fin_crecimiento_empleados",
]


FINANCIAL_NUMERIC_FEATURES = (
    FINANCIAL_RATIO_FEATURES
    + FINANCIAL_GROWTH_FEATURES
)


FINANCIAL_FLAG_FEATURES = [
    "flag_patrimonio_no_positivo",
]


FINANCIAL_FEATURES = (
    FINANCIAL_NUMERIC_FEATURES
    + FINANCIAL_FLAG_FEATURES
)


# ============================================================
# DEFINICIONES
# ============================================================

FEATURE_DEFINITIONS = {

    "fin_ratio_patrimonio_activos": {
        "formula":
            "patrimonio_final / activos_final",

        "regla":
            (
                "Se calcula únicamente cuando activos_final > 0. "
                "El patrimonio puede ser positivo, cero o negativo."
            ),
    },

    "fin_roa": {
        "formula":
            "utilidad_neta_final / activos_final",

        "regla":
            (
                "Se calcula únicamente cuando activos_final > 0."
            ),
    },

    "fin_margen_neto": {
        "formula":
            "utilidad_neta_final / bi_ingresos_ventas",

        "regla":
            (
                "Se calcula únicamente cuando "
                "bi_ingresos_ventas > 0."
            ),
    },

    "fin_rotacion_activos": {
        "formula":
            "bi_ingresos_ventas / activos_final",

        "regla":
            (
                "Se calcula únicamente cuando activos_final > 0."
            ),
    },

    "fin_roe": {
        "formula":
            "utilidad_neta_final / patrimonio_final",

        "regla":
            (
                "Se calcula únicamente cuando patrimonio_final > 0. "
                "No se calcula ROE cuando el patrimonio es cero "
                "o negativo."
            ),
    },

    "fin_crecimiento_activos": {
        "formula":
            "(activos_final / activos_final_t1) - 1",

        "regla":
            (
                "Se calcula únicamente cuando activos_final_t1 > 0. "
                "Si no existe t-1, el resultado permanece missing."
            ),
    },

    "fin_crecimiento_patrimonio": {
        "formula":
            "(patrimonio_final / patrimonio_final_t1) - 1",

        "regla":
            (
                "Se calcula únicamente cuando "
                "patrimonio_final_t1 > 0. "
                "No se calcula crecimiento porcentual cuando "
                "el patrimonio anterior es cero o negativo."
            ),
    },

    "fin_crecimiento_ventas": {
        "formula":
            "(bi_ingresos_ventas / bi_ingresos_ventas_t1) - 1",

        "regla":
            (
                "Se calcula únicamente cuando "
                "bi_ingresos_ventas_t1 > 0. "
                "Las observaciones con ventas t-1 iguales a cero "
                "permanecen missing para esta variable."
            ),
    },

    "fin_crecimiento_empleados": {
        "formula":
            "(bi_n_empleados / bi_n_empleados_t1) - 1",

        "regla":
            (
                "Se calcula únicamente cuando "
                "bi_n_empleados_t1 > 0."
            ),
    },

    "flag_patrimonio_no_positivo": {
        "formula":
            "patrimonio_final <= 0",

        "regla":
            (
                "TRUE cuando patrimonio_final es cero o negativo. "
                "FALSE cuando es positivo. "
                "Missing cuando patrimonio_final no está disponible."
            ),
    },
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def ruta_relativa(path):

    return str(
        path.relative_to(
            PROJECT_ROOT
        )
    ).replace(
        "\\",
        "/",
    )


def validar_archivo(
    path,
    nombre,
):

    if not path.exists():

        raise FileNotFoundError(
            f"No existe {nombre}:\n{path}"
        )


def validar_columnas(
    dataframe,
    required_columns,
    nombre,
):

    faltantes = [
        columna
        for columna in required_columns
        if columna not in dataframe.columns
    ]

    if faltantes:

        raise ValueError(
            f"{nombre} no contiene las siguientes columnas:\n"
            + "\n".join(
                faltantes
            )
        )


def validar_clave_unica(
    dataframe,
    nombre,
):

    duplicados = dataframe.duplicated(
        subset=KEY_COLUMNS,
        keep=False,
    )

    cantidad = int(
        duplicados.sum()
    )

    if cantidad > 0:

        ejemplo = (
            dataframe.loc[
                duplicados,
                KEY_COLUMNS,
            ]
            .head(
                20
            )
        )

        raise ValueError(
            f"{nombre} contiene {cantidad:,} filas "
            f"con claves duplicadas.\n\n"
            f"Ejemplo:\n"
            f"{ejemplo.to_string(index=False)}"
        )


def convertir_numerico(
    serie,
):

    return pd.to_numeric(
        serie,
        errors="coerce",
    ).replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )


def division_segura(
    numerador,
    denominador,
):

    numerador = convertir_numerico(
        numerador
    )

    denominador = convertir_numerico(
        denominador
    )

    resultado = pd.Series(
        np.nan,
        index=numerador.index,
        dtype="float64",
    )

    mascara = (
        numerador.notna()
        &
        denominador.notna()
        &
        (
            denominador
            > 0
        )
    )

    resultado.loc[
        mascara
    ] = (
        numerador.loc[
            mascara
        ]
        /
        denominador.loc[
            mascara
        ]
    )

    resultado = resultado.replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )

    return resultado


def crecimiento_interanual(
    valor_actual,
    valor_anterior,
):

    razon = division_segura(
        valor_actual,
        valor_anterior,
    )

    crecimiento = (
        razon
        - 1.0
    )

    crecimiento = crecimiento.replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )

    return crecimiento


# ============================================================
# CARGA
# ============================================================

def cargar_core():

    validar_archivo(
        CORE_PATH,
        "dataset core v10",
    )

    print(
        "\nCargando dataset core v10..."
    )

    print(
        CORE_PATH
    )

    dataframe = pd.read_csv(
        CORE_PATH,
        low_memory=False,
        dtype={
            "RUC":
                "string",

            "NOMBRE":
                "string",

            "SPLIT":
                "string",
        },
    )

    validar_columnas(
        dataframe,
        CORE_REQUIRED_COLUMNS,
        "Dataset core v10",
    )

    return dataframe


def cargar_utilidad_neta():

    validar_archivo(
        BASE_PATH,
        "dataset base integrado v10",
    )

    print(
        "\nCargando utilidad neta desde base integrada..."
    )

    print(
        BASE_PATH
    )

    encabezado = pd.read_csv(
        BASE_PATH,
        nrows=0,
    )

    validar_columnas(
        encabezado,
        BASE_REQUIRED_COLUMNS,
        "Dataset base integrado v10",
    )

    dataframe = pd.read_csv(
        BASE_PATH,
        usecols=BASE_REQUIRED_COLUMNS,
        low_memory=False,
    )

    return dataframe


# ============================================================
# VALIDACIÓN DEL UNIVERSO
# ============================================================

def validar_universo_core(
    core,
):

    print(
        "\nValidando universo congelado..."
    )

    if len(
        core
    ) != EXPECTED_TOTAL_ROWS:

        raise ValueError(
            "El número de filas del core no coincide "
            "con el universo congelado.\n"
            f"Esperado: {EXPECTED_TOTAL_ROWS:,}\n"
            f"Encontrado: {len(core):,}"
        )

    core[
        "SPLIT"
    ] = (
        core[
            "SPLIT"
        ]
        .astype(
            "string"
        )
        .str.strip()
        .str.upper()
    )

    conteos = (
        core[
            "SPLIT"
        ]
        .value_counts(
            dropna=False
        )
        .to_dict()
    )

    for split, esperado in EXPECTED_SPLIT_COUNTS.items():

        encontrado = int(
            conteos.get(
                split,
                0,
            )
        )

        print(
            f"{split:<12}: "
            f"{encontrado:,} filas"
        )

        if encontrado != esperado:

            raise ValueError(
                f"Split {split} no coincide con "
                f"el universo congelado.\n"
                f"Esperado: {esperado:,}\n"
                f"Encontrado: {encontrado:,}"
            )

    splits_esperados = set(
        EXPECTED_SPLIT_COUNTS.keys()
    )

    splits_encontrados = set(
        core[
            "SPLIT"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    inesperados = (
        splits_encontrados
        - splits_esperados
    )

    if inesperados:

        raise ValueError(
            "Se encontraron splits no esperados:\n"
            + "\n".join(
                sorted(
                    inesperados
                )
            )
        )


# ============================================================
# NORMALIZACIÓN DE CLAVES
# ============================================================

def preparar_claves(
    dataframe,
    nombre,
):

    dataframe = dataframe.copy()

    dataframe[
        "ANIO"
    ] = pd.to_numeric(
        dataframe[
            "ANIO"
        ],
        errors="coerce",
    )

    dataframe[
        "EXPEDIENTE_KEY"
    ] = pd.to_numeric(
        dataframe[
            "EXPEDIENTE_KEY"
        ],
        errors="coerce",
    )

    if dataframe[
        "ANIO"
    ].isna().any():

        raise ValueError(
            f"{nombre}: existen valores ANIO inválidos."
        )

    if dataframe[
        "EXPEDIENTE_KEY"
    ].isna().any():

        raise ValueError(
            f"{nombre}: existen EXPEDIENTE_KEY inválidos."
        )

    dataframe[
        "ANIO"
    ] = dataframe[
        "ANIO"
    ].astype(
        "int64"
    )

    dataframe[
        "EXPEDIENTE_KEY"
    ] = dataframe[
        "EXPEDIENTE_KEY"
    ].astype(
        "int64"
    )

    validar_clave_unica(
        dataframe,
        nombre,
    )

    return dataframe


# ============================================================
# INTEGRACIÓN
# ============================================================

def integrar_utilidad(
    core,
    base,
):

    print(
        "\nIntegrando utilidad_neta_final..."
    )

    core = preparar_claves(
        core,
        "Dataset core v10",
    )

    base = preparar_claves(
        base,
        "Dataset base integrado v10",
    )

    filas_core_antes = len(
        core
    )

    combinado = core.merge(
        base,
        on=KEY_COLUMNS,
        how="left",
        validate="one_to_one",
        indicator=True,
    )

    if len(
        combinado
    ) != filas_core_antes:

        raise ValueError(
            "La integración modificó el número "
            "de filas del dataset core."
        )

    sin_correspondencia = int(
        (
            combinado[
                "_merge"
            ]
            != "both"
        ).sum()
    )

    print(
        f"Filas sin correspondencia con base: "
        f"{sin_correspondencia:,}"
    )

    if sin_correspondencia > 0:

        ejemplos = (
            combinado.loc[
                combinado[
                    "_merge"
                ]
                != "both",
                KEY_COLUMNS,
            ]
            .head(
                20
            )
        )

        raise ValueError(
            "Existen observaciones del core sin "
            "correspondencia en la base integrada.\n\n"
            f"Ejemplo:\n"
            f"{ejemplos.to_string(index=False)}"
        )

    combinado = combinado.drop(
        columns=[
            "_merge",
        ]
    )

    combinado[
        "utilidad_neta_final"
    ] = convertir_numerico(
        combinado[
            "utilidad_neta_final"
        ]
    )

    return combinado


# ============================================================
# CONSTRUCCIÓN DE FEATURES FINANCIERAS
# ============================================================

def construir_features_financieras(
    dataframe,
):

    print(
        "\nConstruyendo indicadores financieros..."
    )

    df = dataframe.copy()

    # --------------------------------------------------------
    # VARIABLES ACTUALES
    # --------------------------------------------------------

    activos = convertir_numerico(
        df[
            "activos_final"
        ]
    )

    patrimonio = convertir_numerico(
        df[
            "patrimonio_final"
        ]
    )

    utilidad = convertir_numerico(
        df[
            "utilidad_neta_final"
        ]
    )

    ventas = convertir_numerico(
        df[
            "bi_ingresos_ventas"
        ]
    )

    empleados = convertir_numerico(
        df[
            "bi_n_empleados"
        ]
    )

    # --------------------------------------------------------
    # VARIABLES T-1
    # --------------------------------------------------------

    activos_t1 = convertir_numerico(
        df[
            "activos_final_t1"
        ]
    )

    patrimonio_t1 = convertir_numerico(
        df[
            "patrimonio_final_t1"
        ]
    )

    ventas_t1 = convertir_numerico(
        df[
            "bi_ingresos_ventas_t1"
        ]
    )

    empleados_t1 = convertir_numerico(
        df[
            "bi_n_empleados_t1"
        ]
    )

    # ========================================================
    # RATIOS FINANCIEROS
    # ========================================================

    # --------------------------------------------------------
    # 1. Fortaleza patrimonial
    # patrimonio / activos
    # --------------------------------------------------------

    df[
        "fin_ratio_patrimonio_activos"
    ] = division_segura(
        patrimonio,
        activos,
    )

    # --------------------------------------------------------
    # 2. ROA
    # utilidad / activos
    # --------------------------------------------------------

    df[
        "fin_roa"
    ] = division_segura(
        utilidad,
        activos,
    )

    # --------------------------------------------------------
    # 3. Margen neto
    # utilidad / ventas
    # --------------------------------------------------------

    df[
        "fin_margen_neto"
    ] = division_segura(
        utilidad,
        ventas,
    )

    # --------------------------------------------------------
    # 4. Rotación de activos
    # ventas / activos
    # --------------------------------------------------------

    df[
        "fin_rotacion_activos"
    ] = division_segura(
        ventas,
        activos,
    )

    # --------------------------------------------------------
    # 5. ROE
    # utilidad / patrimonio
    #
    # Solo se calcula con patrimonio positivo.
    # --------------------------------------------------------

    df[
        "fin_roe"
    ] = division_segura(
        utilidad,
        patrimonio,
    )

    # ========================================================
    # CRECIMIENTOS INTERANUALES
    # ========================================================

    # --------------------------------------------------------
    # 6. Crecimiento de activos
    # (actual / t-1) - 1
    # --------------------------------------------------------

    df[
        "fin_crecimiento_activos"
    ] = crecimiento_interanual(
        activos,
        activos_t1,
    )

    # --------------------------------------------------------
    # 7. Crecimiento de patrimonio
    # (actual / t-1) - 1
    #
    # Solo si patrimonio_t1 > 0.
    # --------------------------------------------------------

    df[
        "fin_crecimiento_patrimonio"
    ] = crecimiento_interanual(
        patrimonio,
        patrimonio_t1,
    )

    # --------------------------------------------------------
    # 8. Crecimiento de ventas
    # (actual / t-1) - 1
    #
    # Solo si ventas_t1 > 0.
    # --------------------------------------------------------

    df[
        "fin_crecimiento_ventas"
    ] = crecimiento_interanual(
        ventas,
        ventas_t1,
    )

    # --------------------------------------------------------
    # 9. Crecimiento de empleados
    # (actual / t-1) - 1
    #
    # Solo si empleados_t1 > 0.
    # --------------------------------------------------------

    df[
        "fin_crecimiento_empleados"
    ] = crecimiento_interanual(
        empleados,
        empleados_t1,
    )

    # ========================================================
    # BANDERAS
    # ========================================================

    # --------------------------------------------------------
    # 10. Patrimonio cero o negativo
    # --------------------------------------------------------

    flag = pd.Series(
        pd.NA,
        index=df.index,
        dtype="boolean",
    )

    mascara_patrimonio_disponible = (
        patrimonio.notna()
    )

    flag.loc[
        mascara_patrimonio_disponible
    ] = (
        patrimonio.loc[
            mascara_patrimonio_disponible
        ]
        <= 0
    )

    df[
        "flag_patrimonio_no_positivo"
    ] = flag

    return df


# ============================================================
# VALIDACIÓN DE FEATURES
# ============================================================

def validar_features(
    dataframe,
):

    print(
        "\nValidando indicadores construidos..."
    )

    for variable in FINANCIAL_NUMERIC_FEATURES:

        serie = pd.to_numeric(
            dataframe[
                variable
            ],
            errors="coerce",
        )

        array = serie.to_numpy(
            dtype="float64",
            na_value=np.nan,
        )

        infinitos = int(
            np.isinf(
                array
            ).sum()
        )

        if infinitos > 0:

            raise ValueError(
                f"{variable} contiene "
                f"{infinitos:,} valores infinitos."
            )

        print(
            f"{variable:<34} "
            f"{int(serie.notna().sum()):>10,} valores"
        )

    if dataframe[
        "flag_patrimonio_no_positivo"
    ].dtype.name != "boolean":

        raise ValueError(
            "flag_patrimonio_no_positivo "
            "no tiene dtype boolean nullable."
        )


# ============================================================
# VALIDACIÓN ESPECÍFICA DE CRECIMIENTOS
# ============================================================

def validar_crecimientos(
    dataframe,
):

    print(
        "\nValidando reglas temporales de crecimiento..."
    )

    #
    # 2012 debe permanecer sin crecimiento porque
    # no existe información t-1 dentro del universo.
    #

    subset_2012 = dataframe[
        dataframe[
            "ANIO"
        ]
        == 2012
    ]

    for variable in FINANCIAL_GROWTH_FEATURES:

        cantidad = int(
            subset_2012[
                variable
            ]
            .notna()
            .sum()
        )

        print(
            f"2012 | {variable:<30}: "
            f"{cantidad:,} valores"
        )

        if cantidad != 0:

            raise ValueError(
                f"{variable} contiene valores en 2012. "
                "Esto no es consistente con la ausencia "
                "de t-1 en el universo."
            )


# ============================================================
# PERFIL TRAIN / VALIDATION
# ============================================================

def construir_perfil(
    dataframe,
):

    #
    # Importante:
    # No se calculan percentiles del TEST.
    #
    # TRAIN y VALIDATION sí pueden utilizarse para
    # diagnóstico durante desarrollo.
    #

    filas = []

    splits_permitidos = [
        "TRAIN",
        "VALIDATION",
    ]

    for split in splits_permitidos:

        subset = dataframe[
            dataframe[
                "SPLIT"
            ]
            == split
        ]

        for variable in FINANCIAL_NUMERIC_FEATURES:

            serie = pd.to_numeric(
                subset[
                    variable
                ],
                errors="coerce",
            ).replace(
                [
                    np.inf,
                    -np.inf,
                ],
                np.nan,
            )

            filas.append(
                {
                    "SPLIT":
                        split,

                    "VARIABLE":
                        variable,

                    "FILAS":
                        len(
                            subset
                        ),

                    "NO_NULOS":
                        int(
                            serie.notna().sum()
                        ),

                    "PCT_DISPONIBLE":
                        float(
                            serie.notna().mean()
                            * 100
                        ),

                    "P01":
                        (
                            float(
                                serie.quantile(
                                    0.01
                                )
                            )
                            if serie.notna().any()
                            else np.nan
                        ),

                    "MEDIANA":
                        (
                            float(
                                serie.median()
                            )
                            if serie.notna().any()
                            else np.nan
                        ),

                    "P99":
                        (
                            float(
                                serie.quantile(
                                    0.99
                                )
                            )
                            if serie.notna().any()
                            else np.nan
                        ),
                }
            )

    return pd.DataFrame(
        filas
    )


# ============================================================
# PERFIL ANUAL DE CRECIMIENTOS
# ============================================================

def construir_perfil_crecimientos_anual(
    dataframe,
):

    filas = []

    train = dataframe[
        dataframe[
            "SPLIT"
        ]
        == "TRAIN"
    ]

    for anio in sorted(
        train[
            "ANIO"
        ]
        .dropna()
        .unique()
        .tolist()
    ):

        subset = train[
            train[
                "ANIO"
            ]
            == anio
        ]

        for variable in FINANCIAL_GROWTH_FEATURES:

            serie = pd.to_numeric(
                subset[
                    variable
                ],
                errors="coerce",
            ).replace(
                [
                    np.inf,
                    -np.inf,
                ],
                np.nan,
            )

            filas.append(
                {
                    "ANIO":
                        int(
                            anio
                        ),

                    "VARIABLE":
                        variable,

                    "FILAS":
                        len(
                            subset
                        ),

                    "NO_NULOS":
                        int(
                            serie.notna().sum()
                        ),

                    "PCT_DISPONIBLE":
                        float(
                            serie.notna().mean()
                            * 100
                        ),
                }
            )

    return pd.DataFrame(
        filas
    )


# ============================================================
# METADATA
# ============================================================

def construir_metadata(
    dataframe,
    profile,
    growth_profile,
):

    flag = dataframe[
        "flag_patrimonio_no_positivo"
    ]

    metadata = {
        "dataset":
            "v10_features_financial_2012_2023",

        "fecha_generacion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "fuente_core":
            ruta_relativa(
                CORE_PATH
            ),

        "fuente_utilidad":
            ruta_relativa(
                BASE_PATH
            ),

        "salida":
            ruta_relativa(
                OUTPUT_PATH
            ),

        "filas":
            int(
                len(
                    dataframe
                )
            ),

        "features_financieras":
            FINANCIAL_FEATURES,

        "features_ratios":
            FINANCIAL_RATIO_FEATURES,

        "features_crecimiento":
            FINANCIAL_GROWTH_FEATURES,

        "features_flags":
            FINANCIAL_FLAG_FEATURES,

        "numero_features_financieras":
            len(
                FINANCIAL_FEATURES
            ),

        "numero_ratios":
            len(
                FINANCIAL_RATIO_FEATURES
            ),

        "numero_crecimientos":
            len(
                FINANCIAL_GROWTH_FEATURES
            ),

        "numero_flags":
            len(
                FINANCIAL_FLAG_FEATURES
            ),

        "definiciones":
            FEATURE_DEFINITIONS,

        "tratamiento_outliers": {
            "aplicado_en_dataset":
                False,

            "descripcion":
                (
                    "Los ratios y crecimientos se conservan crudos. "
                    "No se aplica winsorizacion, clipping "
                    "ni capping durante la construcción "
                    "del dataset."
                ),

            "regla_modelado":
                (
                    "Para modelos sensibles a escala, "
                    "como Regresion Logistica y MLP, "
                    "los limites de capping deben aprenderse "
                    "exclusivamente con TRAIN. "
                    "En backtesting deben recalcularse "
                    "dentro del TRAIN de cada fold."
                ),
        },

        "imputacion": {
            "aplicada_en_dataset":
                False,

            "descripcion":
                (
                    "Los valores faltantes se conservan. "
                    "La imputacion, cuando sea necesaria, "
                    "debe aprenderse exclusivamente "
                    "desde TRAIN."
                ),
        },

        "escalamiento": {
            "aplicado_en_dataset":
                False,

            "descripcion":
                (
                    "No se realiza escalamiento "
                    "durante la construcción."
                ),
        },

        "crecimientos": {
            "formula_general":
                "(valor_actual / valor_t1) - 1",

            "regla_denominador":
                (
                    "El crecimiento se calcula únicamente "
                    "cuando el valor t-1 es estrictamente positivo."
                ),

            "anio_2012":
                (
                    "Permanece missing porque no existe t-1 "
                    "dentro del universo histórico disponible."
                ),

            "capping":
                False,

            "imputacion":
                False,
        },

        "test": {
            "periodo":
                "2022-2023",

            "evaluado":
                False,

            "percentiles_inspeccionados":
                False,

            "estado":
                "RESERVADO",
        },

        "split_counts": {
            split:
                int(
                    cantidad
                )
            for split, cantidad
            in dataframe[
                "SPLIT"
            ]
            .value_counts()
            .to_dict()
            .items()
        },

        "flag_patrimonio_no_positivo": {
            "true":
                int(
                    (
                        flag
                        == True
                    ).sum()
                ),

            "false":
                int(
                    (
                        flag
                        == False
                    ).sum()
                ),

            "missing":
                int(
                    flag.isna().sum()
                ),
        },

        "perfil_train_validation":
            profile.to_dict(
                orient="records"
            ),

        "perfil_anual_crecimientos_train":
            growth_profile.to_dict(
                orient="records"
            ),
    }

    return metadata


# ============================================================
# GUARDAR
# ============================================================

def guardar_resultados(
    dataframe,
    profile,
    metadata,
):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    #
    # utilidad_neta_final fue utilizada únicamente
    # como insumo para construir los indicadores.
    #
    # No se incorpora físicamente al dataset resultante
    # en esta etapa.
    #

    dataframe_salida = dataframe.drop(
        columns=[
            "utilidad_neta_final",
        ]
    )

    dataframe_salida.to_csv(
        OUTPUT_PATH,
        index=False,
        compression="gzip",
    )

    profile.to_csv(
        PROFILE_PATH,
        index=False,
    )

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8",
    ) as archivo:

        json.dump(
            metadata,
            archivo,
            ensure_ascii=False,
            indent=2,
        )


# ============================================================
# RESUMEN
# ============================================================

def mostrar_resumen(
    dataframe,
    profile,
    growth_profile,
):

    print(
        "\n"
        + "=" * 110
    )

    print(
        "NUEVA CAPA FINANCIERA V10"
    )

    print(
        "=" * 110
    )

    print(
        f"\nFilas: "
        f"{len(dataframe):,}"
    )

    print(
        f"Ratios financieros: "
        f"{len(FINANCIAL_RATIO_FEATURES)}"
    )

    print(
        f"Crecimientos interanuales: "
        f"{len(FINANCIAL_GROWTH_FEATURES)}"
    )

    print(
        f"Flags financieros: "
        f"{len(FINANCIAL_FLAG_FEATURES)}"
    )

    print(
        f"Total nuevas features: "
        f"{len(FINANCIAL_FEATURES)}"
    )

    print(
        "\nCobertura TRAIN / VALIDATION:"
    )

    print(
        profile[
            [
                "SPLIT",
                "VARIABLE",
                "PCT_DISPONIBLE",
                "P01",
                "MEDIANA",
                "P99",
            ]
        ].to_string(
            index=False
        )
    )

    print(
        "\nCobertura anual de crecimientos en TRAIN:"
    )

    print(
        growth_profile.to_string(
            index=False
        )
    )

    flag = dataframe[
        "flag_patrimonio_no_positivo"
    ]

    print(
        "\nflag_patrimonio_no_positivo:"
    )

    print(
        f"TRUE:    "
        f"{int((flag == True).sum()):,}"
    )

    print(
        f"FALSE:   "
        f"{int((flag == False).sum()):,}"
    )

    print(
        f"MISSING: "
        f"{int(flag.isna().sum()):,}"
    )

    print(
        "\nTEST 2022-2023:"
    )

    print(
        "No evaluado. "
        "No se calcularon percentiles del TEST."
    )

    print(
        "\nArchivo generado:"
    )

    print(
        OUTPUT_PATH
    )

    print(
        "\nPerfil:"
    )

    print(
        PROFILE_PATH
    )

    print(
        "\nMetadata:"
    )

    print(
        METADATA_PATH
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        + "=" * 110
    )

    print(
        "PROSPECT FINDER BVQ"
    )

    print(
        "CONSTRUCCIÓN DE FEATURES FINANCIERAS V10"
    )

    print(
        "=" * 110
    )

    print(
        "\nPrincipios:"
    )

    print(
        "- El dataset v10 core no se modifica."
    )

    print(
        "- Los ratios se almacenan crudos."
    )

    print(
        "- Los crecimientos se almacenan crudos."
    )

    print(
        "- No existe winsorizacion en esta etapa."
    )

    print(
        "- No existe imputacion en esta etapa."
    )

    print(
        "- No existe escalamiento en esta etapa."
    )

    print(
        "- Las tasas de crecimiento requieren t-1 > 0."
    )

    print(
        "- TEST permanece reservado."
    )

    # --------------------------------------------------------
    # CARGAR
    # --------------------------------------------------------

    core = cargar_core()

    base = cargar_utilidad_neta()

    # --------------------------------------------------------
    # VALIDAR CORE
    # --------------------------------------------------------

    validar_universo_core(
        core
    )

    # --------------------------------------------------------
    # INTEGRAR UTILIDAD
    # --------------------------------------------------------

    dataframe = integrar_utilidad(
        core,
        base,
    )

    # --------------------------------------------------------
    # CONSTRUIR FEATURES
    # --------------------------------------------------------

    dataframe = construir_features_financieras(
        dataframe
    )

    # --------------------------------------------------------
    # VALIDACIONES
    # --------------------------------------------------------

    validar_features(
        dataframe
    )

    validar_crecimientos(
        dataframe
    )

    if len(
        dataframe
    ) != EXPECTED_TOTAL_ROWS:

        raise ValueError(
            "El dataset final modificó "
            "el número de filas."
        )

    # --------------------------------------------------------
    # PERFIL
    # --------------------------------------------------------

    profile = construir_perfil(
        dataframe
    )

    growth_profile = construir_perfil_crecimientos_anual(
        dataframe
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    metadata = construir_metadata(
        dataframe,
        profile,
        growth_profile,
    )

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    guardar_resultados(
        dataframe,
        profile,
        metadata,
    )

    # --------------------------------------------------------
    # MOSTRAR
    # --------------------------------------------------------

    mostrar_resumen(
        dataframe,
        profile,
        growth_profile,
    )

    print(
        "\nConstrucción finalizada correctamente."
    )


if __name__ == "__main__":
    main()