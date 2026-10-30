# Inventario de fuentes de datos

## 1. Objetivo

Este documento registra las fuentes de información utilizadas, contrastadas o evaluadas en el proyecto **Prospect Finder BVQ v10**, con el propósito de mantener trazabilidad sobre:

- origen;
- archivo u objeto de datos;
- período disponible;
- identificadores principales;
- función dentro del pipeline;
- condición de uso;
- relación con el modelo final;
- restricciones de publicación y reutilización.

La referencia vigente del proyecto corresponde a la versión:

`v10`

El universo supervisado final cubre:

`2012–2023`

La fuente financiera principal de v10 es `bi_ranking`, complementada de manera controlada por el histórico financiero armonizado 2015–2023.

La variable objetivo `TARGET_24M` se construye a partir del Registro del Mercado de Valores de la Superintendencia de Compañías, Valores y Seguros (SCVS).

Las fuentes internas de la **Bolsa de Valores de Quito (BVQ)** se mantienen como información complementaria para contraste, validación y potencial enriquecimiento futuro, pero no forman parte automáticamente del vector predictivo final.

---

## 2. Inventario general vigente

| ID | Fuente | Archivo / objeto | Formato | Período utilizado / disponible | Identificador principal | Uso en v10 | Estado |
|---|---|---|---|---|---|---|---|
| F01 | SCVS — Ranking empresarial y financiero | `data/raw/scvs/ranking/bi_ranking.csv` | CSV | 2012–2023 utilizado | Expediente / RUC | Fuente financiera principal de v10 | Utilizada |
| F02 | SCVS — Estados financieros históricos | `estadosFinancieros_2015.zip` a `estadosFinancieros_2025.zip` | ZIP | 2015–2025 disponible; 2015–2023 utilizado | RUC / expediente | Homologación histórica, fallback controlado y auditoría | Utilizada / complementaria |
| F03 | SCVS — Mercado de Valores | `listado_entes_65001_1789908466941.xlsx` | XLSX | Histórico disponible | IDENTIFICACIÓN / RUC | Primera inscripción efectiva y construcción de `TARGET_24M` | Utilizada |
| F04 | SCVS — Mercado de Valores | `codigos_fichas_registrales_1789908530079.xlsx` | XLSX | Histórico disponible | IDENTIFICACIÓN / RUC | Validación de primera inscripción efectiva | Utilizada |
| F05 | SCVS — Mercado de Valores | `hechos_relevantes_1789908501354.xlsx` | XLSX | Histórico disponible | NO. INSCRIPCIÓN / NOMBRE | Fuente complementaria de eventos | Disponible / complementaria |
| F06 | DWH BVQ | `V_BALANCE_LINEAS_RESUMEN` | Vista / CSV | 2022–2025 | RUC / expediente | Contraste y potencial enriquecimiento | Revisada |
| F07 | DWH BVQ | `V_RESULTADOS_LINEAS_RESUMEN` | Vista / CSV | 2022–2025 | RUC / expediente | Contraste y potencial enriquecimiento | Revisada |
| F08 | BVQ | `emisores_emisiones` | XLSX / fuente interna | Por documentar | Por verificar | Validación y enriquecimiento de emisiones históricas | Disponible / complementaria |

---

## 3. Fuente F01 — `bi_ranking`

La fuente financiera principal utilizada en v10 es:

`data/raw/scvs/ranking/bi_ranking.csv`

Cobertura utilizada:

**2012–2023**

Esta fuente amplía el horizonte histórico respecto de las primeras versiones del proyecto y constituye la base principal para construir las variables empresariales y financieras del modelo final.

Entre la información integrada se encuentran:

- activos;
- patrimonio;
- ingresos por ventas;
- ingresos totales;
- utilidad antes de impuestos;
- impuesto a la renta;
- utilidad del ejercicio;
- utilidad neta;
- número de empleados;
- tipo de compañía;
- provincia;
- segmento;
- CIIU;
- indicadores financieros;
- gastos;
- deuda;
- otros campos administrativos y de clasificación.

No todos los campos disponibles se utilizan como predictores.

Durante v10 se excluyeron preventivamente, entre otros:

- `cia_imvalores`;
- `id_estado_financiero`;
- `posicion_general`.

La exclusión responde a criterios de riesgo de leakage, falta de justificación predictiva o naturaleza administrativa.

El catálogo empresarial asociado, incluido `bi_compania`, se utilizó además para apoyar la resolución de identidad empresarial mediante expediente y RUC.

