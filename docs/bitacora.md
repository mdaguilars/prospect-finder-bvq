# Bitácora del proyecto — Prospect Finder BVQ

## 1. Propósito

Esta bitácora registra la evolución técnica y metodológica del proyecto Prospect Finder BVQ.

Su propósito es mantener trazabilidad sobre:

- cambios realizados;
- decisiones metodológicas;
- experimentos ejecutados;
- resultados relevantes;
- aprendizajes obtenidos;
- limitaciones identificadas;
- riesgos metodológicos;
- próximos ajustes.

La cronología utiliza como referencia los commits registrados en Git y GitHub.

El proyecto mantiene los resultados históricos de cada etapa sin reemplazarlos retrospectivamente. Cuando una modificación metodológica cambia el dataset, el target, las divisiones temporales o el protocolo de evaluación, los resultados anteriores se conservan como evidencia histórica, pero no se comparan directamente como si provinieran del mismo experimento.

---

## 2. Proyecto

**Nombre:**

Sistema inteligente basado en aprendizaje automático y redes neuronales para identificar y priorizar empresas con potencial de convertirse en emisores del mercado de valores ecuatoriano para la Bolsa de Valores Quito.

**Integrantes:**

- Marcelo David Aguilar Salguero
- Francisco Xavier Meneses Játiva
- Luis Miguel Gallardo Dávila

---

# 3. Registro cronológico

## 3.1 Creación de la estructura inicial — 6 de septiembre de 2026

**Commit:** `8a91813`

**Mensaje Git:** `Initial project structure`

### Actividades

Se creó la estructura inicial del repositorio para separar:

- datos originales;
- datos intermedios;
- datos procesados;
- código fuente;
- notebooks;
- modelos;
- resultados;
- figuras;
- documentación.

### Decisión

Se estableció desde el inicio una estructura modular para evitar mezclar los archivos originales con los productos derivados del procesamiento.

### Aprendizaje

La separación por etapas facilita la reproducibilidad y permite identificar con mayor claridad dónde se produce cada transformación.

---

## 3.2 Documentación del entorno técnico — 7 de septiembre de 2026

**Commit:** `fbd6812`

**Mensaje Git:** `Add technical environment documentation and dependencies`

### Actividades

Se documentó el entorno técnico utilizado para el proyecto.

Se registraron componentes como:

- Python;
- Visual Studio Code;
- PowerShell;
- Git;
- GitHub;
- entorno virtual;
- principales dependencias.

También se estableció el uso de archivos de requerimientos para registrar las dependencias.

### Decisión

Utilizar un entorno virtual `.venv` específico para el proyecto.

### Aprendizaje

Registrar las versiones del entorno desde las primeras etapas reduce problemas posteriores de reproducibilidad.

---

## 3.3 Validación del entorno Jupyter — 7 de septiembre de 2026

**Commit:** `87b257a`

**Mensaje Git:** `Add Jupyter environment validation`

### Actividades

Se incorporó un notebook para verificar que Jupyter estuviera utilizando el intérprete de Python correspondiente al entorno virtual del proyecto.

Archivo:

`notebooks/00_validacion_entorno.ipynb`

### Decisión

Utilizar notebooks principalmente para exploración y validación, manteniendo los procesos reproducibles principales en scripts Python.

### Aprendizaje

Es necesario confirmar el kernel utilizado por Jupyter para evitar ejecutar análisis con librerías o versiones distintas de las configuradas para el proyecto.

---

## 3.4 Inventario inicial de fuentes — 20 de septiembre de 2026

**Commit:** `4d9e517`

**Mensaje Git:** `Add data source inventory`

### Actividades

Se organizó el inventario inicial de fuentes disponibles para el proyecto.

Se identificaron como fuentes principales:

- estados financieros de la Superintendencia de Compañías, Valores y Seguros;
- Registro del Mercado de Valores de la SCVS;
- información complementaria del Data Warehouse de la Bolsa de Valores Quito.

### Decisión

Utilizar la información financiera de SCVS como fuente principal de variables predictoras.

La información interna de BVQ se mantiene como fuente complementaria de validación y potencial enriquecimiento.

### Aprendizaje

Las fuentes presentan estructuras diferentes entre períodos, por lo que no es posible utilizarlas directamente sin una etapa previa de análisis y homologación.

---

## 3.5 Primera construcción del dataset del MVP — 20 de septiembre de 2026

**Commit:** `71f28ce`

**Mensaje Git:** `Add initial MVP dataset builder`

### Actividades

Se desarrolló una primera versión del proceso de construcción del dataset.

Se comenzó a estructurar la unidad de análisis:

`empresa-año`

También se avanzó en la integración de información financiera histórica.

### Decisión

Utilizar la combinación conceptual de empresa y año como base para construir las observaciones del modelo.

### Aprendizaje

La variación histórica de los planes contables obliga a definir reglas explícitas de homologación antes de entrenar cualquier modelo.

---

## 3.6 Dataset reproducible y primera metodología temporal — 20 de septiembre de 2026

**Commit:** `9231e85`

**Mensaje Git:** `Build reproducible SCVS MVP dataset and temporal features`

### Actividades

Se consolidó el proceso reproducible de construcción del dataset inicial del MVP.

Se analizaron ocho estructuras contables:

- `PLAN_413`
- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

Para el MVP inicial se utilizaron:

- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

`PLAN_413` fue excluido de esta primera etapa debido a su baja cobertura y ausencia de eventos positivos en las cohortes evaluadas.

### Resultado del dataset armonizado

- 887.469 observaciones empresa-año;
- 166.389 empresas únicas;
- período 2015–2023.

### Variables homologadas

Se construyó un conjunto común de nueve variables:

- `ACTIVO_TOTAL`
- `ACTIVO_CORRIENTE`
- `EFECTIVO`
- `PASIVO_TOTAL`
- `PASIVO_CORRIENTE`
- `PASIVO_NO_CORRIENTE`
- `PATRIMONIO`
- `CAPITAL`
- `UTILIDAD_NETA`

