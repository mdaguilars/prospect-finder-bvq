"""
P05 · Utilidad comercial Top-K
Prospect Finder BVQ

Objetivo
--------
Evaluar la utilidad del ranking del modelo v10 sobre el conjunto
TEST intacto mediante:

- Precision@20
- Recall@20
- Precision@50
- Recall@50
- Precision@100
- Recall@100

Adicionalmente se calcula:

- Lift@K;
- porcentaje del universo que requiere revisión;
- posición del primer positivo real;
- posiciones de todos los positivos reales;
- tabla de las primeras 100 empresas del ranking.

IMPORTANTE
----------
Esta prueba NO:

- modifica TEST;
- modifica features;
- modifica el modelo;
- reentrena;
- ajusta hiperparámetros;
- cambia el ranking operacional;
- cambia los resultados oficiales.

Las evidencias se guardan en:

    reports/live_tests/P05/
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
    / "P05"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

TOP_K_VALUES = [
    20,
    50,
    100,
]

EXPECTED_TEST_N = 260_445
EXPECTED_TEST_POSITIVES = 54


# ============================================================
# UTILIDADES
# ============================================================

def header(
    title: str,
) -> None:

    print()
    print("=" * 104)
    print(title)
    print("=" * 104)
    print()


# ============================================================
# ARTEFACTO
# ============================================================

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


# ============================================================
# CATEGORÍAS APRENDIDAS EXCLUSIVAMENTE DESDE TRAIN
# ============================================================

def load_train_categories(
    categorical_features: list[str],
) -> dict[str, list[str]]:

    category_sets = {
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


# ============================================================
# PREPARACIÓN DE FEATURES
# ============================================================

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


# ============================================================
# CARGA TEST INTACTO
# ============================================================

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

    frames = []

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

    test = pd.concat(
        frames,
        ignore_index=True,
    )

    return test


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    header(
        "P05 · UTILIDAD COMERCIAL TOP-K"
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
        "Conjunto:"
    )
    print(
        "TEST 2022-2023 intacto"
    )

    # --------------------------------------------------------
    # MODELO
    # --------------------------------------------------------

    artifact = load_artifact()

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

    print()

    print(
        "Features:"
    )
    print(
        len(
            features
        )
    )

    # --------------------------------------------------------
    # CATEGORÍAS
    # --------------------------------------------------------

    print()

    print(
        "Cargando categorías exclusivamente "
        "desde TRAIN..."
    )

    train_categories = (
        load_train_categories(
            categorical_features
        )
    )

    # --------------------------------------------------------
    # TEST
    # --------------------------------------------------------

    print(
        "Cargando TEST..."
    )

    test = load_test(
        features
    )

    test_n = len(
        test
    )

    test_positives = int(
        test[
            "TARGET_24M"
        ].sum()
    )

    prevalence = (
        test_positives
        / test_n
    )

    print()

    print(
        f"Observaciones TEST: "
        f"{test_n:,}"
    )

    print(
        f"Positivos TEST: "
        f"{test_positives:,}"
    )

    print(
        f"Prevalencia: "
        f"{prevalence:.9f}"
    )

    # --------------------------------------------------------
    # VALIDACIÓN DEL UNIVERSO
    # --------------------------------------------------------

    if test_n != EXPECTED_TEST_N:

        raise RuntimeError(
            "El número de observaciones TEST "
            "no coincide con el resultado oficial."
        )

    if (
        test_positives
        != EXPECTED_TEST_POSITIVES
    ):

        raise RuntimeError(
            "El número de positivos TEST "
            "no coincide con el resultado oficial."
        )

    print()

    print(
        "Universo TEST validado:"
    )
    print(
        "260.445 observaciones / 54 positivos"
    )

    # --------------------------------------------------------
    # PREPARACIÓN
    # --------------------------------------------------------

    print()

    print(
        "Preparando matriz predictora..."
    )

    x_test = (
        prepare_feature_frame(
            test,
            artifact,
            train_categories,
        )
    )

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    print(
        "Calculando scores..."
    )

    scores = (
        model.predict_proba(
            x_test
        )[
            :,
            1,
        ]
    )

    if not np.all(
        np.isfinite(
            scores
        )
    ):

        raise RuntimeError(
            "Se generaron scores no finitos."
        )

    # --------------------------------------------------------
    # RANKING
    # --------------------------------------------------------

    ranking = test[
        [
            "ANIO",
            "EXPEDIENTE_KEY",
            "RUC",
            "NOMBRE",
            "TARGET_24M",
        ]
    ].copy()

    ranking[
        "SCORE_V10"
    ] = scores

    ranking = (
        ranking
        .sort_values(
            [
                "SCORE_V10",
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

    ranking.insert(
        0,
        "RANKING",
        np.arange(
            1,
            len(
                ranking
            )
            + 1,
        ),
    )

    # --------------------------------------------------------
    # TOP-K
    # --------------------------------------------------------

    header(
        "RESULTADOS TOP-K"
    )

    rows = []

    for k in TOP_K_VALUES:

        top = ranking.head(
            k
        )

        positives_top_k = int(
            top[
                "TARGET_24M"
            ].sum()
        )

        precision_at_k = (
            positives_top_k
            / k
        )

        recall_at_k = (
            positives_top_k
            / test_positives
        )

        lift_at_k = (
            precision_at_k
            / prevalence
            if prevalence > 0
            else np.nan
        )

        review_pct = (
            k
            / test_n
            * 100
        )

        print(
            f"Top {k:>3}: "
            f"{positives_top_k} positivos"
        )

        print(
            f"  Precision@{k}: "
            f"{precision_at_k:.6f}"
        )

        print(
            f"  Recall@{k}:    "
            f"{recall_at_k:.6f}"
        )

        print(
            f"  Lift@{k}:      "
            f"{lift_at_k:.6f}"
        )

        print(
            f"  Universo a revisar: "
            f"{review_pct:.6f}%"
        )

        if positives_top_k == 0:

            print(
                "  ADVERTENCIA: "
                "este Top-K no identifica "
                "positivos conocidos."
            )

        print()

        rows.append(
            {
                "K":
                    k,

                "TOTAL_TEST":
                    test_n,

                "POSITIVOS_TEST":
                    test_positives,

                "PREVALENCIA":
                    prevalence,

                "POSITIVOS_TOP_K":
                    positives_top_k,

                "PRECISION_AT_K":
                    precision_at_k,

                "RECALL_AT_K":
                    recall_at_k,

                "LIFT_AT_K":
                    lift_at_k,

                "EMPRESAS_A_REVISAR":
                    k,

                "PORCENTAJE_UNIVERSO_REVISADO":
                    review_pct,
            }
        )

    metrics = pd.DataFrame(
        rows
    )

    # --------------------------------------------------------
    # POSICIONES DE POSITIVOS
    # --------------------------------------------------------

    positives = (
        ranking[
            ranking[
                "TARGET_24M"
            ].eq(
                1
            )
        ]
        .copy()
        .reset_index(
            drop=True
        )
    )

    if positives.empty:

        raise RuntimeError(
            "TEST no contiene positivos, "
            "contrario a la validación previa."
        )

    first_positive_rank = int(
        positives[
            "RANKING"
        ].min()
    )

    header(
        "RECUPERACIÓN DE POSITIVOS"
    )

    print(
        "Primer positivo conocido aparece "
        "en la posición:"
    )

    print(
        f"{first_positive_rank:,}"
    )

    print()

    print(
        "Primeros positivos recuperados:"
    )

    print(
        positives[
            [
                "RANKING",
                "ANIO",
                "EXPEDIENTE_KEY",
                "NOMBRE",
                "SCORE_V10",
            ]
        ]
        .head(
            10
        )
        .to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # INTERPRETACIÓN COMERCIAL
    # --------------------------------------------------------

    header(
        "INTERPRETACIÓN COMERCIAL"
    )

    top_100_positives = int(
        metrics.loc[
            metrics[
                "K"
            ].eq(
                100
            ),
            "POSITIVOS_TOP_K",
        ].iloc[
            0
        ]
    )

    if top_100_positives == 0:

        print(
            "El Top 100 del período TEST no "
            "recupera positivos conocidos."
        )

        print()

        print(
            "Esto limita la evidencia de utilidad "
            "comercial del modelo cuando la capacidad "
            "operativa se restringe estrictamente "
            "a las primeras 100 empresas."
        )

        print()

        print(
            "El resultado no invalida automáticamente "
            "la capacidad general de ordenamiento del "
            "modelo, pero obliga a reportar esta "
            "limitación y evita concluir utilidad "
            "comercial únicamente a partir de ROC-AUC."
        )

    else:

        print(
            "El Top 100 recupera al menos un "
            "positivo conocido."
        )

    # --------------------------------------------------------
    # ESTADO DE LA PRUEBA
    # --------------------------------------------------------

    calculations_valid = bool(
        len(
            metrics
        )
        == len(
            TOP_K_VALUES
        )
        and
        test_n
        == EXPECTED_TEST_N
        and
        test_positives
        == EXPECTED_TEST_POSITIVES
    )

    header(
        "RESULTADO P05"
    )

    if calculations_valid:

        print(
            "CUMPLE"
        )

        print()

        print(
            "Las métricas Top-K fueron "
            "calculadas correctamente sobre "
            "TEST intacto."
        )

        print()

        print(
            "IMPORTANTE:"
        )

        print(
            "CUMPLE significa que la prueba "
            "fue ejecutada y reportada de forma "
            "correcta; no significa que los "
            "Top-K hayan mostrado alta utilidad "
            "comercial."
        )

    else:

        print(
            "NO CUMPLE / REVISAR"
        )

    # --------------------------------------------------------
    # EVIDENCIAS
    # --------------------------------------------------------

    metrics_path = (
        OUTPUT_DIR
        / "p05_topk_metrics.csv"
    )

    metrics.to_csv(
        metrics_path,
        index=False,
    )

    top100_path = (
        OUTPUT_DIR
        / "p05_top100.csv"
    )

    ranking.head(
        100
    ).to_csv(
        top100_path,
        index=False,
    )

    positives_path = (
        OUTPUT_DIR
        / "p05_positive_positions.csv"
    )

    positives.to_csv(
        positives_path,
        index=False,
    )

    # Top 200 adicional como contexto,
    # sin sustituir los K solicitados por el tutor.

    top200 = ranking.head(
        200
    ).copy()

    top200_path = (
        OUTPUT_DIR
        / "p05_top200_context.csv"
    )

    top200.to_csv(
        top200_path,
        index=False,
    )

    metadata = {
        "test_id":
            "P05",

        "model":
            "v10_hgb_financial_c3",

        "config":
            "C3_CONSERVATIVE",

        "test_period":
            "2022-2023",

        "test_rows":
            test_n,

        "test_positives":
            test_positives,

        "prevalence":
            prevalence,

        "top_k_values":
            TOP_K_VALUES,

        "first_positive_rank":
            first_positive_rank,

        "result":
            (
                "CUMPLE"
                if calculations_valid
                else "NO CUMPLE / REVISAR"
            ),

        "interpretation":
            (
                "La ejecución de la prueba cumple. "
                "La utilidad comercial Top-K debe "
                "interpretarse separadamente."
            ),
    }

    with (
        OUTPUT_DIR
        / "p05_metadata.json"
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
        metrics_path
    )

    print(
        top100_path
    )

    print(
        positives_path
    )

    print(
        top200_path
    )

    print(
        OUTPUT_DIR
        / "p05_metadata.json"
    )

    print()


if __name__ == "__main__":
    main()