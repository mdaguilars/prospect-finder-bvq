# Prospect Finder BVQ

## Sistema basado en aprendizaje automático para identificar y priorizar empresas con potencial de convertirse en emisores del mercado de valores ecuatoriano

### Proyecto de Maestría en Inteligencia Artificial

**Universidad de Las Américas — UDLA**

**Integrantes:**

- Marcelo David Aguilar Salguero
- Francisco Xavier Meneses Játiva
- Luis Miguel Gallardo Dávila

---

# 1. Descripción del proyecto

Prospect Finder BVQ es un proyecto de inteligencia artificial orientado a apoyar el proceso de prospección de potenciales emisores para la Bolsa de Valores Quito (BVQ).

El problema organizacional identificado es la dificultad para analizar de manera sistemática un universo amplio de empresas ecuatorianas, aplicar criterios homogéneos de evaluación y priorizar aquellas que podrían presentar mayor afinidad con el mercado de valores.

La solución propuesta busca construir un sistema capaz de analizar información histórica de las empresas y generar un ranking de prospectos que sirva como apoyo para la gestión comercial, financiera y de prospección de la BVQ.

El sistema no pretende determinar automáticamente qué empresas deben convertirse en emisores ni sustituir el criterio especializado.

Su función es:

- reducir el universo inicial de análisis;
- identificar señales financieras relevantes;
- ordenar empresas según afinidad relativa;
- apoyar la priorización comercial;
- facilitar una revisión posterior por especialistas.

La decisión final permanece bajo revisión humana.

---

# 2. Objetivo del prototipo

Desarrollar un prototipo basado en aprendizaje automático que permita identificar patrones asociados históricamente con empresas que posteriormente se registraron por primera vez como emisores del mercado de valores ecuatoriano.

La unidad de análisis es:

`empresa-año`

La variable objetivo es:

`TARGET_24M`

donde:

- **1:** la empresa se registra por primera vez como emisor dentro de los siguientes 24 meses a partir de la fecha de decisión;
- **0:** la empresa no se registra como nuevo emisor dentro de ese horizonte.

Las empresas que ya eran emisoras antes de la fecha de decisión correspondiente son excluidas del universo elegible.

---

# 3. Formulación del problema

Prospect Finder BVQ se aborda principalmente como un problema de:

**ranking y priorización**

y no únicamente como una clasificación binaria convencional.

El objetivo operativo no es asignar automáticamente una etiqueta definitiva a una empresa.

El propósito es ordenar un universo amplio de compañías de manera que las primeras posiciones concentren, en la medida de lo posible, empresas con características similares a aquellas que históricamente se convirtieron posteriormente en emisores.

Por esta razón, además de métricas tradicionales como PR-AUC y ROC-AUC, el proyecto utiliza:

- Precision@K;
- Recall@K;
- Lift@K.

---

# 4. Fuentes de información

## 4.1 Superintendencia de Compañías, Valores y Seguros — Información financiera y societaria

La SCVS constituye la fuente pública principal para construir las variables financieras y empresariales del proyecto.

Durante el ciclo v1–v9 se utilizó principalmente el dataset financiero armonizado construido a partir de estados financieros 2015–2023.

Para la generación v10 se incorporó como fuente financiera principal:

`data/raw/scvs/ranking/bi_ranking.csv`

con cobertura utilizada:

**2012–2023**

Esta fuente aporta, entre otras variables:

- activos;
- patrimonio;
- ingresos y ventas;
- ingresos totales;
- utilidad antes de impuestos;
- impuesto a la renta;
- utilidad del ejercicio;
- utilidad neta;
- número de empleados;
- segmento empresarial;
- clasificación CIIU;
- indicadores financieros;
- gastos y deuda.

La identificación empresarial se complementa con:

`data/raw/scvs/catalogos/bi_compania.csv`

El dataset histórico armonizado 2015–2023 se conserva como fuente complementaria para ampliar cobertura histórica, realizar validaciones y aplicar fallbacks controlados en activos y patrimonio cuando corresponda.

Los archivos originales y derivados de datos se mantienen localmente bajo `data/` y no se almacenan en Git.

---

## 4.2 Superintendencia de Compañías, Valores y Seguros — Registro del Mercado de Valores

Esta fuente se utiliza para construir la variable objetivo.

Los principales archivos utilizados son:

- `listado_entes_65001_1789908466941.xlsx`
- `codigos_fichas_registrales_1789908530079.xlsx`

Ubicación local:

`data/raw/scvs/mercado_valores/`

La primera fecha de inscripción como emisor se utiliza para determinar el evento objetivo.

Se identificaron **619 RUC de emisores históricos** con información disponible en las dos fuentes utilizadas para validación de la primera inscripción.

Las fechas coincidieron para los 619 casos contrastados.

---

## 4.3 Bolsa de Valores Quito — Data Warehouse

La información interna de la BVQ se considera una fuente complementaria de:

- validación;
- análisis;
- enriquecimiento futuro.

No constituye actualmente la fuente principal del feature set utilizado en v1–v9.

Los datos internos de la BVQ no se publican en el repositorio.

---

## 4.4 Condiciones de acceso y reutilización

Las fuentes públicas utilizadas fueron obtenidas de los portales institucionales de la Superintendencia de Compañías, Valores y Seguros.

Durante la revisión documental realizada para el proyecto no se identificó una licencia abierta específica aplicable a los archivos utilizados que permita asumir una autorización irrestricta de redistribución.

Por esta razón:

- se mantiene a la SCVS como fuente original;
- los archivos originales no se redistribuyen mediante GitHub;
- no se atribuye una licencia no publicada explícitamente;
- cualquier publicación externa de datasets derivados deberá revisar previamente las condiciones institucionales y normativas aplicables.

La información interna de la BVQ se considera información institucional y no se publica mediante el repositorio.

El detalle se encuentra en:

`docs/inventario_fuentes.md`

---

# 5. Homologación de estados financieros

Los estados financieros de SCVS presentan diferentes estructuras contables a lo largo del período analizado.

Por esta razón fue necesario construir un proceso de homologación.

Durante el ciclo v1–v9 se analizaron:

- `PLAN_413`
- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

Para el MVP 2015–2023 se utilizaron principalmente:

- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

`PLAN_413` quedó fuera de esta primera generación por su baja cobertura dentro del período inicialmente utilizado.

Las reglas de homologación se mantienen separadas del código mediante:

`config/scvs_account_mapping.csv`

---

# 6. Dataset financiero armonizado — ciclo v1–v9

El proceso inicial de homologación produjo:

| Indicador | Resultado |
|---|---:|
| Observaciones empresa-año | 887.469 |
| Empresas únicas | 166.389 |
| Período | 2015–2023 |

Archivo generado localmente:

`data/interim/scvs_financials_harmonized_2015_2023.csv.gz`

