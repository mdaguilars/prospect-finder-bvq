# Inventario de fuentes de datos

## 1. Objetivo

Este documento registra las fuentes de información utilizadas o evaluadas en el proyecto Prospect Finder BVQ, con el propósito de mantener trazabilidad sobre su origen, estructura, período disponible y función dentro del pipeline de datos.

La fuente principal para la construcción de las variables predictoras del MVP corresponde a los estados financieros de la Superintendencia de Compañías, Valores y Seguros (SCVS).

La variable objetivo se construye a partir de información histórica del Registro del Mercado de Valores de la misma institución.

Las fuentes internas de la Bolsa de Valores Quito (BVQ) se consideran actualmente como información complementaria para validación y potencial enriquecimiento del modelo.

---

## 2. Inventario general

| ID | Fuente | Archivo / objeto | Formato | Período disponible | Identificador principal | Uso en el proyecto | Estado |
|---|---|---|---|---|---|---|---|
| F01 | SCVS - Estados financieros | `estadosFinancieros_2015.zip` a `estadosFinancieros_2025.zip` | ZIP | 2015-2025 | RUC / expediente | Construcción de variables financieras predictoras | Utilizada |
| F02 | SCVS - Mercado de Valores | `listado_entes_65001_1789908466941.xlsx` | XLSX | Histórico disponible en archivo | IDENTIFICACIÓN | Construcción de la fecha de primera inscripción como emisor | Utilizada |
| F03 | SCVS - Mercado de Valores | `codigos_fichas_registrales_1789908530079.xlsx` | XLSX | Histórico disponible en archivo | IDENTIFICACIÓN | Validación de la primera fecha de inscripción | Utilizada |
| F04 | SCVS - Mercado de Valores | `hechos_relevantes_1789908501354.xlsx` | XLSX | Histórico disponible en archivo | NO. INSCRIPCIÓN / NOMBRE | Fuente complementaria de eventos del mercado | Disponible / complementaria |
| F05 | DWH BVQ | `V_BALANCE_LINEAS_RESUMEN` | CSV / vista de datos | 2022-2025 | RUC | Validación y potencial enriquecimiento financiero | Revisada |
| F06 | DWH BVQ | `V_RESULTADOS_LINEAS_RESUMEN` | CSV / vista de datos | 2022-2025 | RUC | Validación y potencial enriquecimiento financiero | Revisada |
| F07 | BVQ | `emisores_emisiones` | XLSX | Por analizar | Por verificar | Validación complementaria del histórico de emisores y emisiones | Disponible |

---

## 3. Fuente F01 — Estados financieros SCVS

La fuente principal de variables predictoras corresponde a los estados financieros publicados por la Superintendencia de Compañías, Valores y Seguros.

Los archivos disponibles comprenden:

- `estadosFinancieros_2015.zip`
- `estadosFinancieros_2016.zip`
- `estadosFinancieros_2017.zip`
- `estadosFinancieros_2018.zip`
- `estadosFinancieros_2019.zip`
- `estadosFinancieros_2020.zip`
- `estadosFinancieros_2021.zip`
- `estadosFinancieros_2022.zip`
- `estadosFinancieros_2023.zip`
- `estadosFinancieros_2024.zip`
- `estadosFinancieros_2025.zip`

Para el dataset etiquetado del MVP se utiliza actualmente el período:

**2015-2023**

Los años 2024 y 2025 se mantienen disponibles para etapas posteriores, pero no forman parte del dataset etiquetado actual debido al horizonte de predicción de 24 meses.

---

## 4. Planes contables identificados

Durante el análisis de los estados financieros se identificaron ocho estructuras de planes contables:

- `PLAN_413`
- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

Para el MVP se utilizaron:

- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

`PLAN_413` fue excluido del MVP debido a su baja cobertura, ausencia de eventos positivos dentro de las cohortes analizadas y dificultad para establecer una homologación comparable con las estructuras principales.

La homologación se mantiene en:

`config/scvs_account_mapping.csv`

---

## 5. Variables financieras obtenidas de SCVS

A partir de los diferentes planes contables se homologaron nueve variables financieras base:

- Activo total
- Activo corriente
- Efectivo
- Pasivo total
- Pasivo corriente
- Pasivo no corriente
- Patrimonio
- Capital
- Utilidad neta

El dataset financiero armonizado contiene:

- 887.469 observaciones empresa-año;
- 166.389 empresas únicas;
- período 2015-2023.

La información detallada de las variables se encuentra en:

`docs/diccionario_datos.md`

---

## 6. Fuentes F02 y F03 — Registro del Mercado de Valores

Los archivos utilizados para identificar la primera inscripción de una empresa como emisor son:

- `listado_entes_65001_1789908466941.xlsx`
- `codigos_fichas_registrales_1789908530079.xlsx`

