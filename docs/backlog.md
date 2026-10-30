# Backlog priorizado — Prospect Finder BVQ

## 1. Propósito

Este documento registra, prioriza y mantiene la trazabilidad de las actividades técnicas, metodológicas y de producto de Prospect Finder BVQ.

El backlog se construye a partir de:

- resultados experimentales;
- análisis de errores;
- limitaciones identificadas;
- riesgos metodológicos;
- necesidades de reproducibilidad;
- compromisos del proyecto de titulación;
- arquitectura del prototipo;
- requerimientos de validación;
- relación del sistema con el proceso de prospección de la Bolsa de Valores de Quito.

Su objetivo es mantener claridad sobre:

- qué se encuentra terminado;
- qué permanece pendiente;
- qué evidencia sustenta cada cierre;
- qué debe desarrollarse a continuación;
- qué actividades corresponden a futuras versiones.

Las actividades completadas no se eliminan.

Cuando una actividad experimental deja de ser pertinente para v10 debido al congelamiento del modelo, se conserva como evidencia y se identifica como posible trabajo para una futura versión.

---

# 2. Estados utilizados

Los estados utilizados son:

- `Pendiente`
- `En análisis`
- `En desarrollo`
- `Completado`
- `Completado inicialmente`
- `Descartado para v10`
- `Evolución futura`

## Interpretación

**Pendiente:** la actividad todavía no ha comenzado.

**En análisis:** existe información previa, pero todavía debe decidirse su incorporación.

**En desarrollo:** la actividad se encuentra en implementación.

**Completado:** existe implementación reproducible y evidencia suficiente para cerrar la actividad.

**Completado inicialmente:** existe implementación funcional, pero podría ampliarse posteriormente.

**Descartado para v10:** la actividad no se incorporará al modelo v10 congelado. Podrá reconsiderarse en una futura versión.

**Evolución futura:** la actividad puede aportar a un despliegue productivo, MLOps o a una nueva versión, pero no es bloqueante para el cierre académico y funcional del Capstone.

---

# 3. Prioridades

## Alta

Actividades necesarias para:

- completar el prototipo;
- cumplir los objetivos académicos;
- garantizar reproducibilidad;
- validar el producto;
- reducir riesgos relevantes.

## Media

Actividades que fortalecen:

- operación;
- arquitectura;
- mantenibilidad;
- escalabilidad;
- monitoreo.

## Baja

Actividades principalmente asociadas con una futura evolución institucional o una nueva versión del producto.

---

# 4. Estado actual del proyecto

Prospect Finder BVQ ya superó la fase principal de experimentación del modelo v10.

El estado actual es:

### Datos

**CONGELADOS**

### Feature set

**CONGELADO**

### Protocolo temporal

**CONGELADO**

### Modelo

**CONGELADO**

### TEST

**EVALUADO**

### Ranking operacional

**IMPLEMENTADO**

### Similitud con emisores

**IMPLEMENTADA**

### Explicabilidad

**IMPLEMENTADA**

### PostgreSQL

**IMPLEMENTADO**

### FastAPI

**IMPLEMENTADO**

### Pruebas automáticas backend

**12 APROBADAS**

### Pruebas automatizadas frontend

**4 APROBADAS**

### Frontend

**IMPLEMENTADO Y VALIDADO TÉCNICAMENTE**

### Pruebas funcionales finales B37

**10 DE 10 APROBADAS**

### Pruebas finales P01–P06

**EJECUTADAS Y DOCUMENTADAS**

P01–P04 no evidenciaron fallos en los controles evaluados.

P05 identificó una limitación en recuperación temprana Top-K.

P06 evidenció influencia relevante de variables de escala.

### Validación con especialistas B36

**COMPLETADA**

Participantes:

`4`

Promedio global:

`4,82 / 5`

Experiencia general:

`5,00 / 5`

Utilidad para prospección:

`4,75 / 5`

---

# 5. Modelo final v10

Modelo:

`v10_hgb_financial_c3`

Configuración:

`C3_CONSERVATIVE`

Algoritmo:

`HistGradientBoostingClassifier`

El modelo utiliza:

`25 variables`

Artefacto:

`models/v10/v10_hgb_financial_c3_final.joblib`

El modelo se encuentra:

**CONGELADO**

No se realizará retuning utilizando los resultados observados en TEST.

---

# 6. Dataset v10

Dataset base:

`data/processed/v10_base_integrated_2012_2023.csv.gz`

Observaciones:

`1.030.671`

Positivos:

`568`

RUC positivos únicos:

`310`

Período:

`2012–2023`

SHA-256:

`b44f9ccf309c20a59be436953a0c6e7f9a3dc1f11cc6f2c87e41c1676a3a2a8d`

Estado:

**CONGELADO**

---

# 7. Feature set v10

Dataset core:

`data/processed/v10_features_core_2012_2023.csv.gz`

Dataset financiero:

`data/processed/v10_features_financial_2012_2023.csv.gz`

Observaciones:

`1.030.671`

El modelo final utiliza:

`25 variables`

Incluye:

- información financiera actual;
- información `t-1`;
- indicadores financieros;
- tasas de crecimiento;
- variables de calidad;
- tipo de compañía.

Provincia no forma parte del modelo.

Estado:

**CONGELADO**

---

# 8. Protocolo temporal v10

| Conjunto | Período | Observaciones | Positivos |
|---|---|---:|---:|
| TRAIN | 2012–2018 | 470.722 | 407 |
| EMBARGO 1 | 2019 | 91.934 | 34 |
| VALIDATION | 2020 | 98.471 | 34 |
| EMBARGO 2 | 2021 | 109.099 | 39 |
| TEST | 2022–2023 | 260.445 | 54 |

TEST fue abierto únicamente después de:

- congelar datos;
- congelar features;
- cerrar protocolo;
- completar backtesting;
- seleccionar modelo;
- congelar hiperparámetros.

