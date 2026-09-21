# Prospect Finder BVQ

## Sistema inteligente para identificar y priorizar potenciales emisores del mercado de valores ecuatoriano

### Proyecto de Maestría en Inteligencia Artificial

**Integrantes:**

- Marcelo David Aguilar Salguero
- Francisco Xavier Meneses Játiva
- Luis Miguel Gallardo Dávila

---

## 1. Descripción del proyecto

Prospect Finder BVQ es un proyecto de inteligencia artificial orientado a apoyar el proceso de prospección de potenciales emisores para la Bolsa de Valores Quito (BVQ).

El problema organizacional identificado es la dificultad para analizar de manera sistemática un universo amplio de empresas ecuatorianas, aplicar criterios homogéneos de evaluación y priorizar aquellas que podrían presentar mayor afinidad con el mercado de valores.

La solución propuesta busca construir un sistema que permita analizar información histórica de las empresas y generar un ranking de prospectos que sirva como apoyo para la gestión comercial y financiera de la BVQ.

El sistema no pretende tomar decisiones automáticas sobre qué empresas deben convertirse en emisores. Su propósito es reducir y priorizar el universo de análisis para apoyar la revisión posterior realizada por especialistas.

---

## 2. Objetivo del prototipo

Desarrollar un prototipo mínimo viable capaz de identificar patrones financieros asociados históricamente con empresas que posteriormente se registraron como emisores del mercado de valores ecuatoriano.

La unidad de análisis es `empresa-año`.

La variable objetivo es `TARGET_24M`, donde:

- **1:** la empresa se registra por primera vez como emisor dentro de los siguientes 24 meses.
- **0:** la empresa no se registra como nuevo emisor dentro de ese horizonte.

Las empresas que ya eran emisoras en la fecha de corte correspondiente son excluidas del universo elegible.

---

## 3. Fuentes de información

### 3.1 Superintendencia de Compañías, Valores y Seguros — Estados financieros

Es la fuente principal utilizada para construir las variables predictoras.

**Período utilizado:** 2015–2023.

**Información utilizada:**

- estados de situación financiera;
- cuentas contables;
- información financiera histórica por empresa;
- identificación de empresa;
- clasificación CIIU.

**Formatos de origen:** archivos comprimidos y archivos de texto publicados por la SCVS.

Los archivos originales se conservan sin modificaciones en:

`data/raw/scvs/estados_financieros/`

### 3.2 Superintendencia de Compañías, Valores y Seguros — Registro del Mercado de Valores

Es la fuente utilizada para construir la variable objetivo.

Los principales archivos utilizados son:

- `listado_entes_65001_1789908466941.xlsx`
- `codigos_fichas_registrales_1789908530079.xlsx`

Ubicación local:

`data/raw/scvs/mercado_valores/`

La fecha de primera inscripción como emisor se utiliza para determinar si una empresa se convierte en nuevo emisor dentro del horizonte de 24 meses.

La fuente principal fue validada contra la información de fichas registrales. Para los 619 RUC de emisores identificados, las fechas de primera inscripción coincidieron entre las dos fuentes utilizadas.

### 3.3 Bolsa de Valores Quito — Data Warehouse

La información interna de la BVQ se considera una fuente complementaria de validación y potencial enriquecimiento.

Entre los extractos disponibles se encuentra información de balances y resultados financieros.

Esta información no constituye la fuente principal de las variables utilizadas por el Baseline v1.

Los datos internos de la BVQ no se publican en el repositorio.

### 3.4 Resumen de fuentes

| Fuente | Formato principal | Información utilizada | Uso |
|---|---|---|---|
| SCVS — Estados financieros | ZIP / TXT | Estados financieros, cuentas, CIIU | Variables predictoras |
| SCVS — Registro del Mercado de Valores | XLSX | Primera inscripción como emisor | Construcción de `TARGET_24M` |
| BVQ — Data Warehouse | CSV / base de datos | Información financiera complementaria | Validación y enriquecimiento futuro |

### Condiciones de acceso y reutilización

Las fuentes públicas utilizadas para el MVP fueron obtenidas de los portales institucionales de la Superintendencia de Compañías, Valores y Seguros (SCVS).