Este archivo continúa preservado como evidencia del ciclo v1–v9 y como fuente complementaria para v10.

No se almacena en Git.

---

# 7. Variables financieras homologadas

Se homologaron nueve variables financieras principales:

| Variable | Tipo | Descripción |
|---|---|---|
| `ACTIVO_TOTAL` | Numérica | Total de activos |
| `ACTIVO_CORRIENTE` | Numérica | Total de activos corrientes |
| `EFECTIVO` | Numérica | Efectivo y equivalentes |
| `PASIVO_TOTAL` | Numérica | Total de pasivos |
| `PASIVO_CORRIENTE` | Numérica | Pasivos corrientes |
| `PASIVO_NO_CORRIENTE` | Numérica | Pasivos no corrientes |
| `PATRIMONIO` | Numérica | Patrimonio |
| `CAPITAL` | Numérica | Capital registrado |
| `UTILIDAD_NETA` | Numérica | Resultado neto del período |

El detalle se documenta en:

`docs/diccionario_datos.md`

---

# 8. Validación de la homologación contable

Se verificaron las principales ecuaciones contables.

## 8.1 Activo = Pasivo + Patrimonio

El **99,24 %** de las observaciones presentó una diferencia relativa menor o igual al **0,01 %**.

## 8.2 Pasivo total = Pasivo corriente + Pasivo no corriente

El **99,31 %** de las observaciones presentó una diferencia relativa menor o igual al **0,01 %**.

Estas verificaciones permiten evaluar la consistencia estructural del proceso de homologación, aunque no sustituyen una revisión contable individual de cada observación.

---

# 9. Corrección de disponibilidad temporal

Uno de los principales ajustes metodológicos realizados después del ciclo inicial v1–v3 fue revisar la fecha en la que la información financiera podía considerarse disponible para una decisión real.

Los archivos utilizados identifican el ejercicio fiscal, pero no proporcionan una fecha individual de presentación o publicación para cada estado financiero.

Utilizar el 31 de diciembre del año fiscal como fecha de decisión podía generar una hipótesis temporal demasiado optimista.

Por esta razón, desde v4 se utiliza una regla normativa conservadora.

Para un ejercicio fiscal `t` se asume:

| Concepto | Fecha |
|---|---|
| Ejercicio financiero | año `t` |
| Fecha ordinaria máxima de disponibilidad asumida | `30/04/t+1` |
| Fecha de decisión | `01/05/t+1` |
| Inicio del horizonte objetivo | `01/05/t+1` |
| Fin del horizonte de 24 meses | `30/04/t+3` |

Esta regla constituye una **suposición normativa de disponibilidad**.

No debe interpretarse como la fecha real individual de presentación de cada empresa.

---

# 10. Dataset etiquetado temporalmente corregido — ciclo v4–v9

Después de aplicar la regla temporal corregida y excluir observaciones de empresas que ya eran emisoras antes de la fecha de decisión, el ciclo v4–v9 produjo:

| Indicador | Resultado |
|---|---:|
| Observaciones financieras originales | 887.469 |
| Empresas en dataset armonizado | 166.389 |
| Emisores históricos identificados | 619 |
| Observaciones ya emisoras antes de la decisión | 3.481 |
| Observaciones elegibles | **883.988** |
| `TARGET_24M = 1` | **423** |
| Prevalencia positiva aproximada | **0,0479 %** |

Estos valores corresponden al universo 2015–2023 utilizado por v4–v9 y se mantienen como referencia histórica.

La generación v10 utiliza un universo integrado distinto y se documenta posteriormente en este README y en `docs/v10_dataset_freeze.md`.

---

# 11. Distribución temporal del target corregido — ciclo v4–v9

| Año fiscal | Observaciones elegibles | Positivos |
|---:|---:|---:|
| 2015 | 75.715 | 41 |
| 2016 | 79.234 | 73 |
| 2017 | 82.417 | 89 |
| 2018 | 86.689 | 59 |
| 2019 | 91.932 | 34 |
| 2020 | 98.470 | 34 |
| 2021 | 109.095 | 39 |
| 2022 | 123.283 | 32 |
| 2023 | 137.153 | 22 |
| **Total** | **883.988** | **423** |

La cantidad de eventos positivos varía de manera importante entre períodos.

Por esta razón la evaluación considera explícitamente la estabilidad temporal.

---

# 12. División temporal del ciclo v4–v9

No se utiliza una partición aleatoria como mecanismo principal de validación.

Para los experimentos v4–v9 se utilizó:

| Conjunto | Período | Observaciones | Positivos |
|---|---|---:|---:|
| TRAIN | 2015–2018 | 324.055 | 262 |
| EMBARGO VALIDATION | 2019 | 91.932 | 34 |
| VALIDATION | 2020 | 98.470 | 34 |
| EMBARGO TEST | 2021 | 109.095 | 39 |
| TEST | 2022–2023 | 260.436 | 54 |

Esta partición pertenece al ciclo v4–v9.

La división temporal definitiva para los futuros experimentos v10 todavía debe definirse sobre el nuevo universo congelado y deberá mantener separación temporal y períodos de embargo compatibles con el horizonte de 24 meses.

---

# 13. Uso de períodos de embargo

El horizonte de predicción es de 24 meses.

Utilizar años inmediatamente consecutivos como TRAIN y VALIDATION puede provocar superposición entre ventanas objetivo.

Para reducir este riesgo se utilizan períodos de embargo.

La estructura actual es:

| Etapa | Período |
|---|---|
| TRAIN | 2015–2018 |
| EMBARGO | 2019 |
| VALIDATION | 2020 |
| EMBARGO | 2021 |
| TEST | 2022–2023 |

Los períodos de embargo no son utilizados como conjuntos de evaluación principal.

---

# 14. Estado del conjunto TEST del ciclo v1–v9

Debe distinguirse entre dos etapas metodológicas.

## 14.1 TEST histórico del ciclo v1–v3

El Baseline v1 fue evaluado históricamente sobre TEST 2022–2023 utilizando la metodología temporal inicial.

Ese resultado permanece documentado como evidencia histórica.

## 14.2 TEST de la metodología corregida

Después de reconstruir el target y las divisiones temporales desde v4, se generó un nuevo TEST temporalmente seguro para:

**2022–2023**

Este conjunto contiene:

- **260.436 observaciones**
- **54 positivos**

Este TEST **no ha sido utilizado para seleccionar ni ajustar v4, v5, v6, v7, v8 o v9**.

Permanece reservado para una evaluación posterior.

---

# 15. Ingeniería inicial de variables

## 15.1 Transformaciones monetarias

Para reducir diferencias de escala se utiliza:

`sign(x) × log(1 + |x|)`

sobre las principales variables monetarias.

## 15.2 Razones financieras

