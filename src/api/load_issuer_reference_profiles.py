"""
Carga operacional de perfiles históricos de emisores.

Prospect Finder BVQ
-------------------

Carga en PostgreSQL los perfiles financieros históricos utilizados
por el motor de similitud v10.

Entrada:
    data/processed/
    v10_issuer_reference_profiles_2024_05_01.csv.gz

Tabla:
    issuer_reference_profiles

Registros esperados:
    272

Este proceso NO modifica:
- operational_prospects
- issuer_similarity_summary
- issuer_similarity_matches
- ranking
- scores
- similitudes
- modelo v10
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import text

from src.api.core.database import engine
from src.api.models.prospect import IssuerReferenceProfile


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "v10_issuer_reference_profiles_2024_05_01.csv.gz"
)

EXPECTED_ROWS = 272

TABLE_NAME = "issuer_reference_profiles"


# ============================================================
# COLUMNAS
# ============================================================

COLUMN_MAPPING = {
    "ANIO": "anio",
    "EXPEDIENTE_KEY": "expediente_key",
    "RUC": "ruc",
    "NOMBRE": "nombre",
    "tipo_compania": "tipo_compania",
    "provincia": "provincia",
    "fecha_decision": "fecha_decision",
    "fecha_primera_inscripcion": "fecha_primera_inscripcion",
    "dias_hasta_inscripcion": "dias_hasta_inscripcion",
    "activos_final": "activos_final",
    "patrimonio_final": "patrimonio_final",
    "bi_ingresos_ventas": "bi_ingresos_ventas",
    "bi_n_empleados": "bi_n_empleados",
    "fin_ratio_patrimonio_activos": "fin_ratio_patrimonio_activos",
    "fin_roa": "fin_roa",
    "fin_rotacion_activos": "fin_rotacion_activos",
    "pct__activos_final": "pct__activos_final",
    "pct__patrimonio_final": "pct__patrimonio_final",
    "pct__bi_ingresos_ventas": "pct__bi_ingresos_ventas",
    "pct__bi_n_empleados": "pct__bi_n_empleados",
    "pct__fin_ratio_patrimonio_activos": (
        "pct__fin_ratio_patrimonio_activos"
    ),
    "pct__fin_roa": "pct__fin_roa",
    "pct__fin_rotacion_activos": "pct__fin_rotacion_activos",
}

REQUIRED_SOURCE_COLUMNS = list(COLUMN_MAPPING.keys())

FINANCIAL_COLUMNS = [
    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",
    "fin_ratio_patrimonio_activos",
    "fin_roa",
    "fin_rotacion_activos",
]

PERCENTILE_COLUMNS = [
    "pct__activos_final",
    "pct__patrimonio_final",
    "pct__bi_ingresos_ventas",
    "pct__bi_n_empleados",
    "pct__fin_ratio_patrimonio_activos",
    "pct__fin_roa",
    "pct__fin_rotacion_activos",
]


# ============================================================
# UTILIDADES
# ============================================================

def section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)
    print()


def format_count(value: int) -> str:
    return f"{value:,}".replace(",", ".")


# ============================================================
# ARCHIVO DE ENTRADA
# ============================================================

def validate_input_file() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "\nNo se encontró el archivo de entrada:\n\n"
            f"{INPUT_FILE}\n\n"
            "Ejecute primero:\n\n"
            "python -m "
            "src.product.export_issuer_reference_profiles_v10"
        )


def load_input_file() -> pd.DataFrame:
    return pd.read_csv(
        INPUT_FILE,
        compression="gzip",
        dtype={
            "RUC": "string",
            "NOMBRE": "string",
            "tipo_compania": "string",
            "provincia": "string",
        },
        low_memory=False,
    )


def validate_columns(dataframe: pd.DataFrame) -> None:
    missing_columns = [
        column
        for column in REQUIRED_SOURCE_COLUMNS
        if column not in dataframe.columns
    ]

    if missing_columns:
        detail = "\n".join(
            f"  - {column}"
            for column in missing_columns
        )

        raise ValueError(
            "\nFaltan columnas requeridas en el archivo:\n"
            f"{detail}\n"
        )


def validate_source_rows(dataframe: pd.DataFrame) -> None:
    row_count = len(dataframe)

    if row_count != EXPECTED_ROWS:
        raise ValueError(
            "\nConteo de perfiles inesperado.\n\n"
            f"Esperados: {EXPECTED_ROWS}\n"
            f"Encontrados: {row_count}\n"
        )

    if dataframe["EXPEDIENTE_KEY"].isna().any():
        raise ValueError(
            "Existen registros sin EXPEDIENTE_KEY."
        )

    duplicated = dataframe[
        "EXPEDIENTE_KEY"
    ].duplicated(
        keep=False
    )

    if duplicated.any():
        duplicate_values = (
            dataframe.loc[
                duplicated,
                "EXPEDIENTE_KEY",
            ]
            .astype(str)
            .unique()
            .tolist()
        )

        raise ValueError(
            "\nExisten EXPEDIENTE_KEY duplicados:\n"
            + "\n".join(
                f"  - {value}"
                for value in duplicate_values[:20]
            )
        )

    if dataframe["dias_hasta_inscripcion"].isna().any():
        raise ValueError(
            "Existen registros sin dias_hasta_inscripcion."
        )

    null_financial = (
        dataframe[
            FINANCIAL_COLUMNS
        ]
        .isna()
        .sum()
    )

    null_financial = null_financial[
        null_financial > 0
    ]

    if not null_financial.empty:
        detail = "\n".join(
            (
                f"  - {column}: "
                f"{int(count)} nulos"
            )
            for column, count
            in null_financial.items()
        )

        raise ValueError(
            "\nExisten valores nulos en las variables "
            "del motor de similitud:\n"
            f"{detail}\n"
        )

    for column in PERCENTILE_COLUMNS:
        series = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

        if series.isna().any():
            raise ValueError(
                f"La columna {column} contiene valores inválidos."
            )

        invalid = (
            (series < 0)
            | (series > 1)
        )

        if invalid.any():
            raise ValueError(
                f"La columna {column} contiene valores "
                "fuera del intervalo [0, 1]."
            )


# ============================================================
# PREPARACIÓN
# ============================================================

def clean_optional_text(
    series: pd.Series,
) -> pd.Series:
    """
    Limpia texto preservando los valores nulos como None.
    """

    cleaned = (
        series
        .astype("string")
        .str.strip()
    )

    cleaned = cleaned.astype(object)

    return cleaned.where(
        pd.notna(cleaned),
        None,
    )


def prepare_dataframe(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    output = (
        dataframe[
            REQUIRED_SOURCE_COLUMNS
        ]
        .rename(
            columns=COLUMN_MAPPING
        )
        .copy()
    )

    # --------------------------------------------------------
    # IDENTIFICADORES
    # --------------------------------------------------------

    output["expediente_key"] = pd.to_numeric(
        output["expediente_key"],
        errors="raise",
    ).astype("int64")

    output["anio"] = pd.to_numeric(
        output["anio"],
        errors="raise",
    ).astype("int64")

    output["dias_hasta_inscripcion"] = pd.to_numeric(
        output["dias_hasta_inscripcion"],
        errors="raise",
    ).astype("int64")

    # --------------------------------------------------------
    # TEXTO
    # --------------------------------------------------------

    for column in [
        "ruc",
        "nombre",
        "tipo_compania",
        "provincia",
    ]:
        output[column] = clean_optional_text(
            output[column]
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
        ).dt.date

    # --------------------------------------------------------
    # VARIABLES FINANCIERAS
    # --------------------------------------------------------

    for column in FINANCIAL_COLUMNS:
        output[column] = pd.to_numeric(
            output[column],
            errors="raise",
        ).astype("float64")

    # --------------------------------------------------------
    # PERCENTILES
    # --------------------------------------------------------

    for column in PERCENTILE_COLUMNS:
        output[column] = pd.to_numeric(
            output[column],
            errors="raise",
        ).astype("float64")

    # --------------------------------------------------------
    # ORDEN ESTABLE
    # --------------------------------------------------------

    output = (
        output
        .sort_values(
            by="expediente_key",
            kind="stable",
        )
        .reset_index(
            drop=True
        )
    )

    return output


# ============================================================
# POSTGRESQL
# ============================================================

def validate_existing_operational_tables() -> None:
    """
    Comprueba que las tres tablas principales existentes
    continúen presentes.
    """

    required_tables = [
        "operational_prospects",
        "issuer_similarity_summary",
        "issuer_similarity_matches",
    ]

    sql = text(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = :table_name
        )
        """
    )

    with engine.connect() as connection:
        for table_name in required_tables:
            exists = connection.execute(
                sql,
                {
                    "table_name": table_name,
                },
            ).scalar_one()

            if not exists:
                raise RuntimeError(
                    f"La tabla requerida '{table_name}' "
                    "no existe en PostgreSQL."
                )


