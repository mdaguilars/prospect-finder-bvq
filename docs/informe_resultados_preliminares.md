# Informe de ajustes al prototipo, validación y resultados preliminares — Prospect Finder BVQ

## UNIVERSIDAD DE LAS AMÉRICAS

### Maestría en Inteligencia Artificial

**Proyecto:** Sistema inteligente basado en aprendizaje automático y redes neuronales para identificar y priorizar empresas con potencial de convertirse en emisores del mercado de valores ecuatoriano para la Bolsa de Valores Quito

**Integrantes:**

- Marcelo David Aguilar Salguero
- Francisco Xavier Meneses Játiva
- Luis Miguel Gallardo Dávila

**Fecha:** Octubre de 2026

---

# 1. Descripción del prototipo desarrollado

Prospect Finder BVQ es un proyecto de inteligencia artificial orientado a apoyar el proceso de prospección de potenciales emisores para la Bolsa de Valores Quito (BVQ).

El problema organizacional identificado es la dificultad para analizar de manera sistemática un universo amplio de empresas ecuatorianas, aplicar criterios homogéneos de evaluación y priorizar aquellas que podrían presentar mayor afinidad con el mercado de valores.

La propuesta consiste en desarrollar un sistema capaz de analizar información financiera histórica y generar un ranking de empresas que permita reducir el universo inicial de revisión y orientar el trabajo posterior de especialistas.

El sistema no pretende determinar automáticamente qué empresa debe convertirse en emisor ni sustituir los análisis:

- financieros;
- comerciales;
- legales;
- regulatorios.

Su función es servir como herramienta de apoyo para la priorización.

La unidad de análisis es:

`empresa-año`

La variable objetivo es:

`TARGET_24M`

donde:

- `1`: la empresa se registra por primera vez como emisor dentro de los siguientes 24 meses a partir de la fecha de decisión;
- `0`: la empresa no se registra como nuevo emisor dentro de ese horizonte.

Las empresas que ya habían sido emisoras antes de la fecha de decisión correspondiente se excluyen del universo elegible.

---

# 2. Fuentes de información

## 2.1 Estados financieros y fuentes societarias de la SCVS

La fuente principal para construir variables predictoras continúa siendo la información publicada por la Superintendencia de Compañías, Valores y Seguros.

Para el ciclo experimental histórico v1–v9 se utilizó principalmente información financiera armonizada correspondiente a:

**2015–2023**

Para la nueva generación v10 se amplió el período a:

**2012–2023**

y se incorporó una integración controlada entre:

- `bi_ranking`;
- `bi_compania`;
- catálogos de clasificación CIIU;
- segmento empresarial;
- dataset financiero histórico armonizado.

La base integrada v10 se construye de forma reproducible mediante:

`scripts/build_v10_base.py`

y se genera localmente como:

`data/processed/v10_base_integrated_2012_2023.csv.gz`

Los archivos originales se mantienen localmente dentro de la estructura de datos del proyecto y no se almacenan en GitHub.

---

## 2.2 Registro del Mercado de Valores

Para construir la variable objetivo se utiliza información histórica del Registro del Mercado de Valores de la SCVS.

Los principales archivos utilizados son:

- `listado_entes_65001_1789908466941.xlsx`
- `codigos_fichas_registrales_1789908530079.xlsx`

Se identificaron **619 RUC de emisores históricos** con información disponible en ambas fuentes.

La primera fecha de inscripción coincidió en los 619 casos contrastados.

La primera inscripción como emisor constituye el evento utilizado para construir `TARGET_24M`.

---

## 2.3 Información interna de la BVQ

El Data Warehouse de la Bolsa de Valores Quito se considera una fuente complementaria para:

- validación;
- análisis;
- enriquecimiento futuro.

La información interna no constituye actualmente la fuente principal del feature set utilizado en v1–v9.

Los datos institucionales de BVQ no se publican en el repositorio.

---

## 2.4 Condiciones de utilización

Las fuentes públicas utilizadas fueron obtenidas de los mecanismos institucionales de publicación de la SCVS.

Durante la revisión documental realizada no se identificó una licencia abierta específica que permita asumir una autorización irrestricta de redistribución de los archivos utilizados.

Por esta razón:

- se mantiene a la SCVS como fuente original;
- los archivos originales no se redistribuyen en GitHub;
- no se atribuye una licencia no publicada expresamente;
- cualquier publicación externa de datasets derivados deberá revisar previamente las condiciones institucionales, legales y normativas aplicables.

El detalle se mantiene en:

`docs/inventario_fuentes.md`

---

# 3. Homologación de información financiera

La información financiera de SCVS utiliza diferentes planes contables a lo largo del período analizado.

Durante la primera generación del dataset se analizaron:

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

Las reglas de homologación se mantienen separadas de la lógica del código mediante:

`config/scvs_account_mapping.csv`

El dataset financiero armonizado contiene:

| Indicador | Resultado |
|---|---:|
| Observaciones empresa-año | 887.469 |
| Empresas únicas | 166.389 |
| Período | 2015–2023 |

---

# 4. Variables financieras base

Se homologaron nueve variables financieras principales:

| Variable | Descripción |
|---|---|
| `ACTIVO_TOTAL` | Total de activos |
| `ACTIVO_CORRIENTE` | Total de activos corrientes |
| `EFECTIVO` | Efectivo y equivalentes |
| `PASIVO_TOTAL` | Total de pasivos |
| `PASIVO_CORRIENTE` | Total de pasivos corrientes |
| `PASIVO_NO_CORRIENTE` | Total de pasivos no corrientes |
| `PATRIMONIO` | Patrimonio |
| `CAPITAL` | Capital registrado |
| `UTILIDAD_NETA` | Resultado neto del ejercicio |

El diccionario completo se mantiene en:

`docs/diccionario_datos.md`

---

# 5. Validación contable

La homologación se verificó mediante ecuaciones contables básicas.

## 5.1 Activo = Pasivo + Patrimonio

El **99,24 %** de las observaciones presentó una diferencia relativa menor o igual al **0,01 %**.

## 5.2 Pasivo total = Pasivo corriente + Pasivo no corriente

El **99,31 %** presentó una diferencia relativa menor o igual al **0,01 %**.

Estas verificaciones constituyen controles de consistencia estructural del dataset, aunque no sustituyen una revisión contable individual de cada registro.

---

# 6. Revisión crítica de la disponibilidad temporal

Uno de los principales ajustes realizados durante esta etapa fue revisar la relación entre:

- ejercicio fiscal;
- disponibilidad de la información;
- fecha de decisión;
- evento futuro utilizado como target.

En el primer ciclo v1–v3 se utilizó el año fiscal como referencia temporal.

Posteriormente se identificó que esta aproximación podía resultar demasiado optimista porque un estado financiero correspondiente al año `t` no necesariamente se encontraba disponible el 31 de diciembre de ese mismo año.

Los archivos utilizados no contienen una fecha individual de publicación o presentación para cada observación.

Por esta razón se adoptó una regla temporal conservadora y reproducible.

---

# 7. Regla temporal corregida

Para cada ejercicio fiscal `t` se utiliza:

| Concepto | Regla |
|---|---|
| Ejercicio financiero | año `t` |
| Fecha ordinaria máxima de disponibilidad asumida | `30/04/t+1` |
| Fecha de decisión | `01/05/t+1` |
| Inicio del horizonte objetivo | `01/05/t+1` |
| Fin del horizonte de 24 meses | `30/04/t+3` |

