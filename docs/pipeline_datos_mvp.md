# Pipeline de datos del MVP — Prospect Finder BVQ

## 1. Objetivo

Este documento describe el proceso reproducible utilizado para construir el dataset del MVP del proyecto:

**Sistema inteligente basado en aprendizaje automático y redes neuronales para identificar y priorizar empresas con potencial de convertirse en emisores del mercado de valores ecuatoriano para la Bolsa de Valores Quito.**

El objetivo del pipeline es transformar información financiera histórica de empresas ecuatorianas y registros oficiales de emisores en un dataset empresa-año apto para entrenamiento y evaluación de modelos de clasificación.

---

## 2. Unidad de análisis

La unidad de análisis es:

**Empresa — Año**

La empresa se identifica mediante su RUC de 13 dígitos.

La clave técnica utilizada durante la construcción del dataset es:

```text
RUC + ANIO