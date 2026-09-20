# Baseline v3 — Evaluación de regularización en regresión logística

## 1. Objetivo

El objetivo del experimento v3 es evaluar si una modificación en la intensidad de regularización mejora el desempeño temporal del modelo de referencia.

Se mantiene la misma estructura del Baseline v1:

- mismas variables financieras;
- uso de `SECTOR_CIIU`;
- mismo split temporal;
- mismo esquema de preprocesamiento;
- misma clase ponderada;
- mismo algoritmo de regresión logística.

La única modificación es el parámetro:

```text
C