"""
Conexión a PostgreSQL para Prospect Finder BVQ API.

Este módulo centraliza:

- creación del engine SQLAlchemy;
- manejo de sesiones;
- clase base de modelos ORM;
- dependencia get_db para FastAPI;
- prueba básica de conectividad.

La conexión se obtiene desde settings.database_url.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from src.api.core.config import settings


# ============================================================
# BASE ORM
# ============================================================

class Base(
    DeclarativeBase
):
    """
    Clase base para los modelos SQLAlchemy del proyecto.
    """

    pass


# ============================================================
# ENGINE
# ============================================================

engine: Engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
)


# ============================================================
# SESSION FACTORY
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)


# ============================================================
# DEPENDENCIA FASTAPI
# ============================================================

def get_db() -> Generator[
    Session,
    None,
    None,
]:
    """
    Proporciona una sesión de base de datos por request.

    La sesión se cierra siempre al finalizar la operación.
    """

    database = SessionLocal()

    try:
        yield database

    finally:
        database.close()


# ============================================================
# PRUEBA DE CONECTIVIDAD
# ============================================================

def check_database_connection() -> bool:
    """
    Comprueba si PostgreSQL responde correctamente.

    No crea tablas ni modifica información.
    """

    try:

        with engine.connect() as connection:

            connection.execute(
                text(
                    "SELECT 1"
                )
            )

        return True

    except Exception:

        return False


# ============================================================
# INFORMACIÓN DE CONEXIÓN SEGURA
# ============================================================

def get_database_info() -> dict[str, str]:
    """
    Devuelve información básica de la base sin exponer
    usuario ni contraseña.
    """

    url = engine.url

    return {
        "driver":
            str(
                url.drivername
            ),
        "host":
            str(
                url.host
                or ""
            ),
        "port":
            str(
                url.port
                or ""
            ),
        "database":
            str(
                url.database
                or ""
            ),
    }