# Diccionario de datos — Prospect Finder BVQ

## 1. Propósito

Este documento describe las variables, campos operacionales y estructuras de datos vigentes de **Prospect Finder BVQ v10**.

Su objetivo es mantener trazabilidad sobre:

- nombre técnico;
- significado;
- origen;
- tipo de dato;
- temporalidad;
- transformación;
- utilización dentro del modelo;
- utilización dentro del producto;
- tratamiento de valores faltantes;
- consideraciones de leakage, calidad e interpretación.

Este documento reemplaza la descripción histórica del MVP y del Baseline v1 como referencia principal del proyecto.

La versión vigente utiliza información correspondiente al período:

`2012–2023`

y el modelo final congelado:

`v10_hgb_financial_c3`

con configuración:

`C3_CONSERVATIVE`

---

## 2. Unidades de análisis

El proyecto utiliza dos unidades diferentes según la etapa.

### 2.1 Modelado

La unidad analítica es:

`empresa-año`

Cada fila representa la información de una empresa para un año determinado.

La identificación técnica principal utiliza:

`EXPEDIENTE_KEY + ANIO`

El RUC se conserva como identificador empresarial y mecanismo de integración, pero no se utiliza como predictor.

### 2.2 Producto operacional

La unidad del producto es:

`empresa`

Para el ranking operacional actual se utiliza una observación por empresa correspondiente a:

`ANIO = 2023`

con fecha de decisión:

`2024-05-01`

Cada empresa aparece una sola vez dentro del ranking.

---

## 3. Fuentes principales

### 3.1 Superintendencia de Compañías, Valores y Seguros — información financiera y empresarial

Constituye la fuente principal para construir las variables empresariales y financieras utilizadas por v10.

Entre la información integrada se encuentran:

- activos;
- patrimonio;
- ingresos por ventas;
- número de empleados;
- utilidad neta;
- tipo de compañía;
- provincia;
- información histórica necesaria para rezagos;
- información utilizada para controles de calidad.

Los distintos archivos y estructuras históricas son integrados antes de construir las features del modelo.

### 3.2 Registro del Mercado de Valores

Se utiliza para construir:

`TARGET_24M`

a partir de la primera inscripción conocida de cada emisor.

El evento se utiliza exclusivamente para:

- entrenamiento;
- validación;
- TEST;
- evaluaciones retrospectivas posteriores.

No se presenta como variable de entrada en el producto operacional.

### 3.3 Bolsa de Valores de Quito

La información de la BVQ se utiliza como fuente complementaria para:

- contraste;
- validación;
- conocimiento de negocio;
- potencial enriquecimiento futuro.

No constituye una variable predictiva automática por el solo hecho de estar disponible.

---

## 4. Principales artefactos de datos v10

### 4.1 Base integrada

`data/processed/v10_base_integrated_2012_2023.csv.gz`

Contiene la base integrada utilizada para construir las features v10.

### 4.2 Dataset core

`data/processed/v10_features_core_2012_2023.csv.gz`

Contiene:

`22 columnas`

Incluye:

- identificación;
- target;
- split;
- variables financieras actuales;
- variables del período anterior;
- tipo de compañía;
- provincia;
- banderas de calidad.

### 4.3 Dataset financiero

`data/processed/v10_features_financial_2012_2023.csv.gz`

Contiene:

`1.030.671 observaciones`

y:

`32 columnas`

Agrega al dataset core:

- `fin_ratio_patrimonio_activos`;
- `fin_roa`;
- `fin_margen_neto`;
- `fin_rotacion_activos`;
- `fin_roe`;
- `flag_patrimonio_no_positivo`;
- `fin_crecimiento_activos`;
- `fin_crecimiento_patrimonio`;
- `fin_crecimiento_ventas`;
- `fin_crecimiento_empleados`.

Este es el dataset de features utilizado por el modelo final y por la explicación operacional.

---

# 5. Variables de identificación y trazabilidad

## 5.1 `ANIO`

**Descripción:** año de la observación financiera.

**Tipo:** entero.

**Uso como predictor:** no.

**Uso metodológico:** sí.

Permite:

- mantener la secuencia temporal;
- generar rezagos;
- construir el target;
- asignar los splits;
- seleccionar la observación operacional 2023.

---

## 5.2 `EXPEDIENTE_KEY`

**Descripción:** identificador estable utilizado para relacionar una empresa entre datasets y componentes operacionales.

**Tipo:** entero / identificador.

**Uso como predictor:** no.

**Uso operacional:** sí.

Es la clave principal utilizada por:

- ranking operacional;
- API;
- PostgreSQL;
- explicabilidad individual;
- similitud con emisores.

No debe interpretarse como característica empresarial.

---

## 5.3 `RUC`

**Descripción:** Registro Único de Contribuyentes de la empresa.

**Tipo:** texto / identificador.

**Uso como predictor:** no.

**Uso operacional:** sí.

Permite:

- identificar empresas;
- búsqueda;
- integración entre fuentes;
- validación;
- presentación en la ficha.

Debe conservarse como texto para evitar pérdida de formato.

---

## 5.4 `NOMBRE`

**Descripción:** razón social de la empresa.

**Tipo:** texto.

**Uso como predictor:** no.

**Uso operacional:** sí.

Se utiliza para:

- presentación;
- búsqueda;
- validación.

No se utiliza como predictor para evitar que el modelo aprenda patrones asociados al texto del nombre.

---

## 5.5 `SPLIT`

**Descripción:** identifica el conjunto temporal asignado a la observación.

**Tipo:** categórica metodológica.

**Valores vigentes de v10:**

| Valor | Período |
|---|---|
| `TRAIN` | 2012–2018 |
| `EMBARGO_1` | 2019 |
| `VALIDATION` | 2020 |
| `EMBARGO_2` | 2021 |
| `TEST` | 2022–2023 |

**Uso como predictor:** no.

**Uso metodológico:** sí.

La división temporal fue congelada antes de la apertura final de TEST.

---

## 5.6 `provincia`

**Descripción:** provincia registrada para la empresa.

**Tipo:** categórica / texto.

**Uso como predictor:** **no**.

**Uso operacional:** sí.

Se utiliza para:

- filtros;
- análisis descriptivo;
- análisis de concentración;
- revisión de sesgos;
- presentación.

La provincia permanece expresamente fuera de las 25 variables predictivas del modelo v10.

---

# 6. Variable objetivo

## 6.1 `TARGET_24M`

**Descripción:** indica si una empresa que todavía no era emisora en la fecha de decisión correspondiente se registra por primera vez como emisor dentro de los siguientes 24 meses.

**Tipo:** binaria.

**Valores:**

- `1`: ocurre la primera inscripción dentro del horizonte;
- `0`: no ocurre dentro del horizonte.

**Fuente:** Registro del Mercado de Valores.

**Uso como predictor:** no.

**Uso:** entrenamiento y evaluación.

### Regla temporal

Para cada observación empresa-año:

1. la empresa debe ser elegible en el momento de decisión;
2. no debe ser ya emisor;
3. el evento positivo se determina únicamente con la primera inscripción dentro del horizonte futuro definido.

El target nunca forma parte del vector predictivo.

En el producto operacional el target no se expone al usuario.

---

# 7. Protocolo temporal v10

La división congelada utilizada por el proyecto es:

| Conjunto | Período | Observaciones | Positivos |
|---|---:|---:|---:|
| TRAIN | 2012–2018 | 470.722 | 407 |
| EMBARGO 1 | 2019 | 91.934 | 34 |
| VALIDATION | 2020 | 98.471 | 34 |
| EMBARGO 2 | 2021 | 109.099 | 39 |
| TEST | 2022–2023 | 260.445 | 54 |

Los períodos de embargo permiten reducir el riesgo de contaminación temporal alrededor de los períodos de evaluación.

---

# 8. Variables financieras actuales

## 8.1 `activos_final`

**Descripción:** activos totales consolidados para el período actual.

**Tipo:** numérica continua.

**Unidad:** monetaria.

**Uso en modelo v10:** sí.

**Uso en producto:** sí.

Representa una medida de escala empresarial.

---

## 8.2 `patrimonio_final`

**Descripción:** patrimonio consolidado para el período actual.

**Tipo:** numérica continua.

**Unidad:** monetaria.

**Uso en modelo v10:** sí.

**Uso en producto:** sí.

Puede presentar valores no positivos. Esa condición se conserva adicionalmente mediante una bandera específica.

---

## 8.3 `bi_ingresos_ventas`

**Descripción:** ingresos por ventas correspondientes al período actual.

**Tipo:** numérica continua.

**Unidad:** monetaria.

**Uso en modelo v10:** sí.

**Uso en producto:** sí.

---

## 8.4 `bi_n_empleados`

**Descripción:** número de empleados disponible para la empresa en el período actual.

**Tipo:** numérica.

**Unidad:** personas.

**Uso en modelo v10:** sí.

**Uso en producto:** sí.

