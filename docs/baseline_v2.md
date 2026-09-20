# Baseline v2 — Regresión Logística sin SECTOR_CIIU

## 1. Objetivo

El objetivo del Baseline v2 es evaluar si la variable categórica `SECTOR_CIIU` estaba introduciendo inestabilidad temporal en el modelo de referencia.

El experimento mantiene la misma estructura metodológica del Baseline v1 y elimina únicamente la variable:

`SECTOR_CIIU`

De esta forma se busca determinar si el desempeño del modelo mejora al depender exclusivamente de variables financieras numéricas.

---

## 2. Motivación del experimento

El análisis del Baseline v1 mostró que varias variables asociadas al sector económico presentaban coeficientes de magnitud elevada.

Adicionalmente, los eventos positivos no se encuentran distribuidos de forma uniforme entre sectores.

En TRAIN, una proporción importante de los futuros emisores se concentra en determinados sectores, mientras que otros presentan pocos o ningún evento positivo.

Esta situación podía provocar que el modelo aprendiera asociaciones sectoriales específicas del período histórico que posteriormente no se mantuvieran de la misma forma en períodos futuros.

Por esta razón se planteó un experimento controlado en el cual se mantiene todo el pipeline del Baseline v1 y se elimina únicamente `SECTOR_CIIU`.

---

## 3. Pregunta experimental

La pregunta principal es:

**¿Eliminar `SECTOR_CIIU` mejora la capacidad de generalización temporal del modelo?**

Para responderla se comparan Baseline v1 y Baseline v2 utilizando exclusivamente:

- TRAIN
- VALIDATION

El conjunto TEST no se utiliza durante esta fase de selección.

---

## 4. Dataset utilizado

Archivo de entrada:

`data/processed/mvp_features_2015_2023.csv.gz`

El dataset corresponde al mismo utilizado por el Baseline v1.

La unidad de análisis es:

`empresa-año`

La variable objetivo es:

`TARGET_24M`

donde:

- `1`: la empresa se registra por primera vez como emisor dentro de los siguientes 24 meses.
- `0`: la empresa no se registra como nuevo emisor dentro de ese horizonte.

---

## 5. División temporal

Se mantiene exactamente la misma división temporal del Baseline v1.

| Conjunto | Período | Observaciones | Positivos | Prevalencia |
|---|---|---:|---:|---:|
| TRAIN | 2015–2020 | 514.527 | 340 | 0,0661 % |
| VALIDATION | 2021 | 109.101 | 42 | 0,0385 % |

El conjunto TEST 2022–2023 no fue evaluado en este experimento.

Esto permite utilizar VALIDATION como conjunto de comparación entre alternativas sin volver a consultar TEST.

---

## 6. Variables utilizadas

El Baseline v2 utiliza únicamente las 16 variables numéricas del Baseline v1.

### Variables monetarias transformadas

- `LOG_ACTIVO_TOTAL`
- `LOG_ACTIVO_CORRIENTE`
- `LOG_EFECTIVO`
- `LOG_PASIVO_TOTAL`
- `LOG_PASIVO_CORRIENTE`
- `LOG_PASIVO_NO_CORRIENTE`
- `LOG_PATRIMONIO`
- `LOG_CAPITAL`
- `LOG_UTILIDAD_NETA`

### Razones financieras

- `LIQUIDEZ_CORRIENTE`
- `ENDEUDAMIENTO`
- `AUTONOMIA_FINANCIERA`
- `ROA`
- `EFECTIVO_ACTIVOS`
- `CAPITAL_ACTIVOS`
- `PASIVO_CORRIENTE_PASIVO`

---

## 7. Variable eliminada

La única variable eliminada respecto del Baseline v1 es:

`SECTOR_CIIU`

No se realizaron otros cambios en las variables predictoras.

Esto permite interpretar el experimento como una comparación controlada entre:

- Baseline v1: variables financieras + sector.
- Baseline v2: únicamente variables financieras.

---

## 8. Preprocesamiento

