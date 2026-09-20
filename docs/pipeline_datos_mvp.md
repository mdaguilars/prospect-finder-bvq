# Pipeline de datos del MVP — Prospect Finder BVQ

## 1. Objetivo

Este documento describe el proceso reproducible utilizado para construir el dataset del MVP del proyecto:

**Sistema inteligente basado en aprendizaje automático y redes neuronales para identificar y priorizar empresas con potencial de convertirse en emisores del mercado de valores ecuatoriano para la Bolsa de Valores Quito.**

El objetivo del pipeline es transformar información financiera histórica de empresas ecuatorianas y registros oficiales de emisores en un dataset empresa-año apto para entrenamiento y evaluación de modelos de clasificación.

El pipeline busca garantizar:

- trazabilidad;
- reproducibilidad;
- consistencia entre fuentes;
- control de calidad;
- prevención de data leakage;
- separación entre datos originales, intermedios y procesados.

---

## 2. Unidad de análisis

La unidad de análisis es:

**empresa-año**

La empresa se identifica mediante su RUC.

La clave conceptual utilizada durante la construcción del dataset es:

`RUC + ANIO`

Cada observación representa la situación financiera de una empresa en un año determinado.

---

## 3. Horizonte de predicción

El objetivo del modelo es identificar empresas que podrían registrarse por primera vez como emisores dentro de los siguientes 24 meses.

La variable objetivo es:

`TARGET_24M`

Su interpretación es:

- `1`: la empresa se registra por primera vez como emisor dentro de los siguientes 24 meses.
- `0`: la empresa no se registra como nuevo emisor dentro de ese horizonte.

Las empresas que ya eran emisoras en la fecha de corte correspondiente son excluidas del universo elegible.

---

## 4. Convención temporal

Para cada año `t` se define como fecha de corte:

`31 de diciembre del año t`

Una observación se etiqueta como positiva cuando la primera inscripción como emisor ocurre:

- después de la fecha de corte del año `t`; y
- hasta el 31 de diciembre del año `t + 2`.

Esta convención permite construir un horizonte aproximado de 24 meses.

---

## 5. Consideración sobre disponibilidad temporal

La convención actual utiliza el año del estado financiero como referencia temporal.

Sin embargo, un estado financiero correspondiente al año `t` puede haber sido presentado o publicado durante el año `t + 1`.

Por esta razón existe una limitación metodológica que deberá controlarse en siguientes iteraciones:

**la fecha contable de la información no necesariamente coincide con la fecha exacta en que esa información estuvo disponible públicamente.**

Esta situación puede afectar especialmente eventos de inscripción ocurridos a inicios del año siguiente.

El MVP conserva por ahora la convención anual, pero esta limitación debe mantenerse documentada para evitar interpretar el pipeline como completamente libre de riesgo temporal.

---

## 6. Fuentes de información

El pipeline utiliza principalmente información proveniente de la Superintendencia de Compañías, Valores y Seguros.

Las fuentes se dividen en dos grandes grupos:

1. información financiera empresarial;
2. información del Registro del Mercado de Valores.

Adicionalmente, la información interna de la Bolsa de Valores Quito se considera una fuente complementaria de validación y enriquecimiento.

---

## 7. Fuente financiera principal

La fuente principal para construir las variables predictoras corresponde a los estados financieros históricos de empresas ecuatorianas publicados por la SCVS.

Ubicación local:

`data/raw/scvs/estados_financieros/`

Los archivos originales se mantienen sin modificaciones.

El período utilizado para el dataset etiquetado del MVP es:

**2015–2023**

Aunque existen archivos correspondientes a años posteriores, el horizonte de 24 meses limita actualmente la utilización de años recientes para la construcción completa del target.

---

## 8. Fuente para la variable objetivo

La variable objetivo se construye utilizando información histórica del Registro del Mercado de Valores de la SCVS.

Ubicación local:

`data/raw/scvs/mercado_valores/`

Entre las fuentes utilizadas se encuentran archivos de:

- listado de entes registrados;
- fichas registrales;
- información complementaria del mercado de valores.

