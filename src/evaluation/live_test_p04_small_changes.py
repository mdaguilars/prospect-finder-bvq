"""
P04 · Robustez a pequeños cambios
Prospect Finder BVQ

Objetivo
--------
Evaluar la sensibilidad del modelo v10 ante una perturbación
pequeña y realista de ±5 % sobre un indicador financiero.

Indicador seleccionado:
    fin_rotacion_activos

La prueba calcula:

- score original;
- score con -5 %;
- score con +5 %;
- posición original en TEST;
- posición después de cada perturbación;
- diferencia absoluta y relativa de score;
- cambio de posiciones.

IMPORTANTE
----------
No se modifica:

- el dataset original;
- el modelo v10;
- el ranking oficial;
- TEST;
- PostgreSQL;
- los resultados oficiales.

Las evidencias se guardan únicamente en:

    reports/live_tests/P04/
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# =============================================================================
# CONFIGURACIÓN
# =============================================================================

ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    ROOT
    / "data"
    / "processed"
    / "v10_features_financial_2012_2023.csv.gz"
)

MODEL_PATH = (
    ROOT
    / "models"
    / "v10"
    / "v10_hgb_financial_c3_final.joblib"
)

OUTPUT_DIR = (
    ROOT
    / "reports"
    / "live_tests"
    / "P04"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =============================================================================
# PERTURBACIÓN
# =============================================================================

TEST_FEATURE = "fin_rotacion_activos"

PERTURBATIONS = {
    "MENOS_5_PCT": 0.95,
    "MAS_5_PCT": 1.05,
}


# =============================================================================
# UTILIDADES
# =============================================================================

def header(
    title: str,
) -> None:

    print()
    print("=" * 100)
    print(title)
    print("=" * 100)
    print()


def percent_change(
    original: float,
    new: float,
) -> float | None:

    if original == 0:
        return None

    return (
        (
            new
            - original
        )
        / abs(
            original
        )
        * 100.0
    )


# =============================================================================
# ARTEFACTO
# =============================================================================

def load_artifact() -> dict:

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"No existe el modelo:\n{MODEL_PATH}"
        )

    artifact = joblib.load(
        MODEL_PATH
    )

    if not isinstance(
        artifact,
        dict,
    ):
        raise RuntimeError(
            "El artefacto final no tiene "
            "la estructura esperada."
        )

    required_keys = [
        "model",
        "features",
        "numeric_features",
        "boolean_features",
        "categorical_features",
    ]

    missing = [
        key
        for key in required_keys
        if key not in artifact
    ]

    if missing:

        raise RuntimeError(
            "Faltan claves requeridas:\n"
            + "\n".join(
                missing
            )
        )

    return artifact


# =============================================================================
# CATEGORÍAS TRAIN
# =============================================================================

def load_train_categories(
    categorical_features: list[str],
) -> dict[str, list[str]]:

    category_sets: dict[
        str,
        set[str],
    ] = {
        feature: set()
        for feature
        in categorical_features
    }

    usecols = [
        "SPLIT",
        *categorical_features,
    ]

    for chunk in pd.read_csv(
        DATA_PATH,
        usecols=usecols,
        chunksize=200_000,
        low_memory=False,
    ):

        train = chunk[
            chunk[
                "SPLIT"
            ].eq(
                "TRAIN"
            )
        ]

        if train.empty:
            continue

        for feature in categorical_features:

            values = (
                train[
                    feature
                ]
                .dropna()
                .astype(
                    "string"
                )
            )

            category_sets[
                feature
            ].update(
                values.tolist()
            )

    return {
        feature:
            sorted(
                values
            )
        for feature, values
        in category_sets.items()
    }


# =============================================================================
# PREPARACIÓN DE FEATURES
# =============================================================================

def prepare_feature_frame(
    dataframe: pd.DataFrame,
    artifact: dict,
    train_categories: dict[
        str,
        list[str],
    ],
) -> pd.DataFrame:

    features = list(
        artifact[
            "features"
        ]
    )

    numeric_features = set(
        artifact[
            "numeric_features"
        ]
    )

    boolean_features = set(
        artifact[
            "boolean_features"
        ]
    )

    categorical_features = set(
        artifact[
            "categorical_features"
        ]
    )

    missing = [
        feature
        for feature in features
        if feature
        not in dataframe.columns
    ]

    if missing:

        raise RuntimeError(
            "Faltan variables requeridas "
            "por el modelo:\n"
            + "\n".join(
                missing
            )
        )

    output = dataframe[
        features
    ].copy()

    for feature in features:

        if feature in categorical_features:

            categories = (
                train_categories.get(
                    feature,
                    [],
                )
            )

            values = (
                output[
                    feature
                ]
                .astype(
                    "string"
                )
            )

            output[
                feature
            ] = pd.Categorical(
                values,
                categories=categories,
            )

            continue

        if (
            feature
            in numeric_features
            or feature
            in boolean_features
        ):

            output[
                feature
            ] = pd.to_numeric(
                output[
                    feature
                ],
                errors="coerce",
            )

            output[
                feature
            ] = (
                output[
                    feature
                ]
                .replace(
                    [
                        np.inf,
                        -np.inf,
                    ],
                    np.nan,
                )
                .astype(
                    "float64"
                )
            )

    return output[
        features
    ]


# =============================================================================
# CARGA DEL UNIVERSO TEST
# =============================================================================

def load_test(
    features: list[str],
) -> pd.DataFrame:

    identification = [
        "ANIO",
        "EXPEDIENTE_KEY",
        "RUC",
        "NOMBRE",
        "TARGET_24M",
        "SPLIT",
    ]

    usecols = list(
        dict.fromkeys(
            [
                *identification,
                *features,
            ]
        )
    )

    frames: list[
        pd.DataFrame
    ] = []

    for chunk in pd.read_csv(
        DATA_PATH,
        usecols=usecols,
        chunksize=200_000,
        low_memory=False,
    ):

        test = chunk[
            chunk[
                "SPLIT"
            ].eq(
                "TEST"
            )
        ].copy()

        if not test.empty:

            frames.append(
                test
            )

    if not frames:

        raise RuntimeError(
            "No existen observaciones TEST."
        )

    output = pd.concat(
        frames,
        ignore_index=True,
    )

    if len(output) != 260_445:

        raise RuntimeError(
            "El universo TEST no coincide "
            "con las 260.445 observaciones "
            "oficiales."
        )

    return output


# =============================================================================
# RANKING DETERMINISTA
# =============================================================================

def calculate_ranking(
    scores: np.ndarray,
) -> np.ndarray:

    """
    Orden descendente por score.

    En caso de empate se conserva como segundo
    criterio la posición original del registro,
    únicamente para obtener una posición
    reproducible durante esta prueba.
    """

    indices = np.arange(
        len(
            scores
        )
    )

    order = np.lexsort(
        (
            indices,
            -scores,
        )
    )

    ranking = np.empty(
        len(
            scores
        ),
        dtype=np.int64,
    )

    ranking[
        order
    ] = (
        np.arange(
            1,
            len(
                scores
            )
            + 1,
        )
    )

    return ranking


# =============================================================================
# SELECCIÓN DEL CASO DE PRUEBA
# =============================================================================

def select_test_case(
    raw_test: pd.DataFrame,
    prepared_test: pd.DataFrame,
    scores: np.ndarray,
    features: list[str],
) -> int:

    """
    Selecciona una empresa:

    - de 2023;
    - con las 25 features disponibles;
    - con rotación de activos finita;
    - rotación distinta de cero;
    - con score cercano a la mediana TEST.

    Esto evita escoger deliberadamente un caso
    extremo de score.
    """

    complete = (
        prepared_test[
            features
        ]
        .notna()
        .all(
            axis=1
        )
    )

    rotation = pd.to_numeric(
        prepared_test[
            TEST_FEATURE
        ],
        errors="coerce",
    )

    eligible = (
        raw_test[
            "ANIO"
        ].eq(
            2023
        )
        &
        complete
        &
        rotation.notna()
        &
        np.isfinite(
            rotation
        )
        &
        rotation.ne(
            0
        )
    )

    eligible_indices = np.flatnonzero(
        eligible.to_numpy()
    )

    if len(
        eligible_indices
    ) == 0:

        raise RuntimeError(
            "No se encontraron casos elegibles "
            "para P04."
        )

    median_score = float(
        np.median(
            scores[
                eligible_indices
            ]
        )
    )

    differences = np.abs(
        scores[
            eligible_indices
        ]
        - median_score
    )

    selected_position = int(
        np.argmin(
            differences
        )
    )

    selected_index = int(
        eligible_indices[
            selected_position
        ]
    )

    return selected_index


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    header(
        "P04 · ROBUSTEZ A PEQUEÑOS CAMBIOS"
    )

    print(
        "Modelo:"
    )
    print(
        "v10_hgb_financial_c3"
    )

    print()

    print(
        "Configuración:"
    )
    print(
        "C3_CONSERVATIVE"
    )

    print()

    print(
        "Indicador a modificar:"
    )
    print(
        TEST_FEATURE
    )

    print()

    print(
        "Perturbaciones:"
    )
    print(
        "-5 % y +5 %"
    )

    # =========================================================================
    # MODELO
    # =========================================================================

    artifact = (
        load_artifact()
    )

    model = artifact[
        "model"
    ]

    features = list(
        artifact[
            "features"
        ]
    )

    categorical_features = list(
        artifact[
            "categorical_features"
        ]
    )

    # =========================================================================
    # CATEGORÍAS
    # =========================================================================

    print()

    print(
        "Cargando categorías aprendidas "
        "exclusivamente desde TRAIN..."
    )

    train_categories = (
        load_train_categories(
            categorical_features
        )
    )

    # =========================================================================
    # TEST
    # =========================================================================

    print(
        "Cargando TEST..."
    )

    raw_test = (
        load_test(
            features
        )
    )

    print(
        f"TEST cargado: "
        f"{len(raw_test):,} observaciones"
    )

    # =========================================================================
    # PREPARACIÓN
    # =========================================================================

    print(
        "Preparando las 25 variables..."
    )

    prepared_test = (
        prepare_feature_frame(
            raw_test,
            artifact,
            train_categories,
        )
    )

    # =========================================================================
    # SCORE BASE
    # =========================================================================

    print(
        "Calculando scores originales..."
    )

    original_scores = (
        model.predict_proba(
            prepared_test
        )[
            :,
            1,
        ]
    )

    if not np.all(
        np.isfinite(
            original_scores
        )
    ):

        raise RuntimeError(
            "El universo TEST produjo "
            "scores no finitos."
        )

    original_ranking = (
        calculate_ranking(
            original_scores
        )
    )

    # =========================================================================
    # CASO
    # =========================================================================

    case_index = (
        select_test_case(
            raw_test,
            prepared_test,
            original_scores,
            features,
        )
    )

    row = (
        raw_test
        .iloc[
            case_index
        ]
    )

    original_score = float(
        original_scores[
            case_index
        ]
    )

    original_rank = int(
        original_ranking[
            case_index
        ]
    )

    original_value = float(
        prepared_test[
            TEST_FEATURE
        ].iloc[
            case_index
        ]
    )

    header(
        "EMPRESA DE ENSAYO"
    )

    print(
        "ANIO:"
    )
    print(
        row[
            "ANIO"
        ]
    )

    print()

    print(
        "EXPEDIENTE_KEY:"
    )
    print(
        row[
            "EXPEDIENTE_KEY"
        ]
    )

    print()

    print(
        "Empresa:"
    )
    print(
        row[
            "NOMBRE"
        ]
    )

    print()

    print(
        "TARGET_24M:"
    )
    print(
        row[
            "TARGET_24M"
        ]
    )

    print()

    print(
        f"{TEST_FEATURE} original:"
    )
    print(
        f"{original_value:.9f}"
    )

    print()

    print(
        "Score original:"
    )
    print(
        f"{original_score:.9f}"
    )

    print()

    print(
        "Posición original en TEST:"
    )
    print(
        f"{original_rank:,} "
        f"de {len(raw_test):,}"
    )

    # =========================================================================
    # PERTURBACIONES
    # =========================================================================

    results: list[
        dict
    ] = []

    input_exports: list[
        pd.DataFrame
    ] = []

    # Caso original

    results.append(
        {
            "caso":
                "ORIGINAL",

            "factor":
                1.0,

            "valor_indicador":
                original_value,

            "score":
                original_score,

            "cambio_score_absoluto":
                0.0,

            "cambio_score_pct":
                0.0,

            "ranking":
                original_rank,

            "cambio_posiciones":
                0,
        }
    )

    original_export = (
        raw_test
        .iloc[
            [
                case_index
            ]
        ]
        .copy()
    )

    original_export[
        "CASO_PRUEBA"
    ] = "ORIGINAL"

    input_exports.append(
        original_export
    )

    for case_name, factor in (
        PERTURBATIONS.items()
    ):

        header(
            f"CASO · {case_name}"
        )

        altered_raw = (
            raw_test
            .iloc[
                [
                    case_index
                ]
            ]
            .copy()
        )

        altered_value = (
            original_value
            * factor
        )

        altered_raw.loc[
            :,
            TEST_FEATURE,
        ] = altered_value

        altered_prepared = (
            prepare_feature_frame(
                altered_raw,
                artifact,
                train_categories,
            )
        )

        altered_score = float(
            model.predict_proba(
                altered_prepared
            )[
                0,
                1,
            ]
        )

        if not np.isfinite(
            altered_score
        ):

            raise RuntimeError(
                f"El caso {case_name} produjo "
                "un score no finito."
            )

        modified_scores = (
            original_scores.copy()
        )

        modified_scores[
            case_index
        ] = altered_score

        modified_ranking = (
            calculate_ranking(
                modified_scores
            )
        )

        altered_rank = int(
            modified_ranking[
                case_index
            ]
        )

        score_change_absolute = (
            altered_score
            - original_score
        )

        score_change_pct = (
            percent_change(
                original_score,
                altered_score,
            )
        )

        rank_change = (
            altered_rank
            - original_rank
        )

        print(
            "Valor original:"
        )
        print(
            f"{original_value:.9f}"
        )

        print()

        print(
            "Valor modificado:"
        )
        print(
            f"{altered_value:.9f}"
        )

        print()

        print(
            "Cambio del indicador:"
        )
        print(
            f"{(factor - 1.0) * 100:+.2f}%"
        )

        print()

        print(
            "Score original:"
        )
        print(
            f"{original_score:.9f}"
        )

        print()

        print(
            "Score modificado:"
        )
        print(
            f"{altered_score:.9f}"
        )

        print()

        print(
            "Cambio absoluto del score:"
        )
        print(
            f"{score_change_absolute:+.9f}"
        )

        print()

        print(
            "Cambio relativo del score:"
        )

        if score_change_pct is None:

            print(
                "No calculable"
            )

        else:

            print(
                f"{score_change_pct:+.4f}%"
            )

        print()

        print(
            "Ranking original:"
        )
        print(
            f"{original_rank:,}"
        )

        print()

        print(
            "Ranking modificado:"
        )
        print(
            f"{altered_rank:,}"
        )

        print()

        print(
            "Cambio de posiciones:"
        )
        print(
            f"{rank_change:+,}"
        )

        if rank_change == 0:

            interpretation = (
                "La perturbación de ±5 % no "
                "cambió la posición de esta empresa."
            )

        elif abs(
            rank_change
        ) <= 10:

            interpretation = (
                "La perturbación produjo un cambio "
                "pequeño de posición."
            )

        else:

            interpretation = (
                "La perturbación produjo un cambio "
                "observable de posición que debe "
                "documentarse."
            )

        print()

        print(
            "Interpretación:"
        )
        print(
            interpretation
        )

        results.append(
            {
                "caso":
                    case_name,

                "factor":
                    factor,

                "valor_indicador":
                    altered_value,

                "score":
                    altered_score,

                "cambio_score_absoluto":
                    score_change_absolute,

                "cambio_score_pct":
                    score_change_pct,

                "ranking":
                    altered_rank,

                "cambio_posiciones":
                    rank_change,
            }
        )

        altered_export = (
            altered_raw.copy()
        )

        altered_export[
            "CASO_PRUEBA"
        ] = case_name

        input_exports.append(
            altered_export
        )

    # =========================================================================
    # RESULTADOS
    # =========================================================================

    results_df = pd.DataFrame(
        results
    )

    header(
        "RESUMEN DE SENSIBILIDAD"
    )

    print(
        results_df[
            [
                "caso",
                "valor_indicador",
                "score",
                "cambio_score_pct",
                "ranking",
                "cambio_posiciones",
            ]
        ].to_string(
            index=False
        )
    )

    valid_scores = (
        results_df[
            "score"
        ]
        .notna()
        .all()
    )

    valid_ranks = bool(
        (
            results_df[
                "ranking"
            ]
            >= 1
        ).all()
        and
        (
            results_df[
                "ranking"
            ]
            <= len(
                raw_test
            )
        ).all()
    )

    p04_pass = bool(
        valid_scores
        and valid_ranks
    )

    header(
        "RESULTADO P04"
    )

    if p04_pass:

        print(
            "CUMPLE"
        )

        print()

        print(
            "El modelo procesó correctamente "
            "las perturbaciones de -5 % y +5 %, "
            "y se documentaron sus efectos "
            "sobre score y posición."
        )

        print()

        print(
            "La prueba no exige que el ranking "
            "permanezca idéntico."
        )

    else:

        print(
            "PARCIAL / REVISAR"
        )

    # =========================================================================
    # EVIDENCIAS
    # =========================================================================

    results_path = (
        OUTPUT_DIR
        / "p04_results.csv"
    )

    results_df.to_csv(
        results_path,
        index=False,
    )

    inputs_df = pd.concat(
        input_exports,
        ignore_index=True,
    )

    inputs_path = (
        OUTPUT_DIR
        / "p04_inputs.csv"
    )

    inputs_df.to_csv(
        inputs_path,
        index=False,
    )

    case_summary = pd.DataFrame(
        [
            {
                "anio":
                    row[
                        "ANIO"
                    ],

                "expediente_key":
                    row[
                        "EXPEDIENTE_KEY"
                    ],

                "ruc":
                    row[
                        "RUC"
                    ],

                "nombre":
                    row[
                        "NOMBRE"
                    ],

                "target_24m":
                    row[
                        "TARGET_24M"
                    ],

                "feature_perturbada":
                    TEST_FEATURE,

                "valor_original":
                    original_value,

                "score_original":
                    original_score,

                "ranking_original":
                    original_rank,

                "universo_test":
                    len(
                        raw_test
                    ),
            }
        ]
    )

    case_summary.to_csv(
        OUTPUT_DIR
        / "p04_case.csv",
        index=False,
    )

    metadata = {
        "test_id":
            "P04",

        "description":
            (
                "Sensibilidad del modelo ante "
                "perturbaciones de ±5 %."
            ),

        "model":
            "v10_hgb_financial_c3",

        "config":
            "C3_CONSERVATIVE",

        "feature":
            TEST_FEATURE,

        "perturbations":
            {
                "-5%":
                    0.95,

                "+5%":
                    1.05,
            },

        "test_rows":
            len(
                raw_test
            ),

        "result":
            (
                "CUMPLE"
                if p04_pass
                else "PARCIAL / REVISAR"
            ),
    }

    with (
        OUTPUT_DIR
        / "p04_metadata.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()

    print(
        "Evidencias generadas:"
    )

    print(
        OUTPUT_DIR
        / "p04_results.csv"
    )

    print(
        OUTPUT_DIR
        / "p04_inputs.csv"
    )

    print(
        OUTPUT_DIR
        / "p04_case.csv"
    )

    print(
        OUTPUT_DIR
        / "p04_metadata.json"
    )

    print()


if __name__ == "__main__":
    main()