Se construyeron indicadores como:

| Variable | Fórmula conceptual |
|---|---|
| `LIQUIDEZ_CORRIENTE` | Activo corriente / pasivo corriente |
| `ENDEUDAMIENTO` | Pasivo total / activo total |
| `AUTONOMIA_FINANCIERA` | Patrimonio / activo total |
| `ROA` | Utilidad neta / activo total |
| `EFECTIVO_ACTIVOS` | Efectivo / activo total |
| `CAPITAL_ACTIVOS` | Capital / activo total |
| `PASIVO_CORRIENTE_PASIVO` | Pasivo corriente / pasivo total |

Los denominadores iguales a cero se mantienen como valores faltantes para ser tratados dentro del pipeline correspondiente.

---

# 16. Variables temporales — v6 en adelante

A partir de v6 se incorporó información de trayectoria financiera.

El feature set utilizado por v6 y v8 contiene:

- 16 variables correspondientes al período actual;
- 17 variables temporales relacionadas con información previa;
- **33 variables numéricas en total**.

El objetivo fue pasar de una fotografía financiera de un solo período a una representación que incorpore cambios en el tiempo.

Archivo utilizado:

`data/processed/mvp_features_temporal_v6.csv.gz`

Este dataset derivado no se almacena en Git.

---

# 17. Métricas de evaluación

Debido al desbalance extremo, `Accuracy` no se utiliza como métrica principal.

Las métricas generales son:

- PR-AUC;
- ROC-AUC;
- Precision;
- Recall;
- F1.

Las métricas relacionadas directamente con la priorización son:

- Precision@K;
- Recall@K;
- Lift@K.

Los valores principales de K son:

- 50;
- 100;
- 200.

PR-AUC y las métricas Top-K tienen especial importancia para evaluar el valor del sistema como herramienta de priorización.

---

# 18. Evolución experimental v1–v9

El desarrollo se divide metodológicamente en dos etapas.

## 18.1 Ciclo histórico v1–v3

Corresponde a la metodología temporal inicial.

Incluye:

- Baseline v1;
- Baseline v2 sin sector;
- v3 de regularización.

Estos resultados se conservan como trazabilidad histórica.

## 18.2 Ciclo temporal corregido v4–v9

A partir de v4 se utiliza:

- nueva definición temporal del target;
- fecha de decisión conservadora;
- observaciones elegibles corregidas;
- períodos de embargo;
- nuevo TRAIN;
- nueva VALIDATION;
- TEST reservado.

Por esta razón, las métricas de v1–v3 no deben compararse directamente con v4–v9 como si utilizaran el mismo protocolo.

---

# 19. Baseline v1 — Histórico

El primer modelo desarrollado fue una regresión logística.

Configuración:

| Parámetro | Valor |
|---|---|
| Modelo | Logistic Regression |
| `C` | 1.0 |
| `class_weight` | balanced |
| `solver` | lbfgs |
| `max_iter` | 2000 |
| `random_state` | 42 |
| Regularización | L2 |

Resultados históricos:

| Conjunto | PR-AUC | ROC-AUC |
|---|---:|---:|
| TRAIN | 0,099413 | 0,946436 |
| VALIDATION | 0,031095 | 0,940593 |
| TEST | 0,007291 | 0,927740 |

Estos resultados pertenecen exclusivamente al protocolo inicial.

Documentación:

`docs/baseline_v1.md`

---

# 20. Baseline v2 — Histórico

v2 eliminó `SECTOR_CIIU`.

Resultados históricos en VALIDATION:

| Métrica | v1 | v2 |
|---|---:|---:|
| PR-AUC | 0,031095 | 0,024402 |
| ROC-AUC | 0,940593 | 0,961619 |
| Precision@50 | 0,1000 | 0,0800 |
| Recall@50 | 0,1190 | 0,0952 |

La eliminación del sector no mejoró las métricas prioritarias dentro de este primer ciclo.

Documentación:

`docs/baseline_v2.md`

---

# 21. Experimento v3 — Histórico

Se evaluaron diferentes valores de regularización:

- `C = 0.001`
- `C = 0.01`
- `C = 0.1`
- `C = 1`
- `C = 10`

El mayor PR-AUC en VALIDATION correspondió a:

- `C = 10` → 0,031135
- `C = 1` → 0,031095

La diferencia absoluta fue solamente:

**0,000040**

Las métricas Top 50, Top 100 y Top 200 no mejoraron.

Se concluyó que no existía una mejora material suficiente para reemplazar la configuración de referencia.

Documentación:

`docs/baseline_v3.md`

---

# 22. Experimento v4 — Regresión logística temporalmente corregida

v4 fue el primer experimento bajo la metodología temporal corregida.

Se utilizó una regresión logística con información sectorial.

Resultados en VALIDATION 2020:

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0,004570 |
| ROC-AUC | 0,920359 |
| Positivos Top 50 | 0 |
| Positivos Top 100 | 1 |
| Positivos Top 200 | 1 |

La reducción frente a los resultados históricos v1 no debe interpretarse directamente como deterioro del algoritmo.

v4 utiliza una definición temporal más estricta y un universo diferente.

---

# 23. Experimento v5 — Regresión logística sin sector

Se eliminó nuevamente `SECTOR_CIIU`, esta vez bajo la metodología corregida.

Resultados en VALIDATION 2020:

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0,005311 |
| ROC-AUC | 0,924389 |
| Positivos Top 50 | 0 |
| Positivos Top 100 | 1 |
| Positivos Top 200 | 1 |

La mejora fue pequeña y el comportamiento Top-K continuó siendo limitado.

---

# 24. Experimento v6 — Regresión logística con variables temporales

v6 incorporó el feature set temporal de 33 variables.

No utiliza `SECTOR_CIIU`.

Preprocesamiento:

- `SimpleImputer(strategy="median")`;
- `StandardScaler()`.

Modelo:

- Logistic Regression;
- `C = 1.0`;
- `class_weight = balanced`;
- `solver = lbfgs`;
- `max_iter = 2000`;
- `random_state = 42`.

Resultados en VALIDATION 2020:

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0,005254 |
| ROC-AUC | 0,906290 |
| Positivos Top 50 | 1 |
| Positivos Top 100 | 1 |
| Positivos Top 200 | 1 |

v6 se mantiene como:

**baseline comparable de la metodología actual**

porque utiliza el mismo conjunto de variables y el mismo protocolo temporal utilizado para comparar posteriormente v8.

Script principal:

`src/models/train_logistic_temporal_features_v6.py`

---

# 25. Experimento v7 — HistGradientBoosting inicial

v7 introdujo un modelo no lineal basado en árboles.

Resultados principales:

| Conjunto / métrica | Resultado |
|---|---:|
| TRAIN PR-AUC | 0,871232 |
| VALIDATION PR-AUC | 0,004980 |
| VALIDATION ROC-AUC | 0,816540 |
| Positivos Top 50 | 1 |
| Positivos Top 100 | 1 |
| Positivos Top 200 | 2 |

La diferencia entre TRAIN y VALIDATION evidenció un fuerte sobreajuste.

v7 no se conserva como candidato operativo.

Su principal utilidad fue identificar la necesidad de incrementar la regularización.

---

# 26. Experimento v8 — HistGradientBoosting regularizado

v8 modificó la complejidad del modelo de v7.

Principales ajustes:

| Parámetro | v7 | v8 |
|---|---:|---:|
| `learning_rate` | 0,10 | 0,05 |
| `max_iter` | 100 | 150 |
| `max_leaf_nodes` | 31 | 7 |
| `max_depth` | sin límite explícito | 3 |
| `min_samples_leaf` | 20 | 100 |
| `l2_regularization` | 0 | 1,0 |

Se mantuvo ponderación de clases.

Resultados en VALIDATION 2020:

| Métrica | Resultado |
|---|---:|
| PR-AUC | **0,011805** |
| ROC-AUC | **0,922378** |
| Positivos Top 50 | **2** |
| Positivos Top 100 | **3** |
| Positivos Top 200 | **4** |

Resultados de ranking:

| K | Positivos | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 2 | 0,0400 | 0,0588 | 115,85 |
| 100 | 3 | 0,0300 | 0,0882 | 86,89 |
| 200 | 4 | 0,0200 | 0,1176 | 57,92 |

v8 constituye actualmente:

**el benchmark de mejor desempeño observado bajo la metodología temporal corregida.**

No constituye todavía el modelo final del proyecto.

---

# 27. Experimento v9 — MLP

v9 incorporó una primera alternativa mediante una red neuronal multicapa.

Resultados en VALIDATION 2020:

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0,005262 |
| ROC-AUC | 0,848818 |
| Positivos Top 50 | 0 |
| Positivos Top 100 | 0 |
| Positivos Top 200 | 0 |

v9 no mejora el desempeño de v8.

Este experimento demuestra que una arquitectura de mayor complejidad no produce necesariamente una mejor generalización.

v9 constituye una primera experimentación neuronal.

No se considera todavía el cumplimiento definitivo del componente TensorFlow/Keras previsto en la propuesta académica.

La evaluación posterior deberá incorporar una arquitectura implementada específicamente con TensorFlow/Keras.

---

# 28. Backtesting temporal rolling-origin

Para reducir la dependencia de una sola ventana de VALIDATION se implementó una evaluación rolling-origin.

Se utilizaron tres folds:

| Fold | TRAIN | EMBARGO | EVALUACIÓN |
|---|---|---|---|
| 1 | 2015–2016 | 2017 | 2018 |
| 2 | 2015–2017 | 2018 | 2019 |
| 3 | 2015–2018 | 2019 | 2020 |

Los años **2021–2023** no participan en estos backtests.

---

# 29. Backtest temporal v6

Resultados:

| Año evaluación | Positivos | PR-AUC | ROC-AUC | Top 50 | Lift@50 |
|---:|---:|---:|---:|---:|---:|
| 2018 | 59 | 0,015520 | 0,897956 | 1 | 29,39 |
| 2019 | 34 | 0,013212 | 0,918509 | 2 | 108,16 |
| 2020 | 34 | 0,005254 | 0,906290 | 1 | 57,92 |

Resumen de PR-AUC:

| Estadístico | v6 |
|---|---:|
| Media | 0,011329 |
| Mediana | 0,013212 |
| Desviación estándar muestral | 0,005386 |

Lift@50 promedio:

**65,15**

Script:

`src/evaluation/backtest_logistic_v6.py`

---

# 30. Backtest temporal v8

Resultados:

| Año evaluación | Positivos | PR-AUC | ROC-AUC | Top 50 | Lift@50 |
|---:|---:|---:|---:|---:|---:|
| 2018 | 59 | 0,034551 | 0,884906 | 5 | 146,93 |
| 2019 | 34 | 0,016766 | 0,938953 | 2 | 108,16 |
| 2020 | 34 | 0,011805 | 0,922378 | 2 | 115,85 |

Resumen de PR-AUC:

| Estadístico | v8 |
|---|---:|
| Media | 0,021041 |
| Mediana | 0,016766 |
| Desviación estándar muestral | 0,011960 |

ROC-AUC:

- media aproximada: **0,915412**;
- mediana: **0,922378**;
- desviación estándar muestral aproximada: **0,027689**.

Lift@50:

- promedio: **123,64**;
- mediana: **115,85**;
- rango aproximado: **108,16–146,93**.

Script:

`src/evaluation/backtest_hist_gradient_boosting_v8.py`

---

# 31. Comparación justa v6 vs v8

La comparación principal del ciclo actual utiliza:

- el mismo dataset;
- las mismas 33 variables;
- los mismos folds;
- los mismos períodos de TRAIN;
- los mismos años de embargo;
- los mismos universos de evaluación;
- las mismas métricas;
- TEST reservado.

El script de comparación valida programáticamente que los universos de evaluación sean equivalentes.

Script:

`src/evaluation/compare_v6_v8_backtests.py`

---

# 32. PR-AUC v6 vs v8

| Año | v6 | v8 | Diferencia |
|---:|---:|---:|---:|
| 2018 | 0,015520 | 0,034551 | +0,019031 |
| 2019 | 0,013212 | 0,016766 | +0,003554 |
| 2020 | 0,005254 | 0,011805 | +0,006550 |

Cambio relativo observado:

| Año | Cambio relativo v8 vs v6 |
|---:|---:|
| 2018 | +122,62 % |
| 2019 | +26,90 % |
| 2020 | +124,67 % |

v8 obtiene mayor PR-AUC que v6 en los tres períodos evaluados.

---

# 33. Resumen estadístico v6 vs v8

| Métrica | v6 | v8 |
|---|---:|---:|
| PR-AUC promedio | 0,011329 | **0,021041** |
| PR-AUC mediano | 0,013212 | **0,016766** |
| Desv. estándar PR-AUC | **0,005386** | 0,011960 |
| Lift@50 promedio | 65,15 | **123,64** |

La diferencia relativa del PR-AUC promedio es aproximadamente:

**+85,73 %**

a favor de v8.

La diferencia relativa del Lift@50 promedio es aproximadamente:

**+89,77 %**

a favor de v8.

v6 presenta una menor desviación estándar del PR-AUC, pero esa menor dispersión ocurre alrededor de un nivel promedio de rendimiento inferior.

Por tanto, menor variabilidad no se interpreta automáticamente como mejor modelo.

---

# 34. Interpretación de ROC-AUC

ROC-AUC no presenta una superioridad uniforme de v8.

