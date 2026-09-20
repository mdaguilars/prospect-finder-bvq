# Backlog priorizado — Prospect Finder BVQ

## 1. Propósito

Este documento registra y prioriza las siguientes actividades técnicas y metodológicas del proyecto Prospect Finder BVQ.

El backlog se construye a partir de:

- resultados del Baseline v1;
- experimentos Baseline v2 y v3;
- análisis de errores;
- limitaciones identificadas;
- necesidades de reproducibilidad;
- relación del modelo con el proceso de prospección de la Bolsa de Valores Quito.

El objetivo es evitar realizar experimentos aislados sin una secuencia definida y mantener trazabilidad sobre qué se debe mejorar, por qué y cómo se evaluará.

---

## 2. Criterio de priorización

Se utilizan tres niveles de prioridad.

### Alta

Actividades que pueden modificar de forma importante la capacidad predictiva o resolver limitaciones metodológicas relevantes.

### Media

Actividades necesarias para ampliar la comparación de modelos, mejorar interpretabilidad o preparar una posible implementación.

### Baja

Actividades importantes para etapas posteriores, pero que dependen de resultados previos o no son críticas para el siguiente experimento.

---

## 3. Estado de las actividades

Los estados utilizados son:

- `Pendiente`
- `En análisis`
- `En desarrollo`
- `Completado`
- `Descartado`

---

## 4. Backlog general

| ID | Prioridad | Actividad | Objetivo | Estado |
|---|---|---|---|---|
| B01 | Alta | Construir variables temporales | Incorporar trayectoria financiera histórica | Pendiente |
| B02 | Alta | Construir tasas de crecimiento | Detectar empresas en expansión | Pendiente |
| B03 | Alta | Construir tendencias multianuales | Capturar evolución de dos y tres años | Pendiente |
| B04 | Alta | Evaluar Gradient Boosting | Capturar relaciones no lineales | Pendiente |
| B05 | Alta | Evaluar CatBoost | Comparar un modelo robusto para datos tabulares | Pendiente |
| B06 | Alta | Comparar nuevos modelos contra Baseline v1 | Determinar si existe mejora material | Pendiente |
| B07 | Alta | Fortalecer control temporal de disponibilidad de datos | Reducir riesgo de data leakage | Pendiente |
| B08 | Media | Evaluar Random Forest | Incorporar otro modelo tabular de referencia | Pendiente |
| B09 | Media | Evaluar estrategias de desbalance | Mejorar aprendizaje de la clase positiva | Pendiente |
| B10 | Media | Ampliar análisis de Top-K | Relacionar evaluación con capacidad comercial | Pendiente |
| B11 | Media | Analizar estabilidad temporal por cohortes | Comprender degradación entre años | Pendiente |
| B12 | Media | Evaluar nuevas fuentes | Incorporar señales adicionales | Pendiente |
| B13 | Media | Evaluar calibración | Convertir scores en probabilidades interpretables | Pendiente |
| B14 | Media | Construir Índice de Afinidad Bursátil | Generar indicador final de priorización | Pendiente |
| B15 | Media | Incorporar interpretabilidad | Explicar razones de priorización | Pendiente |
| B16 | Media | Formalizar diccionario de datos | Mejorar documentación y reproducibilidad | Completado |
| B17 | Baja | Evaluar MLP | Comparar una arquitectura de red neuronal | Pendiente |
| B18 | Baja | Diseñar prototipo de visualización | Mostrar ranking y explicación al usuario final | Pendiente |
| B19 | Baja | Evaluar monitoreo de drift | Preparar futura operación del modelo | Pendiente |

---

# 5. Actividades de prioridad alta

## B01 — Construir variables temporales

**Prioridad:** Alta

**Estado:** Pendiente

### Problema identificado

El Baseline v1 utiliza principalmente información financiera correspondiente a una sola observación empresa-año.

Esto limita la capacidad del modelo para distinguir entre:

- empresas grandes pero estables;
- empresas pequeñas en crecimiento;
- empresas con deterioro financiero;
- empresas con expansión sostenida.

### Actividad

Construir variables que incorporen información histórica previa de cada empresa.

### Variables candidatas

- variación de activos;
- variación de patrimonio;
- variación de capital;
- variación de pasivos;
- variación de efectivo;
- variación de utilidad;
- cambio de liquidez;
- cambio de endeudamiento;
- cambio de ROA.

### Criterio de aceptación

La actividad se considerará completada cuando:

1. las variables se construyan utilizando únicamente información disponible antes de la fecha de corte;
2. se documenten las fórmulas;
3. se evalúe su cobertura;
4. se incorpore un nuevo dataset de features reproducible;
5. se compare el nuevo modelo contra Baseline v1.

---

## B02 — Construir tasas de crecimiento

**Prioridad:** Alta

**Estado:** Pendiente

