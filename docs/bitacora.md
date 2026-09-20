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
- próximos ajustes.

La cronología utiliza como referencia los commits registrados en Git.

---

## 2. Proyecto

**Nombre:**

Sistema inteligente basado en aprendizaje automático y redes neuronales para identificar y priorizar empresas con potencial de convertirse en emisores del mercado de valores ecuatoriano para la Bolsa de Valores Quito.

**Integrantes:**

- Marcelo David Aguilar Salguero
- Francisco Xavier Meneses Játiva
- Luis Miguel Gallardo Dávila

---

## 3. Registro cronológico

### 2026-09-06 — Creación de la estructura inicial

**Commit:** `8a91813`

**Mensaje Git:** `Initial project structure`

#### Actividades

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

#### Decisión

Se estableció desde el inicio una estructura modular para evitar mezclar los archivos originales con los productos derivados del procesamiento.

#### Aprendizaje

La separación por etapas facilita la reproducibilidad y permite identificar con mayor claridad dónde se produce cada transformación.

---

### 2026-09-07 — Documentación del entorno técnico

**Commit:** `fbd6812`

**Mensaje Git:** `Add technical environment documentation and dependencies`

#### Actividades

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

#### Decisión

Utilizar un entorno virtual `.venv` específico para el proyecto.

#### Aprendizaje

Registrar las versiones del entorno desde las primeras etapas reduce problemas posteriores de reproducibilidad.

---

### 2026-09-07 — Validación del entorno Jupyter

**Commit:** `87b257a`

**Mensaje Git:** `Add Jupyter environment validation`

#### Actividades

Se incorporó un notebook para verificar que Jupyter estuviera utilizando el intérprete de Python correspondiente al entorno virtual del proyecto.

Archivo:

`notebooks/00_validacion_entorno.ipynb`

#### Decisión

Utilizar notebooks principalmente para exploración y validación, manteniendo los procesos reproducibles principales en scripts Python.

#### Aprendizaje

Es necesario confirmar el kernel utilizado por Jupyter para evitar ejecutar análisis con librerías o versiones distintas de las configuradas para el proyecto.

---

### 2026-09-20 — Inventario de fuentes

**Commit:** `4d9e517`

**Mensaje Git:** `Add data source inventory`

#### Actividades

Se organizó el inventario inicial de fuentes disponibles para el proyecto.

Se identificaron como fuentes principales:

- estados financieros de la Superintendencia de Compañías, Valores y Seguros;
- Registro del Mercado de Valores de la SCVS;
- información complementaria del Data Warehouse de la Bolsa de Valores Quito.

#### Decisión

Utilizar la información financiera de SCVS como fuente principal de variables predictoras.

La información interna de BVQ se mantiene como fuente complementaria de validación y potencial enriquecimiento.

#### Aprendizaje

Las fuentes presentan estructuras diferentes entre períodos, por lo que no es posible utilizarlas directamente sin una etapa previa de análisis y homologación.

---

### 2026-09-20 — Primera construcción del dataset del MVP

**Commit:** `71f28ce`

**Mensaje Git:** `Add initial MVP dataset builder`

#### Actividades

Se desarrolló una primera versión del proceso de construcción del dataset.

Se comenzó a estructurar la unidad de análisis:

`empresa-año`

También se avanzó en la integración de información financiera histórica.

#### Decisión

Utilizar la combinación conceptual de RUC y año como base para construir las observaciones del modelo.

#### Aprendizaje

La variación histórica de los planes contables obliga a definir reglas explícitas de homologación antes de entrenar cualquier modelo.

---

### 2026-09-20 — Dataset reproducible y estructura temporal del MVP

**Commit:** `9231e85`

**Mensaje Git:** `Build reproducible SCVS MVP dataset and temporal features`

#### Actividades

Se consolidó el proceso reproducible de construcción del dataset del MVP.

Se analizaron ocho estructuras contables:

- `PLAN_413`
- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

Para el MVP se utilizaron siete:

- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

`PLAN_413` fue excluido debido a su baja cobertura y ausencia de eventos positivos en las cohortes analizadas.

#### Resultado del dataset armonizado

- 887.469 observaciones empresa-año;
- 166.389 empresas únicas;
- período 2015–2023.