- 2018: v6 supera a v8;
- 2019: v8 supera a v6;
- 2020: v8 supera a v6.

Por esta razón no se afirma que v8 domine todas las métricas.

La principal evidencia favorable a v8 se encuentra en:

- PR-AUC;
- desempeño Top-K;
- Lift@50.

Estas métricas se encuentran más directamente relacionadas con el objetivo de priorización del proyecto.

---

# 35. Variabilidad y nivel de confianza

El uso de rolling-origin permite evaluar el modelo en múltiples ventanas temporales.

Esto representa una mejora respecto de depender exclusivamente de un único conjunto de validación.

Sin embargo, actualmente solo se dispone de:

**3 folds temporales**

Por esta razón:

- la media se interpreta descriptivamente;
- la mediana se interpreta descriptivamente;
- la desviación estándar se interpreta descriptivamente;
- los rangos se utilizan como evidencia de variabilidad;
- no se presentan intervalos formales de confianza;
- no se realizan afirmaciones de significancia estadística no sustentadas por el número de ventanas disponibles.

---

# 36. Comparación actual de modelos

| Versión | Modelo | Variables temporales | PR-AUC VALIDATION 2020 | ROC-AUC | Top 50 | Estado |
|---|---|---|---:|---:|---:|---|
| v4 | Logistic Regression | No | 0,004570 | 0,920359 | 0 | Histórico metodología corregida |
| v5 | Logistic Regression sin sector | No | 0,005311 | 0,924389 | 0 | Histórico metodología corregida |
| v6 | Logistic Regression | Sí | 0,005254 | 0,906290 | 1 | Baseline comparable |
| v7 | HistGradientBoosting | Sí | 0,004980 | 0,816540 | 1 | Sobreajuste |
| v8 | HistGradientBoosting regularizado | Sí | **0,011805** | **0,922378** | **2** | Benchmark actual |
| v9 | MLP | Sí | 0,005262 | 0,848818 | 0 | Alternativa neuronal exploratoria |

---

# 37. Benchmark del ciclo v4–v9

El benchmark actual es:

**v8 — HistGradientBoosting regularizado**

La decisión se sustenta principalmente en:

- mayor PR-AUC que v6 en los tres folds del backtest;
- mayor PR-AUC promedio;
- mayor Lift@50 promedio;
- mejor concentración Top-K;
- reducción del sobreajuste observado en v7;
- complejidad operativa todavía manejable.

v8 no se considera todavía el modelo definitivo.

---

# 38. Baseline comparable del ciclo v4–v9

Para evaluar nuevas familias de modelos dentro del ciclo temporal corregido se mantiene:

**v6 — Logistic Regression con variables temporales**

como baseline comparable.

La razón es metodológica:

v6 y v8 utilizan el mismo feature set y el mismo protocolo de evaluación.

Comparar directamente v8 contra v1 como criterio principal sería menos riguroso porque v1 pertenece a otra definición temporal del dataset.

---

# 39. Riesgos metodológicos

| Riesgo | Mitigación actual |
|---|---|
| Leakage temporal | Fecha de decisión conservadora |
| Superposición del target | Períodos de embargo |
| Sobreajuste | Regularización y backtesting |
| Desbalance extremo | Ponderación de clases y PR-AUC |
| Pocos positivos | Evaluación por múltiples cohortes |
| Drift temporal | Rolling-origin |
| Scores no calibrados | Uso como ranking |
| Sesgo sectorial | Comparaciones con y sin sector |
| Comparaciones injustas | Mismo protocolo dentro de cada generación de datos |
| Complejidad excesiva | Mantener baseline lineal |
| Contaminación de TEST | TEST v4–v9 reservado; TEST v10 aún no abierto ni utilizado |
| Interpretación causal | Resultados interpretados como asociaciones predictivas |
| Automatización de decisiones | Human-in-the-loop |
| Identidad empresarial incompleta | Exclusión de filas sin RUC verificable en v10 |
| Inconsistencias entre fuentes | Reglas explícitas de precedencia, fallback y variables de auditoría |
| Fuga por variables técnicas o de mercado | Exclusión preventiva de `cia_imvalores`, `id_estado_financiero` y `posicion_general` |

---

# 40. Limitaciones actuales

Las principales limitaciones son:

1. El ciclo v4–v9 dispone de 423 positivos y v10 amplía el universo a 568 positivos, pero el evento sigue siendo extremadamente infrecuente.
2. La prevalencia final del universo v10 es aproximadamente 0,055110 %.
3. La disponibilidad temporal continúa basada en una regla normativa y no en la fecha real individual de presentación de cada empresa.
4. El universo v10 integra fuentes con coberturas históricas distintas.
5. La utilidad neta no dispone de fallback histórico debido a incompatibilidades detectadas entre definiciones de fuente.
6. Existen observaciones con variables faltantes y bloques financieros sin información útil.
7. El rendimiento de v6 y v8 varió entre cohortes temporales.
8. El backtesting histórico disponible para v6 y v8 utiliza únicamente tres folds.
9. Los scores actuales no están calibrados como probabilidades.
10. El feature set definitivo de v10 todavía no está construido.
11. La división temporal definitiva de TRAIN / embargo / VALIDATION / TEST para v10 todavía debe congelarse.
12. Random Forest todavía debe evaluarse sobre v10.
13. CatBoost todavía debe evaluarse sobre v10.
14. Debe implementarse una red TensorFlow/Keras para cumplir la etapa neuronal prevista en el proyecto.
15. Falta incorporar interpretabilidad mediante técnicas como SHAP.
16. Falta ampliar la evaluación explícita de sesgo y equidad.
17. Las variables de inversión societaria y otras fuentes complementarias todavía no forman parte del feature set congelado.
18. El Índice de Afinidad Bursátil todavía no está definido de manera definitiva.
19. El prototipo web funcional todavía está pendiente.
20. El conjunto TEST de v10 debe permanecer cerrado una vez se defina su partición, mientras continúe la selección de modelos.

---

# 41. Dataset base v10 congelado

La generación v10 dejó de ser únicamente una fuente potencial y pasó a contar con una base integrada físicamente construida y validada.

Archivo local:

`data/processed/v10_base_integrated_2012_2023.csv.gz`

Script reproducible:

`scripts/build_v10_base.py`

Documento de congelamiento:

`docs/v10_dataset_freeze.md`

El archivo procesado no se almacena en Git debido a las reglas de exclusión definidas para `data/processed/`.

## 41.1 Período

La base v10 utiliza ejercicios:

**2012–2023**

Los años 2024 y 2025 quedan fuera del universo supervisado actual porque todavía no disponen de una ventana completa y comparable de 24 meses para construir el target.

Podrán utilizarse posteriormente para scoring o análisis prospectivo.

## 41.2 Universo congelado