### Objetivo

Capturar señales de expansión empresarial que puedan estar asociadas con una futura necesidad de financiamiento mediante el mercado de valores.

### Variables propuestas

- crecimiento anual de activos;
- crecimiento anual de patrimonio;
- crecimiento anual de ingresos, si la variable está disponible y correctamente homologada;
- crecimiento de utilidad;
- crecimiento de capital;
- crecimiento de efectivo.

### Consideración

Las tasas deben manejar adecuadamente:

- valores negativos;
- valores iguales a cero;
- empresas sin información del período anterior;
- cambios extremos.

### Criterio de aceptación

Documentar:

- fórmula utilizada;
- tratamiento de ceros;
- tratamiento de valores negativos;
- porcentaje de cobertura;
- comparación de desempeño frente al baseline.

---

## B03 — Construir tendencias multianuales

**Prioridad:** Alta

**Estado:** Pendiente

### Objetivo

Representar trayectoria y estabilidad financiera utilizando más de un período histórico.

### Variables candidatas

- crecimiento acumulado de activos en dos años;
- crecimiento acumulado de patrimonio;
- tendencia de utilidad;
- tendencia de endeudamiento;
- tendencia de liquidez;
- promedio móvil;
- volatilidad de resultados;
- número de años consecutivos con utilidad positiva.

### Criterio de aceptación

Las variables deben calcularse sin utilizar información posterior a la fecha de corte correspondiente.

---

## B04 — Evaluar Gradient Boosting

**Prioridad:** Alta

**Estado:** Pendiente

### Objetivo

Evaluar un modelo capaz de capturar relaciones no lineales e interacciones entre variables.

### Justificación

El Baseline v1 utiliza regresión logística y, por tanto, modela principalmente relaciones lineales en el espacio transformado.

Es posible que la afinidad con el mercado de valores dependa de combinaciones más complejas entre:

- tamaño;
- endeudamiento;
- rentabilidad;
- liquidez;
- crecimiento;
- sector.

### Métricas de evaluación

- PR-AUC;
- ROC-AUC;
- Precision@50;
- Recall@50;
- Lift@50;
- Precision@100;
- Recall@100;
- Lift@100;
- Precision@200;
- Recall@200;
- Lift@200.

### Criterio de aceptación

El nuevo modelo solamente se considerará una mejora si presenta una mejora material en VALIDATION respecto al Baseline v1, especialmente en PR-AUC y métricas Top-K.

---

## B05 — Evaluar CatBoost

**Prioridad:** Alta

**Estado:** Pendiente

### Objetivo

Evaluar un modelo de boosting diseñado para trabajar eficientemente con datos tabulares y variables categóricas.

### Aspectos a evaluar

- tratamiento de `SECTOR_CIIU`;
- comportamiento con datos faltantes;
- ponderación de clases;
- capacidad de generalización temporal;
- estabilidad del ranking.

### Criterio de aceptación

Comparación directa contra:

- Baseline v1;
- Gradient Boosting;
- otras alternativas desarrolladas.

---

## B06 — Comparar nuevos modelos contra Baseline v1

**Prioridad:** Alta

**Estado:** Pendiente

### Objetivo

Evitar reemplazar el baseline por diferencias numéricas pequeñas que no representen una mejora útil.

### Modelo de referencia

El modelo actual de referencia es:

`Baseline v1 — Logistic Regression, C = 1.0, class_weight = balanced`

### Criterios principales

- PR-AUC en VALIDATION;
- Precision@K;
- Recall@K;
- Lift@K.

### Criterios secundarios

- ROC-AUC;
- estabilidad entre TRAIN y VALIDATION;
- complejidad;
- interpretabilidad;
- facilidad de reproducción.

### Regla metodológica

TEST no debe utilizarse para seleccionar cada nueva alternativa.

---

## B07 — Fortalecer control temporal de disponibilidad de datos

**Prioridad:** Alta

**Estado:** Pendiente

### Problema identificado

Actualmente se utiliza el año fiscal como referencia temporal.

Sin embargo, un estado financiero correspondiente al año `t` puede haber sido presentado o publicado durante el año `t + 1`.

### Riesgo

Una empresa podría registrarse como emisor antes de que la información financiera utilizada como predictor hubiera estado disponible públicamente.

Esto podría generar leakage temporal.

### Actividad

Investigar y documentar:

- fecha de presentación;
- fecha de publicación;
- fecha de disponibilidad efectiva;
- relación entre esta fecha y la primera inscripción como emisor.

### Criterio de aceptación

Definir una regla temporal reproducible que garantice que cada variable utilizada habría estado disponible en la fecha hipotética de predicción.

---

# 6. Actividades de prioridad media

## B08 — Evaluar Random Forest

**Prioridad:** Media

**Estado:** Pendiente

### Objetivo