En la revisión documental realizada para esta entrega no se identificó una licencia abierta específica aplicable a los archivos de estados financieros y del Registro del Mercado de Valores utilizados, como Creative Commons u Open Data Commons. Por esta razón, el proyecto no atribuye a estas fuentes una licencia de reutilización que no haya sido publicada explícitamente y mantiene a la SCVS como fuente original de la información.

La información proveniente del Data Warehouse y de otras fuentes internas de la Bolsa de Valores Quito se considera información institucional de acceso interno. No se publica ni redistribuye mediante el repositorio del proyecto.

La ausencia de una licencia abierta identificada no se interpreta como autorización irrestricta de reutilización. Antes de publicar externamente datasets derivados o utilizar la información con otros fines deberán verificarse nuevamente las condiciones institucionales y normativas aplicables.

**Fecha de verificación documental:** 20 de septiembre de 2026.

El detalle de fuentes, condiciones de acceso y tratamiento se encuentra en:

`docs/inventario_fuentes.md`

---

## 4. Consideraciones sobre los datos

Los estados financieros de la SCVS presentan diferentes estructuras contables a lo largo del período analizado.

Por esta razón fue necesario construir un proceso de homologación entre diferentes planes contables.

Se utilizaron las siguientes estructuras principales:

- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

`PLAN_413` fue excluido del MVP debido a su baja cobertura y ausencia de eventos positivos en las cohortes evaluadas.

Los archivos de datos originales y derivados no se versionan en Git debido a su tamaño y a consideraciones de manejo responsable de información.

---

## 5. Pipeline de datos

El proceso implementado sigue las siguientes etapas:

```text
Datos SCVS
    ↓
Inventario y análisis de formatos
    ↓
Homologación de cuentas contables
    ↓
Validaciones contables
    ↓
Construcción del dataset empresa-año
    ↓
Construcción de TARGET_24M
    ↓
Ingeniería de variables
    ↓
División temporal
    ↓
Entrenamiento del baseline
    ↓
Evaluación
    ↓
Análisis de errores
    ↓
Resultados y próximos experimentos
```

La documentación detallada se encuentra en:

`docs/pipeline_datos_mvp.md`

---

## 6. Dataset financiero armonizado

El proceso de homologación produjo:

- **887.469 observaciones empresa-año**
- **166.389 empresas únicas**
- período **2015–2023**

Archivo generado localmente:

`data/interim/scvs_financials_harmonized_2015_2023.csv.gz`

Este archivo no se almacena en Git.

---

## 7. Variables financieras homologadas

Se homologaron nueve variables financieras principales:

| Variable | Tipo | Descripción |
|---|---|---|
| `ACTIVO_TOTAL` | Numérica | Total de activos |
| `ACTIVO_CORRIENTE` | Numérica | Total de activos corrientes |
| `EFECTIVO` | Numérica | Efectivo y equivalentes |
| `PASIVO_TOTAL` | Numérica | Total de pasivos |
| `PASIVO_CORRIENTE` | Numérica | Pasivos corrientes |
| `PASIVO_NO_CORRIENTE` | Numérica | Pasivos no corrientes |
| `PATRIMONIO` | Numérica | Patrimonio de la empresa |
| `CAPITAL` | Numérica | Capital registrado |
| `UTILIDAD_NETA` | Numérica | Resultado neto del período |

El detalle de variables, fórmulas, disponibilidad y tratamiento de faltantes se documenta en:

`docs/diccionario_datos.md`

---

## 8. Validación de la homologación contable

Se verificaron las principales ecuaciones contables.

### Activo = Pasivo + Patrimonio

El **99,24 %** de las observaciones presentó una diferencia relativa menor o igual al 0,01 %.

### Pasivo total = Pasivo corriente + Pasivo no corriente

El **99,31 %** de las observaciones presentó una diferencia relativa menor o igual al 0,01 %.

Estas verificaciones permiten evaluar la consistencia de la homologación realizada entre los diferentes planes contables.

---

## 9. Dataset etiquetado

Después de excluir las empresas que ya eran emisoras en cada fecha de corte, el dataset utilizado para modelado contiene:

| Indicador | Resultado |
|---|---:|
| Observaciones empresa-año | 884.072 |
| Empresas únicas | 166.107 |
| `TARGET_24M = 1` | 440 |
| `TARGET_24M = 0` | 883.632 |
| Prevalencia aproximada | 0,0498 % |

Archivo local:

`data/processed/mvp_labeled_2015_2023.csv.gz`