---

## 4. Fuente F02 — Estados financieros históricos SCVS

Los estados financieros históricos de la SCVS se conservaron como una segunda fuente financiera.

Archivos disponibles:

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

Para el universo supervisado v10 se utiliza información histórica hasta:

**2023**

Los ejercicios 2024 y 2025 no forman parte del universo supervisado v10 porque no disponen de una ventana completa y comparable de 24 meses para construir el target bajo la misma regla temporal.

La salida histórica armonizada utilizada durante v10 es:

`data/interim/scvs_financials_harmonized_2015_2023.csv.gz`

Esta fuente no reemplaza indiscriminadamente a `bi_ranking`.

Su función en v10 es:

- ampliar la trazabilidad histórica;
- recuperar observaciones empresa-año ausentes de `bi_ranking`;
- realizar fallback controlado de activos y patrimonio;
- contrastar valores entre fuentes;
- conservar evidencia de auditoría.

---

## 5. Planes contables identificados en la fuente histórica

Durante el procesamiento de los estados financieros históricos se identificaron ocho estructuras de planes contables:

- `PLAN_413`
- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

En las etapas históricas iniciales se utilizaron:

- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

`PLAN_413` fue excluido en esa etapa debido a su baja cobertura, ausencia de eventos positivos en las cohortes evaluadas y dificultad de homologación comparable.

La homologación se conserva en:

`config/scvs_account_mapping.csv`

Estas decisiones forman parte de la trazabilidad histórica del proyecto.

En v10, `bi_ranking` pasa a ser la fuente financiera principal y el histórico armonizado se utiliza como fuente complementaria bajo reglas explícitas.

---

## 6. Variables financieras de la fuente histórica armonizada

A partir de los planes contables se homologaron nueve variables financieras base:

- activo total;
- activo corriente;
- efectivo;
- pasivo total;
- pasivo corriente;
- pasivo no corriente;
- patrimonio;
- capital;
- utilidad neta.

El dataset financiero armonizado histórico contiene:

- 887.469 observaciones empresa-año;
- 166.389 empresas únicas;
- período 2015–2023.

Estas cifras corresponden al dataset histórico intermedio y **no deben confundirse** con el universo final v10.

El dataset integrado v10 contiene:

`1.030.671 observaciones empresa-año`

para:

`2012–2023`

La definición vigente de variables se encuentra en:

`docs/diccionario_datos.md`

---

## 7. Integración financiera v10

La unión de los universos financieros antes de aplicar elegibilidad produjo:

`1.035.294 empresa-año`

Después de aplicar controles de identidad y elegibilidad, el dataset congelado quedó compuesto por:

- `AMBAS`: 815.331 observaciones;
- `SOLO_BI`: 146.683 observaciones;
- `SOLO_HISTORICO`: 68.657 observaciones.

El universo supervisado final contiene:

- 1.030.671 observaciones elegibles;
- 568 observaciones positivas;
- 310 RUC positivos únicos.

Esta integración evita depender exclusivamente de una sola fuente y conserva observaciones históricas válidas que de otra manera se perderían.

---

## 8. Reglas de fallback entre fuentes

La integración de fuentes no se realiza mediante promedios ni conciliaciones indiscriminadas.

Para activos y patrimonio se definió prioridad a `bi_ranking` cuando el bloque financiero contiene información válida.

Cuando el bloque financiero de `bi_ranking` se encuentra completamente vacío bajo la regla documentada y existe información histórica válida, se permite fallback hacia la fuente histórica.

Variables finales:

- `activos_final`;
- `patrimonio_final`.

Las variables:

- `activos_fallback_old`;
- `patrimonio_fallback_old`;

permiten identificar los casos en que se utilizó el respaldo histórico.

La utilidad neta histórica no se consideró directamente equivalente a la definición de `bi_ranking`.

Por esta razón, `utilidad_neta_final` no utiliza fallback indiscriminado desde la fuente histórica.

Las reglas completas se encuentran documentadas en:

`docs/v10_dataset_freeze.md`

---

## 9. Fuentes F03 y F04 — Registro del Mercado de Valores

Los archivos utilizados para identificar la primera inscripción efectiva de una empresa como emisor son:

- `listado_entes_65001_1789908466941.xlsx`
- `codigos_fichas_registrales_1789908530079.xlsx`

Estas fuentes se almacenan en:

`data/raw/scvs/mercado_valores/`

