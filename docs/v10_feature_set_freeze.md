# Congelamiento del Feature Set núcleo v10

**Proyecto:** Prospect Finder BVQ  
**Versión:** v10  
**Estado:** CONGELADO  
**Fecha:** octubre de 2026

---

## 1. Propósito

Este documento define el conjunto de características utilizado como núcleo para la primera generación de modelos v10.

El Feature Set se construirá exclusivamente a partir del dataset base congelado:

`data/processed/v10_base_integrated_2012_2023.csv.gz`

El universo base contiene:

- 1.030.671 observaciones empresa-año;
- ejercicios 2012-2023;
- 568 observaciones positivas;
- 310 empresas positivas únicas;
- variable objetivo `TARGET_24M`.

El Feature Set no modifica el dataset base congelado.

---

## 2. Principio general

El objetivo del Feature Set núcleo es construir un baseline:

- temporalmente válido;
- reproducible;
- interpretable;
- disponible a lo largo de la mayor parte del período;
- robusto frente a cambios de cobertura de las fuentes;
- libre de información posterior a la fecha de decisión;
- suficientemente simple para servir como referencia frente a modelos posteriores.

La unidad de análisis continúa siendo:

`empresa-año`

---

## 3. Variables numéricas actuales del núcleo

Se utilizarán como variables numéricas observadas en el ejercicio `t`:

1. `activos_final`
2. `patrimonio_final`
3. `bi_ingresos_ventas`
4. `bi_n_empleados`

### Justificación

`activos_final` y `patrimonio_final` presentan cobertura cercana al 100 % durante todo el período y utilizan las reglas de integración ya congeladas en v10.

`bi_ingresos_ventas` y `bi_n_empleados` presentan menor cobertura en determinados años, pero contienen información económica relevante y tienen disponibilidad suficiente para el conjunto positivo.

Los faltantes no provocarán eliminación automática de observaciones.

---

## 4. Variables categóricas actuales del núcleo

Se utilizarán:

1. `tipo_compania`
2. `provincia`

Estas variables se tratarán como categóricas.

No se utilizarán simultáneamente:

- `provincia`
- `codigo_provincia`

para evitar representar dos veces la misma dimensión geográfica.

La representación oficial del núcleo será:

`provincia`

---

## 5. Variables temporales t-1

Para cada una de las cuatro variables numéricas principales se construirá un lag de un ejercicio:

1. `activos_final_t1`
2. `patrimonio_final_t1`
3. `bi_ingresos_ventas_t1`
4. `bi_n_empleados_t1`

El lag será válido únicamente cuando exista una observación de la misma empresa en el ejercicio inmediatamente anterior:

`t - 1`

No se utilizará la última observación disponible si existe un salto de uno o más años.

---

## 6. Disponibilidad temporal

En el dataset base:

- 83,75 % de las observaciones tienen una fila exacta `t-1`;
- 86,97 % de las observaciones positivas tienen una fila exacta `t-1`.

Cobertura de lags entre positivos:

- `activos_final_t1`: 86,27 %;
- `patrimonio_final_t1`: 86,27 %;
- `bi_ingresos_ventas_t1`: 82,39 %;
- `bi_n_empleados_t1`: 82,39 %.

La ausencia de `t-1` no implica eliminar una observación.

En particular, las observaciones de 2012 permanecen en TRAIN aunque no dispongan de historial 2011 dentro del dataset v10.

---

## 7. Feature Set núcleo congelado

Las variables predictoras directas del núcleo son:

### Numéricas actuales

- `activos_final`
- `patrimonio_final`
- `bi_ingresos_ventas`
- `bi_n_empleados`

### Numéricas históricas

- `activos_final_t1`
- `patrimonio_final_t1`
- `bi_ingresos_ventas_t1`
- `bi_n_empleados_t1`

### Categóricas

- `tipo_compania`
- `provincia`

Total de variables predictoras base:

`10`

Este número corresponde a variables conceptuales previas a cualquier expansión producida por codificación categórica.

---

## 8. Variables reservadas para extensión controlada

Las siguientes variables no forman parte del núcleo inicial, pero podrán evaluarse posteriormente mediante experimentos separados:

- `bi_cod_segmento`
- `bi_ciiu_n1`

Esta variante se identificará como Feature Set enriquecido o extensión sectorial.

Su incorporación deberá medirse frente al mismo baseline núcleo usando exclusivamente VALIDATION para la comparación.

`bi_ciiu_n6` no forma parte del núcleo debido a su alta cardinalidad.

---

## 9. Variables financieras enriquecidas excluidas del núcleo

Por el momento quedan fuera:

- `utilidad_neta_final`
- `bi_ingresos_totales`
- `bi_utilidad_an_imp`
- `bi_impuesto_renta`
- `bi_utilidad_ejercicio`

También quedan fuera del núcleo los indicadores financieros oficiales:

- liquidez;
- prueba ácida;
- endeudamiento;
- apalancamiento;
- rotaciones;
- períodos de cobro y pago;
- márgenes;
- rentabilidades;
- ROE;
- ROA;
- gastos;
- depreciaciones;
- amortizaciones;
- costos;
- deuda.

La razón principal es su disponibilidad temporal heterogénea y, para los indicadores oficiales, el quiebre estructural de cobertura observado antes de 2018.

Estas variables podrán formar parte de experimentos enriquecidos posteriores, pero no del primer baseline v10.

---

## 10. Tratamiento especial de 2014

Durante la auditoría se identificó que en 2014:

- `bi_ingresos_totales` presenta 98,14 % de valores cero;
- `bi_utilidad_an_imp` presenta 98,52 % de valores cero;
- `bi_utilidad_ejercicio` presenta 98,02 % de valores cero;
- `utilidad_neta_final` presenta 94,10 % de valores cero.

Además, existen decenas de miles de observaciones con ventas positivas y estas variables iguales a cero.

Por tanto, estos valores no se interpretarán automáticamente como ceros económicos reales en experimentos posteriores.

Ninguna de estas variables forma parte del Feature Set núcleo.

---

## 11. Reglas determinísticas de calidad

El dataset base congelado conservará siempre los valores originales.

Las reglas descritas a continuación se aplicarán únicamente al construir el Feature Set.

### 11.1 Activos negativos

Si:

`activos_final < 0`

el valor utilizado como predictor se convertirá a `NaN`.

El dato original permanece en la base congelada.

Se identificaron 7 casos.

### 11.2 Ventas negativas

Si:

`bi_ingresos_ventas < 0`

el valor utilizado como predictor se convertirá a `NaN`.

Se identificaron 6 casos.

### 11.3 Empleados

`bi_n_empleados` se convertirá a `NaN` cuando se cumpla al menos una de estas condiciones:

1. valor menor que cero;
2. valor superior a 50.000;
3. existen al menos dos observaciones históricas previas;
4. el valor actual es al menos 1.000;
5. el valor actual es al menos 100 veces la mediana histórica previa de la misma empresa.

La mediana histórica utiliza únicamente observaciones anteriores.

La auditoría identificó:

- 24 casos por regla fija;
- 153 casos por salto temporal;
- 165 observaciones únicas afectadas.

---

## 12. Utilidades extremas

Aunque las utilidades no forman parte del núcleo, quedan documentadas las reglas para futuros Feature Sets enriquecidos.

Se identificaron:

- 11 anomalías extremas en utilidad antes de impuestos;
- 12 anomalías extremas en utilidad del ejercicio;
- 1 anomalía extrema en utilidad neta.

Los valores identificados como anomalías no serán corregidos manualmente.

En un Feature Set que utilice estas variables:

- el valor anómalo se convertirá a `NaN`;
- se conservará la trazabilidad de la regla aplicada;
- no se sustituirá por una cifra inferida manualmente.

---

## 13. Impacto sobre la clase positiva

La auditoría conjunta de reglas de calidad identificó:

`180`

observaciones con al menos una anomalía evaluada.

Observaciones positivas afectadas:

`0`

Por tanto, las reglas determinísticas documentadas no eliminan ni modifican directamente ninguna de las 568 observaciones positivas.

---

## 14. Variables de auditoría que no entran al modelo

Quedan excluidas como predictores:

- `tipo_fuente`
- `fuente_bi`
- `fuente_old`
- `fuente_ruc`
- `ruc_difiere`
- `bi_8_finanzas_cero`
- `activos_fallback_old`
- `patrimonio_fallback_old`
- `ruc_old_fila`
- `nombre_old`
- `plan_contable_old`
- `activos_old`
- `patrimonio_old`
- `utilidad_neta_old_auditoria`
- `ruc_catalogo`
- `nombre_catalogo`
- `ruc_hist_unico`
- `n_ruc_hist`

Estas variables existen para integración, trazabilidad o auditoría de fuentes.

No deben permitir que el modelo aprenda diferencias artificiales entre fuentes o períodos de cobertura.

---

## 15. Identificadores que no entran al modelo

Quedan excluidos:

- `EXPEDIENTE_KEY`
- `RUC`
- `NOMBRE`

Podrán conservarse en el dataset de features únicamente como columnas administrativas para trazabilidad y vinculación de resultados.

No serán incluidas en la matriz predictora `X`.

---

## 16. Variables temporales y objetivo excluidos

