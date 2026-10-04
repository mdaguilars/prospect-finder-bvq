# Bitácora del proyecto — Prospect Finder BVQ

## 1. Propósito

Esta bitácora registra la evolución técnica y metodológica del proyecto Prospect Finder BVQ.

Su propósito es mantener trazabilidad sobre:

- cambios realizados;
- decisiones metodológicas;
- experimentos ejecutados;
- resultados relevantes;
- aprendizajes;
- limitaciones;
- riesgos;
- evolución del producto;
- próximos pasos.

La cronología utiliza como referencia los commits registrados en Git y GitHub cuando estos se encuentran disponibles.

Los resultados históricos no se reemplazan retrospectivamente.

Cuando cambia:

- el dataset;
- el target;
- el protocolo temporal;
- las variables;
- la metodología de evaluación;

los resultados anteriores se mantienen como evidencia histórica y no se comparan directamente como si correspondieran al mismo experimento.

---

## 2. Proyecto

**Nombre:**

Sistema inteligente basado en aprendizaje automático y redes neuronales para identificar y priorizar empresas con potencial de convertirse en emisores del mercado de valores ecuatoriano para la Bolsa de Valores Quito.

**Integrantes:**

- Marcelo David Aguilar Salguero
- Francisco Xavier Meneses Játiva
- Luis Miguel Gallardo Dávila

---

# 3. Etapa inicial del proyecto

## 3.1 Creación de la estructura inicial — 6 de septiembre de 2026

**Commit:** `8a91813`

**Mensaje Git:** `Initial project structure`

### Actividades

Se creó la estructura inicial del repositorio para separar:

- datos originales;
- datos intermedios;
- datos procesados;
- código;
- notebooks;
- modelos;
- resultados;
- figuras;
- documentación.

### Decisión

Mantener desde el inicio una estructura modular que separe los archivos originales de los productos derivados del procesamiento.

### Aprendizaje

La separación por etapas facilita:

- reproducibilidad;
- mantenimiento;
- auditoría;
- trazabilidad.

---

## 3.2 Documentación del entorno técnico — 7 de septiembre de 2026

**Commit:** `fbd6812`

**Mensaje Git:** `Add technical environment documentation and dependencies`

### Actividades

Se documentaron:

- Python;
- Visual Studio Code;
- PowerShell;
- Git;
- GitHub;
- `.venv`;
- principales dependencias.

Se incorporaron:

`requirements.txt`

y:

`requirements-lock.txt`

### Decisión

Utilizar un entorno virtual específico para Prospect Finder BVQ.

### Aprendizaje

Registrar versiones del entorno desde las primeras etapas reduce problemas posteriores de reproducibilidad.

---

## 3.3 Validación de Jupyter — 7 de septiembre de 2026

**Commit:** `87b257a`

**Mensaje Git:** `Add Jupyter environment validation`

### Actividades

Se creó:

`notebooks/00_validacion_entorno.ipynb`

para verificar que Jupyter utilizara el intérprete correspondiente al entorno virtual.

### Decisión

Utilizar notebooks principalmente para:

- exploración;
- pruebas;
- validaciones.

Los procesos principales reproducibles se implementan mediante scripts Python.

---

## 3.4 Inventario inicial de fuentes — 20 de septiembre de 2026

**Commit:** `4d9e517`

**Mensaje Git:** `Add data source inventory`

### Fuentes identificadas

- estados financieros de la Superintendencia de Compañías, Valores y Seguros;
- Registro del Mercado de Valores de la SCVS;
- información complementaria del Data Warehouse de la Bolsa de Valores Quito.

### Decisión

Utilizar información financiera de SCVS como fuente principal de variables empresariales y financieras.

La información BVQ se mantiene como fuente complementaria para integración y validación.

### Aprendizaje

Las estructuras históricas difieren entre períodos y requieren homologación antes del modelado.

---

## 3.5 Primera construcción del dataset — 20 de septiembre de 2026

**Commit:** `71f28ce`

**Mensaje Git:** `Add initial MVP dataset builder`

### Actividades

Se desarrolló una primera versión del proceso reproducible de integración.

Se estableció como unidad de análisis:

`empresa-año`

### Aprendizaje

La evolución histórica de las estructuras contables requiere reglas explícitas de homologación.

---

# 4. Primer ciclo metodológico v1–v3

## 4.1 Dataset reproducible inicial

**Commit:** `9231e85`

**Mensaje Git:** `Build reproducible SCVS MVP dataset and temporal features`

Se analizaron las estructuras:

- `PLAN_413`
- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

En el primer MVP se utilizaron principalmente:

- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

`PLAN_413` fue excluido inicialmente por baja cobertura y ausencia de eventos positivos dentro de las cohortes evaluadas.

### Resultado histórico

- 887.469 observaciones empresa-año;
- 166.389 empresas;
- período 2015–2023.

### Variables homologadas iniciales

- `ACTIVO_TOTAL`
- `ACTIVO_CORRIENTE`
- `EFECTIVO`
- `PASIVO_TOTAL`
- `PASIVO_CORRIENTE`
- `PASIVO_NO_CORRIENTE`
- `PATRIMONIO`
- `CAPITAL`
- `UTILIDAD_NETA`

### Validaciones contables

Se verificó aproximadamente:

`Activo = Pasivo + Patrimonio`

con cumplimiento cercano a:

`99,24 %`

También:

`Pasivo total = Pasivo corriente + Pasivo no corriente`

con cumplimiento aproximado de:

`99,31 %`.

---

## 4.2 Primera versión de TARGET_24M

Se construyó:

`TARGET_24M`

para identificar empresas que se registraban como emisores dentro de los 24 meses posteriores a una observación.

Resultado de esta primera metodología:

- 884.072 observaciones;
- 166.107 empresas;
- 440 positivos;
- 883.632 negativos;
- prevalencia aproximada: 0,0498 %.

### División temporal inicial

- TRAIN: 2015–2020;
- VALIDATION: 2021;
- TEST: 2022–2023.

### Decisión

No utilizar un split aleatorio como mecanismo principal de evaluación.

### Nota

Este procedimiento corresponde únicamente al ciclo histórico v1–v3.

Posteriormente se determinó que la disponibilidad temporal de la información financiera requería una regla más conservadora.

---

## 4.3 Baseline v1 — Regresión logística

**Commit:** `f215802`

**Mensaje Git:** `Add reproducible logistic regression baseline v1`

Configuración principal:

- `C = 1.0`;
- `class_weight = balanced`;
- regularización L2;
- `solver = lbfgs`;
- `max_iter = 2000`;
- `random_state = 42`.

