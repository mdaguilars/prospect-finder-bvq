# Backlog priorizado — Prospect Finder BVQ

## 1. Propósito

Este documento registra, prioriza y mantiene la trazabilidad de las actividades técnicas y metodológicas del proyecto Prospect Finder BVQ.

El backlog se construye a partir de:

- resultados experimentales;
- análisis de errores;
- limitaciones identificadas;
- riesgos metodológicos;
- necesidades de reproducibilidad;
- compromisos del proyecto de titulación;
- relación del modelo con el proceso de prospección de la Bolsa de Valores Quito.

Su objetivo es evitar realizar experimentos aislados sin una secuencia definida y mantener trazabilidad sobre:

- qué debe mejorarse;
- por qué debe mejorarse;
- qué evidencia originó la actividad;
- cómo se evaluará;
- cuál es su estado;
- qué decisión se tomó después de ejecutarla.

Las actividades completadas no se eliminan, porque forman parte de la evolución del proyecto.

---

# 2. Estados utilizados

Los estados son:

- `Pendiente`
- `En análisis`
- `En desarrollo`
- `Completado`
- `Completado inicialmente`
- `Descartado`

## Interpretación

**Pendiente:** todavía no se ha iniciado la actividad.

**En análisis:** se dispone de información preliminar o fuentes candidatas, pero todavía no existe una implementación dentro del pipeline principal.

**En desarrollo:** la actividad se encuentra siendo implementada.

**Completado:** existe implementación reproducible y evidencia suficiente para cerrar el objetivo definido en esta iteración.

**Completado inicialmente:** existe una primera implementación, pero deberá ampliarse en etapas posteriores.

**Descartado:** la alternativa fue evaluada y la evidencia disponible no justifica mantenerla como candidata actual.

---

# 3. Criterio de priorización

Se utilizan tres niveles de prioridad.

## Alta

Actividades necesarias para:

- mejorar directamente el diseño experimental;
- reducir riesgos importantes;
- cumplir compromisos principales del proyecto;
- modificar de forma relevante el desempeño del sistema;
- preparar la selección final del modelo.

## Media

Actividades necesarias para:

- ampliar la comparación;
- mejorar interpretabilidad;
- analizar estabilidad;
- preparar el producto final;
- fortalecer una futura implementación.

## Baja

Actividades correspondientes principalmente a etapas posteriores de operación, ampliación o MLOps.

---

# 4. Estado actual del proyecto

El proyecto mantiene dos generaciones claramente separadas.

La generación histórica comprende:

- v1 a v3 bajo la metodología temporal inicial;
- v4 a v9 bajo la metodología temporal corregida;
- backtest rolling-origin de v6;
- backtest rolling-origin de v8;
- comparación automatizada v6 vs v8.

El benchmark histórico del ciclo v1–v9 es:

**v8 — HistGradientBoosting regularizado**

El baseline comparable histórico es:

**v6 — Logistic Regression con variables temporales**

La nueva generación v10 ya cuenta con una **base integrada congelada y reproducible** para el período 2012–2023.

Estado de la base v10:

- observaciones elegibles: **1.030.671**;
- positivos: **568**;
- RUC positivos únicos: **310**;
- prevalencia: **0,055110 %**;
- duplicados empresa-año: **0**;
- SHA-256: `b44f9ccf309c20a59be436953a0c6e7f9a3dc1f11cc6f2c87e41c1676a3a2a8d`.

Archivo local:

`data/processed/v10_base_integrated_2012_2023.csv.gz`

Script reproducible:

`scripts/build_v10_base.py`

Documento de congelamiento:

`docs/v10_dataset_freeze.md`

El feature set v10 todavía no está cerrado y no se ha entrenado ningún modelo v10.

El TEST 2022–2023 del ciclo temporal corregido v4–v9 permanece reservado como evidencia histórica. Para v10 deberá definirse explícitamente un nuevo protocolo temporal de TRAIN / embargo / VALIDATION / TEST antes de comenzar la selección de modelos.

---

# 5. Resumen general del backlog

| ID | Prioridad | Actividad | Estado |
|---|---|---|---|
| B01 | Alta | Construir variables temporales | Completado |
| B02 | Alta | Ampliar tasas de crecimiento | Pendiente |
| B03 | Alta | Construir tendencias multianuales | Pendiente |
| B04 | Alta | Evaluar Gradient Boosting | Completado |
| B05 | Alta | Evaluar CatBoost | Pendiente |
| B06 | Alta | Comparar modelos bajo protocolo equivalente | Completado |
| B07 | Alta | Fortalecer control temporal de disponibilidad | Completado |
| B08 | Media | Evaluar Random Forest | Pendiente |
| B09 | Media | Evaluar estrategias adicionales de desbalance | Pendiente |
| B10 | Media | Ampliar análisis de Top-K | Pendiente |
| B11 | Alta | Analizar estabilidad temporal por cohortes | Completado inicialmente |
| B12 | Alta | Evaluar e integrar nuevas fuentes | En desarrollo |
| B13 | Media | Evaluar calibración | Pendiente |
| B14 | Media | Construir Índice de Afinidad Bursátil | Pendiente |
| B15 | Alta | Incorporar interpretabilidad | Pendiente |
| B16 | Media | Formalizar diccionario de datos | Completado |
| B17 | Media | Evaluar MLP | Completado inicialmente |
| B18 | Alta | Desarrollar prototipo web funcional | Pendiente |
| B19 | Baja | Evaluar monitoreo de drift | Pendiente |
| B20 | Alta | Implementar red neuronal TensorFlow/Keras | Pendiente |
| B21 | Alta | Evaluar sesgo y desempeño segmentado | Pendiente |
| B22 | Alta | Construir Dataset / Feature Set v10 | En desarrollo |
| B23 | Alta | Ejecutar selección final antes de TEST | Pendiente |
| B24 | Alta | Evaluar TEST final de la generación seleccionada | Pendiente |

