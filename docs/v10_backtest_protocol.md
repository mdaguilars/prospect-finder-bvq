# Protocolo de backtesting temporal v10

**Nota de vigencia:** Este documento registra el protocolo de backtesting temporal definido durante la etapa inicial de modelado v10, cuando el proyecto utilizaba el dataset `v10_features_core_2012_2023.csv.gz` y evaluaba inicialmente configuraciones de Regresión Logística. Posteriormente el mismo esquema temporal de cuatro folds fue utilizado para comparar configuraciones adicionales y seleccionar el candidato final `v10_hgb_financial_c3`, basado en `HistGradientBoostingClassifier` y un Feature Set financiero de 25 variables. Para los resultados finales deben consultarse `docs/v10_final_candidate_freeze.md`, `docs/v10_final_test_protocol.md`, `docs/v10_final_test_results.md` y el `README.md`.

## 1. Objetivo

Este documento define el procedimiento de backtesting temporal para los modelos de la generación v10 de Prospect Finder BVQ.

El objetivo es evaluar la estabilidad del desempeño a través del tiempo sin modificar el split oficial previamente congelado.

El backtesting se utilizará como complemento de la evaluación principal sobre VALIDATION 2020.

No reemplaza la estructura oficial:

`TRAIN 2012-2018 -> EMBARGO 2019 -> VALIDATION 2020 -> EMBARGO 2021 -> TEST 2022-2023`

TEST permanece cerrado.

---

## 2. Dataset utilizado

Se utilizará exclusivamente:

`data/processed/v10_features_core_2012_2023.csv.gz`

El backtesting se realizará únicamente con observaciones pertenecientes al período oficial de TRAIN:

`2012-2018`

No se utilizarán para este procedimiento:

- EMBARGO_1 2019;
- VALIDATION 2020;
- EMBARGO_2 2021;
- TEST 2022-2023.

---

## 3. Principio temporal

Prospect Finder BVQ utiliza un horizonte objetivo de 24 meses.

Para reducir el riesgo de contaminación temporal entre entrenamiento y evaluación, cada fold dejará un ejercicio completo de embargo entre ambos conjuntos.

Se utilizará una estrategia de ventana expansiva.

Esto significa que cada fold incorpora al entrenamiento toda la información histórica disponible desde 2012 hasta el último ejercicio permitido antes del embargo.

---

## 4. Folds definidos

| Fold | TRAIN | Embargo | Evaluación | Filas evaluación | Positivos evaluación |
|---|---|---|---|---:|---:|
| 1 | 2012-2013 | 2014 | 2015 | 76.468 | 43 |
| 2 | 2012-2014 | 2015 | 2016 | 79.503 | 73 |
| 3 | 2012-2015 | 2016 | 2017 | 83.107 | 89 |
| 4 | 2012-2016 | 2017 | 2018 | 89.818 | 59 |

Tamaño acumulado de TRAIN:

| Fold | Filas TRAIN | Positivos TRAIN |
|---|---:|---:|
| 1 | 89.298 | 104 |
| 2 | 141.826 | 143 |
| 3 | 218.294 | 186 |
| 4 | 297.797 | 259 |

---

## 5. Regla de embargo

El año de embargo de cada fold:

- no se utiliza para ajustar el modelo;
- no se utiliza para calcular métricas;
- no se utiliza para seleccionar parámetros;
- no se incorpora al conjunto de evaluación.

Su función es mantener separación temporal entre el conjunto utilizado para aprender el modelo y el año utilizado para medir desempeño.

---

## 6. Preprocesamiento

En cada fold, todo preprocesamiento aprendido deberá ajustarse exclusivamente con el TRAIN correspondiente.

Esto incluye:

- imputación de valores faltantes;
- cálculo de medianas;
- escalamiento;
- codificación categórica;
- categorías observadas;
- pesos derivados del conjunto de entrenamiento.

No se podrá aprender ningún parámetro utilizando el año de embargo o el año de evaluación.

---

## 7. Modelos y configuraciones

El primer backtesting se realizará sobre Regresión Logística v10.

Se evaluarán las configuraciones ya analizadas durante la fase inicial de desarrollo:

1. `v10_lr`
   - variables numéricas;
   - variables booleanas;
   - `tipo_compania`;
   - `provincia`.

2. `v10_lr_no_provincia`
   - variables numéricas;
   - variables booleanas;
   - `tipo_compania`;
   - excluye `provincia`.

3. `v10_lr_no_categoricas`
   - variables numéricas;
   - variables booleanas;
   - excluye las variables categóricas.