#### Variables homologadas

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

#### Validaciones

Se verificó:

`Activo = Pasivo + Patrimonio`

con cumplimiento de aproximadamente **99,24 %** dentro de una diferencia relativa de 0,01 %.

También se verificó:

`Pasivo total = Pasivo corriente + Pasivo no corriente`

con cumplimiento aproximado de **99,31 %**.

#### Construcción del target

Se definió:

`TARGET_24M`

para representar si una empresa se registra por primera vez como emisor dentro de los siguientes 24 meses.

Después de aplicar las reglas de elegibilidad se obtuvieron:

- 884.072 observaciones;
- 166.107 empresas;
- 440 positivos;
- 883.632 negativos;
- prevalencia aproximada de 0,0498 %.

#### División temporal

Se definió:

- TRAIN: 2015–2020;
- VALIDATION: 2021;
- TEST: 2022–2023.

#### Decisión

No utilizar un split aleatorio.

#### Justificación

El objetivo es reproducir un escenario en el que un modelo entrenado con información histórica sea utilizado sobre períodos posteriores.

#### Aprendizaje

El problema presenta un desbalance de clases mucho mayor al inicialmente esperado, por lo que Accuracy no resulta una métrica adecuada para evaluar el desempeño.

---

### 2026-09-20 — Baseline v1

**Commit:** `f215802`

**Mensaje Git:** `Add reproducible logistic regression baseline v1`

#### Actividades

Se desarrolló el primer modelo de referencia mediante regresión logística.

Configuración principal:

- `C = 1.0`;
- `class_weight = balanced`;
- regularización L2;
- `solver = lbfgs`;
- `max_iter = 2000`;
- `random_state = 42`.

Se utilizaron variables financieras transformadas, razones financieras y `SECTOR_CIIU`.

#### Resultados principales

| Conjunto | PR-AUC | ROC-AUC |
|---|---:|---:|
| TRAIN | 0,099413 | 0,946436 |
| VALIDATION | 0,031095 | 0,940593 |
| TEST | 0,007291 | 0,927740 |

#### Ranking en VALIDATION

| K | Positivos | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 5 | 0,1000 | 0,1190 | 259,76 |
| 100 | 5 | 0,0500 | 0,1190 | 129,88 |
| 200 | 5 | 0,0250 | 0,1190 | 64,94 |

#### Decisión

Utilizar el Baseline v1 como modelo de referencia para experimentos posteriores.

#### Aprendizajes

El modelo demuestra que existe señal predictiva en las variables utilizadas.

Sin embargo, también se observa:

- degradación temporal;
- número elevado de falsos positivos con threshold 0,50;
- bajo Recall@K en períodos posteriores.

Se concluyó que el problema debe abordarse principalmente como un problema de **ranking y priorización**, no como una clasificación operativa basada directamente en un threshold de 0,50.

---

### 2026-09-20 — Baseline v2 y análisis del sector

**Commit:** `d1e6070`

**Mensaje Git:** `Add sector stability analysis and logistic baseline v2`

#### Objetivo

Evaluar si `SECTOR_CIIU` estaba introduciendo inestabilidad temporal.

#### Modificación

Se eliminó únicamente:

`SECTOR_CIIU`

El resto del pipeline se mantuvo equivalente al Baseline v1.

#### Resultados en VALIDATION

| Métrica | Baseline v1 | Baseline v2 |
|---|---:|---:|
| PR-AUC | 0,031095 | 0,024402 |
| ROC-AUC | 0,940593 | 0,961619 |
| Recall | 0,880952 | 0,952381 |
| Precision@50 | 0,1000 | 0,0800 |
| Recall@50 | 0,1190 | 0,0952 |

#### Decisión

No reemplazar el Baseline v1.

#### Justificación

Aunque el modelo sin sector mejora ROC-AUC y Recall al threshold 0,50, disminuye PR-AUC y las métricas Top 50.

Top 100 y Top 200 no presentan mejoras.

#### Aprendizaje

Una mejora de ROC-AUC no necesariamente representa una mejora útil para el problema organizacional.

Las métricas deben seleccionarse en función del objetivo real de priorización.