---

# 6. B01 — Construir variables temporales

**Prioridad:** Alta

**Estado:** Completado

## Problema identificado

Los primeros modelos utilizaban principalmente una fotografía financiera correspondiente a un solo período.

Esto limitaba la posibilidad de diferenciar entre:

- empresas grandes pero estables;
- empresas en expansión;
- empresas en deterioro;
- empresas con cambios relevantes en su estructura financiera.

## Actividad realizada

En v6 se construyó un nuevo feature set con:

- 16 variables correspondientes al período actual;
- 17 variables temporales;
- 33 variables numéricas en total.

Archivo utilizado:

`data/processed/mvp_features_temporal_v6.csv.gz`

## Modelos que utilizan este feature set

- v6 — Logistic Regression;
- v7 — HistGradientBoosting;
- v8 — HistGradientBoosting regularizado;
- v9 — MLP.

## Resultado

La actividad permitió pasar de una representación principalmente estática a una representación con información temporal previa.

La regresión logística v6 no presentó una mejora material de PR-AUC frente a las variantes anteriores del nuevo ciclo, pero el feature set permitió evaluar posteriormente modelos no lineales bajo las mismas condiciones.

## Criterio de aceptación

Cumplido para la primera generación de variables temporales.

## Próxima ampliación

Las tendencias de mayor horizonte permanecen cubiertas por B02 y B03.

---

# 7. B02 — Ampliar tasas de crecimiento

**Prioridad:** Alta

**Estado:** Pendiente

## Objetivo

Incorporar señales adicionales de expansión, contracción o cambio empresarial.

## Variables candidatas

- crecimiento anual de activos;
- crecimiento de patrimonio;
- crecimiento de capital;
- crecimiento de efectivo;
- crecimiento de utilidad;
- crecimiento de ingresos cuando la variable sea incorporada de forma confiable;
- cambios porcentuales robustos frente a valores negativos o cercanos a cero.

## Consideraciones

Las tasas deberán manejar adecuadamente:

- valores negativos;
- valores iguales a cero;
- faltantes;
- empresas sin observación anterior;
- valores extremos.

## Criterio de aceptación

La actividad se considerará completada cuando:

1. las fórmulas estén documentadas;
2. se controle la disponibilidad temporal;
3. se documente la cobertura;
4. se evalúe el efecto sobre el modelo;
5. se compare contra un baseline utilizando el mismo protocolo.

---

# 8. B03 — Construir tendencias multianuales

**Prioridad:** Alta

**Estado:** Pendiente

## Objetivo

Representar trayectoria y estabilidad utilizando más de un período histórico.

## Variables candidatas

- crecimiento acumulado de activos;
- crecimiento acumulado de patrimonio;
- tendencia de utilidad;
- tendencia de endeudamiento;
- tendencia de liquidez;
- promedios móviles;
- volatilidad de resultados;
- número de ejercicios consecutivos con utilidad positiva;
- pendientes o tendencias de dos y tres años.

## Riesgo

Las variables deben construirse exclusivamente con información disponible antes de la fecha de decisión.

## Criterio de aceptación

- implementación reproducible;
- ausencia de información futura;
- cobertura documentada;
- comparación bajo el protocolo temporal vigente.

---

# 9. B04 — Evaluar Gradient Boosting

**Prioridad:** Alta

**Estado:** Completado

## Objetivo

Evaluar una familia de modelos capaz de capturar relaciones no lineales e interacciones entre variables.

## Experimento v7

Se evaluó inicialmente HistGradientBoosting.

Resultados principales:

- TRAIN PR-AUC: **0,871232**
- VALIDATION PR-AUC: **0,004980**
- VALIDATION ROC-AUC: **0,816540**
- Top 50: **1**
- Top 100: **1**
- Top 200: **2**

## Diagnóstico

Se observó un fuerte sobreajuste.

## Experimento v8

Se redujo la complejidad mediante:

- menor `learning_rate`;
- menor profundidad;
- menor número de hojas;
- mayor `min_samples_leaf`;
- regularización L2.

Resultados en VALIDATION 2020:

- PR-AUC: **0,011805**
- ROC-AUC: **0,922378**
- Top 50: **2**
- Top 100: **3**
- Top 200: **4**

## Decisión

v8 se mantiene como benchmark actual del ciclo temporal corregido.

## Criterio de aceptación

Cumplido.

---

# 10. B05 — Evaluar CatBoost

**Prioridad:** Alta

**Estado:** Pendiente

## Objetivo

Evaluar un modelo tabular adicional capaz de capturar relaciones no lineales.

