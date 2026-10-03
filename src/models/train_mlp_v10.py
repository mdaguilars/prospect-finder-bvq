from pathlib import Path
from datetime import datetime, timezone
import json
import platform
import sys
import warnings

import joblib
import numpy as np
import pandas as pd
import sklearn

from sklearn.compose import ColumnTransformer
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.class_weight import compute_sample_weight


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "v10_features_core_2012_2023.csv.gz"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "results"
    / "v10"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
    / "v10"
)

MODEL_PATH = (
    MODEL_DIR
    / "v10_mlp.joblib"
)

METRICS_PATH = (
    OUTPUT_DIR
    / "v10_mlp_metrics.csv"
)

RANKING_PATH = (
    OUTPUT_DIR
    / "v10_mlp_ranking_metrics.csv"
)

LOSS_PATH = (
    OUTPUT_DIR
    / "v10_mlp_loss_curve.csv"
)

TOP500_PATH = (
    OUTPUT_DIR
    / "v10_mlp_validation_top500.csv"
)

METADATA_PATH = (
    OUTPUT_DIR
    / "v10_mlp_metadata.json"
)


MODEL_NAME = "v10_mlp"

TARGET = "TARGET_24M"

RANDOM_STATE = 42

THRESHOLD = 0.50

CHUNK_SIZE = 150_000

K_VALUES = [
    50,
    100,
    200,
]


# ============================================================
# FEATURES v10
# ============================================================

FEATURES_NUMERICAS = [
    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",
    "activos_final_t1",
    "patrimonio_final_t1",
    "bi_ingresos_ventas_t1",
    "bi_n_empleados_t1",
]


FEATURES_BOOLEANAS = [
    "TIENE_T_MENOS_1",
    "flag_activos_negativos",
    "flag_ventas_negativas",
    "flag_empleados_fijo",
    "flag_empleados_salto_temporal",
    "flag_empleados_anomalia_total",
]


FEATURES_CATEGORICAS = [
    "tipo_compania",
]


FEATURES = (
    FEATURES_NUMERICAS
    + FEATURES_BOOLEANAS
    + FEATURES_CATEGORICAS
)


COLUMNAS_CONTROL = [
    "ANIO",
    "EXPEDIENTE_KEY",
    "RUC",
    "NOMBRE",
    "provincia",
    "SPLIT",
    TARGET,
]


COLUMNAS_LECTURA = list(
    dict.fromkeys(
        COLUMNAS_CONTROL
        + FEATURES
    )
)


# ============================================================
# UNIVERSO ESPERADO
# ============================================================

EXPECTED_TRAIN_ROWS = 470_722
EXPECTED_TRAIN_POSITIVES = 407

EXPECTED_VALIDATION_ROWS = 98_471
EXPECTED_VALIDATION_POSITIVES = 34

EXPECTED_TRAIN_YEARS = {
    2012,
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,
}

EXPECTED_VALIDATION_YEARS = {
    2020,
}


# ============================================================
# CONFIGURACIÓN MLP
# ============================================================