Dispone de controles de calidad específicos debido a posibles anomalías o saltos temporales.

---

# 9. Variables rezagadas `t-1`

Estas variables representan información correspondiente al período anual inmediatamente anterior cuando existe información histórica compatible.

## 9.1 `activos_final_t1`

**Descripción:** activos del período anterior.

**Tipo:** numérica continua.

**Uso en modelo:** sí.

---

## 9.2 `patrimonio_final_t1`

**Descripción:** patrimonio del período anterior.

**Tipo:** numérica continua.

**Uso en modelo:** sí.

---

## 9.3 `bi_ingresos_ventas_t1`

**Descripción:** ingresos por ventas del período anterior.

**Tipo:** numérica continua.

**Uso en modelo:** sí.

---

## 9.4 `bi_n_empleados_t1`

**Descripción:** número de empleados del período anterior.

**Tipo:** numérica.

**Uso en modelo:** sí.

---

# 10. Indicadores financieros derivados

## 10.1 `fin_ratio_patrimonio_activos`

**Descripción:** relación entre patrimonio y activos.

**Tipo:** numérica continua.

**Interpretación conceptual:**

`patrimonio / activos`

**Uso en modelo:** sí.

**Uso en producto:** sí.

---

## 10.2 `fin_roa`

**Descripción:** indicador de rentabilidad sobre activos.

**Tipo:** numérica continua.

**Interpretación conceptual:** relaciona utilidad neta con activos.

**Uso en modelo:** sí.

**Uso en producto:** sí.

Puede ser negativo cuando el resultado neto es negativo.

---

## 10.3 `fin_margen_neto`

**Descripción:** margen neto observado para la empresa.

**Tipo:** numérica continua.

**Interpretación conceptual:** relaciona utilidad neta con ingresos por ventas.

**Uso en modelo:** sí.

**Uso en producto:** sí.

---

## 10.4 `fin_rotacion_activos`

**Descripción:** relación entre actividad comercial y activos.

**Tipo:** numérica continua.

**Interpretación conceptual:** relaciona ingresos por ventas con activos.

**Uso en modelo:** sí.

**Uso en producto:** sí.

---

## 10.5 `fin_roe`

**Descripción:** indicador de rentabilidad sobre patrimonio.

**Tipo:** numérica continua.

**Interpretación conceptual:** relaciona utilidad neta con patrimonio cuando el denominador permite una medición válida.

**Uso en modelo:** sí.

**Uso en producto:** sí.

---

# 11. Variables de crecimiento

Las variables de crecimiento utilizan información de los períodos actual y anterior.

Su cálculo se realiza dentro del builder:

`src/features/build_v10_financial_features.py`

Las reglas de construcción preservan valores faltantes cuando no existe información histórica suficiente o cuando una operación no puede calcularse de forma válida.

## 11.1 `fin_crecimiento_activos`

**Descripción:** variación relativa de activos entre el período actual y `t-1`.

**Tipo:** numérica continua.

**Uso en modelo:** sí.

---

## 11.2 `fin_crecimiento_patrimonio`

**Descripción:** variación relativa del patrimonio entre el período actual y `t-1`.

**Tipo:** numérica continua.

**Uso en modelo:** sí.

---

## 11.3 `fin_crecimiento_ventas`

**Descripción:** variación relativa de ingresos por ventas entre el período actual y `t-1`.

**Tipo:** numérica continua.

**Uso en modelo:** sí.

---

## 11.4 `fin_crecimiento_empleados`

**Descripción:** variación relativa del número de empleados entre el período actual y `t-1`.

**Tipo:** numérica continua.

**Uso en modelo:** sí.

---

# 12. Variables booleanas y de calidad utilizadas por el modelo

## 12.1 `TIENE_T_MENOS_1`

**Descripción:** indica disponibilidad de información compatible del período anterior.

**Tipo:** booleana.

**Uso en modelo:** sí.

Permite que el modelo distinga entre una observación con y sin historia anual previa disponible.

---

## 12.2 `flag_activos_negativos`

**Descripción:** identifica observaciones con activos negativos.

**Tipo:** booleana.

**Uso en modelo:** sí.

**Finalidad:** conservar explícitamente una condición atípica de calidad o consistencia.

---

## 12.3 `flag_ventas_negativas`

**Descripción:** identifica observaciones con ingresos por ventas negativos.

**Tipo:** booleana.

**Uso en modelo:** sí.

---

## 12.4 `flag_empleados_fijo`

**Descripción:** identifica patrones considerados anómalos o artificialmente constantes en la información de empleados según las reglas de preparación v10.