La variable central utilizada es la fecha de primera inscripción como emisor.

---

## 9. Validación de la fecha de primera inscripción

La primera fecha de inscripción como emisor fue obtenida mediante el listado oficial de entes registrados.

La información fue contrastada con fichas registrales.

Resultados de la validación:

- RUC de emisores identificados: 619;
- RUC con fecha disponible en ambas fuentes: 619;
- diferencias encontradas en la primera fecha de inscripción: 0.

Por tanto, para el MVP se adopta como fecha del evento la primera fecha de inscripción obtenida del listado de entes y validada contra las fichas registrales.

---

## 10. Información interna de BVQ

La información del Data Warehouse de la Bolsa de Valores Quito se utiliza como fuente complementaria.

Su función actual es principalmente:

- validación;
- contraste;
- potencial enriquecimiento futuro.

No constituye la fuente primaria de las variables financieras del Baseline v1.

La información interna de BVQ no se almacena públicamente en Git.

---

## 11. Inventario de estructuras contables

El análisis inicial identificó:

- 44 archivos de balance;
- 44 archivos de catálogos;
- 8 estructuras contables principales.

Los planes identificados son:

- `PLAN_413`
- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

---

## 12. Tratamiento de PLAN_413

`PLAN_413` fue excluido del MVP.

El análisis mostró:

- aproximadamente 730 observaciones;
- ausencia de eventos positivos;
- baja representatividad;
- dificultad para establecer una homologación comparable con las estructuras principales.

La exclusión se limita al MVP actual y puede revisarse posteriormente si se dispone de mayor información.

---

## 13. Planes incluidos

El dataset armonizado utiliza:

- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

Distribución aproximada de observaciones entre 2015 y 2023:

| Plan | Observaciones |
|---|---:|
| `PLAN_622` | 295.445 |
| `PLAN_639` | 1.648 |
| `PLAN_807` | 65.262 |
| `PLAN_819` | 108.521 |
| `PLAN_830` | 138.964 |
| `PLAN_868` | 165.882 |
| `PLAN_925` | 111.747 |
| **Total** | **887.469** |

---

## 14. Necesidad de homologación

Las estructuras contables no utilizan necesariamente los mismos códigos o posiciones para representar un mismo concepto financiero.

Por esta razón no resulta adecuado concatenar directamente los archivos de diferentes años o planes.

Se construyó una capa de homologación que convierte los distintos planes a un conjunto común de variables financieras.

---

## 15. Archivo de homologación

La configuración utilizada se encuentra en:

`config/scvs_account_mapping.csv`

Este archivo permite mantener separadas:

- la lógica del programa;
- las equivalencias contables;
- las decisiones de homologación.

La existencia de un archivo de configuración independiente facilita la revisión y actualización del mapeo sin modificar directamente el código principal.

---

## 16. Variables financieras homologadas

Se seleccionaron nueve variables financieras principales:

| Variable | Descripción |
|---|---|
| `ACTIVO_TOTAL` | Total de activos |
| `ACTIVO_CORRIENTE` | Activos corrientes |
| `EFECTIVO` | Efectivo y equivalentes |
| `PASIVO_TOTAL` | Total de pasivos |
| `PASIVO_CORRIENTE` | Pasivos corrientes |
| `PASIVO_NO_CORRIENTE` | Pasivos no corrientes |
| `PATRIMONIO` | Patrimonio |
| `CAPITAL` | Capital registrado |
| `UTILIDAD_NETA` | Resultado neto del período |

Estas variables constituyen la base financiera inicial del MVP.

---

## 17. Normalización del formato numérico

Los archivos originales presentan diferencias de formato entre períodos y estructuras.

Durante el procesamiento se detectó la necesidad de controlar especialmente el separador decimal.

Los valores financieros fueron convertidos a formato numérico estándar antes de cualquier cálculo.

Este paso es necesario para evitar que valores monetarios sean interpretados como texto.

---

## 18. Construcción del dataset armonizado

El proceso general de armonización es:

1. identificar el año;
2. identificar el plan contable;
3. leer el archivo correspondiente;
4. normalizar identificadores;
5. convertir valores financieros a formato numérico;
6. aplicar el mapeo de cuentas;
7. obtener las nueve variables homologadas;
8. consolidar a nivel empresa-año;
9. conservar el plan contable para trazabilidad;
10. concatenar los diferentes períodos.

---

## 19. Resultado del dataset armonizado

El proceso genera:

- **887.469 observaciones empresa-año**;
- **166.389 empresas únicas**;
- período **2015–2023**.

Archivo generado:

`data/interim/scvs_financials_harmonized_2015_2023.csv.gz`

Este archivo es un producto intermedio y no se almacena en Git.

---

## 20. Cobertura de variables homologadas

Las nueve variables financieras seleccionadas presentan cobertura completa dentro del dataset armonizado generado.

Esto significa que cada observación contiene un valor procesable para las variables base seleccionadas.

La existencia de un valor no implica necesariamente que el valor sea distinto de cero.

---

## 21. Validaciones contables

Después de la homologación se realizaron controles sobre ecuaciones contables básicas.

### Activo = Pasivo + Patrimonio

Se calcula la diferencia relativa entre:

`ACTIVO_TOTAL`

y:

`PASIVO_TOTAL + PATRIMONIO`

El **99,24 %** de las observaciones cumple una diferencia relativa menor o igual al 0,01 %.

---

## 22. Validación de composición del pasivo

Se verifica:

`PASIVO_TOTAL = PASIVO_CORRIENTE + PASIVO_NO_CORRIENTE`

El **99,31 %** de las observaciones cumple una diferencia relativa menor o igual al 0,01 %.

Estas validaciones permiten verificar la consistencia de la homologación.

---

## 23. Revisión de PLAN_807

Durante las validaciones se analizaron específicamente diferencias asociadas a `PLAN_807`.

Después de revisar su comportamiento y la lógica de homologación, el plan fue conservado en el dataset del MVP.

No se identificó evidencia suficiente para justificar su exclusión completa.

---

## 24. Script de construcción del dataset armonizado

El proceso principal se encuentra en:

`src/data/build_scvs_harmonized_dataset.py`

Su responsabilidad es construir el dataset común a partir de las diferentes estructuras contables.

---

## 25. Script de validación del dataset armonizado

Las verificaciones de consistencia se ejecutan mediante:

`src/data/validate_scvs_harmonized_dataset.py`

Este proceso permite separar:

- construcción;
- validación.

De esta forma el dataset puede ser evaluado después de su generación.

---

## 26. Construcción del universo de emisores

A partir del Registro del Mercado de Valores se obtiene para cada RUC:

- primera fecha de inscripción;
- condición histórica de emisor.

La primera inscripción se utiliza como evento para la creación de `TARGET_24M`.

No se utilizan reinscripciones posteriores como nuevos eventos.

---

## 27. Elegibilidad en cada fecha de corte

Una empresa solamente puede formar parte del universo prospectable cuando todavía no era emisora en la fecha de corte.

Por tanto:

- una empresa no emisora puede recibir `TARGET_24M = 0` o `TARGET_24M = 1`;
- una empresa que ya era emisora queda excluida de las observaciones posteriores a su inscripción.

Esta regla evita entrenar al modelo con empresas que ya habían alcanzado el evento objetivo.

---

## 28. Construcción de TARGET_24M

Para una empresa `i` y año `t`:

`TARGET_24M = 1`

cuando:

- la empresa no era emisora al 31 de diciembre de `t`; y
- su primera inscripción ocurre dentro de los siguientes 24 meses.

En caso contrario:

`TARGET_24M = 0`

siempre que la empresa continúe siendo elegible.

---

## 29. Dataset etiquetado

Después de aplicar las reglas de elegibilidad y construir el target se obtienen:

| Indicador | Resultado |
|---|---:|
| Observaciones empresa-año | 884.072 |
| Empresas únicas | 166.107 |
| Positivos | 440 |
| Negativos | 883.632 |
| Prevalencia | 0,0498 % |

