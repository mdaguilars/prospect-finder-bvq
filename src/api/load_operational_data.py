"""
Carga de datos operativos de Prospect Finder BVQ a PostgreSQL.

Orden de carga
--------------
1. operational_prospects
2. issuer_similarity_summary
3. issuer_similarity_matches

Características
---------------
- Lee los artefactos generados por los motores v10.
- Carga por bloques para evitar consumo excesivo de memoria.
- Valida columnas antes de insertar.
- Respeta relaciones y llaves foráneas.
- Evita cargas duplicadas.
- Permite recargar deliberadamente usando --replace.
- Verifica las cantidades finales en PostgreSQL.

Uso normal:
    python -m src.api.load_operational_data

Recarga completa:
    python -m src.api.load_operational_data --replace
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import text

from src.api.core.config import settings
from src.api.core.database import SessionLocal
from src.api.core.database import engine
from src.api.models.prospect import IssuerSimilarityMatch
from src.api.models.prospect import IssuerSimilaritySummary
from src.api.models.prospect import OperationalProspect


# ============================================================
# CONFIGURACIÓN
# ============================================================

CHUNK_SIZE = 5_000

RANKING_PATH = (
    settings.processed_data_dir
    / "v10_operational_ranking_2024_05_01.csv.gz"
)

SIMILARITY_SUMMARY_PATH = (
    settings.processed_data_dir
    / "v10_issuer_similarity_summary_2024_05_01.csv.gz"
)

SIMILARITY_MATCHES_PATH = (
    settings.processed_data_dir
    / "v10_issuer_similarity_matches_2024_05_01.csv.gz"
)


# ============================================================
# COLUMNAS DESTINO
# ============================================================

PROSPECT_COLUMNS = [
    "expediente_key",
    "ruc",
    "nombre",
    "anio",
    "fecha_decision",
    "tipo_compania",
    "provincia",
    "ranking",
    "score_afinidad",
    "percentil_ranking",
    "n_features_disponibles",
    "pct_features_disponibles",
    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",
    "fin_ratio_patrimonio_activos",
    "fin_roa",
    "fin_margen_neto",
    "fin_rotacion_activos",
    "fin_roe",
    "fin_crecimiento_activos",
    "fin_crecimiento_patrimonio",
    "fin_crecimiento_ventas",
    "fin_crecimiento_empleados",
    "modelo",
    "configuracion_modelo",
]

SUMMARY_COLUMNS = [
    "expediente_key",
    "comparables_disponibles",
    "similitud_emisor_top1",
    "similitud_emisores_top5_promedio",
    "distancia_emisor_top1",
    "n_emisores_comparados",
    "estado_similitud",
    "metodologia_similitud",
]

MATCH_COLUMNS = [
    "expediente_key",
    "ranking_v10",
    "score_afinidad",
    "orden_comparable",
    "similitud",
    "distancia_percentiles",
    "emisor_expediente_key",
    "emisor_ruc",
    "emisor_nombre",
    "emisor_anio_perfil",
    "emisor_fecha_decision_perfil",
    "emisor_fecha_primera_inscripcion",
    "emisor_tipo_compania",
    "emisor_provincia",
    "mismo_tipo_compania",
]


# ============================================================
# RENOMBRES DESDE CSV
# ============================================================

PROSPECT_RENAME = {
    "EXPEDIENTE_KEY": "expediente_key",
    "RUC": "ruc",
    "NOMBRE": "nombre",
    "ANIO": "anio",
}

SUMMARY_RENAME = {
    "EXPEDIENTE_KEY": "expediente_key",
}

MATCH_RENAME = {
    "EXPEDIENTE_KEY": "expediente_key",
    "emisor_EXPEDIENTE_KEY": "emisor_expediente_key",
    "emisor_RUC": "emisor_ruc",
    "emisor_NOMBRE": "emisor_nombre",
    "emisor_ANIO_perfil": "emisor_anio_perfil",
}


# ============================================================
# UTILIDADES
# ============================================================

def validar_archivo(
    path: Path,
) -> None:
    """
    Comprueba que exista un archivo requerido.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"No existe el archivo requerido:\n{path}"
        )


