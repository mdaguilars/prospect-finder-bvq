# Baseline v1 — Regresión Logística

## 1. Objetivo

El objetivo de este experimento es establecer el primer modelo de referencia para el proyecto Prospect Finder BVQ.

El modelo busca identificar y priorizar empresas ecuatorianas que podrían registrarse por primera vez como emisores del mercado de valores dentro de los siguientes 24 meses.

El Baseline v1 constituye una referencia simple, interpretable y reproducible contra la cual se evaluarán posteriormente modelos de mayor complejidad.

---

## 2. Unidad de análisis

La unidad utilizada es `empresa-año`.

Cada observación representa la situación financiera de una empresa en un período anual determinado.

La variable objetivo es `TARGET_24M`.

Su definición es:

- `1`: la empresa se registra por primera vez como emisor dentro de los siguientes 24 meses.
- `0`: la empresa no se registra como nuevo emisor dentro de ese horizonte.

Las empresas que ya habían sido emisoras a la fecha de corte correspondiente fueron excluidas del universo elegible.

---

## 3. Dataset utilizado

Archivo de entrada:

`data/processed/mvp_features_2015_2023.csv.gz`

El dataset contiene:

| Indicador | Resultado |
|---|---:|
| Observaciones empresa-año | 884.072 |
| Empresas únicas | 166.107 |
| Casos positivos | 440 |
| Casos negativos | 883.632 |
| Prevalencia global aproximada | 0,0498 % |

El problema presenta un desbalance extremo de clases.

---

## 4. Origen de los datos

Las variables predictoras provienen principalmente de los estados financieros publicados por la Superintendencia de Compañías, Valores y Seguros (SCVS).

La variable objetivo se construyó utilizando información histórica del Registro del Mercado de Valores de la SCVS.

La primera fecha de inscripción como emisor fue contrastada con información adicional de fichas registrales.

La información interna de la Bolsa de Valores Quito se considera una fuente complementaria de validación y potencial enriquecimiento, pero no constituye la fuente principal utilizada por este baseline.

---

## 5. División temporal

No se utiliza una partición aleatoria.

El dataset se divide cronológicamente para aproximar un escenario real en el que el modelo aprende con información histórica y posteriormente se aplica sobre períodos futuros.

| Conjunto | Período | Observaciones | Positivos | Prevalencia |
|---|---|---:|---:|---:|
| TRAIN | 2015–2020 | 514.527 | 340 | 0,0661 % |
| VALIDATION | 2021 | 109.101 | 42 | 0,0385 % |
| TEST | 2022–2023 | 260.444 | 58 | 0,0223 % |

Todos los parámetros de preprocesamiento se ajustan exclusivamente utilizando TRAIN.

---

## 6. Variables utilizadas

### 6.1 Variables numéricas

Se utilizan 16 variables numéricas:

- `LOG_ACTIVO_TOTAL`
- `LOG_ACTIVO_CORRIENTE`
- `LOG_EFECTIVO`
- `LOG_PASIVO_TOTAL`
- `LOG_PASIVO_CORRIENTE`
- `LOG_PASIVO_NO_CORRIENTE`
- `LOG_PATRIMONIO`
- `LOG_CAPITAL`
- `LOG_UTILIDAD_NETA`
- `LIQUIDEZ_CORRIENTE`
- `ENDEUDAMIENTO`
- `AUTONOMIA_FINANCIERA`
- `ROA`
- `EFECTIVO_ACTIVOS`
- `CAPITAL_ACTIVOS`
- `PASIVO_CORRIENTE_PASIVO`

### 6.2 Variable categórica

Se utiliza:

`SECTOR_CIIU`

Esta variable corresponde a la primera sección de la clasificación CIIU de cada empresa.

---

## 7. Variables excluidas

No se utilizan como predictores:

- `RUC`
- `EXPEDIENTE`
- `NOMBRE`
- `ANIO`
- `SPLIT`
- `PLAN_CONTABLE`
- `TARGET_24M`

Las fechas utilizadas para construir el target tampoco forman parte de las variables predictoras.