Estas fuentes se almacenan en:

`data/raw/scvs/mercado_valores/`

Durante la construcción del target se identificaron 619 RUC de emisores con información válida para contraste entre ambas fuentes.

La primera fecha de inscripción coincidió en los 619 casos comparados.

Para el MVP se utiliza como evento la primera fecha de inscripción obtenida de `listado_entes`, validada contra `codigos_fichas_registrales`.

Esta información permite construir:

`TARGET_24M`

que identifica si una empresa se registra por primera vez como emisor dentro de los 24 meses posteriores a la fecha de corte.

---

## 7. Fuente F04 — Hechos relevantes

Archivo:

`hechos_relevantes_1789908501354.xlsx`

Esta fuente contiene información complementaria relacionada con eventos del mercado de valores.

Se conserva dentro de las fuentes disponibles, pero no se utiliza actualmente como predictor del Baseline v1 ni como fuente principal para construir `TARGET_24M`.

Podrá evaluarse posteriormente como fuente de enriquecimiento, siempre que se determine que la información correspondiente habría estado disponible antes de la fecha de predicción.

---

## 8. Fuente F05 — V_BALANCE_LINEAS_RESUMEN

La vista del Data Warehouse de la BVQ contiene información financiera resumida por empresa, año, grupo y línea contable.

Campos identificados:

- `FECHA`
- `ANIO`
- `EXPEDIENTE`
- `RUC`
- `EMISOR`
- `RAMA_ACTIVIDAD`
- `DESCRIPCION_RAMA`
- `CIIU`
- `GRUPO`
- `LINEA`
- `ORDEN`
- `VALOR`
- `VERTICAL_PCT`
- `VALOR_ANTERIOR`
- `VAR_ABS`
- `VAR_PCT`

Los grupos identificados incluyen:

- ACTIVO
- PASIVO
- PATRIMONIO

La unidad de registro corresponde a una línea financiera de una empresa en un período determinado.

Esta fuente no constituye actualmente la base principal del entrenamiento del Baseline v1.

Su función actual es de validación y potencial enriquecimiento.

---

## 9. Fuente F06 — V_RESULTADOS_LINEAS_RESUMEN

Esta vista mantiene una estructura técnica similar a la fuente de balances y contiene información del estado de resultados.

El grupo identificado es:

- RESULTADOS

Entre las líneas disponibles se encuentran:

- Ingreso por Actividad
- Costo de Ventas
- Gastos Administrativos
- Gastos Financieros
- Gastos de Venta
- Utilidad Bruta
- Utilidad Operativa
- Utilidad Neta
- Impuestos
- Participación Trabajadores
- Amortizaciones
- Depreciaciones

Al igual que la fuente de balances de la BVQ, actualmente se considera una fuente complementaria y no la fuente principal del Baseline v1.

---

## 10. Fuente F07 — Información de emisores y emisiones BVQ

El archivo:

`emisores_emisiones`

se mantiene disponible como fuente interna complementaria de la Bolsa de Valores Quito.

Su estructura, cobertura histórica e identificadores todavía deben ser documentados antes de incorporarlo formalmente al pipeline de modelado.

Por esta razón, su estado se mantiene como:

**Disponible / por analizar**

---

## 11. Rol actual de las fuentes

La arquitectura de datos del MVP puede resumirse de la siguiente manera:

**Variables predictoras (X)**

SCVS — Estados financieros
→ homologación contable
→ variables financieras
→ ingeniería de características

**Variable objetivo (Y)**

SCVS — Registro del Mercado de Valores
→ primera inscripción como emisor
→ construcción de `TARGET_24M`

**Fuentes complementarias**

DWH BVQ y otras fuentes internas
→ validación
→ contraste
→ potencial enriquecimiento futuro

Esta separación evita confundir las fuentes efectivamente utilizadas por el Baseline v1 con aquellas que todavía se encuentran en evaluación.

---

## 12. Consideraciones temporales

Una variable únicamente debe utilizarse para predecir una empresa si hubiera estado disponible en la fecha de predicción.

Por esta razón, en futuras iteraciones será necesario registrar y validar:

- fecha del período financiero;
- fecha de presentación;
- fecha de publicación;
- fecha efectiva de disponibilidad;
- fecha de corte utilizada por el modelo.

Este control es particularmente importante para evitar fuga de información temporal.

---

## 13. Condiciones de acceso, uso y licencia

Las fuentes utilizadas en el proyecto fueron revisadas desde la perspectiva de procedencia, acceso y condiciones de reutilización.

### 13.1 Estados financieros SCVS

**Fuente:** Superintendencia de Compañías, Valores y Seguros (SCVS)

**Condición de acceso:** Información obtenida a través de los portales institucionales de la SCVS.