def recreate_reference_table() -> None:
    """
    Recrea únicamente issuer_reference_profiles.

    NO modifica las tres tablas operacionales existentes.
    """

    IssuerReferenceProfile.__table__.drop(
        bind=engine,
        checkfirst=True,
    )

    IssuerReferenceProfile.__table__.create(
        bind=engine,
        checkfirst=False,
    )


def dataframe_to_records(
    dataframe: pd.DataFrame,
) -> list[dict]:
    """
    Convierte el DataFrame en registros Python limpios
    para SQLAlchemy.
    """

    records: list[dict] = []

    for row in dataframe.to_dict(
        orient="records"
    ):
        clean_row: dict = {}

        for key, value in row.items():
            if pd.isna(value):
                clean_row[key] = None
            elif hasattr(value, "item"):
                clean_row[key] = value.item()
            else:
                clean_row[key] = value

        records.append(
            clean_row
        )

    return records


def load_reference_profiles(
    dataframe: pd.DataFrame,
) -> None:
    records = dataframe_to_records(
        dataframe
    )

    if len(records) != EXPECTED_ROWS:
        raise RuntimeError(
            "El número de registros preparados "
            "no coincide con el esperado."
        )

    with engine.begin() as connection:
        connection.execute(
            IssuerReferenceProfile
            .__table__
            .insert(),
            records,
        )


