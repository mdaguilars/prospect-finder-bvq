# Congelamiento del Dataset Físico de Features v10-core

**Proyecto:** Prospect Finder BVQ  
**Versión:** v10-core  
**Estado:** CONGELADO  
**Fecha:** octubre de 2026

---

## 1. Propósito

Este documento registra el congelamiento del dataset físico de características correspondiente al Feature Set núcleo v10.

El archivo fue construido de manera reproducible a partir del dataset base v10 previamente congelado y de las reglas definidas en:

`docs/v10_feature_set_freeze.md`

El dataset físico será la fuente de entrada para la siguiente etapa de modelado.

Ningún modelo fue entrenado durante su construcción o validación.

---

## 2. Archivo de origen

Dataset base:

`data/processed/v10_base_integrated_2012_2023.csv.gz`

El dataset base contiene:

- 1.030.671 observaciones empresa-año;
- ejercicios 2012-2023;
- 568 observaciones positivas;
- 310 empresas positivas únicas;
- variable objetivo `TARGET_24M`;
- universo y target previamente congelados.

---

## 3. Script de construcción

El dataset físico de features se construye mediante:

`scripts/build_v10_features.py`

El script:

- carga únicamente las variables requeridas desde la base v10;
- valida tamaño, target y ausencia de duplicados empresa-año;
- ordena determinísticamente por empresa y año;
- aplica reglas determinísticas de calidad;
- genera las variables exactas `t-1`;
- asigna el split temporal congelado;
- valida los conteos esperados;
- genera el archivo físico;
- calcula su hash SHA-256;
- genera un reporte de validación.

No realiza imputación aprendida, escalamiento, normalización, winsorización, codificación categórica ni entrenamiento de modelos.

---

## 4. Archivo físico congelado

Archivo:

`data/processed/v10_features_core_2012_2023.csv.gz`

Características generales:

- filas: 1.030.671;
- columnas totales: 22;
- positivos: 568;
- duplicados empresa-año: 0;
- periodo: 2012-2023.

SHA-256:

`91de8c12e8603d6f2c354f723a7a5e36f30aa8c242edd8ec55d2d8d64f0bcd6c`

El hash fue verificado de forma independiente mediante `Get-FileHash`.

---

## 5. Feature Set núcleo

El Feature Set núcleo contiene 10 variables predictoras conceptuales.

### Variables numéricas del ejercicio t

- `activos_final`
- `patrimonio_final`
- `bi_ingresos_ventas`
- `bi_n_empleados`

### Variables numéricas exactas t-1

- `activos_final_t1`
- `patrimonio_final_t1`
- `bi_ingresos_ventas_t1`
- `bi_n_empleados_t1`

### Variables categóricas

- `tipo_compania`
- `provincia`

`ANIO` no forma parte de las variables predictoras del núcleo.

---

## 6. Reglas determinísticas de calidad

Las reglas fueron aplicadas antes de construir los lags.

### Activos

Los valores negativos de `activos_final` se consideran anomalías de calidad para el Feature Set y se convierten en `NaN`.

Casos detectados:

- 7 observaciones.

### Ventas

Los valores negativos de `bi_ingresos_ventas` se consideran anomalías de calidad para el Feature Set y se convierten en `NaN`.

Casos detectados:

- 6 observaciones.

### Empleados

Se aplican dos reglas.

Regla fija:

- valor menor que 0; o
- valor mayor que 50.000.

Casos detectados:

- 24 observaciones.

Regla temporal:

- existen al menos 2 observaciones históricas previas válidas y no negativas;
- el valor actual es al menos 1.000;
- el valor actual es al menos 100 veces la mediana histórica previa.

Casos detectados:

- 153 observaciones.

Total único de anomalías de empleados:

- 165 observaciones.

Los valores afectados se convierten en `NaN` para el Feature Set.

---

## 7. Impacto de las reglas de calidad

La unión de las anomalías aplicadas al núcleo no afecta observaciones positivas.

Resultado:

- positivos afectados: 0.

Estas reglas modifican únicamente la representación utilizada en el Feature Set físico.

El dataset base congelado permanece sin alteraciones.

---

## 8. Construcción de variables t-1

Las variables `t-1` se generan únicamente cuando existe una observación de la misma empresa exactamente en el ejercicio anterior.

No se utilizan:

- interpolaciones;
- observaciones de dos o más años atrás como sustituto;
- información futura;
- imputaciones para crear el lag.

La limpieza determinística de las variables actuales se realiza antes de construir los lags.

Por tanto, si una observación del ejercicio anterior fue identificada como anomalía y convertida en `NaN`, su correspondiente valor `t-1` también será `NaN`.

---

## 9. Disponibilidad histórica t-1

Observaciones con ejercicio anterior exacto:

- 863.163;
- 83,75 % del universo.

Observaciones positivas con ejercicio anterior exacto:

- 494 de 568;
- 86,97 %.

Cobertura física de los lags después de las reglas de calidad:

| Variable | No nulos |
|---|---:|
| `activos_final_t1` | 858.527 |
| `patrimonio_final_t1` | 858.534 |
| `bi_ingresos_ventas_t1` | 808.748 |
| `bi_n_empleados_t1` | 808.603 |

La ausencia de información `t-1` no provoca la eliminación de observaciones.

---

## 10. Cobertura de las variables predictoras

