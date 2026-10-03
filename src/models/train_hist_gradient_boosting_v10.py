from pathlib import Path
from datetime import datetime, timezone
import json
import platform
import sys

import joblib
import numpy as np
import pandas as pd
import sklearn

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


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
    / "v10_hgb.joblib"
)

METRICS_PATH = (
    OUTPUT_DIR
    / "v10_hgb_metrics.csv"
)

RANKING_PATH = (
    OUTPUT_DIR
    / "v10_hgb_ranking_metrics.csv"
)

TOP500_PATH = (
    OUTPUT_DIR
    / "v10_hgb_validation_top500.csv"
)

METADATA_PATH = (
    OUTPUT_DIR
    / "v10_hgb_metadata.json"
)


MODEL_NAME = "v10_hgb"

TARGET = "TARGET_24M"

RANDOM_STATE = 42

THRESHOLD = 0.5

K_VALUES = [
    50,
    100,
    200,
]

CHUNK_SIZE = 150_000


# ============================================================
# FEATURES
# ============================================================

# Se utilizan las mismas variables físicas del baseline
# logístico seleccionado:
#
# v10_lr_no_provincia
#
# provincia queda excluida del modelo.

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


# ============================================================
# COLUMNAS DE CONTROL
# ============================================================

COLUMNAS_IDENTIFICACION = [
    "ANIO",
    "EXPEDIENTE_KEY",
    "RUC",
    "NOMBRE",
    "provincia",
]


COLUMNAS_LECTURA = (
    COLUMNAS_IDENTIFICACION
    + [
        "SPLIT",
        TARGET,
    ]
    + FEATURES
)


# ============================================================
# UNIVERSOS ESPERADOS v10
# ============================================================

EXPECTED_TRAIN_ROWS = 470_722
EXPECTED_TRAIN_POSITIVES = 407

EXPECTED_VALIDATION_ROWS = 98_471
EXPECTED_VALIDATION_POSITIVES = 34

EXPECTED_TRAIN_YEARS = [
    2012,
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,
]

EXPECTED_VALIDATION_YEARS = [
    2020,
]


# ============================================================
# CONFIGURACIÓN HISTGRADIENTBOOSTING
# ============================================================

# Configuración regularizada heredada de v8.
#
# No se realiza tuning con VALIDATION para este primer
# experimento v10.
#
# El objetivo es evaluar la misma configuración no lineal
# sobre el dataset y feature set v10.

