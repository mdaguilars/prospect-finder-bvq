# Prospect Finder BVQ

## Sistema basado en aprendizaje automático para identificar y priorizar empresas con potencial de convertirse en emisores del mercado de valores ecuatoriano

### Proyecto de Maestría en Inteligencia Artificial

**Universidad de Las Américas — UDLA**

**Integrantes:**
- Marcelo David Aguilar Salguero
- Francisco Xavier Meneses Játiva
- Luis Miguel Gallardo Dávila

---

## Evidencia final v10

Para facilitar la revisión académica y técnica de la versión final, se consolidó un índice único de evidencias:

`docs/v10_evidence_index.md`

Este índice enlaza la selección del modelo, comparación LR/HGB/MLP, TEST congelado, evaluación Top-K, pruebas P01–P06, pruebas funcionales, validación con especialistas y demo reproducible para evaluadores.

---

## 1. Descripción del proyecto

**Prospect Finder BVQ** es una solución de inteligencia artificial orientada a apoyar el proceso de prospección de potenciales emisores para la **Bolsa de Valores de Quito (BVQ)**.

El problema organizacional identificado es la dificultad para analizar sistemáticamente un universo amplio de empresas ecuatorianas, aplicar criterios homogéneos de evaluación y priorizar aquellas que presentan características históricamente asociadas con empresas que posteriormente ingresaron al mercado de valores como emisores.

Prospect Finder transforma este universo en un **ranking de priorización**, acompañado de información financiera, explicaciones del modelo y empresas históricas comparables.

Su propósito no es reemplazar al especialista ni determinar automáticamente qué empresa debe convertirse en emisor.

> **Modelo → Priorización → Especialista → Decisión**

La decisión final permanece bajo revisión humana.

---

## 2. Objetivo

Desarrollar un prototipo basado en aprendizaje automático que permita identificar patrones asociados históricamente con empresas que posteriormente se registraron por primera vez como emisores del mercado de valores ecuatoriano.

La solución busca:
- reducir el universo inicial de análisis;
- aplicar criterios cuantitativos consistentes;
- identificar señales financieras relevantes;
- priorizar empresas mediante un ranking;
- explicar los principales factores asociados con cada resultado;
- presentar empresas emisoras históricas comparables;
- apoyar la gestión comercial y de prospección de la BVQ.

---

## 3. Formulación del problema

Prospect Finder BVQ se aborda principalmente como un problema de **ranking y priorización**, y no únicamente como una clasificación binaria convencional.

La unidad de análisis utilizada durante el entrenamiento es `empresa-año`.

La variable objetivo es `TARGET_24M`, donde:
- **1:** la empresa se registra por primera vez como emisor dentro de los siguientes 24 meses a partir de la fecha de decisión;
- **0:** la empresa no se registra como nuevo emisor dentro de ese horizonte.

Las empresas que ya habían sido emisoras antes de la fecha de decisión son excluidas del universo elegible.

El score generado por el modelo **no es una probabilidad calibrada**. Por ejemplo, `score = 0.90` no significa que la empresa tenga un 90 % de probabilidad de convertirse en emisor. Debe interpretarse como un **valor relativo de priorización**.

---

## 4. Fuentes de información

### 4.1 Superintendencia de Compañías, Valores y Seguros — Información financiera y societaria

La principal fuente pública para construir las variables financieras y empresariales es la SCVS.

La generación final v10 utiliza principalmente:

`data/raw/scvs/ranking/bi_ranking.csv`

con cobertura **2012–2023**.

La identificación empresarial se complementa mediante:

`data/raw/scvs/catalogos/bi_compania.csv`

### 4.2 Registro del Mercado de Valores

Esta fuente se utiliza para identificar la primera inscripción histórica de una empresa como emisor y construir `TARGET_24M`.

Principales archivos:
- `listado_entes_65001_1789908466941.xlsx`
- `codigos_fichas_registrales_1789908530079.xlsx`

