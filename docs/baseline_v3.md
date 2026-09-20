# Baseline v3 — Evaluación de regularización en regresión logística

## 1. Objetivo

El objetivo del experimento v3 es evaluar si una modificación en la intensidad de regularización mejora el desempeño temporal del modelo de referencia.

Se mantiene la misma estructura del Baseline v1:

- mismas variables financieras;
- uso de `SECTOR_CIIU`;
- mismo split temporal;
- mismo esquema de preprocesamiento;
- misma ponderación de clases;
- mismo algoritmo de regresión logística.

La única modificación evaluada es el parámetro `C`.

---

## 2. Pregunta experimental

La pregunta principal es:

**¿Modificar la intensidad de regularización de la regresión logística mejora el desempeño en VALIDATION sin deteriorar las métricas de ranking?**

Para responder esta pregunta se evalúan cinco valores:

- `C = 0.001`
- `C = 0.01`
- `C = 0.1`
- `C = 1.0`
- `C = 10.0`

---

## 3. Interpretación del parámetro C

En una regresión logística regularizada, el parámetro `C` controla de manera inversa la intensidad de regularización.

En términos generales:

- valores pequeños de `C` implican mayor regularización;
- valores grandes de `C` implican menor regularización.

El objetivo del experimento es determinar si una mayor o menor penalización mejora la capacidad de generalización temporal del modelo.

---

## 4. Dataset utilizado

Se utiliza el mismo dataset del Baseline v1.

Archivo:

`data/processed/mvp_features_2015_2023.csv.gz`

La unidad de análisis es:

`empresa-año`

La variable objetivo es:

`TARGET_24M`

donde:

- `1`: la empresa se registra por primera vez como emisor dentro de los siguientes 24 meses.
- `0`: la empresa no se registra como nuevo emisor dentro de ese horizonte.

---

## 5. División temporal

Se mantiene la misma división temporal utilizada por el Baseline v1:

| Conjunto | Período | Observaciones | Positivos |
|---|---|---:|---:|
| TRAIN | 2015–2020 | 514.527 | 340 |
| VALIDATION | 2021 | 109.101 | 42 |

El conjunto TEST 2022–2023 no fue utilizado en este experimento.

---

## 6. Variables utilizadas

Se mantienen las mismas variables del Baseline v1.

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

### Variable categórica

- `SECTOR_CIIU`

---

## 7. Preprocesamiento

Se mantiene el mismo esquema de preprocesamiento utilizado en el Baseline v1.

### Variables numéricas

- imputación mediante mediana;
- escalamiento mediante `StandardScaler`.

### Variable categórica

- imputación mediante la categoría más frecuente;
- codificación mediante `OneHotEncoder(handle_unknown="ignore")`.

Todos los parámetros de preprocesamiento se ajustan exclusivamente con TRAIN.

---

## 8. Modelo

El algoritmo utilizado es:

`LogisticRegression`

La configuración general registrada es:

| Parámetro | Valor |
|---|---|
| Modelo | LogisticRegression |
| Regularización | L2 |
| `class_weight` | balanced |
| `random_state` | 42 |
| `SECTOR_CIIU` | Incluido |
| TRAIN | 2015–2020 |
| VALIDATION | 2021 |
| TEST utilizado | No |

---

## 9. Valores de C evaluados

El experimento compara:

| Variante | C |
|---|---:|
| v3-C1 | 0.001 |
| v3-C2 | 0.01 |
| v3-C3 | 0.1 |
| Baseline de referencia | 1.0 |
| v3-C5 | 10.0 |

`C = 1.0` corresponde a la configuración del Baseline v1.

---

## 10. Criterio de selección

El criterio primario registrado para el experimento es:

`VALIDATION_PR_AUC`

Los criterios secundarios son:

- Precision@50
- Recall@50
- Precision@100
- Recall@100
- Precision@200
- Recall@200

Esta decisión responde al fuerte desbalance de clases y al objetivo de priorización comercial del proyecto.

---

## 11. Resultados generales

| C | TRAIN PR-AUC | VALIDATION PR-AUC | TRAIN ROC-AUC | VALIDATION ROC-AUC | Iteraciones |
|---:|---:|---:|---:|---:|---:|
| 0.001 | 0,094276 | 0,024217 | 0,943988 | 0,955848 | 37 |
| 0.01 | 0,096499 | 0,027559 | 0,945856 | 0,951061 | 56 |
| 0.1 | 0,098494 | 0,030555 | 0,946350 | 0,946416 | 74 |
| 1.0 | 0,099413 | 0,031095 | 0,946436 | 0,940593 | 92 |
| 10.0 | 0,099542 | 0,031135 | 0,946476 | 0,934021 | 122 |

---

## 12. Comportamiento de PR-AUC

En VALIDATION se observa:

| C | VALIDATION PR-AUC |
|---:|---:|
| 0.001 | 0,024217 |
| 0.01 | 0,027559 |
| 0.1 | 0,030555 |
| 1.0 | 0,031095 |
| 10.0 | 0,031135 |

El valor más alto corresponde a:

`C = 10.0`

con:

`PR-AUC = 0,031135`

Sin embargo, la configuración de referencia:

`C = 1.0`

obtiene:

`PR-AUC = 0,031095`

La diferencia absoluta es aproximadamente:

`0,000040`

Por tanto, la mejora observada en PR-AUC es muy pequeña.

---

## 13. Comportamiento de ROC-AUC

En VALIDATION se observa:

| C | VALIDATION ROC-AUC |
|---:|---:|
| 0.001 | 0,955848 |
| 0.01 | 0,951061 |
| 0.1 | 0,946416 |
| 1.0 | 0,940593 |
| 10.0 | 0,934021 |

A medida que aumenta `C`, el ROC-AUC de VALIDATION disminuye.

El mayor ROC-AUC corresponde a:

`C = 0.001`

con:

`ROC-AUC = 0,955848`

Sin embargo, esta variante presenta el menor PR-AUC de las alternativas evaluadas.

Debido al fuerte desbalance, ROC-AUC no se utiliza de forma aislada como criterio principal de selección.

---

## 14. Resultados Top 50

| C | Positivos Top 50 | Precision@50 | Recall@50 | Lift@50 |
|---:|---:|---:|---:|---:|
| 0.001 | 4 | 0,0800 | 0,0952 | 207,81 |
| 0.01 | 4 | 0,0800 | 0,0952 | 207,81 |
| 0.1 | 5 | 0,1000 | 0,1190 | 259,76 |
| 1.0 | 5 | 0,1000 | 0,1190 | 259,76 |
| 10.0 | 5 | 0,1000 | 0,1190 | 259,76 |

Las configuraciones:

- `C = 0.1`
- `C = 1.0`
- `C = 10.0`

obtienen exactamente el mismo desempeño en Top 50.

---

## 15. Resultados Top 100

| C | Positivos Top 100 | Precision@100 | Recall@100 | Lift@100 |
|---:|---:|---:|---:|---:|
| 0.001 | 5 | 0,0500 | 0,1190 | 129,88 |
| 0.01 | 5 | 0,0500 | 0,1190 | 129,88 |
| 0.1 | 5 | 0,0500 | 0,1190 | 129,88 |
| 1.0 | 5 | 0,0500 | 0,1190 | 129,88 |
| 10.0 | 5 | 0,0500 | 0,1190 | 129,88 |

No existe diferencia entre las configuraciones evaluadas para Top 100.

---

## 16. Resultados Top 200

| C | Positivos Top 200 | Precision@200 | Recall@200 | Lift@200 |
|---:|---:|---:|---:|---:|
| 0.001 | 5 | 0,0250 | 0,1190 | 64,94 |
| 0.01 | 5 | 0,0250 | 0,1190 | 64,94 |
| 0.1 | 5 | 0,0250 | 0,1190 | 64,94 |
| 1.0 | 5 | 0,0250 | 0,1190 | 64,94 |
| 10.0 | 5 | 0,0250 | 0,1190 | 64,94 |

Tampoco existe diferencia entre las configuraciones evaluadas para Top 200.

---

## 17. Comparación entre C = 1 y C = 10

Las dos configuraciones con mayor PR-AUC en VALIDATION son:

| Métrica | C = 1 | C = 10 |
|---|---:|---:|
| VALIDATION PR-AUC | 0,031095 | 0,031135 |
| VALIDATION ROC-AUC | 0,940593 | 0,934021 |
| Precision@50 | 0,1000 | 0,1000 |
| Recall@50 | 0,1190 | 0,1190 |
| Precision@100 | 0,0500 | 0,0500 |
| Recall@100 | 0,1190 | 0,1190 |
| Precision@200 | 0,0250 | 0,0250 |
| Recall@200 | 0,1190 | 0,1190 |

`C = 10` obtiene un PR-AUC ligeramente superior.

Sin embargo:

- la diferencia de PR-AUC es mínima;
- ROC-AUC disminuye;
- Top 50 no mejora;
- Top 100 no mejora;
- Top 200 no mejora.

---

## 18. Interpretación

El experimento muestra que modificar la intensidad de regularización produce cambios en las métricas generales, pero no genera una mejora material en la capacidad de priorización.

Las configuraciones con mayor regularización:

- `C = 0.001`
- `C = 0.01`

presentan un PR-AUC inferior y también un resultado inferior en Top 50.

A partir de:

`C = 0.1`

las métricas Top 50 permanecen estables.

En Top 100 y Top 200 todas las configuraciones evaluadas obtienen exactamente los mismos resultados.