**Tipo:** booleana.

**Uso en modelo:** sí.

---

## 12.5 `flag_empleados_salto_temporal`

**Descripción:** identifica cambios temporales atípicos en la serie de número de empleados.

**Tipo:** booleana.

**Uso en modelo:** sí.

---

## 12.6 `flag_empleados_anomalia_total`

**Descripción:** indicador consolidado de anomalía en información de empleados.

**Tipo:** booleana.

**Uso en modelo:** sí.

---

## 12.7 `flag_patrimonio_no_positivo`

**Descripción:** identifica observaciones en las que el patrimonio es menor o igual a cero.

**Tipo:** booleana.

**Uso en modelo:** sí.

Permite conservar explícitamente una condición relevante para interpretar determinados indicadores patrimoniales.

---

# 13. Variable categórica del modelo

## 13.1 `tipo_compania`

**Descripción:** forma societaria registrada para la empresa.

**Tipo:** categórica.

**Uso en modelo:** sí.

**Uso en producto:** sí.

La variable se procesa como categoría nativa del modelo.

Las categorías utilizadas durante inferencia se alinean con las categorías observadas en TRAIN.

Las categorías posteriores no deben redefinir retrospectivamente el vocabulario utilizado durante el entrenamiento de v10.

---

# 14. Vector predictivo final v10

El modelo final utiliza exactamente:

`25 variables`

distribuidas en:

- `17` numéricas;
- `7` booleanas;
- `1` categórica.

## 14.1 Variables numéricas

1. `activos_final`
2. `patrimonio_final`
3. `bi_ingresos_ventas`
4. `bi_n_empleados`
5. `activos_final_t1`
6. `patrimonio_final_t1`
7. `bi_ingresos_ventas_t1`
8. `bi_n_empleados_t1`
9. `fin_ratio_patrimonio_activos`
10. `fin_roa`
11. `fin_margen_neto`
12. `fin_rotacion_activos`
13. `fin_roe`
14. `fin_crecimiento_activos`
15. `fin_crecimiento_patrimonio`
16. `fin_crecimiento_ventas`
17. `fin_crecimiento_empleados`

## 14.2 Variables booleanas

18. `TIENE_T_MENOS_1`
19. `flag_activos_negativos`
20. `flag_ventas_negativas`
21. `flag_empleados_fijo`
22. `flag_empleados_salto_temporal`
23. `flag_empleados_anomalia_total`
24. `flag_patrimonio_no_positivo`

## 14.3 Variable categórica

25. `tipo_compania`

Este orden debe mantenerse consistente con el artefacto congelado.

---

# 15. Modelo final asociado al diccionario

**Nombre:**

`v10_hgb_financial_c3`

**Configuración:**

`C3_CONSERVATIVE`

**Algoritmo:**

`HistGradientBoostingClassifier`

**Artefacto:**

`models/v10/v10_hgb_financial_c3_final.joblib`

El artefacto registra:

- modelo;
- nombre del modelo;
- configuración;
- lista de features;
- variables numéricas;
- variables booleanas;
- variable categórica;
- target;
- período de entrenamiento;
- período de TEST.

El modelo permanece congelado.

Ninguna modificación posterior del frontend, SHAP o motor de similitud cambia estas 25 variables.

---

# 16. Tratamiento de tipos y faltantes

## 16.1 Variables numéricas

Las variables numéricas se convierten al tipo requerido por el modelo.

Los valores infinitos se normalizan como faltantes antes de procesos como explicabilidad.

El modelo final conserva la lógica validada de v10 para trabajar con valores faltantes.

No debe aplicarse retrospectivamente la estrategia histórica del Baseline v1 basada en:

`SimpleImputer + StandardScaler`

porque esa descripción corresponde a una etapa anterior y no al modelo final v10.

---

## 16.2 Variables booleanas

Se conservan conceptualmente como:

- `0`;
- `1`;
- valor faltante cuando corresponda.

---

## 16.3 Variable categórica

`tipo_compania`

se procesa con categorías provenientes de TRAIN.

---

# 17. Variables expresamente excluidas del modelo v10

No forman parte del vector predictivo:

- `ANIO`;
- `EXPEDIENTE_KEY`;
- `RUC`;
- `NOMBRE`;
- `SPLIT`;
- `provincia`;
- `TARGET_24M`;
- fechas de inscripción;
- ranking;
- score;
- percentiles;
- variables de similitud;
- datos obtenidos después de la fecha de decisión.