El tratamiento de las variables numéricas se mantiene equivalente al Baseline v1.

Se aplican:

- `SimpleImputer(strategy="median")`
- `StandardScaler()`

Los parámetros de imputación y escalamiento se ajustan utilizando exclusivamente TRAIN.

Debido a que `SECTOR_CIIU` fue eliminado, el Baseline v2 no requiere codificación categórica mediante `OneHotEncoder`.

---

## 9. Modelo

Se utiliza:

`LogisticRegression`

La configuración registrada para el experimento es:

| Parámetro | Valor |
|---|---|
| Modelo | LogisticRegression |
| `C` | 1.0 |
| `class_weight` | balanced |
| `solver` | lbfgs |
| Regularización | L2 |
| `l1_ratio` | 0 |
| `max_iter` | 2000 |
| `random_state` | 42 |
| Threshold diagnóstico | 0.50 |

La configuración es equivalente al Baseline v1, excepto por la exclusión de `SECTOR_CIIU`.

---

## 10. Tratamiento del desbalance

Se mantiene:

`class_weight="balanced"`

debido al fuerte desbalance entre futuros emisores y empresas que no se convierten en emisores dentro del horizonte observado.

Los valores producidos por `predict_proba()` no se consideran todavía probabilidades calibradas.

Por esta razón, los scores del modelo no deben interpretarse directamente como una probabilidad real de convertirse en emisor.

---

## 11. Métricas de evaluación

Se utilizan las mismas métricas del Baseline v1.

### Métricas generales

- PR-AUC
- ROC-AUC
- Precision
- Recall
- F1

### Métricas de ranking

- Precision@K
- Recall@K
- Lift@K

con:

- K = 50
- K = 100
- K = 200

La métrica Accuracy no se utiliza como criterio principal debido al desbalance extremo de clases.

---

## 12. Resultados en TRAIN

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0,080689 |
| ROC-AUC | 0,931346 |
| Precision | 0,003932 |
| Recall | 0,858824 |
| F1 | 0,007828 |

### Matriz de confusión en TRAIN

Utilizando un threshold de 0,50:

| Resultado | Cantidad |
|---|---:|
| TN | 440.216 |
| FP | 73.971 |
| FN | 48 |
| TP | 292 |

TRAIN contiene:

- 514.527 observaciones;
- 340 positivos;
- prevalencia aproximada de 0,0661 %.

---

## 13. Resultados en VALIDATION

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0,024402 |
| ROC-AUC | 0,961619 |
| Precision | 0,002485 |
| Recall | 0,952381 |
| F1 | 0,004956 |

### Matriz de confusión en VALIDATION

Utilizando un threshold de 0,50:

| Resultado | Cantidad |
|---|---:|
| TN | 93.000 |
| FP | 16.059 |
| FN | 2 |
| TP | 40 |

VALIDATION contiene:

- 109.101 observaciones;
- 42 positivos;
- prevalencia aproximada de 0,0385 %.

---

## 14. Resultados de ranking en TRAIN

| K | Positivos Top-K | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 18 | 0,3600 | 0,0529 | 544,79 |
| 100 | 38 | 0,3800 | 0,1118 | 575,06 |
| 200 | 56 | 0,2800 | 0,1647 | 423,73 |

---

## 15. Resultados de ranking en VALIDATION

| K | Positivos Top-K | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 4 | 0,0800 | 0,0952 | 207,81 |
| 100 | 5 | 0,0500 | 0,1190 | 129,88 |
| 200 | 5 | 0,0250 | 0,1190 | 64,94 |

---

## 16. Comparación Baseline v1 vs Baseline v2

### Métricas generales en VALIDATION

| Métrica | Baseline v1 | Baseline v2 |
|---|---:|---:|
| PR-AUC | 0,031095 | 0,024402 |
| ROC-AUC | 0,940593 | 0,961619 |
| Precision | 0,002566 | 0,002485 |
| Recall | 0,880952 | 0,952381 |
| F1 | 0,005118 | 0,004956 |