---

## 19. Resultado del experimento

El criterio primario era mejorar:

`VALIDATION_PR_AUC`

El mayor resultado se obtiene con:

`C = 10`

con:

`PR-AUC = 0,031135`

frente a:

`PR-AUC = 0,031095`

para:

`C = 1`

La diferencia absoluta es aproximadamente 0,000040.

Esta variación no viene acompañada de mejoras en las métricas de ranking.

Por esta razón no se considera una mejora material respecto del Baseline v1.

---

## 20. Decisión metodológica

Se mantiene:

`C = 1.0`

como configuración de referencia.

Esta decisión se fundamenta en que:

- su PR-AUC es prácticamente equivalente al mejor valor encontrado;
- mantiene mejor ROC-AUC que `C = 10`;
- presenta exactamente los mismos resultados Top 50;
- presenta exactamente los mismos resultados Top 100;
- presenta exactamente los mismos resultados Top 200;
- evita introducir un cambio de hiperparámetro sin una mejora relevante.

Por tanto, el Baseline v1 permanece como modelo de referencia.

---

## 21. Uso del conjunto TEST

El conjunto:

`TEST 2022–2023`

no fue utilizado durante este experimento.

El tuning de regularización se realizó exclusivamente con:

- TRAIN 2015–2020;
- VALIDATION 2021.

No se evaluó cada valor de `C` sobre TEST.

Esto evita utilizar el conjunto TEST para seleccionar hiperparámetros.

---

## 22. Fortalezas del experimento

El experimento presenta las siguientes fortalezas:

- modifica un único hiperparámetro;
- mantiene constantes las variables;
- mantiene `SECTOR_CIIU`;
- mantiene el mismo split temporal;
- mantiene el mismo algoritmo;
- mantiene el tratamiento de clases;
- utiliza un criterio primario definido previamente;
- incorpora métricas de ranking;
- no utiliza TEST para seleccionar la configuración;
- permite comparar directamente el efecto de la regularización.

---

## 23. Limitaciones

Las principales limitaciones son:

1. VALIDATION contiene únicamente 42 positivos.
2. Se utiliza un único período de validación.
3. Los valores evaluados de `C` pertenecen a una grilla discreta.
4. El modelo continúa siendo lineal.
5. No se incorporan todavía variables temporales.
6. El fuerte desbalance continúa presente.
7. El tuning de regularización no resuelve la degradación temporal observada.
8. Los scores del modelo todavía no están calibrados.
9. No se evaluó TEST durante esta fase, por diseño metodológico.

---

## 24. Archivos del experimento

Resultados:

`reports/results/logistic_regularization_v3_validation.csv`

Metadatos:

`reports/results/logistic_regularization_v3_metadata.json`

El script correspondiente se encuentra dentro de la estructura de modelado del proyecto.

---

## 25. Configuración registrada

Los metadatos del experimento registran:

| Elemento | Valor |
|---|---|
| Experimento | v3_regularizacion_logistica |
| Modelo | LogisticRegression |
| Objetivo | Evaluar mayor o menor regularización manteniendo SECTOR_CIIU |
| C evaluados | 0.001, 0.01, 0.1, 1.0, 10.0 |
| Criterio primario | VALIDATION_PR_AUC |
| `random_state` | 42 |
| `class_weight` | balanced |
| Regularización | L2 |
| `SECTOR_CIIU` | Sí |
| TRAIN | 2015–2020 |
| VALIDATION | 2021 |
| TEST utilizado | No |

---

## 26. Criterios secundarios registrados

Los criterios secundarios definidos son:

- Precision@50
- Recall@50
- Precision@100
- Recall@100
- Precision@200
- Recall@200

Los resultados muestran que ninguna configuración supera al Baseline v1 en estas métricas.

---

## 27. Entorno registrado

| Componente | Versión |
|---|---|
| Python | 3.13.7 |
| pandas | 3.0.5 |
| NumPy | 2.5.3 |
| scikit-learn | 1.9.1 |

El entorno completo del proyecto se conserva en:

- `requirements.txt`
- `requirements-lock.txt`

---

## 28. Conclusión

El experimento v3 evaluó cinco niveles de regularización manteniendo el resto del pipeline sin cambios.

`C = 10` alcanzó el mayor PR-AUC en VALIDATION con 0,031135, frente a 0,031095 obtenido por `C = 1`.

La diferencia es mínima y no produce mejoras en Precision@K, Recall@K o Lift@K.

Además, `C = 10` obtiene un ROC-AUC inferior al de `C = 1`.

Por tanto, no existe evidencia en este experimento de una mejora material que justifique reemplazar la configuración del Baseline v1.

Se mantiene `C = 1.0` como configuración de referencia para las siguientes etapas del proyecto.