`PLAN_CONTABLE` se conserva únicamente para trazabilidad y validaciones de calidad, pero se excluye del modelo para reducir el riesgo de que el algoritmo aprenda cambios administrativos o de estructura de reporte en lugar de características financieras de las empresas.

---

## 8. Transformaciones financieras

Las nueve variables monetarias utilizan una transformación logarítmica con signo:

`sign(x) × log(1 + |x|)`

Esta transformación permite reducir diferencias de escala preservando valores positivos, negativos y cero.

---

## 9. Preprocesamiento

Todo el preprocesamiento se encuentra integrado en un `Pipeline` de scikit-learn.

### 9.1 Variables numéricas

Se aplican:

- `SimpleImputer(strategy="median")`
- `StandardScaler()`

La imputación y el escalamiento se ajustan únicamente utilizando TRAIN.

### 9.2 Variable categórica

Se aplican:

- `SimpleImputer(strategy="most_frequent")`
- `OneHotEncoder(handle_unknown="ignore")`

Esto permite gestionar categorías desconocidas que eventualmente aparezcan en períodos posteriores.

---

## 10. Modelo

Modelo utilizado:

`LogisticRegression`

Configuración del experimento:

| Parámetro | Valor |
|---|---|
| Regularización | L2 |
| `C` | 1.0 |
| `class_weight` | balanced |
| `solver` | lbfgs |
| `max_iter` | 2000 |
| `random_state` | 42 |

El modelo convergió después de 92 iteraciones.

No se realizó optimización de hiperparámetros en esta versión.

---

## 11. Tratamiento del desbalance

La prevalencia global de la clase positiva es aproximadamente 0,0498 %.

Debido a este fuerte desbalance se utiliza:

`class_weight="balanced"`

El objetivo es evitar que el modelo favorezca casi exclusivamente a la clase negativa.

Como consecuencia, los valores producidos por `predict_proba()` no deben interpretarse todavía como probabilidades reales calibradas.

Por esta razón, los scores obtenidos en esta versión no constituyen todavía el Índice de Afinidad Bursátil definitivo.

---

## 12. Métricas utilizadas

Debido al desbalance extremo, Accuracy no se utiliza como métrica principal.

Se evalúan:

- PR-AUC
- ROC-AUC
- Precision
- Recall
- F1

Para el objetivo de priorización comercial se incorporan además:

- Precision@K
- Recall@K
- Lift@K

Los valores inicialmente evaluados son:

- K = 50
- K = 100
- K = 200

---

## 13. Umbral inicial de clasificación

Para el diagnóstico inicial de clasificación se utiliza:

`threshold = 0.50`

Este valor se utiliza únicamente como referencia técnica inicial.

No se considera un umbral operativo para la BVQ.

---

## 14. Resultados generales

### TRAIN

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0,099413 |
| ROC-AUC | 0,946436 |
| Precision | 0,004494 |
| Recall | 0,894118 |
| F1 | 0,008942 |

Matriz de confusión:

| Resultado | Cantidad |
|---|---:|
| TN | 446.838 |
| FP | 67.349 |
| FN | 36 |
| TP | 304 |

---

### VALIDATION

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0,031095 |
| ROC-AUC | 0,940593 |
| Precision | 0,002566 |
| Recall | 0,880952 |
| F1 | 0,005118 |

Matriz de confusión:

| Resultado | Cantidad |
|---|---:|
| TN | 94.678 |
| FP | 14.381 |
| FN | 5 |
| TP | 37 |

---

### TEST

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0,007291 |
| ROC-AUC | 0,927740 |
| Precision | 0,000627 |
| Recall | 0,931034 |
| F1 | 0,001254 |

Matriz de confusión:

| Resultado | Cantidad |
|---|---:|
| TN | 174.354 |
| FP | 86.032 |
| FN | 4 |
| TP | 54 |

---

## 15. Interpretación de las métricas generales

El ROC-AUC permanece por encima de 0,92 en TRAIN, VALIDATION y TEST, lo que indica que el modelo mantiene capacidad de discriminación global.

Sin embargo, debido al desbalance extremo, ROC-AUC por sí sola no resulta suficiente para evaluar la utilidad del modelo.