**Uso en el proyecto:** Construcción de las variables financieras predictoras del MVP.

**Licencia identificada:** No se identificó, en las páginas oficiales revisadas para esta entrega, una licencia abierta específica aplicable a los archivos utilizados, como Creative Commons, Open Data Commons u otra licencia equivalente.

Por esta razón, el proyecto no atribuye a estos datos una licencia de reutilización que no haya sido publicada explícitamente por la institución.

La SCVS se mantiene identificada como fuente original de la información.

**Fecha de verificación documental:** 20 de septiembre de 2026.

---

### 13.2 Registro del Mercado de Valores SCVS

**Fuente:** Superintendencia de Compañías, Valores y Seguros (SCVS)

**Archivos principales utilizados:**

- `listado_entes_65001_1789908466941.xlsx`
- `codigos_fichas_registrales_1789908530079.xlsx`
- `hechos_relevantes_1789908501354.xlsx`

**Condición de acceso:** Información obtenida de los servicios y portales institucionales de la SCVS.

**Uso en el proyecto:** Identificación y validación de la primera inscripción de una empresa como emisor y construcción de `TARGET_24M`.

**Licencia identificada:** No se identificó, en las páginas oficiales revisadas para esta entrega, una licencia específica de reutilización aplicable a estos archivos.

En consecuencia, el proyecto conserva la atribución a la SCVS y no presume derechos adicionales de redistribución o reutilización que no hayan sido expresamente establecidos.

**Fecha de verificación documental:** 20 de septiembre de 2026.

---

### 13.3 Información interna de la Bolsa de Valores Quito

**Fuente:** Bolsa de Valores Quito (BVQ)

Incluye actualmente:

- `V_BALANCE_LINEAS_RESUMEN`
- `V_RESULTADOS_LINEAS_RESUMEN`
- otras fuentes institucionales internas disponibles para validación o enriquecimiento.

**Condición de acceso:** Información institucional de acceso interno.

**Uso en el proyecto:** Validación, contraste y potencial enriquecimiento del modelo.

**Licencia:** No se considera información abierta ni se le asigna una licencia pública de reutilización.

Su utilización se limita al entorno autorizado del proyecto y de la Bolsa de Valores Quito.

Los datos internos de BVQ no se publican ni redistribuyen mediante el repositorio GitHub del proyecto.

---

### 13.4 Criterio adoptado para el proyecto

Para mantener trazabilidad y evitar atribuir condiciones de uso que no hayan sido verificadas, se adopta el siguiente criterio:

| Fuente | Acceso | Licencia abierta identificada | Tratamiento |
|---|---|---|---|
| SCVS - Estados financieros | Portal institucional | No identificada explícitamente | Uso académico con atribución a la fuente |
| SCVS - Registro del Mercado de Valores | Portal institucional | No identificada explícitamente | Uso académico con atribución a la fuente |
| DWH y fuentes internas BVQ | Acceso institucional | No aplica como fuente abierta | Uso interno autorizado; no redistribuir |

La ausencia de una licencia abierta identificada no se interpreta como una autorización irrestricta de reutilización. Antes de una eventual publicación externa de datasets derivados o de una explotación comercial del sistema deberá verificarse nuevamente la normativa, términos de uso y condiciones institucionales aplicables.

## 14. Reglas de almacenamiento

Los archivos originales se conservan sin modificación dentro de:

`data/raw/`

Los datos originales no se almacenan en GitHub.

El archivo `.gitignore` excluye el contenido de `data/raw` del control de versiones.

Los resultados de transformación se organizan en:

- `data/interim`: resultados intermedios y datos armonizados;
- `data/processed`: datasets preparados para análisis y modelado.

Los scripts necesarios para reconstruir las transformaciones sí se mantienen bajo control de versiones.

---

## 15. Trazabilidad documental

La información relacionada con las fuentes se complementa con:

- `README.md`
- `docs/pipeline_datos_mvp.md`
- `docs/diccionario_datos.md`
- `docs/entorno_tecnico.md`
- `docs/bitacora.md`
- `docs/backlog.md`

Esta separación permite mantener el inventario centrado en procedencia y función de las fuentes, mientras que las transformaciones y decisiones metodológicas se documentan en sus archivos correspondientes.

---

## 16. Estado actual

El inventario refleja las fuentes utilizadas y evaluadas durante la construcción del MVP.

Actualmente:

- los estados financieros SCVS son la fuente principal de variables predictoras;
- el Registro del Mercado de Valores SCVS es la fuente de la variable objetivo;
- la información del DWH de BVQ se utiliza como fuente complementaria;
- las fuentes adicionales permanecen sujetas a análisis antes de incorporarse al modelo;
- las fechas exactas de extracción y condiciones de reutilización deben continuar fortaleciéndose documentalmente.