La validación identificó **619 RUC efectivos de emisores históricos**, con coincidencia en las fechas de primera inscripción contrastadas.

### 4.3 Bolsa de Valores de Quito

La información interna de la BVQ se utiliza como fuente complementaria para validaciones, análisis institucional, interpretación y enriquecimiento futuro. Los datos internos no se publican en el repositorio.

### 4.4 Acceso y reutilización de datos

Los archivos originales y datasets procesados no se redistribuyen mediante GitHub.

El inventario detallado de fuentes se encuentra en:

`docs/inventario_fuentes.md`

---

## 5. Evolución metodológica

Las versiones v1–v9 permitieron validar progresivamente homologación contable, definición del target, disponibilidad temporal, períodos de embargo, ingeniería de variables, modelos lineales y no lineales, variables temporales, backtesting y estabilidad temporal.

La versión final del proyecto corresponde a **v10**.

| Versión | Modelo / cambio | Resultado metodológico |
|---|---|---|
| v1 | Logistic Regression | Baseline inicial |
| v2 | Logistic sin sector | Evaluación del aporte sectorial |
| v3 | Regularización | Evaluación de sensibilidad |
| v4 | Logistic temporal corregida | Corrección del protocolo temporal |
| v5 | Logistic sin sector | Comparación bajo nuevo protocolo |
| v6 | Logistic + variables temporales | Baseline temporal |
| v7 | HistGradientBoosting | Evidenció sobreajuste |
| v8 | HGB regularizado | Mejor benchmark del ciclo v4–v9 |
| v9 | MLP | Alternativa neuronal exploratoria |
| v10 | HistGradientBoosting financiero | Modelo final congelado |

---

## 6. Disponibilidad temporal

Para un ejercicio fiscal `t` se utiliza una regla conservadora:

| Concepto | Fecha |
|---|---|
| Ejercicio financiero | año `t` |
| Disponibilidad máxima asumida | `30/04/t+1` |
| Fecha de decisión | `01/05/t+1` |
| Inicio del horizonte objetivo | `01/05/t+1` |
| Fin del horizonte de 24 meses | `30/04/t+3` |

Esta fecha representa una **suposición normativa de disponibilidad** y no la fecha real individual de presentación de cada empresa.

---

## 7. Dataset base v10

Archivo local:

`data/processed/v10_base_integrated_2012_2023.csv.gz`

Script reproducible:

`scripts/build_v10_base.py`

Documento técnico:

`docs/v10_dataset_freeze.md`

### 7.1 Universo congelado

| Indicador | Resultado |
|---|---:|
| Unión inicial empresa-año | 1.035.294 |
| Filas excluidas sin RUC verificable | 535 |
| Observaciones excluidas por ser emisores previos | 4.088 |
| Observaciones elegibles finales | **1.030.671** |
| Positivos `TARGET_24M` | **568** |
| RUC positivos únicos | **310** |
| Prevalencia global | **0,055110 %** |
| Duplicados empresa-año | **0** |

### 7.2 Distribución anual

| Año | Elegibles | Positivos |
|---:|---:|---:|
| 2012 | 42.158 | 55 |
| 2013 | 47.140 | 49 |
| 2014 | 52.528 | 39 |
| 2015 | 76.468 | 43 |
| 2016 | 79.503 | 73 |
| 2017 | 83.107 | 89 |
| 2018 | 89.818 | 59 |
| 2019 | 91.934 | 34 |
| 2020 | 98.471 | 34 |
| 2021 | 109.099 | 39 |
| 2022 | 123.289 | 32 |
| 2023 | 137.156 | 22 |

### 7.3 Reproducibilidad

SHA-256 congelado:

`b44f9ccf309c20a59be436953a0c6e7f9a3dc1f11cc6f2c87e41c1676a3a2a8d`

Estado:

**BASE V10 CONGELADA**

---

## 8. Variables excluidas preventivamente

