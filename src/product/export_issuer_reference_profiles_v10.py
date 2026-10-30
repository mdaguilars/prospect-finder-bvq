"""
Exporta los perfiles históricos de emisores utilizados por el
motor de similitud de Prospect Finder BVQ v10.

Objetivo
--------
Convertir el archivo de referencia generado originalmente por:

    src/product/build_issuer_similarity_v10.py

en un artefacto operacional dentro de data/processed que pueda
ser cargado posteriormente a PostgreSQL.

Este proceso NO:

- recalcula similitudes;
- modifica el ranking;
- modifica el modelo v10;
- modifica los percentiles;
- modifica los perfiles históricos seleccionados.

Únicamente valida y copia los 272 perfiles históricos ya
construidos por el pipeline v10.

Salida
------
data/processed/
v10_issuer_reference_profiles_2024_05_01.csv.gz
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


INPUT_REFERENCE = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "v10"
    / "product"
    / "v10_issuer_reference_profiles_2024_05_01.csv"
)


OUTPUT_REFERENCE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "v10_issuer_reference_profiles_2024_05_01.csv.gz"
)


EXPECTED_REFERENCE_COUNT = 272


# ============================================================
# VARIABLES DEL MOTOR DE SIMILITUD
# ============================================================

SIMILARITY_FEATURES = [
    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",
    "fin_ratio_patrimonio_activos",
    "fin_roa",
    "fin_rotacion_activos",
]


PERCENTILE_FEATURES = [
    f"pct__{column}"
    for column in SIMILARITY_FEATURES
]


# ============================================================
# COLUMNAS ESPERADAS
# ============================================================

IDENTIFICATION_COLUMNS = [
    "ANIO",
    "EXPEDIENTE_KEY",
    "RUC",
    "NOMBRE",
]


CONTEXT_COLUMNS = [
    "tipo_compania",
    "provincia",
]


TEMPORAL_COLUMNS = [
    "fecha_decision",
    "fecha_primera_inscripcion",
    "dias_hasta_inscripcion",
]


REQUIRED_COLUMNS = (
    IDENTIFICATION_COLUMNS
    + CONTEXT_COLUMNS
    + TEMPORAL_COLUMNS
    + SIMILARITY_FEATURES
    + PERCENTILE_FEATURES
)


# ============================================================
# VALIDACIONES
# ============================================================

def validar_archivo_entrada() -> None:
    """
    Verifica que exista el archivo de referencia construido
    previamente por el motor de similitud v10.
    """

    if not INPUT_REFERENCE.exists():
        raise FileNotFoundError(
            "\nNo se encontró el archivo de perfiles históricos:\n\n"
            f"{INPUT_REFERENCE}\n\n"
            "Este archivo debe existir porque fue generado por "
            "build_issuer_similarity_v10.py."
        )


def validar_columnas(
    dataframe: pd.DataFrame,
) -> None:
    """
    Verifica que estén presentes todas las columnas necesarias
    para preservar la definición original del perfil histórico.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in dataframe.columns
    ]

    if missing_columns:
        formatted_columns = "\n".join(
            f"  - {column}"
            for column in missing_columns
        )

        raise ValueError(
            "\nEl archivo de referencia no contiene todas las "
            "columnas esperadas.\n\n"
            "Columnas faltantes:\n"
            f"{formatted_columns}\n"
        )


def validar_expedientes(
    dataframe: pd.DataFrame,
) -> None:
    """
    Valida que EXPEDIENTE_KEY exista y no tenga duplicados.

    Cada fila debe representar exactamente un perfil histórico
    seleccionado para un emisor.
    """

    if dataframe["EXPEDIENTE_KEY"].isna().any():
        raise ValueError(
            "Existen perfiles históricos sin EXPEDIENTE_KEY."
        )

    duplicated = dataframe[
        dataframe["EXPEDIENTE_KEY"].duplicated(
            keep=False
        )
    ]

    if not duplicated.empty:
        duplicated_values = (
            duplicated["EXPEDIENTE_KEY"]
            .astype(str)
            .unique()
            .tolist()
        )

        raise ValueError(
            "Se encontraron EXPEDIENTE_KEY duplicados en los "
            "perfiles históricos:\n"
            + "\n".join(
                f"  - {value}"
                for value in duplicated_values[:20]
            )
        )


