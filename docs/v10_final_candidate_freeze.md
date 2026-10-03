# Prospect Finder BVQ
## Congelamiento del candidato final v10

**Estado:** CONGELADO ANTES DE TEST  
**Versión:** v10  
**Candidato final:** `v10_hgb_financial_c3`  
**Familia:** HistGradientBoostingClassifier  
**Configuración:** `C3_CONSERVATIVE`

---

## 1. Propósito

Este documento registra formalmente la selección y congelamiento del candidato final de la versión v10 de Prospect Finder BVQ antes de realizar cualquier evaluación sobre el conjunto TEST 2022–2023.

A partir de este punto, la configuración del modelo, el conjunto de variables y los principales parámetros quedan fijados.

El conjunto TEST no debe utilizarse para:

- seleccionar modelos;
- modificar variables;
- ajustar hiperparámetros;
- modificar reglas de preprocesamiento;
- decidir entre alternativas de modelado.

Su utilización posterior tendrá exclusivamente el propósito de realizar una evaluación final de generalización.

---

## 2. Modelo seleccionado

El candidato congelado es:

`v10_hgb_financial_c3`

| Característica | Configuración |
|---|---|
| Algoritmo | `HistGradientBoostingClassifier` |
| Variante | Financiera |
| Configuración | `C3_CONSERVATIVE` |
| Variables físicas | 25 |
| Target | `TARGET_24M` |
| Horizonte del target | 24 meses |
| Provincia como predictor | No |

El modelo busca priorizar empresas con mayor señal histórica asociada a convertirse en emisores durante los siguientes 24 meses.

Su objetivo principal no es realizar una clasificación binaria definitiva, sino generar un ranking de empresas para apoyar la priorización comercial.

---

## 3. Variables congeladas

### 3.1. Variables numéricas core

1. `activos_final`
2. `patrimonio_final`
3. `bi_ingresos_ventas`
4. `bi_n_empleados`
5. `activos_final_t1`
6. `patrimonio_final_t1`
7. `bi_ingresos_ventas_t1`
8. `bi_n_empleados_t1`

### 3.2. Variables booleanas core

1. `TIENE_T_MENOS_1`
2. `flag_activos_negativos`
3. `flag_ventas_negativas`
4. `flag_empleados_fijo`
5. `flag_empleados_salto_temporal`
6. `flag_empleados_anomalia_total`

### 3.3. Variable categórica

1. `tipo_compania`

La variable `provincia` queda excluida del conjunto final de predictores.

### 3.4. Variables financieras derivadas

1. `fin_ratio_patrimonio_activos`
2. `fin_roa`
3. `fin_margen_neto`
4. `fin_rotacion_activos`
5. `fin_roe`
6. `fin_crecimiento_activos`
7. `fin_crecimiento_patrimonio`
8. `fin_crecimiento_ventas`
9. `fin_crecimiento_empleados`

### 3.5. Variable financiera booleana

1. `flag_patrimonio_no_positivo`

---

## 4. Definición de variables financieras

Las variables financieras fueron construidas a partir de cuentas disponibles históricamente y no a partir de los indicadores financieros precalculados de BI.

Esta decisión se tomó porque los indicadores BI presentaban una disponibilidad temporal fuertemente concentrada en 2018, lo cual podía introducir una señal asociada al año o a la disponibilidad de la fuente en lugar de una señal financiera estable.

Las variables derivadas utilizan las siguientes relaciones conceptuales:

- patrimonio / activos;
- utilidad / activos;
- utilidad / ventas;
- ventas / activos;
- utilidad / patrimonio;
- crecimiento de activos;
- crecimiento de patrimonio;
- crecimiento de ventas;
- crecimiento de empleados.

Las reglas de división fueron definidas previamente durante la construcción del dataset financiero v10.

---

## 5. Tratamiento de valores extremos y faltantes

Para el candidato HGB financiero no se aplica capping P01–P99.

Las variables financieras se mantienen en su escala derivada original.

La razón es que `HistGradientBoostingClassifier` trabaja mediante particiones y es considerablemente menos sensible a valores extremos que los modelos que dependen directamente de distancia o escala, como Regresión Logística y MLP.