No se incorporaron al dataset final:
- `cia_imvalores`
- `id_estado_financiero`
- `posicion_general`

Las exclusiones responden a riesgo potencial de fuga de información, uso de identificadores técnicos y utilización de posiciones de ranking no apropiadas como predictor.

---

## 9. Feature Set final v10

El modelo final utiliza **25 variables**.

### Tamaño y actividad
1. `activos_final`
2. `patrimonio_final`
3. `bi_ingresos_ventas`
4. `bi_n_empleados`

### Información del período anterior
5. `activos_final_t1`
6. `patrimonio_final_t1`
7. `bi_ingresos_ventas_t1`
8. `bi_n_empleados_t1`

### Indicadores financieros
9. `fin_ratio_patrimonio_activos`
10. `fin_roa`
11. `fin_margen_neto`
12. `fin_rotacion_activos`
13. `fin_roe`

### Crecimiento
14. `fin_crecimiento_activos`
15. `fin_crecimiento_patrimonio`
16. `fin_crecimiento_ventas`
17. `fin_crecimiento_empleados`

### Historia y disponibilidad
18. `TIENE_T_MENOS_1`

### Calidad y anomalías
19. `flag_activos_negativos`
20. `flag_ventas_negativas`
21. `flag_empleados_fijo`
22. `flag_empleados_salto_temporal`
23. `flag_empleados_anomalia_total`
24. `flag_patrimonio_no_positivo`

### Característica societaria
25. `tipo_compania`

La variable `provincia` se conserva para filtros y análisis comercial, pero no forma parte del feature set predictivo final.

> **tamaño + actividad + rentabilidad + crecimiento + historia + calidad**

---

## 10. División temporal definitiva v10

| Conjunto | Período | Observaciones | Positivos |
|---|---|---:|---:|
| TRAIN | 2012–2018 | **470.722** | **407** |
| EMBARGO | 2019 | 91.934 | 34 |
| VALIDATION | 2020 | 98.471 | 34 |
| EMBARGO | 2021 | 109.099 | 39 |
| TEST | 2022–2023 | **260.445** | **54** |

Los períodos de embargo reducen el riesgo de superposición entre ventanas objetivo de 24 meses.

El conjunto TEST permaneció reservado durante selección y ajuste y **se utilizó únicamente después de congelar la configuración final v10**.

---

## 11. Modelo final

| Elemento | Valor |
|---|---|
| Modelo | `HistGradientBoostingClassifier` |
| Identificador | `v10_hgb_financial_c3` |
| Configuración | `C3_CONSERVATIVE` |
| Número de features | 25 |
| `random_state` | 42 |
| Estado | **Congelado** |

Artefacto local:

`models/v10/v10_hgb_financial_c3_final.joblib`

---

## 12. Resultados finales v10

### 12.1 Métricas globales

| Conjunto | Observaciones | Positivos | PR-AUC | ROC-AUC |
|---|---:|---:|---:|---:|
| TRAIN | 470.722 | 407 | **0,040249174** | **0,952718962** |
| TEST | 260.445 | 54 | **0,007468801** | **0,934603901** |

### 12.2 Resultados Top-K

| K | Positivos recuperados | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 0 | 0 | 0 | 0 |
| 100 | 0 | 0 | 0 | 0 |
| 200 | 1 | 0,005 | 0,018519 | 24,115278 |

El primer positivo de TEST aparece en la posición **165**.

El resultado evidencia una buena capacidad de ordenamiento global, pero una **limitación de recuperación temprana Top-K**.

No se modificó v10 después de observar TEST. Cualquier mejora posterior deberá evaluarse como una nueva versión, por ejemplo **v11**.

### 12.3 Escenarios operativos de revisión comercial

Para complementar la evaluación Top-K temprana, se analizaron escenarios de capacidad de revisión comercial sobre el mismo TEST congelado, sin reentrenar ni modificar el modelo.

Los resultados reproducibles se encuentran en:

`reports/results/v10/final_test_v10_operational_k.csv`

| Año | Escenario | Empresas a revisar | Empresas/mes aprox. | Positivos recuperados | Precision@K | Recall@K |
|---:|---|---:|---:|---:|---:|---:|
| 2022 | K=2.000 | 2.000 | 166,7 | 20 de 32 | 1,00 % | 62,50 % |
| 2023 | K=2.000 | 2.000 | 166,7 | 11 de 22 | 0,55 % | 50,00 % |
| 2022 | K=5.000 | 5.000 | 416,7 | 26 de 32 | 0,52 % | 81,25 % |
| 2023 | K=5.000 | 5.000 | 416,7 | 17 de 22 | 0,34 % | 77,27 % |

**K=2.000 se plantea como escenario operativo de referencia**, equivalente a aproximadamente 167 empresas por mes. No constituye todavía un umbral formalmente aprobado por la BVQ y deberá contrastarse con la capacidad real del equipo comercial.

**K=5.000 se presenta como escenario ampliado de cobertura**, con una recuperación sustancialmente mayor, pero con una carga aproximada de 417 empresas por mes.

En cada corte anual del TEST, el número de RUC únicos coincide con el número de observaciones evaluadas; por tanto, para este análisis anual los valores de K corresponden también a empresas únicas.

Estos escenarios permiten traducir el desempeño estadístico del ranking a una capacidad de revisión comercial concreta, manteniendo intacto el TEST y evitando cualquier ajuste retrospectivo del modelo.

---

## 13. Ranking operativo

El ranking operativo utiliza información financiera de **2023** con fecha de decisión **01/05/2024**.

Universo operativo:

**137.156 empresas**

Archivo:

`data/processed/v10_operational_ranking_2024_05_01.csv.gz`

El score debe interpretarse como prioridad relativa, no como probabilidad.

---

## 14. Explicabilidad

La interpretación principal utiliza **SHAP** mediante `PermutationExplainer`.

LIME se utiliza como herramienta complementaria.

Principales variables globales:
1. `activos_final`
2. `bi_ingresos_ventas`
3. `patrimonio_final_t1`
4. `fin_crecimiento_patrimonio`
5. `fin_ratio_patrimonio_activos`
6. `fin_crecimiento_activos`
7. `patrimonio_final`
8. `activos_final_t1`
9. `fin_roa`
10. `fin_margen_neto`

La importancia SHAP representa contribuciones al resultado del modelo y **no causalidad**.

---

## 15. Empresas históricas comparables

El sistema incorpora un mecanismo separado de similitud con emisores históricos.

Se utilizan siete variables:
- activos;
- patrimonio;
- ventas;
- número de empleados;
- patrimonio / activos;
- ROA;
- rotación de activos.

La similitud se expresa en una escala de 0 a 100.

Para cada prospecto pueden presentarse hasta **5 emisores históricos comparables**.

El sistema dispone de:
- 288 emisores conocidos hasta la fecha de decisión utilizada;
- 272 perfiles completos para las siete variables de similitud.

> **Score predictivo ≠ similitud histórica**

---

## 16. Arquitectura del producto

```text
PostgreSQL
    ↓
FastAPI
    ↓
React / Vite
```

### Base de datos
**PostgreSQL**

### Backend
**FastAPI**

### Frontend
**React + TypeScript + Vite**

---

## 17. Ejecución del sistema

### 17.1 Base de datos

```powershell
docker compose up -d
docker ps
```

### 17.2 Backend

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

Documentación interactiva:

`http://127.0.0.1:8000/docs`

### 17.3 Frontend

```powershell
cd frontend
npm run dev
```

Aplicación:

`http://localhost:5173`

---

## 18. Pruebas finales

Las evidencias se almacenan en:

`reports/live_tests/`