## Aspectos a evaluar

- comportamiento con valores faltantes;
- ponderación de clases;
- capacidad de generalización;
- estabilidad temporal;
- facilidad de interpretación;
- costo computacional;
- posible incorporación futura de variables categóricas.

## Protocolo

Cuando se evalúe sobre el ciclo v10 deberá utilizar:

- mismo dataset;
- mismo target;
- mismos folds;
- mismas reglas temporales;
- mismas métricas.

## Criterio de aceptación

Comparar contra:

- baseline lineal de la misma generación;
- HistGradientBoosting de la misma generación;
- otras alternativas entrenadas bajo condiciones equivalentes.

---

# 11. B06 — Comparar modelos bajo protocolo equivalente

**Prioridad:** Alta

**Estado:** Completado

## Problema identificado

Comparar modelos entrenados con diferentes:

- targets;
- variables;
- períodos;
- universos;
- splits;

puede producir conclusiones incorrectas.

## Implementación

Se seleccionó como comparación principal:

**v6 vs v8**

porque ambos utilizan:

- el mismo dataset;
- las mismas 33 variables;
- los mismos folds;
- los mismos embargos;
- los mismos universos de evaluación.

## Script

`src/evaluation/compare_v6_v8_backtests.py`

## Validación automática

El script verifica igualdad de:

- fold;
- inicio de TRAIN;
- fin de TRAIN;
- año de evaluación;
- observaciones de TRAIN;
- positivos de TRAIN;
- observaciones de evaluación;
- positivos de evaluación.

## Resultado

La comparabilidad fue confirmada.

### PR-AUC promedio

- v6: **0,011329**
- v8: **0,021041**

Cambio relativo:

**+85,73 %**

### Lift@50 promedio

- v6: **65,15**
- v8: **123,64**

Cambio relativo:

**+89,77 %**

## Decisión

Mantener v8 como benchmark actual.

## Criterio de aceptación

Cumplido para el ciclo v6 vs v8.

La misma regla deberá repetirse en v10.

---

# 12. B07 — Fortalecer control temporal de disponibilidad

**Prioridad:** Alta

**Estado:** Completado

## Problema identificado

Un estado financiero correspondiente al año `t` puede haber sido presentado después del cierre del ejercicio.

Utilizar el 31 de diciembre como fecha de decisión podía introducir leakage temporal.

## Regla adoptada

Para ejercicio fiscal `t`:

| Concepto | Fecha |
|---|---|
| Ejercicio | año `t` |
| Disponibilidad ordinaria máxima asumida | `30/04/t+1` |
| Fecha de decisión | `01/05/t+1` |
| Inicio del target | `01/05/t+1` |
| Fin del target | `30/04/t+3` |

## Alcance

La regla constituye una hipótesis normativa conservadora.

No representa la fecha individual real de presentación de cada empresa.

## Resultado

El dataset corregido contiene:

- **883.988 observaciones elegibles**
- **423 positivos**

## Mitigación adicional

Se incorporaron períodos de embargo.

## Criterio de aceptación

Cumplido para la metodología actual.

## Limitación residual

Una futura disponibilidad de fechas reales de presentación podría permitir una definición temporal aún más precisa.

---

# 13. B08 — Evaluar Random Forest

**Prioridad:** Media

**Estado:** Pendiente

## Objetivo

Incorporar otro modelo basado en árboles como referencia adicional.

## Utilidad

Permitirá evaluar si las mejoras observadas en v8 corresponden específicamente al boosting o si otros modelos no lineales pueden capturar señales similares.

## Criterio de aceptación

Debe utilizar exactamente el mismo protocolo que los demás modelos de su generación.

---

# 14. B09 — Evaluar estrategias adicionales de desbalance

**Prioridad:** Media

**Estado:** Pendiente

## Situación actual

La metodología ya utiliza ponderación de clases en modelos compatibles.

En el ciclo temporal corregido v4–v9 la prevalencia era aproximadamente:

**0,0479 %**

En la base congelada v10 la prevalencia es:

**0,055110 %**

## Estrategias adicionales candidatas

- ajuste controlado de pesos;
- undersampling exclusivamente en TRAIN;
- combinación de ponderación y muestreo;
- estrategias específicas compatibles con validación temporal.

## Regla obligatoria

VALIDATION y TEST deben conservar su distribución real.

Nunca se debe aplicar remuestreo sobre los conjuntos de evaluación.

## Criterio de aceptación

La estrategia debe mejorar las métricas de priorización sin incrementar de manera significativa:

- sobreajuste;
- inestabilidad;
- complejidad innecesaria.

---

# 15. B10 — Ampliar análisis de Top-K

**Prioridad:** Media

**Estado:** Pendiente

## Situación actual

Se utilizan principalmente:

- K = 50;
- K = 100;
- K = 200.

## Objetivo

Relacionar K con la capacidad real de análisis comercial.

## Valores candidatos

- K = 25;
- K = 50;
- K = 100;
- K = 200;
- K = 500;
- K = 1.000.

## Criterio de aceptación

Definir qué niveles de K son realmente útiles para el proceso de prospección de BVQ.

---

# 16. B11 — Analizar estabilidad temporal por cohortes