La fuente principal para construir el evento es:

`listado_entes_65001_1789908466941.xlsx`

La fecha utilizada corresponde a la primera inscripción efectiva asociada al RUC.

La información fue contrastada con:

`codigos_fichas_registrales_1789908530079.xlsx`

Para la validación se consideraron como estados efectivos:

- `VIGENTE`;
- `CANCELADA`.

No se consideran como eventos positivos registros en estados como:

- inscripción negada;
- ente creado;
- en proceso de inscripción.

La validación produjo:

- 619 RUC con primera inscripción efectiva en `listado_entes`;
- 619 RUC equivalentes al restringir fichas registrales a estados efectivos;
- 619 fechas coincidentes;
- 0 diferencias de fecha entre las dos fuentes efectivas.

---

## 10. Construcción de `TARGET_24M`

La información del Registro del Mercado de Valores permite construir:

`TARGET_24M`

El evento positivo corresponde a:

**primera inscripción efectiva de una empresa como emisor dentro de los 24 meses posteriores a la fecha de decisión.**

Para una observación del ejercicio `t`:

- fecha de decisión: 1 de mayo de `t+1`;
- inicio de ventana objetivo: 1 de mayo de `t+1`;
- fin de ventana objetivo: 30 de abril de `t+3`.

Las empresas que ya eran emisoras antes de la fecha de decisión se excluyen del universo elegible.

La fuente de target se utiliza para:

- entrenamiento;
- validación;
- TEST;
- evaluación retrospectiva.

No se utiliza como variable predictora del producto operacional.

---

## 11. Fuente F05 — Hechos relevantes

Archivo:

`hechos_relevantes_1789908501354.xlsx`

Esta fuente contiene información complementaria relacionada con eventos del mercado de valores.

Se conserva dentro del inventario, pero no forma parte de las 25 variables predictoras de `v10_hgb_financial_c3` ni constituye la fuente principal de `TARGET_24M`.

Su eventual incorporación deberá evaluarse en una versión posterior y únicamente si puede demostrarse que cada dato utilizado habría estado disponible antes de la fecha de decisión correspondiente.

---

## 12. Fuente F06 — `V_BALANCE_LINEAS_RESUMEN`

La vista del Data Warehouse de la Bolsa de Valores de Quito contiene información financiera resumida por empresa, año, grupo y línea contable.

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

- ACTIVO;
- PASIVO;
- PATRIMONIO.

La unidad de registro corresponde a una línea financiera de una empresa en un período determinado.

Esta fuente no forma parte del vector predictivo final v10.

Su función actual es:

- validación;
- contraste;
- potencial enriquecimiento futuro.

---

## 13. Fuente F07 — `V_RESULTADOS_LINEAS_RESUMEN`

Esta vista mantiene una estructura técnica similar a la fuente de balances y contiene información del estado de resultados.

El grupo identificado es:

- RESULTADOS.

Entre las líneas disponibles se encuentran:

- Ingreso por Actividad;
- Costo de Ventas;
- Gastos Administrativos;
- Gastos Financieros;
- Gastos de Venta;
- Utilidad Bruta;
- Utilidad Operativa;
- Utilidad Neta;
- Impuestos;
- Participación Trabajadores;
- Amortizaciones;
- Depreciaciones.

Esta fuente tampoco forma parte de las 25 variables predictoras del modelo v10.

Se mantiene como fuente complementaria para contraste y posible evolución posterior.

---

## 14. Fuente F08 — Información de emisores y emisiones BVQ

La fuente interna:

`emisores_emisiones`

se mantiene disponible como fuente complementaria de la Bolsa de Valores de Quito.

Su estructura, cobertura histórica e identificadores deben documentarse de manera completa antes de incorporarla formalmente a un pipeline futuro.

Puede resultar útil para enriquecer información de:

- emisiones históricas;
- tipo de instrumento;
- monto emitido;
- fechas relevantes;
- características de emisores comparables.

Estas posibilidades coinciden con recomendaciones obtenidas durante la validación con especialistas B36.

Su eventual incorporación corresponde a evolución futura del producto y no modifica el modelo v10 congelado.

---

## 15. Rol actual de las fuentes

La arquitectura de datos vigente puede resumirse de la siguiente manera.

### Variables predictoras

`SCVS — bi_ranking`
→ variables empresariales y financieras principales
→ integración con histórico armonizado cuando corresponde
→ ingeniería de características
→ 25 variables del modelo final

