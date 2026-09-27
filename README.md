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

## 4.1 Superintendencia de Compañías, Valores y Seguros — Estados financieros

Es la fuente principal utilizada actualmente para construir las variables predictoras.

**Período utilizado en el ciclo v1–v9:**

2015–2023.

La información incluye:

- estados financieros;
- cuentas contables;
- información financiera histórica por empresa;
- identificación empresarial;
- clasificación CIIU.

Los archivos originales se conservan localmente en:

`data/raw/scvs/estados_financieros/`

Los archivos originales no se almacenan en Git.

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

# 6. Dataset financiero armonizado

El proceso de homologación produjo:

| Indicador | Resultado |
|---|---:|
| Observaciones empresa-año | 887.469 |
| Empresas únicas | 166.389 |
| Período | 2015–2023 |

Archivo generado localmente:

`data/interim/scvs_financials_harmonized_2015_2023.csv.gz`

Este archivo no se almacena en Git.

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

# 10. Dataset etiquetado temporalmente corregido

Después de aplicar la nueva regla temporal y excluir observaciones de empresas que ya eran emisoras antes de la fecha de decisión se obtuvo:

| Indicador | Resultado |
|---|---:|
| Observaciones financieras originales | 887.469 |
| Empresas en dataset armonizado | 166.389 |
| Emisores históricos identificados | 619 |
| Observaciones ya emisoras antes de la decisión | 3.481 |
| Observaciones elegibles | **883.988** |
| `TARGET_24M = 1` | **423** |
| Prevalencia positiva aproximada | **0,0479 %** |

El problema presenta un desbalance de clases extremo.

---

# 11. Distribución temporal del target corregido

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

Por esta razón la evaluación debe considerar explícitamente la estabilidad temporal.

---

# 12. División temporal actual

No se utiliza una partición aleatoria como mecanismo principal de validación.

La metodología corregida utiliza:

| Conjunto | Período | Observaciones | Positivos |
|---|---|---:|---:|
| TRAIN | 2015–2018 | 324.055 | 262 |
| EMBARGO VALIDATION | 2019 | 91.932 | 34 |
| VALIDATION | 2020 | 98.470 | 34 |
| EMBARGO TEST | 2021 | 109.095 | 39 |
| TEST | 2022–2023 | 260.436 | 54 |

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

# 14. Estado del conjunto TEST

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

# 18. Evolución experimental

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

# 37. Benchmark actual

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

# 38. Baseline comparable actual

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
| Comparaciones injustas | Mismo protocolo para v6 y v8 |
| Complejidad excesiva | Mantener baseline lineal |
| Contaminación de TEST | TEST 2022–2023 reservado |
| Interpretación causal | Resultados interpretados como asociaciones predictivas |
| Automatización de decisiones | Human-in-the-loop |

---

# 40. Limitaciones actuales

Las principales limitaciones son:

1. Solo existen 423 positivos en el dataset temporalmente corregido.
2. TRAIN 2015–2018 contiene 262 positivos.
3. VALIDATION 2020 contiene únicamente 34 positivos.
4. TEST 2022–2023 contiene 54 positivos y permanece reservado.
5. Existe un desbalance extremo.
6. El rendimiento varía entre cohortes temporales.
7. Solo se dispone actualmente de tres folds rolling-origin.
8. La regla de disponibilidad es una aproximación normativa y no una fecha individual observada.
9. Las variables actuales siguen concentrándose principalmente en información financiera.
10. Las tendencias multianuales pueden ampliarse.
11. CatBoost todavía debe evaluarse.
12. Random Forest todavía debe evaluarse.
13. Debe implementarse una red TensorFlow/Keras para cumplir la etapa neuronal prevista en el proyecto.
14. Los scores no están calibrados.
15. El Índice de Afinidad Bursátil todavía no está definido de manera definitiva.
16. Falta incorporar interpretabilidad mediante técnicas como SHAP.
17. Falta ampliar la evaluación explícita de sesgo y equidad.
18. Las nuevas fuentes identificadas todavía no han ingresado al feature set v1–v9.
19. El prototipo web funcional todavía está pendiente.
20. El TEST debe mantenerse cerrado mientras continúe la selección de modelos.

---

# 41. Estado de nuevas fuentes

Se han identificado nuevas fuentes potenciales de información para ampliar el modelo.

Estas fuentes no se incorporarán retroactivamente a v1–v9.

Su integración dará origen a una nueva generación de datos y features.

La nomenclatura prevista es:

**Dataset / Feature Set v10**

Dentro de esa generación podrán evaluarse, por ejemplo:

- `v10-LR`;
- `v10-HGB`;
- `v10-RF`;
- `v10-CatBoost`;
- `v10-NN`.