def validar_archivos() -> None:
    """
    Comprueba los tres artefactos necesarios.
    """

    validar_archivo(
        RANKING_PATH
    )

    validar_archivo(
        SIMILARITY_SUMMARY_PATH
    )

    validar_archivo(
        SIMILARITY_MATCHES_PATH
    )


def validar_columnas(
    dataframe: pd.DataFrame,
    required_columns: list[str],
    source_name: str,
) -> None:
    """
    Comprueba que el DataFrame contenga todas las
    columnas necesarias para una tabla destino.
    """

    missing = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing:
        raise ValueError(
            f"{source_name} no contiene las columnas "
            f"requeridas:\n{missing}"
        )


def normalizar_booleano(
    serie: pd.Series,
) -> pd.Series:
    """
    Convierte diferentes representaciones a bool.
    """

    if pd.api.types.is_bool_dtype(
        serie
    ):
        return serie.astype(
            bool
        )

    mapping = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "yes": True,
        "no": False,
    }

    normalized = (
        serie
        .astype(
            "string"
        )
        .str.strip()
        .str.lower()
        .map(
            mapping
        )
    )

    if normalized.isna().any():

        invalid = (
            serie.loc[
                normalized.isna()
            ]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "Se encontraron valores booleanos "
            f"no reconocidos: {invalid}"
        )

    return normalized.astype(
        bool
    )


def convertir_fecha(
    serie: pd.Series,
    column_name: str,
) -> pd.Series:
    """
    Convierte una columna a objetos date.
    """

    converted = pd.to_datetime(
        serie,
        errors="coerce",
    )

    invalid = (
        converted.isna()
        &
        serie.notna()
    )

    if invalid.any():

        examples = (
            serie.loc[
                invalid
            ]
            .head(
                10
            )
            .tolist()
        )

        raise ValueError(
            f"Fechas inválidas en {column_name}: "
            f"{examples}"
        )

    return converted.dt.date


# ============================================================
# ESTADO ACTUAL DE POSTGRESQL
# ============================================================

def obtener_conteos_actuales() -> dict[str, int]:
    """
    Consulta las cantidades actuales de las tres tablas.
    """

    with SessionLocal() as session:

        prospects = session.scalar(
            select(
                func.count()
            ).select_from(
                OperationalProspect
            )
        )

        summaries = session.scalar(
            select(
                func.count()
            ).select_from(
                IssuerSimilaritySummary
            )
        )

        matches = session.scalar(
            select(
                func.count()
            ).select_from(
                IssuerSimilarityMatch
            )
        )

    return {
        "operational_prospects":
            int(
                prospects
                or 0
            ),
        "issuer_similarity_summary":
            int(
                summaries
                or 0
            ),
        "issuer_similarity_matches":
            int(
                matches
                or 0
            ),
    }


def validar_base_vacia(
    replace: bool,
) -> None:
    """
    Evita duplicar información accidentalmente.

    Si --replace está habilitado, elimina los datos
    existentes respetando las relaciones.
    """

    counts = (
        obtener_conteos_actuales()
    )

    total = sum(
        counts.values()
    )

    print(
        "\nEstado actual de PostgreSQL:"
    )

    for table_name, count in (
        counts.items()
    ):
        print(
            f"  {table_name}: "
            f"{count:,}"
        )

    if total == 0:
        return

    if not replace:
        raise RuntimeError(
            "\nLas tablas ya contienen información.\n"
            "La carga fue cancelada para evitar "
            "duplicados.\n"
            "Si realmente desea reconstruirlas, use:\n\n"
            "python -m src.api.load_operational_data "
            "--replace"
        )

    print(
        "\n--replace activado."
    )

    print(
        "Eliminando datos existentes..."
    )

    with engine.begin() as connection:

        connection.execute(
            text(
                """
                TRUNCATE TABLE
                    issuer_similarity_matches,
                    issuer_similarity_summary,
                    operational_prospects
                RESTART IDENTITY
                CASCADE
                """
            )
        )

    print(
        "Datos anteriores eliminados."
    )


# ============================================================
# PREPARACIÓN DE PROSPECTOS
# ============================================================

