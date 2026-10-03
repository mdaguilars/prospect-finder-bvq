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

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
)


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]

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


# ============================================================
# ARCHIVOS DE SALIDA
# ============================================================

METRICS_PATH = (
    OUTPUT_DIR
    / "final_test_v10_metrics.csv"
)

RANKING_METRICS_PATH = (
    OUTPUT_DIR
    / "final_test_v10_ranking_metrics.csv"
)

RANKING_PATH = (
    OUTPUT_DIR
    / "final_test_v10_ranking.csv.gz"
)

YEAR_METRICS_PATH = (
    OUTPUT_DIR
    / "final_test_v10_year_metrics.csv"
)

YEAR_RANKING_METRICS_PATH = (
    OUTPUT_DIR
    / "final_test_v10_year_ranking_metrics.csv"
)

TOP500_PATH = (
    OUTPUT_DIR
    / "final_test_v10_top500.csv"
)

METADATA_PATH = (
    OUTPUT_DIR
    / "final_test_v10_metadata.json"
)

MODEL_PATH = (
    MODEL_DIR
    / "v10_hgb_financial_c3_final.joblib"
)


# ============================================================
# IDENTIFICACIÓN DEL EXPERIMENTO
# ============================================================

MODEL_NAME = "v10_hgb_financial_c3"

CONFIG_ID = "C3_CONSERVATIVE"

TARGET = "TARGET_24M"

RANDOM_STATE = 42

CHUNK_SIZE = 150_000

K_VALUES = [
    50,
    100,
    200,
]

TOP_N_EXPORT = 500


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
# CONJUNTO FINAL DE 25 FEATURES
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
# IDENTIFICADORES PARA RANKING
# ============================================================

ID_COLUMNS = [
    "ANIO",
    "EXPEDIENTE_KEY",
    "RUC",
    "NOMBRE",
]


COLUMNAS_LECTURA = list(
    dict.fromkeys(
        ID_COLUMNS
        + [
            "SPLIT",
            TARGET,
        ]
        + FEATURES
    )
)


# ============================================================
# HIPERPARÁMETROS CONGELADOS C3
# ============================================================

MODEL_PARAMS = {
    "loss":
        "log_loss",

    "learning_rate":
        0.03,

    "max_iter":
        250,

    "max_leaf_nodes":
        5,

    "max_depth":
        2,

    "min_samples_leaf":
        200,

    "l2_regularization":
        3.0,

    "early_stopping":
        False,

    "random_state":
        RANDOM_STATE,

    "class_weight":
        "balanced",

    "categorical_features":
        "from_dtype",
}


# ============================================================
# UNIVERSOS CONGELADOS
# ============================================================

EXPECTED = {
    "TRAIN": {
        "filas":
            470_722,

        "positivos":
            407,

        "anios":
            list(
                range(
                    2012,
                    2019,
                )
            ),
    },

    "TEST": {
        "filas":
            260_445,

        "positivos":
            54,

        "anios":
            [
                2022,
                2023,
            ],
    },
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def ruta_relativa(
    path,
):

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
# PREPARACIÓN DE TIPOS BASE
# ============================================================

def preparar_tipos_base(
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
            "Existen valores TARGET_24M inválidos."
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

    return df


# ============================================================
# CARGA EXCLUSIVA TRAIN + TEST
# ============================================================

def cargar_train_test():

    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"No existe el dataset:\n"
            f"{INPUT_PATH}"
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
        "\n"
        + "!" * 120
    )

    print(
        "APERTURA FINAL DE TEST v10"
    )

    print(
        "Se cargarán únicamente TRAIN y TEST."
    )

    print(
        "VALIDATION y los años de embargo "
        "no se utilizarán para entrenar."
    )

    print(
        "!" * 120
    )

    partes = []

    dtype_lectura = {
        "SPLIT":
            "string",

        "tipo_compania":
            "string",

        "EXPEDIENTE_KEY":
            "string",

        "RUC":
            "string",

        "NOMBRE":
            "string",
    }

    for chunk in pd.read_csv(
        INPUT_PATH,
        usecols=COLUMNAS_LECTURA,
        chunksize=CHUNK_SIZE,
        low_memory=False,
        dtype=dtype_lectura,
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
                "TEST",
            ]
        )

        if mascara.any():

            bloque = chunk.loc[
                mascara
            ].copy()

            bloque[
                "SPLIT"
            ] = (
                split_normalizado.loc[
                    mascara
                ]
                .astype(
                    "string"
                )
            )

            partes.append(
                bloque
            )

    if not partes:

        raise ValueError(
            "No se encontraron observaciones "
            "TRAIN o TEST."
        )

    dataframe = pd.concat(
        partes,
        ignore_index=True,
    )

    dataframe = preparar_tipos_base(
        dataframe
    )

    return dataframe