### Validaciones

Se verificó:

`Activo = Pasivo + Patrimonio`

con cumplimiento de aproximadamente **99,24 %** dentro de una diferencia relativa de 0,01 %.

También se verificó:

`Pasivo total = Pasivo corriente + Pasivo no corriente`

con cumplimiento aproximado de **99,31 %**.

### Primera construcción del target

Se definió:

`TARGET_24M`

para representar si una empresa se registra por primera vez como emisor dentro de los siguientes 24 meses.

Con la metodología temporal inicial se obtuvieron:

- 884.072 observaciones;
- 166.107 empresas;
- 440 positivos;
- 883.632 negativos;
- prevalencia aproximada de 0,0498 %.

### Primera división temporal

Se definió inicialmente:

- TRAIN: 2015–2020;
- VALIDATION: 2021;
- TEST: 2022–2023.

### Decisión

No utilizar un split aleatorio.

### Aprendizaje

El problema presenta un desbalance de clases extremo, por lo que Accuracy no resulta una métrica adecuada para evaluar el desempeño.

### Nota metodológica posterior

Los valores de target y las divisiones temporales de esta sección corresponden al **primer ciclo metodológico v1–v3**.

Posteriormente se identificó que el año fiscal no representaba de manera suficientemente conservadora la fecha en la que la información financiera podía considerarse disponible para una decisión real.

Por este motivo, desde v4 se adoptó una metodología temporal corregida. Los resultados de esta sección se mantienen exclusivamente como evidencia histórica.

---

## 3.7 Baseline v1 — Regresión logística

**Commit:** `f215802`

**Mensaje Git:** `Add reproducible logistic regression baseline v1`

### Actividades

Se desarrolló el primer modelo de referencia mediante regresión logística.

Configuración principal:

- `C = 1.0`;
- `class_weight = balanced`;
- regularización L2;
- `solver = lbfgs`;
- `max_iter = 2000`;
- `random_state = 42`.

Se utilizaron variables financieras transformadas, razones financieras y `SECTOR_CIIU`.

### Resultados históricos

| Conjunto | PR-AUC | ROC-AUC |
|---|---:|---:|
| TRAIN | 0,099413 | 0,946436 |
| VALIDATION | 0,031095 | 0,940593 |
| TEST | 0,007291 | 0,927740 |

### Ranking histórico en VALIDATION

| K | Positivos | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 5 | 0,1000 | 0,1190 | 259,76 |
| 100 | 5 | 0,0500 | 0,1190 | 129,88 |
| 200 | 5 | 0,0250 | 0,1190 | 64,94 |

### Decisión de ese momento

Utilizar el Baseline v1 como modelo de referencia para los experimentos iniciales.

### Aprendizajes

El modelo mostró que existía señal predictiva en las variables utilizadas.

También se observó:

- degradación temporal;
- número elevado de falsos positivos con threshold 0,50;
- bajo Recall@K en períodos posteriores.

Se concluyó que el problema debía abordarse principalmente como un problema de **ranking y priorización**, no como una clasificación operativa basada directamente en un threshold de 0,50.

### Nota

TEST 2022–2023 fue utilizado en esta etapa histórica para evaluar el Baseline v1.

Este TEST no debe confundirse con el TEST temporalmente corregido utilizado a partir de v4, que permanece reservado.

---

## 3.8 Baseline v2 — Análisis de la variable sectorial

**Commit:** `d1e6070`

**Mensaje Git:** `Add sector stability analysis and logistic baseline v2`

### Objetivo

Evaluar si `SECTOR_CIIU` estaba introduciendo inestabilidad temporal.

### Modificación

Se eliminó únicamente:

`SECTOR_CIIU`

El resto del pipeline se mantuvo equivalente al Baseline v1.

### Resultados históricos en VALIDATION

| Métrica | Baseline v1 | Baseline v2 |
|---|---:|---:|
| PR-AUC | 0,031095 | 0,024402 |
| ROC-AUC | 0,940593 | 0,961619 |
| Recall | 0,880952 | 0,952381 |
| Precision@50 | 0,1000 | 0,0800 |
| Recall@50 | 0,1190 | 0,0952 |

### Decisión de ese momento

No reemplazar el Baseline v1.

### Justificación

Aunque el modelo sin sector mejoró ROC-AUC y Recall al threshold 0,50, disminuyó PR-AUC y las métricas Top 50.

### Aprendizaje

Una mejora de ROC-AUC no necesariamente representa una mejora útil para el problema organizacional.

Las métricas deben seleccionarse en función del objetivo real de priorización.

### Uso de TEST

TEST no fue utilizado para seleccionar esta variante.

---

## 3.9 Experimento v3 — Regularización logística

**Commit:** `c47c931`

**Mensaje Git:** `Add logistic regularization experiment v3`

### Objetivo

Evaluar si modificar la intensidad de regularización permitía mejorar el desempeño de la regresión logística.

### Valores evaluados

- `C = 0.001`
- `C = 0.01`
- `C = 0.1`
- `C = 1`
- `C = 10`

### Resultados históricos en VALIDATION

| C | PR-AUC | ROC-AUC |
|---:|---:|---:|
| 0.001 | 0,024217 | 0,955848 |
| 0.01 | 0,027559 | 0,951061 |
| 0.1 | 0,030555 | 0,946416 |
| 1 | 0,031095 | 0,940593 |
| 10 | 0,031135 | 0,934021 |

`C = 10` obtuvo el mayor PR-AUC, pero la diferencia frente a `C = 1` fue aproximadamente 0,000040.

Las métricas Top 50, Top 100 y Top 200 no presentaron una mejora respecto de `C = 1`.

### Decisión

Mantener:

`C = 1.0`

como configuración de referencia de esa etapa.

### Aprendizaje

Una diferencia numérica mínima en una métrica no constituye necesariamente una mejora material.

La selección debe considerar simultáneamente:

- magnitud de la mejora;
- estabilidad;
- métricas de ranking;
- complejidad añadida.

### Uso de TEST

TEST no fue utilizado para seleccionar el hiperparámetro.

---

## 3.10 Figuras y resúmenes de errores

**Commit:** `95a516a`

**Mensaje Git:** `Add baseline evaluation figures and error summaries`

### Actividades

Se generaron visualizaciones para facilitar el análisis de resultados.

Entre las figuras producidas se encuentran:

- distribución de clases;
- Precision-Recall;
- matriz de confusión;
- positivos identificados por Top-K;
- Lift@K;
- Precision@K.

### Decisión

Versionar figuras y resultados agregados necesarios para interpretar los experimentos.

### Aprendizaje

Las métricas numéricas aisladas no permiten comprender completamente el comportamiento del modelo.

---

## 3.11 Análisis detallado de errores

**Commit:** `b280b8b`

**Mensaje Git:** `Add detailed baseline error analysis`

### Actividades

Se profundizó en el análisis de:

- verdaderos positivos;
- falsos positivos;
- falsos negativos;
- posición de eventos positivos dentro del ranking;
- sectores;
- perfiles financieros agregados.

### Decisión

Mantener el análisis de errores como parte de la evaluación de nuevos modelos.

### Aprendizaje

Una buena métrica agregada no garantiza que los casos más importantes para el negocio aparezcan en las primeras posiciones del ranking.

---

## 3.12 Informe de resultados preliminares

**Commit:** `343708d`

**Mensaje Git:** `Add preliminary results report`

### Actividades

Se consolidaron los resultados obtenidos en el primer ciclo metodológico.

El informe integró:

- objetivo del prototipo;
- fuentes;
- dataset;
- variables;
- metodología;
- división temporal;
- Baseline v1;
- experimentos v2 y v3;
- métricas;
- ranking;
- análisis de errores;
- fortalezas;
- limitaciones;
- relación con el problema organizacional de la BVQ;
- próximos pasos.

### Decisión

Mantener un documento consolidado de resultados además de la documentación técnica específica de cada experimento.

### Aprendizaje

La documentación debe explicar no solamente qué resultado obtuvo un modelo, sino también:

- qué se modificó;
- por qué se modificó;
- cómo se evaluó;
- qué se aprendió;
- qué decisión se tomó después del experimento.

---

# 4. Corrección metodológica temporal

## 4.1 Problema identificado

Después del ciclo v1–v3 se revisó con mayor profundidad la disponibilidad temporal de los estados financieros.

Los archivos utilizados de SCVS identifican el ejercicio fiscal, pero no contienen una fecha individual de presentación o publicación que permita conocer exactamente cuándo cada estado financiero estuvo disponible para una decisión de prospección.

Utilizar directamente el cierre del ejercicio como fecha de decisión podía introducir una hipótesis temporal demasiado optimista.

## 4.2 Regla conservadora adoptada

Se adoptó una regla normativa y reproducible de disponibilidad:

- ejercicio fiscal: año `t`;
- fecha ordinaria máxima de disponibilidad asumida: `30/04/t+1`;
- fecha de decisión: `01/05/t+1`;
- inicio del horizonte objetivo: `01/05/t+1`;
- fin del horizonte de 24 meses: `30/04/t+3`.

Esta regla constituye una **suposición normativa conservadora**.

No representa la fecha real individual de presentación de cada compañía.

## 4.3 Elegibilidad

Una observación empresa-año solo permanece en el universo prospectable cuando la empresa todavía no había sido registrada como emisor antes de la fecha de decisión correspondiente.

Las observaciones posteriores a la primera inscripción se excluyen.

## 4.4 Nuevo dataset etiquetado

Con la metodología temporal corregida se obtuvieron:

- 887.469 observaciones financieras originales;
- 166.389 empresas;
- 619 emisores históricos identificados;
- 3.481 observaciones correspondientes a empresas que ya eran emisoras antes de la fecha de decisión;
- **883.988 observaciones elegibles**;
- **423 observaciones positivas**;
- prevalencia aproximada de **0,0479 %**.

### Distribución de positivos por año

| Año | Observaciones elegibles | Positivos |
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

## 4.5 Nueva separación temporal

Se definió el siguiente protocolo:

| Conjunto | Período | Observaciones | Positivos |
|---|---|---:|---:|
| TRAIN | 2015–2018 | 324.055 | 262 |
| EMBARGO VALIDATION | 2019 | 91.932 | 34 |
| VALIDATION | 2020 | 98.470 | 34 |
| EMBARGO TEST | 2021 | 109.095 | 39 |
| TEST | 2022–2023 | 260.436 | 54 |

### Justificación de los embargos

El horizonte objetivo es de 24 meses.

Por esta razón, se dejan períodos intermedios entre TRAIN, VALIDATION y TEST para reducir el riesgo de que ventanas objetivo superpuestas generen contaminación temporal entre conjuntos.

## 4.6 Decisión

A partir de v4, esta metodología temporal corregida reemplaza a la metodología de desarrollo utilizada en v1–v3.

Los resultados de v1–v3 se mantienen como evidencia histórica, pero no se comparan numéricamente de forma directa con v4–v9 como si correspondieran al mismo protocolo.

## 4.7 TEST reservado

El conjunto:

`TEST 2022–2023`

de la metodología temporal corregida **no ha sido utilizado para seleccionar modelos v4–v9**.

Permanece reservado para una evaluación posterior una vez que:

- datos;
- variables;
- familia de modelo;
- hiperparámetros;
- protocolo de evaluación

se encuentren suficientemente estabilizados.

---

# 5. Ciclo experimental v4–v9

## 5.1 Experimento v4 — Regresión logística con metodología temporal corregida

**Commit:** `69d29da`

### Objetivo

Reentrenar una regresión logística utilizando la nueva construcción temporal del target y el nuevo protocolo de evaluación.

### Características

Se mantuvo información sectorial.

### Resultados en VALIDATION 2020