**Prioridad:** Alta

**Estado:** Completado inicialmente

## Objetivo

Evitar conclusiones basadas en un único año de VALIDATION.

## Implementación

Se desarrolló un backtest rolling-origin con tres folds.

| Fold | TRAIN | EMBARGO | EVALUACIÓN |
|---|---|---|---|
| 1 | 2015–2016 | 2017 | 2018 |
| 2 | 2015–2017 | 2018 | 2019 |
| 3 | 2015–2018 | 2019 | 2020 |

## Resultados v6

PR-AUC:

- 2018: **0,015520**
- 2019: **0,013212**
- 2020: **0,005254**

Media:

**0,011329**

Desviación estándar muestral:

**0,005386**

## Resultados v8

PR-AUC:

- 2018: **0,034551**
- 2019: **0,016766**
- 2020: **0,011805**

Media:

**0,021041**

Desviación estándar muestral:

**0,011960**

## Aprendizaje

Existe variabilidad temporal importante.

v8 presenta mayor dispersión, pero mayor PR-AUC que v6 en los tres folds.

## Limitación

Solo existen tres ventanas de evaluación.

Por tanto, la variabilidad actual se interpreta descriptivamente.

## Próxima ampliación

Repetir el análisis una vez que el feature set v10 y su nuevo protocolo temporal hayan sido definidos.

---

# 17. B12 — Evaluar e integrar nuevas fuentes

**Prioridad:** Alta

**Estado:** En desarrollo

## Objetivo

Incorporar señales adicionales que complementen la información financiera utilizada en v1–v9 sin alterar retrospectivamente los experimentos históricos.

## Regla metodológica

Las nuevas fuentes no se incorporan retroactivamente a v1–v9.

Su integración forma parte de la nueva generación v10.

## Avance realizado

Durante la construcción de la base v10 se analizaron e integraron de forma controlada fuentes de SCVS relacionadas con:

- `bi_ranking`;
- catálogo de compañías `bi_compania`;
- clasificación CIIU;
- segmento empresarial;
- Registro del Mercado de Valores;
- listado de entes;
- fichas registrales;
- dataset financiero histórico armonizado.

También se auditaron:

- cobertura temporal;
- correspondencia por `EXPEDIENTE`;
- calidad de RUC;
- discrepancias entre fuentes;
- activos y patrimonio;
- utilidad neta;
- registros financieramente vacíos;
- target histórico.

## Resultado parcial

La integración permitió congelar una base v10 con:

- **1.030.671 observaciones elegibles**;
- **568 positivos**;
- **310 RUC positivos únicos**;
- período **2012–2023**.

## Fuentes todavía pendientes de incorporación al feature set

Continúan en análisis fuentes adicionales, entre ellas:

- inversión societaria;
- actos de capital;
- señales empresariales complementarias;
- otras fuentes que puedan aportar información disponible antes de la fecha de decisión.

## Condición obligatoria

Toda variable utilizada como predictor debe haber estado disponible antes de la fecha de decisión.

## Criterio de aceptación

Cada fuente incorporada deberá documentar:

- origen;
- identificación;
- período;
- granularidad;
- cobertura;
- transformación;
- calidad;
- riesgo de leakage;
- condiciones de uso;
- fecha o regla de disponibilidad.

La actividad permanecerá **En desarrollo** mientras existan fuentes relevantes pendientes de evaluación o integración.

---

# 18. B13 — Evaluar calibración

**Prioridad:** Media

**Estado:** Pendiente

## Problema

Los scores actuales no deben interpretarse directamente como probabilidades reales.

## Objetivo

Evaluar técnicas de calibración después de seleccionar una familia de modelo suficientemente estable.

## Dependencias

Esta actividad depende de:

- selección de modelo;
- estabilidad temporal;
- validación de sesgos;
- definición del uso final del score.

## Criterio de aceptación

Demostrar si la calibración mejora la interpretación probabilística sin deteriorar de forma relevante la utilidad del ranking.

---

# 19. B14 — Construir Índice de Afinidad Bursátil

**Prioridad:** Media

**Estado:** Pendiente

## Objetivo

Transformar el resultado técnico del modelo en un indicador comprensible para usuarios de negocio.

Nombre provisional:

**Índice de Afinidad Bursátil — IAB**

## Regla

No debe construirse como una transformación arbitraria de scores no calibrados.

## Dependencias

Antes de definir el IAB se requiere:

1. seleccionar modelo;
2. evaluar estabilidad;
3. analizar sesgos;
4. incorporar interpretabilidad;
5. evaluar calibración cuando corresponda;
6. definir una escala de negocio;
7. validar el indicador con especialistas.

---

# 20. B15 — Incorporar interpretabilidad

**Prioridad:** Alta

**Estado:** Pendiente

## Objetivo

Explicar por qué una empresa aparece en una determinada posición del ranking.

## Métodos previstos

- coeficientes para modelos lineales;
- importancia de variables;
- SHAP;
- explicaciones locales;
- explicaciones globales.

## Resultado esperado

Para una empresa priorizada deberá ser posible identificar las principales variables que contribuyen a su score.

## Criterio de aceptación

La explicación deberá ser:

- reproducible;
- consistente con el modelo;
- comprensible para especialistas;
- presentada como contribución al score y no como relación causal.