### Resultados históricos

| Conjunto | PR-AUC | ROC-AUC |
|---|---:|---:|
| TRAIN | 0,099413 | 0,946436 |
| VALIDATION | 0,031095 | 0,940593 |
| TEST | 0,007291 | 0,927740 |

### VALIDATION Top-K

| K | Positivos | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 5 | 0,1000 | 0,1190 | 259,76 |
| 100 | 5 | 0,0500 | 0,1190 | 129,88 |
| 200 | 5 | 0,0250 | 0,1190 | 64,94 |

### Aprendizaje

El problema debía tratarse principalmente como:

**ranking y priorización**

y no como clasificación operativa utilizando directamente threshold 0,50.

---

## 4.4 Baseline v2 — Eliminación del sector

**Commit:** `d1e6070`

**Mensaje Git:** `Add sector stability analysis and logistic baseline v2`

Se eliminó:

`SECTOR_CIIU`

manteniendo el resto del pipeline equivalente.

### Resultados históricos VALIDATION

| Métrica | v1 | v2 |
|---|---:|---:|
| PR-AUC | 0,031095 | 0,024402 |
| ROC-AUC | 0,940593 | 0,961619 |
| Recall | 0,880952 | 0,952381 |
| Precision@50 | 0,1000 | 0,0800 |
| Recall@50 | 0,1190 | 0,0952 |

### Decisión

No reemplazar v1.

### Aprendizaje

Una mejora de ROC-AUC no garantiza una mejora operacional en el ranking.

---

## 4.5 Experimento v3 — Regularización

**Commit:** `c47c931`

**Mensaje Git:** `Add logistic regularization experiment v3`

Se probaron:

- `C = 0.001`
- `C = 0.01`
- `C = 0.1`
- `C = 1`
- `C = 10`

### Resultados históricos

| C | PR-AUC | ROC-AUC |
|---:|---:|---:|
| 0.001 | 0,024217 | 0,955848 |
| 0.01 | 0,027559 | 0,951061 |
| 0.1 | 0,030555 | 0,946416 |
| 1 | 0,031095 | 0,940593 |
| 10 | 0,031135 | 0,934021 |

La diferencia entre `C = 10` y `C = 1` en PR-AUC fue mínima.

### Decisión

Mantener:

`C = 1.0`

como configuración de referencia de esa etapa.

---

## 4.6 Figuras y análisis de errores

**Commit:** `95a516a`

**Mensaje Git:** `Add baseline evaluation figures and error summaries`

Se generaron:

- distribución de clases;
- Precision-Recall;
- matriz de confusión;
- positivos Top-K;
- Lift@K;
- Precision@K.

Posteriormente:

**Commit:** `b280b8b`

**Mensaje Git:** `Add detailed baseline error analysis`

Se profundizó en:

- verdaderos positivos;
- falsos positivos;
- falsos negativos;
- posición de los positivos;
- sectores;
- perfiles financieros.

### Aprendizaje

Las métricas agregadas no son suficientes para determinar utilidad comercial.

---

## 4.7 Informe preliminar

**Commit:** `343708d`

**Mensaje Git:** `Add preliminary results report`

Se consolidó:

- objetivo;
- fuentes;
- dataset;
- variables;
- metodología;
- división temporal;
- baselines;
- métricas;
- ranking;
- errores;
- fortalezas;
- limitaciones;
- próximos pasos.

---

# 5. Corrección metodológica temporal

## 5.1 Problema identificado

Los archivos financieros identificaban el ejercicio fiscal, pero no la fecha exacta en la que la información de cada empresa estuvo disponible para una decisión comercial.

Utilizar el cierre fiscal como fecha de decisión podía introducir una hipótesis temporal demasiado optimista.

---

## 5.2 Regla conservadora

Se adoptó:

- ejercicio fiscal: año `t`;
- fecha ordinaria máxima asumida de disponibilidad: `30/04/t+1`;
- fecha de decisión: `01/05/t+1`;
- inicio del horizonte: `01/05/t+1`;
- fin del horizonte de 24 meses: `30/04/t+3`.

Esta regla es una:

**suposición normativa conservadora**

y no la fecha real individual de presentación de cada empresa.

---

## 5.3 Elegibilidad

Una observación permanece prospectable únicamente cuando la empresa todavía no era emisor antes de la fecha de decisión.

Las observaciones posteriores a su primera inscripción como emisor son excluidas.

---

## 5.4 Dataset temporal corregido del ciclo v4–v9

Resultado:

- 883.988 observaciones elegibles;
- 423 positivos;
- prevalencia aproximada: 0,0479 %.

### División temporal

| Conjunto | Período | Observaciones | Positivos |
|---|---|---:|---:|
| TRAIN | 2015–2018 | 324.055 | 262 |
| EMBARGO VALIDATION | 2019 | 91.932 | 34 |
| VALIDATION | 2020 | 98.470 | 34 |
| EMBARGO TEST | 2021 | 109.095 | 39 |
| TEST | 2022–2023 | 260.436 | 54 |

### Decisión

A partir de v4, esta metodología reemplazó a la metodología temporal utilizada en v1–v3.

Los resultados anteriores se mantuvieron exclusivamente como evidencia histórica.

---

# 6. Ciclo experimental v4–v9

## 6.1 v4 — Regresión logística

**Commit:** `69d29da`

VALIDATION 2020:

- PR-AUC: 0,004570;
- ROC-AUC: 0,920359;
- Top 50: 0 positivos;
- Top 100: 1;
- Top 200: 1.

### Aprendizaje

La corrección temporal redujo el desempeño aparente.

Esto refleja una evaluación más exigente y no necesariamente un deterioro del algoritmo.

---

## 6.2 v5 — Regresión logística sin sector

**Commit:** `69d29da`

VALIDATION:

- PR-AUC: 0,005311;
- ROC-AUC: 0,924389;
- Top 50: 0;
- Top 100: 1;
- Top 200: 1.

### Decisión

Continuar explorando modelos sin `SECTOR_CIIU`.

---

## 6.3 v6 — Regresión logística con trayectoria

**Commit:** `c44f24e`

Se incorporaron variables actuales y temporales.

VALIDATION:

- PR-AUC: 0,005254;
- ROC-AUC: 0,906290;
- Top 50: 1;
- Top 100: 1;
- Top 200: 1.

### Decisión

Mantener v6 como baseline comparable del ciclo.

---

## 6.4 v7 — HistGradientBoosting inicial

**Commit:** `1c6555c`

TRAIN:

- PR-AUC aproximado: 0,871232.

VALIDATION:

- PR-AUC: 0,004980;
- ROC-AUC: 0,816540;
- Top 50: 1;
- Top 100: 1;
- Top 200: 2.

### Diagnóstico

Sobreajuste severo.

### Decisión

Descartar v7 como candidato.

---

## 6.5 v8 — HistGradientBoosting regularizado

**Commit:** `d81bbfa`

Configuración regularizada:

| Parámetro | v7 | v8 |
|---|---:|---:|
| learning_rate | 0,10 | 0,05 |
| max_iter | 100 | 150 |
| max_leaf_nodes | 31 | 7 |
| max_depth | Sin límite | 3 |
| min_samples_leaf | 20 | 100 |
| l2_regularization | 0 | 1,0 |

VALIDATION:

- PR-AUC: 0,011805;
- ROC-AUC: 0,922378;
- Top 50: 2;
- Top 100: 3;
- Top 200: 4.

### Decisión

v8 se convirtió en el mejor benchmark del ciclo v4–v9.

---

## 6.6 Backtesting v8

**Commit:** `0565ead`

Folds:

- evaluación 2018;
- evaluación 2019;
- evaluación 2020.

Resultados:

| Año | PR-AUC | ROC-AUC | Top 50 | Lift@50 |
|---:|---:|---:|---:|---:|
| 2018 | 0,034551 | 0,884906 | 5 | 146,93 |
| 2019 | 0,016766 | 0,938953 | 2 | 108,16 |
| 2020 | 0,011805 | 0,922378 | 2 | 115,85 |

PR-AUC promedio:

`0,021041`

Lift@50 promedio:

`123,64`

### Aprendizaje

v8 mantuvo capacidad de priorización en varias ventanas, aunque con variabilidad temporal.

---

## 6.7 v9 — MLP

**Commit:** `1ae9531`

VALIDATION:

- PR-AUC: 0,005262;
- ROC-AUC: 0,848818;
- Top 50: 0;
- Top 100: 0;
- Top 200: 0.

### Decisión

No sustituir v8.

### Aprendizaje

Una red neuronal más compleja no garantiza mejor desempeño en un problema tabular extremadamente desbalanceado.

---

## 6.8 Backtest v6

**Commit:** `c6fadce`

Resultados:

| Año | PR-AUC | ROC-AUC | Top 50 | Lift@50 |
|---:|---:|---:|---:|---:|
| 2018 | 0,015520 | 0,897956 | 1 | 29,39 |
| 2019 | 0,013212 | 0,918509 | 2 | 108,16 |
| 2020 | 0,005254 | 0,906290 | 1 | 57,92 |

PR-AUC promedio:

`0,011329`

Lift@50 promedio:

`65,15`

---

## 6.9 Comparación v6 vs. v8

**Commit:** `99a8ca0`

**Mensaje Git:** `add v6 vs v8 temporal comparison`

Se verificó programáticamente que ambos modelos utilizaran:

- mismos folds;
- mismos períodos;
- mismo universo de evaluación;
- mismas variables comparables;
- mismo protocolo.

### PR-AUC

| Año | v6 | v8 | Diferencia |
|---:|---:|---:|---:|
| 2018 | 0,015520 | 0,034551 | +0,019031 |
| 2019 | 0,013212 | 0,016766 | +0,003554 |
| 2020 | 0,005254 | 0,011805 | +0,006550 |

Promedios:

| Métrica | v6 | v8 |
|---|---:|---:|
| PR-AUC | 0,011329 | 0,021041 |
| Lift@50 | 65,15 | 123,64 |

### Decisión

Mantener v8 como benchmark histórico del ciclo.

---

# 7. Nueva generación v10

## 7.1 Dataset base v10

En octubre de 2026 se construyó una nueva generación del dataset.

Archivo:

`data/processed/v10_base_integrated_2012_2023.csv.gz`

Script:

`scripts/build_v10_base.py`

SHA-256:

`b44f9ccf309c20a59be436953a0c6e7f9a3dc1f11cc6f2c87e41c1676a3a2a8d`

Resultado:

- 1.030.671 observaciones elegibles;
- 568 positivos;
- 310 RUC positivos únicos;
- 0 duplicados empresa-año;
- período 2012–2023;
- prevalencia aproximada: 0,055110 %.

### Procedencia

- `AMBAS`: 815.331;
- `SOLO_BI`: 146.683;
- `SOLO_HISTORICO`: 68.657.

---

## 7.2 Identidad empresarial

Prioridad:

1. identificación proveniente de `bi_compania`;
2. RUC histórico único del mismo expediente;
3. RUC histórico disponible en la propia observación.

Se excluyeron:

- 535 filas;
- 276 expedientes;

para los que no fue posible determinar un RUC de forma reproducible.

No se utilizaron:

- fuzzy matching;
- coincidencias automáticas por nombre.

---

## 7.3 Target v10

Se mantiene:

`TARGET_24M`

con la regla temporal conservadora de fecha de decisión.

La fuente principal de emisores fue validada contra fichas registrales.

Resultado de validación:

- 619 RUC efectivos en ambas fuentes;
- 619 fechas coincidentes;
- 0 diferencias de fecha.

Estados considerados efectivos:

- `VIGENTE`;
- `CANCELADA`.

No se consideran eventos positivos:

- inscripción negada;
- ente creado;
- en proceso de inscripción.

---

## 7.4 Integración financiera

### Activos

Variable:

`activos_final`

Cobertura aproximada:

`99,25 %`

### Patrimonio

Variable:

`patrimonio_final`

Cobertura aproximada:

`99,25 %`

### Utilidad neta

Variable:

`utilidad_neta_final`

Cobertura aproximada:

`90,26 %`

La utilidad histórica no se utilizó como fallback cuando existían diferencias de definición entre fuentes.

---

## 7.5 Bloques financieros vacíos

Se definió:

`bi_8_finanzas_cero`

para observaciones en las que ocho variables financieras principales de BI son simultáneamente cero.

Se identificaron:

`31.744 observaciones`

con esta condición.

---

## 7.6 Variables excluidas preventivamente

Se excluyeron del conjunto predictor:

- `cia_imvalores`;
- `id_estado_financiero`;
- `posicion_general`.

Las razones incluyeron:

- riesgo de leakage;
- naturaleza administrativa;
- falta de justificación predictiva.

---

# 8. Feature set v10

## 8.1 Dataset core

Se construyó:

`data/processed/v10_features_core_2012_2023.csv.gz`

Contiene 22 columnas.

Incluye:

- identificación;
- target;
- split;
- variables financieras actuales;
- rezagos `t-1`;
- tipo de compañía;
- provincia;
- indicadores de calidad.