- PR-AUC: **0,004570**
- ROC-AUC: **0,920359**
- positivos Top 50: **0**
- positivos Top 100: **1**
- positivos Top 200: **1**

### Aprendizaje

La corrección metodológica redujo de manera importante el desempeño aparente respecto de los resultados históricos v1–v3.

Esto no debe interpretarse como un deterioro causado por el algoritmo, sino como consecuencia de un protocolo temporal más estricto y de una definición del problema más cercana al escenario real de decisión.

---

## 5.2 Experimento v5 — Regresión logística sin sector

**Commit:** `69d29da`

### Objetivo

Reevaluar el efecto de eliminar la variable sectorial bajo la metodología temporal corregida.

### Resultados en VALIDATION 2020

- PR-AUC: **0,005311**
- ROC-AUC: **0,924389**
- positivos Top 50: **0**
- positivos Top 100: **1**
- positivos Top 200: **1**

### Aprendizaje

La exclusión del sector produjo una pequeña mejora en PR-AUC respecto de v4 bajo el nuevo protocolo.

Sin embargo, el comportamiento Top-K continuó siendo limitado.

### Decisión

Mantener la experimentación sin `SECTOR_CIIU` en la siguiente fase para evaluar si la trayectoria financiera aportaba una señal más útil que la información sectorial estática.

---

## 5.3 Experimento v6 — Regresión logística con variables temporales

**Commit:** `c44f24e`

### Objetivo

Incorporar información de trayectoria financiera y evaluar si un modelo lineal podía aprovechar cambios interanuales además de la fotografía financiera del año actual.

### Ingeniería de variables

Se construyó un dataset con:

- 16 variables actuales;
- 17 variables temporales relacionadas con el período anterior;
- 33 variables numéricas en total.

No se utilizó `SECTOR_CIIU`.

### Preprocesamiento

Se aplicó:

- imputación por mediana;
- `StandardScaler`;
- ajuste del preprocesamiento exclusivamente con TRAIN.

### Modelo

Regresión logística con:

- `C = 1.0`;
- `class_weight = balanced`;
- `solver = lbfgs`;
- `max_iter = 2000`;
- `random_state = 42`.

### Resultados en VALIDATION 2020

- PR-AUC: **0,005254**
- ROC-AUC: **0,906290**
- positivos Top 50: **1**
- positivos Top 100: **1**
- positivos Top 200: **1**

### Aprendizaje

Las variables temporales permitieron introducir trayectoria empresarial, pero la regresión logística continuó mostrando una capacidad limitada de concentración en las primeras posiciones.

v6 se conserva como **baseline comparable** para evaluar modelos no lineales que utilicen exactamente el mismo conjunto de variables y protocolo temporal.

---

## 5.4 Experimento v7 — HistGradientBoosting inicial

**Commit:** `1c6555c`

### Objetivo

Evaluar si un modelo no lineal basado en boosting podía capturar interacciones que la regresión logística no representaba adecuadamente.

### Resultado observado

TRAIN:

- PR-AUC aproximado: **0,871232**

VALIDATION 2020:

- PR-AUC: **0,004980**
- ROC-AUC: **0,816540**
- positivos Top 50: **1**
- positivos Top 100: **1**
- positivos Top 200: **2**

### Diagnóstico

La diferencia extremadamente grande entre TRAIN y VALIDATION evidenció un fuerte sobreajuste.

### Decisión

No conservar v7 como candidato.

Utilizar su comportamiento como evidencia para diseñar una versión más regularizada.

### Aprendizaje

Incrementar la capacidad del modelo sin controlar adecuadamente su complejidad puede producir excelentes resultados en entrenamiento y una generalización deficiente.

---

## 5.5 Experimento v8 — HistGradientBoosting regularizado

**Commit:** `d81bbfa`

### Objetivo

Reducir el sobreajuste observado en v7 mediante regularización explícita.

### Cambios principales respecto de v7

| Parámetro | v7 | v8 |
|---|---:|---:|
| `learning_rate` | 0,10 | 0,05 |
| `max_iter` | 100 | 150 |
| `max_leaf_nodes` | 31 | 7 |
| `max_depth` | sin límite explícito | 3 |
| `min_samples_leaf` | 20 | 100 |
| `l2_regularization` | 0 | 1,0 |
| ponderación de clases | balanced | balanced |

### Resultados en VALIDATION 2020

- PR-AUC: **0,011805**
- ROC-AUC: **0,922378**
- positivos Top 50: **2**
- positivos Top 100: **3**
- positivos Top 200: **4**

### Ranking

| K | Positivos | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 2 | 0,0400 | 0,0588 | 115,85 |
| 100 | 3 | 0,0300 | 0,0882 | 86,89 |
| 200 | 4 | 0,0200 | 0,1176 | 57,92 |

### Decisión

v8 se convierte en el **benchmark de mejor desempeño observado hasta el momento bajo la metodología temporal corregida**.

No se considera todavía un modelo final.

### Aprendizaje

La regularización permitió reducir el sobreajuste de v7 y mejorar de manera importante la capacidad de priorización frente a v6 en VALIDATION.

---

## 5.6 Backtest temporal rolling-origin de v8

**Commit:** `0565ead`

### Objetivo

Evaluar si el desempeño de v8 se mantenía en múltiples ventanas temporales y no dependía exclusivamente de VALIDATION 2020.

### Protocolo

Se utilizaron tres folds rolling-origin:

#### Fold 1

- TRAIN: 2015–2016
- EMBARGO: 2017
- EVALUACIÓN: 2018

#### Fold 2

- TRAIN: 2015–2017
- EMBARGO: 2018
- EVALUACIÓN: 2019

#### Fold 3

- TRAIN: 2015–2018
- EMBARGO: 2019
- EVALUACIÓN: 2020

Los años 2021–2023 no participaron.

### Resultados