Archivo:

`data/processed/mvp_labeled_2015_2023.csv.gz`

---

## 30. Distribución anual de positivos

Los eventos positivos se distribuyen de la siguiente manera:

| Año | Positivos |
|---|---:|
| 2015 | 39 |
| 2016 | 58 |
| 2017 | 93 |
| 2018 | 78 |
| 2019 | 39 |
| 2020 | 33 |
| 2021 | 42 |
| 2022 | 36 |
| 2023 | 22 |
| **Total** | **440** |

La distribución muestra que el número de nuevos emisores no es constante a través del tiempo.

---

## 31. Script de construcción del dataset etiquetado

El proceso se ejecuta mediante:

`src/data/build_mvp_labeled_dataset.py`

Este script combina:

- información financiera armonizada;
- historial de emisores;
- reglas de elegibilidad;
- horizonte temporal de 24 meses.

---

## 32. Ingeniería de variables

Después del etiquetado se construyen variables destinadas al modelado.

Se utilizan dos grupos principales:

1. transformaciones de escala;
2. razones financieras.

---

## 33. Transformaciones logarítmicas

Para reducir diferencias de magnitud se aplica una transformación logarítmica con signo.

La transformación conceptual es:

`sign(x) × log(1 + |x|)`

Se generan:

- `LOG_ACTIVO_TOTAL`
- `LOG_ACTIVO_CORRIENTE`
- `LOG_EFECTIVO`
- `LOG_PASIVO_TOTAL`
- `LOG_PASIVO_CORRIENTE`
- `LOG_PASIVO_NO_CORRIENTE`
- `LOG_PATRIMONIO`
- `LOG_CAPITAL`
- `LOG_UTILIDAD_NETA`

---

## 34. Razones financieras

Se construyen:

### Liquidez corriente

`ACTIVO_CORRIENTE / PASIVO_CORRIENTE`

Variable:

`LIQUIDEZ_CORRIENTE`

### Endeudamiento

`PASIVO_TOTAL / ACTIVO_TOTAL`

Variable:

`ENDEUDAMIENTO`

### Autonomía financiera

`PATRIMONIO / ACTIVO_TOTAL`

Variable:

`AUTONOMIA_FINANCIERA`

### ROA

`UTILIDAD_NETA / ACTIVO_TOTAL`

Variable:

`ROA`

### Efectivo sobre activos

`EFECTIVO / ACTIVO_TOTAL`

Variable:

`EFECTIVO_ACTIVOS`

### Capital sobre activos

`CAPITAL / ACTIVO_TOTAL`

Variable:

`CAPITAL_ACTIVOS`

### Pasivo corriente sobre pasivo total

`PASIVO_CORRIENTE / PASIVO_TOTAL`

Variable:

`PASIVO_CORRIENTE_PASIVO`

---

## 35. Tratamiento de denominadores iguales a cero

Las razones financieras no se fuerzan artificialmente cuando el denominador es cero.

En estos casos el resultado se conserva como valor faltante.

Posteriormente el pipeline de modelado utiliza imputación calculada exclusivamente con TRAIN.

Esta decisión evita introducir valores arbitrarios durante la construcción de features.

---

## 36. Disponibilidad de razones financieras

La disponibilidad aproximada es:

| Variable | Disponibilidad |
|---|---:|
| `LIQUIDEZ_CORRIENTE` | 68,04 % |
| `ENDEUDAMIENTO` | 95,81 % |
| `AUTONOMIA_FINANCIERA` | 95,81 % |
| `ROA` | 95,81 % |
| `EFECTIVO_ACTIVOS` | 95,81 % |
| `CAPITAL_ACTIVOS` | 95,81 % |
| `PASIVO_CORRIENTE_PASIVO` | 71,03 % |

---

## 37. Variable sectorial

Se incorpora:

`SECTOR_CIIU`

La variable corresponde a la primera sección de la clasificación CIIU.

Su disponibilidad es aproximadamente:

**99,98 %**

Esta variable es tratada como categórica en el Baseline v1.

