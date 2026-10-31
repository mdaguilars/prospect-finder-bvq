# Demo reproducible para evaluador — Prospect Finder BVQ

## Propósito

Esta carpeta proporciona una ruta controlada para revisar el flujo funcional de Prospect Finder BVQ sin publicar datos empresariales reales ni artefactos institucionales restringidos.

La demo no reemplaza la evaluación científica de v10 ni genera nuevas métricas del modelo final.

## Versión académica de referencia

- Modelo final: `v10_hgb_financial_c3`
- Configuración: `C3_CONSERVATIVE`
- Algoritmo: `HistGradientBoostingClassifier`
- Variables predictoras: 25
- TRAIN: 2012–2018
- TEST: 2022–2023
- Tag académico de cierre: `v1.0-thesis`
- Commit de cierre: `f48793be9313626bb17c6e13bcd611a580718771`

## Alcance de reproducibilidad

El repositorio permite revisar la metodología, scripts, configuración, particiones temporales, métricas congeladas, pruebas automatizadas, pruebas funcionales y evidencias P01–P06.

Los datasets empresariales procesados y el artefacto `.joblib` del modelo final no se distribuyen públicamente. Por ello, la reproducción se divide en dos niveles:

1. **Revisión científica:** metodología, configuración, evidencias y resultados oficiales de v10.
2. **Demo funcional sintética:** flujo de aplicación con datos ficticios, sin recalcular ni sustituir las métricas oficiales.

## Resultados oficiales de TEST

- Observaciones: 260.445
- Positivos: 54
- PR-AUC: 0,007468801
- ROC-AUC: 0,934603901
- Top 50: 0 positivos
- Top 100: 0 positivos
- Top 200: 1 positivo
- Primer positivo: posición 165

Estos valores corresponden a la evaluación oficial de v10 y no deben confundirse con resultados de una demo sintética.

## Principio de uso

`Modelo → Priorización → Explicación → Especialista → Decisión`

El score representa prioridad relativa y no una probabilidad calibrada de emisión.

## Integridad metodológica

La demo sintética no implica reentrenamiento, cambio de hiperparámetros, cambio de variables, modificación del target ni reutilización de TEST para seleccionar mejoras.

Cualquier evolución predictiva posterior deberá identificarse como una nueva versión del modelo.