Esta regla se utiliza como una **suposición normativa conservadora de disponibilidad**.

No representa la fecha efectiva individual de presentación de cada empresa.

Su finalidad es reducir el riesgo de utilizar información que no hubiera estado disponible en el momento hipotético de realizar la prospección.

---

# 8. Dataset etiquetado corregido — ciclo histórico v4–v9

Después de aplicar la metodología temporal corregida al dataset financiero armonizado 2015–2023 y excluir las observaciones correspondientes a empresas que ya eran emisoras antes de la fecha de decisión, el ciclo v4–v9 obtuvo:

| Indicador | Resultado |
|---|---:|
| Observaciones financieras originales | 887.469 |
| Empresas en dataset armonizado | 166.389 |
| Emisores históricos identificados | 619 |
| Observaciones ya emisoras antes de la decisión | 3.481 |
| Observaciones elegibles | **883.988** |
| Casos positivos | **423** |
| Prevalencia aproximada | **0,0479 %** |

Estos valores pertenecen exclusivamente al ciclo histórico v4–v9 y no representan el universo actual de v10.

La nueva generación v10 utiliza un universo ampliado y reglas adicionales de integración e identidad, documentadas posteriormente en este informe.

---

# 9. Distribución temporal del target — ciclo histórico v4–v9

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

La cantidad de casos positivos cambia entre períodos.

Esta variación hace necesario evaluar los modelos en más de una ventana temporal.

---

# 10. División temporal histórica v4–v9

No se utilizó una división aleatoria como mecanismo principal de validación.

Para el ciclo histórico v4–v9 se utilizó:

| Conjunto | Período | Observaciones | Positivos |
|---|---|---:|---:|
| TRAIN | 2015–2018 | 324.055 | 262 |
| EMBARGO VALIDATION | 2019 | 91.932 | 34 |
| VALIDATION | 2020 | 98.470 | 34 |
| EMBARGO TEST | 2021 | 109.095 | 39 |
| TEST | 2022–2023 | 260.436 | 54 |

Esta división continúa siendo evidencia válida del ciclo v4–v9.

**No debe asumirse automáticamente como el split de v10.**

La generación v10 deberá definir y congelar su propio protocolo temporal antes de entrenar modelos.

---

# 11. Justificación de los períodos de embargo

El horizonte objetivo utilizado es de 24 meses.

Por esta razón, utilizar períodos inmediatamente consecutivos entre entrenamiento y evaluación puede provocar que las ventanas futuras utilizadas para construir `TARGET_24M` se superpongan.

Para reducir este riesgo se incorporaron períodos de embargo.

La secuencia metodológica es:

| Etapa | Período |
|---|---|
| TRAIN | 2015–2018 |
| EMBARGO | 2019 |
| VALIDATION | 2020 |
| EMBARGO | 2021 |
| TEST | 2022–2023 |

Los períodos de embargo no se utilizan para medir el desempeño principal.

---

# 12. Uso del conjunto TEST

Es necesario distinguir entre tres estados metodológicos.

## 12.1 Ciclo histórico v1–v3

El Baseline v1 fue evaluado sobre TEST 2022–2023 utilizando la primera metodología temporal.

Ese resultado se conserva como parte de la historia experimental.

## 12.2 Ciclo temporal corregido v4–v9

Después de reconstruir:

- target;
- elegibilidad;
- fecha de decisión;
- división temporal;
- períodos de embargo;

se obtuvo un nuevo conjunto TEST 2022–2023.

Este conjunto contiene:

- **260.436 observaciones**;
- **54 positivos**.

Este TEST no fue utilizado para seleccionar:

- v4;
- v5;
- v6;
- v7;
- v8;
- v9.

Permanece reservado como evidencia del ciclo v4–v9.

## 12.3 Generación v10

La base integrada v10 utiliza un universo diferente, ampliado a 2012–2023.

Por esta razón, todavía **no existe un TEST v10 abierto ni evaluado**.

Antes del primer entrenamiento v10 deberá definirse y congelarse un nuevo protocolo temporal que especifique:

- TRAIN;
- embargo de validación;
- VALIDATION;
- embargo de TEST;
- TEST final.

El TEST final de v10 deberá permanecer cerrado durante la selección de variables, modelos e hiperparámetros.

---

# 12A. Dataset base v10 congelado

La nueva generación de datos ya fue construida, auditada y congelada.

Archivo:

`data/processed/v10_base_integrated_2012_2023.csv.gz`

Script reproducible:

`scripts/build_v10_base.py`

Documento de congelamiento:

`docs/v10_dataset_freeze.md`

SHA-256 validado:

`b44f9ccf309c20a59be436953a0c6e7f9a3dc1f11cc6f2c87e41c1676a3a2a8d`

## 12A.1 Universo final

La integración inicial produjo:

- **1.035.294** observaciones empresa-año antes de aplicar las reglas finales de identidad y elegibilidad.

Después de resolver identidad y excluir observaciones no utilizables:

- **535** filas sin RUC verificable fueron excluidas;
- corresponden a **276 expedientes**;
- **4.088** observaciones de empresas que ya eran emisoras antes de la fecha de decisión fueron excluidas.

El universo final congelado contiene:

- **1.030.671 observaciones elegibles**;
- **568 positivos**;
- **310 RUC positivos únicos**;
- **0 duplicados empresa-año**;
- prevalencia positiva de **0,055110 %**.

## 12A.2 Procedencia del universo

Dentro del universo elegible final:

- `AMBAS`: **815.331** observaciones;
- `SOLO_BI`: **146.683** observaciones;
- `SOLO_HISTORICO`: **68.657** observaciones.

## 12A.3 Validación del target

El target se construye a partir de la primera inscripción efectiva como emisor.

La validación cruzada entre listado de entes y fichas registrales confirmó:

- **619 RUC** efectivos comunes;
- **619 fechas coincidentes**;
- **0 diferencias de fecha**.

Se consideran como estados efectivos:

- `VIGENTE`;
- `CANCELADA`.

No se consideran positivos estados como:

- inscripción negada;
- ente creado;
- en proceso de inscripción.

## 12A.4 Reglas de integración financiera

Para activos y patrimonio se utiliza como fuente principal `bi_ranking`.

Cuando el bloque financiero básico BI está completamente en cero, se permite fallback histórico controlado.

Resultados:

- `activos_final`: **1.022.910** valores disponibles;
- `patrimonio_final`: **1.022.910** valores disponibles;
- cobertura aproximada de ambos: **99,25 %**;
- fallbacks históricos de activos: **92.640**;
- fallbacks históricos de patrimonio: **92.640**.

Para utilidad neta:

- se utiliza `utilidad_neta_final`;
- no se utiliza la utilidad histórica como fallback por diferencias de definición entre fuentes;
- valores disponibles: **930.270**;
- cobertura aproximada: **90,26 %**.

## 12A.5 Variables excluidas preventivamente

Se excluyen como predictores:

- `cia_imvalores`;
- `id_estado_financiero`;
- `posicion_general`.

Estas exclusiones responden a riesgo de leakage, naturaleza técnica o falta de justificación predictiva.

## 12A.6 Estado metodológico

Con v10 se encuentran congelados:

- universo;
- target;
- reglas de identidad;
- reglas de elegibilidad;
- reglas principales de integración.

Todavía **no** se encuentran congelados:

- feature set;
- transformaciones finales;
- variables temporales;
- protocolo TRAIN / VALIDATION / TEST;
- modelos v10.

Por esta razón no existen todavía resultados de `v10-LR`, `v10-HGB`, `v10-RF`, `v10-CatBoost` ni `v10-NN`.

---

# 13. Ingeniería inicial de variables

## 13.1 Transformaciones logarítmicas

Para reducir diferencias extremas de escala se utiliza la transformación:

`sign(x) × log(1 + |x|)`

sobre las variables monetarias principales.

Esta transformación permite conservar el signo de valores negativos.

---

## 13.2 Razones financieras

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

Cuando el denominador no permite calcular una razón válida, el resultado se mantiene como faltante para ser tratado posteriormente dentro del pipeline.

---

# 14. Ajuste 1 — Variables temporales

Una de las principales limitaciones del primer baseline era utilizar principalmente una fotografía financiera correspondiente a un solo ejercicio.

Por esta razón, en v6 se incorporaron variables relacionadas con el período anterior.

El feature set temporal contiene:

- 16 variables del período actual;
- 17 variables temporales;
- **33 variables numéricas en total**.

El objetivo fue representar no solamente el nivel financiero de una empresa, sino también parte de su trayectoria.

Archivo:

`data/processed/mvp_features_temporal_v6.csv.gz`

---

# 15. Ajuste 2 — Cambio de modelo

La regresión logística utilizada como referencia inicial representa principalmente relaciones lineales en el espacio transformado.

Se planteó que la afinidad con el mercado de valores podía depender de interacciones no lineales entre variables como:

- tamaño;
- endeudamiento;
- liquidez;
- rentabilidad;
- capital;
- cambios financieros.

Por esta razón se evaluó `HistGradientBoostingClassifier`.

---

# 16. Ajuste 3 — Regularización del modelo no lineal

La primera implementación de HistGradientBoosting, correspondiente a v7, presentó un fuerte sobreajuste.

TRAIN alcanzó:

**PR-AUC = 0,871232**

mientras que VALIDATION 2020 obtuvo:

**PR-AUC = 0,004980**

Esta diferencia evidenció que el modelo tenía demasiada capacidad para el número reducido de eventos positivos disponibles.

Para v8 se redujo la complejidad.

| Parámetro | v7 | v8 |
|---|---:|---:|
| `learning_rate` | 0,10 | 0,05 |
| `max_iter` | 100 | 150 |
| `max_leaf_nodes` | 31 | 7 |
| `max_depth` | sin límite explícito | 3 |
| `min_samples_leaf` | 20 | 100 |
| `l2_regularization` | 0 | 1,0 |

Se mantuvo ponderación de clases.

El propósito fue reducir la capacidad de memorizar TRAIN y mejorar la generalización temporal.

---

# 17. Ajuste 4 — Preprocesamiento según el modelo

Para la regresión logística v6 se utiliza:

- `SimpleImputer(strategy="median")`;
- `StandardScaler()`.

El preprocesamiento se ajusta exclusivamente con TRAIN dentro de cada experimento o fold.

Para HistGradientBoosting se aprovecha la capacidad del modelo para trabajar directamente con valores faltantes, evitando transformaciones innecesarias.

Esto permite adaptar el preprocesamiento a las características de cada familia de modelo sin utilizar información del conjunto de evaluación.

---

# 18. Ajuste 5 — Cambio del esquema de validación

Una única ventana de VALIDATION puede producir conclusiones frágiles, especialmente cuando existen pocos positivos.

Por esta razón se incorporó backtesting temporal rolling-origin.

Se definieron tres folds:

| Fold | TRAIN | EMBARGO | EVALUACIÓN |
|---|---|---|---|
| 1 | 2015–2016 | 2017 | 2018 |
| 2 | 2015–2017 | 2018 | 2019 |
| 3 | 2015–2018 | 2019 | 2020 |

Los años 2021–2023 permanecen fuera de estos backtests.

---

# 19. Evolución de los experimentos históricos v1–v9

El ciclo histórico documentado cuenta con nueve iteraciones principales. La generación v10 todavía no ha iniciado entrenamiento de modelos.

| Versión | Modelo / cambio principal | Metodología |
|---|---|---|
| v1 | Regresión logística con sector | Histórica |
| v2 | Regresión logística sin sector | Histórica |
| v3 | Ajuste de regularización logística | Histórica |
| v4 | Regresión logística con target temporal corregido | Corregida |
| v5 | Regresión logística sin sector | Corregida |
| v6 | Regresión logística + variables temporales | Corregida |
| v7 | HistGradientBoosting inicial | Corregida |
| v8 | HistGradientBoosting regularizado | Corregida |
| v9 | MLP | Corregida |

Los resultados de v1–v3 no se comparan directamente contra v4–v9 porque existe un cambio en:

- definición temporal;
- elegibilidad;
- target;
- divisiones del dataset.

---

# 20. Resultados históricos v1

Configuración principal:

- Logistic Regression;
- `C = 1.0`;
- `class_weight = balanced`;
- regularización L2;
- `solver = lbfgs`;
- `max_iter = 2000`;
- `random_state = 42`.

Resultados históricos:

| Conjunto | PR-AUC | ROC-AUC |
|---|---:|---:|
| TRAIN | 0,099413 | 0,946436 |
| VALIDATION | 0,031095 | 0,940593 |
| TEST | 0,007291 | 0,927740 |

Estos resultados fueron útiles para establecer la viabilidad inicial del pipeline, pero corresponden al protocolo anterior.

---

# 21. Experimentos históricos v2 y v3

## 21.1 v2 — Sin sector

En VALIDATION:

| Métrica | v1 | v2 |
|---|---:|---:|
| PR-AUC | 0,031095 | 0,024402 |
| ROC-AUC | 0,940593 | 0,961619 |
| Precision@50 | 0,1000 | 0,0800 |
| Recall@50 | 0,1190 | 0,0952 |

Eliminar `SECTOR_CIIU` no produjo una mejora en las métricas prioritarias del primer ciclo.

---

## 21.2 v3 — Regularización

Se evaluaron:

- `C = 0.001`
- `C = 0.01`
- `C = 0.1`
- `C = 1`
- `C = 10`

El mejor PR-AUC correspondió a:

`C = 10 → 0,031135`

frente a:

`C = 1 → 0,031095`

La diferencia absoluta fue:

**0,000040**

y no se observaron mejoras en Top 50, Top 100 o Top 200.

La modificación no se consideró material.

---

# 22. Resultados v4

v4 fue el primer experimento con la metodología temporal corregida.

Resultados en VALIDATION 2020:

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0,004570 |
| ROC-AUC | 0,920359 |
| Top 50 | 0 |
| Top 100 | 1 |
| Top 200 | 1 |

Los resultados son inferiores a los históricos de v1, pero no son directamente comparables debido al cambio de metodología.

---

# 23. Resultados v5

v5 eliminó `SECTOR_CIIU` bajo el nuevo protocolo.

Resultados en VALIDATION 2020:

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0,005311 |
| ROC-AUC | 0,924389 |
| Top 50 | 0 |
| Top 100 | 1 |
| Top 200 | 1 |