MODEL_PARAMS = {
    "hidden_layer_sizes": (
        64,
        32,
    ),
    "activation": "relu",
    "solver": "adam",
    "alpha": 0.01,
    "batch_size": 512,
    "learning_rate": "constant",
    "learning_rate_init": 0.001,
    "max_iter": 200,
    "shuffle": True,
    "random_state": RANDOM_STATE,
    "tol": 1e-4,
    "early_stopping": False,
    "n_iter_no_change": 10,
    "verbose": False,
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def ruta_relativa(path):
    """
    Devuelve ruta relativa al proyecto.
    """

    return str(
        path.relative_to(PROJECT_ROOT)
    ).replace("\\", "/")


def normalizar_booleana(serie):
    """
    Convierte representaciones booleanas a 0/1.
    """

    texto = (
        serie
        .astype("string")
        .str.strip()
        .str.lower()
    )

    mapa = {
        "true": 1.0,
        "false": 0.0,
        "1": 1.0,
        "0": 0.0,
        "1.0": 1.0,
        "0.0": 0.0,
        "si": 1.0,
        "sí": 1.0,
        "no": 0.0,
        "yes": 1.0,
        "verdadero": 1.0,
        "falso": 0.0,
    }

    resultado_texto = texto.map(
        mapa
    )

    resultado_numerico = pd.to_numeric(
        serie,
        errors="coerce",
    )

    resultado_numerico = resultado_numerico.where(
        resultado_numerico.isin(
            [
                0,
                1,
            ]
        )
    )

    resultado = resultado_texto.fillna(
        resultado_numerico
    )

    return resultado.astype(
        "float64"
    )


# ============================================================
# MÉTRICAS GENERALES
# ============================================================

def metricas_clasificacion(
    y_true,
    scores,
    threshold,
):
    """
    Calcula métricas generales.

    predict_proba se utiliza como score de priorización.
    No se interpreta como probabilidad calibrada.
    """

    predicciones = (
        np.asarray(
            scores
        )
        >= threshold
    ).astype(
        int
    )

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predicciones,
        labels=[
            0,
            1,
        ],
    ).ravel()

    return {
        "PR_AUC":
            float(
                average_precision_score(
                    y_true,
                    scores,
                )
            ),

        "ROC_AUC":
            float(
                roc_auc_score(
                    y_true,
                    scores,
                )
            ),

        "THRESHOLD":
            float(
                threshold
            ),

        "PRECISION":
            float(
                precision_score(
                    y_true,
                    predicciones,
                    zero_division=0,
                )
            ),

        "RECALL":
            float(
                recall_score(
                    y_true,
                    predicciones,
                    zero_division=0,
                )
            ),

        "F1":
            float(
                f1_score(
                    y_true,
                    predicciones,
                    zero_division=0,
                )
            ),

        "TN":
            int(
                tn
            ),

        "FP":
            int(
                fp
            ),

        "FN":
            int(
                fn
            ),

        "TP":
            int(
                tp
            ),
    }


# ============================================================
# MÉTRICAS DE RANKING
# ============================================================

def metricas_ranking(
    y_true,
    scores,
):
    """
    Calcula Precision@K, Recall@K y Lift@K.
    """

    tabla = pd.DataFrame(
        {
            "TARGET":
                np.asarray(
                    y_true
                ),

            "SCORE":
                np.asarray(
                    scores
                ),
        }
    )

    tabla = tabla.sort_values(
        "SCORE",
        ascending=False,
        kind="mergesort",
    ).reset_index(
        drop=True
    )

    total = len(
        tabla
    )

    positivos_totales = int(
        tabla[
            "TARGET"
        ].sum()
    )

    prevalencia = (
        positivos_totales
        / total
        if total > 0
        else np.nan
    )

    resultados = []

    for k in K_VALUES:

        k_real = min(
            k,
            total,
        )

        top = tabla.head(
            k_real
        )

        positivos_top = int(
            top[
                "TARGET"
            ].sum()
        )

        precision_k = (
            positivos_top
            / k_real
            if k_real > 0
            else np.nan
        )

        recall_k = (
            positivos_top
            / positivos_totales
            if positivos_totales > 0
            else np.nan
        )

        lift_k = (
            precision_k
            / prevalencia
            if prevalencia > 0
            else np.nan
        )

        resultados.append(
            {
                "K":
                    int(
                        k
                    ),

                "POSITIVOS_TOP_K":
                    positivos_top,

                "POSITIVOS_TOTALES":
                    positivos_totales,

                "PREVALENCIA":
                    float(
                        prevalencia
                    ),

                "PRECISION_AT_K":
                    float(
                        precision_k
                    ),

                "RECALL_AT_K":
                    float(
                        recall_k
                    ),

                "LIFT_AT_K":
                    float(
                        lift_k
                    ),
            }
        )

    return resultados


# ============================================================
# CARGA DEL DATASET
# ============================================================