4. `v10_lr_no_tipo_compania`
   - variables numéricas;
   - variables booleanas;
   - `provincia`;
   - excluye `tipo_compania`.

La finalidad del backtesting es analizar la estabilidad de estas configuraciones a través de diferentes períodos.

---

## 8. Configuración de Regresión Logística

Para mantener comparabilidad, se utilizará la misma configuración base:

- `C = 1.0`;
- regularización L2;
- `class_weight = "balanced"`;
- `solver = "lbfgs"`;
- `max_iter = 2000`;
- `random_state = 42`.

No se modificarán hiperparámetros de manera independiente para cada fold.

---

## 9. Métricas

Las métricas principales serán:

- PR-AUC;
- Precision@50;
- Precision@100;
- Precision@200;
- Recall@50;
- Recall@100;
- Recall@200;
- Lift@50;
- Lift@100;
- Lift@200.

ROC-AUC podrá calcularse como métrica complementaria.

Accuracy no será utilizada como criterio principal debido al fuerte desbalance de clases.

---

## 10. Evaluación de estabilidad

Para cada configuración se calcularán, al menos:

- resultado por fold;
- PR-AUC promedio;
- PR-AUC mediano;
- desviación estándar de PR-AUC;
- mínimo y máximo de PR-AUC;
- desempeño Top-K por fold;
- promedio de Lift@K;
- variabilidad entre períodos.

No se considerará suficiente una mejora observada únicamente en un año.

---

## 11. Criterio de interpretación

El backtesting no seleccionará automáticamente una configuración por obtener el valor máximo en una única métrica.

La evaluación deberá considerar conjuntamente:

- PR-AUC;
- capacidad de priorización Top-K;
- estabilidad temporal;
- variabilidad;
- comportamiento frente al desbalance;
- interpretabilidad;
- complejidad;
- riesgo de sobreajuste;
- riesgo de dependencia excesiva de categorías poco representadas.

---

## 12. Variables categóricas

Durante los experimentos iniciales de VALIDATION se observaron coeficientes elevados asociados a algunas categorías de:

- `tipo_compania`;
- `provincia`.

Algunas de estas categorías presentan pocos o ningún caso positivo dentro de TRAIN.

Por esta razón, el backtesting permitirá evaluar si su aporte es estable a través del tiempo o si depende excesivamente de períodos específicos.

Esta observación no implica eliminar automáticamente dichas variables.

---

## 13. Relación con VALIDATION

VALIDATION 2020 continúa siendo el conjunto oficial para comparar modelos durante la fase de desarrollo.

Los folds de backtesting:

- se encuentran completamente dentro de TRAIN 2012-2018;
- permiten analizar estabilidad histórica;
- complementan VALIDATION;
- no sustituyen VALIDATION.

Los resultados del backtesting y de VALIDATION deberán analizarse conjuntamente.

---

## 14. Uso de TEST

El conjunto:

`TEST 2022-2023`

permanece completamente reservado.

Durante este backtesting no se permitirá:

- generar predicciones sobre TEST;
- calcular PR-AUC sobre TEST;
- calcular Top-K sobre TEST;
- revisar errores de TEST;
- utilizar TEST para elegir variables;
- utilizar TEST para elegir hiperparámetros;
- utilizar TEST para seleccionar el modelo.

La evaluación de TEST se realizará únicamente después de cerrar formalmente la selección final del modelo.

---

## 15. Reproducibilidad

Los resultados del backtesting deberán almacenarse bajo:

`reports/results/v10/`

Los archivos deberán permitir reconstruir:

- fold;
- años de TRAIN;
- año de embargo;
- año de evaluación;
- configuración utilizada;
- número de observaciones;
- número de positivos;
- métricas generales;
- métricas Top-K;
- resumen de estabilidad;
- semilla;
- versiones relevantes del entorno.

---

## 16. Regla de modificación

Los folds definidos en este documento deberán mantenerse constantes durante la comparación de configuraciones v10.

Si en el futuro se propone otro esquema temporal, deberá documentarse como un protocolo diferente y no reemplazar retrospectivamente los resultados obtenidos con este procedimiento.

---

## 17. Secuencia de ejecución

La secuencia será:

1. congelar este protocolo;
2. implementar el script de backtesting;
3. ejecutar las cuatro configuraciones de Regresión Logística;
4. comparar estabilidad temporal;
5. contrastar resultados con VALIDATION 2020;
6. documentar las conclusiones;
7. continuar posteriormente con los modelos no lineales v10.

TEST permanecerá cerrado durante toda esta fase.