### Fuente financiera complementaria

`SCVS — estados financieros históricos`
→ homologación
→ auditoría
→ recuperación de observaciones
→ fallback controlado de activos y patrimonio

### Variable objetivo

`SCVS — Registro del Mercado de Valores`
→ primera inscripción efectiva como emisor
→ validación cruzada de fecha
→ `TARGET_24M`

### Fuentes complementarias

`DWH BVQ + fuentes internas`
→ validación
→ contraste
→ contexto de negocio
→ potencial enriquecimiento futuro

Esta separación evita confundir fuentes efectivamente utilizadas por el modelo final con fuentes disponibles únicamente para análisis, contraste o evolución.

---

## 16. Relación con el modelo final

El modelo final congelado es:

`v10_hgb_financial_c3`

Configuración:

`C3_CONSERVATIVE`

Algoritmo:

`HistGradientBoostingClassifier`

El modelo utiliza exactamente:

`25 variables predictoras`

La provincia se conserva como contexto operacional y filtro, pero no forma parte del vector predictivo final.

Las fuentes complementarias internas de BVQ tampoco se incorporan automáticamente al modelo.

Cualquier nueva fuente o variable predictiva deberá evaluarse en una nueva versión, por ejemplo:

`v11`

---

## 17. Consideraciones temporales

Una variable únicamente puede utilizarse para priorizar una empresa si habría estado disponible antes o en la fecha de decisión correspondiente.

Por esta razón deben controlarse:

- año del período financiero;
- fecha de disponibilidad;
- fecha de presentación cuando exista;
- fecha de publicación cuando exista;
- fecha de decisión;
- horizonte del target;
- fecha de ocurrencia del evento futuro.

En v10 se utiliza la regla normativa de disponibilidad:

`01 de mayo de t+1`

para los estados financieros del ejercicio `t`.

Las variables `t-1` se construyen únicamente con información histórica.

Los datos posteriores pueden utilizarse para evaluar retrospectivamente el resultado, pero no para modificar retroactivamente el ranking histórico.

---

## 18. Datos 2024 y 2025

Los datos financieros 2024 y 2025 pueden estar disponibles en las fuentes originales.

Sin embargo, no forman parte del universo supervisado v10.

La razón metodológica es que la construcción del target exige una ventana futura completa de 24 meses bajo una regla comparable.

Su disponibilidad física no implica que puedan incorporarse retrospectivamente al entrenamiento de v10.

Podrán evaluarse posteriormente para:

- scoring;
- nuevas versiones;
- análisis prospectivo;
- actualización operacional;

siempre bajo un protocolo temporal previamente definido.

---

## 19. Ranking operacional

El producto funcional utiliza información financiera correspondiente a:

`ANIO = 2023`

con fecha de decisión:

`2024-05-01`

El universo operacional contiene:

`137.156 empresas`

Archivo principal:

`data/processed/v10_operational_ranking_2024_05_01.csv.gz`

El ranking utiliza exclusivamente el modelo v10 congelado.

El evento futuro real no se utiliza para modificar el ranking generado para esa fecha.

---

## 20. Condiciones de acceso, uso y licencia

Las fuentes utilizadas fueron revisadas desde la perspectiva de procedencia, acceso y condiciones de reutilización.

### 20.1 Información SCVS

**Fuente:** Superintendencia de Compañías, Valores y Seguros.

Incluye:

- información financiera empresarial;
- `bi_ranking`;
- estados financieros históricos;
- Registro del Mercado de Valores;
- fichas registrales;
- hechos relevantes.

**Condición de acceso:** información obtenida de fuentes, archivos y servicios institucionales utilizados durante el proyecto.

**Licencia identificada:** en la revisión documental registrada el 20 de septiembre de 2026 no se identificó una licencia abierta específica aplicable a los archivos utilizados, como Creative Commons, Open Data Commons u otra equivalente.

Por esta razón:

- se mantiene la atribución a la SCVS;
- no se presume una autorización irrestricta de redistribución;
- no se asigna una licencia abierta que la institución no haya publicado expresamente.

**Fecha de verificación documental registrada:** 20 de septiembre de 2026.

### 20.2 Información interna de la Bolsa de Valores de Quito

Incluye:

- `V_BALANCE_LINEAS_RESUMEN`;
- `V_RESULTADOS_LINEAS_RESUMEN`;
- `emisores_emisiones`;
- otras fuentes institucionales internas que puedan utilizarse para validación o enriquecimiento.