def cargar_desarrollo():
    """
    Carga exclusivamente TRAIN y VALIDATION.

    TEST 2022-2023 no se retiene para modelado,
    transformación ni evaluación.
    """

    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"No existe el dataset:\n{INPUT_PATH}"
        )

    encabezado = pd.read_csv(
        INPUT_PATH,
        nrows=0,
    )

    columnas_disponibles = set(
        encabezado.columns
    )

    faltantes = [
        columna
        for columna in COLUMNAS_LECTURA
        if columna not in columnas_disponibles
    ]

    if faltantes:

        raise ValueError(
            "Faltan columnas requeridas:\n"
            + "\n".join(
                faltantes
            )
        )

    print(
        "\nCargando dataset v10..."
    )

    print(
        f"Fuente: {INPUT_PATH}"
    )

    partes = []

    for chunk in pd.read_csv(
        INPUT_PATH,
        usecols=COLUMNAS_LECTURA,
        chunksize=CHUNK_SIZE,
        low_memory=False,
        dtype={
            "RUC": "string",
            "NOMBRE": "string",
            "SPLIT": "string",
            "tipo_compania": "string",
            "provincia": "string",
        },
    ):

        split_normalizado = (
            chunk[
                "SPLIT"
            ]
            .astype(
                "string"
            )
            .str.strip()
            .str.upper()
        )

        mascara = split_normalizado.isin(
            [
                "TRAIN",
                "VALIDATION",
            ]
        )

        if mascara.any():

            bloque = chunk.loc[
                mascara
            ].copy()

            bloque[
                "SPLIT"
            ] = split_normalizado.loc[
                mascara
            ]

            partes.append(
                bloque
            )

    if not partes:

        raise ValueError(
            "No se encontraron observaciones TRAIN/VALIDATION."
        )

    df = pd.concat(
        partes,
        ignore_index=True,
    )

    return preparar_tipos(
        df
    )


# ============================================================
# PREPARAR TIPOS
# ============================================================

def preparar_tipos(df):
    """
    Normaliza tipos sin aprender información estadística.
    """

    df = df.copy()

    # --------------------------------------------------------
    # ANIO
    # --------------------------------------------------------

    df[
        "ANIO"
    ] = pd.to_numeric(
        df[
            "ANIO"
        ],
        errors="coerce",
    )

    if df[
        "ANIO"
    ].isna().any():

        raise ValueError(
            "Existen valores inválidos en ANIO."
        )

    df[
        "ANIO"
    ] = df[
        "ANIO"
    ].astype(
        int
    )

    # --------------------------------------------------------
    # TARGET
    # --------------------------------------------------------

    df[
        TARGET
    ] = pd.to_numeric(
        df[
            TARGET
        ],
        errors="coerce",
    )

    if df[
        TARGET
    ].isna().any():

        raise ValueError(
            "Existen valores inválidos en TARGET_24M."
        )

    valores_target = set(
        df[
            TARGET
        ]
        .unique()
        .tolist()
    )

    if not valores_target.issubset(
        {
            0,
            1,
        }
    ):

        raise ValueError(
            "TARGET_24M contiene valores distintos de 0 y 1."
        )

    df[
        TARGET
    ] = df[
        TARGET
    ].astype(
        int
    )

    # --------------------------------------------------------
    # NUMÉRICAS
    # --------------------------------------------------------

    for variable in FEATURES_NUMERICAS:

        df[
            variable
        ] = pd.to_numeric(
            df[
                variable
            ],
            errors="coerce",
        )

    df[
        FEATURES_NUMERICAS
    ] = df[
        FEATURES_NUMERICAS
    ].replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )

    # --------------------------------------------------------
    # BOOLEANAS
    # --------------------------------------------------------

    for variable in FEATURES_BOOLEANAS:

        df[
            variable
        ] = normalizar_booleana(
            df[
                variable
            ]
        )

    # --------------------------------------------------------
    # CATEGÓRICAS
    # --------------------------------------------------------

    for variable in FEATURES_CATEGORICAS:

        serie = df[
            variable
        ].astype(
            "string"
        )

        df[
            variable
        ] = np.where(
            serie.isna(),
            np.nan,
            serie.astype(
                object
            ),
        )

    return df


# ============================================================
# VALIDAR SPLITS
# ============================================================