El dataset presenta un desbalance extremo entre la clase positiva y negativa.

---

## 10. Ingeniería de variables

### 10.1 Transformaciones monetarias

Para reducir el efecto de escala se aplica una transformación logarítmica con signo:

`sign(x) × log(1 + |x|)`

Variables generadas:

- `LOG_ACTIVO_TOTAL`
- `LOG_ACTIVO_CORRIENTE`
- `LOG_EFECTIVO`
- `LOG_PASIVO_TOTAL`
- `LOG_PASIVO_CORRIENTE`
- `LOG_PASIVO_NO_CORRIENTE`
- `LOG_PATRIMONIO`
- `LOG_CAPITAL`
- `LOG_UTILIDAD_NETA`

### 10.2 Razones financieras

| Variable | Tipo | Descripción |
|---|---|---|
| `LIQUIDEZ_CORRIENTE` | Numérica | Activo corriente / pasivo corriente |
| `ENDEUDAMIENTO` | Numérica | Pasivo total / activo total |
| `AUTONOMIA_FINANCIERA` | Numérica | Patrimonio / activo total |
| `ROA` | Numérica | Utilidad neta / activo total |
| `EFECTIVO_ACTIVOS` | Numérica | Efectivo / activo total |
| `CAPITAL_ACTIVOS` | Numérica | Capital / activo total |
| `PASIVO_CORRIENTE_PASIVO` | Numérica | Pasivo corriente / pasivo total |

Cuando el denominador es igual a cero, el valor se conserva como faltante para ser tratado posteriormente dentro del pipeline de preprocesamiento.

### 10.3 Variable categórica

| Variable | Tipo | Descripción |
|---|---|---|
| `SECTOR_CIIU` | Categórica | Primera sección de la clasificación CIIU |

### 10.4 Variable objetivo

| Variable | Tipo | Descripción |
|---|---|---|
| `TARGET_24M` | Binaria | Indica si la empresa se registra por primera vez como emisor dentro de los siguientes 24 meses |

---

## 11. Disponibilidad de variables

Las nueve variables financieras base homologadas presentan cobertura completa en el dataset armonizado utilizado para el MVP. Sus transformaciones logarítmicas se derivan de estas variables.

Las razones financieras presentan las siguientes disponibilidades aproximadas:

| Variable | Disponibilidad |
|---|---:|
| `LIQUIDEZ_CORRIENTE` | 68,04 % |
| `ENDEUDAMIENTO` | 95,81 % |
| `AUTONOMIA_FINANCIERA` | 95,81 % |
| `ROA` | 95,81 % |
| `EFECTIVO_ACTIVOS` | 95,81 % |
| `CAPITAL_ACTIVOS` | 95,81 % |
| `PASIVO_CORRIENTE_PASIVO` | 71,03 % |
| `SECTOR_CIIU` | 99,98 % |

Los valores faltantes de variables numéricas se tratan mediante imputación basada exclusivamente en TRAIN.

---

## 12. División temporal

No se utiliza una partición aleatoria.

El dataset se divide cronológicamente:

| Conjunto | Período | Observaciones | Positivos | Prevalencia |
|---|---|---:|---:|---:|
| TRAIN | 2015–2020 | 514.527 | 340 | 0,0661 % |
| VALIDATION | 2021 | 109.101 | 42 | 0,0385 % |
| TEST | 2022–2023 | 260.444 | 58 | 0,0223 % |

El objetivo es simular un escenario real en el que el modelo aprende con información histórica y posteriormente prioriza empresas en períodos futuros.

Todo el preprocesamiento se ajusta exclusivamente utilizando TRAIN.

---

## 13. Modelo baseline

El modelo de referencia es una **regresión logística**.

Configuración del Baseline v1:

| Parámetro | Valor |
|---|---|
| `C` | 1.0 |
| `class_weight` | balanced |
| `solver` | lbfgs |
| `max_iter` | 2000 |
| `random_state` | 42 |
| Regularización | L2 |

El modelo convergió en 92 iteraciones.

Script:

`src/models/train_logistic_baseline.py`

---

## 14. Preprocesamiento

### Variables numéricas

Se utilizan:

- `SimpleImputer(strategy="median")`
- `StandardScaler()`

### Variable categórica

Se utilizan:

- `SimpleImputer(strategy="most_frequent")`
- `OneHotEncoder(handle_unknown="ignore")`