Disponer de un modelo basado en árboles que sirva como comparación adicional.

### Evaluación

Se utilizarán las mismas divisiones temporales y métricas del Baseline v1.

---

## B09 — Evaluar estrategias de desbalance

**Prioridad:** Media

**Estado:** Pendiente

### Problema identificado

La prevalencia global de positivos es aproximadamente 0,0498 %.

### Estrategias posibles

- ponderación de clases;
- diferentes pesos para la clase positiva;
- undersampling controlado;
- combinación de ponderación y muestreo;
- evaluación de técnicas compatibles con el split temporal.

### Precaución

Cualquier técnica de remuestreo debe aplicarse únicamente sobre TRAIN.

VALIDATION y TEST deben conservar su distribución real.

### Criterio de aceptación

La estrategia debe mejorar métricas relevantes sin generar una reducción significativa de estabilidad.

---

## B10 — Ampliar análisis de Top-K

**Prioridad:** Media

**Estado:** Pendiente

### Objetivo

Relacionar el modelo con la capacidad real de análisis comercial de la BVQ.

Actualmente se utilizan:

- K = 50;
- K = 100;
- K = 200.

### Actividad

Evaluar adicionalmente valores como:

- K = 25;
- K = 50;
- K = 100;
- K = 200;
- K = 500;
- K = 1.000.

### Criterio de aceptación

Definir qué rangos de K son realmente útiles para el proceso de prospección.

---

## B11 — Analizar estabilidad temporal por cohortes

**Prioridad:** Media

**Estado:** Pendiente

### Objetivo

Comprender por qué el rendimiento disminuye en períodos posteriores.

### Análisis propuesto

Comparar por año:

- número de observaciones;
- número de positivos;
- prevalencia;
- distribución de sectores;
- tamaño de las empresas;
- ratios financieros;
- posición de positivos en el ranking.

### Resultado esperado

Identificar si existe evidencia de:

- cambio de población;
- cambio de prevalencia;
- cambio sectorial;
- drift de variables;
- deterioro específico de determinadas señales.

---

## B12 — Evaluar nuevas fuentes

**Prioridad:** Media

**Estado:** Pendiente

### Objetivo

Incorporar señales que complementen los estados financieros estáticos.

### Fuentes candidatas

- información adicional de SCVS;
- información interna de BVQ;
- fuentes públicas empresariales;
- variables sectoriales;
- variables macroeconómicas.

### Regla obligatoria

Toda nueva fuente debe cumplir:

**la información utilizada como predictor debe haber estado disponible antes de la fecha de predicción.**

### Criterio de aceptación

Cada nueva fuente deberá documentar:

- origen;
- variable utilizada;
- período;
- disponibilidad;
- calidad;
- riesgo de leakage;
- condiciones de uso.

---

## B13 — Evaluar calibración

**Prioridad:** Media

**Estado:** Pendiente

### Problema identificado

El Baseline v1 utiliza:

`class_weight="balanced"`

Por esta razón, sus scores no deben interpretarse directamente como probabilidades reales de ocurrencia.

### Actividad

Después de seleccionar un modelo competitivo se evaluarán métodos de calibración.

### Objetivo

Obtener scores con una interpretación probabilística más consistente.

### Dependencia

Esta actividad debe realizarse después de seleccionar una familia de modelo con desempeño adecuado.

---

## B14 — Construir Índice de Afinidad Bursátil

**Prioridad:** Media

**Estado:** Pendiente

### Objetivo

Convertir el resultado técnico del modelo en un indicador interpretable para priorización.

Nombre provisional:

**Índice de Afinidad Bursátil — IAB**

### Condición previa

No debe construirse como una simple transformación de los scores actuales sin calibración y validación.

### Resultado esperado

Un indicador que permita ordenar empresas y facilite la interpretación por usuarios de negocio.

---

## B15 — Incorporar interpretabilidad

**Prioridad:** Media

**Estado:** Pendiente

### Objetivo

Explicar por qué una empresa aparece en una determinada posición del ranking.

### Métodos candidatos

- coeficientes para modelos lineales;
- importancia de variables;
- SHAP para modelos compatibles;
- explicaciones locales;
- explicaciones globales.

### Resultado esperado

Para cada empresa priorizada deberá ser posible identificar las variables que más contribuyen a su score.

---

## B16 — Formalizar diccionario de datos

**Prioridad:** Media

**Estado:** Completado

### Objetivo

Crear un documento específico que describa de manera estructurada las variables utilizadas por el proyecto y facilite la comprensión, revisión y reproducibilidad del dataset.

### Información documentada

Para cada variable se incorporó, según corresponda:

- nombre;
- descripción;
- fuente;
- tipo;
- unidad o interpretación;
- fórmula o transformación;
- disponibilidad;
- tratamiento de valores faltantes;
- utilización o exclusión del modelo;
- consideraciones relacionadas con trazabilidad y riesgo de fuga de información.