# ============================================================
# VALIDACIONES POST-CARGA
# ============================================================

def get_database_count() -> int:
    with engine.connect() as connection:
        value = connection.execute(
            select(
                func.count()
            ).select_from(
                IssuerReferenceProfile
            )
        ).scalar_one()

    return int(value)


def get_database_unique_count() -> int:
    with engine.connect() as connection:
        value = connection.execute(
            select(
                func.count(
                    func.distinct(
                        IssuerReferenceProfile
                        .expediente_key
                    )
                )
            )
        ).scalar_one()

    return int(value)


def validate_database_rows() -> None:
    rows = get_database_count()

    unique_rows = get_database_unique_count()

    if rows != EXPECTED_ROWS:
        raise RuntimeError(
            "\nLa carga terminó con un conteo incorrecto.\n\n"
            f"Esperados: {EXPECTED_ROWS}\n"
            f"Cargados: {rows}\n"
        )

    if unique_rows != EXPECTED_ROWS:
        raise RuntimeError(
            "\nEl número de expedientes únicos es incorrecto.\n\n"
            f"Esperados: {EXPECTED_ROWS}\n"
            f"Únicos: {unique_rows}\n"
        )


def validate_similarity_match_coverage() -> dict:
    """
    Comprueba que los emisores utilizados por
    issuer_similarity_matches puedan encontrarse
    en issuer_reference_profiles.
    """

    sql = text(
        """
        SELECT
            COUNT(
                DISTINCT m.emisor_expediente_key
            ) AS emisores_en_matches,

            COUNT(
                DISTINCT CASE
                    WHEN r.expediente_key IS NOT NULL
                    THEN m.emisor_expediente_key
                END
            ) AS emisores_con_perfil,

            COUNT(
                DISTINCT CASE
                    WHEN r.expediente_key IS NULL
                    THEN m.emisor_expediente_key
                END
            ) AS emisores_sin_perfil

        FROM issuer_similarity_matches AS m

        LEFT JOIN issuer_reference_profiles AS r
            ON r.expediente_key = m.emisor_expediente_key
        """
    )

    with engine.connect() as connection:
        row = (
            connection.execute(
                sql
            )
            .mappings()
            .one()
        )

    return {
        "emisores_en_matches": int(
            row["emisores_en_matches"] or 0
        ),
        "emisores_con_perfil": int(
            row["emisores_con_perfil"] or 0
        ),
        "emisores_sin_perfil": int(
            row["emisores_sin_perfil"] or 0
        ),
    }


def validate_financial_ranges() -> None:
    """
    Confirma que los siete percentiles estén dentro
    del intervalo [0, 1].
    """

    sql = text(
        """
        SELECT
            MIN(
                pct__activos_final
            ) AS min_activos,

            MAX(
                pct__activos_final
            ) AS max_activos,

            MIN(
                pct__patrimonio_final
            ) AS min_patrimonio,

            MAX(
                pct__patrimonio_final
            ) AS max_patrimonio,

            MIN(
                pct__bi_ingresos_ventas
            ) AS min_ventas,

            MAX(
                pct__bi_ingresos_ventas
            ) AS max_ventas,

            MIN(
                pct__bi_n_empleados
            ) AS min_empleados,

            MAX(
                pct__bi_n_empleados
            ) AS max_empleados,

            MIN(
                pct__fin_ratio_patrimonio_activos
            ) AS min_ratio,

            MAX(
                pct__fin_ratio_patrimonio_activos
            ) AS max_ratio,

            MIN(
                pct__fin_roa
            ) AS min_roa,

            MAX(
                pct__fin_roa
            ) AS max_roa,

            MIN(
                pct__fin_rotacion_activos
            ) AS min_rotacion,

            MAX(
                pct__fin_rotacion_activos
            ) AS max_rotacion

        FROM issuer_reference_profiles
        """
    )

    with engine.connect() as connection:
        row = (
            connection.execute(
                sql
            )
            .mappings()
            .one()
        )

    for key, value in row.items():
        if value is None:
            raise RuntimeError(
                f"El control {key} devolvió NULL."
            )

        numeric_value = float(
            value
        )

        if (
            numeric_value < 0
            or numeric_value > 1
        ):
            raise RuntimeError(
                f"El valor {key}={numeric_value} "
                "está fuera del intervalo [0, 1]."
            )