Después de TEST no se realizó retuning.

---

# 9. Resultado final TEST

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0.007468801 |
| ROC-AUC | 0.934603901 |

Ranking combinado:

- Top 20: 0 positivos;
- Top 50: 0 positivos;
- Top 100: 0 positivos;
- Top 200: 1 positivo;
- primer positivo: posición 165.

El resultado evidencia que el modelo conserva capacidad de ordenamiento general, pero presenta una limitación explícita en recuperación temprana Top-K.

Su utilidad debe interpretarse como priorización y no como predicción determinística.

---

# 10. Resumen general del backlog

| ID | Prioridad | Actividad | Estado |
|---|---|---|---|
| B01 | Alta | Construir variables temporales | Completado |
| B02 | Alta | Construir tasas de crecimiento v10 | Completado |
| B03 | Media | Construir tendencias multianuales adicionales | Descartado para v10 |
| B04 | Alta | Evaluar Gradient Boosting | Completado |
| B05 | Media | Evaluar CatBoost | Descartado para v10 |
| B06 | Alta | Comparar modelos bajo protocolo equivalente | Completado |
| B07 | Alta | Fortalecer control temporal | Completado |
| B08 | Media | Evaluar Random Forest | Descartado para v10 |
| B09 | Media | Estrategias adicionales de desbalance | Descartado para v10 |
| B10 | Baja | Ajustar tamaños Top-K a capacidad comercial | Evolución futura |
| B11 | Alta | Analizar estabilidad temporal | Completado |
| B12 | Alta | Integrar fuentes para v10 | Completado |
| B13 | Media | Evaluar calibración probabilística | Descartado para v10 |
| B14 | Alta | Definir Índice de Afinidad Bursátil | Completado |
| B15 | Alta | Incorporar interpretabilidad | Completado |
| B16 | Media | Formalizar diccionario de datos | Completado |
| B17 | Media | Evaluar red neuronal MLP | Completado |
| B18 | Alta | Desarrollar prototipo web funcional | Completado |
| B19 | Media | Implementar monitoreo de drift | Evolución futura |
| B20 | Media | Evaluar TensorFlow/Keras | Descartado para v10 |
| B21 | Alta | Evaluar sesgo y desempeño segmentado | Completado |
| B22 | Alta | Construir Dataset / Feature Set v10 | Completado |
| B23 | Alta | Ejecutar selección final antes de TEST | Completado |
| B24 | Alta | Evaluar TEST final v10 | Completado |
| B25 | Alta | Construir ranking operacional | Completado |
| B26 | Alta | Implementar similitud con emisores | Completado |
| B27 | Alta | Implementar PostgreSQL operacional | Completado |
| B28 | Alta | Implementar API FastAPI | Completado |
| B29 | Alta | Implementar SHAP operacional | Completado |
| B30 | Alta | Implementar pruebas automáticas API | Completado |
| B31 | Alta | Construir frontend web | Completado |
| B32 | Media | Dockerizar FastAPI y frontend | Evolución futura |
| B33 | Media | Implementar migraciones Alembic | Evolución futura |
| B34 | Media | Incorporar DVC | Evolución futura |
| B35 | Media | Incorporar MLflow | Evolución futura |
| B36 | Alta | Validar con especialistas BVQ | Completado |
| B37 | Alta | Ejecutar pruebas funcionales finales | Completado |
| B38 | Alta | Preparar documentación e informe final | Completado |
| B39 | Alta | Preparar presentación final | Pendiente |
| B40 | Baja | Autenticación institucional | Evolución futura |
| B41 | Alta | Implementar pruebas automatizadas frontend | Completado |
| B42 | Alta | Ejecutar pruebas finales P01–P06 | Completado |

---

# 11. B01 — Variables temporales

**Prioridad:** Alta

**Estado:** Completado

Se incorporaron variables correspondientes al período anterior:

- activos `t-1`;
- patrimonio `t-1`;
- ventas `t-1`;
- empleados `t-1`.

El modelo v10 utiliza estas variables.

### Criterio de aceptación

Cumplido.

---

# 12. B02 — Tasas de crecimiento v10

**Prioridad:** Alta

**Estado:** Completado

Se implementaron:

- `fin_crecimiento_activos`
- `fin_crecimiento_patrimonio`
- `fin_crecimiento_ventas`
- `fin_crecimiento_empleados`

Estas variables forman parte del modelo final v10.

### Decisión

Cerrar esta actividad para v10.

Cualquier ampliación con nuevas tasas deberá formar parte de una futura versión.

---

# 13. B03 — Tendencias multianuales adicionales

**Prioridad:** Media

**Estado:** Descartado para v10

Se contemplaron inicialmente:

- tendencias de tres años;
- promedios móviles;
- volatilidad;
- pendientes multianuales;
- crecimiento acumulado.

Estas variables no forman parte del feature set v10 congelado.

### Decisión

No modificar v10 para incorporarlas después de TEST.

Podrán evaluarse en:

`v11`

---

# 14. B04 — Gradient Boosting

**Prioridad:** Alta

**Estado:** Completado

Se evaluaron distintas configuraciones de HistGradientBoosting desde ciclos anteriores.

La experiencia de v7 y v8 permitió identificar:

- riesgo de sobreajuste;
- necesidad de regularización;
- utilidad de modelos no lineales.

En v10 se seleccionó:

`v10_hgb_financial_c3`

con configuración conservadora.

### Criterio de aceptación

Cumplido.

---

# 15. B05 — CatBoost

**Prioridad:** Media

**Estado:** Descartado para v10

CatBoost fue considerado como algoritmo candidato durante el diseño inicial.

No fue incorporado al modelo final v10.

### Decisión

No ejecutar nuevos experimentos CatBoost después de abrir TEST únicamente para intentar mejorar el resultado.

Podrá evaluarse en una futura:

`v11`

utilizando un nuevo ciclo completo de desarrollo.

