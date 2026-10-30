# ACTA DE PRUEBAS EN VIVO
## Prospect Finder BVQ – Modelo v10

**Proyecto:** Prospect Finder BVQ
**Modelo:** `v10_hgb_financial_c3`
**Configuración:** `C3_CONSERVATIVE`
**Algoritmo:** HistGradientBoostingClassifier
**Número de variables predictivas:** 25
**Fecha de ejecución de pruebas:** 21 de octubre de 2026
**TRAIN:** 2012–2018
**VALIDATION:** 2020, no utilizado para entrenamiento final
**Embargos temporales:** 2019 y 2021
**TEST congelado:** 2022–2023
**Observaciones TEST:** 260.445
**Positivos TEST:** 54

---

# 1. Objetivo

El presente documento registra las pruebas funcionales y metodológicas ejecutadas sobre el modelo final v10 de Prospect Finder BVQ.

Las pruebas fueron realizadas después del congelamiento del modelo y tienen como finalidad verificar:

- reproducibilidad;
- control de fuga temporal;
- comportamiento frente a datos faltantes y atípicos;
- sensibilidad ante cambios pequeños;
- utilidad del ranking Top-K;
- explicabilidad y comportamiento asociado con el tamaño empresarial.

Las pruebas no modifican el modelo final, sus hiperparámetros, el conjunto de variables ni los resultados oficiales de TEST.

Los resultados adversos o limitaciones identificados durante las pruebas se documentan como evidencia y no se utilizan para reajustar retrospectivamente el modelo v10.

---

# 2. Resumen de resultados

| ID | Prueba | Resultado | Observación principal |
|---|---|---|---|
| P01 | Ranking reproducible | CUMPLE | Dos ejecuciones independientes produjeron exactamente el mismo ranking y métricas. |
| P02 | Fuga temporal | CUMPLE | La información introducida después de la fecha de decisión fue detectada y no ingresó al conjunto predictor. |
| P03 | Datos faltantes y atípicos | CUMPLE | El modelo procesó los casos sin excepción y las perturbaciones fueron detectadas y documentadas. |
| P04 | Robustez a cambios ±5 % | CUMPLE | La perturbación seleccionada no modificó el score ni la posición del caso evaluado. |
| P05 | Utilidad comercial Top-K | CUMPLE CON LIMITACIÓN | Top 20, Top 50 y Top 100 no recuperaron positivos conocidos en TEST. |
| P06 | Explicabilidad y tamaño | CUMPLE CON OBSERVACIÓN | SHAP mostró influencia relevante de variables asociadas con escala empresarial. |

---

# 3. P01 – Ranking reproducible

## Objetivo

Verificar que la ejecución del modelo congelado sobre el mismo conjunto TEST produzca los mismos resultados cuando no cambian los datos, configuración ni parámetros.

## Procedimiento

Se ejecutó en dos ocasiones independientes la evaluación final del modelo:

`v10_hgb_financial_c3`

utilizando:

- TRAIN 2012–2018;
- TEST 2022–2023;
- configuración `C3_CONSERVATIVE`;
- 25 variables predictivas.

Los resultados de ambas ejecuciones fueron almacenados de forma independiente.

## Resultado

- Filas ejecución 1: 260.445
- Filas ejecución 2: 260.445
- Ranking idéntico: Sí
- Métricas idénticas: Sí
- Métricas Top-K idénticas: Sí

La comparación exacta mediante DataFrame obtuvo:

`Ranking idéntico: True`

`Métricas idénticas: True`

`Métricas Top-K idénticas: True`

## Conclusión

**CUMPLE**

El modelo y el proceso de evaluación demostraron reproducibilidad bajo las mismas condiciones de entrada y configuración.

## Evidencias

Directorio:

`reports/live_tests/P01/`

Archivos principales:

- `ranking_run1.csv.gz`
- `ranking_run2.csv.gz`
- `metrics_run1.csv`
- `metrics_run2.csv`
- `ranking_metrics_run1.csv`
- `ranking_metrics_run2.csv`
- `ranking_top50.csv`

---

# 4. P02 – Fuga temporal

## Objetivo