| Año evaluación | Positivos | PR-AUC | ROC-AUC | Positivos Top 50 | Lift@50 |
|---:|---:|---:|---:|---:|---:|
| 2018 | 59 | 0,034551 | 0,884906 | 5 | 146,93 |
| 2019 | 34 | 0,016766 | 0,938953 | 2 | 108,16 |
| 2020 | 34 | 0,011805 | 0,922378 | 2 | 115,85 |

### Estabilidad descriptiva de PR-AUC

- media: **0,021041**
- mediana: **0,016766**
- desviación estándar muestral: **0,011960**

### ROC-AUC

- media aproximada: **0,915412**
- mediana: **0,922378**
- desviación estándar muestral aproximada: **0,027689**

### Lift@50

- media aproximada: **123,64**
- mediana: **115,85**
- rango aproximado: **108,16–146,93**

### Interpretación

v8 mantiene capacidad de priorización por encima de una selección aleatoria en las tres ventanas evaluadas.

Sin embargo, existe variabilidad entre años.

Debido a que solo existen tres folds, estas medidas se interpretan de forma descriptiva y no como intervalos formales de confianza.

---

## 5.7 Experimento v9 — MLP

**Commit:** `1ae9531`

### Objetivo

Incorporar una primera alternativa basada en red neuronal multicapa para comparar su comportamiento frente a los modelos tabulares.

### Resultados en VALIDATION 2020

- PR-AUC: **0,005262**
- ROC-AUC: **0,848818**
- positivos Top 50: **0**
- positivos Top 100: **0**
- positivos Top 200: **0**

### Decisión

No sustituir v8.

### Aprendizaje

La mayor complejidad de una red neuronal no produjo automáticamente un mejor desempeño para este problema extremadamente desbalanceado y con pocos eventos positivos.

### Alcance

v9 constituye una primera experimentación con MLP.

No se considera todavía el cumplimiento definitivo del componente de redes neuronales previsto en la propuesta académica.

Antes del cierre del proyecto deberá desarrollarse y documentarse una alternativa con **TensorFlow/Keras**, manteniendo el mismo rigor temporal de evaluación.

---

## 5.8 Backtest temporal rolling-origin de v6

**Commit:** `c6fadce`

### Objetivo

Construir una comparación estadísticamente más justa entre v6 y v8 utilizando:

- exactamente las mismas ventanas temporales;
- el mismo universo de evaluación;
- el mismo conjunto de 33 variables;
- el mismo protocolo de embargo;
- TEST reservado.

### Resultados

| Año evaluación | PR-AUC | ROC-AUC | Positivos Top 50 | Lift@50 |
|---:|---:|---:|---:|---:|
| 2018 | 0,015520 | 0,897956 | 1 | 29,39 |
| 2019 | 0,013212 | 0,918509 | 2 | 108,16 |
| 2020 | 0,005254 | 0,906290 | 1 | 57,92 |

### Estabilidad descriptiva de PR-AUC

- media: **0,011329**
- mediana: **0,013212**
- desviación estándar muestral: **0,005386**

### Lift@50

- media aproximada: **65,15**

### Aprendizaje

v6 presenta menor dispersión de PR-AUC que v8, pero alrededor de un nivel de desempeño promedio inferior.

Una desviación estándar menor no debe interpretarse de forma aislada como evidencia de superioridad.

---

## 5.9 Comparación temporal v6 vs v8

**Commit:** `99a8ca0`

**Mensaje Git:** `add v6 vs v8 temporal comparison`

### Objetivo

Automatizar una comparación reproducible entre:

- v6 — Logistic Regression con variables temporales;
- v8 — HistGradientBoosting regularizado.

### Validación de comparabilidad

El script verifica programáticamente igualdad entre ambos experimentos en:

- fold;
- inicio de TRAIN;
- fin de TRAIN;
- año de evaluación;
- observaciones de TRAIN;
- positivos de TRAIN;
- observaciones de evaluación;
- positivos de evaluación.

El resultado confirmó que:

**los folds, períodos de entrenamiento y universos de evaluación son idénticos.**

### PR-AUC por año

| Año | v6 | v8 | Diferencia v8 - v6 |
|---:|---:|---:|---:|
| 2018 | 0,015520 | 0,034551 | +0,019031 |
| 2019 | 0,013212 | 0,016766 | +0,003554 |
| 2020 | 0,005254 | 0,011805 | +0,006550 |

### Cambio relativo de PR-AUC

- 2018: **+122,62 %**
- 2019: **+26,90 %**
- 2020: **+124,67 %**

### Resumen promedio

| Métrica | v6 | v8 |
|---|---:|---:|
| PR-AUC promedio | 0,011329 | 0,021041 |
| Desv. estándar muestral PR-AUC | 0,005386 | 0,011960 |
| Lift@50 promedio | 65,15 | 123,64 |

### Cambio promedio

- mejora relativa de PR-AUC promedio: **+85,73 %**
- mejora relativa de Lift@50 promedio: **+89,77 %**

### ROC-AUC por año

El comportamiento de ROC-AUC no es uniforme:

- en 2018 v6 supera a v8;
- en 2019 v8 supera a v6;
- en 2020 v8 supera a v6.

Por esta razón no se concluye que v8 domine todas las métricas.

### Interpretación

La evidencia disponible favorece a v8 principalmente en las métricas directamente relacionadas con la priorización:

- PR-AUC;
- concentración Top-K;
- Lift@50.

v8 obtiene un PR-AUC superior a v6 en los tres años evaluados y un Lift@50 promedio sustancialmente superior.

v6 presenta una menor desviación estándar del PR-AUC, pero esa menor dispersión ocurre alrededor de un rendimiento promedio más bajo.

### Limitación estadística

Solo existen tres folds temporales.

Por esta razón:

- la variabilidad se reporta de forma descriptiva;
- no se presentan intervalos formales de confianza;
- no se realizan afirmaciones de significancia estadística que los datos disponibles no permiten sustentar.

### Decisión

Mantener a v8 como **benchmark actual bajo la metodología temporal corregida**.

No utilizar todavía TEST 2022–2023.