# ============================================================
# VALIDACIÓN DEL UNIVERSO
# ============================================================

def validar_universo(
    dataframe,
):

    print(
        "\nValidando universos congelados..."
    )

    splits_presentes = set(
        dataframe[
            "SPLIT"
        ]
        .unique()
        .tolist()
    )

    if splits_presentes != {
        "TRAIN",
        "TEST",
    }:

        raise ValueError(
            "El script cargó splits distintos "
            "de TRAIN y TEST."
        )

    for split, esperado in EXPECTED.items():

        subset = dataframe[
            dataframe[
                "SPLIT"
            ]
            == split
        ]

        filas = len(
            subset
        )

        positivos = int(
            subset[
                TARGET
            ].sum()
        )

        anios = sorted(
            subset[
                "ANIO"
            ]
            .unique()
            .tolist()
        )

        print(
            f"{split}: "
            f"{filas:,} filas | "
            f"{positivos} positivos | "
            f"años={anios}"
        )

        if filas != esperado[
            "filas"
        ]:

            raise ValueError(
                f"{split}: número de filas incorrecto. "
                f"Esperado={esperado['filas']:,}, "
                f"obtenido={filas:,}."
            )

        if positivos != esperado[
            "positivos"
        ]:

            raise ValueError(
                f"{split}: número de positivos incorrecto. "
                f"Esperado={esperado['positivos']}, "
                f"obtenido={positivos}."
            )

        if anios != esperado[
            "anios"
        ]:

            raise ValueError(
                f"{split}: años inesperados. "
                f"Esperado={esperado['anios']}, "
                f"obtenido={anios}."
            )


# ============================================================
# PREPARACIÓN DE CATEGORÍA TRAIN-ONLY
# ============================================================

def preparar_categoria_train_test(
    train,
    test,
):

    train_out = train.copy()

    test_out = test.copy()

    for variable in FEATURES_CATEGORICAS:

        train_serie = (
            train_out[
                variable
            ]
            .astype(
                "string"
            )
        )

        categorias_train = sorted(
            train_serie
            .dropna()
            .unique()
            .tolist()
        )

        train_out[
            variable
        ] = pd.Categorical(
            train_serie,
            categories=categorias_train,
        )

        test_serie = (
            test_out[
                variable
            ]
            .astype(
                "string"
            )
        )

        categorias_test = set(
            test_serie
            .dropna()
            .unique()
            .tolist()
        )

        categorias_desconocidas = sorted(
            categorias_test
            - set(
                categorias_train
            )
        )

        if categorias_desconocidas:

            print(
                f"\nCategorías desconocidas en TEST "
                f"para {variable}: "
                f"{categorias_desconocidas}"
            )

            print(
                "Serán tratadas como missing, "
                "sin aprender información desde TEST."
            )

        test_out[
            variable
        ] = pd.Categorical(
            test_serie,
            categories=categorias_train,
        )

        print(
            f"\n{variable}: "
            f"{len(categorias_train)} categorías "
            f"aprendidas exclusivamente desde TRAIN."
        )

    return (
        train_out,
        test_out,
    )


# ============================================================
# MODELO CONGELADO
# ============================================================

def construir_modelo():

    return HistGradientBoostingClassifier(
        **MODEL_PARAMS
    )


# ============================================================
# MÉTRICAS GENERALES
# ============================================================