Después de integrar fuentes, resolver identidad, excluir filas sin RUC verificable y retirar observaciones de empresas que ya eran emisoras antes de la fecha de decisión, se obtuvo:

| Indicador | Resultado |
|---|---:|
| Unión inicial empresa-año | 1.035.294 |
| Filas excluidas sin RUC verificable | 535 |
| Observaciones excluidas por ser emisores previos | 4.088 |
| Observaciones elegibles finales | **1.030.671** |
| Positivos `TARGET_24M` | **568** |
| RUC positivos únicos | **310** |
| Prevalencia | **0,055110 %** |
| Duplicados empresa-año | **0** |

## 41.3 Procedencia del universo elegible

| Procedencia | Observaciones |
|---|---:|
| Ambas fuentes | 815.331 |
| Solo `bi_ranking` | 146.683 |
| Solo histórico | 68.657 |

La unión evita depender exclusivamente de `bi_ranking`, ya que el dataset histórico contiene observaciones empresa-año válidas ausentes de esa fuente.

## 41.4 Identidad empresarial

La prioridad para resolver el RUC es:

1. `bi_compania`;
2. RUC histórico único asociado al mismo expediente;
3. RUC de la propia fila histórica, únicamente si los anteriores no están disponibles.

Después de aplicar estas reglas quedaron 535 filas sin RUC utilizable, correspondientes a 276 expedientes únicos.

Estas filas fueron excluidas del universo supervisado porque sin RUC no puede determinarse de manera segura la condición histórica o futura de emisor.

No se aplicaron coincidencias por nombre ni fuzzy matching.

Se conserva además una bandera `ruc_difiere` para registrar discrepancias entre fuentes.

## 41.5 Validación del target

El target continúa definido como primera inscripción efectiva como emisor dentro de los 24 meses posteriores a la fecha de decisión.

La validación de la fuente de mercado confirmó:

- 619 RUC efectivos en `listado_entes`;
- 619 RUC equivalentes al restringir fichas registrales a estados `VIGENTE` y `CANCELADA`;
- 619 fechas coincidentes;
- 0 diferencias entre las fechas efectivas contrastadas.

Dentro del universo v10:

- 2012–2014 aportan 143 positivos;
- 2015–2023 contienen 425 positivos;
- los 423 positivos históricos del ciclo anterior están preservados;
- se incorporan 2 positivos adicionales de 2015 por ampliación de cobertura del universo.

## 41.6 Integración de activos y patrimonio

En las observaciones compartidas entre fuentes, activos y patrimonio presentan una coincidencia global superior al 99,6 % al centavo.

No obstante, las discrepancias restantes incluyen ceros, cambios de signo y diferencias materiales, por lo que no se utilizan promedios ni conciliaciones automáticas.

Se definió un bloque financiero de ocho variables BI:

- activos;
- patrimonio;
- ingresos por ventas;
- ingresos totales;
- utilidad antes de impuestos;
- impuesto a la renta;
- utilidad del ejercicio;
- utilidad neta.

Cuando las ocho variables son simultáneamente cero se registra:

`bi_8_finanzas_cero`

En el universo elegible existen:

**31.744 observaciones**

con esta condición.

Las variables finales:

- `activos_final`;
- `patrimonio_final`;

utilizan `bi_ranking` cuando el bloque financiero es válido y realizan fallback histórico cuando la información BI se considera vacía o cuando la empresa-año existe únicamente en el histórico.

Resultado:

- 92.640 fallbacks históricos de activos;
- 92.640 fallbacks históricos de patrimonio;
- cobertura final de activos: 99,25 %;
- cobertura final de patrimonio: 99,25 %.

## 41.7 Utilidad neta

La utilidad neta histórica no se utiliza como fallback.

La auditoría mostró que el dataset histórico contiene numerosos ceros donde `bi_ranking` reporta utilidades o pérdidas.

Por ello:

`utilidad_neta_final`

se construye únicamente desde `bi_utilidad_neta` cuando el bloque financiero BI es válido.

Resultado:

- 930.270 valores disponibles;
- cobertura final de 90,26 %.

La utilidad histórica permanece exclusivamente como variable de auditoría.

## 41.8 Variables excluidas preventivamente

No se incorporaron al dataset v10:

- `cia_imvalores`;
- `id_estado_financiero`;
- `posicion_general`.

Las razones corresponden respectivamente a:

- riesgo potencial de fuga de información;
- identificador técnico;
- posición de ranking no apropiada como predictor directo.

## 41.9 Distribución anual final

| Año | Elegibles | Positivos | Prevalencia |
|---:|---:|---:|---:|
| 2012 | 42.158 | 55 | 0,130462 % |
| 2013 | 47.140 | 49 | 0,103946 % |
| 2014 | 52.528 | 39 | 0,074246 % |
| 2015 | 76.468 | 43 | 0,056233 % |
| 2016 | 79.503 | 73 | 0,091820 % |
| 2017 | 83.107 | 89 | 0,107091 % |
| 2018 | 89.818 | 59 | 0,065688 % |
| 2019 | 91.934 | 34 | 0,036983 % |
| 2020 | 98.471 | 34 | 0,034528 % |
| 2021 | 109.099 | 39 | 0,035747 % |
| 2022 | 123.289 | 32 | 0,025955 % |
| 2023 | 137.156 | 22 | 0,016040 % |

## 41.10 Reproducibilidad binaria

El dataset v10 fue construido y posteriormente reconstruido desde las fuentes mediante:

`scripts/build_v10_base.py`

El archivo reconstruido produjo exactamente el mismo SHA-256 que el archivo validado:

`b44f9ccf309c20a59be436953a0c6e7f9a3dc1f11cc6f2c87e41c1676a3a2a8d`

Estado:

**BASE V10 CONGELADA**

El congelamiento comprende universo, target, identidad, período y reglas de integración de fuentes.

Todavía no comprende el feature set definitivo ni los splits de modelado v10.

---

# 42. Índice de Afinidad Bursátil

El proyecto contempla la construcción posterior de un:

**Índice de Afinidad Bursátil — IAB**

Los scores actuales no deben convertirse automáticamente en probabilidades.

El IAB deberá definirse después de:

1. estabilizar el modelo;
2. evaluar su comportamiento temporal;
3. analizar sesgos;
4. incorporar interpretabilidad;
5. evaluar calibración cuando corresponda;
6. definir una escala comprensible para usuarios de negocio;
7. validar el indicador con especialistas.

---

# 43. Uso responsable

El proyecto se desarrolla con fines académicos, experimentales y de investigación aplicada.

Los resultados:

- no constituyen recomendaciones de inversión;
- no determinan automáticamente que una empresa deba convertirse en emisor;
- no representan aprobación regulatoria;
- no sustituyen análisis financiero;
- no sustituyen análisis legal;
- no sustituyen análisis comercial;
- no deben utilizarse como único criterio para contactar o evaluar empresas;
- no deben interpretarse como probabilidades reales mientras no exista calibración.