Verificar que información conocida después de la fecha de decisión no sea incorporada al conjunto predictor utilizado por el modelo.

## Caso de prueba

Se seleccionó una observación perteneciente a TEST:

- Año financiero: 2023
- Empresa: CASO A
- Expediente: [ANONIMIZADO]
- Split: TEST
- Fecha de decisión: 2024-05-01

Se introdujo artificialmente:

`DATO_FUTURO_PRUEBA = 999.999.999`

con fecha:

`2024-07-30`

correspondiente a 90 días después de la fecha de decisión.

## Resultado

- Dato posterior a la fecha de decisión: Sí
- Violación temporal detectada: Sí
- Features congeladas del modelo: 25
- Variable futura pertenece al modelo: No
- Fecha futura pertenece al modelo: No
- Entrada predictora original y alterada: Idénticas

La observación alterada pasó de 32 a 34 columnas debido a los campos artificiales utilizados en la prueba, pero la matriz finalmente utilizada por el modelo mantuvo exclusivamente las 25 variables congeladas.

## Conclusión

**CUMPLE**

En el ensayo realizado, la información futura fue identificada explícitamente y no ingresó a la matriz predictora del modelo.

Esta prueba no implica que cualquier nueva fuente de datos futura quede automáticamente protegida sin controles de ingeniería; confirma el comportamiento del feature set congelado y del control temporal utilizado en el ensayo.

## Evidencias

Directorio:

`reports/live_tests/P02/`

Archivos:

- `p02_temporal_leakage_result.csv`
- `p02_model_features.csv`
- `p02_input_original.csv`
- `p02_input_altered.csv`
- `p02_metadata.json`

---

# 5. P03 – Datos faltantes y atípicos

## Objetivo

Evaluar el comportamiento del modelo frente a:

1. información financiera faltante;
2. una razón financiera extremadamente alejada de su distribución de referencia.

## Caso base

Empresa:

CASO A

Año:

2023

Score original:

`0.348435641`

## Caso A – Datos faltantes

Se convirtieron a faltantes nueve variables financieras:

- activos;
- patrimonio;
- ingresos por ventas;
- número de empleados;
- patrimonio / activos;
- ROA;
- margen neto;
- rotación de activos;
- ROE.

Resultado:

- Faltantes antes: 0
- Faltantes después: 9
- Perturbación detectada: Sí
- Predicción realizada sin excepción: Sí
- Score original: 0.348435641
- Score alterado: 0.301758721
- Cambio absoluto: -0.046676920
- Cambio relativo: -13,40 %

El modelo pudo producir un score aun con información incompleta.

La prueba documenta que este tipo de resultado debe interpretarse con cautela por la reducción de información disponible.

## Caso B – Valor atípico

Variable modificada:

`fin_ratio_patrimonio_activos`

Valor original:

`0.9568938804`

Distribución TRAIN:

- P01: -3.360810
- P50: 0.501652
- P99: 1.000000

Valor de ensayo:

`10.000000`

Resultado:

- Valor fuera del rango de referencia: Sí
- Predicción realizada sin excepción: Sí
- Score original: 0.348435641
- Score alterado: 0.352409192
- Cambio absoluto: +0.003973551
- Cambio relativo: +1,14 %

## Conclusión

**CUMPLE**

El modelo procesó ambos casos sin generar errores no controlados y las condiciones alteradas fueron registradas explícitamente.

La advertencia de calidad utilizada durante esta prueba forma parte del procedimiento de ensayo. No debe interpretarse como evidencia de que toda la interfaz productiva bloquee automáticamente este tipo de observaciones si dicho control no ha sido implementado en esa capa.

## Evidencias

Directorio:

`reports/live_tests/P03/`

Archivos:

- `p03_results.csv`
- `p03_input_original.csv`
- `p03_input_missing.csv`
- `p03_input_extreme.csv`
- `p03_extreme_reference.json`
- `p03_metadata.json`

---

# 6. P04 – Robustez a pequeños cambios

## Objetivo

Evaluar la sensibilidad local del modelo ante una modificación de ±5 % en una variable financiera no determinante.

## Caso de ensayo

Empresa:

CASO B

Año:

2023

Variable:

`fin_rotacion_activos`

Valor original:

`6.556447840`

Score original:

`0.122732576`

Ranking original:

`73.043 de 260.445`

## Perturbación -5 %

Valor modificado:

`6.228625448`

Score:

`0.122732576`

Cambio del score:

`0,0000 %`

Ranking:

`73.043`

Cambio de posiciones:

`0`

## Perturbación +5 %

Valor modificado:

`6.884270232`

Score:

`0.122732576`

Cambio del score:

`0,0000 %`

Ranking:

`73.043`

Cambio de posiciones:

`0`

## Conclusión

**CUMPLE**

Para el caso evaluado, una modificación de ±5 % en la rotación de activos no modificó el score ni la posición relativa de la empresa.

Este resultado constituye evidencia de estabilidad local para este caso concreto y no implica que todas las variables o todas las observaciones presenten necesariamente el mismo comportamiento.

## Evidencias

Directorio:

`reports/live_tests/P04/`

Archivos:

- `p04_results.csv`
- `p04_inputs.csv`
- `p04_case.csv`
- `p04_metadata.json`

---

# 7. P05 – Utilidad comercial Top-K

## Objetivo

Evaluar cuántos positivos conocidos del conjunto TEST son recuperados dentro de los primeros lugares del ranking.

## Universo

- Observaciones TEST: 260.445
- Positivos: 54
- Prevalencia: 0.000207337

## Resultados

### Top 20

- Positivos: 0
- Precision@20: 0
- Recall@20: 0
- Lift@20: 0
- Universo revisado: 0,007679 %

### Top 50

- Positivos: 0
- Precision@50: 0
- Recall@50: 0
- Lift@50: 0
- Universo revisado: 0,019198 %

### Top 100

- Positivos: 0
- Precision@100: 0
- Recall@100: 0
- Lift@100: 0
- Universo revisado: 0,038396 %

## Primer positivo recuperado

El primer positivo conocido aparece en:

`Ranking 165`

Empresa:

`ECUAHIELO S.A.`

Score:

`0.967644`

Los siguientes positivos aparecen en posiciones posteriores, entre ellas:

- 269
- 309
- 342
- 364
- 463
- 533
- 717
- 751
- 817

## Interpretación

La prueba fue ejecutada correctamente, pero evidencia una limitación relevante de recuperación temprana.

En TEST 2022–2023, revisar únicamente las primeras 100 empresas no habría permitido recuperar ningún positivo conocido.

Por este motivo, no corresponde concluir alta utilidad comercial exclusivamente a partir del ROC-AUC.

El ranking debe interpretarse como herramienta de priorización y apoyo al especialista, no como una regla automática de selección.

## Conclusión

**CUMPLE CON LIMITACIÓN**

La metodología y los cálculos Top-K son correctos, pero la utilidad observada en los primeros 100 puestos de TEST es limitada.

Este hallazgo no será utilizado para reajustar v10. Una eventual optimización posterior deberá realizarse dentro de una nueva versión del modelo y con un nuevo protocolo de entrenamiento y evaluación.

## Evidencias

Directorio:

`reports/live_tests/P05/`

Archivos:

- `p05_topk_metrics.csv`
- `p05_top100.csv`
- `p05_positive_positions.csv`
- `p05_top200_context.csv`
- `p05_metadata.json`

---

# 8. P06 – Explicabilidad y análisis por tamaño empresarial

## Objetivo

Comparar explicaciones SHAP de empresas de distinto tamaño y analizar si las variables asociadas con escala tienen un peso relevante en las predicciones.

Para mejorar la comparabilidad se seleccionaron:

- empresas de TEST 2023;
- observaciones completas;
- mismo tipo societario;
- una empresa aproximadamente en P90 de activos;
- una empresa aproximadamente en P10 de activos.

Tipo de compañía controlado:

`ANÓNIMA`

Referencia del grupo:

- P10 activos: USD 7.772,46
- P50 activos: USD 202.537,99
- P90 activos: USD 3.684.995,55

## Empresa grande

Empresa:

`VENPARGLOBAL S.A.`

Activos:

`USD 3.684.973,43`

Score:

`0.894149556`

Score reconstruido por SHAP:

`0.894149556`