---

## 8.2 Dataset financiero

Se construyó:

`data/processed/v10_features_financial_2012_2023.csv.gz`

Número de observaciones:

`1.030.671`

Se añadieron diez variables financieras:

- `fin_ratio_patrimonio_activos`
- `fin_roa`
- `fin_margen_neto`
- `fin_rotacion_activos`
- `fin_roe`
- `flag_patrimonio_no_positivo`
- `fin_crecimiento_activos`
- `fin_crecimiento_patrimonio`
- `fin_crecimiento_ventas`
- `fin_crecimiento_empleados`

El dataset financiero contiene:

`32 columnas`

---

# 9. Protocolo temporal v10

Se congeló la siguiente división:

| Conjunto | Período | Observaciones | Positivos |
|---|---|---:|---:|
| TRAIN | 2012–2018 | 470.722 | 407 |
| EMBARGO 1 | 2019 | 91.934 | 34 |
| VALIDATION | 2020 | 98.471 | 34 |
| EMBARGO 2 | 2021 | 109.099 | 39 |
| TEST | 2022–2023 | 260.445 | 54 |

La separación fue congelada antes de la evaluación final.

---

# 10. Backtesting temporal v10

Se utilizaron cuatro folds.

### Fold 1

TRAIN:

`2012–2013`

EMBARGO:

`2014`

EVALUACIÓN:

`2015`

### Fold 2

TRAIN:

`2012–2014`

EMBARGO:

`2015`

EVALUACIÓN:

`2016`

### Fold 3

TRAIN:

`2012–2015`

EMBARGO:

`2016`

EVALUACIÓN:

`2017`

### Fold 4

TRAIN:

`2012–2016`

EMBARGO:

`2017`

EVALUACIÓN:

`2018`

Estos folds permitieron evaluar estabilidad antes de abrir TEST.

---

# 11. Modelo final v10

## 11.1 Selección

El candidato finalmente seleccionado fue:

`v10_hgb_financial_c3`

Configuración:

`C3_CONSERVATIVE`

Algoritmo:

`HistGradientBoostingClassifier`

### Parámetros

- `learning_rate = 0.03`
- `max_iter = 250`
- `max_leaf_nodes = 5`
- `max_depth = 2`
- `min_samples_leaf = 200`
- `l2_regularization = 3`
- `early_stopping = False`
- `random_state = 42`
- `class_weight = balanced`
- `categorical_features = from_dtype`

---

## 11.2 Variables

El modelo utiliza 25 variables:

1. `activos_final`
2. `patrimonio_final`
3. `bi_ingresos_ventas`
4. `bi_n_empleados`
5. `activos_final_t1`
6. `patrimonio_final_t1`
7. `bi_ingresos_ventas_t1`
8. `bi_n_empleados_t1`
9. `fin_ratio_patrimonio_activos`
10. `fin_roa`
11. `fin_margen_neto`
12. `fin_rotacion_activos`
13. `fin_roe`
14. `fin_crecimiento_activos`
15. `fin_crecimiento_patrimonio`
16. `fin_crecimiento_ventas`
17. `fin_crecimiento_empleados`
18. `TIENE_T_MENOS_1`
19. `flag_activos_negativos`
20. `flag_ventas_negativas`
21. `flag_empleados_fijo`
22. `flag_empleados_salto_temporal`
23. `flag_empleados_anomalia_total`
24. `flag_patrimonio_no_positivo`
25. `tipo_compania`

`provincia`

no forma parte del modelo.

---

## 11.3 Artefacto congelado

Archivo:

`models/v10/v10_hgb_financial_c3_final.joblib`

Contiene:

- modelo;
- nombre;
- configuración;
- features;
- variables numéricas;
- booleanas;
- categóricas;
- target;
- período de entrenamiento;
- período de TEST.

---

# 12. Apertura controlada de TEST v10

El conjunto TEST v10 permaneció cerrado hasta completar:

- definición del dataset;
- feature set;
- backtesting;
- comparación de alternativas;
- selección del candidato;
- congelamiento de configuración.

Una vez cerrado el proceso de selección se realizó la evaluación final.

### TEST

Período:

`2022–2023`

Observaciones:

`260.445`

Positivos:

`54`

### Resultados

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0.007468801 |
| ROC-AUC | 0.934603901 |

### Ranking combinado

- Top 50: 0 positivos;
- Top 100: 0 positivos;
- Top 200: 1 positivo.

El comportamiento de 2022 fue mejor que el observado en 2023.

### Decisión

No realizar:

- retuning;
- modificación de variables;
- ajuste de hiperparámetros;
- cambio de candidato;

después de observar TEST.

El resultado final se conserva como evaluación fuera de muestra del modelo congelado.

---

# 13. Interpretabilidad

## 13.1 Permutation Importance

Se utilizó como análisis global complementario.

Su objetivo fue observar cuánto cambia el desempeño al alterar cada variable.

---

## 13.2 SHAP y LIME

**Commit:** `2deb583`

Se implementó el análisis:

`src/analysis/analyze_v10_shap_lime.py`

Documento:

`docs/v10_explainability_shap_lime.md`

### SHAP global

Principales variables:

| Rank | Variable | Mean Abs SHAP |
|---:|---|---:|
| 1 | activos_final | 0.062030 |
| 2 | bi_ingresos_ventas | 0.033458 |
| 3 | patrimonio_final_t1 | 0.016976 |
| 4 | fin_crecimiento_patrimonio | 0.014514 |
| 5 | fin_ratio_patrimonio_activos | 0.010584 |
| 6 | fin_crecimiento_activos | 0.009977 |
| 7 | patrimonio_final | 0.009283 |
| 8 | activos_final_t1 | 0.008516 |
| 9 | fin_roa | 0.008402 |
| 10 | fin_margen_neto | 0.007309 |

### Decisión

Utilizar:

**SHAP como explicador principal**

y:

**LIME como técnica complementaria**.

SHAP reconstruyó el score de los casos evaluados con precisión numérica.

LIME se mantuvo como aproximación local.

---

# 14. Sesgos y riesgos

**Commit:** `790081b`

Se realizó una evaluación explícita de:

- concentración;
- tamaño empresarial;
- disponibilidad de información;
- tipo de compañía;
- distribución geográfica;
- riesgo de interpretación automática.

### Decisión

No utilizar características descriptivas como reglas automáticas de exclusión.

La provincia se mantiene fuera de las variables predictivas.

### Principio

`Modelo → Priorización → Especialista → Decisión`

---

# 15. Estabilidad

**Commit:** `8e20058`

Se documentó el comportamiento temporal del modelo y la necesidad de monitorear:

- variables;
- score;
- ranking;
- cohortes;
- desempeño posterior;
- drift.

### Decisión

La estabilidad se considera parte del criterio de evaluación, no únicamente una métrica secundaria.

---

# 16. Diseño operacional

**Commit:** `7bc937d`

Se definió el diseño del producto Prospect Finder BVQ.

Principales decisiones:

- una empresa por fila;
- utilizar score como indicador de priorización;
- no presentarlo como probabilidad;
- incorporar filtros;
- incluir ficha financiera;
- incluir explicación;
- incluir comparables;
- mantener supervisión humana.

---

# 17. Arquitectura de solución

**Commit:** `de2d3c2`

Se definió la arquitectura:

`Datos → Modelo → Producto operacional → Base de datos → API → Interfaz`

Se estableció separación entre:

- datos;
- procesamiento;
- modelo;
- persistencia;
- API;
- frontend.

---

# 18. Ranking operacional

**Commit:** `e37fe23`

**Mensaje Git:** `feat: add v10 operational ranking builder`

Script:

`src/product/build_operational_ranking_v10.py`

Fecha de decisión:

`2024-05-01`

Información utilizada:

`2023`

### Resultado

Empresas prospectables:

`137.156`

Archivo:

`data/processed/v10_operational_ranking_2024_05_01.csv.gz`

Top 500:

`reports/results/v10/product/v10_operational_top500_2024_05_01.csv`

### Distribución del score

- mínimo: 0.006069;
- máximo: 0.973694;
- media: 0.157457;
- mediana: 0.089750.

### Control de reproducibilidad

El scoring operacional fue comparado contra las observaciones 2023 utilizadas en TEST.

Resultado:

- 137.156 observaciones comparadas;
- diferencia máxima del score: 0.

### Decisión

El score se utilizará como:

**Índice de Afinidad Bursátil**

en la capa de presentación.

No se interpretará como probabilidad calibrada.

---

# 19. Similitud con emisores históricos

**Commit:** `7bed6da`

Se implementó:

`src/product/build_issuer_similarity_v10.py`

### Universo de referencia

Emisores conocidos hasta:

`2024-05-01`

Total:

`288`

Perfiles con siete variables completas:

`272`

### Variables

1. activos;
2. patrimonio;
3. ventas;
4. empleados;
5. patrimonio / activos;
6. ROA;
7. rotación de activos.

### Metodología

- percentiles anuales;
- distancia euclidiana;
- transformación a similitud 0–100;
- cinco emisores comparables.

### Resultado

Prospectos con similitud:

`131.320`

Prospectos sin información suficiente:

`5.836`

Registros de comparables:

`656.600`

### Archivos

`data/processed/v10_issuer_similarity_summary_2024_05_01.csv.gz`

`data/processed/v10_issuer_similarity_matches_2024_05_01.csv.gz`

### Decisión

Mantener completamente separadas:

- afinidad predictiva;
- similitud financiera.

No se implementa una fórmula ponderada entre ambas.

---

# 20. Evaluación retrospectiva de similitud

Se analizaron empresas que posteriormente se convirtieron en emisores, sin incorporarlas como referencias futuras.

Número de casos:

`29`

Similitud Top 1 media de ese grupo:

`96,01`

Resto del universo:

`87,19`

### Interpretación

El resultado es exploratorio.

No demuestra capacidad predictiva independiente del motor de similitud.

No se utilizó para ajustar:

- modelo;
- ranking;
- metodología;
- threshold.

---

# 21. Dependencias para backend

**Commit:** `2067948`

**Mensaje Git:** `chore: add FastAPI and PostgreSQL dependencies`

Se incorporaron dependencias para:

- FastAPI;
- Uvicorn;
- SQLAlchemy;
- psycopg;
- Pydantic;
- Alembic;
- dotenv;
- PostgreSQL.

### Decisión

Separar la aplicación del procesamiento analítico mediante una API.

---

# 22. PostgreSQL y Docker

**Commit:** `a5bba08`

**Mensaje Git:** `feat: add PostgreSQL API infrastructure`

Se incorporó:

`compose.yaml`

Imagen:

`postgres:17-alpine`

Base de desarrollo:

`prospect_finder_bvq`

Se incorporaron:

- configuración;
- conexión;
- modelos ORM;
- cargador operacional.

### Tablas

#### `operational_prospects`

Registros:

`137.156`

#### `issuer_similarity_summary`

Registros:

`137.156`

#### `issuer_similarity_matches`

Registros:

`656.600`

### Total

`930.912 registros`

cargados y validados.

### Decisión

PostgreSQL se utilizará como capa operacional para la aplicación.

Los CSV continuarán siendo artefactos reproducibles del pipeline, pero no serán consultados directamente por el frontend.

---

# 23. FastAPI

**Commit:** `18dc974`

**Mensaje Git:** `feat: add FastAPI health and prospect endpoints`

Se implementó la aplicación:

`src/api/main.py`

y los primeros endpoints.

### Health

`GET /api/health`

Valida:

- disponibilidad del servicio;
- conexión PostgreSQL.

### Ranking

`GET /api/prospects`

### Detalle

`GET /api/prospects/{expediente_key}`

La ficha de empresa incluye:

- identificación;
- ranking;
- score;
- percentil;
- indicadores;
- calidad;
- comparables.

---

# 24. Catálogos y filtros

**Commit:** `d1c44e4`

**Mensaje Git:** `feat: add catalogs and normalized prospect filters`

Se incorporó:

`GET /api/catalogs`

### Catálogos actuales

Provincias:

`24`

Tipos de compañía:

`9`

### Ejemplos de conteos

Pichincha:

`43.487`

Guayas:

`52.560`

ANÓNIMA:

`65.769`

SOCIEDAD POR ACCIONES SIMPLIFICADA:

`41.638`

RESPONSABILIDAD LIMITADA:

`28.972`

SUCURSAL EXTRANJERA:

`722`

### Normalización

Se incorporó limpieza de espacios internos y finales para evitar duplicidades visuales provenientes de los archivos fuente.

### Filtros actuales

- búsqueda;
- provincia;
- tipo de compañía;
- score mínimo;
- similitud mínima;
- disponibilidad de comparables;
- paginación.

---

# 25. SHAP operacional

**Commit:** `169ba8b`

**Mensaje Git:** `feat: add SHAP explainability API`

Se implementó:

`src/api/services/explainability.py`

Endpoints:

`GET /api/explainability/global`

y:

`GET /api/explainability/prospects/{expediente_key}`

---

## 25.1 Metodología

Se mantiene:

`SHAP PermutationExplainer`