---

# 6. Estado metodológico actual

## 6.1 Unidad de análisis

La unidad de análisis continúa siendo:

`empresa-año`

## 6.2 Horizonte objetivo

El horizonte es de:

**24 meses**

## 6.3 Fecha de decisión

Para un ejercicio fiscal `t`, la fecha de decisión utilizada es:

`01/05/t+1`

## 6.4 Elegibilidad

Las empresas que ya habían sido emisoras antes de la fecha de decisión quedan excluidas del universo prospectable.

## 6.5 Modelo benchmark actual

El benchmark actual es:

**v8 — HistGradientBoosting regularizado con variables financieras actuales y temporales.**

Esto no significa que sea el modelo definitivo del proyecto.

## 6.6 Baseline comparable

Para las comparaciones actuales se utiliza:

**v6 — Logistic Regression con el mismo conjunto de variables temporales y el mismo protocolo temporal.**

Esto permite que la comparación entre modelo lineal y modelo no lineal sea más justa que una comparación directa contra v1, que pertenece a una metodología temporal anterior.

## 6.7 TEST

El nuevo:

`TEST 2022–2023`

permanece reservado.

## 6.8 Métricas prioritarias

Debido al desbalance extremo, las métricas principales son:

- PR-AUC;
- Precision@K;
- Recall@K;
- Lift@K.

ROC-AUC se mantiene como métrica complementaria.

Accuracy no se utiliza como criterio principal.

## 6.9 Scores

Los scores actuales se utilizan para:

- ordenar;
- priorizar;
- comparar afinidad relativa.

No deben interpretarse todavía como probabilidades reales calibradas.

---

# 7. Principales decisiones metodológicas acumuladas

1. La unidad de análisis es `empresa-año`.
2. El horizonte objetivo es de 24 meses.
3. Las empresas previamente emisoras se excluyen del universo prospectable.
4. La evaluación debe respetar el orden temporal.
5. No se utiliza split aleatorio como mecanismo principal de validación.
6. La disponibilidad temporal de los estados financieros se aproxima mediante una regla normativa conservadora.
7. La fecha de decisión actual es `01/05/t+1`.
8. Se utilizan períodos de embargo entre entrenamiento y evaluación.
9. El nuevo TEST 2022–2023 permanece reservado.
10. v1–v3 se conservan como ciclo histórico.
11. v4 en adelante corresponden a la metodología temporal corregida.
12. Las métricas de ambos ciclos no deben compararse directamente como si provinieran del mismo protocolo.
13. PR-AUC tiene mayor relevancia que Accuracy para este problema.
14. Precision@K, Recall@K y Lift@K son métricas centrales.
15. El threshold 0,50 se utiliza únicamente con fines diagnósticos cuando corresponde.
16. El problema se formula principalmente como ranking y priorización.
17. Los scores actuales no representan probabilidades calibradas.
18. Las variables temporales forman parte de la etapa actual del modelo.
19. v6 constituye el baseline comparable de la etapa temporal actual.
20. v8 constituye el benchmark de mejor desempeño observado hasta el momento.
21. v7 se mantiene como evidencia de sobreajuste.
22. v9 demuestra que mayor complejidad no garantiza mejor generalización.
23. La comparación entre alternativas debe utilizar los mismos datos, folds, variables y protocolo siempre que el objetivo sea determinar el efecto del algoritmo.
24. La selección de un modelo no debe basarse en una sola métrica.
25. La estabilidad temporal debe analizarse mediante múltiples ventanas.
26. TEST no debe utilizarse iterativamente para ajustar modelos.
27. La interpretabilidad y el riesgo de sesgo deberán formar parte de la selección final.
28. La decisión comercial final debe permanecer bajo revisión humana.

---

# 8. Principales aprendizajes acumulados

Hasta el momento se han identificado los siguientes aprendizajes:

- la homologación contable es una etapa crítica antes del modelado;
- el problema presenta un desbalance extremo;
- existen pocos eventos positivos en relación con el universo total;
- la prevalencia cambia entre períodos;
- la disponibilidad temporal de una variable es tan importante como su contenido;
- una división temporal puede continuar siendo insuficiente si no se controla la superposición del horizonte objetivo;
- los períodos de embargo permiten reducir riesgos de contaminación temporal;
- ROC-AUC debe interpretarse junto con PR-AUC y métricas de ranking;
- un Recall elevado con threshold 0,50 puede coexistir con miles de falsos positivos;
- la utilidad comercial depende de la concentración de prospectos en las primeras posiciones;
- modificar únicamente la regularización de la regresión logística no produjo una mejora material en el primer ciclo;
- las variables temporales permiten representar trayectoria, pero por sí solas no garantizan una mejora importante en un modelo lineal;
- un modelo no lineal muy flexible puede sobreajustarse severamente;
- la regularización de v8 permitió mejorar la generalización respecto de v7;
- v8 supera a v6 en PR-AUC en los tres folds temporales evaluados;
- v8 presenta un Lift@50 promedio superior al de v6;
- una menor variabilidad no implica automáticamente un mejor modelo si el nivel promedio de desempeño es inferior;
- los resultados de solo tres folds deben interpretarse de forma descriptiva;
- una red neuronal no necesariamente supera a modelos tabulares en este tipo de problema;
- el análisis de errores debe acompañar a las métricas agregadas;
- la selección final deberá considerar desempeño, estabilidad, explicabilidad, riesgo e integración.

---

# 9. Riesgos identificados y mitigaciones actuales

