# Dataset v10 — Congelamiento de universo, target e integración de fuentes

## 1. Propósito

Este documento registra las decisiones metodológicas y los controles utilizados para congelar la base integrada v10 del proyecto Prospect Finder BVQ.

La base v10 constituye el universo supervisado sobre el cual se desarrollarán posteriormente la ingeniería de variables y los modelos de aprendizaje automático.

El congelamiento busca asegurar:

- reproducibilidad;
- trazabilidad de las fuentes;
- consistencia temporal;
- control de fuga de información;
- conservación de evidencia histórica;
- separación entre construcción del dataset y entrenamiento de modelos.

A partir de este punto, cualquier modificación que altere el universo, el target, las reglas de identidad o la integración de fuentes deberá tratarse como una nueva versión del dataset.

---

## 2. Archivo congelado

Archivo generado:

`data/processed/v10_base_integrated_2012_2023.csv.gz`

Script reproducible:

`scripts/build_v10_base.py`

SHA-256 del archivo validado:

`b44f9ccf309c20a59be436953a0c6e7f9a3dc1f11cc6f2c87e41c1676a3a2a8d`

El archivo procesado no se almacena en Git debido a su tamaño y a las reglas de exclusión definidas en `.gitignore`. Su construcción queda reproducida mediante el script correspondiente.

---

## 3. Período de análisis

El universo congelado cubre ejercicios financieros:

**2012–2023**

La selección de 2012 como año inicial responde a la mejora estructural observada en la disponibilidad de información financiera a partir de ese ejercicio.

Los ejercicios 2024 y 2025 no forman parte del universo supervisado v10 debido a que no disponen todavía de una ventana completa de 24 meses para construir el target de manera comparable.

Estos ejercicios podrán utilizarse posteriormente para scoring o análisis prospectivo, pero no se incorporan al entrenamiento supervisado congelado de esta versión.

---

## 4. Unidad de observación

La unidad de observación es:

**empresa-año**

La clave técnica utilizada para controlar duplicados es:

`ANIO + EXPEDIENTE_KEY`

El dataset final contiene:

- 1.030.671 observaciones elegibles;
- 0 duplicados empresa-año;
- 568 observaciones positivas;
- 310 RUC positivos únicos;
- prevalencia total de 0,055110 %.

---

## 5. Fecha de decisión y ventana temporal

Para un ejercicio financiero `t` se utiliza como fecha de decisión:

**01 de mayo de t+1**

Esta fecha representa una regla temporal normativa basada en la disponibilidad ordinaria de la información financiera anual.

No representa necesariamente la fecha real de presentación individual de cada estado financiero.

La ventana objetivo corresponde a los siguientes 24 meses:

**01/05/t+1 hasta 30/04/t+3**

La construcción temporal evita utilizar como predictor información posterior a la fecha de decisión.

---

## 6. Definición del target

El evento positivo corresponde a:

**primera inscripción efectiva de una empresa como emisor de valores dentro de los 24 meses posteriores a la fecha de decisión.**

La fuente principal del evento es:

`listado_entes_65001_1789908466941.xlsx`

La fecha utilizada es la primera fecha efectiva de inscripción asociada al RUC.

La fuente fue contrastada con:

`codigos_fichas_registrales_1789908530079.xlsx`

Para la validación se consideraron como estados efectivos en fichas registrales:

- `VIGENTE`
- `CANCELADA`

No se consideran eventos positivos registros con estados como:

- inscripción negada;
- ente creado;
- en proceso de inscripción.

La validación final produjo:

- 619 RUC con primera inscripción efectiva en `listado_entes`;
- 619 RUC equivalentes al restringir fichas registrales a estados efectivos;
- 619 fechas coincidentes;
- 0 diferencias de fecha entre las dos fuentes efectivas.

---

## 7. Exclusión de empresas que ya eran emisores

Una observación empresa-año no es elegible cuando la empresa ya era emisor antes de su fecha de decisión.

Regla:

`fecha_primera_inscripcion < fecha_decision`

Después de resolver la identidad empresarial, se excluyeron:

**4.088 observaciones empresa-año**

por corresponder a empresas que ya tenían condición de emisor antes de la fecha de decisión.

---

## 8. Fuentes financieras utilizadas

La base v10 integra dos universos principales.

### 8.1 bi_ranking

Fuente:

`data/raw/scvs/ranking/bi_ranking.csv`

Cobertura utilizada:

**2012–2023**

Esta fuente constituye la fuente financiera principal de v10.

Incluye, entre otras variables:

- activos;
- patrimonio;
- ingresos y ventas;
- ingresos totales;
- utilidad antes de impuestos;
- impuesto a la renta;
- utilidad del ejercicio;
- utilidad neta;
- número de empleados;
- segmento;
- CIIU;
- indicadores financieros;
- gastos;
- deuda.

### 8.2 Dataset financiero histórico

Fuente:

`data/interim/scvs_financials_harmonized_2015_2023.csv.gz`

Cobertura:

**2015–2023**

Esta fuente se conserva para:

- ampliar el universo histórico;
- recuperar observaciones empresa-año ausentes de `bi_ranking`;
- realizar fallback controlado de activos y patrimonio;
- mantener evidencia de auditoría.

No se utiliza como reemplazo indiscriminado de `bi_ranking`.

---

## 9. Unión de universos

Antes de aplicar elegibilidad y controles de identidad, la unión produjo:

**1.035.294 empresa-año**

sin duplicados.

Después de aplicar elegibilidad, la procedencia del dataset congelado es:

- `AMBAS`: 815.331 observaciones;
- `SOLO_BI`: 146.683 observaciones;
- `SOLO_HISTORICO`: 68.657 observaciones.

Esta estrategia evita utilizar `bi_ranking` como universo exclusivo, lo que habría eliminado observaciones históricas válidas y algunos positivos.

---

## 10. Identidad empresarial

La variable principal de identidad es el RUC.

La prioridad de identificación es:

1. `bi_compania`;
2. RUC histórico único asociado al mismo `EXPEDIENTE`;
3. RUC de la fila histórica, únicamente si los anteriores no están disponibles.

El catálogo `bi_compania` utiliza `EXPEDIENTE` como clave principal de enlace.

Durante la auditoría se comprobó que los RUC del target presentes en `bi_compania` no presentaban ambigüedad de múltiples expedientes dentro del universo analizado.

---

## 11. Observaciones sin RUC

Después de aplicar las reglas determinísticas de recuperación de identidad permanecieron:

- 535 filas sin RUC utilizable;
- 276 expedientes únicos.

Estas observaciones fueron excluidas del universo supervisado.

La razón es que sin RUC no puede establecerse de manera confiable si la entidad:

- ya era emisor antes de la fecha de decisión; o
- se convirtió en emisor dentro de la ventana futura de 24 meses.

No se realizaron coincidencias por nombre ni técnicas de fuzzy matching para recuperar estos registros.

Esto evita asignar implícitamente una etiqueta negativa sin evidencia suficiente.

---

## 12. Discrepancia de RUC identificada

Se identificó una única discrepancia entre el RUC histórico y `bi_compania`:

- Expediente: `749052`
- Empresa: `CIMA INMOBIL CIMABIL S.A.S.`
- RUC histórico: `0916053283001`
- RUC en `bi_compania`: `0993379824001`

La empresa presenta valores financieros coincidentes entre las fuentes para 2023.

Ninguno de los dos RUC aparece en el target histórico.

Para v10 se conserva como identidad principal el RUC de `bi_compania` y se mantiene la discrepancia mediante la variable:

`ruc_difiere`

No se realizó corrección manual.

---

## 13. Validación de activos y patrimonio entre fuentes

Sobre 818.667 empresa-año comunes entre las fuentes históricas 2015–2023 se observó una coincidencia superior al 99,6 % para activos y patrimonio considerando diferencias al centavo.

Sin embargo, las discrepancias restantes no correspondían únicamente a redondeos.

Se identificaron casos con:

- ceros en `bi_ranking` frente a valores financieros históricos;
- cambios de signo en patrimonio;
- diferencias materiales entre fuentes.

Por esta razón no se aplicaron promedios ni conciliaciones automáticas.

---

## 14. Bloques financieros vacíos de bi_ranking

Se definió un bloque financiero básico compuesto por ocho variables:

1. activos;
2. patrimonio;
3. ingresos por ventas;
4. ingresos totales;
5. utilidad antes de impuestos;
6. impuesto a la renta;
7. utilidad del ejercicio;
8. utilidad neta.

Cuando las ocho variables de `bi_ranking` son simultáneamente cero, la observación se marca mediante:

`bi_8_finanzas_cero`

En el dataset elegible final existen:

**31.744 observaciones**

con esta condición.

El patrón se había observado especialmente en determinados años y planes contables y fue tratado como ausencia de información financiera útil en `bi_ranking`, no automáticamente como ocho ceros económicos reales.

---

## 15. Regla final para activos

La variable utilizada para modelado será:

`activos_final`

Regla:

1. utilizar `bi_activos` cuando existe información financiera válida en `bi_ranking`;
2. si el bloque de ocho variables BI está completamente en cero y existe valor histórico, utilizar `activos_old`;
3. si la empresa-año existe únicamente en el histórico, utilizar `activos_old`;
4. si ninguna fuente válida dispone del valor, mantener faltante.

La aplicación de esta regla produjo:

- 92.640 fallbacks históricos;
- 1.022.910 valores disponibles;
- cobertura final de 99,25 %.

La variable:

`activos_fallback_old`

permite identificar las observaciones en las que se utilizó el respaldo histórico.

---

## 16. Regla final para patrimonio

La variable utilizada para modelado será:

`patrimonio_final`

La regla es equivalente a la aplicada en activos:

1. prioridad a `bi_patrimonio` cuando el bloque financiero BI es válido;
2. fallback a `patrimonio_old` cuando el bloque BI está completamente en cero;
3. utilización del histórico para registros presentes exclusivamente en esa fuente;
4. faltante cuando no existe valor confiable.

Resultado:

- 92.640 fallbacks históricos;
- 1.022.910 valores disponibles;
- cobertura final de 99,25 %.

La variable:

`patrimonio_fallback_old`

conserva la trazabilidad de esta decisión.

---

## 17. Regla final para utilidad neta

La utilidad neta histórica no se considera compatible con la definición de `bi_ranking`.

En la comparación de fuentes se identificó que el dataset histórico contenía una gran cantidad de ceros donde `bi_ranking` mostraba utilidades o pérdidas.

Por ello:

1. `utilidad_neta_final` utiliza únicamente `bi_utilidad_neta`;
2. solo se utiliza cuando el bloque financiero BI no está completamente en cero;
3. no se realiza fallback desde `utilidad_neta_old_auditoria`;
4. para observaciones exclusivamente históricas, la utilidad neta final permanece como faltante.

La variable histórica se conserva exclusivamente para auditoría.

Resultado:

- 930.270 valores de utilidad neta disponibles;
- cobertura final de 90,26 %.

---

## 18. Variables excluidas intencionalmente

Las siguientes columnas disponibles en `bi_ranking` no se incorporan al dataset v10 de modelado:

### `cia_imvalores`

Se excluye por potencial riesgo de fuga de información hasta disponer de una definición documental que descarte relación directa con la condición de emisor.

### `id_estado_financiero`

Se excluye por tratarse de un identificador técnico sin justificación como predictor.

### `posicion_general`

Se excluye porque corresponde a una posición de ranking y no se utilizará como predictor financiero directo.

Estas exclusiones quedan implementadas en `scripts/build_v10_base.py`.

---

## 19. Variables de procedencia y auditoría

El dataset conserva variables que permiten reconstruir cómo se obtuvo cada observación, incluyendo:

- `tipo_fuente`;
- `fuente_bi`;
- `fuente_old`;
- `fuente_ruc`;
- `ruc_difiere`;
- `bi_8_finanzas_cero`;
- `activos_fallback_old`;
- `patrimonio_fallback_old`;
- valores originales de `bi_ranking`;
- valores históricos utilizados para auditoría.