def preparar_prospectos(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Adapta columnas del ranking operativo al esquema SQL.
    """

    dataframe = dataframe.rename(
        columns=PROSPECT_RENAME
    )

    validar_columnas(
        dataframe,
        PROSPECT_COLUMNS,
        "Ranking operativo",
    )

    dataframe = dataframe[
        PROSPECT_COLUMNS
    ].copy()

    dataframe[
        "fecha_decision"
    ] = convertir_fecha(
        dataframe[
            "fecha_decision"
        ],
        "fecha_decision",
    )

    if dataframe[
        "expediente_key"
    ].isna().any():
        raise ValueError(
            "Existen prospectos sin expediente_key."
        )

    if dataframe[
        "ranking"
    ].isna().any():
        raise ValueError(
            "Existen prospectos sin ranking."
        )

    return dataframe


# ============================================================
# PREPARACIÓN DE RESUMEN DE SIMILITUD
# ============================================================

def preparar_resumen(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Adapta el resumen de similitud al esquema SQL.
    """

    dataframe = dataframe.rename(
        columns=SUMMARY_RENAME
    )

    validar_columnas(
        dataframe,
        SUMMARY_COLUMNS,
        "Resumen de similitud",
    )

    dataframe = dataframe[
        SUMMARY_COLUMNS
    ].copy()

    dataframe[
        "comparables_disponibles"
    ] = normalizar_booleano(
        dataframe[
            "comparables_disponibles"
        ]
    )

    if dataframe[
        "expediente_key"
    ].isna().any():
        raise ValueError(
            "Existen resúmenes sin expediente_key."
        )

    return dataframe


# ============================================================
# PREPARACIÓN DE MATCHES
# ============================================================

def preparar_matches(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Adapta relaciones prospecto-emisor al esquema SQL.
    """

    dataframe = dataframe.rename(
        columns=MATCH_RENAME
    )

    validar_columnas(
        dataframe,
        MATCH_COLUMNS,
        "Comparables históricos",
    )

    dataframe = dataframe[
        MATCH_COLUMNS
    ].copy()

    dataframe[
        "mismo_tipo_compania"
    ] = normalizar_booleano(
        dataframe[
            "mismo_tipo_compania"
        ]
    )

    dataframe[
        "emisor_fecha_decision_perfil"
    ] = convertir_fecha(
        dataframe[
            "emisor_fecha_decision_perfil"
        ],
        "emisor_fecha_decision_perfil",
    )

    dataframe[
        "emisor_fecha_primera_inscripcion"
    ] = convertir_fecha(
        dataframe[
            "emisor_fecha_primera_inscripcion"
        ],
        "emisor_fecha_primera_inscripcion",
    )

    if dataframe[
        "expediente_key"
    ].isna().any():
        raise ValueError(
            "Existen comparables sin expediente_key."
        )

    if dataframe[
        "orden_comparable"
    ].isna().any():
        raise ValueError(
            "Existen comparables sin orden."
        )

    return dataframe


# ============================================================
# CARGA POR BLOQUES
# ============================================================

def cargar_csv_en_tabla(
    *,
    path: Path,
    table_name: str,
    prepare_function,
    rename_map: dict[str, str],
    required_columns: list[str],
) -> int:
    """
    Lee un CSV comprimido por bloques y lo carga
    utilizando pandas.to_sql sobre el esquema existente.
    """

    total_inserted = 0

    print(
        f"\nCargando {table_name}..."
    )

    reader = pd.read_csv(
        path,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    )

    for chunk_number, chunk in enumerate(
        reader,
        start=1,
    ):

        prepared = prepare_function(
            chunk
        )

        if prepared.empty:
            continue

        prepared.to_sql(
            name=table_name,
            con=engine,
            if_exists="append",
            index=False,
            method=None,
            chunksize=CHUNK_SIZE,
        )

        total_inserted += len(
            prepared
        )

        print(
            f"  bloque {chunk_number:>3}: "
            f"{total_inserted:,} filas acumuladas",
            end="\r",
        )

    print()

    print(
        f"  Total cargado: "
        f"{total_inserted:,}"
    )

    return total_inserted


# ============================================================
# VALIDACIÓN FINAL
# ============================================================

def validar_carga_final(
    expected_prospects: int,
    expected_summaries: int,
    expected_matches: int,
) -> None:
    """
    Comprueba que PostgreSQL contenga exactamente
    las cantidades cargadas.
    """

    counts = (
        obtener_conteos_actuales()
    )

    expected = {
        "operational_prospects":
            expected_prospects,
        "issuer_similarity_summary":
            expected_summaries,
        "issuer_similarity_matches":
            expected_matches,
    }

    print(
        "\nValidación final:"
    )

    errors = []

    for table_name, expected_count in (
        expected.items()
    ):

        actual_count = counts[
            table_name
        ]

        status = (
            "OK"
            if actual_count
            == expected_count
            else "ERROR"
        )

        print(
            f"  {table_name}: "
            f"{actual_count:,} "
            f"(esperado {expected_count:,}) "
            f"[{status}]"
        )

        if actual_count != expected_count:

            errors.append(
                (
                    table_name,
                    expected_count,
                    actual_count,
                )
            )

    if errors:
        raise RuntimeError(
            "La validación final encontró "
            f"diferencias: {errors}"
        )


# ============================================================
# ARGUMENTOS
# ============================================================

def parse_arguments() -> argparse.Namespace:
    """
    Procesa parámetros de línea de comandos.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Carga artefactos operativos de "
            "Prospect Finder BVQ a PostgreSQL."
        )
    )

    parser.add_argument(
        "--replace",
        action="store_true",
        help=(
            "Elimina y reconstruye los datos existentes."
        ),
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """
    Ejecuta la carga completa.
    """

    args = (
        parse_arguments()
    )

    print(
        "\n"
        "================================================="
    )

    print(
        "PROSPECT FINDER BVQ"
    )

    print(
        "Carga operativa a PostgreSQL"
    )

    print(
        "================================================="
    )

    print(
        f"\nBase de datos: "
        f"{engine.url.database}"
    )

    print(
        f"Servidor: "
        f"{engine.url.host}:"
        f"{engine.url.port}"
    )

    validar_archivos()

    validar_base_vacia(
        replace=args.replace
    )

    # --------------------------------------------------------
    # PROSPECTOS
    # --------------------------------------------------------

    prospects_loaded = (
        cargar_csv_en_tabla(
            path=RANKING_PATH,
            table_name=(
                OperationalProspect
                .__tablename__
            ),
            prepare_function=(
                preparar_prospectos
            ),
            rename_map=(
                PROSPECT_RENAME
            ),
            required_columns=(
                PROSPECT_COLUMNS
            ),
        )
    )

    # --------------------------------------------------------
    # RESUMEN DE SIMILITUD
    # --------------------------------------------------------

    summaries_loaded = (
        cargar_csv_en_tabla(
            path=SIMILARITY_SUMMARY_PATH,
            table_name=(
                IssuerSimilaritySummary
                .__tablename__
            ),
            prepare_function=(
                preparar_resumen
            ),
            rename_map=(
                SUMMARY_RENAME
            ),
            required_columns=(
                SUMMARY_COLUMNS
            ),
        )
    )

    # --------------------------------------------------------
    # COMPARABLES
    # --------------------------------------------------------

    matches_loaded = (
        cargar_csv_en_tabla(
            path=SIMILARITY_MATCHES_PATH,
            table_name=(
                IssuerSimilarityMatch
                .__tablename__
            ),
            prepare_function=(
                preparar_matches
            ),
            rename_map=(
                MATCH_RENAME
            ),
            required_columns=(
                MATCH_COLUMNS
            ),
        )
    )

    # --------------------------------------------------------
    # VALIDACIÓN
    # --------------------------------------------------------

    validar_carga_final(
        expected_prospects=(
            prospects_loaded
        ),
        expected_summaries=(
            summaries_loaded
        ),
        expected_matches=(
            matches_loaded
        ),
    )

    print(
        "\n"
        "================================================="
    )

    print(
        "CARGA COMPLETADA CORRECTAMENTE"
    )

    print(
        "================================================="
    )

    print(
        f"\nProspectos: "
        f"{prospects_loaded:,}"
    )

    print(
        f"Resúmenes de similitud: "
        f"{summaries_loaded:,}"
    )

    print(
        f"Comparables históricos: "
        f"{matches_loaded:,}"
    )

    print(
        "\nPostgreSQL quedó listo para ser "
        "consultado por FastAPI."
    )


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    main()