También fueron excluidos preventivamente durante la construcción de v10 campos administrativos o con riesgo de leakage, entre ellos:

- `cia_imvalores`;
- `id_estado_financiero`;
- `posicion_general`.

---

# 18. Control de data leakage

Los principales controles de v10 son:

- separación temporal;
- períodos de embargo;
- target construido hacia adelante;
- exclusión de empresas que ya eran emisoras al momento correspondiente;
- exclusión del target y fechas futuras del vector predictivo;
- categorías de `tipo_compania` aprendidas desde TRAIN;
- construcción de rezagos únicamente con información histórica;
- congelamiento del modelo antes de TEST;
- no utilización de eventos posteriores para alterar retrospectivamente el ranking operacional.

La información posterior a la fecha de decisión puede utilizarse para evaluación retrospectiva, pero no para modificar el resultado histórico.

---

# 19. Ranking operacional

El producto actual utiliza:

`ANIO = 2023`

Fecha de decisión:

`2024-05-01`

Universo prospectable:

`137.156 empresas`

Archivo:

`data/processed/v10_operational_ranking_2024_05_01.csv.gz`

El score se presenta en la interfaz como:

**Índice de Afinidad Bursátil**

No representa una probabilidad calibrada.

---

# 20. Tabla `operational_prospects`

PostgreSQL almacena una fila por empresa operacional.

Tabla:

`operational_prospects`

Registros:

`137.156`

## 20.1 Identificación

| Campo | Tipo lógico | Descripción |
|---|---|---|
| `expediente_key` | entero | Clave principal del prospecto |
| `ruc` | texto | RUC de la empresa |
| `nombre` | texto | Razón social |
| `anio` | entero | Año financiero utilizado |
| `fecha_decision` | fecha | Fecha de decisión operacional |
| `tipo_compania` | texto | Forma societaria |
| `provincia` | texto | Provincia registrada |

## 20.2 Ranking

| Campo | Tipo lógico | Descripción |
|---|---|---|
| `ranking` | entero | Posición global dentro del universo |
| `score_afinidad` | decimal | Score generado por v10 |
| `percentil_ranking` | decimal | Posición relativa dentro del universo |

`score_afinidad` no debe interpretarse como una probabilidad.

## 20.3 Calidad y cobertura

| Campo | Tipo lógico | Descripción |
|---|---|---|
| `n_features_disponibles` | entero | Número de features consideradas disponibles |
| `pct_features_disponibles` | decimal | Porcentaje de disponibilidad utilizado como señal de calidad |

Estos campos describen cobertura.

No modifican por sí mismos el score ya calculado.

## 20.4 Información financiera expuesta

| Campo | Tipo lógico |
|---|---|
| `activos_final` | decimal |
| `patrimonio_final` | decimal |
| `bi_ingresos_ventas` | decimal |
| `bi_n_empleados` | decimal |
| `fin_ratio_patrimonio_activos` | decimal |
| `fin_roa` | decimal |
| `fin_margen_neto` | decimal |
| `fin_rotacion_activos` | decimal |
| `fin_roe` | decimal |
| `fin_crecimiento_activos` | decimal |
| `fin_crecimiento_patrimonio` | decimal |
| `fin_crecimiento_ventas` | decimal |
| `fin_crecimiento_empleados` | decimal |

## 20.5 Trazabilidad de modelo

| Campo | Descripción |
|---|---|
| `modelo` | Nombre de la versión de modelo utilizada |
| `configuracion_modelo` | Configuración del modelo |

---

# 21. Motor de similitud con emisores históricos

La similitud es un componente independiente del modelo predictivo.

No modifica:

- `score_afinidad`;
- ranking;
- percentil.

No existe una fórmula como:

`afinidad + similitud`

Las dos señales se presentan por separado.

## 21.1 Variables de similitud

El motor utiliza siete dimensiones:

1. activos;
2. patrimonio;
3. ingresos por ventas;
4. número de empleados;
5. patrimonio / activos;
6. ROA;
7. rotación de activos.

Las variables se llevan a percentiles anuales y posteriormente se calcula una distancia euclidiana.

La similitud se expresa en una escala:

`0–100`

Una mayor similitud representa mayor cercanía financiera dentro de este espacio.

No representa probabilidad de emisión.

---

# 22. Tabla `issuer_similarity_summary`

Tabla:

`issuer_similarity_summary`

Registros:

`137.156`