| Riesgo | Descripción | Mitigación actual |
|---|---|---|
| Leakage temporal | Utilizar información antes de que hubiera podido estar disponible | Regla de disponibilidad `01/05/t+1` y embargos |
| Superposición de horizontes | Eventos objetivo compartidos entre entrenamiento y evaluación | Años de embargo |
| Sobreajuste | Modelos complejos pueden memorizar TRAIN | Regularización y backtesting temporal |
| Desbalance extremo | Muy pocos positivos frente a negativos | `class_weight`, PR-AUC y métricas Top-K |
| Pocos eventos positivos | Alta sensibilidad de las métricas entre años | Rolling-origin y reporte de variabilidad |
| Drift temporal | La relación entre variables y target puede cambiar | Evaluación por cohortes |
| Scores no calibrados | `predict_proba()` no necesariamente representa probabilidad real | Uso como ranking, no como probabilidad |
| Sesgo sectorial | Determinados sectores pueden estar sobrerrepresentados | Comparaciones con y sin sector; análisis futuro segmentado |
| Comparaciones injustas | Modelos pueden parecer mejores por cambios de dataset o protocolo | Comparación v6 vs v8 con protocolo idéntico |
| Complejidad innecesaria | Un modelo más complejo puede no mejorar | Mantener alternativas simples como baseline |
| Uso prematuro de TEST | Ajustar decisiones observando repetidamente el conjunto final | TEST 2022–2023 reservado |
| Interpretación causal | Asociaciones predictivas pueden confundirse con causas | Interpretación exclusivamente predictiva |
| Uso automático | El ranking podría utilizarse sin revisión especializada | Human-in-the-loop |

---

# 10. Limitaciones actualmente registradas

Las principales limitaciones son:

1. El dataset corregido contiene únicamente **423 eventos positivos**.
2. TRAIN 2015–2018 contiene **262 positivos**.
3. VALIDATION 2020 contiene **34 positivos**.
4. TEST 2022–2023 contiene **54 positivos** y permanece reservado.
5. Existe un desbalance extremo.
6. Las métricas presentan variación importante entre cohortes.
7. Solo se dispone actualmente de tres folds en el backtest rolling-origin.
8. La regla de disponibilidad financiera es normativa y no representa la fecha real de presentación de cada empresa.
9. El conjunto de variables todavía se concentra principalmente en información financiera.
10. Las tendencias multianuales más amplias todavía pueden fortalecerse.
11. CatBoost todavía no ha sido evaluado en el ciclo actual.
12. Random Forest todavía no ha sido evaluado.
13. La red neuronal TensorFlow/Keras prevista para la etapa final todavía no ha sido implementada.
14. Los scores no se encuentran calibrados.
15. El Índice de Afinidad Bursátil definitivo todavía no se ha construido.
16. La interpretabilidad mediante SHAP todavía no se ha incorporado al benchmark.
17. La evaluación explícita de sesgos y equidad todavía debe ampliarse.
18. Las nuevas fuentes identificadas todavía no forman parte del dataset de modelado actual.
19. El prototipo web operativo todavía está pendiente.
20. TEST no debe abrirse mientras el ciclo de selección no se encuentre suficientemente estabilizado.

---

# 11. Backtest y confianza en los resultados

La evaluación rolling-origin representa un avance frente a depender de una única ventana de validación.

Actualmente se dispone de evaluaciones para:

- 2018;
- 2019;
- 2020.

Esto permite observar:

- desempeño medio;
- mediana;
- desviación estándar;
- rango temporal;
- comportamiento del ranking entre cohortes.

Sin embargo, tres folds continúan siendo una muestra pequeña.

Por esta razón, los resultados actuales permiten hablar de:

- consistencia descriptiva;
- diferencias observadas;
- estabilidad relativa;

pero no justifican todavía afirmaciones fuertes de significancia estadística.

---

# 12. Comparación actual de alternativas

| Versión | Modelo | Variables temporales | PR-AUC VALIDATION 2020 | ROC-AUC VALIDATION 2020 | Top 50 | Estado |
|---|---|---|---:|---:|---:|---|
| v4 | Logistic Regression | No | 0,004570 | 0,920359 | 0 | Histórico metodología corregida |
| v5 | Logistic Regression sin sector | No | 0,005311 | 0,924389 | 0 | Histórico metodología corregida |
| v6 | Logistic Regression | Sí | 0,005254 | 0,906290 | 1 | Baseline comparable |
| v7 | HistGradientBoosting | Sí | 0,004980 | 0,816540 | 1 | Descartado por sobreajuste |
| v8 | HistGradientBoosting regularizado | Sí | 0,011805 | 0,922378 | 2 | Benchmark actual |
| v9 | MLP | Sí | 0,005262 | 0,848818 | 0 | Alternativa exploratoria |

### Interpretación

v8 presenta actualmente el mejor equilibrio observado entre:

- PR-AUC;
- ranking;
- generalización temporal;
- complejidad operativa.

v6 continúa siendo importante porque proporciona una referencia lineal más interpretable y utiliza exactamente el mismo protocolo y conjunto de variables.

v9 no mejora a v8 y no justifica, con la evidencia actual, una mayor complejidad.

---

# 13. Evidencia de reproducibilidad

El proyecto utiliza:

- Git;
- GitHub;
- entorno virtual;
- `requirements.txt`;
- `requirements-lock.txt`;
- `random_state = 42` donde aplica;
- scripts independientes por etapa;
- datasets derivados reproducibles localmente;
- resultados agregados versionados;
- documentación por experimento;
- bitácora;
- backlog;
- diccionario de datos;
- inventario de fuentes.

Los datasets originales y derivados de gran tamaño no se versionan en Git.

Los resultados agregados necesarios para sustentar las comparaciones sí pueden versionarse de manera controlada.

---

# 14. Evidencias recientes de control de versiones

Los hitos recientes del ciclo temporal corregido incluyen:

| Commit | Evidencia |
|---|---|
| `69d29da` | Corrección temporal del target y experimentos v4–v5 |
| `c44f24e` | Variables temporales y modelo v6 |
| `1c6555c` | HistGradientBoosting v7 |
| `d81bbfa` | HistGradientBoosting regularizado v8 |
| `0565ead` | Backtest temporal rolling-origin de v8 |
| `1ae9531` | Experimento MLP v9 |
| `c6fadce` | Backtest temporal rolling-origin de v6 |
| `99a8ca0` | Comparación automatizada v6 vs v8 |