con:

- modelo v10 congelado;
- 25 variables exactas;
- categorías aprendidas en TRAIN;
- background de 75 observaciones de TRAIN;
- `max_evals = 51`.

---

## 25.2 Validación operacional

Caso funcional:

score modelo:

`0.9736944399096825`

score del ranking:

`0.9736944399096824`

diferencia:

`1.11 × 10^-16`

### Reconstrucción SHAP

Base:

`0.1783474992099843`

Score reconstruido:

`0.9736944399096834`

Error:

`8.88 × 10^-16`

### Conclusión

La explicación operacional reproduce adecuadamente la predicción presentada al usuario.

---

# 26. Evaluación de TreeExplainer

Se evaluó TreeExplainer con el objetivo de reducir el tiempo de respuesta.

Tiempo observado:

`≈ 0,046 segundos`

Sin embargo, la reconstrucción obtenida fue:

`≈ 0,476484`

frente al score real:

`≈ 0,973694`

Diferencia:

`≈ 0,49721`

### Decisión

Descartar TreeExplainer.

La velocidad no compensa una explicación que no sea fiel al score producido por el modelo.

---

# 27. Optimización de SHAP

La primera ejecución de PermutationExplainer podía presentar tiempos elevados debido al cold start.

Una ejecución inicial llegó aproximadamente a:

`72,66 segundos`

Las siguientes ejecuciones fueron sustancialmente menores.

Se probaron backgrounds reducidos y se comprobó que el principal problema no correspondía al número de observaciones del background.

### Solución

Implementar precalentamiento en el `lifespan` de FastAPI.

Al iniciar la aplicación:

1. se carga el runtime;
2. se carga el modelo;
3. se inicializa SHAP;
4. se ejecuta una explicación operacional de calentamiento.

### Resultado

Después de:

`Application startup complete`

una primera consulta local posterior registró aproximadamente:

`0,254 segundos`

También se verificaron otros casos con tiempos adecuados para el prototipo.

### Decisión

Mantener PermutationExplainer y resolver la latencia mediante warm-up.

---

# 28. Pruebas automáticas API

Se incorporó:

`pytest 9.1.1`

Archivos:

- `tests/api/test_health.py`
- `tests/api/test_prospects.py`
- `tests/api/test_catalogs.py`
- `tests/api/test_explainability.py`

### Cobertura funcional inicial

Se prueban:

- health;
- conexión;
- ranking;
- paginación;
- búsqueda;
- filtros;
- detalle;
- catálogos;
- explicabilidad global;
- explicabilidad local;
- manejo de empresas inexistentes.

### Resultado individual

Health:

`2 passed`

Prospects:

`5 passed`

Catalogs:

`2 passed`

Explainability:

`3 passed`

### Suite completa

Comando:

`python -m pytest "tests\api" -q`

Resultado:

`12 passed`

Se registraron tres warnings de deprecación provenientes de dependencias de SHAP/Matplotlib.

No constituyen fallos de las pruebas.

---

# 29. Versionamiento de pruebas

**Commit:** `b1b577f`

**Mensaje Git:**

`test: add API integration tests`

El commit incluye:

- actualización de `requirements.txt`;
- actualización de `requirements-lock.txt`;
- cuatro archivos de pruebas.

El commit fue publicado correctamente en GitHub:

`169ba8b..b1b577f main -> main`

---

# 30. Preparación del frontend

En octubre de 2026 se instaló:

`Node.js LTS 24.19.0`

y:

`npm 11.17.0`

El entorno queda preparado para comenzar la construcción de la interfaz web.

Esta etapa todavía no se considera implementada.

---

# 31. Actualización documental — octubre de 2026

Después de completar la infraestructura operacional se inició la actualización de la documentación para evitar inconsistencias entre el diseño original y la implementación real.

Se actualizaron:

`docs/entorno_tecnico.md`

`docs/v10_solution_architecture.md`

`docs/v10_operational_product_design.md`

`docs/v10_explainability_shap_lime.md`

y la presente:

`docs/bitacora.md`

### Objetivo

Distinguir claramente entre:

- componentes históricos;
- componentes implementados;
- componentes pendientes.

---

# 32. Estado metodológico actual

## 32.1 Unidad

Entrenamiento:

`empresa-año`

Producto:

`empresa`

---

## 32.2 Horizonte

`24 meses`

---

## 32.3 Fecha de decisión

Para ejercicio fiscal `t`:

`01/05/t+1`

---

## 32.4 Elegibilidad

Se excluyen empresas que ya eran emisores antes de la fecha de decisión correspondiente.

---

## 32.5 Dataset

`v10_base_integrated_2012_2023.csv.gz`

Estado:

**CONGELADO**

---

## 32.6 Features

Feature set:

**CONGELADO**

Modelo:

25 variables.

---

## 32.7 Split

TRAIN:

`2012–2018`

VALIDATION:

`2020`

TEST:

`2022–2023`

con embargos 2019 y 2021.

---

## 32.8 Modelo

`v10_hgb_financial_c3`

Estado:

**CONGELADO**

---

## 32.9 TEST

Estado:

**EVALUADO UNA VEZ DESPUÉS DE LA SELECCIÓN**

No se realizó retuning posterior.

---

## 32.10 Producto

Ranking operacional:

**IMPLEMENTADO**

---

## 32.11 Similitud

Motor de emisores comparables:

**IMPLEMENTADO**

---

## 32.12 Explicabilidad

SHAP:

**IMPLEMENTADO EN ANÁLISIS Y API**

LIME:

**COMPLEMENTARIO / ACADÉMICO**

---

## 32.13 Backend

PostgreSQL:

**IMPLEMENTADO**

FastAPI:

**IMPLEMENTADO**

Pruebas:

**12 APROBADAS**

---

## 32.14 Frontend

Estado:

**PENDIENTE**

---

# 33. Principales decisiones acumuladas