---

# 16. B06 — Comparación equivalente

**Prioridad:** Alta

**Estado:** Completado

Se estableció como principio que cualquier comparación de modelos debe mantener, cuando corresponda:

- dataset;
- target;
- features;
- folds;
- embargos;
- métricas;
- universos de evaluación.

Este principio fue aplicado en las comparaciones históricas y en el proceso de selección v10.

### Criterio de aceptación

Cumplido.

---

# 17. B07 — Control temporal

**Prioridad:** Alta

**Estado:** Completado

Para ejercicio fiscal `t` se utiliza:

| Concepto | Fecha |
|---|---|
| Ejercicio | año `t` |
| Disponibilidad ordinaria asumida | `30/04/t+1` |
| Fecha de decisión | `01/05/t+1` |
| Inicio target | `01/05/t+1` |
| Fin target | `30/04/t+3` |

Se utilizan además períodos de embargo.

### Criterio de aceptación

Cumplido.

---

# 18. B08 — Random Forest

**Prioridad:** Media

**Estado:** Descartado para v10

No forma parte de la configuración final seleccionada.

### Decisión

No ampliar el ciclo v10 después de TEST.

Podrá evaluarse como alternativa en v11 si existe una razón metodológica o académica suficiente.

---

# 19. B09 — Estrategias adicionales de desbalance

**Prioridad:** Media

**Estado:** Descartado para v10

El modelo final utiliza:

`class_weight = balanced`

No se incorporaron técnicas adicionales de remuestreo al candidato final.

### Decisión

No aplicar oversampling o undersampling después de observar TEST.

Podrán explorarse en una nueva versión.

---

# 20. B10 — Ajustar Top-K según capacidad comercial

**Prioridad:** Baja

**Estado:** Evolución futura

Durante la evaluación se utilizaron principalmente:

- Top 20;
- Top 50;
- Top 100;
- Top 200.

El producto permite explorar el universo completo mediante paginación, filtros, percentiles y niveles relativos de prioridad.

La validación B36 confirmó utilidad comercial general del producto, pero no estableció un único tamaño operativo de lista que deba fijarse como regla permanente.

### Decisión

No bloquear el cierre del Capstone por esta definición.

En una etapa productiva podrá acordarse con el área comercial una cadencia de revisión y tamaños de lista manejables, por ejemplo:

- Top 25;
- Top 50;
- Top 100;
- Top 200;
- Top 500;
- segmentos por percentil.

La elección deberá responder a capacidad real de seguimiento y no modificar el score del modelo.
---

# 21. B11 — Estabilidad temporal

**Prioridad:** Alta

**Estado:** Completado

Se ejecutaron análisis temporales y backtesting.

Evidencia principal:

`docs/v10_backtest_protocol.md`

y análisis posterior de estabilidad.

**Commit asociado:**

`8e20058`

### Resultado

Se confirmó que el desempeño varía entre períodos.

Esto se mantiene como limitación y fundamento para monitoreo futuro.

---

# 22. B12 — Integración de fuentes v10

**Prioridad:** Alta

**Estado:** Completado

La construcción de v10 integró y auditó fuentes relacionadas con:

- información financiera;
- identificación empresarial;
- Registro del Mercado de Valores;
- listado de entes;
- fichas registrales;
- información de `bi_ranking`;
- información histórica.

### Resultado

Base congelada:

`1.030.671 observaciones`

### Decisión

Cerrar las fuentes de v10.

Cualquier nueva fuente deberá evaluarse como parte de una futura generación.

---

# 23. B13 — Calibración

**Prioridad:** Media

**Estado:** Descartado para v10

El producto no necesita actualmente interpretar el score como probabilidad.

### Decisión

Utilizar el score exclusivamente como:

- ranking;
- afinidad relativa;
- mecanismo de priorización.

No presentar:

`score = probabilidad`

La calibración deberá reconsiderarse únicamente si aparece un requerimiento real de interpretación probabilística.

---

# 24. B14 — Índice de Afinidad Bursátil

**Prioridad:** Alta

**Estado:** Completado

El nombre de negocio seleccionado es:

**Índice de Afinidad Bursátil**

El valor técnico permanece como:

`score_afinidad`

### Decisión

No aplicar una transformación artificial ni presentarlo como probabilidad.

El índice representa la prioridad relativa producida por el modelo.

Puede acompañarse de:

- percentil;
- ranking;
- categoría visual de prioridad.

---

# 25. B15 — Interpretabilidad

**Prioridad:** Alta

**Estado:** Completado

Se evaluaron:

- Permutation Importance;
- SHAP;
- LIME.

### Técnica principal

`SHAP PermutationExplainer`

### Técnica complementaria

`LIME`

### Evidencia

`src/analysis/analyze_v10_shap_lime.py`

`docs/v10_explainability_shap_lime.md`

### Resultado

SHAP reprodujo los scores de los casos evaluados dentro de tolerancia numérica.

---

# 26. B16 — Diccionario de datos

**Prioridad:** Media

**Estado:** Completado

Documento:

`docs/diccionario_datos.md`

El diccionario fue actualizado para reflejar:

- dataset v10 2012–2023;
- 25 predictores del modelo final;
- variables actuales y `t-1`;
- ratios y crecimientos;
- banderas de calidad;
- exclusión de `provincia` del modelo;
- ranking operacional;
- score y percentil;
- niveles relativos de prioridad;
- tablas PostgreSQL;
- motor de similitud;
- campos SHAP;
- campos del frontend;
- próximo paso comercial;
- recomendaciones de evolución identificadas en B36.

### Criterio de aceptación

Cumplido.

La actualización documental no modifica el modelo congelado.
---

# 27. B17 — MLP

**Prioridad:** Media

**Estado:** Completado

Se evaluó una red neuronal multicapa.

La evidencia mostró que mayor complejidad no garantizaba mejor desempeño frente a modelos tabulares.