El sistema se concibe como una herramienta de apoyo a especialistas.

---

# 44. Herramientas y entorno tecnológico

| Herramienta | Versión / uso |
|---|---|
| Python | 3.13.7 |
| pandas | 3.0.5 |
| NumPy | 2.5.3 |
| scikit-learn | 1.9.1 |
| SciPy | 1.18.1 |
| Matplotlib | 3.11.1 |
| joblib | 1.6.0 |
| openpyxl | 3.1.5 |
| Jupyter | 1.1.1 |
| Git | Control de versiones |
| GitHub | Repositorio remoto privado |
| Visual Studio Code | Desarrollo |
| PowerShell | Ejecución y administración |

Las dependencias se mantienen en:

- `requirements.txt`
- `requirements-lock.txt`

---

# 45. Estructura general del repositorio

- `config/` — reglas de configuración y homologación.
- `data/raw/` — archivos originales.
- `data/interim/` — datos intermedios.
- `data/processed/` — datasets derivados para modelado; excluidos de Git salvo `.gitkeep`.
- `docs/` — documentación técnica y académica.
- `models/` — modelos generados localmente.
- `notebooks/` — exploración y validaciones.
- `reports/figures/` — visualizaciones.
- `reports/results/` — resultados agregados.
- `scripts/` — scripts reproducibles de construcción de datasets, incluido `build_v10_base.py`.
- `src/data/` — construcción y validación de datos del ciclo inicial.
- `src/features/` — ingeniería de variables.
- `src/models/` — entrenamiento de modelos.
- `src/evaluation/` — evaluación, backtesting y comparación.
- `README.md` — visión general y estado actual.
- `requirements.txt` — dependencias.
- `requirements-lock.txt` — versiones exactas del entorno.

---

# 46. Reproducción del entorno

Desde PowerShell y la carpeta raíz del proyecto:

`.\.venv\Scripts\Activate.ps1`

Verificar:

`python --version`

Instalar dependencias cuando corresponda:

`pip install -r requirements.txt`

Las versiones exactas utilizadas se encuentran en:

`requirements-lock.txt`

---

# 47. Pipeline de datos

## 47.1 Ciclo v1–v9

Construir dataset armonizado:

`python src/data/build_scvs_harmonized_dataset.py`

Validar homologación:

`python src/data/validate_scvs_harmonized_dataset.py`

Construir dataset etiquetado:

`python src/data/build_mvp_labeled_dataset.py`

La lógica versionada de este ciclo debe respetar la metodología temporal corregida documentada en el README y en la bitácora.

## 47.2 Base integrada v10

Reconstruir la base congelada v10:

`python scripts/build_v10_base.py`

Salida local:

`data/processed/v10_base_integrated_2012_2023.csv.gz`

El script contiene asserts de control sobre:

- tamaño del universo;
- duplicados;
- número de positivos;
- RUC positivos únicos;
- cantidad de RUC del target;
- reproducibilidad mediante SHA-256.

Hash esperado:

`b44f9ccf309c20a59be436953a0c6e7f9a3dc1f11cc6f2c87e41c1676a3a2a8d`

---

# 48. Ejecución de v6

Entrenar la regresión logística con variables temporales:

`python src/models/train_logistic_temporal_features_v6.py`

Ejecutar el backtest temporal:

`python src/evaluation/backtest_logistic_v6.py`

---

# 49. Backtest de v8

Ejecutar:

`python src/evaluation/backtest_hist_gradient_boosting_v8.py`

El script utiliza exclusivamente información hasta 2020 dentro del ciclo de backtesting.

TEST 2022–2023 permanece fuera de esta evaluación.

---

# 50. Comparación v6 vs v8

Ejecutar:

`python src/evaluation/compare_v6_v8_backtests.py`

El proceso valida primero que ambos experimentos utilicen:

- los mismos folds;
- los mismos períodos de entrenamiento;
- el mismo año de evaluación;
- el mismo número de observaciones;
- el mismo número de positivos.

Luego genera las tablas comparativas.

---

# 51. Resultados versionados

Los resultados agregados utilizados para el análisis se encuentran en:

`reports/results/`

Entre los resultados actualmente versionados se encuentran los correspondientes al backtest de v6, backtest de v8 y comparación entre ambos modelos.

## Backtest v6

- `backtest_logistic_v6_metrics.csv`
- `backtest_logistic_v6_ranking_metrics.csv`
- `backtest_logistic_v6_summary.csv`
- `backtest_logistic_v6_metadata.json`

## Comparación v6 vs v8

- `comparison_v6_v8_metrics_by_year.csv`
- `comparison_v6_v8_ranking_by_year.csv`
- `comparison_v6_v8_stability_summary.csv`
- `comparison_v6_v8_model_summary.csv`
- `comparison_v6_v8_metadata.json`

Los datasets completos y los modelos binarios reconstruibles permanecen fuera de Git.

---

# 52. Reproducibilidad

El proyecto utiliza:

- Git para control de versiones;
- GitHub como repositorio remoto;
- scripts separados por etapa;
- entorno virtual;
- `requirements.txt`;
- `requirements-lock.txt`;
- resultados agregados versionados;
- metadata de experimentos;
- documentación técnica;
- bitácora;
- backlog;
- diccionario de datos;
- inventario de fuentes.

Se utiliza `random_state = 42` en procesos donde es aplicable.

Para v10 se añadió una validación adicional de reproducibilidad:

- script: `scripts/build_v10_base.py`;
- dataset local: `data/processed/v10_base_integrated_2012_2023.csv.gz`;
- SHA-256 congelado: `b44f9ccf309c20a59be436953a0c6e7f9a3dc1f11cc6f2c87e41c1676a3a2a8d`.

La reconstrucción desde las mismas fuentes produjo un archivo binariamente idéntico al previamente validado.

---

# 53. Principales commits del ciclo actual

| Commit | Hito |
|---|---|
| `69d29da` | Corrección temporal del target y experimentos v4–v5 |
| `c44f24e` | Variables temporales y v6 |
| `1c6555c` | HistGradientBoosting v7 |
| `d81bbfa` | HistGradientBoosting regularizado v8 |
| `0565ead` | Backtest temporal v8 |
| `1ae9531` | MLP v9 |
| `c6fadce` | Backtest temporal v6 |
| `99a8ca0` | Comparación temporal automatizada v6 vs v8 |

El historial completo se mantiene en Git.

---

# 54. Documentación disponible