Estas variables no deben interpretarse automáticamente como predictores.

Su inclusión en la base integrada tiene como objetivo principal garantizar trazabilidad y control de calidad.

---

## 20. Distribución final del target

| Año | Elegibles | Positivos | Prevalencia |
|---:|---:|---:|---:|
| 2012 | 42.158 | 55 | 0,130462 % |
| 2013 | 47.140 | 49 | 0,103946 % |
| 2014 | 52.528 | 39 | 0,074246 % |
| 2015 | 76.468 | 43 | 0,056233 % |
| 2016 | 79.503 | 73 | 0,091820 % |
| 2017 | 83.107 | 89 | 0,107091 % |
| 2018 | 89.818 | 59 | 0,065688 % |
| 2019 | 91.934 | 34 | 0,036983 % |
| 2020 | 98.471 | 34 | 0,034528 % |
| 2021 | 109.099 | 39 | 0,035747 % |
| 2022 | 123.289 | 32 | 0,025955 % |
| 2023 | 137.156 | 22 | 0,016040 % |

Total:

- elegibles: **1.030.671**
- positivos: **568**
- RUC positivos únicos: **310**
- prevalencia: **0,055110 %**

---

## 21. Comparabilidad con versiones anteriores

Las versiones v1–v9 se preservan como evidencia histórica del desarrollo.

No deben compararse directamente sus resultados con futuros modelos v10 sin considerar el cambio de universo y de variables.

Para 2015–2023:

- el dataset histórico contenía 423 observaciones positivas;
- v10 conserva las 423;
- v10 incorpora además 2 positivos en 2015;
- ambos corresponden a empresa-año disponibles en `bi_ranking` que no estaban presentes en el universo financiero histórico anterior.

Por tanto, v10 contiene:

**425 positivos entre 2015–2023**

sin pérdida de positivos históricos.

Los años 2012–2014 incorporan adicionalmente:

**143 positivos**

para un total v10 de 568.

---

## 22. Reproducibilidad

El archivo fue construido inicialmente y posteriormente reconstruido desde las fuentes mediante:

`scripts/build_v10_base.py`

La reconstrucción independiente produjo exactamente el mismo SHA-256:

`b44f9ccf309c20a59be436953a0c6e7f9a3dc1f11cc6f2c87e41c1676a3a2a8d`

Esto confirma reproducibilidad binaria del dataset generado bajo las mismas fuentes, versiones de software y reglas implementadas.

---

## 23. Estado del dataset

**Estado: CONGELADO**

El congelamiento comprende:

- período 2012–2023;
- unidad empresa-año;
- reglas de identidad;
- universo de observaciones;
- definición del target;
- fecha de decisión;
- ventana futura de 24 meses;
- exclusión de emisores previos;
- integración `bi_ranking` + histórico;
- reglas de fallback de activos y patrimonio;
- regla de utilidad neta;
- exclusión de filas sin RUC;
- exclusión preventiva de variables con riesgo de fuga;
- controles de reproducibilidad.

El congelamiento no implica que todas las columnas de la base integrada serán utilizadas como predictores.

La selección definitiva de variables, tratamiento de faltantes, transformaciones, winsorización/capping, ingeniería temporal y pipelines de modelado se realizará en etapas posteriores.

Las transformaciones estadísticas aprendidas de los datos deberán calcularse únicamente sobre TRAIN para evitar fuga de información.

---

## 24. Próxima etapa

La siguiente etapa será construir el **feature set v10** a partir de esta base congelada.

Antes del entrenamiento se deberán definir explícitamente:

- variables elegibles como predictores;
- variables exclusivamente administrativas o de auditoría;
- reglas de missingness;
- variables temporales `t-1`;
- transformaciones;
- tratamiento de valores extremos;
- variables categóricas;
- estrategia temporal de TRAIN / embargo / validación / TEST.

El conjunto TEST permanecerá cerrado hasta completar la selección metodológica correspondiente.