### Decisión

No seleccionar MLP como modelo final.

---

# 28. B18 — Prototipo web funcional

**Prioridad:** Alta

**Estado:** Completado

El prototipo web dispone de un flujo funcional integrado:

`PostgreSQL → FastAPI → React → usuario`

y:

`modelo congelado → SHAP → FastAPI → React → usuario`

### Componentes implementados

- resumen ejecutivo;
- ranking;
- búsqueda;
- filtros;
- paginación;
- ficha de empresa;
- indicadores financieros;
- Índice de Afinidad Bursátil;
- percentil;
- niveles relativos de prioridad;
- explicabilidad SHAP bajo demanda;
- emisores comparables;
- calidad de datos;
- próximo paso comercial;
- información del modelo.

### Validación realizada

Se verificó:

- carga de `137.156` empresas;
- `24` provincias;
- `9` tipos de compañía;
- ranking y paginación;
- filtros;
- ficha financiera;
- comparables;
- factores SHAP positivos y negativos;
- pruebas automatizadas frontend: `4 passed`;
- pruebas funcionales B37: `10 de 10 aprobadas`;
- validación B36 con cuatro especialistas.

### Criterio de cierre

Cumplido.

La funcionalidad principal del prototipo está implementada, probada y validada para el alcance del Capstone.

Las mejoras futuras de experiencia de usuario no reabren esta actividad.
---

# 29. B19 — Monitoreo de drift

**Prioridad:** Media

**Estado:** Evolución futura

Un despliegue productivo debería contemplar monitoreo sobre datos, features, score, ranking y desempeño cuando existan labels maduros.

### Decisión

El monitoreo continuo corresponde a una etapa productiva posterior y no constituye un pendiente bloqueante del Capstone.
---

# 30. B20 — TensorFlow/Keras

**Prioridad:** Media

**Estado:** Descartado para v10

TensorFlow/Keras fue contemplado dentro de las tecnologías potenciales del planteamiento inicial.

El proyecto sí evaluó una alternativa neuronal mediante MLP.

El modelo v10 se encuentra congelado y TEST ya fue abierto.

### Decisión

No incorporar un nuevo experimento TensorFlow/Keras dentro del ciclo v10 después de observar TEST.

Si una futura actividad académica exigiera específicamente TensorFlow/Keras, deberá documentarse como experimento complementario independiente o como parte de una nueva versión metodológica.
---

# 31. B21 — Sesgo y desempeño segmentado

**Prioridad:** Alta

**Estado:** Completado

**Commit:**

`790081b`

Se analizaron concentraciones asociadas con:

- tamaño;
- información disponible;
- tipo de compañía;
- ubicación.

### Decisión

No convertir estas variables automáticamente en reglas de exclusión.

Provincia no forma parte del modelo final.

---

# 32. B22 — Dataset / Feature Set v10

**Prioridad:** Alta

**Estado:** Completado

Se completaron:

- base integrada;
- feature set;
- tasas de crecimiento;
- variables t-1;
- indicadores financieros;
- flags de calidad;
- variables categóricas;
- protocolo temporal;
- validaciones de leakage.

### Resultado

El ciclo v10 pudo pasar a modelado sin decisiones pendientes sobre sus 25 variables finales.

---

# 33. B23 — Selección final antes de TEST

**Prioridad:** Alta

**Estado:** Completado

Antes de abrir TEST quedaron definidos:

- dataset;
- features;
- split;
- candidato final;
- configuración;
- hiperparámetros;
- métricas;
- protocolo.

Modelo seleccionado:

`v10_hgb_financial_c3`

Configuración:

`C3_CONSERVATIVE`

### Criterio de aceptación

Cumplido.

---

# 34. B24 — TEST final

**Prioridad:** Alta

**Estado:** Completado

TEST:

`2022–2023`

Observaciones:

`260.445`

Positivos:

`54`

Resultados:

- PR-AUC: `0.007468801`;
- ROC-AUC: `0.934603901`;
- Top 50: 0 positivos;
- Top 100: 0 positivos;
- Top 200: 1 positivo.

### Decisión

Cerrar v10.

No realizar retuning posterior.

---

# 35. B25 — Ranking operacional

**Prioridad:** Alta

**Estado:** Completado

**Commit:**

`e37fe23`

Script:

`src/product/build_operational_ranking_v10.py`

Fecha de decisión:

`2024-05-01`

Año financiero:

`2023`

Empresas:

`137.156`

### Score

- mínimo: 0.006069;
- máximo: 0.973694;
- media: 0.157457;
- mediana: 0.089750.

### Validación

Los scores fueron reproducidos exactamente frente al modelo congelado para las observaciones correspondientes.

---

# 36. B26 — Similitud con emisores

**Prioridad:** Alta

**Estado:** Completado

**Commit:**

`7bed6da`

Script:

`src/product/build_issuer_similarity_v10.py`

### Variables

- activos;
- patrimonio;
- ventas;
- empleados;
- patrimonio / activos;
- ROA;
- rotación de activos.

### Metodología

- percentiles anuales;
- distancia euclidiana;
- similitud 0–100;
- cinco comparables.

### Resultado

Empresas con similitud:

`131.320`

Sin información suficiente:

`5.836`

Comparables almacenados:

`656.600`

### Regla

La similitud permanece separada del score predictivo.

---

# 37. B27 — PostgreSQL

**Prioridad:** Alta

**Estado:** Completado

**Commit:**

`a5bba08`

Docker utiliza:

`postgres:17-alpine`

Tablas:

- `operational_prospects`;
- `issuer_similarity_summary`;
- `issuer_similarity_matches`.

Registros:

| Tabla | Registros |
|---|---:|
| operational_prospects | 137.156 |
| issuer_similarity_summary | 137.156 |
| issuer_similarity_matches | 656.600 |
| **Total** | **930.912** |

### Criterio de aceptación

