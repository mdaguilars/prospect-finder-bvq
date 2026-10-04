"""
Pruebas automáticas del endpoint de salud
de Prospect Finder BVQ API.

Estas pruebas verifican la respuesta lógica del endpoint
sin depender de una conexión real a PostgreSQL.
"""

from __future__ import annotations

from src.api.core.config import settings
from src.api.routers import health


def test_health_check_database_connected(
    monkeypatch,
) -> None:
    """
    Debe devolver estado OK cuando PostgreSQL
    está disponible.
    """

    monkeypatch.setattr(
        health,
        "check_database_connection",
        lambda: True,
    )

    monkeypatch.setattr(
        health,
        "get_database_info",
        lambda: {
            "driver": "postgresql+psycopg",
            "host": "localhost",
            "port": 5432,
            "database": "prospect_finder_bvq",
        },
    )

    response = health.health_check()

    assert response[
        "status"
    ] == "ok"

    assert response[
        "application"
    ] == settings.app_name

    assert response[
        "version"
    ] == settings.app_version

    assert response[
        "environment"
    ] == settings.environment

    assert response[
        "database"
    ][
        "connected"
    ] is True

    assert response[
        "database"
    ][
        "driver"
    ] == "postgresql+psycopg"

    assert response[
        "database"
    ][
        "host"
    ] == "localhost"

    assert response[
        "database"
    ][
        "port"
    ] == 5432

    assert response[
        "database"
    ][
        "database"
    ] == "prospect_finder_bvq"


def test_health_check_database_disconnected(
    monkeypatch,
) -> None:
    """
    Debe devolver estado DEGRADED cuando PostgreSQL
    no está disponible.
    """

    monkeypatch.setattr(
        health,
        "check_database_connection",
        lambda: False,
    )

    monkeypatch.setattr(
        health,
        "get_database_info",
        lambda: {
            "driver": "postgresql+psycopg",
            "host": "localhost",
            "port": 5432,
            "database": "prospect_finder_bvq",
        },
    )

    response = health.health_check()

    assert response[
        "status"
    ] == "degraded"

    assert response[
        "database"
    ][
        "connected"
    ] is False