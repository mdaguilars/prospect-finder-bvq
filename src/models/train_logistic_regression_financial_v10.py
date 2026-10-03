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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "v10_features_financial_2012_2023.csv.gz"
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


METRICS_PATH = (
    OUTPUT_DIR
    / "v10_lr_financial_metrics.csv"
)

RANKING_PATH = (
    OUTPUT_DIR
    / "v10_lr_financial_ranking_metrics.csv"
)

CAPPING_PATH = (
    OUTPUT_DIR
    / "v10_lr_financial_capping.csv"
)

TOP500_PATH = (
    OUTPUT_DIR
    / "v10_lr_financial_validation_top500.csv"
)

METADATA_PATH = (
    OUTPUT_DIR
    / "v10_lr_financial_metadata.json"
)

MODEL_PATH = (
    MODEL_DIR
    / "v10_lr_financial.joblib"
)


TARGET = "TARGET_24M"

RANDOM_STATE = 42

CHUNK_SIZE = 150_000

K_VALUES = [
    50,
    100,
    200,
]

CAPPING_LOWER_QUANTILE = 0.01
CAPPING_UPPER_QUANTILE = 0.99


# ============================================================
# FEATURES CORE
# ============================================================

FEATURES_NUMERICAS_CORE = [
    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",
    "activos_final_t1",
    "patrimonio_final_t1",
    "bi_ingresos_ventas_t1",
    "bi_n_empleados_t1",
]


