"""
Construcción del ranking operativo Prospect Finder BVQ - v10.

Objetivo
--------
Generar el universo de empresas prospectables al 01-05-2024 y
asignar a cada empresa el score producido por el modelo final
congelado v10_hgb_financial_c3.

Principios metodológicos
------------------------
1. No reentrena el modelo.
2. Utiliza exclusivamente información financiera 2023.
3. El corte de decisión es 2024-05-01.
4. Excluye únicamente empresas que ya eran emisores al corte.
5. No utiliza TARGET_24M para generar scores.
6. No incorpora fechas futuras de inscripción al resultado.
7. Replica el tratamiento categórico aprendido desde TRAIN.
8. El score se interpreta como score de priorización,
   no como probabilidad calibrada.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

FINANCIAL_DATA_PATH = (
    ROOT
    / "data"
    / "processed"
    / "v10_features_financial_2012_2023.csv.gz"
)

BASE_DATA_PATH = (
    ROOT
    / "data"
    / "processed"
    / "v10_base_integrated_2012_2023.csv.gz"
)

MODEL_PATH = (
    ROOT
    / "models"
    / "v10"
    / "v10_hgb_financial_c3_final.joblib"
)

OUTPUT_DATA_DIR = (
    ROOT
    / "data"
    / "processed"
)

OUTPUT_REPORT_DIR = (
    ROOT
    / "reports"
    / "results"
    / "v10"
    / "product"
)

OUTPUT_FULL_RANKING = (
    OUTPUT_DATA_DIR
    / "v10_operational_ranking_2024_05_01.csv.gz"
)

OUTPUT_TOP500 = (
    OUTPUT_REPORT_DIR
    / "v10_operational_top500_2024_05_01.csv"
)

OUTPUT_METADATA = (
    OUTPUT_REPORT_DIR
    / "v10_operational_ranking_metadata.json"
)

OPERATIONAL_YEAR = 2023

DECISION_DATE = pd.Timestamp(
    "2024-05-01"
)


# ============================================================
# UTILIDADES
# ============================================================

def validar_archivos() -> None:
    """
    Comprueba que existan los insumos necesarios.
    """

    required_paths = [
        FINANCIAL_DATA_PATH,
        BASE_DATA_PATH,
        MODEL_PATH,
    ]

    missing = [
        path
        for path in required_paths
        if not path.exists()
    ]

    if missing:
        missing_text = "\n".join(
            str(path)
            for path in missing
        )

        raise FileNotFoundError(
            "Faltan archivos requeridos:\n"
            f"{missing_text}"
        )


def cargar_modelo():
    """
    Carga el artefacto final congelado.
    """

    artifact = joblib.load(
        MODEL_PATH
    )

    if not isinstance(
        artifact,
        dict,
    ):
        raise TypeError(
            "El artefacto final debe ser un diccionario."
        )

    required_keys = {
        "model",
        "model_name",
        "config_id",
        "features",
        "numeric_features",
        "boolean_features",
        "categorical_features",
        "train_period",
        "test_period",
    }

    missing_keys = (
        required_keys
        - set(
            artifact.keys()
        )
    )

    if missing_keys:
        raise KeyError(
            "Faltan claves en el artefacto: "
            f"{sorted(missing_keys)}"
        )

    return artifact


def obtener_emisores_al_corte() -> set:
    """
    Obtiene empresas cuya primera inscripción ocurrió
    en o antes de la fecha de decisión.

    Las inscripciones posteriores al corte no se utilizan
    para excluir empresas.
    """

    base = pd.read_csv(
        BASE_DATA_PATH,
        usecols=[
            "EXPEDIENTE_KEY",
            "fecha_primera_inscripcion",
        ],
        low_memory=False,
    )

    base[
        "fecha_primera_inscripcion"
    ] = pd.to_datetime(
        base[
            "fecha_primera_inscripcion"
        ],
        errors="coerce",
    )

    emisores = base.loc[
        base[
            "fecha_primera_inscripcion"
        ].notna()
        &
        (
            base[
                "fecha_primera_inscripcion"
            ]
            <= DECISION_DATE
        ),
        "EXPEDIENTE_KEY",
    ]

    emisores = set(
        emisores
        .dropna()
        .unique()
        .tolist()
    )

    return emisores


def obtener_categorias_train(
    categorical_features: list[str],
) -> dict[str, list[str]]:
    """
    Aprende las categorías exclusivamente desde TRAIN,
    replicando la metodología de evaluación final.
    """

    usecols = [
        "SPLIT",
        *categorical_features,
    ]

    dataframe = pd.read_csv(
        FINANCIAL_DATA_PATH,
        usecols=usecols,
        low_memory=False,
    )

    train = dataframe.loc[
        dataframe[
            "SPLIT"
        ]
        == "TRAIN"
    ].copy()

    categories = {}

    for variable in categorical_features:

        serie = (
            train[
                variable
            ]
            .astype(
                "string"
            )
        )

        categorias_train = sorted(
            serie
            .dropna()
            .unique()
            .tolist()
        )

        categories[
            variable
        ] = categorias_train

    return categories


def cargar_universo_operativo(
    features: list[str],
) -> pd.DataFrame:
    """
    Carga únicamente las columnas necesarias y obtiene
    el universo correspondiente al año financiero 2023.
    """

    identification_columns = [
        "ANIO",
        "EXPEDIENTE_KEY",
        "RUC",
        "NOMBRE",
        "provincia",
    ]

    requested_columns = list(
        dict.fromkeys(
            identification_columns
            + features
        )
    )

    dataframe = pd.read_csv(
        FINANCIAL_DATA_PATH,
        usecols=requested_columns,
        dtype={
            "RUC": "string",
            "NOMBRE": "string",
        },
        low_memory=False,
    )

    operational = dataframe.loc[
        dataframe[
            "ANIO"
        ]
        == OPERATIONAL_YEAR
    ].copy()

    if operational.empty:
        raise ValueError(
            "No existen observaciones para "
            f"ANIO={OPERATIONAL_YEAR}."
        )

    duplicates = (
        operational[
            "EXPEDIENTE_KEY"
        ]
        .duplicated()
        .sum()
    )

    if duplicates > 0:
        raise ValueError(
            "El universo operativo contiene "
            f"{duplicates} EXPEDIENTE_KEY duplicados."
        )

    return operational


def preparar_categorias_operativas(
    dataframe: pd.DataFrame,
    train_categories: dict[
        str,
        list[str],
    ],
) -> tuple[
    pd.DataFrame,
    dict[str, list[str]],
]:
    """
    Convierte las variables categóricas utilizando únicamente
    categorías aprendidas desde TRAIN.

    Categorías desconocidas se convierten a missing.
    """

    output = dataframe.copy()

    unknown_categories = {}

    for variable, categorias_train in (
        train_categories.items()
    ):

        serie = (
            output[
                variable
            ]
            .astype(
                "string"
            )
        )

        categorias_operativas = set(
            serie
            .dropna()
            .unique()
            .tolist()
        )

        unknown = sorted(
            categorias_operativas
            - set(
                categorias_train
            )
        )

        unknown_categories[
            variable
        ] = unknown

        output[
            variable
        ] = pd.Categorical(
            serie,
            categories=categorias_train,
        )

    return (
        output,
        unknown_categories,
    )


def construir_ranking() -> None:
    """
    Ejecuta el flujo completo de scoring operativo.
    """

    print(
        "\n"
        "==============================================="
    )
    print(
        "PROSPECT FINDER BVQ"
    )
    print(
        "Construcción del ranking operativo v10"
    )
    print(
        "===============================================\n"
    )

    validar_archivos()

    OUTPUT_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # MODELO FINAL
    # --------------------------------------------------------

    artifact = cargar_modelo()

    model = artifact[
        "model"
    ]

    model_name = artifact[
        "model_name"
    ]

    config_id = artifact[
        "config_id"
    ]

    features = list(
        artifact[
            "features"
        ]
    )

    numeric_features = list(
        artifact[
            "numeric_features"
        ]
    )

    boolean_features = list(
        artifact[
            "boolean_features"
        ]
    )

    categorical_features = list(
        artifact[
            "categorical_features"
        ]
    )

    print(
        f"Modelo: {model_name}"
    )

    print(
        f"Configuración: {config_id}"
    )

    print(
        f"TRAIN original: "
        f"{artifact['train_period']}"
    )

    print(
        f"TEST original: "
        f"{artifact['test_period']}"
    )

    print(
        f"Número de features: "
        f"{len(features)}"
    )

    # --------------------------------------------------------
    # CATEGORÍAS APRENDIDAS DESDE TRAIN
    # --------------------------------------------------------

    print(
        "\nObteniendo categorías aprendidas "
        "exclusivamente desde TRAIN..."
    )

    train_categories = (
        obtener_categorias_train(
            categorical_features
        )
    )

    for variable, categorias in (
        train_categories.items()
    ):
        print(
            f"{variable}: "
            f"{len(categorias)} categorías TRAIN"
        )

    # --------------------------------------------------------
    # UNIVERSO 2023
    # --------------------------------------------------------

    print(
        "\nCargando universo operativo 2023..."
    )

    operational = (
        cargar_universo_operativo(
            features
        )
    )

    initial_count = len(
        operational
    )

    print(
        f"Empresas con información 2023: "
        f"{initial_count:,}"
    )

    # --------------------------------------------------------
    # EXCLUSIÓN DE EMISORES EXISTENTES
    # --------------------------------------------------------

    print(
        "\nIdentificando emisores existentes "
        f"al {DECISION_DATE.date()}..."
    )

    issuers_at_cutoff = (
        obtener_emisores_al_corte()
    )

    print(
        "Emisores históricos identificados "
        f"al corte: {len(issuers_at_cutoff):,}"
    )

    operational = operational.loc[
        ~operational[
            "EXPEDIENTE_KEY"
        ].isin(
            issuers_at_cutoff
        )
    ].copy()

    excluded_from_operational = (
        initial_count
        - len(
            operational
        )
    )

    print(
        "Emisores eliminados del universo "
        f"2023: {excluded_from_operational:,}"
    )

    print(
        "Universo prospectable final: "
        f"{len(operational):,}"
    )

    # --------------------------------------------------------
    # VALIDACIÓN Y PREPARACIÓN DE FEATURES
    # --------------------------------------------------------

    missing_features = [
        feature
        for feature in features
        if feature
        not in operational.columns
    ]

    if missing_features:
        raise KeyError(
            "Faltan features requeridas por "
            "el modelo:\n"
            f"{missing_features}"
        )

    for variable in numeric_features:
        operational[
            variable
        ] = pd.to_numeric(
            operational[
                variable
            ],
            errors="coerce",
        )

    (
        operational,
        unknown_categories,
    ) = preparar_categorias_operativas(
        operational,
        train_categories,
    )

    for variable, unknown in (
        unknown_categories.items()
    ):

        if unknown:
            print(
                "\nCategorías desconocidas para "
                f"{variable}: {unknown}"
            )

            print(
                "Se tratan como missing, "
                "sin aprender información nueva."
            )
        else:
            print(
                f"\n{variable}: "
                "sin categorías desconocidas."
            )

    # --------------------------------------------------------
    # MATRIZ DEL MODELO
    # --------------------------------------------------------

    X_operational = operational[
        features
    ].copy()

    if list(
        X_operational.columns
    ) != features:
        raise ValueError(
            "El orden de las variables no coincide "
            "con el artefacto del modelo."
        )

    # --------------------------------------------------------
    # INDICADOR DE COMPLETITUD
    # --------------------------------------------------------

    operational[
        "n_features_disponibles"
    ] = (
        X_operational
        .notna()
        .sum(
            axis=1
        )
        .astype(
            int
        )
    )

    operational[
        "pct_features_disponibles"
    ] = (
        operational[
            "n_features_disponibles"
        ]
        / len(
            features
        )
        * 100
    )

    # --------------------------------------------------------
    # SCORING
    # --------------------------------------------------------

    print(
        "\nGenerando scores con el "
        "modelo congelado..."
    )

    scores = model.predict_proba(
        X_operational
    )[:, 1]

    if not np.isfinite(
        scores
    ).all():
        raise ValueError(
            "Se generaron scores no finitos."
        )

    if (
        (scores < 0).any()
        or (scores > 1).any()
    ):
        raise ValueError(
            "Se generaron scores fuera "
            "del rango [0, 1]."
        )

    operational[
        "score_afinidad"
    ] = scores

    # --------------------------------------------------------
    # RANKING
    # --------------------------------------------------------

    operational = (
        operational
        .sort_values(
            by=[
                "score_afinidad",
                "EXPEDIENTE_KEY",
            ],
            ascending=[
                False,
                True,
            ],
            kind="mergesort",
        )
        .reset_index(
            drop=True
        )
    )

    operational[
        "ranking"
    ] = np.arange(
        1,
        len(
            operational
        )
        + 1,
        dtype=int,
    )

    operational[
        "percentil_ranking"
    ] = (
        1
        - (
            operational[
                "ranking"
            ]
            - 1
        )
        / len(
            operational
        )
    ) * 100

    # --------------------------------------------------------
    # CAMPOS DEL PRODUCTO
    # --------------------------------------------------------

    operational[
        "fecha_decision"
    ] = DECISION_DATE.date().isoformat()

    operational[
        "modelo"
    ] = model_name

    operational[
        "configuracion_modelo"
    ] = config_id

    # No incluir TARGET_24M ni SPLIT.
    # No incluir fecha futura de inscripción.

    preferred_columns = [
        "ranking",
        "score_afinidad",
        "percentil_ranking",
        "fecha_decision",
        "ANIO",
        "EXPEDIENTE_KEY",
        "RUC",
        "NOMBRE",
        "tipo_compania",
        "provincia",
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

    final_columns = [
        column
        for column in preferred_columns
        if column
        in operational.columns
    ]

    ranking = operational[
        final_columns
    ].copy()

    # --------------------------------------------------------
    # VALIDACIONES FINALES
    # --------------------------------------------------------

    if ranking[
        "EXPEDIENTE_KEY"
    ].duplicated().any():
        raise ValueError(
            "El ranking final contiene "
            "empresas duplicadas."
        )

    if ranking[
        "ranking"
    ].duplicated().any():
        raise ValueError(
            "El ranking contiene posiciones "
            "duplicadas."
        )

    if "TARGET_24M" in ranking.columns:
        raise ValueError(
            "TARGET_24M no debe formar parte "
            "del producto operativo."
        )

    # --------------------------------------------------------
    # EXPORTACIÓN
    # --------------------------------------------------------

    ranking.to_csv(
        OUTPUT_FULL_RANKING,
        index=False,
        compression="gzip",
    )

    ranking.head(
        500
    ).to_csv(
        OUTPUT_TOP500,
        index=False,
    )

    metadata = {
        "model_name":
            model_name,
        "config_id":
            config_id,
        "train_period":
            artifact[
                "train_period"
            ],
        "test_period":
            artifact[
                "test_period"
            ],
        "operational_financial_year":
            OPERATIONAL_YEAR,
        "decision_date":
            DECISION_DATE.date().isoformat(),
        "number_of_features":
            len(
                features
            ),
        "features":
            features,
        "numeric_features":
            numeric_features,
        "boolean_features":
            boolean_features,
        "categorical_features":
            categorical_features,
        "train_categories":
            train_categories,
        "unknown_operational_categories":
            unknown_categories,
        "companies_2023_before_filter":
            int(
                initial_count
            ),
        "known_issuers_at_cutoff":
            int(
                len(
                    issuers_at_cutoff
                )
            ),
        "issuers_removed_from_2023":
            int(
                excluded_from_operational
            ),
        "operational_universe":
            int(
                len(
                    ranking
                )
            ),
        "score_min":
            float(
                ranking[
                    "score_afinidad"
                ].min()
            ),
        "score_max":
            float(
                ranking[
                    "score_afinidad"
                ].max()
            ),
        "score_mean":
            float(
                ranking[
                    "score_afinidad"
                ].mean()
            ),
        "score_median":
            float(
                ranking[
                    "score_afinidad"
                ].median()
            ),
        "interpretation":
            (
                "score_afinidad es un score de "
                "priorizacion relativo y no una "
                "probabilidad calibrada."
            ),
    }

    with open(
        OUTPUT_METADATA,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2,
        )

    # --------------------------------------------------------
    # RESUMEN
    # --------------------------------------------------------

    print(
        "\n"
        "==============================================="
    )
    print(
        "RANKING OPERATIVO GENERADO CORRECTAMENTE"
    )
    print(
        "==============================================="
    )

    print(
        f"\nUniverso final: "
        f"{len(ranking):,}"
    )

    print(
        "Score mínimo: "
        f"{ranking['score_afinidad'].min():.6f}"
    )

    print(
        "Score máximo: "
        f"{ranking['score_afinidad'].max():.6f}"
    )

    print(
        "Score promedio: "
        f"{ranking['score_afinidad'].mean():.6f}"
    )

    print(
        "Score mediano: "
        f"{ranking['score_afinidad'].median():.6f}"
    )

    print(
        "\nTop 10:"
    )

    print(
        ranking[
            [
                "ranking",
                "EXPEDIENTE_KEY",
                "NOMBRE",
                "score_afinidad",
                "pct_features_disponibles",
            ]
        ]
        .head(
            10
        )
        .to_string(
            index=False
        )
    )

    print(
        "\nArchivo completo:"
    )

    print(
        OUTPUT_FULL_RANKING
    )

    print(
        "\nTop 500:"
    )

    print(
        OUTPUT_TOP500
    )

    print(
        "\nMetadata:"
    )

    print(
        OUTPUT_METADATA
    )

    print(
        "\nIMPORTANTE:"
    )

    print(
        "El score es un mecanismo de priorización."
    )

    print(
        "No representa una probabilidad calibrada "
        "de convertirse en emisor."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    construir_ranking()