| Prueba | Resultado |
|---|---|
| P01 — Reproducibilidad | **CUMPLE** |
| P02 — Leakage temporal | **CUMPLE** |
| P03 — Faltantes / extremos | **CUMPLE** |
| P04 — Sensibilidad ±5 % | **CUMPLE** |
| P05 — Utilidad Top-K | **CUMPLE CON LIMITACIÓN** |
| P06 — Explicabilidad / tamaño | **CUMPLE CON OBSERVACIÓN** |

### P01 — Reproducibilidad
Dos ejecuciones produjeron ranking y métricas idénticas.

### P02 — Fuga temporal
La inyección de información futura no modificó el input predictivo utilizado por el modelo.

### P03 — Faltantes y valores extremos
Con nueve variables faltantes, el score varió aproximadamente **−13,40 %**. Con `fin_ratio_patrimonio_activos = 10`, el score varió aproximadamente **+1,14 %**.

### P04 — Sensibilidad ±5 %
En el caso evaluado, una modificación de ±5 % en `fin_rotacion_activos` no cambió score ni ranking.

### P05 — Utilidad Top-K
Top 20, 50 y 100 no recuperaron positivos. El primer positivo aparece en la posición 165 y Top 200 recupera 1 positivo.

### P06 — Explicabilidad y tamaño
Se observó influencia relevante de variables asociadas a escala empresarial. Esto no constituye por sí solo evidencia de discriminación, pero justifica monitoreo segmentado y revisión humana.

---

## 19. Evidencias de defensa

Documentos principales:

- `reports/live_tests/ACTA_PRUEBAS_V10.md`
- `reports/live_tests/HOJA_DEFENSA_V10.md`
- `live_demo_v10.ps1`

---

## 20. Riesgos metodológicos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Leakage temporal | Fecha de decisión conservadora |
| Superposición del target | Períodos de embargo |
| Sobreajuste | Regularización, validación temporal y backtesting |
| Desbalance extremo | PR-AUC y métricas Top-K |
| Drift | Evaluación temporal y monitoreo futuro |
| Scores no calibrados | Interpretación como ranking |
| Contaminación de TEST | TEST utilizado únicamente después del congelamiento de v10 |
| Interpretación causal | SHAP interpretado como contribución, no causalidad |
| Automatización de decisiones | Human-in-the-loop |
| Influencia de escala | Evaluación segmentada y P06 |
| Calidad de datos | Flags, pruebas de faltantes y valores extremos |

---

## 21. Limitaciones

1. El evento objetivo es extremadamente infrecuente.
2. La prevalencia global de v10 es aproximadamente 0,055110 %.
3. TEST contiene únicamente 54 casos positivos.
4. La disponibilidad temporal se basa en una regla normativa.
5. Las fuentes presentan diferentes coberturas históricas.
6. Algunas variables contienen información faltante.
7. El score no es una probabilidad calibrada.
8. El desempeño Top-K temprano en TEST es limitado.
9. El primer positivo TEST aparece en la posición 165.
10. Las variables de tamaño muestran influencia relevante en explicaciones locales.
11. El modelo está expuesto a drift futuro.
12. Cualquier mejora posterior al análisis de TEST debe evaluarse como una nueva versión.

---

## 22. Uso responsable

Prospect Finder BVQ:
- no constituye una recomendación de inversión;
- no representa aprobación regulatoria;
- no determina automáticamente que una empresa deba convertirse en emisor;
- no sustituye análisis financiero, legal o comercial;
- no debe utilizarse como único criterio para contactar o evaluar empresas;
- requiere revisión humana.

---

## 23. Evolución futura

La versión v10 se considera **congelada**.

Líneas futuras:
- nuevos períodos financieros;
- monitoreo de drift;
- nuevas variables;
- segmentación por tamaño;
- estrategias para mejorar Top-K;
- calibración si el negocio requiere probabilidades;
- nuevas familias de modelos;
- retroalimentación de especialistas;
- evaluación del valor comercial real.

---

## 24. Tecnologías