PR-AUC disminuye temporalmente:

| Conjunto | PR-AUC |
|---|---:|
| TRAIN | 0,099413 |
| VALIDATION | 0,031095 |
| TEST | 0,007291 |

Esta reducción constituye una señal de degradación temporal y deberá investigarse en siguientes iteraciones.

---

## 16. Limitación del threshold 0,50

En VALIDATION, el modelo identifica 37 de los 42 futuros emisores, pero produce 14.381 falsos positivos.

En TEST identifica 54 de los 58 futuros emisores, pero produce 86.032 falsos positivos.

Por esta razón, el threshold 0,50 no resulta adecuado como regla operativa de prospección.

El proyecto debe orientarse principalmente hacia un problema de ranking y priorización.

---

## 17. Métricas de ranking

### TRAIN

| K | Positivos Top-K | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 24 | 0,4800 | 0,0706 | 726,39 |
| 100 | 42 | 0,4200 | 0,1235 | 635,59 |
| 200 | 59 | 0,2950 | 0,1735 | 446,43 |

### VALIDATION

| K | Positivos Top-K | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 5 | 0,1000 | 0,1190 | 259,76 |
| 100 | 5 | 0,0500 | 0,1190 | 129,88 |
| 200 | 5 | 0,0250 | 0,1190 | 64,94 |

### TEST

| K | Positivos Top-K | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 1 | 0,0200 | 0,0172 | 89,81 |
| 100 | 2 | 0,0200 | 0,0345 | 89,81 |
| 200 | 3 | 0,0150 | 0,0517 | 67,36 |

---

## 18. Interpretación del ranking

En VALIDATION, dentro de las primeras 50 empresas priorizadas aparecen 5 futuros emisores.

Esto representa:

- Precision@50 = 10 %
- Recall@50 = 11,90 %
- Lift@50 = 259,76

El Lift@50 indica que la concentración de futuros emisores dentro de las primeras posiciones es aproximadamente 260 veces superior a la prevalencia general de VALIDATION.

Esto demuestra que existe señal predictiva útil.

Sin embargo, el Recall@50 continúa siendo reducido, por lo que la mayoría de los futuros emisores todavía se encuentra fuera de las primeras posiciones.

---

## 19. Degradación temporal

Se observa una reducción de desempeño desde TRAIN hacia TEST.

Por ejemplo:

| Métrica | TRAIN | VALIDATION | TEST |
|---|---:|---:|---:|
| PR-AUC | 0,099413 | 0,031095 | 0,007291 |
| Precision@50 | 48 % | 10 % | 2 % |

Entre las hipótesis que deberán investigarse se encuentran:

- cambios en la composición de las empresas;
- cambios en la prevalencia de nuevos emisores;
- cambios sectoriales;
- variables predictoras insuficientes;
- ausencia de variables temporales;
- relaciones no lineales;
- cambios en las condiciones económicas o de acceso al mercado.

Estas posibilidades se consideran hipótesis y no conclusiones demostradas.

---

## 20. Coeficientes de mayor magnitud

Entre los coeficientes de mayor magnitud absoluta se encontraron:

| Variable | Coeficiente |
|---|---:|
| `SECTOR_CIIU_Q` | -6,336224 |
| `SECTOR_CIIU_D` | -4,437906 |
| `SECTOR_CIIU_E` | 3,611968 |
| `SECTOR_CIIU_S` | -3,576214 |
| `SECTOR_CIIU_R` | -2,609615 |
| `SECTOR_CIIU_C` | 2,353863 |
| `ROA` | -1,814500 |
| `SECTOR_CIIU_G` | 1,732244 |
| `SECTOR_CIIU_I` | 1,629966 |
| `SECTOR_CIIU_H` | -1,298718 |

Estos coeficientes representan asociaciones estadísticas dentro del modelo y no deben interpretarse como relaciones causales.

Debido al reducido número de positivos y a la distribución desigual de eventos entre sectores, algunos coeficientes sectoriales pueden presentar inestabilidad.

---

## 21. Uso del conjunto TEST

