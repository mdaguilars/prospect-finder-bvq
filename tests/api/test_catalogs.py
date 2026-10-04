"""
Pruebas automáticas de los catálogos operativos
de Prospect Finder BVQ API.

Estas pruebas verifican que:

- se devuelvan las 24 provincias;
- se devuelvan los 9 tipos de compañía;
- los valores estén normalizados;
- los conteos principales coincidan con la base cargada.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.api.core.database import SessionLocal
from src.api.routers.catalogs import get_catalogs


def test_catalogs_structure_and_counts() -> None:
    """
    Valida la estructura general y los conteos
    principales del endpoint de catálogos.
    """

    db: Session = SessionLocal()

    try:
        response = get_catalogs(
            db=db
        )

    finally:
        db.close()

    assert response[
        "metadata"
    ][
        "total_provincias"
    ] == 24

    assert response[
        "metadata"
    ][
        "total_tipos_compania"
    ] == 9

    provincias = {
        item[
            "value"
        ]: item[
            "count"
        ]
        for item in response[
            "provincias"
        ]
    }

    tipos = {
        item[
            "value"
        ]: item[
            "count"
        ]
        for item in response[
            "tipos_compania"
        ]
    }

    assert provincias[
        "PICHINCHA"
    ] == 43_487

    assert provincias[
        "GUAYAS"
    ] == 52_560

    assert tipos[
        "ANÓNIMA"
    ] == 65_769

    assert tipos[
        "SOCIEDAD POR ACCIONES SIMPLIFICADA"
    ] == 41_638

    assert tipos[
        "SUCURSAL EXTRANJERA"
    ] == 722


def test_catalog_values_are_normalized() -> None:
    """
    Verifica que no existan espacios innecesarios
    al inicio, al final o duplicados internamente.
    """

    db: Session = SessionLocal()

    try:
        response = get_catalogs(
            db=db
        )

    finally:
        db.close()

    values = [
        item[
            "value"
        ]
        for item in response[
            "provincias"
        ]
    ]

    values += [
        item[
            "value"
        ]
        for item in response[
            "tipos_compania"
        ]
    ]

    for value in values:

        assert value == value.strip()

        assert "  " not in value