Carga completada y conteos validados.

---

# 38. B28 — FastAPI

**Prioridad:** Alta

**Estado:** Completado

Commits principales:

- `18dc974`
- `d1c44e4`

Endpoints implementados:

`GET /api/health`

`GET /api/prospects`

`GET /api/prospects/{expediente_key}`

`GET /api/catalogs`

Filtros:

- búsqueda;
- provincia;
- tipo;
- score mínimo;
- similitud mínima;
- disponibilidad de comparables.

La API funciona como capa exclusiva entre frontend y datos.

---

# 39. B29 — SHAP operacional

**Prioridad:** Alta

**Estado:** Completado

**Commit:**

`169ba8b`

Endpoints:

`GET /api/explainability/global`

`GET /api/explainability/prospects/{expediente_key}`

Se utiliza:

`PermutationExplainer`

### Validaciones

Se verifica:

- score del modelo;
- score operacional;
- reconstrucción SHAP.

Los errores observados se encuentran únicamente dentro del orden de precisión numérica.

### Optimización

El servicio reutiliza el runtime de explicabilidad mediante caché en memoria.

Durante la ejecución funcional del 4 de octubre de 2026 se verificó además el precalentamiento de SHAP al iniciar FastAPI. El log de arranque mostró:

`Inicializando explicabilidad SHAP...`

`Precalentando SHAP con expediente 1...`

`SHAP inicializado correctamente.`

Por tanto, el entorno funcional validado inicia el runtime de explicabilidad y ejecuta un calentamiento antes de atender las consultas del usuario.

---

# 40. B30 — Pruebas automáticas del backend

**Prioridad:** Alta

**Estado:** Completado

**Commit:**

`b1b577f`

Archivos:

- `test_health.py`;
- `test_prospects.py`;
- `test_catalogs.py`;
- `test_explainability.py`.

Comando:

`python -m pytest "tests\api" -q`

Resultado:

`12 passed`

### Nota

Estas pruebas son técnicas.

No sustituyen la validación funcional con especialistas.

---

# 41. B31 — Frontend web

**Prioridad:** Alta

**Estado:** Completado

**Commit principal:**

`20fb2e4`

**Mensaje Git:**

`feat: add Prospect Finder frontend`

### Tecnologías verificadas

- Node.js `24.19.0`;
- npm `11.17.0`;
- React `19.3.0`;
- React DOM `19.3.0`;
- TypeScript `6.0.3`;
- Vite `8.3.2`;
- Lucide React `1.52.0`;
- React Router DOM `7.18.4`;
- Recharts `3.10.1`;
- Oxlint `1.86.0`;
- Vitest `5.0.3`;
- Testing Library React `16.3.3`;
- Testing Library jest-dom `7.0.1`;
- Testing Library user-event `14.6.7`;
- jsdom `30.1.2`.

React Router DOM y Recharts están instalados para evolución posterior. La primera vista funcional no depende todavía de navegación compleja ni de gráficos construidos con Recharts.

Vitest, Testing Library y jsdom se utilizan para las pruebas automatizadas del frontend.

### Funcionalidad implementada

#### Inicio

- total de empresas;
- fecha de decisión;
- versión/configuración del modelo;
- indicadores generales;
- total de provincias;
- total de tipos de compañía.

#### Ranking

- posición;
- empresa;
- RUC;
- afinidad;
- percentil;
- provincia;
- tipo;
- similitud;
- calidad.

#### Filtros

- búsqueda;
- provincia;
- tipo de compañía.

La API también mantiene disponibles filtros por:

- score mínimo;
- similitud mínima;
- disponibilidad de comparables.

#### Ficha

- identificación;
- indicadores financieros;
- score;
- percentil;
- ranking;
- SHAP;
- comparables;
- calidad.

### Validación técnica

Build:

`npm --prefix frontend run build`

Resultado:

`1898 modules transformed`

sin errores.

Lint:

`npm --prefix frontend run lint`

Resultado:

`0 warnings`

`0 errors`

Pruebas automatizadas:

`npm --prefix frontend run test`

Resultado:

`1 test file passed`

`4 tests passed`

### Criterio de aceptación

Se verificó desde navegador el flujo:

`Ranking → Filtrar → Empresa → Explicación → Comparables`

La actividad de construcción del frontend se considera completada.

Las pruebas automatizadas, las pruebas funcionales B37 y la validación con especialistas B36 fueron ejecutadas como actividades independientes y se encuentran cerradas.


# 41.1 B41 — Pruebas automatizadas frontend

**Prioridad:** Alta

**Estado:** Completado

**Commit:**

`7a50bf6`

**Mensaje Git:**

`test: add frontend automated tests`

Se incorporó una suite automatizada específica para la interfaz React.

### Herramientas

- Vitest `5.0.3`;
- `@testing-library/react 16.3.3`;
- `@testing-library/jest-dom 7.0.1`;
- `@testing-library/user-event 14.6.7`;
- jsdom `30.1.2`.

### Archivos

`frontend/src/test/setup.ts`

`frontend/src/test/App.test.tsx`

Configuración:

`frontend/vite.config.ts`

Script:

`npm --prefix frontend run test`

### Cobertura funcional inicial

La suite valida:

1. carga inicial del ranking y de los catálogos;
2. aplicación de búsqueda desde el formulario;
3. apertura del detalle financiero de una empresa;
4. consulta y presentación de factores SHAP positivos y negativos.

Las llamadas a la API se sustituyen por mocks para aislar la capa React.

Estas pruebas no consultan PostgreSQL ni ejecutan SHAP real.

La integración completa continúa validándose mediante las pruebas del backend y las pruebas funcionales del prototipo.

### Resultado inicial

Primera ejecución:

`1 passed`

`3 failed`

La causa correspondió a contaminación del DOM entre pruebas.

### Corrección

Se incorporó:

`cleanup()`

en:

`frontend/src/test/setup.ts`