1. La unidad analítica de entrenamiento es empresa-año.
2. El producto muestra una empresa por fila.
3. El horizonte objetivo es de 24 meses.
4. Se utiliza una regla temporal conservadora de disponibilidad.
5. No se utiliza split aleatorio como evaluación principal.
6. Se utilizan embargos temporales.
7. Las empresas ya emisoras se excluyen del universo prospectable.
8. PR-AUC es más informativo que Accuracy para este problema.
9. Precision@K, Recall@K y Lift@K son centrales para evaluar ranking.
10. ROC-AUC es complementario.
11. Un threshold de 0,50 no constituye la lógica operacional del producto.
12. El problema se formula principalmente como ranking.
13. El score no representa probabilidad calibrada.
14. El modelo final es `v10_hgb_financial_c3`.
15. El modelo permanece congelado después de TEST.
16. Provincia no forma parte de las variables predictivas.
17. SHAP es la técnica principal de explicabilidad.
18. LIME es complementario.
19. TreeExplainer fue descartado para el modelo actual por falta de fidelidad.
20. El score y la similitud no se combinan.
21. Los comparables son una señal exploratoria.
22. PostgreSQL es la capa de persistencia operacional.
23. FastAPI es la capa de acceso al producto.
24. El frontend no deberá acceder directamente al modelo ni a PostgreSQL.
25. Las decisiones comerciales permanecen bajo supervisión humana.
26. TEST no se utiliza para retuning.
27. Los resultados históricos se conservan.
28. Las nuevas versiones deberán registrarse explícitamente.
29. Las credenciales reales no deben versionarse.
30. Los datasets operacionales no deben publicarse en Git.

---

# 34. Principales aprendizajes

Se han identificado los siguientes aprendizajes:

- la homologación contable es crítica;
- el problema presenta desbalance extremo;
- los eventos positivos son escasos;
- la prevalencia cambia temporalmente;
- la disponibilidad temporal de la información es tan importante como el valor de la variable;
- los embargos ayudan a reducir contaminación;
- ROC-AUC por sí sola no representa adecuadamente la utilidad del ranking;
- los modelos complejos pueden sobreajustarse severamente;
- una red neuronal no necesariamente supera modelos tabulares;
- HistGradientBoosting regularizado mostró mejor comportamiento que configuraciones más flexibles;
- el desempeño cambia entre cohortes;
- TEST puede ser considerablemente más exigente que VALIDATION;
- el score debe utilizarse como ranking;
- la interpretabilidad debe validarse contra el score real;
- una técnica de explicación rápida no es útil si no reproduce la predicción;
- los comparables aportan contexto, pero no reemplazan la señal predictiva;
- la explicación no representa causalidad;
- la arquitectura desacoplada facilita evolución;
- la persistencia relacional simplifica la capa de producto;
- las pruebas automáticas son necesarias antes de construir la interfaz;
- la supervisión humana es una parte central del diseño.

---

# 35. Riesgos y mitigaciones

| Riesgo | Descripción | Mitigación |
|---|---|---|
| Leakage temporal | Uso prematuro de información futura | Fechas de decisión y embargos |
| Solapamiento de target | Ventanas objetivo compartidas | Períodos de embargo |
| Sobreajuste | Exceso de ajuste a TRAIN | Regularización y backtesting |
| Desbalance extremo | Muy pocos positivos | PR-AUC y Top-K |
| Pocos positivos | Alta variabilidad | Evaluación temporal |
| Drift | Cambio del comportamiento | Monitoreo futuro |
| Score no calibrado | Confusión con probabilidad | Presentarlo como afinidad |
| Concentración | Mayor representación de ciertos perfiles | Auditoría segmentada |
| Causalidad | Confundir explicación con causa | Comunicación explícita |
| Uso automático | Tomar ranking como decisión | Human-in-the-loop |
| Similitud mal interpretada | Confundir cercanía con predicción | Mantener señales separadas |
| Explicación incorrecta | Mostrar factores que no reconstruyen score | Validación SHAP |
| Credenciales expuestas | Publicar secretos en Git | Variables de entorno |
| Datos sensibles | Versionar datos operacionales | Exclusión del repositorio |
| Obsolescencia | Modelo pierde capacidad temporal | Monitoreo y nueva versión |

---

# 36. Limitaciones actuales

Las principales limitaciones vigentes son:

1. el target continúa siendo extremadamente desbalanceado;
2. TEST contiene únicamente 54 eventos positivos;
3. el comportamiento cambia entre años;
4. la regla de disponibilidad financiera es una aproximación conservadora y no la fecha individual real de presentación;
5. la mayor parte de las variables son financieras;
6. el score no está calibrado como probabilidad;
7. un score alto no garantiza conversión en emisor;
8. existen factores comerciales y estratégicos no observados por el modelo;
9. SHAP explica el modelo, no causalidad;
10. la similitud con emisores no constituye una predicción;
11. el análisis retrospectivo de similitud no demuestra poder predictivo;
12. la interfaz web todavía no está implementada;
13. la autenticación institucional no está implementada;
14. el monitoreo operacional completo todavía está pendiente;
15. DVC todavía no está integrado;
16. MLflow todavía no está integrado;
17. FastAPI todavía no está contenerizado;
18. las migraciones Alembic todavía no están configuradas;
19. la validación funcional con especialistas todavía está pendiente;
20. el ambiente actual corresponde a desarrollo local.

---

# 37. Reproducibilidad

El proyecto utiliza actualmente:

- Git;
- GitHub;
- `.venv`;
- `requirements.txt`;
- `requirements-lock.txt`;
- scripts reproducibles;
- datasets congelados;
- protocolos congelados;
- modelo serializado;
- documentación metodológica;
- SHA-256 donde corresponde;
- `random_state = 42`;
- Docker;
- PostgreSQL;
- pruebas automáticas;
- metadatos;
- evidencia de resultados.

Los datos originales y operacionales de gran tamaño no se almacenan directamente en el repositorio.

---

# 38. Infraestructura actual

### Python

Versión utilizada:

`3.13.7`

### PostgreSQL

Imagen:

`postgres:17-alpine`

### Docker

Docker Desktop:

`4.93`

Docker:

`29.8.1`

### Backend

FastAPI:

`0.142.2`

Uvicorn:

`0.54.0`

SQLAlchemy:

`2.1.3`

psycopg:

`3.3.6`

pytest:

`9.1.1`

### Frontend

Node.js:

`24.19.0`

npm:

`11.17.0`

Las versiones completas del entorno se mantienen en:

`requirements-lock.txt`

---

# 39. Estado actual por componente

| Componente | Estado |
|---|---|
| Fuentes | Implementado |
| Integración | Implementada |
| Dataset v10 | Congelado |
| Target | Congelado |
| Feature set | Congelado |
| Split temporal | Congelado |
| Backtesting | Completado |
| Modelos clásicos | Evaluados |
| MLP | Evaluado |
| Selección final | Completada |
| TEST | Completado |
| Modelo v10 | Congelado |
| Análisis de errores | Completado |
| SHAP global | Completado |
| SHAP local | Completado |
| LIME | Completado |
| Sesgos | Analizados |
| Estabilidad | Analizada |
| Ranking operacional | Implementado |
| Índice de Afinidad | Implementado como score operacional |
| Similitud con emisores | Implementada |
| PostgreSQL | Implementado |
| Docker PostgreSQL | Implementado |
| ORM | Implementado |
| FastAPI | Implementado |
| Health API | Implementado |
| Ranking API | Implementado |
| Detalle API | Implementado |
| Catálogos API | Implementado |
| SHAP API | Implementado |
| Pruebas automáticas | 12 aprobadas |
| Node.js/npm | Instalados |
| Frontend | Pendiente |
| Docker FastAPI | Pendiente |
| Alembic | Pendiente de configuración |
| DVC | Pendiente |
| MLflow | Pendiente |
| Monitoreo operacional completo | Pendiente |
| Validación con especialistas | Pendiente |