Todos los parámetros del preprocesamiento se ajustan únicamente utilizando TRAIN para evitar contaminación de información entre conjuntos.

---

## 15. Métricas de evaluación

Debido al fuerte desbalance de clases, `Accuracy` no se utiliza como métrica principal.

Las métricas técnicas utilizadas son:

- PR-AUC
- ROC-AUC
- Precision
- Recall
- F1

Para evaluar la utilidad del sistema como herramienta de prospección se utilizan además:

- Precision@K
- Recall@K
- Lift@K

Los valores inicialmente evaluados son:

- K = 50
- K = 100
- K = 200

---

## 16. Resultados del Baseline v1

| Conjunto | PR-AUC | ROC-AUC | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|
| TRAIN | 0,099413 | 0,946436 | 0,004494 | 0,894118 | 0,008942 |
| VALIDATION | 0,031095 | 0,940593 | 0,002566 | 0,880952 | 0,005118 |
| TEST | 0,007291 | 0,927740 | 0,000627 | 0,931034 | 0,001254 |

El ROC-AUC permanece por encima de 0,92 en los tres conjuntos.

Sin embargo, debido al fuerte desbalance, PR-AUC y las métricas de ranking son más representativas para evaluar la utilidad del modelo.

Se observa una reducción temporal del PR-AUC:

- TRAIN: 0,099413
- VALIDATION: 0,031095
- TEST: 0,007291

---

## 17. Matriz de confusión

Utilizando inicialmente un threshold de 0,50:

### VALIDATION

| Resultado | Cantidad |
|---|---:|
| Verdaderos positivos | 37 |
| Falsos negativos | 5 |
| Falsos positivos | 14.381 |
| Verdaderos negativos | 94.678 |

### TEST

| Resultado | Cantidad |
|---|---:|
| Verdaderos positivos | 54 |
| Falsos negativos | 4 |
| Falsos positivos | 86.032 |
| Verdaderos negativos | 174.354 |

El elevado número de falsos positivos muestra que el threshold 0,50 no es adecuado como regla operativa de prospección.

Por esta razón el proyecto se orienta principalmente hacia un problema de **ranking y priorización**.

---

## 18. Resultados de ranking

### TRAIN

| K | Positivos | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 24 | 0,4800 | 0,0706 | 726,39 |
| 100 | 42 | 0,4200 | 0,1235 | 635,59 |
| 200 | 59 | 0,2950 | 0,1735 | 446,43 |

### VALIDATION

| K | Positivos | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 5 | 0,1000 | 0,1190 | 259,76 |
| 100 | 5 | 0,0500 | 0,1190 | 129,88 |
| 200 | 5 | 0,0250 | 0,1190 | 64,94 |

### TEST

| K | Positivos | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 1 | 0,0200 | 0,0172 | 89,81 |
| 100 | 2 | 0,0200 | 0,0345 | 89,81 |
| 200 | 3 | 0,0150 | 0,0517 | 67,36 |

El modelo concentra futuros emisores por encima de una selección aleatoria, pero presenta una degradación temporal significativa.

---

## 19. Uso del conjunto TEST

TEST 2022–2023 fue utilizado para la evaluación final del Baseline v1.

Los análisis gráficos y de errores posteriores reproducen resultados del mismo modelo ya fijado y no fueron utilizados para modificar retrospectivamente sus parámetros.

Los experimentos v2 y v3 fueron evaluados utilizando únicamente TRAIN y VALIDATION para tomar decisiones de selección.

---

## 20. Experimentos realizados

### 20.1 Baseline v1

Regresión logística utilizando variables financieras y `SECTOR_CIIU`.

**Estado:** modelo de referencia vigente.

Documentación:

`docs/baseline_v1.md`

### 20.2 Baseline v2 — Sin sector CIIU

Se eliminó `SECTOR_CIIU` para evaluar si la variable sectorial estaba generando inestabilidad.

Resultados principales en VALIDATION:

| Métrica | v1 | v2 |
|---|---:|---:|
| PR-AUC | 0,031095 | 0,024402 |
| ROC-AUC | 0,940593 | 0,961619 |
| Precision@50 | 0,1000 | 0,0800 |
| Recall@50 | 0,1190 | 0,0952 |

La eliminación de la información sectorial no mejoró las métricas prioritarias.

Documentación:

`docs/baseline_v2.md`

### 20.3 Experimento v3 — Regularización

Se evaluaron:

- C = 0,001
- C = 0,01
- C = 0,1
- C = 1
- C = 10

El mayor PR-AUC en VALIDATION fue:

- C = 10 → 0,031135
- C = 1 → 0,031095

La diferencia absoluta fue únicamente 0,000040 y los resultados Top 50, Top 100 y Top 200 fueron iguales.

No se consideró una mejora material.

Documentación:

`docs/baseline_v3.md`

---

## 21. Modelo de referencia vigente

Después de los experimentos realizados se mantiene:

- Modelo: Regresión logística
- C = 1.0
- `class_weight = balanced`
- `SECTOR_CIIU` incluido
- Regularización L2

como Baseline v1 de referencia.

---

## 22. Análisis de errores

Script:

`src/evaluation/analyze_baseline_errors.py`

Se analizaron:

- verdaderos positivos;
- falsos positivos;
- falsos negativos;
- verdaderos negativos;
- posiciones de los futuros emisores en el ranking;
- sectores asociados a errores;
- perfiles financieros agregados.

### VALIDATION

- Mejor posición positiva: 7
- Mediana de posición positiva: 2.362
- Peor posición positiva: 64.033
- Top 1.000: 10 de 42 positivos
- Recall@1000: 23,81 %

### TEST

- Mejor posición positiva: 50
- Mediana de posición positiva: 4.317
- Peor posición positiva: 160.698
- Top 1.000: 10 de 58 positivos
- Recall@1000: 17,24 %

Los resultados muestran que existe señal predictiva, pero la capacidad de concentración disminuye en períodos posteriores.

---

## 23. Comportamientos observados en falsos negativos

En VALIDATION, los falsos negativos presentan, en términos medianos:

- menor tamaño;
- mayor liquidez;
- menor endeudamiento;
- mayor autonomía financiera.

En TEST se identificaron cuatro falsos negativos con un perfil financiero atípico respecto al patrón predominante del modelo.

Estos resultados son descriptivos y no permiten establecer relaciones causales.

---

## 24. Figuras generadas

Las visualizaciones se encuentran en:

`reports/figures/`

Archivos:

- `baseline_01_distribucion_clases.png`
- `baseline_02_precision_recall.png`
- `baseline_03_confusion_matrix_validation.png`
- `baseline_04_confusion_matrix_test.png`
- `baseline_05_positivos_top_k.png`
- `baseline_06_lift_top_k.png`
- `baseline_07_precision_top_k.png`

---

## 25. Herramientas y entorno tecnológico

| Herramienta | Uso |
|---|---|
| Python 3.13.7 | Desarrollo del pipeline |
| pandas 3.0.5 | Procesamiento y análisis de datos |
| NumPy 2.5.3 | Operaciones numéricas |
| scikit-learn 1.9.1 | Preprocesamiento, modelos y métricas |
| SciPy 1.18.1 | Dependencias científicas |
| Matplotlib 3.11.1 | Visualización |
| joblib 1.6.0 | Persistencia local de modelos |
| openpyxl 3.1.5 | Lectura de archivos Excel |
| Git | Control de versiones |
| GitHub | Repositorio y trazabilidad |
| VS Code | Entorno de desarrollo |
| Jupyter | Exploración y validación |

Las versiones exactas del entorno están registradas en:

- `requirements.txt`
- `requirements-lock.txt`

---

## 26. Estructura del repositorio

```text
prospect-finder-bvq/
│
├── config/
│   └── scvs_account_mapping.csv
│
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── docs/
│   ├── backlog.md
│   ├── baseline_v1.md
│   ├── baseline_v2.md
│   ├── baseline_v3.md
│   ├── bitacora.md
│   ├── diccionario_datos.md
│   ├── entorno_tecnico.md
│   ├── informe_resultados_preliminares.md
│   ├── inventario_fuentes.md
│   └── pipeline_datos_mvp.md
│
├── models/
│
├── notebooks/
│   └── 00_validacion_entorno.ipynb
│
├── reports/
│   ├── figures/
│   └── results/
│
├── src/
│   ├── data/
│   ├── evaluation/
│   ├── features/
│   └── models/
│
├── .gitignore
├── README.md
├── requirements.txt
└── requirements-lock.txt
```

---

## 27. Reproducción del pipeline principal