| Campo | Tipo lógico | Descripción |
|---|---|---|
| `expediente_key` | entero | Empresa prospecto |
| `comparables_disponibles` | booleano | Indica si fue posible calcular comparables |
| `similitud_emisor_top1` | decimal | Similitud con el emisor histórico más cercano |
| `similitud_emisores_top5_promedio` | decimal | Promedio de similitud de los cinco primeros comparables |
| `distancia_emisor_top1` | decimal | Distancia del comparable más cercano |
| `n_emisores_comparados` | entero | Número de perfiles evaluados |
| `estado_similitud` | texto | Estado del cálculo |
| `metodologia_similitud` | texto | Descripción metodológica registrada |

Cobertura actual:

- empresas con similitud calculable: `131.320`;
- empresas sin información suficiente: `5.836`.

La falta de similitud no elimina a una empresa del ranking.

---

# 23. Tabla `issuer_similarity_matches`

Tabla:

`issuer_similarity_matches`

Registros:

`656.600`

Cada prospecto con información suficiente puede tener hasta cinco comparables históricos.

| Campo | Descripción |
|---|---|
| `id` | Identificador del registro |
| `expediente_key` | Prospecto analizado |
| `ranking_v10` | Ranking del prospecto |
| `score_afinidad` | Score v10 del prospecto |
| `orden_comparable` | Posición del comparable, de 1 a 5 |
| `similitud` | Índice de similitud 0–100 |
| `distancia_percentiles` | Distancia euclidiana en el espacio de percentiles |
| `emisor_expediente_key` | Identificador del emisor comparable |
| `emisor_ruc` | RUC del emisor |
| `emisor_nombre` | Nombre del emisor |
| `emisor_anio_perfil` | Año del perfil financiero utilizado |
| `emisor_fecha_decision_perfil` | Fecha de decisión asociada al perfil |
| `emisor_fecha_primera_inscripcion` | Primera inscripción conocida como emisor |
| `emisor_tipo_compania` | Tipo de compañía del emisor |
| `emisor_provincia` | Provincia del emisor |
| `mismo_tipo_compania` | Indica si prospecto y emisor comparten tipo societario |

Los emisores utilizados como referencia deben ser conocidos hasta la fecha de decisión correspondiente.

---

# 24. Universo de referencia de similitud

Para el corte:

`2024-05-01`

se identificaron:

`288 emisores conocidos`

De ellos:

`272`

disponían de perfiles completos para las siete variables requeridas.

Los emisores posteriores al corte no se utilizan como referencia operacional.

---

# 25. Campos de explicabilidad SHAP

La API de explicabilidad individual devuelve información asociada a cada factor.

Los principales campos son:

| Campo | Descripción |
|---|---|
| `feature` | Nombre técnico de la variable |
| `label` | Nombre comprensible para el usuario |
| `value` | Valor observado de la empresa |
| `shap_value` | Contribución SHAP con signo |
| `abs_shap_value` | Magnitud absoluta de la contribución |
| `direction` | Sentido de la contribución |

Valores de `direction` utilizados por el frontend:

- `aumenta_afinidad`;
- `reduce_afinidad`;
- `sin_impacto`.

SHAP explica cómo una variable contribuyó al score del modelo.

No demuestra causalidad.

---

# 26. Etiquetas de negocio para explicabilidad

La capa de presentación utiliza etiquetas comprensibles.

| Variable técnica | Etiqueta |
|---|---|
| `activos_final` | Activos |
| `patrimonio_final` | Patrimonio |
| `bi_ingresos_ventas` | Ingresos por ventas |
| `bi_n_empleados` | Número de empleados |
| `activos_final_t1` | Activos del año anterior |
| `patrimonio_final_t1` | Patrimonio del año anterior |
| `bi_ingresos_ventas_t1` | Ingresos por ventas del año anterior |
| `bi_n_empleados_t1` | Número de empleados del año anterior |
| `fin_ratio_patrimonio_activos` | Relación patrimonio / activos |
| `fin_roa` | ROA |
| `fin_margen_neto` | Margen neto |
| `fin_rotacion_activos` | Rotación de activos |
| `fin_roe` | ROE |
| `fin_crecimiento_activos` | Crecimiento de activos |
| `fin_crecimiento_patrimonio` | Crecimiento de patrimonio |
| `fin_crecimiento_ventas` | Crecimiento de ventas |
| `fin_crecimiento_empleados` | Crecimiento de empleados |
| `TIENE_T_MENOS_1` | Disponibilidad de información histórica |
| `flag_activos_negativos` | Bandera de activos negativos |
| `flag_ventas_negativas` | Bandera de ventas negativas |
| `flag_empleados_fijo` | Bandera de empleados con valor fijo |
| `flag_empleados_salto_temporal` | Bandera de salto temporal en empleados |
| `flag_empleados_anomalia_total` | Bandera de anomalía en empleados |
| `flag_patrimonio_no_positivo` | Bandera de patrimonio no positivo |
| `tipo_compania` | Tipo de compañía |