La eliminación de `SECTOR_CIIU` produce un incremento de ROC-AUC y Recall utilizando el threshold diagnóstico de 0,50.

Sin embargo, disminuyen PR-AUC, Precision y F1.

Debido al fuerte desbalance, el incremento de ROC-AUC no se considera suficiente por sí mismo para afirmar que el Baseline v2 es superior.

---

## 17. Comparación de ranking

### Top 50

| Métrica | Baseline v1 | Baseline v2 |
|---|---:|---:|
| Positivos | 5 | 4 |
| Precision@50 | 0,1000 | 0,0800 |
| Recall@50 | 0,1190 | 0,0952 |
| Lift@50 | 259,76 | 207,81 |

El Baseline v2 identifica un positivo menos dentro de las primeras 50 empresas priorizadas.

### Top 100

| Métrica | Baseline v1 | Baseline v2 |
|---|---:|---:|
| Positivos | 5 | 5 |
| Precision@100 | 0,0500 | 0,0500 |
| Recall@100 | 0,1190 | 0,1190 |
| Lift@100 | 129,88 | 129,88 |

Los dos modelos presentan el mismo resultado en Top 100.

### Top 200

| Métrica | Baseline v1 | Baseline v2 |
|---|---:|---:|
| Positivos | 5 | 5 |
| Precision@200 | 0,0250 | 0,0250 |
| Recall@200 | 0,1190 | 0,1190 |
| Lift@200 | 64,94 | 64,94 |

Los resultados también son equivalentes en Top 200.

---

## 18. Interpretación

El objetivo del proyecto no es únicamente clasificar correctamente cada observación, sino construir un ranking que permita reducir un universo amplio de empresas a un grupo manejable para análisis posterior por parte de la BVQ.

Desde esta perspectiva, las métricas prioritarias son:

- PR-AUC;
- Precision@K;
- Recall@K;
- Lift@K.

El Baseline v2 mejora ROC-AUC y Recall al threshold 0,50, pero no mejora las métricas consideradas más relevantes para la priorización.

En particular:

- PR-AUC disminuye de 0,031095 a 0,024402.
- Precision@50 disminuye de 10 % a 8 %.
- Recall@50 disminuye de 11,90 % a 9,52 %.
- Top 100 y Top 200 permanecen sin mejora.

Por tanto, la eliminación de `SECTOR_CIIU` no aporta una mejora suficiente para reemplazar al Baseline v1.

---

## 19. Interpretación del threshold 0,50

En VALIDATION, el Baseline v2 obtiene:

- 40 verdaderos positivos;
- 2 falsos negativos;
- 16.059 falsos positivos.

El Recall de 95,24 % resulta elevado, pero se obtiene a costa de un número muy grande de falsos positivos.

Esto refuerza la conclusión obtenida en el Baseline v1:

**un threshold fijo de 0,50 no constituye una estrategia operativa apropiada para el problema de prospección.**

El sistema debe evaluarse principalmente como una herramienta de ranking.

---

## 20. Resultado del experimento

La hipótesis evaluada era que la eliminación de `SECTOR_CIIU` podría mejorar la estabilidad temporal del modelo.

Los resultados muestran que esta eliminación:

- mejora ROC-AUC;
- mejora Recall al threshold 0,50;
- reduce PR-AUC;
- reduce Precision@50;
- reduce Recall@50;
- no mejora Top 100;
- no mejora Top 200.

Con base en las métricas prioritarias definidas para el proyecto, el Baseline v2 no presenta una mejora material frente al Baseline v1.

---

## 21. Decisión metodológica

Se mantiene el Baseline v1 como modelo de referencia.

`SECTOR_CIIU` permanece incluido en el modelo de referencia actual.

Esto no implica que la variable sectorial haya demostrado ser estable de forma definitiva.

Su comportamiento deberá continuar evaluándose en modelos posteriores, especialmente cuando se incorporen:

- nuevas variables temporales;
- modelos no lineales;
- mayor análisis de estabilidad;
- técnicas de interpretabilidad.

---

## 22. Uso del conjunto TEST

El conjunto TEST 2022–2023:

**no fue evaluado durante este experimento.**

La comparación entre Baseline v1 y Baseline v2 se realizó utilizando únicamente:

- TRAIN 2015–2020;
- VALIDATION 2021.

Esta decisión busca evitar utilizar repetidamente TEST para seleccionar modelos o hiperparámetros.

---

## 23. Fortalezas del experimento

El experimento presenta las siguientes fortalezas:

- modifica una sola condición respecto del Baseline v1;
- mantiene el mismo dataset;
- mantiene la misma división temporal;
- mantiene el mismo algoritmo;
- mantiene la misma regularización;
- mantiene el mismo tratamiento de clases;
- compara las mismas métricas;
- no utiliza TEST para seleccionar la alternativa;
- permite analizar específicamente el efecto de eliminar `SECTOR_CIIU`.

---

## 24. Limitaciones

Las principales limitaciones del experimento son:

1. Continúa existiendo un desbalance extremo.
2. VALIDATION contiene únicamente 42 eventos positivos.
3. Se evalúa un solo año de validación.
4. El modelo continúa limitado a relaciones lineales.
5. No se incorporan todavía variables de tendencia.
6. El experimento únicamente permite analizar la eliminación completa de la variable sectorial.
7. No demuestra que la información sectorial sea estable en períodos futuros.
8. Los scores del modelo no están calibrados.
9. El threshold 0,50 continúa siendo únicamente diagnóstico.

---

## 25. Archivos del experimento

Métricas TRAIN y VALIDATION:

`reports/results/logistic_no_sector_v2_metrics_train_validation.csv`

Ranking:

`reports/results/logistic_no_sector_v2_ranking_train_validation.csv`

Coeficientes:

`reports/results/logistic_no_sector_v2_coefficients.csv`

Metadatos:

`reports/results/logistic_no_sector_v2_metadata.json`

Análisis de estabilidad sectorial:

`reports/results/sector_stability_train_validation.csv`

Resumen sectorial del análisis de errores:

`reports/results/baseline_error_sector_summary.csv`

---

## 26. Configuración registrada

Los metadatos del experimento registran:

| Elemento | Valor |
|---|---|
| Experimento | Baseline v2 |
| Modelo | LogisticRegression |
| Descripción | Regresión logística equivalente al Baseline v1 eliminando SECTOR_CIIU |
| Objetivo | Evaluar si la variable sectorial genera inestabilidad temporal |
| `random_state` | 42 |
| Threshold | 0,50 |
| `C` | 1.0 |
| `class_weight` | balanced |
| `solver` | lbfgs |
| `l1_ratio` | 0 |
| Regularización | L2 |
| `max_iter` | 2000 |
| Sector CIIU utilizado | No |
| TRAIN | 2015–2020 |
| VALIDATION | 2021 |
| TEST evaluado en selección | No |
| Probabilidades calibradas | No |

---

## 27. Entorno registrado

| Componente | Versión |
|---|---|
| Python | 3.13.7 |
| pandas | 3.0.5 |
| NumPy | 2.5.3 |
| scikit-learn | 1.9.1 |

El entorno completo del proyecto se conserva adicionalmente en:

- `requirements.txt`
- `requirements-lock.txt`

---

## 28. Conclusión

El Baseline v2 permitió evaluar directamente el efecto de eliminar `SECTOR_CIIU`.

Aunque el modelo sin sector presenta un ROC-AUC superior y mayor Recall al threshold 0,50 en VALIDATION, las métricas más relevantes para el objetivo de prospección no mejoran.

PR-AUC disminuye y el resultado Top 50 es inferior al Baseline v1, mientras que Top 100 y Top 200 permanecen sin cambios.

Por esta razón, el Baseline v1 continúa siendo el modelo de referencia para las siguientes etapas del proyecto.