| Variable | No nulos | Cobertura |
|---|---:|---:|
| `activos_final` | 1.022.903 | 99,25 % |
| `patrimonio_final` | 1.022.910 | 99,25 % |
| `bi_ingresos_ventas` | 962.008 | 93,34 % |
| `bi_n_empleados` | 961.849 | 93,32 % |
| `activos_final_t1` | 858.527 | 83,30 % |
| `patrimonio_final_t1` | 858.534 | 83,30 % |
| `bi_ingresos_ventas_t1` | 808.748 | 78,47 % |
| `bi_n_empleados_t1` | 808.603 | 78,45 % |
| `tipo_compania` | 1.030.663 | 100,00 % |
| `provincia` | 1.030.663 | 100,00 % |

Los porcentajes mostrados con dos decimales corresponden al reporte de construcción.

---

## 11. Split temporal congelado

El dataset conserva el split definido previamente.

| Split | Periodo | Filas | Positivos | Prevalencia |
|---|---|---:|---:|---:|
| TRAIN | 2012-2018 | 470.722 | 407 | 0,086463 % |
| EMBARGO_1 | 2019 | 91.934 | 34 | 0,036983 % |
| VALIDATION | 2020 | 98.471 | 34 | 0,034528 % |
| EMBARGO_2 | 2021 | 109.099 | 39 | 0,035747 % |
| TEST | 2022-2023 | 260.445 | 54 | 0,020734 % |

Los años de embargo no serán utilizados como observaciones para ajuste o evaluación de modelos.

Sus características históricas pueden alimentar variables `t-1` de observaciones posteriores cuando correspondan temporalmente.

---

## 12. TEST

El periodo TEST corresponde a los ejercicios 2022-2023.

Su existencia, tamaño, prevalencia y estructura fueron comprobados como parte de la validación del dataset.

No se ha realizado sobre TEST:

- entrenamiento;
- selección de variables;
- ajuste de hiperparámetros;
- comparación de modelos;
- cálculo de PR-AUC;
- cálculo de ROC-AUC;
- cálculo de Precision@K;
- cálculo de Recall@K;
- cálculo de Lift@K;
- selección del modelo final.

TEST permanece cerrado para evaluación predictiva hasta finalizar la selección metodológica utilizando TRAIN y VALIDATION.

---

## 13. Columnas físicas del archivo

El archivo contiene 22 columnas:

1. `ANIO`
2. `EXPEDIENTE_KEY`
3. `RUC`
4. `NOMBRE`
5. `TARGET_24M`
6. `SPLIT`
7. `activos_final`
8. `patrimonio_final`
9. `bi_ingresos_ventas`
10. `bi_n_empleados`
11. `activos_final_t1`
12. `patrimonio_final_t1`
13. `bi_ingresos_ventas_t1`
14. `bi_n_empleados_t1`
15. `tipo_compania`
16. `provincia`
17. `TIENE_T_MENOS_1`
18. `flag_activos_negativos`
19. `flag_ventas_negativas`
20. `flag_empleados_fijo`
21. `flag_empleados_salto_temporal`
22. `flag_empleados_anomalia_total`

Las columnas administrativas y de auditoría no forman parte automáticamente de la matriz de predictores.

La matriz `X` del núcleo debe construirse únicamente con las 10 variables congeladas.

---

## 14. Transformaciones aprendidas

El dataset físico no contiene transformaciones aprendidas a partir del conjunto completo.

La siguiente etapa deberá realizar dentro del pipeline de modelado y ajustando exclusivamente con TRAIN cualquier proceso como:

- imputación de valores faltantes;
- escalamiento;
- normalización;
- transformación logarítmica si posteriormente se justifica;
- codificación categórica;
- tratamiento aprendido de valores extremos;
- selección de variables;
- ajuste de hiperparámetros.

VALIDATION será utilizado únicamente para comparación y selección metodológica.

TEST permanecerá cerrado.

---

## 15. Reproducibilidad

El dataset físico puede reconstruirse desde el dataset base congelado utilizando:

`python scripts/build_v10_features.py`

La reproducción se considerará correcta si:

- mantiene 1.030.671 filas;
- mantiene 568 positivos;
- mantiene 0 duplicados empresa-año;
- reproduce los conteos congelados de anomalías;
- reproduce los conteos del split;
- reproduce las 22 columnas;
- reproduce el SHA-256 congelado.

Hash esperado:

`91de8c12e8603d6f2c354f723a7a5e36f30aa8c242edd8ec55d2d8d64f0bcd6c`

---

## 16. Política de cambios

A partir de este congelamiento, cualquier modificación que altere:

- universo;
- target;
- variables predictoras;
- reglas determinísticas de calidad;
- construcción de lags;
- split temporal;
- contenido físico del dataset;
- hash del archivo;

deberá generar una nueva versión documentada del dataset.

No se modificarán silenciosamente las reglas de v10-core después de observar resultados de modelado.

---

## 17. Estado final

**Dataset físico de features v10-core: CONGELADO**

Archivo:

`data/processed/v10_features_core_2012_2023.csv.gz`

SHA-256:

`91de8c12e8603d6f2c354f723a7a5e36f30aa8c242edd8ec55d2d8d64f0bcd6c`

Filas:

`1.030.671`

Variables predictoras conceptuales:

`10`

Columnas físicas:

`22`

La siguiente etapa será preparar el pipeline de modelado v10 utilizando exclusivamente TRAIN para aprender transformaciones y parámetros.

**TEST permanece cerrado para evaluación predictiva.**