def validar_splits(
    train,
    validation,
):
    """
    Verifica exactamente el universo congelado v10.
    """

    train_rows = len(
        train
    )

    train_pos = int(
        train[
            TARGET
        ].sum()
    )

    validation_rows = len(
        validation
    )

    validation_pos = int(
        validation[
            TARGET
        ].sum()
    )

    train_years = set(
        train[
            "ANIO"
        ].unique()
        .tolist()
    )

    validation_years = set(
        validation[
            "ANIO"
        ].unique()
        .tolist()
    )

    if train_rows != EXPECTED_TRAIN_ROWS:

        raise ValueError(
            "TRAIN filas incorrectas. "
            f"Esperado={EXPECTED_TRAIN_ROWS:,}, "
            f"observado={train_rows:,}."
        )

    if train_pos != EXPECTED_TRAIN_POSITIVES:

        raise ValueError(
            "TRAIN positivos incorrectos. "
            f"Esperado={EXPECTED_TRAIN_POSITIVES}, "
            f"observado={train_pos}."
        )

    if validation_rows != EXPECTED_VALIDATION_ROWS:

        raise ValueError(
            "VALIDATION filas incorrectas. "
            f"Esperado={EXPECTED_VALIDATION_ROWS:,}, "
            f"observado={validation_rows:,}."
        )

    if validation_pos != EXPECTED_VALIDATION_POSITIVES:

        raise ValueError(
            "VALIDATION positivos incorrectos. "
            f"Esperado={EXPECTED_VALIDATION_POSITIVES}, "
            f"observado={validation_pos}."
        )

    if train_years != EXPECTED_TRAIN_YEARS:

        raise ValueError(
            "Años TRAIN diferentes al protocolo v10. "
            f"Observado={sorted(train_years)}."
        )

    if validation_years != EXPECTED_VALIDATION_YEARS:

        raise ValueError(
            "Año VALIDATION diferente al protocolo v10. "
            f"Observado={sorted(validation_years)}."
        )

    print(
        "\nSplit validado:"
    )

    print(
        f"TRAIN: {train_rows:,} filas | "
        f"{train_pos} positivos"
    )

    print(
        f"VALIDATION: {validation_rows:,} filas | "
        f"{validation_pos} positivos"
    )


# ============================================================
# PREPROCESAMIENTO
# ============================================================

def construir_preprocesador():
    """
    Construye preprocesamiento aprendido exclusivamente
    desde TRAIN.

    Numéricas:
        mediana + StandardScaler.

    Booleanas:
        imputación más frecuente.

    Categóricas:
        categoría faltante explícita + One-Hot Encoding
        con manejo de categorías desconocidas.
    """

    pipeline_numerico = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
        ]
    )

    pipeline_booleano = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                ),
            ),
        ]
    )

    pipeline_categorico = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="constant",
                    fill_value="__MISSING__",
                ),
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                    dtype=np.float64,
                ),
            ),
        ]
    )

    preprocesador = ColumnTransformer(
        transformers=[
            (
                "numeric",
                pipeline_numerico,
                FEATURES_NUMERICAS,
            ),
            (
                "boolean",
                pipeline_booleano,
                FEATURES_BOOLEANAS,
            ),
            (
                "categorical",
                pipeline_categorico,
                FEATURES_CATEGORICAS,
            ),
        ],
        remainder="drop",
        sparse_threshold=0,
        verbose_feature_names_out=True,
    )

    return preprocesador


# ============================================================
# TOP 500 VALIDATION
# ============================================================