Los valores faltantes son conservados y manejados de manera nativa por el algoritmo cuando corresponde.

No se eliminan observaciones por presentar valores faltantes en las variables predictoras.

---

## 6. Configuración congelada del modelo

La configuración seleccionada corresponde a `C3_CONSERVATIVE`.

```python
HistGradientBoostingClassifier(
    loss="log_loss",
    learning_rate=0.03,
    max_iter=250,
    max_leaf_nodes=5,
    max_depth=2,
    min_samples_leaf=200,
    l2_regularization=3.0,
    early_stopping=False,
    random_state=42,
    class_weight="balanced",
    categorical_features="from_dtype",
)
```

Estos hiperparámetros quedan congelados antes de la evaluación del TEST.

---

## 7. Protocolo temporal utilizado

El protocolo temporal de la versión v10 queda definido de la siguiente manera:

| Conjunto | Periodo | Observaciones | Positivos | Uso |
|---|---:|---:|---:|---|
| TRAIN | 2012–2018 | 470.722 | 407 | Entrenamiento y desarrollo |
| EMBARGO 1 | 2019 | 91.934 | 34 | Excluido del entrenamiento y evaluación |
| VALIDATION | 2020 | 98.471 | 34 | Comparación y selección durante desarrollo |
| EMBARGO 2 | 2021 | 109.099 | 39 | Excluido del entrenamiento y evaluación |
| TEST | 2022–2023 | 260.445 | 54 | Evaluación final |

**Estado de TEST al momento del congelamiento:** `RESERVADO`

El conjunto TEST no ha sido utilizado para elegir el candidato final ni para ajustar sus hiperparámetros.

---

## 8. Backtesting temporal

La evaluación histórica previa al TEST utilizó cuatro folds con ventana creciente y un año de embargo entre entrenamiento y evaluación.

| Fold | TRAIN | Embargo | Evaluación |
|---:|---|---:|---:|
| 1 | 2012–2013 | 2014 | 2015 |
| 2 | 2012–2014 | 2015 | 2016 |
| 3 | 2012–2015 | 2016 | 2017 |
| 4 | 2012–2016 | 2017 | 2018 |

Este esquema busca medir la capacidad del modelo de generalizar hacia años posteriores sin utilizar información futura durante el entrenamiento.

---

## 9. Resultados del candidato congelado

### VALIDATION 2020

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0.008612 |
| ROC-AUC | 0.949422 |
| Positivos Top 50 | 1 |
| Positivos Top 100 | 2 |
| Positivos Top 200 | 2 |

El resultado de VALIDATION es inferior al comportamiento promedio observado en los backtests históricos, por lo que se conserva como una señal de posible variación temporal que deberá considerarse al interpretar TEST.

---

## 10. Resultados del backtest temporal

Resultados de `v10_hgb_financial_c3`:

| Métrica | Resultado |
|---|---:|
| PR-AUC media | 0.029487 |
| PR-AUC mediana | 0.030329 |
| PR-AUC desviación estándar | 0.002709 |
| PR-AUC mínima | 0.025559 |
| PR-AUC máxima | 0.031732 |
| ROC-AUC media | 0.872163 |
| Lift@50 medio | 94.299911 |
| Lift@100 medio | 76.102088 |
| Lift@200 medio | 68.267274 |
| Positivos acumulados Top 50 | 14 |
| Positivos acumulados Top 100 | 23 |
| Positivos acumulados Top 200 | 40 |

Los positivos acumulados corresponden a la suma de los resultados obtenidos en los cuatro años evaluados del backtest.

---

## 11. Comparación de candidatos por familia

Antes del congelamiento se seleccionó un candidato representativo de cada familia.

| Familia | Candidato | PR-AUC Validation | PR-AUC media backtest | PR-AUC std | Lift@50 | Lift@100 | Lift@200 |
|---|---|---:|---:|---:|---:|---:|---:|
| Logistic Regression | `v10_lr_no_provincia` | 0.008387 | 0.016363 | 0.003383 | 74.853825 | 53.070212 | 43.122520 |
| HistGradientBoosting | `v10_hgb_financial_c3` | 0.008612 | 0.029487 | 0.002709 | 94.299911 | 76.102088 | 68.267274 |
| MLP | `v10_mlp` | 0.009135 | 0.016009 | 0.007558 | 52.458854 | 46.066813 | 40.259647 |

