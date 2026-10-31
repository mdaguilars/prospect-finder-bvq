"""Explicabilidad sintética para la demo pública del evaluador.

Este módulo existe únicamente para demostrar el flujo funcional de la
interfaz cuando los artefactos privados del modelo v10 no están disponibles.

No calcula SHAP real, no sustituye las evidencias académicas y no modifica
el modelo congelado.
"""

from __future__ import annotations

from src.api.models.prospect import OperationalProspect


DEMO_GLOBAL_ITEMS = [
    {
        "rank": 1,
        "feature": "activos_final",
        "label": "Activos",
        "mean_abs_shap": 0.120,
    },
    {
        "rank": 2,
        "feature": "bi_ingresos_ventas",
        "label": "Ingresos por ventas",
        "mean_abs_shap": 0.095,
    },
    {
        "rank": 3,
        "feature": "patrimonio_final",
        "label": "Patrimonio",
        "mean_abs_shap": 0.072,
    },
    {
        "rank": 4,
        "feature": "fin_roa",
        "label": "ROA",
        "mean_abs_shap": 0.041,
    },
    {
        "rank": 5,
        "feature": "fin_rotacion_activos",
        "label": "Rotación de activos",
        "mean_abs_shap": 0.030,
    },
]


def get_demo_global_importance(limit: int = 15) -> dict:
    """Devuelve una importancia global ficticia para la demo funcional."""

    return {
        "method": "Explicación sintética de demo; no corresponde a SHAP real.",
        "scope": (
            "Datos ficticios utilizados exclusivamente para demostrar "
            "la interfaz del prototipo."
        ),
        "reference": (
            "Los resultados SHAP oficiales de v10 permanecen en las "
            "evidencias académicas del repositorio."
        ),
        "items": DEMO_GLOBAL_ITEMS[:limit],
    }



def get_demo_prospect_explanation(
    prospect: OperationalProspect,
    top_n: int = 10,
) -> dict:
    """Construye una explicación local ficticia compatible con el frontend."""

    base_value = 0.50
    score = float(prospect.score_afinidad)
    delta = score - base_value

    specifications = [
        (
            "activos_final",
            "Activos",
            prospect.activos_final,
            0.35,
        ),
        (
            "bi_ingresos_ventas",
            "Ingresos por ventas",
            prospect.bi_ingresos_ventas,
            0.26,
        ),
        (
            "patrimonio_final",
            "Patrimonio",
            prospect.patrimonio_final,
            0.18,
        ),
        (
            "fin_rotacion_activos",
            "Rotación de activos",
            prospect.fin_rotacion_activos,
            -0.08,
        ),
        (
            "fin_roa",
            "ROA",
            prospect.fin_roa,
            0.29,
        ),
    ]

    factors = []

    for feature, label, value, weight in specifications:
        contribution = float(delta * weight)

        if contribution > 0:
            direction = "aumenta_afinidad"
        elif contribution < 0:
            direction = "reduce_afinidad"
        else:
            direction = "sin_impacto"

        factors.append(
            {
                "feature": feature,
                "label": label,
                "value": None if value is None else float(value),
                "shap_value": contribution,
                "abs_shap_value": abs(contribution),
                "direction": direction,
            }
        )

    factors.sort(
        key=lambda item: item["abs_shap_value"],
        reverse=True,
    )

    reconstructed = base_value + sum(
        item["shap_value"]
        for item in factors
    )

    positive = [
        item
        for item in factors
        if item["shap_value"] > 0
    ]

    negative = [
        item
        for item in factors
        if item["shap_value"] < 0
    ]

    top_n_effective = min(top_n, len(factors))

    return {
        "empresa": {
            "expediente_key": int(prospect.expediente_key),
            "ruc": prospect.ruc,
            "nombre": prospect.nombre,
            "anio": int(prospect.anio),
        },
        "score": {
            "modelo": score,
            "ranking_operativo": score,
            "diferencia": 0.0,
            "nota": (
                "Score sintético de demo para reproducir el flujo visual. "
                "No es una probabilidad calibrada."
            ),
        },
        "shap": {
            "base_value": base_value,
            "reconstructed_score": reconstructed,
            "local_error": abs(score - reconstructed),
            "background_train_size": 0,
            "max_evals": 0,
            "method": (
                "Explicación sintética de demo; no corresponde a SHAP real."
            ),
            "reference": (
                "La explicación SHAP oficial requiere los artefactos "
                "privados de v10 y se conserva en las evidencias del proyecto."
            ),
        },
        "principales_factores": factors[:top_n_effective],
        "factores_que_aumentan_afinidad": positive[:5],
        "factores_que_reducen_afinidad": negative[:5],
        "metadata": {
            "model_name": "DEMO_SYNTHETIC_UI_FLOW",
            "config_id": "EVALUATOR_DEMO_MODE",
            "features_total": len(factors),
            "top_n": top_n_effective,
            "interpretation": (
                "Valores ficticios utilizados únicamente para validar "
                "el flujo funcional de la interfaz."
            ),
        },
        "ranking": {
            "posicion": int(prospect.ranking),
            "percentil": float(prospect.percentil_ranking),
        },
    }