para desmontar la interfaz después de cada prueba.

### Resultado final

`1 test file passed`

`4 tests passed`

Build posterior:

`1898 modules transformed`

Lint posterior:

`0 warnings`

`0 errors`

### Criterio de aceptación

Cumplido.

La cobertura deberá ampliarse progresivamente cuando se incorporen nuevas vistas o flujos relevantes.

---

# 41.2 B42 — Pruebas finales P01–P06

**Prioridad:** Alta

**Estado:** Completado

Se ejecutó una batería adicional de pruebas sobre el modelo final y su comportamiento operacional.

Evidencia:

`reports/live_tests/ACTA_PRUEBAS_V10.md`

`reports/live_tests/HOJA_DEFENSA_V10.md`

### Resultados

- P01 — Consistencia: **CUMPLE**;
- P02 — Fuga temporal: **CUMPLE**;
- P03 — Faltantes y valores atípicos: **CUMPLE**;
- P04 — Robustez ±5 %: **CUMPLE**;
- P05 — Utilidad Top-K: **CUMPLE CON LIMITACIÓN**;
- P06 — Explicabilidad y escala: **CUMPLE CON OBSERVACIÓN**.

En P05:

- Top 20: 0 positivos;
- Top 50: 0 positivos;
- Top 100: 0 positivos;
- Top 200: 1 positivo;
- primer positivo: posición 165.

P06 confirmó reconstrucción SHAP dentro de tolerancia numérica y evidenció influencia relevante de variables de escala en los casos evaluados.

### Criterio de aceptación

Cumplido con las limitaciones y observaciones documentadas.

No se realizó retuning posterior a estas pruebas.

---

# 42. B32 — Dockerizar FastAPI y frontend

**Prioridad:** Media

**Estado:** Evolución futura

Actualmente Docker ejecuta PostgreSQL mediante `compose.yaml`.

La contenerización completa de FastAPI y frontend corresponde a una evolución productiva futura y no es bloqueante para el cierre del Capstone.
---

# 43. B33 — Alembic

**Prioridad:** Media

**Estado:** Evolución futura

Alembic se encuentra instalado, pero la versión funcional validada no utiliza todavía migraciones formales.

Su incorporación corresponde a una mejora productiva futura y no es requisito bloqueante del Capstone.
---

# 44. B34 — DVC

**Prioridad:** Media

**Estado:** Evolución futura

DVC puede fortalecer la reproducibilidad de datasets, transformaciones y artefactos.

La trazabilidad actual de v10 se sustenta en scripts reproducibles, hashes, datasets identificados, documentación de congelamiento, Git/GitHub y el modelo serializado.

DVC puede añadirse posteriormente como mejora MLOps.
---

# 45. B35 — MLflow

**Prioridad:** Media

**Estado:** Evolución futura

MLflow puede utilizarse en una futura madurez MLOps para registrar experimentos, parámetros, métricas, artefactos y modelos.

La selección de v10 ya se encuentra documentada mediante protocolos, resultados, archivos de métricas, Git y el modelo final congelado.

No constituye un requisito bloqueante del Capstone.
---

# 46. B36 — Validación con especialistas BVQ

**Prioridad:** Alta

**Estado:** Completado

Documento de evidencia:

`docs/v10_specialist_validation.md`

La validación fue ejecutada con `4 participantes`, superando el mínimo inicialmente previsto de dos especialistas.

### Resultados

Promedio global: `4,82 / 5`.

Experiencia general: `5,00 / 5`.

Utilidad para prospección: `4,75 / 5`.

Dimensiones:

| Dimensión | Resultado |
|---|---:|
| Claridad y usabilidad | 4,75 / 5 |
| Priorización y contexto | 4,75 / 5 |
| Análisis de negocio y explicabilidad | 4,84 / 5 |
| Utilidad comercial | 4,92 / 5 |

### Hallazgos

- 100 % consideró suficiente la información para decidir una revisión comercial más profunda;
- 100 % indicó que revisaría una empresa ubicada en los primeros lugares del ranking;
- 100 % recomendaría utilizar la herramienta, con o sin ajustes.

### Decisión

Cerrar B36.

Las recomendaciones se registran como evolución futura del producto y no modifican retrospectivamente el modelo v10 congelado.
---

# 47. B37 — Pruebas funcionales finales

**Prioridad:** Alta

**Estado:** Completado

Se ejecutó una matriz estructurada de pruebas funcionales sobre el prototipo integrado.

Documento de evidencia:

`docs/v10_functional_test_matrix.md`

### Entorno validado

Flujo principal:

`PostgreSQL → FastAPI → React → usuario`

Flujo de explicabilidad:

`modelo v10 congelado → SHAP → FastAPI → React → usuario`

### Escenarios ejecutados

#### PF-01 — Carga inicial del ranking

**Resultado:** APROBADA

Se verificó:

- universo prospectable: `137.156`;
- mayor afinidad visible: `0.974`;
- `24` provincias;
- `9` tipos de compañía;
- fecha de decisión `01 mayo 2024`;
- carga correcta del ranking.

#### PF-02 — Búsqueda de empresa

**Resultado:** APROBADA

Se buscó `EMPRESA PRUEBA A` y la interfaz devolvió correctamente `EMPRESA PRUEBA A S.A.`.

#### PF-03 — Filtro por provincia

**Resultado:** APROBADA

Se seleccionó `PICHINCHA` y se obtuvieron `43.487` resultados.

#### PF-04 — Filtro por tipo de compañía

**Resultado:** APROBADA

Se seleccionó `RESPONSABILIDAD LIMITADA` y se obtuvieron `28.972` resultados.

#### PF-05 — Paginación

**Resultado:** APROBADA

Se verificó la navegación a `Página 2 de 5.487`, manteniendo la numeración global del ranking.

#### PF-06 — Ficha empresarial

**Resultado:** APROBADA