FEATURES_BOOLEANAS_CORE = [
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


# ============================================================
# FEATURES FINANCIERAS
# ============================================================

FEATURES_FINANCIERAS_NUMERICAS = [
    "fin_ratio_patrimonio_activos",
    "fin_roa",
    "fin_margen_neto",
    "fin_rotacion_activos",
    "fin_roe",
    "fin_crecimiento_activos",
    "fin_crecimiento_patrimonio",
    "fin_crecimiento_ventas",
    "fin_crecimiento_empleados",
]


FEATURES_FINANCIERAS_BOOLEANAS = [
    "flag_patrimonio_no_positivo",
]


# ============================================================
# CONJUNTO TOTAL
# ============================================================

FEATURES_NUMERICAS = (
    FEATURES_NUMERICAS_CORE
    + FEATURES_FINANCIERAS_NUMERICAS
)


FEATURES_BOOLEANAS = (
    FEATURES_BOOLEANAS_CORE
    + FEATURES_FINANCIERAS_BOOLEANAS
)


FEATURES = (
    FEATURES_NUMERICAS
    + FEATURES_BOOLEANAS
    + FEATURES_CATEGORICAS
)


# ============================================================
# COLUMNAS DE CONTROL
# ============================================================

COLUMNAS_CONTROL = [
    "ANIO",
    "EXPEDIENTE_KEY",
    "RUC",
    "NOMBRE",
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
# UNIVERSO CONGELADO
# ============================================================

EXPECTED_TRAIN_ROWS = 470_722
EXPECTED_TRAIN_POSITIVES = 407

EXPECTED_VALIDATION_ROWS = 98_471
EXPECTED_VALIDATION_POSITIVES = 34


# ============================================================
# PARÁMETROS DEL MODELO
# ============================================================

#
# Se conserva la configuración del baseline
# v10_lr_no_provincia.
#

LOGISTIC_PARAMS = {
    "penalty":
        "l2",

    "C":
        1.0,

    "solver":
        "lbfgs",

    "max_iter":
        2000,

    "class_weight":
        "balanced",

    "random_state":
        RANDOM_STATE,
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def ruta_relativa(path):

    return str(
        path.relative_to(
            PROJECT_ROOT
        )
    ).replace(
        "\\",
        "/",
    )


def normalizar_booleana(
    serie,
):

    texto = (
        serie
        .astype(
            "string"
        )
        .str.strip()
        .str.lower()
    )

    mapa = {
        "true":
            1.0,

        "false":
            0.0,

        "1":
            1.0,

        "0":
            0.0,

        "1.0":
            1.0,

        "0.0":
            0.0,

        "si":
            1.0,

        "sí":
            1.0,

        "no":
            0.0,

        "yes":
            1.0,

        "verdadero":
            1.0,

        "falso":
            0.0,
    }

    por_texto = texto.map(
        mapa
    )

    por_numero = pd.to_numeric(
        serie,
        errors="coerce",
    )

    por_numero = por_numero.where(
        por_numero.isin(
            [
                0,
                1,
            ]
        )
    )

    resultado = por_texto.fillna(
        por_numero
    )

    return resultado.astype(
        "float64"
    )


# ============================================================
# PREPARACIÓN DE TIPOS
# ============================================================

def preparar_tipos(
    dataframe,
):

    df = dataframe.copy()

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
            "Existen valores ANIO inválidos."
        )

    df[
        "ANIO"
    ] = df[
        "ANIO"
    ].astype(
        "int64"
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
            "Existen TARGET_24M inválidos."
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
            "TARGET_24M contiene valores "
            "distintos de 0 y 1."
        )

    df[
        TARGET
    ] = df[
        TARGET
    ].astype(
        "int64"
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
    #
    # Conversión explícita de pd.NA a np.nan para que
    # SimpleImputer opere de forma consistente.
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

    # --------------------------------------------------------
    # IDENTIFICADORES
    # --------------------------------------------------------

    df[
        "RUC"
    ] = df[
        "RUC"
    ].astype(
        "string"
    )

    df[
        "NOMBRE"
    ] = df[
        "NOMBRE"
    ].astype(
        "string"
    )

    return df


# ============================================================
# CARGA DEL DATASET
# ============================================================

def cargar_dataset():

    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"No existe el dataset:\n{INPUT_PATH}"
        )

    encabezado = pd.read_csv(
        INPUT_PATH,
        nrows=0,
    )

    disponibles = set(
        encabezado.columns
    )

    faltantes = [
        columna
        for columna in COLUMNAS_LECTURA
        if columna not in disponibles
    ]

    if faltantes:

        raise ValueError(
            "Faltan columnas requeridas:\n"
            + "\n".join(
                faltantes
            )
        )

    print(
        "\nCargando dataset financiero v10..."
    )

    print(
        INPUT_PATH
    )

    partes = []

    for chunk in pd.read_csv(
        INPUT_PATH,
        usecols=COLUMNAS_LECTURA,
        chunksize=CHUNK_SIZE,
        low_memory=False,
        dtype={
            "RUC":
                "string",

            "NOMBRE":
                "string",

            "SPLIT":
                "string",

            "tipo_compania":
                "string",
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

        #
        # TEST NO SE CARGA.
        #
        # EMBARGO tampoco es necesario para este
        # entrenamiento TRAIN -> VALIDATION.
        #

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
            "No se encontraron filas TRAIN/VALIDATION."
        )

    dataframe = pd.concat(
        partes,
        ignore_index=True,
    )

    return preparar_tipos(
        dataframe
    )


# ============================================================
# VALIDAR UNIVERSO
# ============================================================

def validar_universo(
    train,
    validation,
):

    print(
        "\nValidando universo..."
    )

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

    print(
        f"TRAIN:      "
        f"{train_rows:,} filas | "
        f"{train_pos} positivos"
    )

    print(
        f"VALIDATION: "
        f"{validation_rows:,} filas | "
        f"{validation_pos} positivos"
    )

    if train_rows != EXPECTED_TRAIN_ROWS:

        raise ValueError(
            "Número de filas TRAIN incorrecto."
        )

    if train_pos != EXPECTED_TRAIN_POSITIVES:

        raise ValueError(
            "Número de positivos TRAIN incorrecto."
        )

    if validation_rows != EXPECTED_VALIDATION_ROWS:

        raise ValueError(
            "Número de filas VALIDATION incorrecto."
        )

    if validation_pos != EXPECTED_VALIDATION_POSITIVES:

        raise ValueError(
            "Número de positivos VALIDATION incorrecto."
        )


# ============================================================
# APRENDER CAPPING DESDE TRAIN
# ============================================================

def aprender_limites_capping(
    train,
):

    print(
        "\nAprendiendo límites de capping "
        "exclusivamente desde TRAIN..."
    )

    limites = {}

    filas = []

    for variable in FEATURES_FINANCIERAS_NUMERICAS:

        serie = pd.to_numeric(
            train[
                variable
            ],
            errors="coerce",
        ).replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )

        valores_validos = serie.dropna()

        if valores_validos.empty:

            raise ValueError(
                f"{variable} no contiene valores "
                "válidos en TRAIN."
            )

        limite_inferior = float(
            valores_validos.quantile(
                CAPPING_LOWER_QUANTILE
            )
        )

        limite_superior = float(
            valores_validos.quantile(
                CAPPING_UPPER_QUANTILE
            )
        )

        if not np.isfinite(
            limite_inferior
        ):

            raise ValueError(
                f"Límite inferior inválido para {variable}."
            )

        if not np.isfinite(
            limite_superior
        ):

            raise ValueError(
                f"Límite superior inválido para {variable}."
            )

        if limite_inferior > limite_superior:

            raise ValueError(
                f"Límites invertidos para {variable}."
            )

        limites[
            variable
        ] = {
            "lower":
                limite_inferior,

            "upper":
                limite_superior,
        }

        inferiores = int(
            (
                serie
                < limite_inferior
            ).sum()
        )

        superiores = int(
            (
                serie
                > limite_superior
            ).sum()
        )

        filas.append(
            {
                "VARIABLE":
                    variable,

                "QUANTILE_LOWER":
                    CAPPING_LOWER_QUANTILE,

                "QUANTILE_UPPER":
                    CAPPING_UPPER_QUANTILE,

                "LOWER_BOUND":
                    limite_inferior,

                "UPPER_BOUND":
                    limite_superior,

                "TRAIN_NO_NULOS":
                    int(
                        serie.notna().sum()
                    ),

                "TRAIN_DEBAJO_LIMITE":
                    inferiores,

                "TRAIN_SOBRE_LIMITE":
                    superiores,
            }
        )

        print(
            f"{variable:<32} "
            f"[{limite_inferior:.6f}, "
            f"{limite_superior:.6f}]"
        )

    return (
        limites,
        pd.DataFrame(
            filas
        ),
    )


# ============================================================
# APLICAR CAPPING
# ============================================================

def aplicar_capping(
    dataframe,
    limites,
):

    df = dataframe.copy()

    for variable in FEATURES_FINANCIERAS_NUMERICAS:

        lower = limites[
            variable
        ][
            "lower"
        ]

        upper = limites[
            variable
        ][
            "upper"
        ]

        serie = pd.to_numeric(
            df[
                variable
            ],
            errors="coerce",
        ).replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )

        #
        # Los NaN permanecen NaN.
        #
        # Solo los valores finitos fuera del intervalo
        # son recortados.
        #

        df[
            variable
        ] = serie.clip(
            lower=lower,
            upper=upper,
        )

    return df


# ============================================================
# PREPROCESAMIENTO
# ============================================================

def construir_preprocesador():

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
                    strategy="most_frequent"
                ),
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore"
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
    )

    return preprocesador