### Archivo generado

`docs/diccionario_datos.md`

### Resultado

Se construyó y versionó un diccionario de datos que documenta:

- variables de identificación y trazabilidad;
- nueve variables financieras homologadas;
- transformaciones logarítmicas;
- razones financieras;
- variable sectorial;
- variable objetivo `TARGET_24M`;
- disponibilidad de información;
- tratamiento de faltantes;
- variables excluidas del modelo;
- variables previstas para futuras iteraciones.

### Criterio de aceptación

**Cumplido.**

El documento permite comprender la estructura y significado de las principales variables del dataset sin necesidad de revisar directamente el código fuente.

### Evidencia

Documento:

`docs/diccionario_datos.md`

Versionado en el repositorio Git como parte del commit:

`ed1034d — Complete project documentation and reproducibility records`

---
# 7. Actividades de prioridad baja

## B17 — Evaluar MLP

**Prioridad:** Baja

**Estado:** Pendiente

### Objetivo

Evaluar una red neuronal multicapa como parte de la comparación metodológica del proyecto.

### Justificación de la prioridad

El dataset contiene únicamente 440 positivos en total y 340 en TRAIN.

Por esta razón, una red neuronal debe evaluarse después de:

- mejorar las variables;
- establecer modelos tabulares sólidos;
- definir estrategias frente al desbalance.

### Riesgos

- sobreajuste;
- baja estabilidad;
- sensibilidad a hiperparámetros;
- menor interpretabilidad.

### Métricas

Se utilizarán las mismas métricas que para los otros modelos.

---

## B18 — Diseñar prototipo de visualización

**Prioridad:** Baja

**Estado:** Pendiente

### Objetivo

Diseñar una interfaz orientada al uso futuro del sistema por parte de la BVQ.

### Elementos potenciales

- ranking de empresas;
- IAB;
- principales variables;
- explicación del score;
- filtros;
- sector;
- tamaño;
- evolución financiera;
- estado de revisión comercial.

### Dependencia

Debe desarrollarse después de definir el modelo y el indicador de priorización.

---

## B19 — Evaluar monitoreo de drift

**Prioridad:** Baja

**Estado:** Pendiente

### Objetivo

Preparar una posible futura operación del modelo.

### Aspectos a monitorear

- cambio de distribución de variables;
- cambio de prevalencia;
- variación de métricas;
- cambio de sectores;
- reducción de Precision@K;
- reducción de Recall@K.

### Dependencia

Esta actividad corresponde a una fase posterior de operación y MLOps.

---

## 8. Orden recomendado de ejecución

La secuencia inicial propuesta es:

1. B07 — Control temporal de disponibilidad.
2. B01 — Variables temporales.
3. B02 — Crecimiento.
4. B03 — Tendencias multianuales.
5. B04 — Gradient Boosting.
6. B05 — CatBoost.
7. B06 — Comparación contra Baseline v1.
8. B09 — Estrategias de desbalance.
9. B10 — Ampliación de Top-K.
10. B11 — Estabilidad temporal.
11. B08 — Random Forest.
12. B12 — Nuevas fuentes.
13. B17 — MLP.
14. B13 — Calibración.
15. B15 — Interpretabilidad.
16. B14 — Índice de Afinidad Bursátil.
17. B18 — Visualización.
18. B19 — Monitoreo de drift.

---

## 9. Criterio para aceptar un nuevo modelo

Un modelo nuevo no reemplazará automáticamente al Baseline v1 por obtener un valor ligeramente superior en una sola métrica.

Se considerarán conjuntamente:

- PR-AUC;
- Precision@K;
- Recall@K;
- Lift@K;
- estabilidad temporal;
- diferencia entre TRAIN y VALIDATION;
- interpretabilidad;
- complejidad;
- reproducibilidad;
- utilidad para el proceso de prospección.

Una mejora deberá considerarse material y consistente con el objetivo del proyecto.

---

## 10. Relación con el problema organizacional

El backlog prioriza actividades que permitan mejorar la capacidad del sistema para:

- analizar un universo amplio de empresas;
- aplicar criterios homogéneos;
- detectar señales financieras relevantes;
- reducir el número de empresas que requieren revisión manual;
- priorizar prospectos;
- apoyar el trabajo de especialistas de la BVQ.

El sistema no busca reemplazar la decisión humana.

El ranking constituye una herramienta de apoyo para enfocar el análisis posterior.

---

## 11. Actualización del backlog

Este documento deberá actualizarse después de cada experimento importante.

Cada actividad debe registrar:

- cambio de estado;
- resultado;
- decisión;
- aprendizaje;
- nueva actividad derivada, cuando corresponda.

Las actividades completadas no deben eliminarse, ya que forman parte de la trazabilidad del proyecto.