---

# 21. B16 — Formalizar diccionario de datos

**Prioridad:** Media

**Estado:** Completado

## Documento

`docs/diccionario_datos.md`

## Contenido

Incluye, según corresponde:

- nombre de variable;
- descripción;
- fuente;
- tipo;
- fórmula;
- disponibilidad;
- tratamiento de faltantes;
- uso o exclusión;
- consideraciones de trazabilidad.

## Criterio de aceptación

Cumplido.

## Próxima actualización

El diccionario deberá ampliarse al cerrar el feature set v10, incorporando las variables finalmente elegibles para modelado y distinguiéndolas de campos administrativos y de auditoría.

---

# 22. B17 — Evaluar MLP

**Prioridad:** Media

**Estado:** Completado inicialmente

## Objetivo

Evaluar una primera alternativa neuronal.

## Experimento

v9 utilizó una red neuronal multicapa.

Resultados en VALIDATION 2020:

- PR-AUC: **0,005262**
- ROC-AUC: **0,848818**
- Top 50: **0**
- Top 100: **0**
- Top 200: **0**

## Resultado

v9 no supera a v8.

## Aprendizaje

Una mayor complejidad no garantiza mejor desempeño en un problema con:

- fuerte desbalance;
- pocos positivos;
- datos tabulares.

## Limitación

Este experimento no constituye todavía la implementación TensorFlow/Keras prevista para el proyecto final.

La continuación se registra en B20.

---

# 23. B18 — Desarrollar prototipo web funcional

**Prioridad:** Alta

**Estado:** Pendiente

## Objetivo

Desarrollar una interfaz funcional para presentar los resultados del sistema.

## Componentes esperados

- ranking de empresas;
- indicadores principales;
- información financiera relevante;
- trayectoria;
- filtros;
- empresas comparables;
- explicación del score;
- estado de revisión;
- visualización del Índice de Afinidad Bursátil cuando este se encuentre definido.

## Regla de comunicación

La interfaz deberá utilizar conceptos como:

- afinidad;
- priorización;
- ranking;
- señales relevantes.

No deberá presentar el resultado como una predicción determinística.

## Dependencia

Puede iniciarse con datos simulados o resultados de desarrollo, pero deberá integrarse posteriormente con el pipeline seleccionado.

---

# 24. B19 — Evaluar monitoreo de drift

**Prioridad:** Baja

**Estado:** Pendiente

## Objetivo

Preparar una eventual futura operación del modelo.

## Indicadores candidatos

- cambio de distribución;
- cambio de prevalencia;
- PR-AUC;
- Precision@K;
- Recall@K;
- Lift@K;
- cambios sectoriales;
- cambios por tamaño de empresa.

## Dependencia

Corresponde principalmente a una etapa posterior de MLOps.

---

# 25. B20 — Implementar red neuronal TensorFlow/Keras

**Prioridad:** Alta

**Estado:** Pendiente

## Objetivo

Evaluar una alternativa neuronal implementada específicamente con TensorFlow/Keras.

## Justificación

La propuesta académica contempla explícitamente esta familia tecnológica.

El experimento v9 constituye evidencia exploratoria con MLP, pero no sustituye esta actividad.

## Reglas de comparación

La red deberá utilizar:

- mismo dataset de su generación;
- mismos folds;
- mismos embargos;
- mismas métricas;
- TEST reservado.

## Aspectos a controlar

- arquitectura;
- regularización;
- early stopping;
- ponderación de clases;
- sobreajuste;
- reproducibilidad;
- semilla;
- complejidad.

## Criterio de aceptación

Debe existir una comparación reproducible contra modelos tabulares equivalentes.

---

# 26. B21 — Evaluar sesgo y desempeño segmentado

**Prioridad:** Alta

**Estado:** Pendiente

## Objetivo

Identificar si el modelo presenta diferencias sistemáticas de desempeño entre grupos empresariales.

## Segmentos candidatos

Cuando la disponibilidad y metodología lo permitan:

- sector;
- tamaño empresarial;
- segmento empresarial;
- ubicación geográfica agregada;
- otros grupos relevantes disponibles en el dataset.

## Métricas

Se podrán analizar, según corresponda:

- prevalencia;
- PR-AUC;
- Recall@K;
- representación dentro del Top-K;
- errores;
- distribución de scores.

## Precaución

Una diferencia de desempeño no debe interpretarse automáticamente como discriminación.

Se deberá analizar:

- representación histórica;
- número de positivos;
- calidad de los datos;
- diferencias estructurales entre grupos.

## Criterio de aceptación

Documentar:

- grupos evaluados;
- tamaño de muestra;
- métricas;
- limitaciones;
- posibles mitigaciones.

---

# 27. B22 — Construir Dataset / Feature Set v10

**Prioridad:** Alta

**Estado:** En desarrollo

## Objetivo

Crear una nueva generación de datos incorporando fuentes y variables adicionales sin alterar retrospectivamente v1–v9.

## Nomenclatura

La nueva generación se denomina:

**Dataset / Feature Set v10**

## Avance completado — base integrada v10

La base integrada fue construida, auditada, congelada y reconstruida de forma reproducible.

Archivo:

`data/processed/v10_base_integrated_2012_2023.csv.gz`

Script:

`scripts/build_v10_base.py`

Documento de congelamiento:

`docs/v10_dataset_freeze.md`

Resultados congelados:

- período: **2012–2023**;
- observaciones elegibles: **1.030.671**;
- positivos: **568**;
- RUC positivos únicos: **310**;
- prevalencia: **0,055110 %**;
- duplicados empresa-año: **0**;
- SHA-256: `b44f9ccf309c20a59be436953a0c6e7f9a3dc1f11cc6f2c87e41c1676a3a2a8d`.

La reconstrucción desde las fuentes produjo exactamente el mismo SHA-256.

## Reglas congeladas

Quedaron congeladas:

- unidad `empresa-año`;
- período 2012–2023;
- fecha de decisión `01/05/t+1`;
- horizonte objetivo de 24 meses;
- definición del target;
- exclusión de emisores previos;
- reglas de identidad y RUC;
- exclusión de filas sin RUC verificable;
- integración de `bi_ranking` con el histórico;
- fallback controlado de activos y patrimonio;
- regla de utilidad neta;
- exclusión preventiva de variables con riesgo de leakage.

## Trabajo todavía pendiente — feature set v10

Antes de entrenar modelos se deberá definir:

- variables elegibles como predictores;
- variables exclusivamente administrativas o de auditoría;
- missingness;
- variables temporales `t-1`;
- tasas de crecimiento;
- tendencias multianuales;
- transformaciones;
- tratamiento de valores extremos;
- variables categóricas;
- nuevo protocolo temporal TRAIN / embargo / VALIDATION / TEST.

## Modelos previstos

Una vez cerrado el feature set podrán desarrollarse:

- `v10-LR`;
- `v10-HGB`;
- `v10-RF`;
- `v10-CatBoost`;
- `v10-NN`.

## Regla principal

El primer modelo de la nueva generación deberá ser:

**v10-LR**

Esto permitirá separar el aporte del nuevo dataset y de las nuevas variables del aporte de algoritmos más complejos.

## Criterio de aceptación

La actividad B22 se considerará completamente cerrada cuando:

1. la base integrada permanezca congelada y reproducible;
2. se cierre el feature set;
3. se documenten variables y transformaciones;
4. se defina el protocolo temporal v10;
5. se documente cobertura y missingness;
6. se verifique ausencia de leakage;
7. pueda iniciarse el baseline `v10-LR` sin decisiones de datos pendientes.

La primera condición ya se encuentra cumplida. El resto permanece en desarrollo.

---

# 28. B23 — Ejecutar selección final antes de TEST

**Prioridad:** Alta

**Estado:** Pendiente

## Objetivo

Cerrar el proceso de selección de modelo antes de evaluar el conjunto TEST.

## Requisitos previos

Antes de esta actividad deberán estar suficientemente definidos:

- dataset;
- feature set;
- familia de modelo;
- hiperparámetros;
- protocolo;
- métricas;
- interpretabilidad;
- evaluación de sesgo.

## Criterios de selección

La decisión deberá considerar:

- PR-AUC;
- Precision@K;
- Recall@K;
- Lift@K;
- variabilidad temporal;
- interpretabilidad;
- sesgo;
- complejidad;
- facilidad de integración;
- reproducibilidad.

## Regla

No utilizar TEST para resolver decisiones pendientes.

---

# 29. B24 — Evaluar TEST final de la generación seleccionada

**Prioridad:** Alta

**Estado:** Pendiente

## Objetivo

Realizar una única evaluación final del modelo seleccionado sobre el conjunto TEST definido para la generación de datos correspondiente.

## Situación histórica

El ciclo v4–v9 mantiene reservado su TEST temporalmente corregido 2022–2023:

- observaciones: **260.436**;
- positivos: **54**.

Este conjunto no fue utilizado para seleccionar v4–v9.

## Regla para v10

El nuevo universo v10 cubre 2012–2023 y difiere del universo utilizado en v4–v9.

Por esta razón, el TEST v10 **no se asume automáticamente igual al TEST histórico 2022–2023**.

Antes de entrenar modelos v10 deberá definirse y documentarse un nuevo protocolo temporal que especifique:

- TRAIN;
- embargo de validación;
- VALIDATION;
- embargo de TEST;
- TEST final.

## Condición previa

La evaluación final deberá ejecutarse únicamente cuando B23 haya cerrado:

- dataset;
- feature set;
- familia de modelo;
- hiperparámetros;
- protocolo;
- métricas;
- interpretabilidad;
- análisis de sesgo.

## Regla

Una vez observado el TEST final de la generación:

- no reajustar retrospectivamente el modelo utilizando esos resultados;
- documentar cualquier limitación encontrada;
- separar claramente evaluación final de desarrollo.

## Criterio de aceptación

Registrar, según corresponda:

- PR-AUC;
- ROC-AUC;
- Precision;
- Recall;
- F1;
- Precision@K;
- Recall@K;
- Lift@K;
- análisis de errores;
- comparación con resultados de desarrollo.

---

# 30. Evidencia actual de backtesting

## v6

Archivos versionados:

- `reports/results/backtest_logistic_v6_metrics.csv`
- `reports/results/backtest_logistic_v6_ranking_metrics.csv`
- `reports/results/backtest_logistic_v6_summary.csv`
- `reports/results/backtest_logistic_v6_metadata.json`

## v8

Se mantienen versionados los archivos equivalentes de su backtest temporal.

## Comparación

Archivos:

- `reports/results/comparison_v6_v8_metrics_by_year.csv`
- `reports/results/comparison_v6_v8_ranking_by_year.csv`
- `reports/results/comparison_v6_v8_stability_summary.csv`
- `reports/results/comparison_v6_v8_model_summary.csv`
- `reports/results/comparison_v6_v8_metadata.json`

---

# 31. Evidencia actual de control de versiones

Principales commits del ciclo temporal corregido:

| Commit | Hito |
|---|---|
| `69d29da` | Corrección temporal del target y v4–v5 |
| `c44f24e` | Variables temporales y v6 |
| `1c6555c` | HistGradientBoosting v7 |
| `d81bbfa` | HistGradientBoosting regularizado v8 |
| `0565ead` | Backtest temporal de v8 |
| `1ae9531` | MLP v9 |
| `c6fadce` | Backtest temporal de v6 |
| `99a8ca0` | Comparación temporal v6 vs v8 |

Las actividades siguientes deberán continuar registrándose mediante commits independientes y descriptivos.

---

# 32. Orden recomendado de ejecución

La secuencia actual recomendada es:

1. mantener congelada la base integrada v10;
2. cerrar B12 para las fuentes que vayan a entrar en esta generación;
3. continuar B22 con la construcción del feature set v10;
4. definir variables predictoras frente a variables administrativas y de auditoría;
5. B02 — ampliar tasas de crecimiento;
6. B03 — construir tendencias multianuales;
7. definir missingness, transformaciones y tratamiento de extremos sin fuga de información;
8. definir el nuevo protocolo temporal v10 con TRAIN / embargo / VALIDATION / TEST;
9. entrenar el baseline `v10-LR`;
10. entrenar `v10-HGB`;
11. B08 — evaluar Random Forest;
12. B05 — evaluar CatBoost;
13. B20 — evaluar TensorFlow/Keras;
14. B11 — repetir backtesting temporal con v10;
15. B06 — comparar alternativas v10 bajo protocolo equivalente;
16. B21 — evaluar sesgo y desempeño segmentado;
17. B15 — incorporar interpretabilidad;
18. B09 — evaluar estrategias adicionales de desbalance si la evidencia lo justifica;
19. B10 — relacionar Top-K con capacidad comercial;
20. B23 — cerrar selección final;
21. B13 — evaluar calibración cuando corresponda;
22. B14 — construir IAB;
23. B18 — integrar el prototipo web con los resultados seleccionados;
24. B24 — evaluar una única vez el TEST final definido para v10;
25. B19 — preparar monitoreo y MLOps.

---

# 33. Criterio para aceptar un nuevo modelo

Un modelo nuevo no reemplazará automáticamente al benchmark por obtener un valor ligeramente superior en una sola métrica.

La evaluación deberá considerar conjuntamente:

- PR-AUC;
- PR-AUC por fold;
- Precision@K;
- Recall@K;
- Lift@K;
- estabilidad temporal;
- variabilidad;
- interpretabilidad;
- riesgo de sesgo;
- complejidad;
- reproducibilidad;
- facilidad de integración;
- utilidad para el proceso de prospección.

Cuando el objetivo sea medir el efecto del algoritmo, las comparaciones deberán mantener constantes:

- dataset;
- target;
- feature set;
- folds;
- embargos;
- universos;
- métricas.

---

# 34. Benchmark y criterio actual

El benchmark histórico del ciclo v1–v9 es:

**v8 — HistGradientBoosting regularizado**

El baseline comparable histórico es:

**v6 — Logistic Regression con variables temporales**

Resultados rolling-origin históricos:

| Métrica | v6 | v8 |
|---|---:|---:|
| PR-AUC promedio | 0,011329 | **0,021041** |
| PR-AUC mediano | 0,013212 | **0,016766** |
| Desviación estándar PR-AUC | **0,005386** | 0,011960 |
| Lift@50 promedio | 65,15 | **123,64** |

v8 obtuvo mayor PR-AUC en:

- 2018;
- 2019;
- 2020.

No obstante, presentó mayor variabilidad.

Estas métricas pertenecen exclusivamente al universo y feature set del ciclo v1–v9.

**Todavía no existe un benchmark v10.**

El primer punto de referencia de la nueva generación será `v10-LR` una vez que B22 cierre el feature set y el nuevo protocolo temporal.

---

# 35. Riesgos que deben mantenerse visibles

## Leakage temporal

Mitigación:

- regla de disponibilidad;
- embargo;
- ajuste del preprocesamiento únicamente con TRAIN.

## Sobreajuste

Mitigación:

- regularización;
- comparación TRAIN vs evaluación;
- rolling-origin.

## Desbalance

Mitigación:

- ponderación;
- PR-AUC;
- Top-K.

## Pocos positivos

Mitigación:

- múltiples cohortes;
- interpretación de variabilidad;
- evitar conclusiones estadísticas excesivas.

## Drift

Mitigación:

- evaluación por año;
- monitoreo futuro.