def calcular_metricas(
    y_true,
    scores,
):

    prevalencia = float(
        np.mean(
            y_true
        )
    )

    return {
        "N":
            int(
                len(
                    y_true
                )
            ),

        "POSITIVOS":
            int(
                np.sum(
                    y_true
                )
            ),

        "PREVALENCIA":
            prevalencia,

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


# ============================================================
# MÉTRICAS TOP K
# ============================================================

def calcular_ranking_metrics(
    y_true,
    scores,
):

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

    positivos_totales = int(
        tabla[
            "TARGET"
        ].sum()
    )

    prevalencia = (
        positivos_totales
        / len(
            tabla
        )
    )

    resultados = []

    for k in K_VALUES:

        if k > len(
            tabla
        ):

            continue

        top = tabla.head(
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

    return pd.DataFrame(
        resultados
    )


# ============================================================
# RANKING COMPLETO
# ============================================================

def construir_ranking(
    test_original,
    scores,
):

    columnas_disponibles = [
        columna
        for columna in ID_COLUMNS
        if columna
        in test_original.columns
    ]

    ranking = test_original[
        columnas_disponibles
        + [
            TARGET
        ]
    ].copy()

    ranking[
        "SCORE"
    ] = np.asarray(
        scores
    )

    ranking = ranking.sort_values(
        [
            "SCORE",
            "ANIO",
            "EXPEDIENTE_KEY",
        ],
        ascending=[
            False,
            True,
            True,
        ],
        kind="mergesort",
    ).reset_index(
        drop=True
    )

    ranking.insert(
        0,
        "RANK",
        np.arange(
            1,
            len(
                ranking
            )
            + 1,
        ),
    )

    return ranking


# ============================================================
# MÉTRICAS DESCRIPTIVAS POR AÑO
# ============================================================

def calcular_metricas_por_anio(
    test_original,
    scores,
):

    base = test_original[
        [
            "ANIO",
            TARGET,
        ]
    ].copy()

    base[
        "SCORE"
    ] = np.asarray(
        scores
    )

    filas_metricas = []

    filas_ranking = []

    for anio in sorted(
        base[
            "ANIO"
        ]
        .unique()
        .tolist()
    ):

        bloque = base[
            base[
                "ANIO"
            ]
            == anio
        ].copy()

        y_true = bloque[
            TARGET
        ].to_numpy()

        score = bloque[
            "SCORE"
        ].to_numpy()

        metricas = calcular_metricas(
            y_true,
            score,
        )

        filas_metricas.append(
            {
                "MODELO":
                    MODEL_NAME,

                "ANIO":
                    int(
                        anio
                    ),

                **metricas,
            }
        )

        ranking_anio = calcular_ranking_metrics(
            y_true,
            score,
        )

        for _, fila in ranking_anio.iterrows():

            filas_ranking.append(
                {
                    "MODELO":
                        MODEL_NAME,

                    "ANIO":
                        int(
                            anio
                        ),

                    "N":
                        len(
                            y_true
                        ),

                    "POSITIVOS":
                        int(
                            np.sum(
                                y_true
                            )
                        ),

                    "K":
                        int(
                            fila[
                                "K"
                            ]
                        ),

                    "POSITIVOS_TOP_K":
                        int(
                            fila[
                                "POSITIVOS_TOP_K"
                            ]
                        ),

                    "PRECISION_AT_K":
                        float(
                            fila[
                                "PRECISION_AT_K"
                            ]
                        ),

                    "RECALL_AT_K":
                        float(
                            fila[
                                "RECALL_AT_K"
                            ]
                        ),

                    "LIFT_AT_K":
                        float(
                            fila[
                                "LIFT_AT_K"
                            ]
                        ),
                }
            )

    return (
        pd.DataFrame(
            filas_metricas
        ),
        pd.DataFrame(
            filas_ranking
        ),
    )


# ============================================================
# MOSTRAR RESULTADOS
# ============================================================

def mostrar_resultados(
    metricas_train,
    metricas_test,
    ranking_metrics,
    year_metrics,
    year_ranking,
):

    print(
        "\n"
        + "=" * 120
    )

    print(
        "RESULTADO FINAL TEST v10"
    )

    print(
        "=" * 120
    )

    print(
        "\nMODELO CONGELADO:"
    )

    print(
        MODEL_NAME
    )

    print(
        "\nTRAIN 2012-2018"
    )

    print(
        f"N:          "
        f"{metricas_train['N']:,}"
    )

    print(
        f"Positivos:  "
        f"{metricas_train['POSITIVOS']}"
    )

    print(
        f"PR-AUC:     "
        f"{metricas_train['PR_AUC']:.9f}"
    )

    print(
        f"ROC-AUC:    "
        f"{metricas_train['ROC_AUC']:.9f}"
    )

    print(
        "\n"
        + "-" * 120
    )

    print(
        "TEST 2022-2023 - RESULTADO OFICIAL"
    )

    print(
        "-" * 120
    )

    print(
        f"N:           "
        f"{metricas_test['N']:,}"
    )

    print(
        f"Positivos:   "
        f"{metricas_test['POSITIVOS']}"
    )

    print(
        f"Prevalencia: "
        f"{metricas_test['PREVALENCIA']:.9f}"
    )

    print(
        f"PR-AUC:      "
        f"{metricas_test['PR_AUC']:.9f}"
    )

    print(
        f"ROC-AUC:     "
        f"{metricas_test['ROC_AUC']:.9f}"
    )

    print(
        "\nRanking TEST:"
    )

    for _, fila in ranking_metrics.iterrows():

        print(
            f"Top {int(fila['K']):>3}: "
            f"{int(fila['POSITIVOS_TOP_K'])} positivos | "
            f"Precision="
            f"{fila['PRECISION_AT_K']:.6f} | "
            f"Recall="
            f"{fila['RECALL_AT_K']:.6f} | "
            f"Lift="
            f"{fila['LIFT_AT_K']:.6f}"
        )

    print(
        "\n"
        + "-" * 120
    )

    print(
        "ANÁLISIS DESCRIPTIVO POR AÑO"
    )

    print(
        "-" * 120
    )

    print(
        year_metrics.to_string(
            index=False
        )
    )

    print(
        "\nRanking por año:"
    )

    print(
        year_ranking.to_string(
            index=False
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        + "=" * 120
    )

    print(
        "PROSPECT FINDER BVQ"
    )

    print(
        "EVALUACIÓN FINAL TEST v10"
    )

    print(
        "=" * 120
    )

    print(
        "\nModelo congelado:"
    )

    print(
        MODEL_NAME
    )

    print(
        "\nConfiguración:"
    )

    print(
        CONFIG_ID
    )

    print(
        "\nFeatures físicas:"
    )

    print(
        len(
            FEATURES
        )
    )

    print(
        "\nEntrenamiento autorizado:"
    )

    print(
        "TRAIN 2012-2018"
    )

    print(
        "\nEvaluación autorizada:"
    )

    print(
        "TEST 2022-2023"
    )

    print(
        "\nVALIDATION 2020:"
    )

    print(
        "NO SE UTILIZARÁ PARA ENTRENAR"
    )

    print(
        "\nEmbargos 2019 y 2021:"
    )

    print(
        "NO SE UTILIZARÁN"
    )

    # --------------------------------------------------------
    # CARGAR TRAIN + TEST
    # --------------------------------------------------------

    dataframe = cargar_train_test()

    # --------------------------------------------------------
    # VALIDAR UNIVERSOS
    # --------------------------------------------------------

    validar_universo(
        dataframe
    )

    # --------------------------------------------------------
    # SEPARAR
    # --------------------------------------------------------

    train_original = dataframe[
        dataframe[
            "SPLIT"
        ]
        == "TRAIN"
    ].copy()

    test_original = dataframe[
        dataframe[
            "SPLIT"
        ]
        == "TEST"
    ].copy()

    # --------------------------------------------------------
    # CATEGORÍA APRENDIDA EXCLUSIVAMENTE DESDE TRAIN
    # --------------------------------------------------------

    (
        train,
        test,
    ) = preparar_categoria_train_test(
        train_original,
        test_original,
    )

    # --------------------------------------------------------
    # MATRICES
    # --------------------------------------------------------

    X_train = train[
        FEATURES
    ].copy()

    y_train = train[
        TARGET
    ].astype(
        int
    )

    X_test = test[
        FEATURES
    ].copy()

    y_test = test[
        TARGET
    ].astype(
        int
    )

    # --------------------------------------------------------
    # ENTRENAR ÚNICO MODELO CONGELADO
    # --------------------------------------------------------

    modelo = construir_modelo()

    print(
        "\nEntrenando modelo congelado "
        "exclusivamente con TRAIN 2012-2018..."
    )

    warning_messages = []

    with warnings.catch_warnings(
        record=True
    ) as warnings_capturados:

        warnings.simplefilter(
            "always"
        )

        modelo.fit(
            X_train,
            y_train,
        )

        for warning in warnings_capturados:

            warning_messages.append(
                {
                    "category":
                        warning.category.__name__,

                    "message":
                        str(
                            warning.message
                        ),
                }
            )

    print(
        "Entrenamiento finalizado."
    )

    # --------------------------------------------------------
    # PREDICCIONES
    # --------------------------------------------------------

    score_train = modelo.predict_proba(
        X_train
    )[:, 1]

    #
    # A PARTIR DE ESTA LÍNEA SE PRODUCE
    # LA EVALUACIÓN FINAL DEL TEST.
    #

    print(
        "\nEvaluando TEST 2022-2023..."
    )

    score_test = modelo.predict_proba(
        X_test
    )[:, 1]

    # --------------------------------------------------------
    # MÉTRICAS
    # --------------------------------------------------------

    metricas_train = calcular_metricas(
        y_train.to_numpy(),
        score_train,
    )

    metricas_test = calcular_metricas(
        y_test.to_numpy(),
        score_test,
    )

    metrics_df = pd.DataFrame(
        [
            {
                "MODELO":
                    MODEL_NAME,

                "CONFIG_ID":
                    CONFIG_ID,

                "SPLIT":
                    "TRAIN",

                **metricas_train,
            },

            {
                "MODELO":
                    MODEL_NAME,

                "CONFIG_ID":
                    CONFIG_ID,

                "SPLIT":
                    "TEST",

                **metricas_test,
            },
        ]
    )

    # --------------------------------------------------------
    # RANKING METRICS OFICIAL TEST
    # --------------------------------------------------------

    ranking_metrics = calcular_ranking_metrics(
        y_test.to_numpy(),
        score_test,
    )

    ranking_metrics.insert(
        0,
        "MODELO",
        MODEL_NAME,
    )

    ranking_metrics.insert(
        1,
        "CONFIG_ID",
        CONFIG_ID,
    )

    ranking_metrics.insert(
        2,
        "SPLIT",
        "TEST",
    )

    ranking_metrics.insert(
        3,
        "N",
        len(
            y_test
        ),
    )

    ranking_metrics.insert(
        4,
        "POSITIVOS",
        int(
            y_test.sum()
        ),
    )

    ranking_metrics.insert(
        5,
        "PREVALENCIA",
        float(
            y_test.mean()
        ),
    )

    # --------------------------------------------------------
    # RANKING COMPLETO
    # --------------------------------------------------------

    ranking_df = construir_ranking(
        test_original,
        score_test,
    )

    top500_df = ranking_df.head(
        TOP_N_EXPORT
    ).copy()

    # --------------------------------------------------------
    # MÉTRICAS POR AÑO
    # --------------------------------------------------------

    (
        year_metrics,
        year_ranking,
    ) = calcular_metricas_por_anio(
        test_original,
        score_test,
    )

    # --------------------------------------------------------
    # DIRECTORIOS
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

    ranking_metrics.to_csv(
        RANKING_METRICS_PATH,
        index=False,
    )

    ranking_df.to_csv(
        RANKING_PATH,
        index=False,
        compression="gzip",
    )

    year_metrics.to_csv(
        YEAR_METRICS_PATH,
        index=False,
    )

    year_ranking.to_csv(
        YEAR_RANKING_METRICS_PATH,
        index=False,
    )

    top500_df.to_csv(
        TOP500_PATH,
        index=False,
    )

    # --------------------------------------------------------
    # GUARDAR MODELO FINAL LOCAL
    # --------------------------------------------------------

    model_bundle = {
        "model":
            modelo,

        "model_name":
            MODEL_NAME,

        "config_id":
            CONFIG_ID,

        "features":
            FEATURES,

        "numeric_features":
            FEATURES_NUMERICAS,

        "boolean_features":
            FEATURES_BOOLEANAS,

        "categorical_features":
            FEATURES_CATEGORICAS,

        "target":
            TARGET,

        "train_period":
            "2012-2018",

        "test_period":
            "2022-2023",
    }

    joblib.dump(
        model_bundle,
        MODEL_PATH,
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    metadata = {
        "experimento":
            (
                "Evaluacion final TEST "
                "Prospect Finder BVQ v10"
            ),

        "estado":
            "FINAL_TEST_EVALUATED",

        "fecha_ejecucion_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "dataset":
            ruta_relativa(
                INPUT_PATH
            ),

        "documentos_previos":
            [
                "docs/v10_final_candidate_freeze.md",
                "docs/v10_final_test_protocol.md",
            ],

        "modelo":
            MODEL_NAME,

        "familia":
            "HistGradientBoostingClassifier",

        "config_id":
            CONFIG_ID,

        "modelo_parametros":
            MODEL_PARAMS,

        "random_state":
            RANDOM_STATE,

        "target":
            TARGET,

        "horizonte_target":
            "24 meses",

        "numero_features_fisicas":
            len(
                FEATURES
            ),

        "features":
            FEATURES,

        "features_numericas":
            FEATURES_NUMERICAS,

        "features_booleanas":
            FEATURES_BOOLEANAS,

        "features_categoricas":
            FEATURES_CATEGORICAS,

        "provincia_utilizada":
            False,

        "preprocesamiento":
            {
                "capping":
                    False,

                "standard_scaler":
                    False,

                "imputacion_numerica":
                    False,

                "missing_values":
                    (
                        "Conservados para manejo "
                        "nativo de HGB."
                    ),

                "tipo_compania":
                    (
                        "Categorias aprendidas "
                        "exclusivamente desde TRAIN. "
                        "Categorias desconocidas en "
                        "TEST se convierten en missing."
                    ),
            },

        "train":
            {
                "periodo":
                    "2012-2018",

                **metricas_train,
            },

        "test":
            {
                "periodo":
                    "2022-2023",

                **metricas_test,

                "ranking_metrics":
                    ranking_metrics[
                        [
                            "K",
                            "POSITIVOS_TOP_K",
                            "PRECISION_AT_K",
                            "RECALL_AT_K",
                            "LIFT_AT_K",
                        ]
                    ].to_dict(
                        orient="records"
                    ),

                "evaluacion_final":
                    True,

                "utilizado_para_seleccion":
                    False,
            },

        "analisis_por_anio":
            {
                "metricas":
                    year_metrics.to_dict(
                        orient="records"
                    ),

                "ranking":
                    year_ranking.to_dict(
                        orient="records"
                    ),
            },

        "warnings_entrenamiento":
            warning_messages,

        "archivos_salida":
            {
                "metricas":
                    ruta_relativa(
                        METRICS_PATH
                    ),

                "ranking_metrics":
                    ruta_relativa(
                        RANKING_METRICS_PATH
                    ),

                "ranking_completo":
                    ruta_relativa(
                        RANKING_PATH
                    ),

                "metricas_por_anio":
                    ruta_relativa(
                        YEAR_METRICS_PATH
                    ),

                "ranking_por_anio":
                    ruta_relativa(
                        YEAR_RANKING_METRICS_PATH
                    ),

                "top500":
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

        "regla_post_test":
            (
                "Los resultados de TEST no "
                "deben utilizarse para modificar "
                "retrospectivamente el modelo v10. "
                "Cualquier nuevo desarrollo debe "
                "realizarse como una nueva version."
            ),

        "entorno":
            {
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
    # MOSTRAR RESULTADO
    # --------------------------------------------------------

    mostrar_resultados(
        metricas_train,
        metricas_test,
        ranking_metrics,
        year_metrics,
        year_ranking,
    )

    print(
        "\n"
        + "=" * 120
    )

    print(
        "ARCHIVOS GENERADOS"
    )

    print(
        "=" * 120
    )

    print(
        METRICS_PATH
    )

    print(
        RANKING_METRICS_PATH
    )

    print(
        RANKING_PATH
    )

    print(
        YEAR_METRICS_PATH
    )

    print(
        YEAR_RANKING_METRICS_PATH
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
        "\n"
        + "=" * 120
    )

    print(
        "EVALUACIÓN FINAL v10 COMPLETADA"
    )

    print(
        "=" * 120
    )

    print(
        "\nLos resultados obtenidos en TEST "
        "constituyen la evaluación final "
        "de generalización de v10."
    )

    print(
        "\nNo modificar el modelo v10 "
        "en función de estos resultados."
    )


if __name__ == "__main__":
    main()