---

## 38. Dataset de features

El proceso de ingeniería de variables genera:

`data/processed/mvp_features_2015_2023.csv.gz`

Este archivo constituye la entrada principal para los experimentos de modelado del MVP.

---

## 39. Script de ingeniería de variables

La construcción de features se realiza mediante:

`src/features/build_mvp_features.py`

Este script permite mantener separadas:

- la construcción del target;
- la ingeniería de variables;
- el modelado.

---

## 40. Variables excluidas como predictores

No se utilizan directamente como variables predictoras:

- `RUC`
- `EXPEDIENTE`
- `NOMBRE`
- `ANIO`
- `SPLIT`
- `PLAN_CONTABLE`
- `TARGET_24M`

Las fechas utilizadas para construir el evento tampoco se utilizan como predictores.

---

## 41. Uso de PLAN_CONTABLE

`PLAN_CONTABLE` se conserva únicamente para trazabilidad y control de calidad.

No se utiliza como predictor.

El objetivo es reducir el riesgo de que el modelo aprenda cambios administrativos o modificaciones históricas en la estructura de reporte contable en lugar de características económicas de la empresa.

---

## 42. División temporal

El dataset no se divide aleatoriamente.

Se utiliza:

| Conjunto | Período |
|---|---|
| TRAIN | 2015–2020 |
| VALIDATION | 2021 |
| TEST | 2022–2023 |

Esta estructura busca aproximar un escenario real de aplicación.

---

## 43. Tamaño de los conjuntos

| Conjunto | Observaciones | Positivos | Prevalencia |
|---|---:|---:|---:|
| TRAIN | 514.527 | 340 | 0,0661 % |
| VALIDATION | 109.101 | 42 | 0,0385 % |
| TEST | 260.444 | 58 | 0,0223 % |

La reducción de prevalencia entre períodos constituye una característica relevante del problema.

---

## 44. Prevención de data leakage

El pipeline aplica los siguientes principios:

- separación temporal entre TRAIN, VALIDATION y TEST;
- imputadores ajustados exclusivamente con TRAIN;
- escaladores ajustados exclusivamente con TRAIN;
- codificadores categóricos ajustados exclusivamente con TRAIN;
- exclusión de variables que contienen información futura;
- exclusión de empresas que ya eran emisoras en la fecha de corte;
- no utilización del resultado futuro como predictor.

---

## 45. Limitación temporal pendiente

Aunque el split es temporal, todavía debe fortalecerse el control sobre la fecha exacta en que cada estado financiero estuvo disponible.

La utilización del año fiscal por sí sola no garantiza que toda la información hubiera sido pública exactamente al 31 de diciembre.

Este punto se considera una limitación del MVP y deberá formar parte de la evolución metodológica del proyecto.

---

## 46. Baseline

El primer modelo desarrollado es una regresión logística.

Este modelo se seleccionó como baseline porque permite:

- disponer de una referencia simple;
- interpretar coeficientes;
- verificar el pipeline;
- establecer métricas comparables;
- detectar problemas antes de utilizar modelos más complejos.

---

## 47. Preprocesamiento para el baseline

Para variables numéricas se utiliza:

- imputación mediante mediana;
- estandarización.

Para `SECTOR_CIIU` se utiliza:

- imputación mediante categoría más frecuente;
- One-Hot Encoding;
- manejo de categorías desconocidas.

Todo el preprocesamiento se ajusta únicamente con TRAIN.

---

## 48. Desbalance de clases

El dataset presenta una prevalencia positiva extremadamente baja.

Por esta razón el Baseline v1 utiliza:

`class_weight="balanced"`

La ponderación permite reducir la tendencia de la regresión logística a favorecer exclusivamente la clase negativa.

---

## 49. Consecuencia de class_weight

Debido al uso de `class_weight="balanced"`, los valores generados por `predict_proba()` no deben interpretarse todavía como probabilidades reales calibradas.

En esta etapa se utilizan principalmente como:

- score;
- criterio de ordenamiento;
- base para construir rankings.