v8 permanecerá como benchmark del ciclo anterior.

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
- `data/processed/` — datasets derivados para modelado.
- `docs/` — documentación técnica y académica.
- `models/` — modelos generados localmente.
- `notebooks/` — exploración y validaciones.
- `reports/figures/` — visualizaciones.
- `reports/results/` — resultados agregados.
- `src/data/` — construcción y validación de datos.
- `src/features/` — ingeniería de variables.
- `src/models/` — entrenamiento de modelos.
- `src/evaluation/` — evaluación, backtesting y comparación.
- `README.md` — visión general del proyecto.
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

# 47. Pipeline base de datos

Construir dataset armonizado:

`python src/data/build_scvs_harmonized_dataset.py`

Validar homologación:

`python src/data/validate_scvs_harmonized_dataset.py`

Construir dataset etiquetado:

`python src/data/build_mvp_labeled_dataset.py`

La lógica actualmente versionada debe respetar la metodología temporal corregida documentada en este README y en la bitácora.

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

---

# 55. Estado actual del proyecto

| Componente | Estado |
|---|---|
| Estructura del repositorio | Completada |
| Entorno técnico | Documentado |
| Inventario inicial de fuentes | Completado |
| Diccionario de datos | Completado para ciclo actual |
| Homologación contable 2015–2023 | Completada |
| Dataset armonizado | Completado |
| Validaciones contables | Completadas |
| Target temporal corregido | Completado |
| Regla de disponibilidad | Implementada como supuesto normativo |
| División con embargos | Completada |
| Variables temporales | Completadas para v6–v9 |
| Logistic Regression v6 | Completada |
| HistGradientBoosting v7 | Completado |
| HistGradientBoosting v8 | Completado |
| MLP v9 | Completado como experimento exploratorio |
| Backtest v6 | Completado |
| Backtest v8 | Completado |
| Comparación v6 vs v8 | Completada |
| Benchmark actual | v8 |
| TEST temporal corregido | Reservado |
| CatBoost | Pendiente |
| Random Forest | Pendiente |
| TensorFlow/Keras | Pendiente |
| Interpretabilidad SHAP | Pendiente |
| Calibración | Pendiente |
| Evaluación ampliada de sesgo | Pendiente |
| Dataset / Feature Set v10 | Siguiente ciclo |
| Índice de Afinidad Bursátil | Pendiente |
| Prototipo web | Pendiente |
| MLOps / monitoreo | Pendiente |

---

# 56. Próxima fase

El siguiente ciclo del proyecto se orientará a:

1. cerrar documentalmente el ciclo v1–v9;
2. mantener TEST 2022–2023 reservado;
3. incorporar nuevas fuentes mediante una nueva generación de dataset;
4. construir Dataset / Feature Set v10;
5. ampliar variables financieras, empresariales y temporales;
6. entrenar un nuevo baseline `v10-LR`;
7. evaluar `v10-HGB`;
8. evaluar Random Forest;
9. evaluar CatBoost;
10. implementar una red TensorFlow/Keras;
11. comparar modelos bajo un protocolo temporal común;
12. incorporar interpretabilidad;
13. evaluar sesgos y comportamiento segmentado;
14. estudiar calibración;
15. construir posteriormente el IAB;
16. desarrollar el prototipo web de apoyo a prospección.

---

# 57. Estado del benchmark

A septiembre de 2026:

**Benchmark actual: v8 — HistGradientBoosting regularizado**

**Baseline comparable: v6 — Logistic Regression con variables temporales**

La comparación rolling-origin muestra:

- PR-AUC promedio v6: **0,011329**
- PR-AUC promedio v8: **0,021041**
- mejora relativa promedio observada: **+85,73 %**
- Lift@50 promedio v6: **65,15**
- Lift@50 promedio v8: **123,64**

Estos resultados son preliminares y corresponden exclusivamente a las ventanas temporales de desarrollo 2018, 2019 y 2020.

El TEST temporalmente corregido 2022–2023 permanece reservado.

---

# 58. Conclusión del ciclo actual

El desarrollo realizado hasta v9 permite establecer una base metodológica reproducible para el proyecto Prospect Finder BVQ.

El principal avance no consiste únicamente en obtener un modelo con mejores métricas, sino en fortalecer progresivamente el diseño experimental mediante:

- una definición temporal más conservadora;
- exclusión de empresas previamente emisoras;
- períodos de embargo;
- variables temporales;
- comparación entre modelos lineales y no lineales;
- detección y corrección de sobreajuste;
- backtesting rolling-origin;
- análisis de variabilidad;
- comparación reproducible bajo protocolos equivalentes;
- preservación de un TEST final no utilizado durante la selección.

Los resultados actuales indican que v8 presenta una mayor capacidad de priorización que v6 dentro de las tres ventanas temporales evaluadas.

No obstante, el modelo todavía se encuentra en fase experimental.

El proyecto continuará incorporando nuevas fuentes, nuevas familias de modelos, interpretabilidad, evaluación de sesgos y mecanismos de validación antes de considerar el sistema suficientemente maduro para una utilización operativa.

Prospect Finder BVQ se mantiene como una herramienta de apoyo al análisis humano y no como un mecanismo autónomo de decisión.