MODEL_PARAMS = {
    "loss": "log_loss",
    "learning_rate": 0.05,
    "max_iter": 150,
    "max_leaf_nodes": 7,
    "max_depth": 3,
    "min_samples_leaf": 100,
    "l2_regularization": 1.0,
    "early_stopping": False,
    "random_state": RANDOM_STATE,
    "class_weight": "balanced",
    "categorical_features": "from_dtype",
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def ruta_relativa(path):
    """
    Devuelve una ruta relativa al proyecto.
    """

    return str(
        path.relative_to(PROJECT_ROOT)
    ).replace("\\", "/")


def normalizar_booleana(serie):
    """
    Convierte distintas representaciones booleanas a 0/1.
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
# CARGA DE DATOS
# ============================================================

def cargar_desarrollo():
    """
    Carga exclusivamente TRAIN y VALIDATION.

    EMBARGO_1 2019, EMBARGO_2 2021 y TEST 2022-2023
    no se incorporan al dataframe de desarrollo.
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

    columnas_faltantes = [
        columna
        for columna in COLUMNAS_LECTURA
        if columna not in columnas_disponibles
    ]

    if columnas_faltantes:

        raise ValueError(
            "Faltan columnas requeridas:\n"
            + "\n".join(
                columnas_faltantes
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
            chunk["SPLIT"]
            .astype("string")
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

            partes.append(
                chunk.loc[
                    mascara
                ].copy()
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
# PREPARACIÓN DETERMINÍSTICA
# ============================================================

def preparar_tipos(df):
    """
    Normaliza tipos sin aprender parámetros desde VALIDATION.

    HistGradientBoosting manejará directamente los valores
    faltantes numéricos.
    """

    df = df.copy()

    # --------------------------------------------------------
    # ANIO
    # --------------------------------------------------------

    df["ANIO"] = pd.to_numeric(
        df["ANIO"],
        errors="coerce",
    )

    if df["ANIO"].isna().any():

        raise ValueError(
            "Existen valores ANIO inválidos."
        )

    df["ANIO"] = df["ANIO"].astype(
        int
    )

    # --------------------------------------------------------
    # TARGET
    # --------------------------------------------------------

    df[TARGET] = pd.to_numeric(
        df[TARGET],
        errors="coerce",
    )

    if df[TARGET].isna().any():

        raise ValueError(
            "Existen valores TARGET_24M inválidos."
        )

    valores_target = set(
        df[TARGET].unique().tolist()
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

    df[TARGET] = df[TARGET].astype(
        int
    )

    # --------------------------------------------------------
    # NUMÉRICAS
    # --------------------------------------------------------

    for variable in FEATURES_NUMERICAS:

        df[variable] = pd.to_numeric(
            df[variable],
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

        df[variable] = normalizar_booleana(
            df[variable]
        )

    # --------------------------------------------------------
    # CATEGÓRICA
    # --------------------------------------------------------

    for variable in FEATURES_CATEGORICAS:

        df[variable] = df[
            variable
        ].astype(
            "string"
        )

    return df


# ============================================================
# VALIDACIÓN DEL SPLIT
# ============================================================

def validar_split(
    train,
    validation,
):
    """
    Verifica que TRAIN y VALIDATION coincidan con el
    protocolo congelado v10.
    """

    if len(train) != EXPECTED_TRAIN_ROWS:

        raise ValueError(
            "Número de filas TRAIN diferente al esperado. "
            f"Esperado={EXPECTED_TRAIN_ROWS:,}, "
            f"observado={len(train):,}."
        )

    positivos_train = int(
        train[TARGET].sum()
    )

    if positivos_train != EXPECTED_TRAIN_POSITIVES:

        raise ValueError(
            "Número de positivos TRAIN diferente al esperado. "
            f"Esperado={EXPECTED_TRAIN_POSITIVES}, "
            f"observado={positivos_train}."
        )

    if len(validation) != EXPECTED_VALIDATION_ROWS:

        raise ValueError(
            "Número de filas VALIDATION diferente al esperado. "
            f"Esperado={EXPECTED_VALIDATION_ROWS:,}, "
            f"observado={len(validation):,}."
        )

    positivos_validation = int(
        validation[TARGET].sum()
    )

    if positivos_validation != EXPECTED_VALIDATION_POSITIVES:

        raise ValueError(
            "Número de positivos VALIDATION diferente al esperado. "
            f"Esperado={EXPECTED_VALIDATION_POSITIVES}, "
            f"observado={positivos_validation}."
        )

    anios_train = sorted(
        train["ANIO"]
        .unique()
        .tolist()
    )

    if anios_train != EXPECTED_TRAIN_YEARS:

        raise ValueError(
            "Años de TRAIN diferentes al protocolo v10. "
            f"Observado={anios_train}"
        )

    anios_validation = sorted(
        validation["ANIO"]
        .unique()
        .tolist()
    )

    if anios_validation != EXPECTED_VALIDATION_YEARS:

        raise ValueError(
            "Año de VALIDATION diferente al protocolo v10. "
            f"Observado={anios_validation}"
        )


# ============================================================
# CATEGORÍAS APRENDIDAS SOLO DESDE TRAIN
# ============================================================

def preparar_categorias(
    train,
    validation,
):
    """
    Aprende las categorías exclusivamente desde TRAIN.

    Cualquier categoría presente en VALIDATION pero ausente
    en TRAIN se convierte en missing.
    """

    train = train.copy()
    validation = validation.copy()

    categorias_por_variable = {}
    desconocidos_validation = {}

    for variable in FEATURES_CATEGORICAS:

        categorias_train = (
            train[
                variable
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        categorias_train = sorted(
            categorias_train
        )

        if len(categorias_train) > 255:

            raise ValueError(
                f"{variable} contiene {len(categorias_train)} "
                "categorías en TRAIN; excede max_bins=255."
            )

        categorias_por_variable[
            variable
        ] = categorias_train

        valores_validation_originales = (
            validation[
                variable
            ]
            .copy()
        )

        desconocidos = (
            valores_validation_originales.notna()
            &
            ~valores_validation_originales.astype(
                str
            ).isin(
                categorias_train
            )
        )

        desconocidos_validation[
            variable
        ] = int(
            desconocidos.sum()
        )

        dtype_categorico = pd.CategoricalDtype(
            categories=categorias_train
        )

        train[
            variable
        ] = train[
            variable
        ].astype(
            dtype_categorico
        )

        validation[
            variable
        ] = validation[
            variable
        ].astype(
            dtype_categorico
        )

    return (
        train,
        validation,
        categorias_por_variable,
        desconocidos_validation,
    )


# ============================================================
# MÉTRICAS
# ============================================================

def metricas_clasificacion(
    y_true,
    scores,
):
    """
    Calcula métricas generales utilizando threshold 0.5.

    PR-AUC y ranking son las métricas principales.
    """

    predicciones = (
        scores >= THRESHOLD
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
            THRESHOLD,

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


def metricas_ranking(
    y_true,
    scores,
    split,
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

    positivos = int(
        tabla[
            "TARGET"
        ].sum()
    )

    prevalencia = (
        positivos / total
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
        )

        recall_k = (
            positivos_top
            / positivos
            if positivos > 0
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
                "SPLIT":
                    split,

                "K":
                    int(
                        k
                    ),

                "POSITIVOS_TOP_K":
                    positivos_top,

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
# TOP 500 VALIDATION
# ============================================================

def construir_top500(
    validation,
    scores,
):
    """
    Genera ranking local para revisión.

    Este archivo contiene identificadores empresariales y
    permanece excluido de Git mediante .gitignore.
    """

    columnas = [
        "ANIO",
        "EXPEDIENTE_KEY",
        "RUC",
        "NOMBRE",
        TARGET,
        "tipo_compania",
        "provincia",
    ]

    top = validation[
        columnas
    ].copy()

    top[
        "SCORE_V10_HGB"
    ] = scores

    top = top.sort_values(
        "SCORE_V10_HGB",
        ascending=False,
        kind="mergesort",
    ).reset_index(
        drop=True
    )

    top[
        "RANK"
    ] = np.arange(
        1,
        len(top) + 1,
    )

    return top.head(
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
        "HISTGRADIENTBOOSTING v10"
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
        "tipo_compania: categórica nativa"
    )

    print(
        "Configuración del algoritmo: heredada de v8, sin tuning v10"
    )

    # --------------------------------------------------------
    # CARGAR
    # --------------------------------------------------------

    df = cargar_desarrollo()

    train = df[
        df[
            "SPLIT"
        ]
        .astype("string")
        .str.strip()
        .str.upper()
        .eq(
            "TRAIN"
        )
    ].copy()

    validation = df[
        df[
            "SPLIT"
        ]
        .astype("string")
        .str.strip()
        .str.upper()
        .eq(
            "VALIDATION"
        )
    ].copy()

    validar_split(
        train,
        validation,
    )

    print(
        "\nSplit validado:"
    )

    print(
        f"TRAIN: {len(train):,} filas | "
        f"{int(train[TARGET].sum()):,} positivos"
    )

    print(
        f"VALIDATION: {len(validation):,} filas | "
        f"{int(validation[TARGET].sum()):,} positivos"
    )

    # --------------------------------------------------------
    # CATEGORÍAS
    # --------------------------------------------------------

    (
        train,
        validation,
        categorias_por_variable,
        desconocidos_validation,
    ) = preparar_categorias(
        train,
        validation,
    )

    print(
        "\nCategorías aprendidas exclusivamente desde TRAIN:"
    )

    for variable in FEATURES_CATEGORICAS:

        print(
            f"{variable}: "
            f"{len(categorias_por_variable[variable])} categorías"
        )

        print(
            f"{variable} desconocidas en VALIDATION: "
            f"{desconocidos_validation[variable]}"
        )

    # --------------------------------------------------------
    # X / y
    # --------------------------------------------------------

    X_train = train[
        FEATURES
    ].copy()

    y_train = train[
        TARGET
    ].astype(
        int
    )

    X_validation = validation[
        FEATURES
    ].copy()

    y_validation = validation[
        TARGET
    ].astype(
        int
    )

    # --------------------------------------------------------
    # MODELO
    # --------------------------------------------------------

    modelo = HistGradientBoostingClassifier(
        **MODEL_PARAMS
    )

    print(
        "\nEntrenando HistGradientBoosting v10..."
    )

    modelo.fit(
        X_train,
        y_train,
    )

    # --------------------------------------------------------
    # SCORES
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

    metricas_train = metricas_clasificacion(
        y_train,
        scores_train,
    )

    metricas_validation = metricas_clasificacion(
        y_validation,
        scores_validation,
    )

    metricas_df = pd.DataFrame(
        [
            {
                "SPLIT":
                    "TRAIN",

                "OBSERVACIONES":
                    len(
                        train
                    ),

                "POSITIVOS":
                    int(
                        y_train.sum()
                    ),

                "PREVALENCIA":
                    float(
                        y_train.mean()
                    ),

                **metricas_train,
            },

            {
                "SPLIT":
                    "VALIDATION",

                "OBSERVACIONES":
                    len(
                        validation
                    ),

                "POSITIVOS":
                    int(
                        y_validation.sum()
                    ),

                "PREVALENCIA":
                    float(
                        y_validation.mean()
                    ),

                **metricas_validation,
            },
        ]
    )

    # --------------------------------------------------------
    # RANKING
    # --------------------------------------------------------

    ranking_resultados = []

    ranking_resultados.extend(
        metricas_ranking(
            y_train,
            scores_train,
            "TRAIN",
        )
    )

    ranking_resultados.extend(
        metricas_ranking(
            y_validation,
            scores_validation,
            "VALIDATION",
        )
    )

    ranking_df = pd.DataFrame(
        ranking_resultados
    )

    # --------------------------------------------------------
    # TOP 500
    # --------------------------------------------------------

    top500 = construir_top500(
        validation,
        scores_validation,
    )

    # --------------------------------------------------------
    # SALIDAS
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

    top500.to_csv(
        TOP500_PATH,
        index=False,
    )

    joblib.dump(
        {
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

            "categorias_train":
                categorias_por_variable,
        },
        MODEL_PATH,
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    metadata = {
        "experimento":
            "HistGradientBoosting v10",

        "modelo":
            "HistGradientBoostingClassifier",

        "nombre_modelo":
            MODEL_NAME,

        "fecha_ejecucion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "objetivo":
            (
                "Evaluar un modelo no lineal sobre el dataset "
                "y protocolo v10 utilizando la configuración "
                "regularizada previamente utilizada en v8."
            ),

        "dataset":
            ruta_relativa(
                INPUT_PATH
            ),

        "target":
            TARGET,

        "horizonte_target":
            "24 meses",

        "split": {
            "train":
                "2012-2018",

            "embargo_1":
                2019,

            "validation":
                2020,

            "embargo_2":
                2021,

            "test":
                "2022-2023",
        },

        "test_utilizado":
            False,

        "test_estado":
            "RESERVADO - SIN EVALUACION",

        "baseline_comparacion":
            "v10_lr_no_provincia",

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

        "provincia_utilizada_como_predictor":
            False,

        "tipo_compania_manejo":
            (
                "Categorica nativa mediante pandas.Categorical "
                "y categorical_features='from_dtype'."
            ),

        "categorias_aprendidas_solo_train":
            True,

        "categorias_train":
            categorias_por_variable,

        "categorias_desconocidas_validation":
            desconocidos_validation,

        "manejo_missing_numerico":
            (
                "Nativo de HistGradientBoostingClassifier; "
                "no se aplica imputacion previa."
            ),

        "escalamiento":
            False,

        "configuracion_modelo":
            MODEL_PARAMS,

        "origen_configuracion":
            (
                "Configuracion regularizada heredada del "
                "experimento v8. No se realiza tuning con "
                "VALIDATION 2020 en este experimento inicial v10."
            ),

        "metricas_principales":
            [
                "PR-AUC",
                "Precision@50",
                "Precision@100",
                "Precision@200",
                "Recall@50",
                "Recall@100",
                "Recall@200",
                "Lift@50",
                "Lift@100",
                "Lift@200",
            ],

        "metrica_complementaria":
            "ROC-AUC",

        "threshold_reportado":
            THRESHOLD,

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

            "top500_local":
                ruta_relativa(
                    TOP500_PATH
                ),

            "modelo_local":
                ruta_relativa(
                    MODEL_PATH
                ),

            "metadata":
                ruta_relativa(
                    METADATA_PATH
                ),
        },

        "notas": [
            (
                "ANIO, EXPEDIENTE_KEY, RUC, NOMBRE y SPLIT "
                "no se utilizan como predictores."
            ),
            (
                "provincia no se utiliza como predictor para "
                "mantener comparabilidad con el baseline "
                "v10_lr_no_provincia."
            ),
            (
                "VALIDATION 2020 se utiliza para comparación "
                "durante desarrollo."
            ),
            (
                "TEST 2022-2023 permanece completamente cerrado."
            ),
            (
                "El archivo validation_top500 contiene "
                "identificadores empresariales y no se versiona "
                "en Git."
            ),
        ],
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
    # MOSTRAR RESULTADOS
    # --------------------------------------------------------

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

    print(
        f"\nTRAIN PR-AUC: "
        f"{metricas_train['PR_AUC']:.9f}"
    )

    print(
        f"TRAIN ROC-AUC: "
        f"{metricas_train['ROC_AUC']:.9f}"
    )

    print(
        f"\nVALIDATION PR-AUC: "
        f"{metricas_validation['PR_AUC']:.9f}"
    )

    print(
        f"VALIDATION ROC-AUC: "
        f"{metricas_validation['ROC_AUC']:.9f}"
    )

    print(
        "\nRanking VALIDATION:"
    )

    ranking_validation = ranking_df[
        ranking_df[
            "SPLIT"
        ]
        == "VALIDATION"
    ]

    for _, fila in ranking_validation.iterrows():

        print(
            f"Top {int(fila['K']):>3}: "
            f"{int(fila['POSITIVOS_TOP_K'])} positivos | "
            f"Precision={fila['PRECISION_AT_K']:.6f} | "
            f"Recall={fila['RECALL_AT_K']:.6f} | "
            f"Lift={fila['LIFT_AT_K']:.6f}"
        )

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
        TOP500_PATH
    )

    print(
        METADATA_PATH
    )

    print(
        f"\nModelo local:"
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
        "\nHistGradientBoosting v10 finalizado."
    )


if __name__ == "__main__":
    main()