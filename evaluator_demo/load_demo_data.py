from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEMO_DATABASE_URL = (
    "postgresql+psycopg://"
    "prospect_demo:prospect_demo@"
    "localhost:5434/prospect_finder_demo"
)
os.environ["DATABASE_URL"] = DEMO_DATABASE_URL

from src.api.core.database import Base, engine
import src.api.models.prospect  # noqa: F401

ROOT = Path(__file__).resolve().parent

# ------------------------------------------------------------
# Control de seguridad: nunca escribir fuera de la base demo.
# ------------------------------------------------------------
if (
    engine.url.host not in {"localhost", "127.0.0.1"}
    or engine.url.port != 5434
    or engine.url.database != "prospect_finder_demo"
):
    raise RuntimeError(
        "Carga cancelada: la conexión no corresponde a la base demo."
    )

# ------------------------------------------------------------
# Leer datos sintéticos.
# ------------------------------------------------------------
prospects = pd.read_csv(ROOT / "synthetic_prospects.csv")
comparables = pd.read_csv(ROOT / "synthetic_comparables.csv")

prospects["fecha_decision"] = pd.to_datetime(
    prospects["fecha_decision"]
).dt.date

for column in (
    "emisor_fecha_decision_perfil",
    "emisor_fecha_primera_inscripcion",
):
    comparables[column] = pd.to_datetime(
        comparables[column]
    ).dt.date

# Enriquecer comparables con ranking y score del prospecto.
lookup = prospects[
    ["expediente_key", "ranking", "score_afinidad"]
].rename(
    columns={"ranking": "ranking_v10"}
)

comparables = comparables.merge(
    lookup,
    on="expediente_key",
    how="left",
    validate="many_to_one",
)

# ------------------------------------------------------------
# Construir resumen de similitud.
# ------------------------------------------------------------
summary_rows = []

for expediente_key in prospects["expediente_key"].astype(int):
    group = comparables[
        comparables["expediente_key"] == expediente_key
    ].sort_values("orden_comparable")

    if group.empty:
        summary_rows.append(
            {
                "expediente_key": expediente_key,
                "comparables_disponibles": False,
                "similitud_emisor_top1": None,
                "similitud_emisores_top5_promedio": None,
                "distancia_emisor_top1": None,
                "n_emisores_comparados": 0,
                "estado_similitud": "SIN_COMPARABLES",
                "metodologia_similitud": (
                    "Demo sintética para evaluación funcional."
                ),
            }
        )
    else:
        first = group.iloc[0]
        summary_rows.append(
            {
                "expediente_key": expediente_key,
                "comparables_disponibles": True,
                "similitud_emisor_top1": float(first["similitud"]),
                "similitud_emisores_top5_promedio": float(
                    group["similitud"].mean()
                ),
                "distancia_emisor_top1": float(
                    first["distancia_percentiles"]
                ),
                "n_emisores_comparados": int(len(group)),
                "estado_similitud": "DISPONIBLE",
                "metodologia_similitud": (
                    "Demo sintética para evaluación funcional. "
                    "No corresponde a resultados académicos oficiales."
                ),
            }
        )

summary = pd.DataFrame(summary_rows)

# ------------------------------------------------------------
# Crear tablas y cargar datos.
# ------------------------------------------------------------
Base.metadata.create_all(bind=engine)

with engine.begin() as connection:
    connection.execute(text("DELETE FROM issuer_similarity_matches"))
    connection.execute(text("DELETE FROM issuer_similarity_summary"))
    connection.execute(text("DELETE FROM operational_prospects"))

    prospects.to_sql(
        "operational_prospects",
        connection,
        if_exists="append",
        index=False,
        method="multi",
    )

    summary.to_sql(
        "issuer_similarity_summary",
        connection,
        if_exists="append",
        index=False,
        method="multi",
    )

    comparables.to_sql(
        "issuer_similarity_matches",
        connection,
        if_exists="append",
        index=False,
        method="multi",
    )

print("Demo cargada correctamente.")
print(f"Prospectos sintéticos: {len(prospects)}")
print(f"Comparables sintéticos: {len(comparables)}")
print("Base: prospect_finder_demo | puerto: 5434")