def validar_variables_similitud(
    dataframe: pd.DataFrame,
) -> None:
    """
    Los 272 perfiles efectivos de referencia fueron definidos
    porque cuentan con información completa en las siete
    variables utilizadas por el motor de similitud.

    Por tanto, ninguna de estas variables debe ser nula.
    """

    null_counts = (
        dataframe[
            SIMILARITY_FEATURES
        ]
        .isna()
        .sum()
    )

    columns_with_nulls = (
        null_counts[
            null_counts > 0
        ]
    )

    if not columns_with_nulls.empty:
        detail = "\n".join(
            (
                f"  - {column}: "
                f"{int(count)} valores nulos"
            )
            for column, count
            in columns_with_nulls.items()
        )

        raise ValueError(
            "\nSe encontraron valores faltantes en variables "
            "utilizadas para similitud:\n"
            f"{detail}\n"
        )


def validar_percentiles(
    dataframe: pd.DataFrame,
) -> None:
    """
    Verifica que los percentiles utilizados para la distancia
    estén dentro del intervalo [0, 1].
    """

    for column in PERCENTILE_FEATURES:
        series = dataframe[column]

        if series.isna().any():
            raise ValueError(
                f"La columna {column} contiene valores nulos."
            )

        invalid = series[
            (series < 0)
            | (series > 1)
        ]

        if not invalid.empty:
            raise ValueError(
                f"La columna {column} contiene percentiles "
                "fuera del intervalo [0, 1]."
            )


def validar_fechas(
    dataframe: pd.DataFrame,
) -> None:
    """
    Verifica consistencia temporal.

    El perfil financiero utilizado como referencia debe
    corresponder a información conocida antes de la primera
    inscripción del emisor.
    """

    fecha_decision = pd.to_datetime(
        dataframe["fecha_decision"],
        errors="coerce",
    )

    fecha_inscripcion = pd.to_datetime(
        dataframe["fecha_primera_inscripcion"],
        errors="coerce",
    )

    if fecha_decision.isna().any():
        raise ValueError(
            "Existen valores inválidos en fecha_decision."
        )

    if fecha_inscripcion.isna().any():
        raise ValueError(
            "Existen valores inválidos en "
            "fecha_primera_inscripcion."
        )

    invalid_temporal = dataframe[
        fecha_decision
        >= fecha_inscripcion
    ]

    if not invalid_temporal.empty:
        raise ValueError(
            "Se encontraron perfiles cuya fecha de decisión "
            "no es anterior a la primera inscripción."
        )


# ============================================================
# PREPARACIÓN
# ============================================================

def cargar_referencia() -> pd.DataFrame:
    """
    Carga el archivo original generado por el pipeline.
    """

    dataframe = pd.read_csv(
        INPUT_REFERENCE,
        low_memory=False,
    )

    return dataframe