# ============================================================
# MODELO
# ============================================================

def construir_modelo():

    preprocesador = construir_preprocesador()

    clasificador = LogisticRegression(
        **LOGISTIC_PARAMS
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocesador,
            ),
            (
                "classifier",
                clasificador,
            ),
        ]
    )

    return pipeline


# ============================================================
# MÉTRICAS
# ============================================================

def calcular_metricas(
    y_true,
    scores,
):

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
    }


def calcular_ranking(
    y_true,
    scores,
):

    ranking = pd.DataFrame(
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

    ranking = ranking.sort_values(
        "SCORE",
        ascending=False,
        kind="mergesort",
    ).reset_index(
        drop=True
    )

    positivos_totales = int(
        ranking[
            "TARGET"
        ].sum()
    )

    prevalencia = (
        positivos_totales
        / len(
            ranking
        )
    )

    resultados = []

    for k in K_VALUES:

        top = ranking.head(
            k
        )

        positivos_top = int(
            top[
                "TARGET"
            ].sum()
        )

        precision_k = (
            positivos_top
            / k
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
                    k,

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

    columnas = [
        "ANIO",
        "EXPEDIENTE_KEY",
        "RUC",
        "NOMBRE",
        TARGET,
    ]

    top = validation[
        columnas
    ].copy()

    top[
        "SCORE"
    ] = np.asarray(
        scores
    )

    top = top.sort_values(
        "SCORE",
        ascending=False,
        kind="mergesort",
    ).head(
        500
    ).reset_index(
        drop=True
    )

    top[
        "RANK"
    ] = np.arange(
        1,
        len(
            top
        )
        + 1,
    )

    columnas_salida = [
        "RANK",
        "ANIO",
        "EXPEDIENTE_KEY",
        "RUC",
        "NOMBRE",
        TARGET,
        "SCORE",
    ]

    return top[
        columnas_salida
    ]


# ============================================================
# ENTRENAMIENTO
# ============================================================

def entrenar(
    train,
    validation,
):

    # --------------------------------------------------------
    # CAPPING TRAIN-ONLY
    # --------------------------------------------------------

    (
        limites,
        capping_df,
    ) = aprender_limites_capping(
        train
    )

    train_cap = aplicar_capping(
        train,
        limites,
    )

    validation_cap = aplicar_capping(
        validation,
        limites,
    )

    # --------------------------------------------------------
    # MATRICES
    # --------------------------------------------------------

    X_train = train_cap[
        FEATURES
    ].copy()

    y_train = train_cap[
        TARGET
    ].astype(
        int
    )

    X_validation = validation_cap[
        FEATURES
    ].copy()

    y_validation = validation_cap[
        TARGET
    ].astype(
        int
    )

    # --------------------------------------------------------
    # MODELO
    # --------------------------------------------------------

    pipeline = construir_modelo()

    print(
        "\nEntrenando Regresión Logística financiera v10..."
    )

    convergencia_warning = False
    mensajes_warning = []

    with warnings.catch_warnings(
        record=True
    ) as warnings_capturados:

        warnings.simplefilter(
            "always",
            ConvergenceWarning,
        )

        pipeline.fit(
            X_train,
            y_train,
        )

        for warning in warnings_capturados:

            if issubclass(
                warning.category,
                ConvergenceWarning,
            ):

                convergencia_warning = True

                mensajes_warning.append(
                    str(
                        warning.message
                    )
                )

    # --------------------------------------------------------
    # PREDICCIONES
    # --------------------------------------------------------

    score_train = pipeline.predict_proba(
        X_train
    )[:, 1]

    score_validation = pipeline.predict_proba(
        X_validation
    )[:, 1]

    # --------------------------------------------------------
    # MÉTRICAS
    # --------------------------------------------------------

    metricas_train = calcular_metricas(
        y_train,
        score_train,
    )

    metricas_validation = calcular_metricas(
        y_validation,
        score_validation,
    )

    ranking_validation = calcular_ranking(
        y_validation,
        score_validation,
    )

    # --------------------------------------------------------
    # FEATURES TRANSFORMADAS
    # --------------------------------------------------------

    preprocesador = pipeline.named_steps[
        "preprocessor"
    ]

    try:

        nombres_transformados = (
            preprocesador
            .get_feature_names_out()
            .tolist()
        )

        n_features_transformadas = len(
            nombres_transformados
        )

    except Exception:

        nombres_transformados = []

        muestra = preprocesador.transform(
            X_train.head(
                2
            )
        )

        n_features_transformadas = int(
            muestra.shape[
                1
            ]
        )

    return {
        "pipeline":
            pipeline,

        "limites":
            limites,

        "capping_df":
            capping_df,

        "metricas_train":
            metricas_train,

        "metricas_validation":
            metricas_validation,

        "ranking_validation":
            ranking_validation,

        "score_validation":
            score_validation,

        "convergence_warning":
            convergencia_warning,

        "warning_messages":
            mensajes_warning,

        "n_features_transformadas":
            n_features_transformadas,

        "nombres_transformados":
            nombres_transformados,
    }


# ============================================================
# CONSTRUIR TABLA DE MÉTRICAS
# ============================================================

def construir_metricas_dataframe(
    resultado,
):

    train_metrics = resultado[
        "metricas_train"
    ]

    validation_metrics = resultado[
        "metricas_validation"
    ]

    filas = [
        {
            "MODELO":
                "v10_lr_financial",

            "SPLIT":
                "TRAIN",

            "PR_AUC":
                train_metrics[
                    "PR_AUC"
                ],

            "ROC_AUC":
                train_metrics[
                    "ROC_AUC"
                ],
        },

        {
            "MODELO":
                "v10_lr_financial",

            "SPLIT":
                "VALIDATION",

            "PR_AUC":
                validation_metrics[
                    "PR_AUC"
                ],

            "ROC_AUC":
                validation_metrics[
                    "ROC_AUC"
                ],
        },
    ]

    return pd.DataFrame(
        filas
    )


# ============================================================
# CONSTRUIR TABLA DE RANKING
# ============================================================

def construir_ranking_dataframe(
    resultado,
):

    filas = []

    for ranking in resultado[
        "ranking_validation"
    ]:

        filas.append(
            {
                "MODELO":
                    "v10_lr_financial",

                "SPLIT":
                    "VALIDATION",

                **ranking,
            }
        )

    return pd.DataFrame(
        filas
    )


# ============================================================
# METADATA
# ============================================================

def construir_metadata(
    train,
    validation,
    resultado,
):

    return {
        "experimento":
            "Regresion Logistica financiera v10",

        "fecha_ejecucion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "dataset":
            ruta_relativa(
                INPUT_PATH
            ),

        "modelo":
            "LogisticRegression",

        "baseline_referencia":
            "v10_lr_no_provincia",

        "objetivo":
            (
                "Evaluar el baseline de Regresion Logistica "
                "incorporando las nuevas features financieras "
                "sin modificar la configuracion del modelo."
            ),

        "target":
            TARGET,

        "horizonte_target":
            "24 meses",

        "modelo_parametros":
            LOGISTIC_PARAMS,

        "features_fisicas":
            FEATURES,

        "numero_features_fisicas":
            len(
                FEATURES
            ),

        "features_numericas_core":
            FEATURES_NUMERICAS_CORE,

        "features_financieras_numericas":
            FEATURES_FINANCIERAS_NUMERICAS,

        "features_booleanas_core":
            FEATURES_BOOLEANAS_CORE,

        "features_financieras_booleanas":
            FEATURES_FINANCIERAS_BOOLEANAS,

        "features_categoricas":
            FEATURES_CATEGORICAS,

        "provincia_utilizada":
            False,

        "preprocesamiento": {
            "numericas":
                (
                    "SimpleImputer(strategy='median') "
                    "+ StandardScaler(), ajustados solo con TRAIN."
                ),

            "booleanas":
                (
                    "SimpleImputer(strategy='most_frequent'), "
                    "ajustado solo con TRAIN."
                ),

            "categoricas":
                (
                    "SimpleImputer(strategy='most_frequent') "
                    "+ OneHotEncoder(handle_unknown='ignore'), "
                    "ajustados solo con TRAIN."
                ),

            "capping_financieras":
                {
                    "aplicado":
                        True,

                    "variables":
                        FEATURES_FINANCIERAS_NUMERICAS,

                    "percentil_inferior":
                        CAPPING_LOWER_QUANTILE,

                    "percentil_superior":
                        CAPPING_UPPER_QUANTILE,

                    "aprendido_desde":
                        "TRAIN exclusivamente",

                    "validation":
                        (
                            "Los limites aprendidos en TRAIN "
                            "se aplican sin recalcular."
                        ),
                },
        },

        "class_imbalance":
            {
                "metodo":
                    "class_weight='balanced'",

                "sample_weight_adicional":
                    False,
            },

        "train": {
            "filas":
                int(
                    len(
                        train
                    )
                ),

            "positivos":
                int(
                    train[
                        TARGET
                    ].sum()
                ),
        },

        "validation": {
            "anio":
                2020,

            "filas":
                int(
                    len(
                        validation
                    )
                ),

            "positivos":
                int(
                    validation[
                        TARGET
                    ].sum()
                ),

            "rol":
                "evaluacion de desarrollo",
        },

        "resultados": {
            "train_pr_auc":
                resultado[
                    "metricas_train"
                ][
                    "PR_AUC"
                ],

            "train_roc_auc":
                resultado[
                    "metricas_train"
                ][
                    "ROC_AUC"
                ],

            "validation_pr_auc":
                resultado[
                    "metricas_validation"
                ][
                    "PR_AUC"
                ],

            "validation_roc_auc":
                resultado[
                    "metricas_validation"
                ][
                    "ROC_AUC"
                ],

            "gap_pr_auc":
                (
                    resultado[
                        "metricas_train"
                    ][
                        "PR_AUC"
                    ]
                    -
                    resultado[
                        "metricas_validation"
                    ][
                        "PR_AUC"
                    ]
                ),

            "ranking_validation":
                resultado[
                    "ranking_validation"
                ],
        },

        "convergencia": {
            "warning":
                resultado[
                    "convergence_warning"
                ],

            "mensajes":
                resultado[
                    "warning_messages"
                ],
        },

        "numero_features_transformadas":
            resultado[
                "n_features_transformadas"
            ],

        "test": {
            "periodo":
                "2022-2023",

            "cargado":
                False,

            "transformado":
                False,

            "evaluado":
                False,

            "estado":
                "RESERVADO",
        },

        "backtest":
            {
                "realizado_en_este_script":
                    False,

                "nota":
                    (
                        "El backtest temporal se ejecutara "
                        "en un script separado. Los limites "
                        "de capping deberan aprenderse nuevamente "
                        "dentro del TRAIN de cada fold."
                    ),
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

            "capping":
                ruta_relativa(
                    CAPPING_PATH
                ),

            "top500_validation":
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
    }


# ============================================================
# GUARDAR MODELO
# ============================================================

def guardar_modelo(
    resultado,
):

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    bundle = {
        "pipeline":
            resultado[
                "pipeline"
            ],

        "capping_limits":
            resultado[
                "limites"
            ],

        "financial_capping_features":
            FEATURES_FINANCIERAS_NUMERICAS,

        "physical_features":
            FEATURES,

        "target":
            TARGET,

        "model_name":
            "v10_lr_financial",
    }

    joblib.dump(
        bundle,
        MODEL_PATH,
    )


# ============================================================
# MOSTRAR RESULTADOS
# ============================================================

def mostrar_resultados(
    resultado,
):

    metricas_train = resultado[
        "metricas_train"
    ]

    metricas_validation = resultado[
        "metricas_validation"
    ]

    print(
        "\n"
        + "=" * 110
    )

    print(
        "RESULTADOS - LR FINANCIAL v10"
    )

    print(
        "=" * 110
    )

    print(
        f"\nFeatures físicas: "
        f"{len(FEATURES)}"
    )

    print(
        f"Features transformadas: "
        f"{resultado['n_features_transformadas']}"
    )

    print(
        "\nTRAIN:"
    )

    print(
        f"PR-AUC:  "
        f"{metricas_train['PR_AUC']:.9f}"
    )

    print(
        f"ROC-AUC: "
        f"{metricas_train['ROC_AUC']:.9f}"
    )

    print(
        "\nVALIDATION 2020:"
    )

    print(
        f"PR-AUC:  "
        f"{metricas_validation['PR_AUC']:.9f}"
    )

    print(
        f"ROC-AUC: "
        f"{metricas_validation['ROC_AUC']:.9f}"
    )

    print(
        "\nRanking VALIDATION:"
    )

    for ranking in resultado[
        "ranking_validation"
    ]:

        print(
            f"Top {ranking['K']:>3}: "
            f"{ranking['POSITIVOS_TOP_K']} positivos | "
            f"Precision={ranking['PRECISION_AT_K']:.6f} | "
            f"Recall={ranking['RECALL_AT_K']:.6f} | "
            f"Lift={ranking['LIFT_AT_K']:.6f}"
        )

    print(
        "\nConvergenceWarning:"
    )

    print(
        resultado[
            "convergence_warning"
        ]
    )

    print(
        "\nTEST 2022-2023:"
    )

    print(
        "RESERVADO - NO CARGADO - NO EVALUADO"
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
        "REGRESIÓN LOGÍSTICA FINANCIERA v10"
    )

    print(
        "=" * 110
    )

    print(
        "\nBaseline de referencia:"
    )

    print(
        "v10_lr_no_provincia"
    )

    print(
        "\nConfiguración LR:"
    )

    print(
        "L2 | C=1.0 | solver=lbfgs | "
        "max_iter=2000 | class_weight=balanced"
    )

    print(
        "\nFeatures:"
    )

    print(
        f"{len(FEATURES)} variables físicas"
    )

    print(
        "\nCapping:"
    )

    print(
        "P01-P99 solo sobre las 9 variables "
        "financieras numéricas."
    )

    print(
        "Límites aprendidos exclusivamente desde TRAIN."
    )

    print(
        "\nTEST 2022-2023:"
    )

    print(
        "RESERVADO - NO SE CARGARÁ"
    )

    # --------------------------------------------------------
    # CARGAR
    # --------------------------------------------------------

    dataframe = cargar_dataset()

    train = dataframe[
        dataframe[
            "SPLIT"
        ]
        == "TRAIN"
    ].copy()

    validation = dataframe[
        dataframe[
            "SPLIT"
        ]
        == "VALIDATION"
    ].copy()

    # --------------------------------------------------------
    # VALIDAR
    # --------------------------------------------------------

    validar_universo(
        train,
        validation,
    )

    # --------------------------------------------------------
    # ENTRENAR
    # --------------------------------------------------------

    resultado = entrenar(
        train,
        validation,
    )

    # --------------------------------------------------------
    # TABLAS
    # --------------------------------------------------------

    metrics_df = construir_metricas_dataframe(
        resultado
    )

    ranking_df = construir_ranking_dataframe(
        resultado
    )

    top500_df = construir_top500(
        validation,
        resultado[
            "score_validation"
        ],
    )

    metadata = construir_metadata(
        train,
        validation,
        resultado,
    )

    # --------------------------------------------------------
    # CREAR DIRECTORIOS
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # GUARDAR RESULTADOS
    # --------------------------------------------------------

    metrics_df.to_csv(
        METRICS_PATH,
        index=False,
    )

    ranking_df.to_csv(
        RANKING_PATH,
        index=False,
    )

    resultado[
        "capping_df"
    ].to_csv(
        CAPPING_PATH,
        index=False,
    )

    top500_df.to_csv(
        TOP500_PATH,
        index=False,
    )

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

    guardar_modelo(
        resultado
    )

    # --------------------------------------------------------
    # MOSTRAR
    # --------------------------------------------------------

    mostrar_resultados(
        resultado
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
        CAPPING_PATH
    )

    print(
        TOP500_PATH
    )

    print(
        METADATA_PATH
    )

    print(
        MODEL_PATH
    )

    print(
        "\nEntrenamiento finalizado correctamente."
    )


if __name__ == "__main__":
    main()