Se observó una mejora pequeña en PR-AUC respecto de v4.

Sin embargo, la concentración Top-K continuó siendo limitada.

---

# 24. Resultados v6

v6 incorporó las variables temporales y se mantiene como el baseline comparable de la etapa actual.

Resultados en VALIDATION 2020:

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0,005254 |
| ROC-AUC | 0,906290 |
| Top 50 | 1 |
| Top 100 | 1 |
| Top 200 | 1 |

La incorporación de variables temporales no produjo por sí sola una mejora importante en PR-AUC utilizando regresión logística.

Sin embargo, v6 es metodológicamente importante porque utiliza el mismo feature set posteriormente empleado por v8.

---

# 25. Resultados v7

v7 utilizó HistGradientBoosting con una configuración inicial de mayor capacidad.

Resultados:

| Métrica | Resultado |
|---|---:|
| TRAIN PR-AUC | 0,871232 |
| VALIDATION PR-AUC | 0,004980 |
| VALIDATION ROC-AUC | 0,816540 |
| Top 50 | 1 |
| Top 100 | 1 |
| Top 200 | 2 |

La gran diferencia entre TRAIN y VALIDATION evidencia sobreajuste.

v7 no se considera una alternativa adecuada para selección.

Su principal aporte fue identificar la necesidad de regularización.

---

# 26. Resultados v8

v8 utilizó HistGradientBoosting con una configuración considerablemente más regularizada.

Resultados en VALIDATION 2020:

| Métrica | Resultado |
|---|---:|
| PR-AUC | **0,011805** |
| ROC-AUC | **0,922378** |
| Top 50 | **2** |
| Top 100 | **3** |
| Top 200 | **4** |

Resultados de ranking:

| K | Positivos | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 2 | 0,0400 | 0,0588 | 115,85 |
| 100 | 3 | 0,0300 | 0,0882 | 86,89 |
| 200 | 4 | 0,0200 | 0,1176 | 57,92 |

v8 presenta actualmente el mejor desempeño observado bajo la metodología temporal corregida.

---

# 27. Resultados v9

v9 incorporó una primera alternativa mediante MLP.

Resultados en VALIDATION 2020:

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0,005262 |
| ROC-AUC | 0,848818 |
| Top 50 | 0 |
| Top 100 | 0 |
| Top 200 | 0 |

v9 no mejora el desempeño de v8.

El resultado muestra que incrementar la complejidad del algoritmo no implica necesariamente una mejor capacidad de generalización.

v9 se considera una primera experimentación neuronal.

La propuesta académica contempla una implementación con TensorFlow/Keras, por lo que todavía deberá desarrollarse una alternativa específica utilizando ese framework antes del cierre del proyecto.

---

# 28. Técnica de validación estadística

La técnica principal incorporada en esta etapa es:

**rolling-origin temporal con períodos de embargo**

Esta metodología permite que:

1. el entrenamiento utilice únicamente años anteriores;
2. exista un período de separación temporal;
3. la evaluación se realice sobre un período posterior;
4. el conjunto de entrenamiento crezca progresivamente.

Los tres folds son:

| Fold | TRAIN | EMBARGO | EVALUACIÓN |
|---|---|---|---|
| 1 | 2015–2016 | 2017 | 2018 |
| 2 | 2015–2017 | 2018 | 2019 |
| 3 | 2015–2018 | 2019 | 2020 |

Esta estrategia resulta más apropiada que una validación cruzada aleatoria para un problema donde el objetivo es utilizar información histórica para priorizar empresas en períodos futuros.

---

# 29. Backtest de v6

## 29.1 Año 2018

TRAIN:

- observaciones: 154.949;
- positivos: 114.

Evaluación:

- observaciones: 86.689;
- positivos: 59.

Resultados:

- PR-AUC: **0,015520**
- ROC-AUC: **0,897956**
- Precision: **0,002849**
- Recall: **0,847458**
- F1: **0,005680**

Ranking:

| K | Positivos | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 1 | 0,0200 | 0,0169 | 29,39 |
| 100 | 3 | 0,0300 | 0,0508 | 44,08 |
| 200 | 5 | 0,0250 | 0,0847 | 36,73 |

---

## 29.2 Año 2019

TRAIN:

- observaciones: 237.366;
- positivos: 203.

Evaluación:

- observaciones: 91.932;
- positivos: 34.

Resultados:

- PR-AUC: **0,013212**
- ROC-AUC: **0,918509**
- Precision: **0,001760**
- Recall: **0,852941**
- F1: **0,003513**

Ranking:

| K | Positivos | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 2 | 0,0400 | 0,0588 | 108,16 |
| 100 | 3 | 0,0300 | 0,0882 | 81,12 |
| 200 | 5 | 0,0250 | 0,1471 | 67,60 |

---

## 29.3 Año 2020

TRAIN:

- observaciones: 324.055;
- positivos: 262.

Evaluación:

- observaciones: 98.470;
- positivos: 34.

Resultados:

- PR-AUC: **0,005254**
- ROC-AUC: **0,906290**
- Precision: **0,001713**
- Recall: **0,794118**
- F1: **0,003419**

Ranking:

| K | Positivos | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 1 | 0,0200 | 0,0294 | 57,92 |
| 100 | 1 | 0,0100 | 0,0294 | 28,96 |
| 200 | 1 | 0,0050 | 0,0294 | 14,48 |

---

# 30. Estabilidad temporal de v6

PR-AUC de los tres folds:

- 2018: 0,015520;
- 2019: 0,013212;
- 2020: 0,005254.

Resumen:

| Estadístico | Resultado |
|---|---:|
| Media | 0,011329 |
| Mediana | 0,013212 |
| Desviación estándar muestral | 0,005386 |
| Mínimo | 0,005254 |
| Máximo | 0,015520 |

Lift@50 promedio:

**65,15**

Los resultados muestran variabilidad entre períodos, particularmente en 2020.

---

# 31. Backtest de v8

## 31.1 Año 2018

Resultados:

- positivos en evaluación: 59;
- PR-AUC: **0,034551**;
- ROC-AUC: **0,884906**;
- positivos Top 50: **5**;
- Lift@50: **146,93**.

---

## 31.2 Año 2019

Resultados:

- positivos en evaluación: 34;
- PR-AUC: **0,016766**;
- ROC-AUC: **0,938953**;
- positivos Top 50: **2**;
- Lift@50: **108,16**.

---

## 31.3 Año 2020

Resultados:

- positivos en evaluación: 34;
- PR-AUC: **0,011805**;
- ROC-AUC: **0,922378**;
- positivos Top 50: **2**;
- Lift@50: **115,85**.

---

# 32. Estabilidad temporal de v8

PR-AUC:

- 2018: 0,034551;
- 2019: 0,016766;
- 2020: 0,011805.

Resumen:

| Estadístico | Resultado |
|---|---:|
| Media | 0,021041 |
| Mediana | 0,016766 |
| Desviación estándar muestral | 0,011960 |
| Mínimo | 0,011805 |
| Máximo | 0,034551 |

ROC-AUC:

| Estadístico | Resultado |
|---|---:|
| Media aproximada | 0,915412 |
| Mediana | 0,922378 |
| Desviación estándar muestral aproximada | 0,027689 |

Lift@50:

| Estadístico | Resultado |
|---|---:|
| Media | 123,64 |
| Mediana | 115,85 |
| Mínimo | 108,16 |
| Máximo | 146,93 |

---

# 33. Comparación justa entre baseline y modelo ajustado

Para esta entrega, la comparación principal no se realiza entre v1 y v8.

v1 pertenece a una metodología temporal anterior.

La comparación metodológicamente más justa es:

**v6 vs v8**

porque ambos utilizan:

- el mismo dataset temporal;
- las mismas 33 variables;
- los mismos folds;
- los mismos años de entrenamiento;
- los mismos embargos;
- los mismos universos de evaluación;
- las mismas métricas.

La principal diferencia evaluada es la familia de modelo:

- v6: Logistic Regression;
- v8: HistGradientBoosting regularizado.

---

# 34. Comparación PR-AUC v6 vs v8

| Año | v6 | v8 | Diferencia absoluta |
|---:|---:|---:|---:|
| 2018 | 0,015520 | 0,034551 | +0,019031 |
| 2019 | 0,013212 | 0,016766 | +0,003554 |
| 2020 | 0,005254 | 0,011805 | +0,006550 |

Cambio relativo observado:

| Año | Cambio relativo |
|---:|---:|
| 2018 | +122,62 % |
| 2019 | +26,90 % |
| 2020 | +124,67 % |

v8 obtiene mayor PR-AUC en los tres años evaluados.

---

# 35. Comparación agregada v6 vs v8

| Métrica | v6 | v8 |
|---|---:|---:|
| PR-AUC promedio | 0,011329 | **0,021041** |
| PR-AUC mediano | 0,013212 | **0,016766** |
| Desviación estándar PR-AUC | **0,005386** | 0,011960 |
| Lift@50 promedio | 65,15 | **123,64** |

La mejora relativa observada en PR-AUC promedio es:

**+85,73 %**

La mejora relativa observada en Lift@50 promedio es:

**+89,77 %**

---

# 36. Interpretación de la variabilidad

v6 presenta una desviación estándar del PR-AUC menor que v8.

Esto significa que sus resultados presentan menor dispersión entre los tres folds evaluados.

Sin embargo, esa menor dispersión ocurre alrededor de un nivel promedio de rendimiento inferior.

Por esta razón no sería correcto concluir que v6 es superior únicamente por presentar menor desviación estándar.

La evaluación debe considerar conjuntamente:

- nivel promedio de desempeño;
- mediana;
- variabilidad;
- comportamiento Top-K;
- consistencia entre años.

v8 presenta mayor variabilidad, pero también:

- mayor PR-AUC en los tres folds;
- mayor PR-AUC promedio;
- mayor Lift@50 promedio.

---

# 37. Interpretación de ROC-AUC

La comparación de ROC-AUC es más heterogénea.

En 2018:

**v6 > v8**

En 2019:

**v8 > v6**

En 2020:

**v8 > v6**

Por esta razón no se concluye que v8 sea superior en todas las métricas.

La principal evidencia favorable a v8 se encuentra en las métricas relacionadas con el objetivo real de priorización:

- PR-AUC;
- Top-K;
- Lift@K.

---

# 38. Incertidumbre y confianza en los resultados

El rolling-origin permite mejorar la evaluación de estabilidad frente a utilizar una sola ventana temporal.

Sin embargo, actualmente se dispone únicamente de:

**3 folds**

Por esta razón:

- las medias se interpretan de forma descriptiva;
- las medianas se interpretan de forma descriptiva;
- la desviación estándar se utiliza como medida descriptiva;
- los rangos muestran variación entre períodos;
- no se presentan intervalos formales de confianza;
- no se realizan afirmaciones de significancia estadística no sustentadas por el tamaño de la evaluación temporal.

Los resultados permiten afirmar que v8 mostró un comportamiento más favorable que v6 en las tres ventanas observadas para PR-AUC, pero todavía se requiere ampliar la evidencia antes de considerar definitivo el modelo.

---

# 39. Comparación de alternativas

| Modelo | PR-AUC VALIDATION 2020 | ROC-AUC | Top 50 | Interpretabilidad | Complejidad |
|---|---:|---:|---:|---|---|
| v6 Logistic Regression | 0,005254 | 0,906290 | 1 | Alta | Baja |
| v8 HistGradientBoosting | **0,011805** | **0,922378** | **2** | Media | Baja-media |
| v9 MLP | 0,005262 | 0,848818 | 0 | Menor | Media |

La regresión logística continúa siendo útil como baseline por su simplicidad e interpretabilidad.

HistGradientBoosting ofrece actualmente una mayor capacidad de priorización.

MLP no justifica todavía su mayor complejidad con los resultados obtenidos.

---

# 40. Benchmark histórico del ciclo v1–v9

Con la evidencia disponible del ciclo v1–v9 se mantiene:

**v8 — HistGradientBoosting regularizado**

como benchmark histórico de la metodología temporal corregida.

Esta decisión se sustentó en:

- mayor PR-AUC que v6 en 2018;
- mayor PR-AUC que v6 en 2019;
- mayor PR-AUC que v6 en 2020;
- mayor PR-AUC promedio;
- mayor Lift@50 promedio;
- mejor desempeño Top-K;
- menor sobreajuste que v7.

v8 no se considera el modelo definitivo del proyecto.

Tampoco se considera automáticamente benchmark de v10, porque la nueva generación utiliza un universo distinto.

El primer baseline de v10 deberá construirse con `v10-LR` una vez congelados el feature set y el nuevo protocolo temporal.

---

# 41. Criterio de éxito para futuras mejoras

Una nueva alternativa no deberá considerarse mejor por presentar una mejora mínima en una sola métrica.

Para considerar una mejora material se deberá evaluar al menos:

- PR-AUC promedio;
- PR-AUC por fold;
- Precision@K;
- Recall@K;
- Lift@K;
- variabilidad temporal;
- interpretabilidad;
- complejidad;
- riesgo de sesgo;
- reproducibilidad.

Para v10, las comparaciones deberán realizarse únicamente entre modelos entrenados sobre:

- el mismo dataset v10;
- el mismo feature set;
- los mismos folds;
- los mismos embargos;
- las mismas métricas;
- las mismas reglas de elegibilidad.

El primer punto de referencia será `v10-LR`.

El TEST final de v10 no deberá utilizarse para alcanzar estos criterios.

---

# 42. Riesgo de leakage temporal

## Riesgo

Utilizar una variable antes de que hubiera podido estar disponible en la fecha de decisión.

## Mitigación

- regla temporal `01/05/t+1`;
- construcción del target desde esa fecha;
- períodos de embargo;
- procesamiento ajustado exclusivamente con TRAIN.

---

# 43. Riesgo de sobreajuste

## Evidencia

v7 obtuvo un PR-AUC muy elevado en TRAIN y muy bajo en VALIDATION.

## Mitigación

En v8 se redujo:

- profundidad;
- número de hojas;
- velocidad de aprendizaje;
- flexibilidad de los nodos.

Además se incorporó:

- regularización L2;
- mayor mínimo de observaciones por hoja;
- backtesting temporal.

---

# 44. Riesgo de desbalance

El problema mantiene un desbalance extremo.

En el ciclo histórico v4–v9:

- positivos: **423**;
- observaciones elegibles: **883.988**;
- prevalencia aproximada: **0,0479 %**.

En la base integrada v10:

- positivos: **568**;
- observaciones elegibles: **1.030.671**;
- prevalencia aproximada: **0,055110 %**.

## Mitigaciones

- ponderación de clases cuando sea apropiado;
- PR-AUC como métrica central;
- Precision@K;
- Recall@K;
- Lift@K;
- análisis por ranking en lugar de depender de Accuracy;
- cualquier remuestreo deberá limitarse exclusivamente a TRAIN.

---

# 45. Riesgo de pocos eventos positivos

El número de casos positivos por año es reducido.

Por ejemplo:

- 2018: 59;
- 2019: 34;
- 2020: 34.

Esto provoca sensibilidad en las métricas.

## Mitigación

- múltiples ventanas temporales;
- reporte de media;
- mediana;
- desviación estándar;
- rango;
- interpretación prudente de resultados.

---

# 46. Riesgo de drift

La prevalencia y el comportamiento financiero pueden cambiar entre años.

## Mitigación actual

Se utiliza backtesting rolling-origin para observar la evolución del desempeño.

## Mitigación futura

Se deberán incorporar mecanismos para monitorear:

- distribución de variables;
- prevalencia;
- PR-AUC;
- Precision@K;
- Recall@K;
- Lift@K.

---

# 47. Riesgo de sesgo

Es posible que el modelo aprenda patrones asociados con:

- sector;
- tamaño;
- disponibilidad de información;
- representación histórica de ciertos tipos de empresas.

## Mitigaciones desarrolladas

Se realizaron experimentos:

- con sector;
- sin sector.

## Trabajo pendiente

La siguiente fase deberá evaluar desempeño segmentado por:

- sector;
- tamaño;
- localización cuando sea metodológicamente apropiado;
- otras categorías empresariales disponibles.

La finalidad será identificar si la priorización funciona de manera sistemáticamente distinta entre grupos.

---

# 48. Riesgo de comparación injusta entre modelos

Comparar modelos entrenados con diferentes:

- targets;
- variables;
- splits;
- universos;

puede llevar a conclusiones incorrectas.

## Mitigación

La comparación v6 vs v8 utiliza:

- exactamente los mismos folds;
- los mismos períodos;
- el mismo feature set;
- los mismos universos de evaluación.

El script verifica programáticamente la comparabilidad antes de calcular las diferencias.

---

# 49. Riesgo de interpretar score como probabilidad

Los scores actuales se utilizan para ordenar empresas.

No se interpretan como probabilidades reales.

Por ejemplo, un score de 0,80 no debe interpretarse automáticamente como una probabilidad del 80 % de convertirse en emisor.

La calibración se evaluará posteriormente, una vez seleccionada una familia de modelo suficientemente estable.

---

# 50. Riesgo de automatización de decisiones

El proyecto no busca sustituir la decisión humana.

El modelo debe funcionar bajo un esquema:

**human-in-the-loop**

El ranking constituye un insumo para una revisión posterior realizada por especialistas.

---

# 51. Ajustes realizados y efecto esperado

| Ajuste | Motivo | Efecto esperado / observado |
|---|---|---|
| Corrección temporal | Reducir leakage | Evaluación más realista |
| Embargos | Evitar solapamiento de horizontes | Mayor independencia temporal |
| Variables temporales | Capturar trayectoria | Mayor información sobre evolución |
| HistGradientBoosting | Capturar no linealidad | Mayor capacidad de ranking |
| Regularización v8 | Reducir sobreajuste de v7 | Mejor generalización |
| Rolling-origin | Evitar depender de un año | Medición de estabilidad |
| Comparación automatizada | Evitar comparación injusta | Trazabilidad y reproducibilidad |

---

# 52. Resultados principales de la etapa

Los principales resultados acumulados son:

1. se corrigió la metodología temporal del ciclo histórico;
2. se introdujeron períodos de embargo;
3. se incorporaron variables temporales;
4. se evaluaron regresión logística, HistGradientBoosting y MLP;
5. se identificó sobreajuste en v7;
6. se regularizó el modelo para producir v8;
7. se desarrollaron backtests temporales para v6 y v8;
8. se automatizó la comparación entre ambos;
9. v8 obtuvo mayor PR-AUC que v6 en los tres folds históricos;
10. v8 obtuvo mayor Lift@50 promedio;
11. se auditaron nuevas fuentes de SCVS para la siguiente generación;
12. se validó el target contra listado de entes y fichas registrales;
13. se integró `bi_ranking` con el dataset histórico;
14. se definieron reglas determinísticas de identidad y elegibilidad;
15. se congeló la base integrada v10 2012–2023;
16. la base v10 contiene **1.030.671 observaciones elegibles** y **568 positivos**;
17. la reconstrucción física produjo el mismo SHA-256;
18. todavía no se ha definido el feature set ni el split temporal v10;
19. todavía no se ha entrenado ningún modelo v10;
20. ningún TEST v10 ha sido evaluado.

---

# 53. Evidencia de reproducibilidad

El proyecto utiliza:

- Git;
- GitHub;
- entorno virtual;
- scripts Python separados por etapa;
- `requirements.txt`;
- `requirements-lock.txt`;
- resultados agregados versionados;
- metadata de experimentos;
- documentación técnica;
- bitácora;
- backlog;
- diccionario de datos;
- inventario de fuentes.

Los datasets de gran tamaño no se versionan en Git.

Los modelos binarios reconstruibles tampoco constituyen la evidencia principal.

Para la base integrada v10 se validó reproducibilidad binaria mediante SHA-256:

`b44f9ccf309c20a59be436953a0c6e7f9a3dc1f11cc6f2c87e41c1676a3a2a8d`

La reconstrucción del dataset produjo exactamente el mismo hash.

Se versionan principalmente:

- código;
- configuración;
- resultados agregados;
- metadata;
- documentación.

---

# 54. Scripts principales del ciclo actual

| Componente | Archivo |
|---|---|
| Dataset armonizado | `src/data/build_scvs_harmonized_dataset.py` |
| Validación de homologación | `src/data/validate_scvs_harmonized_dataset.py` |
| Dataset etiquetado | `src/data/build_mvp_labeled_dataset.py` |
| Variables temporales | scripts de `src/features/` |
| Regresión logística v6 | `src/models/train_logistic_temporal_features_v6.py` |
| Backtest v6 | `src/evaluation/backtest_logistic_v6.py` |
| HistGradientBoosting v8 | scripts de `src/models/` |
| Backtest v8 | `src/evaluation/backtest_hist_gradient_boosting_v8.py` |
| Comparación v6 vs v8 | `src/evaluation/compare_v6_v8_backtests.py` |
| Base integrada v10 | `scripts/build_v10_base.py` |

---

# 55. Resultados versionados

## 55.1 Backtest v6

- `reports/results/backtest_logistic_v6_metrics.csv`
- `reports/results/backtest_logistic_v6_ranking_metrics.csv`
- `reports/results/backtest_logistic_v6_summary.csv`
- `reports/results/backtest_logistic_v6_metadata.json`

## 55.2 Comparación v6 vs v8

- `reports/results/comparison_v6_v8_metrics_by_year.csv`
- `reports/results/comparison_v6_v8_ranking_by_year.csv`
- `reports/results/comparison_v6_v8_stability_summary.csv`
- `reports/results/comparison_v6_v8_model_summary.csv`
- `reports/results/comparison_v6_v8_metadata.json`

