"""
Configuración central de Prospect Finder BVQ API.

La configuración se obtiene principalmente desde variables
de entorno. Los valores definidos aquí corresponden al
entorno local de desarrollo.

No deben almacenarse credenciales productivas en el código.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# RUTAS DEL PROYECTO
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]

ENV_FILE = (
    PROJECT_ROOT
    / ".env"
)

load_dotenv(
    dotenv_path=ENV_FILE,
    override=False,
)


# ============================================================
# UTILIDADES DE CONFIGURACIÓN
# ============================================================

def get_bool(
    variable_name: str,
    default: bool = False,
) -> bool:
    """
    Convierte una variable de entorno a booleano.
    """

    raw_value = os.getenv(
        variable_name
    )

    if raw_value is None:
        return default

    return (
        raw_value
        .strip()
        .lower()
        in {
            "1",
            "true",
            "yes",
            "y",
            "on",
        }
    )


def get_list(
    variable_name: str,
    default: list[str] | None = None,
) -> list[str]:
    """
    Convierte una variable de entorno separada por comas
    a una lista de strings.
    """

    raw_value = os.getenv(
        variable_name
    )

    if raw_value is None:
        return (
            default.copy()
            if default is not None
            else []
        )

    return [
        item.strip()
        for item in raw_value.split(",")
        if item.strip()
    ]


# ============================================================
# SETTINGS
# ============================================================

@dataclass(
    frozen=True
)
class Settings:
    """
    Configuración general de la API.
    """

    # --------------------------------------------------------
    # APLICACIÓN
    # --------------------------------------------------------

    app_name: str = os.getenv(
        "APP_NAME",
        "Prospect Finder BVQ API",
    )

    app_version: str = os.getenv(
        "APP_VERSION",
        "0.1.0",
    )

    environment: str = os.getenv(
        "APP_ENV",
        "development",
    )

    api_prefix: str = os.getenv(
        "API_PREFIX",
        "/api",
    )

    debug: bool = get_bool(
        "DEBUG",
        False,
    )

    evaluator_demo_mode: bool = get_bool(
        "EVALUATOR_DEMO_MODE",
        False,
    )

    # --------------------------------------------------------
    # BASE DE DATOS
    # --------------------------------------------------------

    database_url: str = os.getenv(
        "DATABASE_URL",
        (
            "postgresql+psycopg://"
            "prospect_finder:"
            "prospect_finder@"
            "localhost:5432/"
            "prospect_finder_bvq"
        ),
    )

    database_echo: bool = get_bool(
        "DATABASE_ECHO",
        False,
    )

    # --------------------------------------------------------
    # CORS
    # --------------------------------------------------------

    cors_origins: tuple[str, ...] = tuple(
        get_list(
            "CORS_ORIGINS",
            [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://localhost:5174",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:5174",
            ],
        )
    )

    # --------------------------------------------------------
    # RUTAS DEL PROYECTO
    # --------------------------------------------------------

    project_root: Path = PROJECT_ROOT

    data_dir: Path = (
        PROJECT_ROOT
        / "data"
    )

    processed_data_dir: Path = (
        PROJECT_ROOT
        / "data"
        / "processed"
    )

    reports_dir: Path = (
        PROJECT_ROOT
        / "reports"
    )

    models_dir: Path = (
        PROJECT_ROOT
        / "models"
    )

    # --------------------------------------------------------
    # ARTEFACTOS OPERATIVOS
    # --------------------------------------------------------

    operational_ranking_path: Path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "v10_operational_ranking_2024_05_01.csv.gz"
    )

    issuer_similarity_summary_path: Path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "v10_issuer_similarity_summary_2024_05_01.csv.gz"
    )

    issuer_similarity_matches_path: Path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "v10_issuer_similarity_matches_2024_05_01.csv.gz"
    )

    final_model_path: Path = (
        PROJECT_ROOT
        / "models"
        / "v10"
        / "v10_hgb_financial_c3_final.joblib"
    )

    # --------------------------------------------------------
    # METADATOS DEL MODELO
    # --------------------------------------------------------

    model_name: str = (
        "v10_hgb_financial_c3"
    )

    model_config_id: str = (
        "C3_CONSERVATIVE"
    )

    operational_financial_year: int = 2023

    operational_decision_date: str = (
        "2024-05-01"
    )


# ============================================================
# INSTANCIA GLOBAL
# ============================================================

settings = Settings()