---

# 27. Campos visibles en la interfaz

La versión funcional del frontend presenta principalmente:

### Ranking

- ranking;
- empresa;
- provincia;
- tipo de compañía;
- Índice de Afinidad Bursátil;
- percentil;
- nivel relativo de prioridad, mediante referencias como Top 1 %, Top 5 % y Top 10 %;
- similitud con emisor;
- calidad.

### Ficha individual

- razón social;
- RUC;
- provincia;
- tipo de compañía;
- ranking;
- score;
- percentil;
- nivel relativo de prioridad;
- activos;
- patrimonio;
- ingresos por ventas;
- empleados;
- factores SHAP;
- comparables históricos;
- próximo paso comercial;
- advertencias de interpretación.

Los niveles Top son una clasificación de presentación derivada de la posición relativa de la empresa dentro del ranking.

No representan una probabilidad adicional ni modifican el score generado por el modelo.

El próximo paso comercial funciona como orientación para continuar el análisis humano y no constituye una decisión automatizada.

No todos los campos existentes en PostgreSQL deben mostrarse simultáneamente.

La capa de presentación prioriza información útil para análisis comercial.

---

# 28. Diferencia entre datos de modelo y datos de producto

Debe mantenerse la siguiente separación:

| Tipo | Ejemplos | ¿Afecta el score? |
|---|---|---|
| Predictor v10 | activos, ventas, crecimiento, tipo compañía | Sí |
| Identificación | RUC, nombre, expediente | No |
| Contexto | provincia | No |
| Resultado | score, ranking, percentil | Resultado del modelo |
| Calidad | disponibilidad | No modifica retroactivamente el score |
| Similitud | comparables, similitud 0–100 | No |
| Explicabilidad | SHAP | Explica el score; no lo modifica |

---

# 29. Control de interpretación

## 29.1 Score

`score_afinidad`

es una señal relativa de priorización.

No es una probabilidad calibrada.

## 29.2 Percentil

`percentil_ranking`

ubica relativamente a la empresa dentro del universo operacional.

No representa probabilidad.

## 29.3 Similitud

La similitud mide cercanía de perfil financiero frente a emisores históricos.

No constituye una predicción independiente.

## 29.4 SHAP

SHAP describe contribuciones al resultado del modelo.

No demuestra causalidad.

---

# 30. Campos no expuestos como señales predictivas

Los siguientes datos pueden existir en fuentes o procesos internos, pero no deben confundirse con variables del modelo:

- RUC;
- nombre;
- expediente;
- provincia;
- fechas de inscripción;
- ranking;
- comparables;
- similitud;
- variables de interfaz;
- campos administrativos;
- eventos conocidos posteriormente.

---

# 31. Archivos operacionales

Ranking:

`data/processed/v10_operational_ranking_2024_05_01.csv.gz`

Resumen de similitud:

`data/processed/v10_issuer_similarity_summary_2024_05_01.csv.gz`

Comparables:

`data/processed/v10_issuer_similarity_matches_2024_05_01.csv.gz`

Top 500 utilizado como salida de revisión:

`reports/results/v10/product/v10_operational_top500_2024_05_01.csv`

Los datasets operacionales contienen información empresarial y no forman parte del código fuente publicado.

---

# 32. Persistencia PostgreSQL

La base operacional contiene:

| Tabla | Registros |
|---|---:|
| `operational_prospects` | 137.156 |
| `issuer_similarity_summary` | 137.156 |
| `issuer_similarity_matches` | 656.600 |
| **Total** | **930.912** |

La base es utilizada por FastAPI.

El frontend no consulta PostgreSQL directamente.

---

# 33. API y exposición de datos

Los principales endpoints relacionados con este diccionario son:

`GET /api/prospects`

`GET /api/prospects/{expediente_key}`

`GET /api/catalogs`

`GET /api/explainability/global`

`GET /api/explainability/prospects/{expediente_key}`

La API funciona como capa de separación entre:

- frontend;
- PostgreSQL;
- modelo;
- servicios de explicabilidad.

---

# 34. Normalización de textos

La capa operacional normaliza textos utilizados para presentación y filtros.

Esto permite reducir diferencias producidas por:

- espacios finales;
- espacios internos repetidos;
- inconsistencias menores de formato.