## Sesgo

Mitigación:

- análisis segmentado;
- interpretabilidad;
- revisión humana.

## Comparación injusta

Mitigación:

- protocolos equivalentes;
- scripts automatizados de validación.

## Uso repetido de TEST

Mitigación:

- mantener cerrado cualquier TEST final durante la selección;
- no asumir que el TEST histórico 2022–2023 es automáticamente el TEST de v10;
- definir el TEST v10 antes del entrenamiento y abrirlo únicamente en B24.

## Scores no calibrados

Mitigación:

- utilizar score como ranking;
- calibrar solamente después de seleccionar modelo.

## Automatización excesiva

Mitigación:

- human-in-the-loop.

---

# 36. Relación con el problema organizacional

El backlog prioriza actividades que permitan mejorar la capacidad del sistema para:

- analizar un universo amplio de empresas;
- aplicar criterios homogéneos;
- identificar señales financieras y empresariales;
- reducir revisión manual;
- priorizar prospectos;
- explicar la priorización;
- apoyar el trabajo de especialistas de la BVQ.

El sistema no busca sustituir la decisión humana.

El ranking constituye una herramienta de apoyo.

---

# 37. Regla para nuevas fuentes

Toda nueva fuente deberá cumplir una condición fundamental:

**la información utilizada como predictor debe haber estado disponible antes de la fecha de decisión.**

Además deberá documentar:

- procedencia;
- granularidad;
- identificador;
- período;
- cobertura;
- calidad;
- transformación;
- disponibilidad temporal;
- riesgo de leakage;
- condiciones de uso.

---

# 38. Regla de versionamiento

No se sobrescribirán los experimentos v1–v9.

Cada nueva generación deberá mantener su propia identidad.

La generación actualmente en construcción utiliza:

**v10**

Esto permite distinguir:

- cambios de datos;
- cambios de variables;
- cambios de algoritmos;
- cambios de protocolo.

v8 permanecerá como benchmark del ciclo anterior.

---

# 39. Regla para TEST

El conjunto TEST debe permanecer separado del proceso iterativo de desarrollo.

## Ciclo histórico v4–v9

El TEST temporalmente corregido 2022–2023 permanece reservado como evidencia histórica de ese ciclo.

No fue utilizado para seleccionar:

- v4;
- v5;
- v6;
- v7;
- v8;
- v9.

## Generación v10

La base v10 cubre 2012–2023 y utiliza un universo diferente.

Por tanto, antes del entrenamiento deberá definirse explícitamente el nuevo TEST v10 junto con TRAIN, embargos y VALIDATION.

El TEST v10 no deberá utilizarse para:

- elegir variables;
- seleccionar algoritmo;
- ajustar hiperparámetros;
- seleccionar umbrales;
- decidir estrategias de desbalance;
- elegir una alternativa de interpretabilidad;
- seleccionar un modelo final.

Solo deberá utilizarse después de cerrar B23.

---

# 40. Estado del backlog al 2 de octubre de 2026

El proyecto ha completado:

- control temporal;
- reconstrucción y validación del target;
- períodos de embargo del ciclo histórico;
- variables temporales v6–v9;
- evaluación de Gradient Boosting;
- regularización;
- MLP exploratorio;
- backtesting temporal;
- comparación v6 vs v8;
- auditoría de `bi_ranking`;
- validación de `bi_compania`;
- validación de CIIU y segmento;
- validación cruzada del target mediante listado de entes y fichas registrales;
- auditoría de activos y patrimonio;
- auditoría de utilidad neta;
- reglas de identidad empresarial;
- integración controlada de fuentes;
- congelamiento reproducible de la base integrada v10 2012–2023.

La base v10 congelada contiene:

- **1.030.671 observaciones elegibles**;
- **568 positivos**;
- **310 RUC positivos únicos**;
- prevalencia de **0,055110 %**;
- **0 duplicados empresa-año**.

El SHA-256 validado es:

`b44f9ccf309c20a59be436953a0c6e7f9a3dc1f11cc6f2c87e41c1676a3a2a8d`

Los principales objetivos inmediatos son:

- continuar la evaluación de nuevas fuentes que realmente vayan a integrar v10;
- cerrar el feature set v10;
- definir variables temporales y de trayectoria;
- definir transformaciones y tratamiento de extremos;
- establecer el nuevo protocolo temporal v10;
- entrenar `v10-LR` como baseline;
- ampliar posteriormente la comparación con HGB, Random Forest, CatBoost y TensorFlow/Keras.

El TEST final deberá permanecer cerrado durante la selección.

---

# 41. Mantenimiento del backlog

Este documento deberá actualizarse después de:

- cada nuevo experimento;
- cada cambio de dataset;
- cada nueva fuente;
- cada cambio metodológico;
- cada decisión de modelo;
- cada análisis de sesgo;
- cada actualización del prototipo;
- la evaluación final de TEST.

Cada actividad deberá registrar:

- cambio de estado;
- evidencia;
- resultado;
- decisión;
- aprendizaje;
- nueva actividad derivada cuando corresponda.

Las actividades completadas no deben eliminarse.

Su permanencia permite reconstruir cómo evolucionó Prospect Finder BVQ desde el baseline inicial hasta el sistema final.