**Condición de acceso:** información institucional de acceso interno.

**Uso en el proyecto:** validación, contraste, conocimiento de negocio y potencial enriquecimiento futuro.

**Licencia:** no se considera información abierta ni se le asigna una licencia pública de reutilización.

Su utilización se limita al entorno autorizado del proyecto y de la Bolsa de Valores de Quito.

Los datos internos no deben publicarse ni redistribuirse mediante el repositorio GitHub.

---

## 21. Criterio adoptado para reutilización

| Fuente | Acceso | Licencia abierta identificada | Tratamiento |
|---|---|---|---|
| SCVS — información financiera | Institucional | No identificada explícitamente en la revisión registrada | Uso académico con atribución |
| SCVS — Registro del Mercado de Valores | Institucional | No identificada explícitamente en la revisión registrada | Uso académico con atribución |
| DWH y fuentes internas BVQ | Acceso institucional | No aplica como fuente abierta | Uso interno autorizado; no redistribuir |

La ausencia de una licencia abierta identificada no se interpreta como autorización irrestricta de reutilización.

Antes de una publicación externa de datasets derivados o de una explotación comercial fuera del alcance autorizado deberá verificarse nuevamente:

- normativa aplicable;
- términos de uso;
- condiciones institucionales;
- restricciones de redistribución;
- protección de información que corresponda.

---

## 22. Reglas de almacenamiento

Los archivos originales se conservan sin modificación dentro de:

`data/raw/`

Los datos originales y los datasets empresariales sensibles no se almacenan directamente en GitHub.

El archivo `.gitignore` excluye los contenidos definidos como no versionables.

Los resultados de transformación se organizan en:

- `data/interim`: resultados intermedios y datos armonizados;
- `data/processed`: datasets preparados para análisis, modelado y producto.

Los scripts necesarios para reproducir las transformaciones sí se mantienen bajo control de versiones.

---

## 23. Datos que no deben publicarse directamente

El repositorio del proyecto debe priorizar:

- código;
- configuración no sensible;
- documentación;
- protocolos;
- resultados agregados;
- métricas;
- metadatos;
- pruebas.

No deben publicarse sin autorización:

- fuentes originales de acceso restringido;
- información interna BVQ;
- datasets operacionales completos;
- credenciales;
- archivos `.env`;
- secretos;
- información empresarial que deba mantenerse fuera del repositorio público.

Esta revisión deberá realizarse antes de modificar la visibilidad del repositorio GitHub.

---

## 24. Trazabilidad documental

La información relacionada con las fuentes se complementa con:

- `README.md`;
- `docs/v10_dataset_freeze.md`;
- `docs/v10_split_freeze.md`;
- `docs/v10_feature_set_freeze.md`;
- `docs/v10_features_dataset_freeze.md`;
- `docs/v10_final_candidate_freeze.md`;
- `docs/v10_final_test_protocol.md`;
- `docs/v10_final_test_results.md`;
- `docs/diccionario_datos.md`;
- `docs/entorno_tecnico.md`;
- `docs/bitacora.md`;
- `docs/backlog.md`.

Los documentos históricos del MVP y de los baselines anteriores se conservan como evidencia de evolución y no sustituyen la documentación final de v10.

---

## 25. Estado actual

El inventario vigente refleja las fuentes utilizadas y evaluadas durante el desarrollo de Prospect Finder BVQ v10.

Estado final:

- `bi_ranking` es la fuente financiera principal del universo v10;
- el histórico financiero 2015–2023 se utiliza como fuente complementaria, de auditoría y fallback controlado;
- el Registro del Mercado de Valores SCVS es la fuente de `TARGET_24M`;
- `listado_entes` y `codigos_fichas_registrales` presentaron 619 fechas efectivas coincidentes en la validación;
- el universo supervisado final contiene 1.030.671 observaciones empresa-año;
- el modelo final utiliza 25 predictores;
- las fuentes internas BVQ no forman parte automáticamente del vector predictivo;
- los datos 2024–2025 no se incorporan al universo supervisado congelado v10;
- el producto operacional utiliza el corte 2023 con fecha de decisión 2024-05-01;
- las fuentes adicionales permanecen sujetas a evaluación antes de incorporarse a una nueva versión del modelo;
- la publicación de datos deberá respetar las condiciones de acceso, licencia y confidencialidad documentadas.

La referencia metodológica vigente es v10.