### 27.1 Activar el entorno

Desde la carpeta raíz del proyecto en Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 27.2 Construir dataset armonizado

```powershell
python src/data/build_scvs_harmonized_dataset.py
```

### 27.3 Validar dataset armonizado

```powershell
python src/data/validate_scvs_harmonized_dataset.py
```

### 27.4 Construir dataset etiquetado

```powershell
python src/data/build_mvp_labeled_dataset.py
```

### 27.5 Construir features

```powershell
python src/features/build_mvp_features.py
```

### 27.6 Entrenar Baseline v1

```powershell
python src/models/train_logistic_baseline.py
```

### 27.7 Generar figuras

```powershell
python src/evaluation/generate_baseline_figures.py
```

### 27.8 Ejecutar análisis de errores

```powershell
python src/evaluation/analyze_baseline_errors.py
```

Los experimentos v2 y v3 están documentados de forma independiente en `docs/baseline_v2.md` y `docs/baseline_v3.md`.

---

## 28. Limitaciones actuales

Las principales limitaciones identificadas son:

1. Desbalance extremo de la variable objetivo.
2. Solo 440 eventos positivos en todo el período etiquetado.
3. Degradación temporal del rendimiento.
4. Bajo Recall@K en períodos recientes.
5. Variables principalmente estáticas.
6. Ausencia todavía de tendencias financieras interanuales.
7. Baseline basado en relaciones lineales.
8. Posible inestabilidad de algunas categorías sectoriales.
9. Probabilidades todavía no calibradas.
10. El threshold de 0,50 no es adecuado para uso operativo.
11. La fecha efectiva de disponibilidad de cada estado financiero deberá controlarse con mayor precisión.
12. Todavía no se han incorporado fuentes externas adicionales que puedan aportar señales de crecimiento o intención de acceso al mercado.

---

## 29. Backlog priorizado

El backlog técnico y metodológico completo se mantiene en:

`docs/backlog.md`

Este documento constituye la fuente principal para registrar prioridades, estados, objetivos y criterios de aceptación de las actividades pendientes.

Las líneas de trabajo prioritarias son:

| Prioridad | Línea de trabajo | Objetivo |
|---|---|---|
| Alta | Control temporal de disponibilidad de datos | Reducir el riesgo de data leakage |
| Alta | Variables temporales | Incorporar trayectoria financiera |
| Alta | Crecimiento interanual | Detectar evolución financiera |
| Alta | Tendencias multianuales | Capturar estabilidad y cambio |
| Alta | Gradient Boosting | Evaluar relaciones no lineales |
| Alta | CatBoost | Evaluar un modelo tabular adicional |
| Alta | Comparación contra Baseline v1 | Determinar si existe una mejora material |
| Media | Random Forest | Incorporar otro modelo tabular de referencia |
| Media | Tratamiento del desbalance | Mejorar el aprendizaje de la clase positiva |
| Media | Análisis de Top-K | Relacionar métricas con capacidad comercial |
| Media | Estabilidad temporal | Analizar degradación por cohortes |
| Media | Nuevas fuentes | Incorporar señales adicionales |
| Media | Calibración | Obtener scores más interpretables |
| Media | Interpretabilidad | Explicar la priorización |
| Media | Índice de Afinidad Bursátil | Construir el indicador final |
| Baja | MLP | Evaluar posteriormente una red neuronal |
| Baja | Visualización y monitoreo | Preparar una futura aplicación operativa |

El diccionario de datos, anteriormente considerado una actividad pendiente, ya fue formalizado en:

`docs/diccionario_datos.md`

---

## 30. Próximas líneas de mejora

### Variables temporales

Se evaluará la construcción de:

- crecimiento de activos;
- crecimiento de patrimonio;
- variación del endeudamiento;
- variación de liquidez;
- crecimiento de utilidad;
- estabilidad de resultados;
- tendencia de dos y tres años;
- crecimiento acumulado.

### Modelos no lineales

Se evaluarán:

- Gradient Boosting;
- CatBoost;
- Random Forest.

### Redes neuronales

Se evaluará posteriormente una red neuronal multicapa o MLP.

Debido al reducido número de positivos, será necesario controlar cuidadosamente:

- sobreajuste;
- arquitectura;
- regularización;
- ponderación de clases;
- validación temporal.

### Nuevas fuentes