Los resultados equivalentes del backtest v8 también permanecen versionados en el repositorio.

---

# 56. Control de versiones

Los principales hitos del ciclo temporal corregido son:

| Commit | Hito |
|---|---|
| `69d29da` | Corrección temporal del target y v4–v5 |
| `c44f24e` | Variables temporales y v6 |
| `1c6555c` | HistGradientBoosting v7 |
| `d81bbfa` | HistGradientBoosting regularizado v8 |
| `0565ead` | Backtest temporal v8 |
| `1ae9531` | MLP v9 |
| `c6fadce` | Backtest temporal v6 |
| `99a8ca0` | Comparación automatizada v6 vs v8 |

El historial de Git permite reconstruir el orden de los cambios y evita modificar retrospectivamente los resultados obtenidos.

---

# 57. Documentación del repositorio

El repositorio dispone de:

| Documento | Propósito |
|---|---|
| `README.md` | Visión general y estado actual |
| `docs/bitacora.md` | Evolución técnica y decisiones |
| `docs/backlog.md` | Actividades pendientes y completadas |
| `docs/diccionario_datos.md` | Variables y transformaciones |
| `docs/inventario_fuentes.md` | Fuentes de información |
| `docs/entorno_tecnico.md` | Entorno y versiones |
| `docs/pipeline_datos_mvp.md` | Pipeline de procesamiento |
| `docs/baseline_v1.md` | Evidencia histórica v1 |
| `docs/baseline_v2.md` | Evidencia histórica v2 |
| `docs/baseline_v3.md` | Evidencia histórica v3 |
| `docs/informe_resultados_preliminares.md` | Consolidación de ajustes y resultados |
| `docs/v10_dataset_freeze.md` | Congelamiento formal del universo, target, identidad e integración v10 |

---

# 58. Entorno tecnológico

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
| PowerShell | Ejecución |

Las versiones completas se mantienen en:

- `requirements.txt`
- `requirements-lock.txt`

---

# 59. Principales decisiones técnicas

## 59.1 No utilizar split aleatorio

Se prioriza una evaluación cronológica porque el caso de uso consiste en utilizar información histórica para priorizar empresas futuras.

## 59.2 Utilizar embargo

Se incorporaron períodos intermedios para reducir solapamiento entre ventanas del target.

## 59.3 Utilizar PR-AUC

La prevalencia extremadamente baja hace que Accuracy resulte poco informativa.

PR-AUC permite observar mejor el desempeño sobre la clase positiva.

## 59.4 Incorporar métricas Top-K

El valor de negocio se concentra en las primeras posiciones del ranking.

Por esta razón se utilizan:

- Precision@K;
- Recall@K;
- Lift@K.

## 59.5 Mantener un baseline simple

La regresión logística se conserva como referencia porque facilita:

- interpretación;
- comparación;
- reproducción;
- detección de mejoras realmente atribuibles a modelos más complejos.

## 59.6 No abrir TEST durante el desarrollo

El conjunto TEST final de cada generación debe permanecer reservado para evitar ajustar decisiones a partir de su desempeño.

En v10 todavía debe definirse y congelarse el nuevo protocolo temporal antes del primer entrenamiento.

---

# 60. Reflexión técnica

La evolución del proyecto muestra que mejorar un modelo de inteligencia artificial no significa únicamente incrementar la complejidad del algoritmo.

Durante el desarrollo se observó que:

- v7 presentó una capacidad muy alta en TRAIN, pero generalizó deficientemente;
- v8 mejoró al reducir la complejidad;
- v9 incorporó una red neuronal, pero no superó a v8;
- v6 mostró que la incorporación de variables temporales no garantiza por sí sola un incremento del PR-AUC;
- la modificación de la metodología temporal produjo resultados aparentemente inferiores a los del primer baseline, pero metodológicamente más confiables.

Uno de los principales aprendizajes es que la calidad del diseño experimental puede ser más importante que una mejora aislada de una métrica.

---

# 61. Reflexión sobre estabilidad

La evaluación por múltiples ventanas permite observar que el desempeño no es constante.

En v8 el PR-AUC cambia entre:

**0,011805 y 0,034551**

Esto demuestra que el desempeño depende del período evaluado.

Por tanto, utilizar exclusivamente el resultado de 2020 podría producir una interpretación incompleta.

La incorporación del rolling-origin permite disponer de una visión más robusta, aunque tres folds todavía constituyen una cantidad limitada para realizar inferencias estadísticas fuertes.

---

# 62. Reflexión sobre utilidad para BVQ

El objetivo organizacional no requiere necesariamente clasificar correctamente a todas las empresas.

La utilidad se encuentra en reducir un universo muy amplio a una lista priorizada que pueda ser revisada por especialistas.

Desde esta perspectiva, métricas como:

- Lift@50;
- Precision@50;
- Recall@50;

tienen una relación más directa con el proceso comercial.

El Lift@50 promedio observado para v8 es:

**123,64**

frente a:

**65,15**

para v6.

Esto indica que v8 concentra eventos positivos en las primeras posiciones con mayor intensidad relativa que el baseline comparable durante las ventanas analizadas.

---

# 63. Limitaciones actuales

Las principales limitaciones identificadas son:

1. el evento positivo continúa siendo extremadamente poco frecuente;
2. la base v10 contiene **568 positivos** dentro de **1.030.671 observaciones elegibles**;
3. la prevalencia v10 es aproximadamente **0,055110 %**;
4. el feature set v10 todavía no está cerrado;
5. el protocolo temporal v10 todavía no está congelado;
6. no existe todavía baseline `v10-LR`;
7. todavía no se han entrenado `v10-HGB`, Random Forest, CatBoost ni TensorFlow/Keras;
8. la disponibilidad temporal se aproxima mediante una regla normativa y no mediante la fecha individual real de presentación;
9. los indicadores oficiales presentan cobertura temporal desigual, especialmente antes de 2018;
10. existen valores extremos y anomalías de fuente que requieren reglas reproducibles antes del modelado;
11. las variables temporales y tendencias multianuales de v10 todavía deben construirse;
12. los scores todavía no están calibrados;
13. la interpretabilidad mediante SHAP todavía está pendiente;
14. debe ampliarse la evaluación de sesgos;
15. todavía no se ha construido el Índice de Afinidad Bursátil definitivo;
16. el prototipo web todavía está pendiente;
17. el TEST final de v10 no debe evaluarse mientras existan decisiones metodológicas abiertas.

---

# 64. Próximas mejoras basadas en evidencia

## 64.1 Mantener congelada la base v10

Las reglas de:

- universo;
- target;
- identidad;
- elegibilidad;
- integración principal

no deberán modificarse salvo que se identifique un error reproducible que justifique una nueva versión.

## 64.2 Cerrar el feature set v10

La siguiente etapa inmediata consiste en clasificar las columnas de la base v10 en:

- predictores;
- variables administrativas;
- variables de auditoría;
- variables excluidas.

También deberán definirse:

- missingness;
- variables `t-1`;
- tasas de crecimiento;
- tendencias multianuales;
- variables categóricas;
- transformaciones;
- tratamiento de valores extremos.

## 64.3 Definir el nuevo protocolo temporal

Antes del primer entrenamiento v10 deberá congelarse:

- TRAIN;
- embargo de validación;
- VALIDATION;
- embargo de TEST;
- TEST final.

## 64.4 Nuevo baseline

El primer modelo de la nueva generación será:

`v10-LR`

Esto permitirá medir el aporte del nuevo dataset y del nuevo feature set antes de atribuir mejoras a algoritmos más complejos.

## 64.5 Nuevos modelos

Posteriormente se evaluarán, bajo el mismo protocolo:

- `v10-HGB`;
- `v10-RF`;
- `v10-CatBoost`;
- `v10-NN`.

## 64.6 TensorFlow/Keras

La alternativa neuronal final deberá implementarse mediante TensorFlow/Keras para cumplir el componente metodológico previsto en la propuesta.

## 64.7 Interpretabilidad

Se incorporará SHAP en modelos compatibles para analizar:

- importancia global;
- explicación local;
- variables que impulsan el ranking.

## 64.8 Sesgo

Se evaluará el desempeño segmentado para identificar posibles diferencias sistemáticas entre grupos de empresas.

## 64.9 Calibración

La calibración se evaluará únicamente después de seleccionar una familia de modelo suficientemente estable.

---

# 65. Índice de Afinidad Bursátil

El proyecto contempla posteriormente construir un:

**Índice de Afinidad Bursátil — IAB**

Los scores actuales no deben interpretarse directamente como probabilidades.

El IAB deberá construirse después de:

1. seleccionar el modelo;
2. analizar estabilidad;
3. evaluar sesgos;
4. incorporar interpretabilidad;
5. evaluar calibración;
6. definir una escala útil para el negocio;
7. validar el indicador con especialistas.

---

# 66. Prototipo funcional

El proyecto contempla desarrollar una interfaz web que permita visualizar de manera dinámica:

- ranking de empresas;
- indicadores financieros;
- evolución temporal;
- principales variables;
- explicación del score;
- empresas comparables;
- filtros de análisis;
- estado de revisión.

La interfaz deberá presentar el resultado como:

**afinidad o priorización**

y no como una predicción determinística de que una empresa necesariamente se convertirá en emisor.

---

# 67. Uso responsable

Prospect Finder BVQ se desarrolla con fines académicos, experimentales y de investigación aplicada.

El sistema:

- no constituye una recomendación de inversión;
- no determina automáticamente que una empresa deba convertirse en emisor;
- no representa una aprobación regulatoria;
- no sustituye análisis financiero;
- no sustituye análisis legal;
- no sustituye análisis comercial;
- no debe utilizarse como único criterio de decisión;
- no debe presentar scores no calibrados como probabilidades reales.

La revisión humana constituye parte fundamental del diseño.

---

# 68. Estado actual del proyecto

| Componente | Estado |
|---|---|
| Dataset financiero armonizado v1–v9 | Completado |
| Validación contable histórica | Completada |
| Target temporal corregido v4–v9 | Completado |
| Regla de disponibilidad | Implementada |
| Períodos de embargo v4–v9 | Implementados |
| Variables temporales v6–v9 | Implementadas |
| Regresión logística v6 | Completada |
| HistGradientBoosting v7 | Completado |
| HistGradientBoosting v8 | Completado |
| MLP v9 | Completado como experimento |
| Backtest v6 | Completado |
| Backtest v8 | Completado |
| Comparación v6 vs v8 | Completada |
| Benchmark histórico v1–v9 | v8 |
| Auditoría de nuevas fuentes | Completada para la base v10 actual |
| Validación del target v10 | Completada |
| Integración de fuentes v10 | Completada |
| Dataset base v10 | **Congelado y reproducible** |
| Feature set v10 | En desarrollo |
| Split temporal v10 | Pendiente |
| `v10-LR` | Pendiente |
| `v10-HGB` | Pendiente |
| Random Forest v10 | Pendiente |
| CatBoost v10 | Pendiente |
| TensorFlow/Keras v10 | Pendiente |
| Interpretabilidad SHAP | Pendiente |
| Evaluación ampliada de sesgo | Pendiente |
| Calibración | Pendiente |
| TEST final v10 | **No evaluado / pendiente de definición formal** |
| IAB | Pendiente |
| Prototipo web | Pendiente |
| MLOps / monitoreo | Pendiente |

---

# 69. Síntesis de resultados

El proyecto ha avanzado en dos etapas claramente diferenciadas.

La primera corresponde al ciclo experimental v1–v9, en el que se fortaleció progresivamente el diseño temporal, se introdujeron embargos, variables temporales y backtesting rolling-origin, y se compararon modelos bajo condiciones equivalentes.

Dentro de ese ciclo histórico, la comparación principal fue:

| Indicador | v6 | v8 |
|---|---:|---:|
| PR-AUC promedio | 0,011329 | **0,021041** |
| Lift@50 promedio | 65,15 | **123,64** |

v8 obtuvo mayor PR-AUC en los tres años evaluados, aunque también presentó mayor dispersión.

La segunda etapa corresponde a la nueva generación v10.

La base integrada v10 ya fue congelada con:

- **1.030.671 observaciones elegibles**;
- **568 positivos**;
- **310 RUC positivos únicos**;
- período **2012–2023**;
- prevalencia de **0,055110 %**;
- **0 duplicados empresa-año**.

La base fue reconstruida de forma reproducible y produjo el mismo SHA-256.

Todavía no existen resultados de modelos v10.

La siguiente decisión metodológica será cerrar el feature set y el nuevo protocolo temporal antes de entrenar `v10-LR`.

---

# 70. Conclusión

Los resultados obtenidos muestran que la construcción de un sistema de priorización de potenciales emisores es técnicamente viable, pero también evidencian las dificultades de trabajar con un evento extremadamente poco frecuente y con información cuya disponibilidad temporal debe controlarse cuidadosamente.

El ciclo v1–v9 permitió fortalecer el diseño experimental mediante:

- metodología temporal conservadora;
- períodos de embargo;
- variables temporales;
- rolling-origin;
- análisis de sobreajuste;
- comparación reproducible entre modelos.

Dentro de ese ciclo histórico, v8 mostró una mayor capacidad de priorización que v6 en PR-AUC y Lift@50 bajo las tres ventanas evaluadas.

Sin embargo, la nueva generación v10 cambia de manera sustancial el universo de datos, por lo que esos resultados no deben trasladarse directamente como desempeño esperado de v10.

La contribución principal de la etapa actual es haber construido y congelado una base integrada 2012–2023 con:

- **1.030.671 observaciones elegibles**;
- **568 positivos**;
- **310 RUC positivos únicos**;
- reglas explícitas de identidad;
- target validado;
- integración financiera documentada;
- reproducibilidad binaria verificada mediante SHA-256.

El siguiente paso no es abrir TEST ni entrenar múltiples modelos de inmediato.

Primero deberán cerrarse el feature set v10 y el nuevo protocolo temporal. Posteriormente se entrenará `v10-LR` como baseline de la nueva generación y, bajo las mismas condiciones, se evaluarán alternativas como HistGradientBoosting, Random Forest, CatBoost y TensorFlow/Keras.

Prospect Finder BVQ continúa concibiéndose como una herramienta de apoyo al análisis y la prospección comercial de la Bolsa de Valores Quito. El resultado del modelo deberá utilizarse como señal de afinidad y priorización, manteniendo la revisión humana como componente obligatorio del proceso.