El commit:

`99a8ca0 — add v6 vs v8 temporal comparison`

incorpora:

- `src/evaluation/compare_v6_v8_backtests.py`;
- `reports/results/comparison_v6_v8_metadata.json`;
- `reports/results/comparison_v6_v8_metrics_by_year.csv`;
- `reports/results/comparison_v6_v8_model_summary.csv`;
- `reports/results/comparison_v6_v8_ranking_by_year.csv`;
- `reports/results/comparison_v6_v8_stability_summary.csv`.

---

# 15. Resultados versionados del backtest

## v6

Se mantienen versionados:

- `reports/results/backtest_logistic_v6_metrics.csv`
- `reports/results/backtest_logistic_v6_ranking_metrics.csv`
- `reports/results/backtest_logistic_v6_summary.csv`
- `reports/results/backtest_logistic_v6_metadata.json`

## v8

Se mantienen versionados los resultados equivalentes del backtest temporal de v8.

## Comparación

Se mantienen versionados:

- métricas por año;
- métricas de ranking;
- estadísticas descriptivas de estabilidad;
- resumen por modelo;
- metadata del protocolo.

Esto permite reconstruir la comparación sin depender de valores copiados manualmente en la documentación.

---

# 16. Estado del conjunto TEST

Debe mantenerse una distinción explícita entre dos etapas.

## TEST histórico v1

El Baseline v1 utilizó el TEST 2022–2023 de la metodología inicial.

Ese resultado se conserva como evidencia histórica del primer ciclo.

## TEST temporalmente corregido

Desde v4 se reconstruyó el target y se modificó el protocolo temporal.

El nuevo:

`TEST 2022–2023`

contiene:

- 260.436 observaciones;
- 54 positivos.

Este conjunto **no ha sido utilizado para seleccionar v4, v5, v6, v7, v8 ni v9**.

Permanece reservado.

---

# 17. Próxima fase

La siguiente fase deberá concentrarse en:

1. cerrar la actualización documental del ciclo v1–v9;
2. mantener TEST 2022–2023 cerrado;
3. revisar e incorporar nuevas fuentes mediante una nueva generación de dataset;
4. ampliar variables temporales y de trayectoria;
5. evaluar CatBoost;
6. evaluar Random Forest;
7. desarrollar la alternativa neuronal TensorFlow/Keras comprometida;
8. mantener comparaciones bajo protocolos idénticos;
9. incorporar interpretabilidad;
10. evaluar sesgos y desempeño segmentado;
11. estudiar calibración únicamente cuando exista un modelo suficientemente estable;
12. construir posteriormente el Índice de Afinidad Bursátil;
13. diseñar el prototipo web de apoyo a prospección;
14. preparar mecanismos de monitoreo y MLOps.

---

# 18. Nueva generación de datos prevista

Las nuevas fuentes identificadas no se incorporan retroactivamente a v1–v9.

La siguiente generación deberá construirse como una nueva versión del dataset y del feature set.

Se utilizará la nomenclatura:

**Dataset / Feature Set v10**

Los nuevos modelos asociados deberán distinguirse explícitamente, por ejemplo:

- `v10-LR`;
- `v10-HGB`;
- `v10-RF`;
- `v10-CatBoost`;
- `v10-NN`.

v8 permanecerá como benchmark del ciclo anterior para permitir una comparación clara entre generaciones.

---

# 19. Criterio para aceptar mejoras futuras

Un nuevo modelo no reemplazará al benchmark únicamente por mejorar una métrica aislada.

La evaluación deberá considerar conjuntamente:

- PR-AUC;
- Precision@K;
- Recall@K;
- Lift@K;
- estabilidad temporal;
- variabilidad entre folds;
- comportamiento frente al desbalance;
- interpretabilidad;
- riesgo de sesgo;
- complejidad;
- reproducibilidad;
- facilidad de integración;
- utilidad para la prospección comercial.

Cuando se comparen algoritmos para determinar cuál aporta mayor capacidad predictiva, deberán mantenerse constantes, siempre que sea posible:

- dataset;
- target;
- variables;
- folds;
- años;
- métricas;
- reglas de elegibilidad;
- protocolo temporal.

---

# 20. Uso responsable

El sistema se desarrolla como una herramienta de apoyo a la prospección.

Sus resultados:

- no constituyen recomendaciones de inversión;
- no determinan que una empresa deba convertirse en emisor;
- no determinan aceptación regulatoria;
- no sustituyen análisis financiero;
- no sustituyen análisis legal;
- no sustituyen análisis comercial;
- no deben interpretarse como probabilidades reales mientras no exista calibración;
- no deben utilizarse como único criterio de decisión.

La revisión humana se mantiene como parte del diseño del sistema.

---

# 21. Estado actual de la bitácora

La bitácora se encuentra actualizada hasta:

- metodología temporal corregida;
- v4;
- v5;
- v6;
- v7;
- v8;
- backtest v8;
- v9;
- backtest v6;
- comparación temporal v6 vs v8;
- commit `99a8ca0`.

El benchmark actual es:

**v8 — HistGradientBoosting regularizado**

El baseline comparable de la metodología actual es:

**v6 — Logistic Regression con variables temporales**

El conjunto:

**TEST 2022–2023**

permanece reservado.

---

# 22. Regla de mantenimiento de la bitácora

Esta bitácora deberá actualizarse cuando se produzca:

- un nuevo experimento;
- un cambio de dataset;
- una nueva generación de features;
- una modificación importante del pipeline;
- una nueva fuente;
- un cambio metodológico;
- una decisión de selección de modelo;
- una evaluación sobre TEST;
- una nueva evidencia de sesgo;
- una modificación del protocolo temporal;
- un resultado que cambie el rumbo del proyecto.

Las actividades y experimentos completados no deben eliminarse.

La bitácora complementa el historial de Git:

**Git registra qué cambió; la bitácora registra por qué cambió, qué resultado produjo y qué decisión se tomó.**