---

## 12. Efecto de las variables financieras

La incorporación de las variables financieras produjo comportamientos diferentes según la familia de modelos.

| Familia | Core PR-AUC backtest | Financial PR-AUC backtest | Variación |
|---|---:|---:|---:|
| Logistic Regression | 0.016363 | 0.015276 | -6,64 % |
| HistGradientBoosting | 0.016891 | 0.029487 | +74,57 % |
| MLP | 0.016009 | 0.013289 | -16,99 % |

### Logistic Regression

Las variables financieras no mejoraron el comportamiento histórico de la Regresión Logística.

### HistGradientBoosting

Las variables financieras produjeron una mejora importante en PR-AUC y también redujeron la variabilidad temporal.

La desviación estándar pasó de:

- Core: **0.003282**
- Financial C3: **0.002709**

### MLP

La incorporación de variables financieras no produjo una mejora histórica consistente en MLP.

---

## 13. Justificación de selección

`v10_hgb_financial_c3` queda congelado como candidato final porque presenta una combinación favorable de:

- mayor PR-AUC media en backtesting;
- mayor PR-AUC mediana;
- menor desviación estándar entre los tres candidatos por familia;
- mejor Lift@50;
- mejor Lift@100;
- mejor Lift@200;
- mayor recuperación acumulada de positivos en los rankings históricos;
- mejora consistente del HGB al incorporar las variables financieras;
- configuración conservadora dentro de las alternativas HGB evaluadas;
- estabilidad temporal favorable dentro de los cuatro folds evaluados.

La selección no se basa exclusivamente en una métrica de VALIDATION.

El comportamiento de VALIDATION 2020 se considera conjuntamente con los cuatro folds históricos para reducir el riesgo de seleccionar una configuración únicamente por su desempeño en un año específico.

---

## 14. Interpretación de negocio

Prospect Finder no se plantea como un sistema que determine automáticamente:

> **“Esta empresa será emisora.”**

El uso previsto es:

> **“Estas empresas presentan mayor prioridad relativa y deberían ser analizadas primero por el equipo especializado.”**

Por esta razón, además de PR-AUC, se consideran especialmente relevantes:

- Precision@K;
- Recall@K;
- Lift@K;
- número de positivos recuperados dentro del Top 50;
- número de positivos recuperados dentro del Top 100;
- número de positivos recuperados dentro del Top 200.

El objetivo operativo consiste en reducir un universo empresarial muy amplio a una lista manejable de prospectos para análisis comercial.

---

## 15. Regla posterior al congelamiento

A partir de este documento quedan congelados:

- familia de algoritmo;
- configuración C3;
- variables predictoras;
- exclusión de provincia;
- reglas de construcción de las variables financieras;
- target;
- horizonte de 24 meses;
- protocolo temporal;
- métricas principales;
- criterio de ranking.

No se realizarán cambios al modelo basándose en los resultados del TEST.

Si el desempeño en TEST resultara inferior al esperado, este resultado deberá reportarse como evidencia de capacidad de generalización y no utilizarse para regresar al proceso de selección y modificar retrospectivamente el candidato v10.

Cualquier desarrollo posterior deberá realizarse como una nueva versión experimental independiente.

---

## 16. Próximo paso

Una vez versionado este congelamiento, se podrá realizar la evaluación única del candidato:

`v10_hgb_financial_c3`

sobre:

`TEST 2022–2023`

La evaluación deberá conservar los mismos criterios utilizados durante el desarrollo:

- PR-AUC;
- ROC-AUC como métrica complementaria;
- Precision@50, @100 y @200;
- Recall@50, @100 y @200;
- Lift@50, @100 y @200;
- positivos recuperados dentro de cada Top K.

Los resultados de TEST deberán considerarse resultados finales de generalización de la versión v10.