Se abrió `EMPRESA PRUEBA A S.A.` y se verificaron ranking, Índice de Afinidad Bursátil, percentil, activos, patrimonio, ventas, empleados y comparables.

#### PF-07 — Explicabilidad SHAP

**Resultado:** APROBADA

Se verificaron factores que aumentan y reducen afinidad utilizando un caso con ambas direcciones:

`EMPRESA PRUEBA B S.A.`

RUC:

`[RUC ANONIMIZADO]`

Ranking:

`#16.302`

#### PF-08 — Emisores históricos comparables

**Resultado:** APROBADA

Se verificó la presentación de cinco comparables históricos con sus porcentajes de similitud.

#### PF-09 — Empresa sin similitud suficiente

**Resultado:** APROBADA

Se verificó:

`EXPORTQUILSA & PRODUCTORES ASOCIADOS S.A.`

RUC:

`992708093001`

La interfaz mostró correctamente:

`No existen comparables históricos suficientes para esta empresa.`

sin generar comparables artificiales.

#### PF-10 — Expediente inexistente

**Resultado:** APROBADA

Se consultó:

`GET /api/prospects/999999999999`

La API respondió:

`404`

con el mensaje:

`{"detail":"No se encontró una empresa con el expediente solicitado."}`

### Resultado general

`10 de 10 pruebas funcionales aprobadas`

No se identificaron errores bloqueantes en los flujos principales evaluados.

### Evidencia complementaria

Las pruebas funcionales se suman a:

- backend: `12 passed`;
- frontend automatizado: `4 passed`.

### Criterio de aceptación

Cumplido.

Los principales flujos fueron ejecutados y documentados sin errores bloqueantes.

La validación técnica de B37 se complementa con B36, que fue ejecutada posteriormente con cuatro especialistas y quedó cerrada.

---

# 48. B38 — Documentación e informe final

**Prioridad:** Alta

**Estado:** Completado

Se actualizaron y cerraron los principales documentos de v10, incluyendo README, diccionario de datos, inventario de fuentes, entorno técnico, bitácora, backlog, congelamientos, resultados finales, arquitectura, diseño operacional, explicabilidad, pruebas funcionales y validación con especialistas.

La documentación diferencia entre evidencia histórica, configuración final v10, resultados TEST, producto operacional, pruebas, validación, limitaciones y evolución futura.

### Criterio de aceptación

Cumplido.
---

# 49. B39 — Presentación final

**Prioridad:** Alta

**Estado:** Pendiente

La presentación deberá sintetizar:

1. problema organizacional;
2. fuentes;
3. metodología;
4. prevención de leakage;
5. modelo;
6. resultados;
7. explicabilidad;
8. sesgos;
9. arquitectura;
10. prototipo;
11. validación con especialistas;
12. conclusiones.

La presentación no deberá exagerar el desempeño.

Debe dejar claro que Prospect Finder BVQ es una herramienta de priorización.

---

# 50. B40 — Autenticación institucional

**Prioridad:** Baja

**Estado:** Evolución futura

El prototipo académico puede ejecutarse inicialmente en ambiente controlado.

Una eventual implantación institucional deberá incorporar:

- autenticación;
- autorización;
- roles;
- sesiones;
- auditoría;
- gestión de accesos.

Esta actividad no es requisito para probar la lógica funcional del prototipo actual.

---

# 51. Orden actual recomendado

La secuencia recomendada desde el estado actual es:

1. realizar auditoría final del repositorio antes de cambiar su visibilidad;
2. verificar que no existan credenciales, secretos o datasets no autorizados;
3. realizar el commit final de documentación y evidencias;
4. sincronizar la rama `main`;
5. crear el tag de versión para defensa;
6. completar B39 — presentación final;
7. preparar preguntas y respuestas para defensa.

Después de la defensa, y únicamente si se decide avanzar hacia una implantación productiva, podrán priorizarse B32, B33, B34, B35, B19, B40 y B10.

B36, B37, B38, B41 y B42 ya se encuentran completados.

B20 queda fuera de v10.
---

# 52. Actividades que no deben reabrir v10

Debido a que TEST ya fue evaluado, no deben incorporarse al modelo v10 nuevos experimentos con el propósito de mejorar retrospectivamente su desempeño.

Esto incluye:

- CatBoost;
- Random Forest;
- nuevas tasas;
- nuevas fuentes;
- tendencias multianuales;
- nuevas estrategias de sampling;
- nuevos hiperparámetros;
- nuevas variables;
- calibración utilizada para seleccionar nuevamente el modelo.

Estas actividades podrán formar parte de:

`v11`

si existe una nueva iteración metodológica.

---

# 53. Riesgos que permanecen activos

## Leakage temporal

Mitigación:

- fecha de decisión;
- embargos;
- features construidas con información histórica.

## Desbalance

Mitigación:

- class weighting;
- PR-AUC;
- métricas Top-K.

## Variación temporal

Mitigación:

- backtesting;
- análisis de estabilidad;
- monitoreo futuro.

## Score no calibrado

Mitigación:

- utilizarlo como afinidad;
- no presentarlo como probabilidad.

## Similitud mal interpretada

Mitigación:

- separarla del score;
- describirla como cercanía financiera.

## Interpretación causal

Mitigación:

- SHAP se presenta como contribución al modelo.

## Uso automático

Mitigación:

- supervisión humana.

## Datos sensibles

Mitigación:

- no publicar datasets operacionales;
- no almacenar credenciales reales en Git.

## Recuperación temprana Top-K

Limitación:

- Top 20, Top 50 y Top 100 no recuperan positivos en TEST;
- primer positivo en posición 165.

Mitigación:

- no exagerar la utilidad temprana del ranking;
- combinar ranking con filtros, contexto y revisión especialista;
- evaluar nuevas estrategias únicamente en una versión futura.

## Influencia de escala

Observación:

- P06 evidenció influencia relevante de variables de escala en los casos evaluados.

Mitigación:

- monitoreo por tamaño empresarial;
- análisis segmentado;
- no interpretar SHAP como causalidad o discriminación por sí sola.

## Drift

Mitigación futura:

- monitoreo.

---

# 54. Relación con los objetivos del Capstone

## Objetivo 1 — Datos

Estado:

**Cumplido**

Evidencia:

- datasets;
- fuentes;
- feature set;
- calidad;
- target;
- documentación.

## Objetivo 2 — Arquitectura

Estado:

**Cumplido en el prototipo funcional**

Evidencia:

- arquitectura;
- PostgreSQL;
- FastAPI;
- frontend React;
- contratos TypeScript;
- separación de capas;
- integración frontend–FastAPI.

El cierre de despliegue y contenerización completa se mantiene dentro de la capa de MLOps y operación.

## Objetivo 3 — Modelos

Estado:

**Cumplido**

Se compararon alternativas clásicas y una alternativa neuronal.

Modelo final:

`v10_hgb_financial_c3`

## Objetivo 4 — Evaluación

Estado:

**Cumplido**

Incluye:

- PR-AUC;
- ROC-AUC;
- Top-K;
- estabilidad;
- sesgos;
- explicabilidad.

## Objetivo 5 — Prototipo

Estado:

**Cumplido**

Backend implementado.

Frontend implementado.

Pruebas automatizadas del frontend:

`4 passed`

Pruebas funcionales finales:

`10 de 10 aprobadas`

Ranking, filtros, ficha financiera, comparables y SHAP fueron validados técnicamente.

Validación con especialistas B36:

- 4 participantes;
- promedio global `4,82 / 5`;
- experiencia general `5,00 / 5`;
- utilidad para prospección `4,75 / 5`.

## Objetivo 6 — Reproducibilidad y MLOps

Estado:

**Cumplido para el alcance del Capstone; con evolución productiva futura**

Implementado:

- Git;
- GitHub;
- requirements;
- modelo congelado;
- datasets y protocolos identificados;
- Docker PostgreSQL;
- 12 pruebas automatizadas del backend;
- 4 pruebas automatizadas del frontend;
- 10 pruebas funcionales B37;
- pruebas P01–P06;
- documentación técnica.

Evolución futura:

- DVC;
- MLflow;
- Docker FastAPI/frontend;
- Alembic;
- monitoreo continuo;
- autenticación productiva.

Estas mejoras aumentan la madurez operacional, pero no son necesarias para considerar cerrado el alcance académico actual.
---

# 55. Control de versiones reciente

Las pruebas automatizadas del frontend fueron confirmadas y publicadas en Git mediante el commit `7a50bf6`.

La matriz de pruebas funcionales finales y las evidencias documentales de cierre se encuentran preparadas para incorporarse al commit final del proyecto.

| Commit | Hito |
|---|---|
| `2deb583` | SHAP y LIME |
| `790081b` | Sesgos y riesgos |
| `8e20058` | Estabilidad |
| `7bc937d` | Diseño operacional |
| `de2d3c2` | Arquitectura |
| `e37fe23` | Ranking operacional |
| `7bed6da` | Similitud |
| `2067948` | Dependencias API/PostgreSQL |
| `a5bba08` | PostgreSQL |
| `18dc974` | API inicial |
| `d1c44e4` | Catálogos y filtros |
| `169ba8b` | SHAP operacional |
| `b1b577f` | Pruebas automáticas |
| `c0dac5a` | Actualización documental de arquitectura y estado |
| `20fb2e4` | Frontend React funcional |
| `5fdd292` | Documentación actualizada con estado del frontend |
| `7a50bf6` | Pruebas automatizadas del frontend y documentación asociada |

---

# 56. Próxima versión metodológica

Cualquier cambio posterior que altere:

- dataset;
- target;
- variables;
- algoritmo;
- hiperparámetros;
- metodología de similitud predictiva;
- reglas de scoring;

deberá evaluarse como una nueva versión.

Nombre previsto:

`v11`

v10 permanecerá como referencia congelada del presente proyecto.

---

# 57. Estado del backlog al 30 de octubre de 2026

Prospect Finder BVQ cuenta actualmente con:

- dataset v10 congelado;
- feature set congelado;
- protocolo temporal congelado;
- modelo final seleccionado y congelado;
- TEST evaluado una sola vez después de la selección;
- ranking operacional con 137.156 prospectos;
- Índice de Afinidad Bursátil;
- similitud con emisores;
- PostgreSQL y FastAPI;
- frontend React funcional;
- SHAP global e individual;
- 12 pruebas automáticas del backend;
- 4 pruebas automatizadas del frontend;
- 10 de 10 pruebas funcionales B37;
- pruebas P01–P06 ejecutadas y documentadas;
- validación B36 completada con 4 especialistas;
- promedio global B36 de 4,82 / 5;
- documentación principal de v10 actualizada y cerrada.

La prioridad inmediata es:

**cerrar Git/GitHub y preparar la defensa.**

Pendientes inmediatos del Capstone:

- auditoría final del repositorio;
- commit y push final;
- tag de versión de defensa;
- B39 — presentación final;
- preparación de preguntas y respuestas.

Las actividades de Docker completo, Alembic, DVC, MLflow, monitoreo y autenticación se mantienen como evolución productiva futura y no como bloqueantes del cierre académico.
---

# 58. Regla de mantenimiento

El backlog deberá actualizarse cuando ocurra:

- un nuevo componente;
- un cambio de estado;
- una nueva prueba;
- una decisión metodológica;
- un cambio de arquitectura;
- una validación con usuarios;
- una implementación MLOps;
- un despliegue;
- un resultado que genere una nueva actividad.

Las actividades completadas no deberán eliminarse.

El backlog debe permitir responder siempre:

**qué falta, por qué falta y cuál es el siguiente paso del proyecto.**
