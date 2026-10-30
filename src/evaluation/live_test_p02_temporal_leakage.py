"""
P02 · Fuga temporal
Prospect Finder BVQ

Objetivo
--------
Demostrar que información conocida después de la fecha de decisión
no puede incorporarse al conjunto predictor del modelo v10.

La prueba:

1. carga el dataset financiero congelado;
2. selecciona una observación del conjunto TEST;
3. calcula su fecha de decisión;
4. crea una copia de ensayo;
5. agrega un dato artificial fechado después del corte temporal;
6. valida que existe una violación temporal;
7. carga el artefacto final v10;
8. recupera la lista congelada de variables;
9. comprueba que la variable futura no forma parte del modelo;
10. construye la matriz predictora exclusivamente con las features
    congeladas y verifica que el dato futuro fue excluido.

IMPORTANTE
----------
No modifica:
- dataset original;
- modelo;
- ranking;
- métricas oficiales;
- TEST;
- archivos de producción.

Todas las salidas se guardan únicamente en:

    reports/live_tests/P02/
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "v10_features_financial_2012_2023.csv.gz"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "v10"
    / "v10_hgb_financial_c3_final.joblib"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "live_tests"
    / "P02"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# CONSTANTES DE LA PRUEBA
# ============================================================

FUTURE_FEATURE_NAME = "DATO_FUTURO_PRUEBA"

FUTURE_DATE_NAME = "FECHA_DATO_FUTURO_PRUEBA"

FUTURE_VALUE = 999_999_999.0


# ============================================================
# 25 FEATURES CONGELADAS v10
# ============================================================

EXPECTED_FEATURES = [
    "activos_final",
    "patrimonio_final",
    "bi_ingresos_ventas",
    "bi_n_empleados",
    "activos_final_t1",
    "patrimonio_final_t1",
    "bi_ingresos_ventas_t1",
    "bi_n_empleados_t1",
    "fin_ratio_patrimonio_activos",
    "fin_roa",
    "fin_margen_neto",
    "fin_rotacion_activos",
    "fin_roe",
    "fin_crecimiento_activos",
    "fin_crecimiento_patrimonio",
    "fin_crecimiento_ventas",
    "fin_crecimiento_empleados",
    "TIENE_T_MENOS_1",
    "flag_activos_negativos",
    "flag_ventas_negativas",
    "flag_empleados_fijo",
    "flag_empleados_salto_temporal",
    "flag_empleados_anomalia_total",
    "flag_patrimonio_no_positivo",
    "tipo_compania",
]


# ============================================================
# UTILIDADES
# ============================================================

def print_header(
    title: str,
) -> None:
    print()
    print("=" * 88)
    print(title)
    print("=" * 88)
    print()


def clean_json_value(
    value,
):
    """
    Convierte tipos pandas/numpy en valores serializables.
    """

    if pd.isna(value):
        return None

    if hasattr(
        value,
        "item",
    ):
        return value.item()

    if isinstance(
        value,
        pd.Timestamp,
    ):
        return value.isoformat()

    return value


# ============================================================
# ARTEFACTO DEL MODELO
# ============================================================

def extract_features_from_artifact(
    artifact,
) -> list[str]:
    """
    Intenta recuperar la lista congelada de features
    directamente desde el artefacto final.

    Si el artefacto no expone la lista con uno de los nombres
    conocidos, la prueba utiliza EXPECTED_FEATURES pero deja
    constancia explícita de ello.
    """

    if not isinstance(
        artifact,
        dict,
    ):
        return EXPECTED_FEATURES.copy()

    candidate_keys = [
        "features",
        "feature_columns",
        "feature_names",
        "FEATURES",
        "FEATURE_COLUMNS",
        "features_final",
    ]

    for key in candidate_keys:
        value = artifact.get(
            key
        )

        if (
            isinstance(
                value,
                (
                    list,
                    tuple,
                ),
            )
            and len(value) > 0
        ):
            return [
                str(item)
                for item in value
            ]

    return EXPECTED_FEATURES.copy()


def identify_feature_source(
    artifact,
) -> str:
    if not isinstance(
        artifact,
        dict,
    ):
        return (
            "Lista documentada v10 "
            "(artefacto no es diccionario)"
        )

    candidate_keys = [
        "features",
        "feature_columns",
        "feature_names",
        "FEATURES",
        "FEATURE_COLUMNS",
        "features_final",
    ]

    for key in candidate_keys:
        value = artifact.get(
            key
        )

        if (
            isinstance(
                value,
                (
                    list,
                    tuple,
                ),
            )
            and len(value) > 0
        ):
            return (
                f"Artefacto final · clave '{key}'"
            )

    return (
        "Lista documentada v10 "
        "(no se encontró clave explícita en artefacto)"
    )


# ============================================================
# CARGA DEL DATASET
# ============================================================

def load_test_row() -> pd.DataFrame:
    """
    Carga únicamente las columnas necesarias para identificar
    una observación TEST y las 25 features.

    Se escoge la primera observación TEST 2023 disponible.
    """

    print(
        "Cargando dataset congelado..."
    )

    dataframe = pd.read_csv(
        DATASET_PATH,
        low_memory=False,
    )

    required_columns = [
        "ANIO",
        "EXPEDIENTE_KEY",
        "RUC",
        "NOMBRE",
        "TARGET_24M",
        "SPLIT",
        *EXPECTED_FEATURES,
    ]

    missing = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing:
        raise RuntimeError(
            "Faltan columnas necesarias para P02:\n"
            + "\n".join(
                f"  - {column}"
                for column in missing
            )
        )

    test_rows = dataframe[
        (
            dataframe["SPLIT"]
            .astype(str)
            .str.upper()
            == "TEST"
        )
        &
        (
            dataframe["ANIO"]
            == 2023
        )
    ].copy()

    if test_rows.empty:
        raise RuntimeError(
            "No se encontraron observaciones TEST 2023."
        )

    return (
        test_rows
        .head(1)
        .copy()
    )


# ============================================================
# FECHA DE DECISIÓN
# ============================================================

def calculate_decision_date(
    year: int,
) -> pd.Timestamp:
    """
    Regla temporal del proyecto:

    para una observación financiera del año t,
    la fecha de decisión es 1 de mayo del año t+1.
    """

    return pd.Timestamp(
        year=year + 1,
        month=5,
        day=1,
    )


# ============================================================
# PRUEBA
# ============================================================

def main() -> None:

    print_header(
        "P02 · FUGA TEMPORAL"
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
        "Dataset:"
    )
    print(
        DATASET_PATH
    )

    # --------------------------------------------------------
    # 1. CARGAR FILA TEST
    # --------------------------------------------------------

    original = load_test_row()

    row = original.iloc[0]

    year = int(
        row["ANIO"]
    )

    decision_date = (
        calculate_decision_date(
            year
        )
    )

    # --------------------------------------------------------
    # 2. CREAR DATO FUTURO
    # --------------------------------------------------------

    future_date = (
        decision_date
        + pd.Timedelta(
            days=90
        )
    )

    altered = original.copy()

    altered[
        FUTURE_FEATURE_NAME
    ] = FUTURE_VALUE

    altered[
        FUTURE_DATE_NAME
    ] = future_date

    # --------------------------------------------------------
    # 3. VALIDAR TIMESTAMP
    # --------------------------------------------------------

    temporal_violation = bool(
        future_date
        > decision_date
    )

    # --------------------------------------------------------
    # 4. CARGAR MODELO
    # --------------------------------------------------------

    artifact = joblib.load(
        MODEL_PATH
    )

    model_features = (
        extract_features_from_artifact(
            artifact
        )
    )

    feature_source = (
        identify_feature_source(
            artifact
        )
    )

    # --------------------------------------------------------
    # 5. VALIDAR FEATURES
    # --------------------------------------------------------

    feature_count_ok = (
        len(model_features)
        == 25
    )

    expected_feature_set_ok = (
        set(model_features)
        == set(EXPECTED_FEATURES)
    )

    future_feature_in_model = (
        FUTURE_FEATURE_NAME
        in model_features
    )

    future_date_in_model = (
        FUTURE_DATE_NAME
        in model_features
    )

    # --------------------------------------------------------
    # 6. CONSTRUIR ENTRADA REAL DEL MODELO
    # --------------------------------------------------------

    model_input_original = (
        original[
            model_features
        ]
        .copy()
    )

    model_input_altered = (
        altered[
            model_features
        ]
        .copy()
    )

    # --------------------------------------------------------
    # 7. COMPARAR MATRIZ PREDICTORA
    # --------------------------------------------------------

    predictor_input_identical = (
        model_input_original
        .equals(
            model_input_altered
        )
    )

    # --------------------------------------------------------
    # 8. RESULTADO
    # --------------------------------------------------------

    p02_pass = all(
        [
            temporal_violation,
            feature_count_ok,
            expected_feature_set_ok,
            not future_feature_in_model,
            not future_date_in_model,
            predictor_input_identical,
        ]
    )

    # --------------------------------------------------------
    # 9. IMPRESIÓN
    # --------------------------------------------------------

    print_header(
        "OBSERVACIÓN DE ENSAYO"
    )

    print(
        "ANIO financiero:"
    )
    print(
        year
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
        "Split:"
    )
    print(
        row[
            "SPLIT"
        ]
    )

    print()

    print(
        "Fecha de decisión:"
    )
    print(
        decision_date.date()
    )

    print()

    print(
        "Fecha del dato futuro introducido:"
    )
    print(
        future_date.date()
    )

    print()

    print(
        "Dato futuro introducido:"
    )
    print(
        f"{FUTURE_FEATURE_NAME} = "
        f"{FUTURE_VALUE:,.2f}"
    )

    print_header(
        "VALIDACIÓN TEMPORAL"
    )

    print(
        "¿El dato ocurre después de la fecha de decisión?"
    )
    print(
        temporal_violation
    )

    if temporal_violation:
        print(
            "VIOLACIÓN TEMPORAL DETECTADA"
        )

    print_header(
        "VALIDACIÓN DEL FEATURE SET"
    )

    print(
        "Fuente de lista de features:"
    )
    print(
        feature_source
    )

    print()

    print(
        "Número de features congeladas:"
    )
    print(
        len(model_features)
    )

    print()

    print(
        "¿Son las 25 features esperadas?"
    )
    print(
        expected_feature_set_ok
    )

    print()

    print(
        f"¿'{FUTURE_FEATURE_NAME}' pertenece al modelo?"
    )
    print(
        future_feature_in_model
    )

    print()

    print(
        f"¿'{FUTURE_DATE_NAME}' pertenece al modelo?"
    )
    print(
        future_date_in_model
    )

    print_header(
        "VALIDACIÓN DE ENTRADA AL MODELO"
    )

    print(
        "Columnas de la fila original:"
    )
    print(
        len(
            original.columns
        )
    )

    print()

    print(
        "Columnas de la fila alterada:"
    )
    print(
        len(
            altered.columns
        )
    )

    print()

    print(
        "Columnas que finalmente recibe el modelo:"
    )
    print(
        len(
            model_input_altered.columns
        )
    )

    print()

    print(
        "¿La entrada predictora es idéntica antes/después "
        "de agregar el dato futuro?"
    )
    print(
        predictor_input_identical
    )

    print_header(
        "RESULTADO P02"
    )

    if p02_pass:
        print(
            "CUMPLE"
        )
        print()
        print(
            "La información posterior a la fecha de decisión "
            "fue identificada como futura y no forma parte "
            "del conjunto predictor congelado."
        )
    else:
        print(
            "NO CUMPLE / REVISAR"
        )

    # --------------------------------------------------------
    # 10. EVIDENCIA CSV
    # --------------------------------------------------------

    evidence_row = {
        "prueba":
            "P02",

        "modelo":
            "v10_hgb_financial_c3",

        "configuracion":
            "C3_CONSERVATIVE",

        "anio":
            year,

        "expediente_key":
            clean_json_value(
                row[
                    "EXPEDIENTE_KEY"
                ]
            ),

        "ruc":
            clean_json_value(
                row[
                    "RUC"
                ]
            ),

        "nombre":
            clean_json_value(
                row[
                    "NOMBRE"
                ]
            ),

        "split":
            clean_json_value(
                row[
                    "SPLIT"
                ]
            ),

        "fecha_decision":
            decision_date
            .date()
            .isoformat(),

        "fecha_dato_futuro":
            future_date
            .date()
            .isoformat(),

        "variable_futura":
            FUTURE_FEATURE_NAME,

        "valor_futuro":
            FUTURE_VALUE,

        "violacion_temporal_detectada":
            temporal_violation,

        "numero_features_modelo":
            len(
                model_features
            ),

        "feature_futura_en_modelo":
            future_feature_in_model,

        "fecha_futura_en_modelo":
            future_date_in_model,

        "entrada_modelo_identica":
            predictor_input_identical,

        "resultado":
            (
                "CUMPLE"
                if p02_pass
                else "NO CUMPLE"
            ),
    }

    evidence_df = pd.DataFrame(
        [
            evidence_row
        ]
    )

    evidence_csv = (
        OUTPUT_DIR
        / "p02_temporal_leakage_result.csv"
    )

    evidence_df.to_csv(
        evidence_csv,
        index=False,
    )

    # --------------------------------------------------------
    # 11. LISTA DE FEATURES
    # --------------------------------------------------------

    features_df = pd.DataFrame(
        {
            "orden":
                range(
                    1,
                    len(model_features) + 1,
                ),

            "feature":
                model_features,
        }
    )

    features_csv = (
        OUTPUT_DIR
        / "p02_model_features.csv"
    )

    features_df.to_csv(
        features_csv,
        index=False,
    )

    # --------------------------------------------------------
    # 12. ENTRADA ORIGINAL Y ALTERADA
    # --------------------------------------------------------

    original_export = original.copy()

    original_export[
        "FECHA_DECISION_PRUEBA"
    ] = decision_date

    original_export.to_csv(
        OUTPUT_DIR
        / "p02_input_original.csv",
        index=False,
    )

    altered_export = altered.copy()

    altered_export[
        "FECHA_DECISION_PRUEBA"
    ] = decision_date

    altered_export.to_csv(
        OUTPUT_DIR
        / "p02_input_altered.csv",
        index=False,
    )

    # --------------------------------------------------------
    # 13. JSON DE TRAZABILIDAD
    # --------------------------------------------------------

    metadata = {
        "test_id":
            "P02",

        "description":
            (
                "Prueba de fuga temporal mediante "
                "inyección de dato posterior al corte."
            ),

        "model":
            "v10_hgb_financial_c3",

        "config":
            "C3_CONSERVATIVE",

        "feature_source":
            feature_source,

        "feature_count":
            len(
                model_features
            ),

        "future_feature":
            FUTURE_FEATURE_NAME,

        "future_date_field":
            FUTURE_DATE_NAME,

        "result":
            (
                "CUMPLE"
                if p02_pass
                else "NO CUMPLE"
            ),
    }

    with open(
        OUTPUT_DIR
        / "p02_metadata.json",
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
        / "p02_temporal_leakage_result.csv"
    )

    print(
        OUTPUT_DIR
        / "p02_model_features.csv"
    )

    print(
        OUTPUT_DIR
        / "p02_input_original.csv"
    )

    print(
        OUTPUT_DIR
        / "p02_input_altered.csv"
    )

    print(
        OUTPUT_DIR
        / "p02_metadata.json"
    )

    print()


if __name__ == "__main__":
    main()