Después de explotar las variables históricas disponibles se podrá evaluar información adicional proveniente de:

- SCVS;
- información interna de BVQ;
- fuentes públicas empresariales;
- variables sectoriales;
- variables macroeconómicas.

Toda fuente adicional deberá cumplir la condición de haber estado disponible antes de la fecha de predicción para evitar data leakage.

---

## 31. Calibración e Índice de Afinidad Bursátil

Los valores actuales generados por `predict_proba()` no se interpretan como probabilidades reales debido al uso de `class_weight="balanced"`.

Por esta razón todavía no se utilizan directamente como Índice de Afinidad Bursátil.

Después de seleccionar un modelo con desempeño adecuado se evaluarán técnicas de calibración.

Posteriormente se podrá definir formalmente el:

**Índice de Afinidad Bursátil (IAB)**

como mecanismo de priorización para el usuario final.

---

## 32. Uso responsable

El proyecto se desarrolla actualmente con fines académicos, de investigación y de validación de un prototipo.

Los resultados del modelo:

- no constituyen recomendaciones de inversión;
- no determinan automáticamente la aceptación de una empresa como emisor;
- no sustituyen el análisis financiero, legal o comercial realizado por especialistas;
- no deben utilizarse como único criterio para tomar decisiones comerciales;
- no deben interpretarse como probabilidades reales mientras el modelo no haya sido calibrado.

Los resultados agregados versionados en el repositorio no incluyen nombres de empresas, RUC ni predicciones individuales.

Los datasets originales y derivados no son publicados en Git.

El uso de información debe respetar las condiciones de las fuentes originales y las políticas institucionales aplicables.

---

## 33. Reproducibilidad y trazabilidad

El proyecto utiliza:

- Git para control de versiones;
- GitHub como repositorio remoto;
- `random_state = 42` en los procesos que requieren control de aleatoriedad;
- `requirements.txt`;
- `requirements-lock.txt`;
- scripts separados por etapa;
- resultados agregados versionados;
- documentación técnica por experimento;
- bitácora de cambios y decisiones;
- backlog priorizado;
- diccionario de datos;
- inventario de fuentes.

Cada experimento se registra de forma independiente para evitar modificar retrospectivamente los resultados obtenidos.

Los principales experimentos documentados son:

- Baseline v1;
- Baseline v2;
- Experimento v3.

La bitácora del proyecto se encuentra en:

`docs/bitacora.md`

El backlog se encuentra en:

`docs/backlog.md`

---

## 34. Documentación disponible

### Pipeline de datos

`docs/pipeline_datos_mvp.md`

### Entorno técnico

`docs/entorno_tecnico.md`

### Inventario de fuentes

`docs/inventario_fuentes.md`

### Diccionario de datos

`docs/diccionario_datos.md`

### Bitácora del proyecto

`docs/bitacora.md`

### Backlog priorizado

`docs/backlog.md`

### Baseline v1

`docs/baseline_v1.md`

### Baseline v2

`docs/baseline_v2.md`

### Experimento v3

`docs/baseline_v3.md`

### Informe de resultados preliminares

`docs/informe_resultados_preliminares.md`

---

## 35. Estado actual del proyecto

| Componente | Estado |
|---|---|
| Estructura del repositorio | Completada |
| Entorno técnico | Documentado |
| Inventario de fuentes | Completado |
| Diccionario de datos | Completado |
| Bitácora del proyecto | Completada y en mantenimiento |
| Backlog priorizado | Completado y en mantenimiento |
| Homologación contable | Completada para MVP |
| Dataset armonizado | Completado |
| Validación contable | Completada |
| Target `TARGET_24M` | Completado |
| Ingeniería inicial de variables | Completada |
| División temporal | Completada |
| Baseline v1 | Completado |
| Baseline v2 | Completado |
| Experimento v3 | Completado |
| Figuras | Generadas |
| Análisis de errores | Completado |
| Informe preliminar | Elaborado |
| Control temporal de disponibilidad | Pendiente de fortalecimiento |
| Variables temporales | Pendiente |
| Modelos no lineales | Pendiente |
| Red neuronal | Pendiente |
| Calibración | Pendiente |
| IAB definitivo | Pendiente |

**Modelo de referencia vigente:** Baseline v1.

El proyecto continúa en fase experimental y los resultados obtenidos hasta el momento deben considerarse preliminares.