def construir_top500(
    validation,
    scores,
):
    """
    Genera ranking local para revisión operativa.

    Este archivo contiene identificadores empresariales
    y permanece excluido de Git.
    """

    columnas = [
        "ANIO",
        "EXPEDIENTE_KEY",
        "RUC",
        "NOMBRE",
        "tipo_compania",
        "provincia",
        TARGET,
    ]

    ranking = validation[
        columnas
    ].copy()

    ranking[
        "SCORE"
    ] = np.asarray(
        scores
    )

    ranking = ranking.sort_values(
        "SCORE",
        ascending=False,
        kind="mergesort",
    ).reset_index(
        drop=True
    )

    ranking[
        "RANK"
    ] = np.arange(
        1,
        len(
            ranking
        ) + 1,
    )

    ranking = ranking[
        [
            "RANK",
            "SCORE",
            TARGET,
            "ANIO",
            "EXPEDIENTE_KEY",
            "RUC",
            "NOMBRE",
            "tipo_compania",
            "provincia",
        ]
    ]

    return ranking.head(
        500
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        + "=" * 110
    )

    print(
        "PROSPECT FINDER BVQ"
    )

    print(
        "MLP v10"
    )

    print(
        "=" * 110
    )

    print(
        "\nConfiguración:"
    )

    print(
        "Dataset: v10_features_core_2012_2023.csv.gz"
    )

    print(
        "TRAIN: 2012-2018"
    )

    print(
        "VALIDATION: 2020"
    )

    print(
        "TEST 2022-2023: RESERVADO - SIN EVALUACIÓN"
    )

    print(
        f"Features físicas: {len(FEATURES)}"
    )

    print(
        "Provincia como predictor: NO"
    )

    print(
        "tipo_compania: One-Hot Encoding"
    )

    print(
        "Arquitectura: 64 -> 32"
    )

    print(
        "Configuración inicial: heredada de v9, sin tuning v10"
    )

    # --------------------------------------------------------
    # CARGAR
    # --------------------------------------------------------

    df = cargar_desarrollo()

    train = df[
        df[
            "SPLIT"
        ]
        == "TRAIN"
    ].copy()

    validation = df[
        df[
            "SPLIT"
        ]
        == "VALIDATION"
    ].copy()

    validar_splits(
        train,
        validation,
    )

    # --------------------------------------------------------
    # X / y
    # --------------------------------------------------------

    X_train_raw = train[
        FEATURES
    ].copy()

    y_train = train[
        TARGET
    ].astype(
        int
    )

    X_validation_raw = validation[
        FEATURES
    ].copy()

    y_validation = validation[
        TARGET
    ].astype(
        int
    )

    # --------------------------------------------------------
    # PREPROCESAMIENTO
    # --------------------------------------------------------

    print(
        "\nAjustando preprocesamiento exclusivamente con TRAIN..."
    )

    preprocesador = construir_preprocesador()

    X_train = preprocesador.fit_transform(
        X_train_raw
    )

    X_validation = preprocesador.transform(
        X_validation_raw
    )

    nombres_features_transformadas = (
        preprocesador
        .get_feature_names_out()
        .tolist()
    )

    print(
        f"Features transformadas: "
        f"{X_train.shape[1]}"
    )

    # --------------------------------------------------------
    # PESOS DE CLASE
    # --------------------------------------------------------

    sample_weights = compute_sample_weight(
        class_weight="balanced",
        y=y_train,
    )

    pesos_clase_0 = sample_weights[
        y_train.to_numpy()
        == 0
    ]

    pesos_clase_1 = sample_weights[
        y_train.to_numpy()
        == 1
    ]

    print(
        "\nPesos de entrenamiento:"
    )

    print(
        f"Peso clase 0: "
        f"{pesos_clase_0[0]:.6f}"
    )

    print(
        f"Peso clase 1: "
        f"{pesos_clase_1[0]:.6f}"
    )

    print(
        f"Media pesos: "
        f"{sample_weights.mean():.6f}"
    )

    # --------------------------------------------------------
    # MODELO
    # --------------------------------------------------------

    modelo = MLPClassifier(
        **MODEL_PARAMS
    )

    print(
        "\nEntrenando MLP v10..."
    )

    convergence_warning = False

    with warnings.catch_warnings(
        record=True
    ) as advertencias:

        warnings.simplefilter(
            "always"
        )

        modelo.fit(
            X_train,
            y_train,
            sample_weight=sample_weights,
        )

        convergence_warning = any(
            issubclass(
                advertencia.category,
                ConvergenceWarning,
            )
            for advertencia in advertencias
        )

    print(
        "Entrenamiento finalizado."
    )

    print(
        f"Iteraciones utilizadas: "
        f"{modelo.n_iter_}"
    )

    print(
        f"Loss final: "
        f"{modelo.loss_:.9f}"
    )

    print(
        f"ConvergenceWarning: "
        f"{convergence_warning}"
    )

    # --------------------------------------------------------
    # PREDICCIONES
    # --------------------------------------------------------

    scores_train = modelo.predict_proba(
        X_train
    )[:, 1]

    scores_validation = modelo.predict_proba(
        X_validation
    )[:, 1]

    # --------------------------------------------------------
    # MÉTRICAS
    # --------------------------------------------------------

    resultados_metricas = []

    resultados_ranking = []

    datasets = [
        (
            "TRAIN",
            y_train,
            scores_train,
        ),
        (
            "VALIDATION",
            y_validation,
            scores_validation,
        ),
    ]

    print(
        "\n"
        + "=" * 110
    )

    print(
        "RESULTADOS"
    )

    print(
        "=" * 110
    )

    for (
        split,
        y_split,
        scores_split,
    ) in datasets:

        resultado = metricas_clasificacion(
            y_split,
            scores_split,
            THRESHOLD,
        )

        resultado[
            "SPLIT"
        ] = split

        resultado[
            "OBSERVACIONES"
        ] = int(
            len(
                y_split
            )
        )

        resultado[
            "POSITIVOS"
        ] = int(
            y_split.sum()
        )

        resultado[
            "PREVALENCIA"
        ] = float(
            y_split.mean()
        )

        resultados_metricas.append(
            resultado
        )

        ranking_split = metricas_ranking(
            y_split,
            scores_split,
        )

        for fila in ranking_split:

            fila[
                "SPLIT"
            ] = split

            resultados_ranking.append(
                fila
            )

        print(
            f"\n{split}"
        )

        print(
            f"PR-AUC:  "
            f"{resultado['PR_AUC']:.9f}"
        )

        print(
            f"ROC-AUC: "
            f"{resultado['ROC_AUC']:.9f}"
        )

        if split == "VALIDATION":

            print(
                "\nRanking VALIDATION:"
            )

            for fila in ranking_split:

                print(
                    f"Top {fila['K']:>3}: "
                    f"{fila['POSITIVOS_TOP_K']} positivos | "
                    f"Precision={fila['PRECISION_AT_K']:.6f} | "
                    f"Recall={fila['RECALL_AT_K']:.6f} | "
                    f"Lift={fila['LIFT_AT_K']:.6f}"
                )

    # --------------------------------------------------------
    # DATAFRAMES
    # --------------------------------------------------------

    metricas_df = pd.DataFrame(
        resultados_metricas
    )

    metricas_df = metricas_df[
        [
            "SPLIT",
            "OBSERVACIONES",
            "POSITIVOS",
            "PREVALENCIA",
            "PR_AUC",
            "ROC_AUC",
            "THRESHOLD",
            "PRECISION",
            "RECALL",
            "F1",
            "TN",
            "FP",
            "FN",
            "TP",
        ]
    ]

    ranking_df = pd.DataFrame(
        resultados_ranking
    )

    ranking_df = ranking_df[
        [
            "SPLIT",
            "K",
            "POSITIVOS_TOP_K",
            "POSITIVOS_TOTALES",
            "PREVALENCIA",
            "PRECISION_AT_K",
            "RECALL_AT_K",
            "LIFT_AT_K",
        ]
    ]

    loss_df = pd.DataFrame(
        {
            "ITERACION":
                np.arange(
                    1,
                    len(
                        modelo.loss_curve_
                    ) + 1,
                ),

            "LOSS":
                modelo.loss_curve_,
        }
    )

    top500_df = construir_top500(
        validation,
        scores_validation,
    )

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metricas_df.to_csv(
        METRICS_PATH,
        index=False,
    )

    ranking_df.to_csv(
        RANKING_PATH,
        index=False,
    )

    loss_df.to_csv(
        LOSS_PATH,
        index=False,
    )

    top500_df.to_csv(
        TOP500_PATH,
        index=False,
    )

    joblib.dump(
        {
            "preprocessor":
                preprocesador,

            "model":
                modelo,

            "features":
                FEATURES,

            "features_numericas":
                FEATURES_NUMERICAS,

            "features_booleanas":
                FEATURES_BOOLEANAS,

            "features_categoricas":
                FEATURES_CATEGORICAS,

            "transformed_feature_names":
                nombres_features_transformadas,
        },
        MODEL_PATH,
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    metadata = {
        "experimento":
            "MLP v10",

        "modelo":
            "MLPClassifier",

        "nombre_modelo":
            MODEL_NAME,

        "fecha_ejecucion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "dataset":
            ruta_relativa(
                INPUT_PATH
            ),

        "target":
            TARGET,

        "horizonte_target":
            "24 meses",

        "split_temporal": {
            "train":
                "2012-2018",

            "embargo_validation":
                "2019",

            "validation":
                "2020",

            "embargo_test":
                "2021",

            "test":
                "2022-2023",
        },

        "train": {
            "observaciones":
                int(
                    len(
                        train
                    )
                ),

            "positivos":
                int(
                    y_train.sum()
                ),
        },

        "validation": {
            "observaciones":
                int(
                    len(
                        validation
                    )
                ),

            "positivos":
                int(
                    y_validation.sum()
                ),
        },

        "test_evaluado":
            False,

        "nota_test":
            (
                "TEST 2022-2023 permanece reservado. "
                "No se transforma, predice ni evalua."
            ),

        "features_numericas":
            FEATURES_NUMERICAS,

        "features_booleanas":
            FEATURES_BOOLEANAS,

        "features_categoricas":
            FEATURES_CATEGORICAS,

        "numero_features_fisicas":
            len(
                FEATURES
            ),

        "numero_features_transformadas":
            int(
                X_train.shape[
                    1
                ]
            ),

        "features_transformadas":
            nombres_features_transformadas,

        "provincia_utilizada_como_predictor":
            False,

        "preprocesamiento": {
            "numericas":
                (
                    "SimpleImputer(strategy='median') + "
                    "StandardScaler; ambos ajustados "
                    "exclusivamente con TRAIN."
                ),

            "booleanas":
                (
                    "SimpleImputer(strategy='most_frequent') "
                    "ajustado exclusivamente con TRAIN."
                ),

            "categoricas":
                (
                    "SimpleImputer con categoria faltante "
                    "explicita + OneHotEncoder("
                    "handle_unknown='ignore'), "
                    "ajustados exclusivamente con TRAIN."
                ),
        },

        "arquitectura": {
            "hidden_layer_sizes":
                [
                    64,
                    32,
                ],

            "activation":
                "relu",

            "solver":
                "adam",
        },

        "configuracion_modelo":
            {
                "alpha":
                    0.01,

                "batch_size":
                    512,

                "learning_rate":
                    "constant",

                "learning_rate_init":
                    0.001,

                "max_iter":
                    200,

                "shuffle":
                    True,

                "random_state":
                    RANDOM_STATE,

                "tol":
                    1e-4,

                "early_stopping":
                    False,

                "n_iter_no_change":
                    10,
            },

        "origen_configuracion":
            (
                "Arquitectura controlada heredada de v9. "
                "No se realiza tuning en este primer "
                "experimento MLP v10."
            ),

        "manejo_desbalance":
            (
                "sample_weight calculado mediante "
                "compute_sample_weight("
                "class_weight='balanced') "
                "exclusivamente con TRAIN."
            ),

        "peso_clase_0":
            float(
                pesos_clase_0[
                    0
                ]
            ),

        "peso_clase_1":
            float(
                pesos_clase_1[
                    0
                ]
            ),

        "entrenamiento": {
            "iteraciones_utilizadas":
                int(
                    modelo.n_iter_
                ),

            "loss_final":
                float(
                    modelo.loss_
                ),

            "convergence_warning":
                bool(
                    convergence_warning
                ),
        },

        "threshold_evaluacion":
            THRESHOLD,

        "k_ranking":
            K_VALUES,

        "scores_calibrados":
            False,

        "nota_calibracion":
            (
                "predict_proba se utiliza como score de "
                "priorizacion y no como probabilidad "
                "calibrada."
            ),

        "tuning_realizado":
            False,

        "comparadores_v10": [
            "v10_lr_no_provincia",
            "v10_hgb",
        ],

        "entorno": {
            "python":
                sys.version.split()[0],

            "platform":
                platform.platform(),

            "pandas":
                pd.__version__,

            "numpy":
                np.__version__,

            "scikit_learn":
                sklearn.__version__,
        },

        "archivos_salida": {
            "metricas":
                ruta_relativa(
                    METRICS_PATH
                ),

            "ranking":
                ruta_relativa(
                    RANKING_PATH
                ),

            "loss_curve":
                ruta_relativa(
                    LOSS_PATH
                ),

            "top500_local":
                ruta_relativa(
                    TOP500_PATH
                ),

            "metadata":
                ruta_relativa(
                    METADATA_PATH
                ),

            "modelo_local":
                ruta_relativa(
                    MODEL_PATH
                ),
        },
    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8",
    ) as archivo:

        json.dump(
            metadata,
            archivo,
            ensure_ascii=False,
            indent=2,
        )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print(
        "\nArchivos generados:"
    )

    print(
        METRICS_PATH
    )

    print(
        RANKING_PATH
    )

    print(
        LOSS_PATH
    )

    print(
        TOP500_PATH
    )

    print(
        METADATA_PATH
    )

    print(
        "\nModelo local:"
    )

    print(
        MODEL_PATH
    )

    print(
        "\nTEST 2022-2023:"
    )

    print(
        "RESERVADO - SIN EVALUACIÓN"
    )

    print(
        "\nMLP v10 finalizado."
    )


if __name__ == "__main__":
    main()