def preparar_referencia(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepara el dataset para uso operacional sin modificar
    los valores calculados originalmente.
    """

    output = dataframe[
        REQUIRED_COLUMNS
    ].copy()


    # --------------------------------------------------------
    # IDENTIFICADORES
    # --------------------------------------------------------

    output["EXPEDIENTE_KEY"] = pd.to_numeric(
        output["EXPEDIENTE_KEY"],
        errors="raise",
    ).astype("int64")


    output["ANIO"] = pd.to_numeric(
        output["ANIO"],
        errors="raise",
    ).astype("int64")


    # --------------------------------------------------------
    # VARIABLES NUMÉRICAS
    # --------------------------------------------------------

    numeric_columns = (
        SIMILARITY_FEATURES
        + PERCENTILE_FEATURES
        + [
            "dias_hasta_inscripcion",
        ]
    )


    for column in numeric_columns:
        output[column] = pd.to_numeric(
            output[column],
            errors="coerce",
        )


    # --------------------------------------------------------
    # FECHAS
    # --------------------------------------------------------

    for column in [
        "fecha_decision",
        "fecha_primera_inscripcion",
    ]:
        output[column] = pd.to_datetime(
            output[column],
            errors="raise",
        ).dt.strftime(
            "%Y-%m-%d"
        )


    # --------------------------------------------------------
    # TEXTO
    # --------------------------------------------------------

    for column in [
        "RUC",
        "NOMBRE",
        "tipo_compania",
        "provincia",
    ]:
        output[column] = (
            output[column]
            .astype("string")
            .str.strip()
        )


    # --------------------------------------------------------
    # ORDEN ESTABLE
    # --------------------------------------------------------

    output = (
        output
        .sort_values(
            by=[
                "EXPEDIENTE_KEY",
            ],
            kind="stable",
        )
        .reset_index(
            drop=True
        )
    )


    return output


# ============================================================
# EXPORTACIÓN
# ============================================================

def exportar_referencia(
    dataframe: pd.DataFrame,
) -> None:
    """
    Guarda el dataset como CSV comprimido gzip.
    """

    OUTPUT_REFERENCE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    dataframe.to_csv(
        OUTPUT_REFERENCE,
        index=False,
        compression="gzip",
    )


# ============================================================
# VALIDACIÓN DE SALIDA
# ============================================================

def validar_salida() -> pd.DataFrame:
    """
    Reabre el archivo recién generado para comprobar que
    pueda ser utilizado posteriormente por el loader de
    PostgreSQL.
    """

    if not OUTPUT_REFERENCE.exists():
        raise FileNotFoundError(
            "El archivo de salida no fue generado."
        )


    output = pd.read_csv(
        OUTPUT_REFERENCE,
        low_memory=False,
    )


    validar_columnas(
        output
    )

    validar_expedientes(
        output
    )

    validar_variables_similitud(
        output
    )

    validar_percentiles(
        output
    )

    validar_fechas(
        output
    )


    return output


# ============================================================
# RESUMEN
# ============================================================

def imprimir_resumen(
    dataframe: pd.DataFrame,
) -> None:
    """
    Muestra controles básicos para confirmar el resultado.
    """

    print()
    print("=" * 72)
    print(
        "PROSPECT FINDER BVQ"
    )
    print(
        "EXPORTACIÓN DE PERFILES HISTÓRICOS DE EMISORES"
    )
    print("=" * 72)
    print()


    print(
        "Archivo fuente:"
    )
    print(
        INPUT_REFERENCE
    )
    print()


    print(
        "Archivo generado:"
    )
    print(
        OUTPUT_REFERENCE
    )
    print()


    print(
        "Perfiles históricos exportados:"
    )
    print(
        f"{len(dataframe):,}"
        .replace(
            ",",
            ".",
        )
    )
    print()


    print(
        "Expedientes únicos:"
    )
    print(
        f"{dataframe['EXPEDIENTE_KEY'].nunique():,}"
        .replace(
            ",",
            ".",
        )
    )
    print()


    print(
        "Variables financieras utilizadas:"
    )

    for column in SIMILARITY_FEATURES:
        print(
            f"  - {column}"
        )

    print()


    print(
        "Percentiles conservados:"
    )

    for column in PERCENTILE_FEATURES:
        print(
            f"  - {column}"
        )

    print()


    if (
        len(dataframe)
        == EXPECTED_REFERENCE_COUNT
    ):
        print(
            "VALIDACIÓN DE CONTEO: OK"
        )
        print(
            f"Se encontraron los "
            f"{EXPECTED_REFERENCE_COUNT} "
            "perfiles históricos esperados."
        )
    else:
        print(
            "ADVERTENCIA DE CONTEO"
        )
        print(
            f"Se esperaban "
            f"{EXPECTED_REFERENCE_COUNT} "
            "perfiles y se encontraron "
            f"{len(dataframe)}."
        )


    print()
    print("=" * 72)
    print(
        "EXPORTACIÓN COMPLETADA"
    )
    print("=" * 72)
    print()


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    validar_archivo_entrada()


    reference = cargar_referencia()


    validar_columnas(
        reference
    )


    reference = preparar_referencia(
        reference
    )


    validar_expedientes(
        reference
    )


    validar_variables_similitud(
        reference
    )


    validar_percentiles(
        reference
    )


    validar_fechas(
        reference
    )


    exportar_referencia(
        reference
    )


    output = validar_salida()


    imprimir_resumen(
        output
    )


if __name__ == "__main__":
    main()