---

# 40. Evidencias recientes en Git

| Commit | Evidencia |
|---|---|
| `2deb583` | SHAP y LIME |
| `790081b` | Sesgos y riesgos |
| `8e20058` | Estabilidad |
| `7bc937d` | Diseño operacional |
| `de2d3c2` | Arquitectura |
| `e37fe23` | Ranking operacional |
| `7bed6da` | Similitud con emisores |
| `2067948` | Dependencias FastAPI/PostgreSQL |
| `a5bba08` | Infraestructura PostgreSQL |
| `18dc974` | API health y prospectos |
| `d1c44e4` | Catálogos y filtros |
| `169ba8b` | SHAP operacional |
| `b1b577f` | Pruebas API |

---

# 41. Separación investigación-producto

Prospect Finder BVQ distingue dos contextos.

## Investigación

Incluye:

- construcción del target;
- datasets;
- features;
- entrenamiento;
- comparación;
- backtesting;
- TEST;
- análisis de sesgos;
- interpretabilidad;
- estabilidad.

## Producto

Incluye:

- ranking operacional;
- percentiles;
- motor de similitud;
- PostgreSQL;
- API;
- SHAP bajo demanda;
- interfaz web.

La capa de producto consume un modelo congelado.

No modifica automáticamente el modelo.

---

# 42. Estado del TEST

Debe mantenerse una distinción clara.

## TEST histórico v1–v3

Fue utilizado durante el primer ciclo metodológico y se mantiene únicamente como evidencia histórica.

## TEST v4–v9

Perteneció a la metodología temporal corregida anterior y no se utilizó durante la selección de esos modelos.

## TEST v10

El nuevo dataset v10 modificó el universo.

El TEST v10 contiene:

- 260.445 observaciones;
- 54 positivos.

Fue abierto únicamente después de:

- congelar dataset;
- congelar features;
- congelar split;
- completar backtesting;
- seleccionar el candidato final;
- congelar hiperparámetros.

Después de observar TEST:

**no se realizó retuning.**

---

# 43. Próxima fase

La siguiente fase del proyecto se concentra en convertir el backend ya implementado en un prototipo completo.

Las actividades pendientes principales son:

1. construir el frontend web;
2. integrar el frontend con FastAPI;
3. validar ranking y ficha de empresa desde navegador;
4. presentar SHAP en lenguaje de negocio;
5. presentar emisores comparables;
6. completar dockerización de FastAPI;
7. configurar migraciones Alembic;
8. implementar DVC;
9. implementar MLflow;
10. completar mecanismos de monitoreo;
11. ejecutar pruebas funcionales finales;
12. realizar validación con al menos dos especialistas BVQ;
13. documentar resultados de validación;
14. preparar el informe final;
15. preparar la presentación final.

---

# 44. Validación con especialistas

La propuesta contempla validación funcional con al menos:

`2 especialistas de la BVQ`

Esta validación todavía no se ha ejecutado.

No deberán inventarse resultados ni participantes.

Cuando se realice deberá registrar:

- fecha;
- participante;
- función;
- escenario evaluado;
- observaciones;
- problemas encontrados;
- utilidad percibida;
- cambios sugeridos;
- decisión sobre el prototipo.

---

# 45. Uso responsable

Prospect Finder BVQ es una herramienta de apoyo.

Sus resultados:

- no constituyen recomendación de inversión;
- no determinan aceptación regulatoria;
- no garantizan que una empresa emitirá valores;
- no reemplazan análisis financiero;
- no reemplazan análisis comercial;
- no reemplazan análisis legal;
- no reemplazan análisis regulatorio;
- no deben utilizarse como único criterio de decisión.

El score expresa:

**prioridad relativa**

y no:

**probabilidad real calibrada**.

La similitud expresa:

**cercanía del perfil financiero**

y no:

**probabilidad de emisión**.

SHAP explica:

**el comportamiento del modelo**

y no:

**una relación causal**.

---

# 46. Estado actual de la bitácora

La bitácora se encuentra actualizada hasta:

- ciclos históricos v1–v3;
- corrección temporal;
- modelos v4–v9;
- backtesting temporal;
- dataset v10;
- integración de fuentes;
- congelamiento del dataset;
- feature set v10;
- protocolo temporal v10;
- backtesting v10;
- selección del modelo final;
- apertura controlada de TEST;
- evaluación final;
- explicabilidad SHAP/LIME;
- análisis de sesgos;
- estabilidad;
- diseño operacional;
- arquitectura;
- ranking operacional;
- similitud con emisores;
- PostgreSQL;
- Docker PostgreSQL;
- FastAPI;
- filtros;
- catálogos;
- SHAP operacional;
- optimización de SHAP;
- pruebas automáticas;
- actualización de dependencias;
- preparación del entorno frontend.

Modelo final:

`v10_hgb_financial_c3`

Configuración:

`C3_CONSERVATIVE`

Estado:

**CONGELADO**

Producto operacional:

**IMPLEMENTADO EN BACKEND**

Backend:

**IMPLEMENTADO Y PROBADO**

Pruebas API:

`12 passed`

Frontend:

**SIGUIENTE ETAPA**

---

# 47. Regla de mantenimiento de la bitácora

Esta bitácora deberá actualizarse cuando se produzca:

- nuevo experimento;
- cambio de dataset;
- nueva fuente;
- modificación de target;
- cambio de features;
- nueva versión del modelo;
- evaluación nueva;
- evidencia nueva de sesgo;
- cambio de protocolo;
- componente nuevo de producto;
- endpoint nuevo;
- cambio de arquitectura;
- despliegue;
- validación con usuarios;
- cambio que altere el rumbo del proyecto.

Los experimentos completados no deben eliminarse.

Los resultados antiguos deben mantenerse identificados como históricos cuando hayan sido reemplazados metodológicamente.

La bitácora complementa el historial de Git:

**Git registra qué cambió; la bitácora registra por qué cambió, qué resultado produjo y qué decisión se tomó.**