def validate_null_financial_values() -> None:
    """
    Confirma que PostgreSQL contenga las siete variables
    financieras completas.
    """

    sql = text(
        """
        SELECT COUNT(*) AS registros_invalidos

        FROM issuer_reference_profiles

        WHERE
            activos_final IS NULL
            OR patrimonio_final IS NULL
            OR bi_ingresos_ventas IS NULL
            OR bi_n_empleados IS NULL
            OR fin_ratio_patrimonio_activos IS NULL
            OR fin_roa IS NULL
            OR fin_rotacion_activos IS NULL
        """
    )

    with engine.connect() as connection:
        invalid_rows = connection.execute(
            sql
        ).scalar_one()

    if int(invalid_rows) != 0:
        raise RuntimeError(
            "Existen perfiles históricos con variables "
            "financieras nulas en PostgreSQL."
        )


# ============================================================
# RESUMEN
# ============================================================

def print_summary(
    source: pd.DataFrame,
    coverage: dict,
) -> None:
    section(
        "PROSPECT FINDER BVQ - CARGA COMPLETADA"
    )

    print(
        "Archivo de origen:"
    )
    print(
        INPUT_FILE
    )
    print()

    print(
        "Tabla PostgreSQL:"
    )
    print(
        TABLE_NAME
    )
    print()

    print(
        "Registros del archivo:"
    )
    print(
        format_count(
            len(source)
        )
    )
    print()

    print(
        "Registros cargados:"
    )
    print(
        format_count(
            get_database_count()
        )
    )
    print()

    print(
        "Expedientes únicos:"
    )
    print(
        format_count(
            get_database_unique_count()
        )
    )
    print()

    print(
        "Cobertura frente a issuer_similarity_matches:"
    )

    print(
        "  Emisores distintos utilizados en comparables: "
        + format_count(
            coverage[
                "emisores_en_matches"
            ]
        )
    )

    print(
        "  Emisores con perfil financiero: "
        + format_count(
            coverage[
                "emisores_con_perfil"
            ]
        )
    )

    print(
        "  Emisores sin perfil financiero: "
        + format_count(
            coverage[
                "emisores_sin_perfil"
            ]
        )
    )

    print()

    if (
        coverage[
            "emisores_sin_perfil"
        ] == 0
    ):
        print(
            "COBERTURA DE COMPARABLES: OK"
        )

        print(
            "Todos los emisores utilizados por el motor "
            "de similitud tienen perfil financiero disponible."
        )
    else:
        print(
            "ADVERTENCIA DE COBERTURA"
        )

        print(
            "Existen emisores utilizados en comparables "
            "sin perfil financiero disponible."
        )

    print()

    print(
        "VALIDACIÓN DE TABLA: OK"
    )

    print(
        f"issuer_reference_profiles contiene "
        f"{EXPECTED_ROWS} perfiles históricos."
    )

    print()

    print("=" * 72)
    print(
        "PROCESO FINALIZADO CORRECTAMENTE"
    )
    print("=" * 72)
    print()


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    section(
        "1. VALIDACIÓN DEL ARTEFACTO"
    )

    validate_input_file()

    source = load_input_file()

    validate_columns(
        source
    )

    validate_source_rows(
        source
    )

    print(
        "Archivo de entrada validado correctamente."
    )

    print(
        f"Perfiles encontrados: "
        f"{format_count(len(source))}"
    )


    section(
        "2. PREPARACIÓN DE DATOS"
    )

    prepared = prepare_dataframe(
        source
    )

    print(
        "Datos preparados correctamente."
    )


    section(
        "3. VALIDACIÓN DE POSTGRESQL"
    )

    validate_existing_operational_tables()

    print(
        "Las tres tablas operacionales existentes "
        "están disponibles."
    )


    section(
        "4. CREACIÓN DE issuer_reference_profiles"
    )

    recreate_reference_table()

    print(
        "Tabla issuer_reference_profiles creada."
    )


    section(
        "5. CARGA DE PERFILES"
    )

    load_reference_profiles(
        prepared
    )

    print(
        "Inserción finalizada."
    )


    section(
        "6. VALIDACIONES POST-CARGA"
    )

    validate_database_rows()

    print(
        "Conteo de registros: OK"
    )

    validate_null_financial_values()

    print(
        "Variables financieras: OK"
    )

    validate_financial_ranges()

    print(
        "Percentiles: OK"
    )

    coverage = (
        validate_similarity_match_coverage()
    )

    print(
        "Cobertura de comparables calculada."
    )


    print_summary(
        prepared,
        coverage,
    )


if __name__ == "__main__":
    main()