El conjunto TEST 2022–2023 fue utilizado para la evaluación final del Baseline v1 después de fijar la configuración del modelo.

Los análisis gráficos y de errores realizados posteriormente reproducen resultados del mismo Baseline v1 ya fijado y no fueron utilizados para modificar retrospectivamente sus parámetros.

Los experimentos posteriores v2 y v3 se compararon utilizando TRAIN y VALIDATION, sin utilizar TEST para seleccionar esas alternativas.

---

## 22. Fortalezas del Baseline v1

Los resultados permiten identificar las siguientes fortalezas:

- existe señal predictiva en las variables financieras;
- el ranking supera ampliamente una selección aleatoria;
- se utiliza una división temporal;
- el modelo es interpretable;
- el pipeline es reproducible;
- el preprocesamiento se ajusta exclusivamente con TRAIN;
- existe una referencia cuantitativa para comparar modelos futuros;
- las métricas de ranking se relacionan directamente con el problema de prospección de la BVQ.

---

## 23. Limitaciones

El Baseline v1 presenta las siguientes limitaciones:

1. Desbalance extremo de clases.
2. Solamente 340 positivos disponibles en TRAIN.
3. Descenso del desempeño en períodos posteriores.
4. Bajo Recall@K en TEST.
5. Threshold 0,50 no adecuado para uso operativo.
6. Scores de `predict_proba()` no calibrados.
7. Posible inestabilidad de variables sectoriales.
8. Uso principalmente de variables financieras estáticas.
9. Ausencia de variables de crecimiento y tendencia financiera.
10. Modelo basado en relaciones lineales.
11. Ausencia todavía de comparación con modelos no lineales.
12. Necesidad de controlar con mayor precisión la disponibilidad temporal efectiva de los estados financieros.

---

## 24. Próximos experimentos

Las siguientes líneas de trabajo incluyen:

1. Analizar estabilidad de `SECTOR_CIIU`.
2. Comparar el modelo con y sin información sectorial.
3. Evaluar diferentes niveles de regularización.
4. Incorporar variables financieras interanuales.
5. Construir variables de tendencia.
6. Evaluar Random Forest.
7. Evaluar Gradient Boosting y CatBoost.
8. Evaluar posteriormente una red neuronal MLP.
9. Analizar nuevas estrategias para el desbalance.
10. Comparar modelos mediante métricas de ranking.
11. Evaluar calibración de probabilidades.
12. Definir posteriormente el Índice de Afinidad Bursátil.
13. Incorporar mecanismos de interpretabilidad como SHAP.

---

## 25. Archivos reproducibles del experimento

Script principal:

`src/models/train_logistic_baseline.py`

Métricas:

`reports/results/baseline_logistic_metrics.csv`

Ranking:

`reports/results/baseline_logistic_ranking_metrics.csv`

Coeficientes:

`reports/results/baseline_logistic_coefficients.csv`

Metadatos:

`reports/results/baseline_logistic_metadata.json`

Modelo serializado generado localmente:

`models/logistic_baseline.joblib`

El archivo `.joblib` no se almacena en Git porque puede reconstruirse a partir del código, parámetros, datos y entorno correspondiente.

---

## 26. Entorno

El experimento fue ejecutado con:

| Componente | Versión |
|---|---|
| Python | 3.13.7 |
| scikit-learn | 1.9.1 |
| pandas | 3.0.5 |
| NumPy | 2.5.3 |
| SciPy | 1.18.1 |
| joblib | 1.6.0 |

El entorno completo se encuentra registrado en:

- `requirements.txt`
- `requirements-lock.txt`

---

## 27. Estado del experimento

| Elemento | Estado |
|---|---|
| Experimento | Baseline v1 |
| Modelo | Logistic Regression |
| Tuning | No |
| Calibración | No |
| Interpretabilidad | Coeficientes iniciales |
| TEST utilizado para ajustar el modelo | No |
| Estado | Completado |
| Modelo de referencia | Sí |

El Baseline v1 se conserva como referencia permanente para evaluar objetivamente las siguientes iteraciones del proyecto.