#### Uso de TEST

TEST no fue utilizado para seleccionar esta variante.

---

### 2026-09-20 — Experimento v3 de regularización

**Commit:** `c47c931`

**Mensaje Git:** `Add logistic regularization experiment v3`

#### Objetivo

Evaluar si modificar la intensidad de regularización permite mejorar el desempeño de la regresión logística.

#### Valores evaluados

- `C = 0.001`
- `C = 0.01`
- `C = 0.1`
- `C = 1`
- `C = 10`

#### Resultados en VALIDATION

| C | PR-AUC | ROC-AUC |
|---:|---:|---:|
| 0.001 | 0,024217 | 0,955848 |
| 0.01 | 0,027559 | 0,951061 |
| 0.1 | 0,030555 | 0,946416 |
| 1 | 0,031095 | 0,940593 |
| 10 | 0,031135 | 0,934021 |

`C = 10` obtiene el mayor PR-AUC, pero la diferencia frente a `C = 1` es aproximadamente 0,000040.

Las métricas Top 50, Top 100 y Top 200 no presentan una mejora respecto de `C = 1`.

#### Decisión

Mantener:

`C = 1.0`

como configuración de referencia.

#### Aprendizaje

Una diferencia numérica mínima en una métrica no constituye necesariamente una mejora material.

La selección debe considerar simultáneamente:

- magnitud de la mejora;
- estabilidad;
- métricas de ranking;
- complejidad añadida.

#### Uso de TEST

TEST no fue utilizado en la selección del hiperparámetro.

---

### 2026-09-20 — Figuras y resúmenes de errores

**Commit:** `95a516a`

**Mensaje Git:** `Add baseline evaluation figures and error summaries`

#### Actividades

Se generaron visualizaciones para facilitar el análisis de resultados.

Entre las figuras producidas se encuentran:

- distribución de clases;
- Precision-Recall;
- matriz de confusión de VALIDATION;
- matriz de confusión de TEST;
- positivos identificados por Top-K;
- Lift@K;
- Precision@K.

#### Decisión

Versionar figuras y resultados agregados necesarios para interpretar los experimentos.

#### Aprendizaje

Las métricas numéricas aisladas no permiten comprender completamente el comportamiento del modelo.

Las visualizaciones permiten evidenciar con mayor claridad el desbalance y la degradación temporal.

---

### 2026-09-20 — Análisis detallado de errores

**Commit:** `b280b8b`

**Mensaje Git:** `Add detailed baseline error analysis`

#### Actividades

Se profundizó en el análisis de:

- verdaderos positivos;
- falsos positivos;
- falsos negativos;
- posiciones de eventos positivos dentro del ranking;
- sectores;
- perfiles financieros agregados.

#### VALIDATION

Se identificó:

- mejor posición positiva: 7;
- mediana de posición: aproximadamente 2.362;
- peor posición: 64.033;
- positivos dentro del Top 1.000: 10 de 42.

#### TEST

Se identificó:

- mejor posición positiva: 50;
- mediana de posición: 4.317;
- peor posición: 160.698;
- positivos dentro del Top 1.000: 10 de 58.

#### Falsos negativos

VALIDATION presentó 5 falsos negativos.

TEST presentó 4 falsos negativos.

Los cuatro falsos negativos de TEST mostraron un perfil financiero atípico respecto al patrón predominante del modelo, aunque el tamaño de la muestra es demasiado reducido para obtener conclusiones generales.

#### Decisión

Mantener el análisis de errores como parte obligatoria de la evaluación de nuevos modelos.

#### Aprendizaje

Una buena métrica agregada no garantiza que los casos más importantes para el negocio aparezcan en las primeras posiciones del ranking.

El análisis de posiciones y errores individuales resulta necesario para entender dónde falla el modelo.

---

### 2026-09-20 — Informe de resultados preliminares

**Commit:** `343708d`

**Mensaje Git:** `Add preliminary results report`

#### Actividades

Se consolidaron los resultados obtenidos hasta el momento en un informe preliminar.

El documento integra:

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

#### Decisión

Mantener un documento consolidado de resultados además de la documentación técnica específica de cada experimento.

#### Aprendizaje

