"""
Modelos ORM principales de Prospect Finder BVQ.

Tablas
------
1. operational_prospects
   Contiene el ranking operativo v10 y la información financiera
   necesaria para mostrar el detalle de cada empresa.

2. issuer_similarity_summary
   Contiene el resumen de similitud de cada empresa con perfiles
   históricos de emisores.

3. issuer_similarity_matches
   Contiene los cinco emisores históricos más similares para cada
   empresa con información suficiente.

4. issuer_reference_profiles
   Contiene los perfiles financieros históricos de los emisores
   utilizados como universo de referencia por el motor de similitud.

El score predictivo y la similitud se almacenan por separado.
No existe una fórmula que combine ambos indicadores.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Date
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.api.core.database import Base


# ============================================================
# RANKING OPERATIVO
# ============================================================

class OperationalProspect(Base):
    """
    Una fila por empresa del universo operativo 2023
    al corte de decisión 2024-05-01.
    """

    __tablename__ = "operational_prospects"

    # --------------------------------------------------------
    # IDENTIFICACIÓN
    # --------------------------------------------------------

    expediente_key: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        nullable=False,
    )

    ruc: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    nombre: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    anio: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    fecha_decision: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    tipo_compania: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    provincia: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    # --------------------------------------------------------
    # RANKING Y SCORE
    # --------------------------------------------------------

    ranking: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True,
        index=True,
    )

    score_afinidad: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
    )

    percentil_ranking: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # --------------------------------------------------------
    # CALIDAD / COBERTURA DE INFORMACIÓN
    # --------------------------------------------------------

    n_features_disponibles: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    pct_features_disponibles: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
    )

    # --------------------------------------------------------
    # VARIABLES FINANCIERAS PRINCIPALES
    # --------------------------------------------------------

    activos_final: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    patrimonio_final: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    bi_ingresos_ventas: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    bi_n_empleados: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    fin_ratio_patrimonio_activos: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    fin_roa: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    fin_margen_neto: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    fin_rotacion_activos: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    fin_roe: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    fin_crecimiento_activos: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    fin_crecimiento_patrimonio: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    fin_crecimiento_ventas: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    fin_crecimiento_empleados: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    # --------------------------------------------------------
    # MODELO
    # --------------------------------------------------------

    modelo: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    configuracion_modelo: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # --------------------------------------------------------
    # RELACIONES
    # --------------------------------------------------------

    similarity_summary: Mapped[
        "IssuerSimilaritySummary | None"
    ] = relationship(
        back_populates="prospect",
        cascade="all, delete-orphan",
        uselist=False,
        passive_deletes=True,
    )

    similarity_matches: Mapped[
        list["IssuerSimilarityMatch"]
    ] = relationship(
        back_populates="prospect",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="IssuerSimilarityMatch.orden_comparable",
    )

    # --------------------------------------------------------
    # ÍNDICES COMPUESTOS
    # --------------------------------------------------------

    __table_args__ = (
        Index(
            "ix_operational_prospects_score_ranking",
            "score_afinidad",
            "ranking",
        ),
        Index(
            "ix_operational_prospects_provincia_tipo",
            "provincia",
            "tipo_compania",
        ),
    )


# ============================================================
# RESUMEN DE SIMILITUD
# ============================================================

class IssuerSimilaritySummary(Base):
    """
    Resumen de similitud entre una empresa del universo
    operativo y los perfiles históricos de emisores.
    """

    __tablename__ = "issuer_similarity_summary"

    expediente_key: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "operational_prospects.expediente_key",
            ondelete="CASCADE",
        ),
        primary_key=True,
        nullable=False,
    )

    comparables_disponibles: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    similitud_emisor_top1: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
        index=True,
    )

    similitud_emisores_top5_promedio: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    distancia_emisor_top1: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    n_emisores_comparados: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    estado_similitud: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    metodologia_similitud: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    prospect: Mapped[
        "OperationalProspect"
    ] = relationship(
        back_populates="similarity_summary",
    )


# ============================================================
# PERFILES HISTÓRICOS DE EMISORES
# ============================================================

class IssuerReferenceProfile(Base):
    """
    Perfil financiero histórico de un emisor utilizado como
    referencia por el motor de similitud de Prospect Finder.

    Cada fila representa el perfil temporal seleccionado antes
    de la primera inscripción del emisor.

    Las siete variables financieras y sus percentiles son
    exactamente las utilizadas por el motor de similitud v10.
    """

    __tablename__ = "issuer_reference_profiles"

    # --------------------------------------------------------
    # IDENTIFICACIÓN
    # --------------------------------------------------------

    expediente_key: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        nullable=False,
    )

    ruc: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    nombre: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    anio: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    tipo_compania: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    provincia: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    # --------------------------------------------------------
    # REFERENCIA TEMPORAL
    # --------------------------------------------------------

    fecha_decision: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    fecha_primera_inscripcion: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    dias_hasta_inscripcion: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # --------------------------------------------------------
    # 7 VARIABLES DEL MOTOR DE SIMILITUD
    # --------------------------------------------------------

    activos_final: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    patrimonio_final: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    bi_ingresos_ventas: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    bi_n_empleados: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    fin_ratio_patrimonio_activos: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    fin_roa: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    fin_rotacion_activos: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # --------------------------------------------------------
    # PERCENTILES UTILIZADOS EN LA DISTANCIA
    # --------------------------------------------------------

    pct__activos_final: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    pct__patrimonio_final: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    pct__bi_ingresos_ventas: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    pct__bi_n_empleados: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    pct__fin_ratio_patrimonio_activos: Mapped[
        float
    ] = mapped_column(
        Float,
        nullable=False,
    )

    pct__fin_roa: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    pct__fin_rotacion_activos: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # --------------------------------------------------------
    # ÍNDICES
    # --------------------------------------------------------

    __table_args__ = (
        Index(
            "ix_issuer_reference_profiles_provincia_tipo",
            "provincia",
            "tipo_compania",
        ),
        Index(
            "ix_issuer_reference_profiles_dates",
            "fecha_decision",
            "fecha_primera_inscripcion",
        ),
    )


# ============================================================
# COMPARABLES HISTÓRICOS
# ============================================================

class IssuerSimilarityMatch(Base):
    """
    Relación individual entre una empresa prospecto y uno
    de sus cinco emisores históricos más similares.
    """

    __tablename__ = "issuer_similarity_matches"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # --------------------------------------------------------
    # EMPRESA PROSPECTO
    # --------------------------------------------------------

    expediente_key: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "operational_prospects.expediente_key",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    ranking_v10: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    score_afinidad: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # --------------------------------------------------------
    # POSICIÓN DEL COMPARABLE
    # --------------------------------------------------------

    orden_comparable: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    similitud: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
    )

    distancia_percentiles: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # --------------------------------------------------------
    # EMISOR HISTÓRICO
    # --------------------------------------------------------

    emisor_expediente_key: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    emisor_ruc: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    emisor_nombre: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    emisor_anio_perfil: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    emisor_fecha_decision_perfil: Mapped[
        date
    ] = mapped_column(
        Date,
        nullable=False,
    )

    emisor_fecha_primera_inscripcion: Mapped[
        date
    ] = mapped_column(
        Date,
        nullable=False,
    )

    emisor_tipo_compania: Mapped[
        str | None
    ] = mapped_column(
        String(150),
        nullable=True,
    )

    emisor_provincia: Mapped[
        str | None
    ] = mapped_column(
        String(150),
        nullable=True,
    )

    mismo_tipo_compania: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    # --------------------------------------------------------
    # RELACIÓN
    # --------------------------------------------------------

    prospect: Mapped[
        "OperationalProspect"
    ] = relationship(
        back_populates="similarity_matches",
    )

    # --------------------------------------------------------
    # RESTRICCIONES E ÍNDICES
    # --------------------------------------------------------

    __table_args__ = (
        UniqueConstraint(
            "expediente_key",
            "orden_comparable",
            name=(
                "uq_issuer_similarity_matches_"
                "prospect_order"
            ),
        ),
        Index(
            "ix_issuer_similarity_matches_prospect_similarity",
            "expediente_key",
            "similitud",
        ),
    )