| Herramienta | Uso |
|---|---|
| Python | Procesamiento y modelado |
| pandas | Preparación y análisis |
| NumPy | Operaciones numéricas |
| scikit-learn | Modelos y evaluación |
| SHAP | Explicabilidad |
| PostgreSQL | Base de datos |
| FastAPI | Backend |
| React | Frontend |
| TypeScript | Frontend tipado |
| Vite | Construcción frontend |
| Docker | Infraestructura |
| Git / GitHub | Control de versiones |

---

## 25. Estructura del repositorio

```text
prospect-finder-bvq/
├── config/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── docs/
├── frontend/
├── models/
├── notebooks/
├── reports/
│   ├── figures/
│   ├── results/
│   └── live_tests/
├── scripts/
├── src/
│   ├── api/
│   ├── data/
│   ├── evaluation/
│   ├── features/
│   ├── models/
│   └── product/
├── live_demo_v10.ps1
├── README.md
├── requirements.txt
└── requirements-lock.txt
```

---

## 26. Scripts principales v10

- `scripts/build_v10_base.py`
- `src/evaluation/evaluate_final_test_v10.py`
- `src/evaluation/live_test_p02_temporal_leakage.py`
- `src/evaluation/live_test_p03_missing_outliers.py`
- `src/evaluation/live_test_p04_small_changes.py`
- `src/evaluation/live_test_p05_topk_utility.py`
- `src/evaluation/live_test_p06_explainability_bias.py`
- `src/product/export_issuer_reference_profiles_v10.py`
- `src/api/load_issuer_reference_profiles.py`

---

## 27. Documentación principal

| Documento | Propósito |
|---|---|
| `README.md` | Punto de entrada |
| `docs/inventario_fuentes.md` | Inventario de fuentes |
| `docs/diccionario_datos.md` | Variables |
| `docs/pipeline_datos_mvp.md` | Pipeline histórico |
| `docs/entorno_tecnico.md` | Entorno |
| `docs/v10_dataset_freeze.md` | Congelamiento v10 |
| `docs/bitacora.md` | Evolución metodológica |
| `reports/live_tests/ACTA_PRUEBAS_V10.md` | Acta de pruebas |
| `reports/live_tests/HOJA_DEFENSA_V10.md` | Guía de defensa |

---

## 28. Estado final del proyecto

| Componente | Estado |
|---|---|
| Base integrada v10 | **Congelada** |
| Feature Set v10 | **Congelado — 25 variables** |
| División temporal | **Congelada** |
| Modelo final v10 | **Congelado** |
| Evaluación TEST | **Completada** |
| Ranking operativo | **Generado** |
| SHAP | **Implementado** |
| Comparables históricos | **Implementados** |
| PostgreSQL | **Implementado** |
| FastAPI | **Implementado** |
| Frontend React | **Implementado** |
| Pruebas P01–P06 | **Ejecutadas** |
| Documentación de defensa | **Preparada** |

---

## 29. Estado del modelo final

- **Modelo:** `v10_hgb_financial_c3`
- **Configuración:** `C3_CONSERVATIVE`
- **Algoritmo:** `HistGradientBoostingClassifier`
- **Features:** 25
- **TRAIN:** 2012–2018
- **TEST:** 2022–2023
- **ROC-AUC TEST:** 0,934603901
- **PR-AUC TEST:** 0,007468801
- **Estado:** **CONGELADO**

---

## 30. Conclusión

Prospect Finder BVQ demuestra la aplicación de inteligencia artificial a un problema real de prospección empresarial dentro del mercado de valores ecuatoriano.

Su principal contribución no consiste en predecir de manera determinística qué empresa se convertirá en emisor, sino en transformar un universo amplio de empresas en una priorización cuantitativa, trazable y explicable que pueda ser utilizada como insumo por especialistas.

> **Prospect Finder no reemplaza la decisión humana. Convierte datos históricos en una priorización que permite enfocar mejor el análisis especializado.**

> **Modelo → Priorización → Especialista → Decisión**