Error de reconstrucción:

`0.0000000000`

Principales contribuciones SHAP:

- Activos: +0.390341
- Ingresos por ventas: +0.131237
- Patrimonio: +0.046352
- ROA: +0.031764
- Patrimonio del año anterior: +0.023358

Peso absoluto de variables de escala:

`86,41 %`

## Empresa pequeña

Empresa:

`COMPAÑIA DE TRANSPORTES TRANSCAMPO S.A.`

Activos:

`USD 7.772,85`

Score:

`0.081387026`

Score reconstruido por SHAP:

`0.081387026`

Error de reconstrucción:

`0.0000000000`

Principales contribuciones SHAP:

- Activos: -0.059736
- Ingresos por ventas: -0.024907
- Crecimiento de patrimonio: +0.017774
- Crecimiento de ventas: -0.012677
- Margen neto: +0.011260

Peso absoluto de variables de escala:

`67,29 %`

## Interpretación

Las explicaciones muestran una influencia considerable de características relacionadas con escala empresarial, particularmente activos y ventas.

En el caso grande estas variables contribuyen positivamente al score, mientras que en la empresa pequeña tienen contribuciones negativas.

Este resultado:

- no demuestra causalidad;
- no constituye por sí solo evidencia de discriminación;
- no permite concluir que el tamaño sea la única razón del score;
- sí justifica monitorear el comportamiento del modelo por segmentos de tamaño.

SHAP describe cómo las variables contribuyeron a predicciones concretas del modelo.

La interpretación correcta es que el modelo ha aprendido asociaciones presentes en los datos históricos, no relaciones causales.

## Conclusión

**CUMPLE CON OBSERVACIÓN**

La explicación SHAP reconstruyó exactamente los scores de ambos casos.

Se identificó una influencia relevante de variables asociadas con escala, que deberá ser monitoreada mediante análisis segmentado en futuras evaluaciones del modelo.

## Evidencias

Directorio:

`reports/live_tests/P06/`

Archivos:

- `p06_cases.csv`
- `p06_shap_explanations.csv`
- `p06_comparison_summary.csv`
- `p06_size_analysis.csv`
- `p06_shap_empresa_grande.png`
- `p06_shap_empresa_pequena.png`
- `p06_metadata.json`

---

# 9. Conclusión general

Se ejecutaron las seis pruebas funcionales y metodológicas previstas sobre Prospect Finder BVQ v10.

Las pruebas P01 a P04 no evidenciaron fallos en los controles evaluados:

- el ranking fue reproducible;
- el ensayo de fuga temporal evitó incorporar información posterior al corte;
- el modelo procesó casos con faltantes y valores atípicos;
- el caso de sensibilidad ±5 % mostró estabilidad local.

Las pruebas P05 y P06 generaron hallazgos que deben permanecer explícitamente documentados.

P05 mostró que la recuperación temprana del ranking en TEST es limitada: ninguno de los 54 positivos conocidos aparece dentro de los primeros 100 puestos.

P06 mostró que las características de escala empresarial tienen una influencia importante en las explicaciones locales estudiadas.

Estos resultados no se utilizarán para modificar retrospectivamente el modelo v10.

El principio metodológico se mantiene:

**Modelo → Priorización → Especialista → Decisión**

Prospect Finder BVQ debe utilizarse como una herramienta de apoyo para ordenar y analizar un universo amplio de empresas, complementando el criterio de los especialistas y no sustituyéndolo.

Cualquier modificación del feature set, estrategia de entrenamiento, hiperparámetros o criterio de priorización basada en los resultados finales de TEST deberá ser tratada como una futura versión del modelo y evaluada mediante un nuevo protocolo independiente.

---

# 10. Estado final

**Pruebas ejecutadas:** 6 de 6

**P01:** CUMPLE
**P02:** CUMPLE
**P03:** CUMPLE
**P04:** CUMPLE
**P05:** CUMPLE CON LIMITACIÓN
**P06:** CUMPLE CON OBSERVACIÓN

**Modelo v10:** CONGELADO

**Retuning posterior a TEST:** NO

**Evidencias:** `reports/live_tests/`

**Conclusión:** Pruebas completadas y resultados documentados.