La documentación debe explicar no solamente qué resultado obtuvo un modelo, sino también:

- qué se modificó;
- por qué se modificó;
- cómo se evaluó;
- qué se aprendió;
- qué decisión se tomó después del experimento.

---

## 4. Decisiones metodológicas acumuladas

A partir de los experimentos realizados se mantienen las siguientes decisiones:

1. La unidad de análisis es `empresa-año`.
2. El horizonte inicial de predicción es 24 meses.
3. Las empresas que ya eran emisoras se excluyen del universo prospectable.
4. El split del dataset es temporal y no aleatorio.
5. TRAIN corresponde a 2015–2020.
6. VALIDATION corresponde a 2021.
7. TEST corresponde a 2022–2023.
8. El Baseline v1 continúa siendo el modelo de referencia.
9. `SECTOR_CIIU` permanece incluido en el Baseline v1.
10. Se mantiene `C = 1.0`.
11. PR-AUC tiene mayor relevancia que Accuracy para este problema.
12. Precision@K, Recall@K y Lift@K son métricas centrales para relacionar el modelo con el proceso de prospección.
13. El threshold 0,50 se utiliza únicamente como diagnóstico.
14. Los scores actuales no deben interpretarse como probabilidades reales calibradas.
15. Los experimentos v2 y v3 no utilizan TEST para seleccionar alternativas.
16. La siguiente etapa debe priorizar nuevas variables y modelos antes que continuar ajustando únicamente la regresión logística.

---

## 5. Principales aprendizajes acumulados

Hasta el momento se han identificado los siguientes aprendizajes:

- la homologación contable es una etapa crítica antes del modelado;
- el problema presenta un desbalance extremo;
- la prevalencia cambia entre períodos;
- ROC-AUC debe interpretarse junto con PR-AUC y métricas de ranking;
- un Recall alto con threshold 0,50 puede venir acompañado de miles de falsos positivos;
- la utilidad comercial depende de la concentración de prospectos en las primeras posiciones;
- eliminar el sector no produjo una mejora en las métricas prioritarias;
- cambiar únicamente la regularización tampoco produjo una mejora material;
- existe señal predictiva, pero se degrada temporalmente;
- se requieren variables que representen evolución y trayectoria financiera;
- el análisis de errores debe acompañar a las métricas agregadas;
- debe controlarse con mayor precisión la fecha efectiva de disponibilidad de la información financiera.

---

## 6. Limitaciones actualmente registradas

Las principales limitaciones son:

1. Solo existen 440 positivos en todo el dataset etiquetado.
2. TRAIN contiene 340 positivos.
3. VALIDATION contiene 42 positivos.
4. TEST contiene 58 positivos.
5. Existe fuerte desbalance.
6. Existe degradación temporal.
7. Las variables actuales son principalmente estáticas.
8. Todavía no se incorporan tendencias financieras interanuales.
9. El modelo de referencia es lineal.
10. Los scores no están calibrados.
11. El threshold 0,50 no es operativo.
12. La fecha efectiva de disponibilidad de los estados financieros requiere mayor control.
13. Todavía no se han evaluado modelos no lineales.
14. Todavía no se ha construido el Índice de Afinidad Bursátil definitivo.

---

## 7. Próxima fase

La siguiente fase del proyecto se concentrará en:

- variables de crecimiento;
- variables de tendencia;
- comportamiento financiero histórico;
- Gradient Boosting;
- CatBoost;
- Random Forest;
- posterior evaluación de MLP;
- tratamiento adicional del desbalance;
- comparación sistemática mediante métricas Top-K;
- calibración;
- interpretabilidad;
- evaluación de nuevas fuentes;
- definición posterior del Índice de Afinidad Bursátil.

---

## 8. Estado de la bitácora

Esta bitácora debe actualizarse cuando se produzca:

- un nuevo experimento;
- un cambio de dataset;
- una modificación importante del pipeline;
- una nueva fuente;
- un cambio metodológico;
- una decisión de selección de modelo;
- un resultado que modifique el rumbo del proyecto.

La bitácora complementa el historial de Git: Git registra qué archivos cambiaron, mientras este documento registra por qué se realizaron los cambios y qué se aprendió de ellos.