| Documento | Propósito |
|---|---|
| `README.md` | Punto de entrada y estado actual |
| `docs/pipeline_datos_mvp.md` | Pipeline de datos |
| `docs/inventario_fuentes.md` | Fuentes de información |
| `docs/diccionario_datos.md` | Variables y transformaciones |
| `docs/entorno_tecnico.md` | Entorno y dependencias |
| `docs/baseline_v1.md` | Baseline histórico v1 |
| `docs/baseline_v2.md` | Experimento histórico v2 |
| `docs/baseline_v3.md` | Experimento histórico v3 |
| `docs/bitacora.md` | Evolución técnica y metodológica |
| `docs/backlog.md` | Actividades pendientes y completadas |
| `docs/informe_resultados_preliminares.md` | Informe académico consolidado |
| `docs/v10_dataset_freeze.md` | Congelamiento del universo, target e integración de fuentes v10 |

---

# 55. Estado actual del proyecto

| Componente | Estado |
|---|---|
| Estructura del repositorio | Completada |
| Entorno técnico | Documentado |
| Inventario inicial de fuentes | Completado |
| Diccionario de datos | Completado para ciclo v1–v9; actualización v10 pendiente |
| Homologación contable 2015–2023 | Completada |
| Dataset armonizado histórico | Completado |
| Validaciones contables históricas | Completadas |
| Target temporal corregido v4–v9 | Completado |
| Regla de disponibilidad | Implementada como supuesto normativo |
| División con embargos v4–v9 | Completada |
| Variables temporales v6–v9 | Completadas |
| Logistic Regression v6 | Completada |
| HistGradientBoosting v7 | Completado |
| HistGradientBoosting v8 | Completado |
| MLP v9 | Completado como experimento exploratorio |
| Backtest v6 | Completado |
| Backtest v8 | Completado |
| Comparación v6 vs v8 | Completada |
| Benchmark del ciclo anterior | v8 |
| TEST temporal v4–v9 | Reservado |
| Auditoría de nuevas fuentes | Completada para congelamiento base v10 |
| Universo y target v10 | **Congelados** |
| Base integrada v10 2012–2023 | **Construida y reproducible** |
| SHA-256 v10 | **Validado** |
| Feature Set v10 | Pendiente |
| Split temporal v10 | Pendiente de definición y congelamiento |
| `v10-LR` | Pendiente |
| `v10-HGB` | Pendiente |
| Random Forest v10 | Pendiente |
| CatBoost v10 | Pendiente |
| TensorFlow/Keras v10 | Pendiente |
| Interpretabilidad SHAP | Pendiente |
| Calibración | Pendiente |
| Evaluación ampliada de sesgo | Pendiente |
| Índice de Afinidad Bursátil | Pendiente |
| Prototipo web | Pendiente |
| MLOps / monitoreo | Pendiente |

---

# 56. Próxima fase

Con el universo y target v10 ya congelados, la siguiente fase se orientará a:

1. actualizar documentación general y registrar el congelamiento en Git;
2. mantener íntegramente preservado el ciclo v1–v9;
3. construir el **Feature Set v10** sin modificar el universo congelado;
4. clasificar columnas entre predictores, identificadores, auditoría y variables no utilizables;
5. definir reglas de missingness;
6. incorporar variables temporales `t-1` y otras trayectorias disponibles;
7. definir transformaciones y tratamiento de valores extremos aprendidos únicamente sobre TRAIN cuando corresponda;
8. definir y congelar la nueva estrategia temporal TRAIN / embargo / VALIDATION / TEST;
9. mantener el TEST v10 cerrado durante selección y ajuste;
10. entrenar `v10-LR` como baseline de la nueva generación;
11. evaluar `v10-HGB`;
12. evaluar Random Forest;
13. evaluar CatBoost;
14. implementar una red TensorFlow/Keras;
15. comparar las familias de modelos bajo un protocolo temporal común;
16. incorporar interpretabilidad mediante SHAP;
17. evaluar sesgos y comportamiento segmentado;
18. estudiar calibración cuando corresponda;
19. construir posteriormente el Índice de Afinidad Bursátil;
20. desarrollar el prototipo web de apoyo a la prospección.

El primer entrenamiento v10 no se realizará hasta completar el feature set y congelar el nuevo protocolo temporal.

---

# 57. Estado del benchmark

A octubre de 2026, y mientras todavía no existen modelos entrenados sobre el nuevo universo v10:

**Benchmark histórico del ciclo v4–v9: v8 — HistGradientBoosting regularizado**

**Baseline comparable del ciclo v4–v9: v6 — Logistic Regression con variables temporales**

La comparación rolling-origin del ciclo anterior muestra:

- PR-AUC promedio v6: **0,011329**
- PR-AUC promedio v8: **0,021041**
- diferencia relativa promedio observada: **+85,73 %**
- Lift@50 promedio v6: **65,15**
- Lift@50 promedio v8: **123,64**

Estos resultados corresponden exclusivamente a las ventanas temporales de desarrollo 2018, 2019 y 2020 del universo v4–v9.

No deben trasladarse directamente al nuevo dataset v10.

v8 permanece como referencia histórica hasta que exista una comparación reproducible entre modelos entrenados y evaluados bajo el protocolo v10.

El TEST temporalmente corregido 2022–2023 del ciclo v4–v9 permanece reservado.

---

# 58. Conclusión del ciclo actual

El desarrollo realizado hasta v9 estableció una base metodológica reproducible para Prospect Finder BVQ mediante una definición temporal conservadora, exclusión de emisores previos, períodos de embargo, variables temporales, modelos lineales y no lineales, backtesting rolling-origin y preservación del conjunto TEST.

El ciclo posterior de auditoría de datos permitió avanzar a una nueva generación v10.

El principal hito actual es el congelamiento de una base integrada 2012–2023 con:

- 1.030.671 observaciones elegibles;
- 568 positivos;
- 310 RUC positivos únicos;
- 0 duplicados empresa-año;
- reglas explícitas de identidad;
- validación del target;
- reglas documentadas de precedencia y fallback entre fuentes;
- exclusión de observaciones sin identidad verificable;
- variables de auditoría para mantener trazabilidad;
- un script reproducible de construcción;
- un SHA-256 validado mediante reconstrucción independiente.

El archivo congelado es:

`data/processed/v10_base_integrated_2012_2023.csv.gz`

con SHA-256:

`b44f9ccf309c20a59be436953a0c6e7f9a3dc1f11cc6f2c87e41c1676a3a2a8d`

Este congelamiento no significa que el modelo v10 esté construido.

El siguiente trabajo se concentra en definir el feature set, las transformaciones y la nueva estrategia de validación temporal antes de entrenar cualquier modelo.

Los resultados v6 y v8 permanecen como referencia histórica y no se compararán directamente con futuros modelos v10 sin reconocer el cambio de universo.

Prospect Finder BVQ se mantiene como una herramienta de apoyo a la priorización y al análisis humano, no como un mecanismo autónomo de decisión.