No se utilizarán como predictores:

- `fecha_decision`
- `fin_ventana_24m`
- `fecha_primera_inscripcion`
- `TARGET_24M`

`TARGET_24M` se utilizará exclusivamente como variable objetivo `y`.

`fecha_primera_inscripcion` contiene información del evento futuro y por tanto está expresamente excluida de la matriz predictora.

---

## 17. Año

`ANIO` se conservará como columna administrativa para:

- split temporal;
- validación;
- reportes;
- análisis de estabilidad;
- métricas por período.

No formará parte del Feature Set núcleo como predictor.

Esto evita que el primer baseline utilice directamente el año como aproximación de cambios temporales en la prevalencia o en la cobertura de fuentes.

---

## 18. Años de embargo como fuente histórica

Los ejercicios de embargo:

- 2019;
- 2021;

no se utilizarán como observaciones para ajustar modelos.

Sin embargo, sus variables explicativas pueden utilizarse como información histórica `t-1` para construir una observación posterior.

Ejemplos:

- VALIDATION 2020 puede utilizar variables 2019 como `t-1`;
- TEST 2022 puede utilizar variables 2021 como `t-1`.

No se utiliza el target del año de embargo como información predictora.

---

## 19. Valores faltantes

Las filas no se eliminarán automáticamente por presentar valores faltantes.

En particular:

- no se eliminarán observaciones sin `t-1`;
- no se eliminarán observaciones por ausencia de variables BI;
- no se eliminarán observaciones positivas por falta parcial de información.

Las estrategias de imputación se definirán dentro del pipeline de modelado.

Cualquier parámetro de imputación deberá aprenderse exclusivamente con TRAIN.

---

## 20. Transformaciones

El Feature Set físico conservará los valores numéricos limpios sin aplicar todavía:

- estandarización;
- normalización;
- winsorización aprendida;
- clipping aprendido;
- logaritmos;
- imputación estadística;
- codificación one-hot;
- target encoding.

Estas transformaciones pertenecerán al pipeline de modelado.

Sus parámetros deberán ajustarse exclusivamente sobre TRAIN.

---

## 21. Crecimientos y variaciones

Los lags `t-1` sí forman parte del núcleo.

Las tasas de crecimiento, diferencias porcentuales y tendencias derivadas no forman parte del Feature Set núcleo inicial.

Podrán evaluarse posteriormente como una extensión separada.

Esta decisión evita introducir inicialmente inestabilidad por:

- denominadores iguales a cero;
- patrimonios negativos;
- valores cercanos a cero;
- faltantes de `t-1`;
- valores extremos.

---

## 22. Split temporal asociado

El Feature Set v10 utilizará exclusivamente el split congelado:

`TRAIN 2012-2018 -> EMBARGO 2019 -> VALIDATION 2020 -> EMBARGO 2021 -> TEST 2022-2023`

Documento asociado:

`docs/v10_split_freeze.md`

TEST permanece cerrado para evaluación predictiva.

---

## 23. Feature sets previstos

Se distinguen inicialmente dos configuraciones.

### v10-core

Variables:

- activos;
- patrimonio;
- ventas;
- empleados;
- lags exactos `t-1` de esas cuatro variables;
- tipo de compañía;
- provincia.

Esta será la configuración utilizada para establecer el primer baseline v10.

### v10-sector

Extensión de `v10-core` incorporando:

- `bi_cod_segmento`;
- `bi_ciiu_n1`.

Su aporte se evaluará posteriormente en VALIDATION.

No sustituye automáticamente al núcleo.

---

## 24. Reglas de selección

El Feature Set no se modificará en función del desempeño observado en TEST.

Cualquier nueva variable o conjunto de variables deberá:

1. tener justificación económica o metodológica;
2. estar disponible antes de la fecha de decisión;
3. tener trazabilidad hasta su fuente;
4. ser evaluado con TRAIN y VALIDATION;
5. documentarse como una nueva configuración o versión si modifica el conjunto congelado.

---

## 25. Estado final

**Feature Set núcleo v10: CONGELADO**

Configuración oficial:

### v10-core

Numéricas `t`:

- `activos_final`
- `patrimonio_final`
- `bi_ingresos_ventas`
- `bi_n_empleados`

Numéricas `t-1`:

- `activos_final_t1`
- `patrimonio_final_t1`
- `bi_ingresos_ventas_t1`
- `bi_n_empleados_t1`

Categóricas:

- `tipo_compania`
- `provincia`

Total:

`10 variables predictoras conceptuales`

El siguiente paso será implementar estas reglas en un script reproducible para construir el dataset físico de features v10.

No se entrenará ningún modelo hasta que dicho dataset sea construido y validado.