La calibración se evaluará posteriormente.

---

## 50. Métricas

Las métricas generales utilizadas son:

- PR-AUC;
- ROC-AUC;
- Precision;
- Recall;
- F1.

Debido al fuerte desbalance, Accuracy no se utiliza como criterio principal.

---

## 51. Métricas de ranking

El objetivo operacional del proyecto es priorizar empresas.

Por esta razón se utilizan además:

- Precision@K;
- Recall@K;
- Lift@K.

Inicialmente se evalúan:

- K = 50;
- K = 100;
- K = 200.

---

## 52. Uso de TEST

El conjunto TEST 2022–2023 fue utilizado para la evaluación final del Baseline v1.

Después de observar estos resultados, los experimentos siguientes no utilizan TEST para seleccionar alternativas.

Los experimentos v2 y v3 se evaluaron utilizando:

- TRAIN;
- VALIDATION.

Los análisis gráficos y de errores posteriores sobre TEST reproducen resultados del Baseline v1 ya fijado y no se utilizan para modificar retrospectivamente su configuración.

---

## 53. Flujo completo del MVP

El pipeline actual puede resumirse como:

1. Obtener datos financieros originales.
2. Obtener información histórica de emisores.
3. Inventariar estructuras.
4. Identificar planes contables.
5. Homologar cuentas.
6. Construir dataset financiero común.
7. Ejecutar validaciones contables.
8. Determinar primera inscripción como emisor.
9. Definir elegibilidad por empresa y año.
10. Construir `TARGET_24M`.
11. Construir variables financieras.
12. Construir variable sectorial.
13. Dividir cronológicamente.
14. Ajustar preprocesamiento con TRAIN.
15. Entrenar baseline.
16. Evaluar TRAIN.
17. Evaluar VALIDATION.
18. Evaluar TEST para el Baseline v1.
19. Calcular métricas de ranking.
20. Analizar errores.
21. Documentar resultados.
22. Comparar nuevos experimentos únicamente con TRAIN y VALIDATION durante selección.

---

## 54. Archivos principales del pipeline

### Homologación

`src/data/build_scvs_harmonized_dataset.py`

### Validación

`src/data/validate_scvs_harmonized_dataset.py`

### Construcción del target

`src/data/build_mvp_labeled_dataset.py`

### Ingeniería de variables

`src/features/build_mvp_features.py`

### Entrenamiento del Baseline v1

`src/models/train_logistic_baseline.py`

### Generación de gráficos

`src/evaluation/generate_baseline_figures.py`

### Análisis de errores

`src/evaluation/analyze_baseline_errors.py`

---

## 55. Productos principales

### Dataset armonizado

`data/interim/scvs_financials_harmonized_2015_2023.csv.gz`

### Dataset etiquetado

`data/processed/mvp_labeled_2015_2023.csv.gz`

### Dataset de features

`data/processed/mvp_features_2015_2023.csv.gz`

Los datasets no se almacenan en Git.

---

## 56. Separación de datos

El proyecto distingue:

### Raw

`data/raw/`

Contiene datos originales.

### Interim

`data/interim/`

Contiene productos intermedios.

### Processed

`data/processed/`

Contiene datasets preparados para modelado.

Esta estructura permite conservar los archivos originales y reproducir progresivamente las transformaciones.

---

## 57. Resultados reproducibles

Las métricas agregadas de los experimentos se almacenan en:

`reports/results/`

Las visualizaciones se almacenan en:

`reports/figures/`

Los modelos serializados reconstruibles se almacenan localmente en:

`models/`

---

## 58. Datos no versionados

Los datasets originales, intermedios y procesados no se publican en Git.

Las razones principales son:

- tamaño;
- manejo responsable de información;
- separación entre código y datos;
- existencia de información interna de BVQ que no debe publicarse.

El repositorio versiona principalmente:

- código;
- configuraciones;
- documentación;
- métricas agregadas;
- figuras;
- decisiones metodológicas.

---

## 59. Reproducibilidad

La reproducción del pipeline requiere:

- acceso a los archivos originales;
- Python y dependencias correspondientes;
- archivo de homologación;
- scripts versionados;
- ejecución de las etapas en el orden definido.

Las versiones exactas de las dependencias se mantienen en:

- `requirements.txt`;
- `requirements-lock.txt`.

---

## 60. Orden de ejecución

Desde la raíz del proyecto:

### Paso 1

Construir el dataset armonizado:

`python src/data/build_scvs_harmonized_dataset.py`

### Paso 2

Validar la homologación:

`python src/data/validate_scvs_harmonized_dataset.py`

### Paso 3

Construir el dataset etiquetado:

`python src/data/build_mvp_labeled_dataset.py`

### Paso 4

Construir las features:

`python src/features/build_mvp_features.py`

### Paso 5

Entrenar el Baseline v1:

`python src/models/train_logistic_baseline.py`

### Paso 6

Generar figuras:

`python src/evaluation/generate_baseline_figures.py`

### Paso 7

Ejecutar análisis de errores:

`python src/evaluation/analyze_baseline_errors.py`

---

## 61. Principios de calidad aplicados

El pipeline incorpora:

- conservación de datos originales;
- reglas explícitas de transformación;
- homologación configurable;
- validaciones contables;
- separación temporal;
- registro de métricas;
- documentación de experimentos;
- control de versiones;
- análisis de errores;
- comparación contra baseline.

---

## 62. Limitaciones actuales

Las principales limitaciones son:

1. fuerte desbalance de clases;
2. únicamente 440 eventos positivos;
3. variación temporal en la prevalencia;
4. dependencia actual de variables financieras principalmente estáticas;
5. falta de variables de crecimiento;
6. falta de variables de tendencia;
7. necesidad de mejorar el control de fecha efectiva de disponibilidad;
8. posible inestabilidad de algunas categorías sectoriales;
9. ausencia todavía de fuentes externas adicionales;
10. ausencia de calibración de scores;
11. necesidad de evaluar modelos no lineales.

---

## 63. Próximas mejoras del pipeline

Las siguientes etapas deberán considerar:

- crecimiento interanual;
- tendencias de dos y tres años;
- variación del endeudamiento;
- evolución de liquidez;
- evolución de utilidad;
- estabilidad de resultados;
- modelos basados en árboles;
- Gradient Boosting;
- CatBoost;
- Random Forest;
- posteriormente MLP;
- calibración de probabilidades;
- interpretabilidad;
- nuevas fuentes;
- control más preciso de disponibilidad temporal.

---

## 64. Relación con el problema de la BVQ

El pipeline transforma un universo amplio de empresas en una base estructurada que puede utilizarse para priorización.

El objetivo no es decidir automáticamente qué empresas deben convertirse en emisores.

El sistema busca apoyar un proceso humano de prospección permitiendo:

- analizar un universo amplio;
- utilizar criterios homogéneos;
- generar rankings;
- orientar recursos comerciales;
- identificar empresas que requieren análisis posterior.

---

## 65. Uso responsable

Los datos y resultados del pipeline se utilizan actualmente con fines académicos, experimentales y de investigación.

Los resultados:

- no constituyen recomendaciones de inversión;
- no determinan automáticamente la admisión de un emisor;
- no sustituyen el análisis de especialistas;
- no deben utilizarse como criterio único de decisión;
- deben interpretarse considerando sus limitaciones.

Los resultados versionados de evaluación no incluyen identificadores individuales de empresas.

---

## 66. Estado actual

El pipeline del MVP permite actualmente:

- cargar información financiera histórica;
- armonizar diferentes estructuras contables;
- validar consistencia;
- construir una unidad empresa-año;
- identificar el primer evento de inscripción como emisor;
- construir `TARGET_24M`;
- generar variables financieras;
- crear una división temporal;
- entrenar un baseline;
- calcular métricas;
- generar rankings;
- analizar errores;
- comparar experimentos.

La siguiente fase del proyecto se orienta a enriquecer las variables, evaluar modelos no lineales y mejorar la capacidad de priorización temporal del sistema.