La normalización de presentación no modifica retroactivamente las categorías con las que fue entrenado el modelo.

---

# 35. Calidad de información

El proyecto conserva señales explícitas de calidad en dos niveles.

### Nivel de features

Banderas como:

- activos negativos;
- ventas negativas;
- patrimonio no positivo;
- anomalías de empleados;
- disponibilidad de `t-1`.

### Nivel de producto

Campos como:

- `n_features_disponibles`;
- `pct_features_disponibles`.

La calidad no debe utilizarse como regla automática de rechazo de una empresa.

---

# 36. Variables y datos futuros

El modelo v10 se encuentra congelado.

Por tanto, variables nuevas no deben incorporarse retroactivamente.

Cualquier cambio que modifique el vector predictivo deberá evaluarse en una nueva versión, por ejemplo:

`v11`

Entre las posibles ampliaciones predictivas podrían considerarse:

- tendencias multianuales;
- promedios móviles;
- volatilidad;
- información sectorial adicional;
- variables macroeconómicas;
- nuevas fuentes empresariales;
- información interna BVQ con justificación metodológica.

La validación con especialistas B36 también identificó oportunidades de enriquecimiento del producto, entre ellas:

- indicador de liquidez;
- datos de contacto;
- información histórica de emisiones;
- tipo y valor de papeles emitidos por empresas comparables;
- segmentación adicional por tamaño y actividad económica;
- información sobre impagos y calificaciones de emisiones comparables;
- notas de seguimiento comercial;
- funcionalidades tipo CRM;
- simulaciones financieras relacionadas con una potencial emisión.

Estas recomendaciones no implican que todos esos datos deban convertirse en predictores.

Cada elemento deberá definirse según su función:

- predictor potencial;
- filtro;
- dato descriptivo;
- información comercial;
- atributo de comparables;
- funcionalidad de seguimiento;
- apoyo para análisis humano.

Toda nueva variable predictiva deberá documentar:

- fuente;
- fecha de disponibilidad;
- definición;
- fórmula;
- cobertura;
- tratamiento de faltantes;
- riesgo de leakage;
- justificación;
- efecto sobre reproducibilidad.

Las mejoras exclusivamente operacionales o de interfaz deberán mantenerse separadas del Feature Set del modelo.

---

# 37. Mantenimiento del diccionario

Este documento deberá actualizarse cuando:

- se incorpore una nueva versión del modelo;
- cambie una variable;
- cambie una fórmula;
- cambie una fuente;
- cambie una regla de temporalidad;
- cambie la estructura operacional;
- cambie el contrato de la API;
- cambie una tabla PostgreSQL;
- cambie la lógica de similitud;
- cambie la salida de explicabilidad;
- se agreguen nuevas variables de producto.

Los cambios relevantes deben registrarse también en la bitácora del proyecto.

---

# 38. Estado actual

El diccionario vigente documenta:

- dataset v10 2012–2023;
- target `TARGET_24M`;
- protocolo temporal v10;
- 25 predictores del modelo final;
- variables actuales y `t-1`;
- ratios financieros;
- crecimiento;
- banderas de calidad;
- variable categórica `tipo_compania`;
- exclusión de `provincia` del modelo;
- ranking operacional;
- score y percentil;
- niveles relativos de prioridad;
- campos de calidad;
- motor de similitud;
- tablas PostgreSQL;
- campos SHAP;
- campos visibles en el frontend;
- próximo paso comercial;
- oportunidades de enriquecimiento identificadas en la validación con especialistas.

El prototipo asociado a este diccionario se encuentra implementado, probado y validado.

Evidencia de cierre:

| Evidencia | Resultado |
|---|---:|
| Pruebas automáticas API | 12 aprobadas |
| Pruebas automatizadas frontend | 4 aprobadas |
| Pruebas funcionales B37 | 10 de 10 aprobadas |
| Participantes validación B36 | 4 |
| Promedio global B36 | 4,82 / 5 |
| Experiencia general B36 | 5,00 / 5 |
| Utilidad para prospección B36 | 4,75 / 5 |

La referencia metodológica vigente es v10.

El modelo `v10_hgb_financial_c3` permanece congelado.

Las recomendaciones posteriores de usuarios se registran como evolución del producto y no modifican retrospectivamente las 25 variables, el target, los hiperparámetros, el split temporal ni los resultados TEST.

Los componentes correspondientes al antiguo MVP y Baseline v1 se conservan únicamente como evidencia histórica del proceso de desarrollo y no deben utilizarse para describir el modelo final.