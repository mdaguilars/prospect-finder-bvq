# Diccionario de datos — Prospect Finder BVQ

## 1. Propósito

Este documento describe las principales variables utilizadas en el proyecto Prospect Finder BVQ.

El objetivo es mantener trazabilidad sobre:

- nombre de la variable;
- significado;
- origen;
- tipo de dato;
- transformación aplicada;
- disponibilidad;
- tratamiento de valores faltantes;
- utilización dentro del modelo;
- consideraciones metodológicas.

Este diccionario corresponde al MVP desarrollado con información financiera del período 2015–2023.

---

## 2. Unidad de análisis

La unidad de análisis del proyecto es:

**empresa-año**

Cada observación representa la información disponible para una empresa en un período anual determinado.

La empresa se identifica principalmente mediante su RUC.

La clave conceptual de una observación es:

`RUC + ANIO`

---

## 3. Variable objetivo

La variable objetivo es:

`TARGET_24M`

Esta variable indica si una empresa que todavía no era emisora en una determinada fecha de corte se registra por primera vez como emisor dentro de los siguientes 24 meses.

Interpretación:

- `1`: se registra por primera vez como emisor dentro del horizonte definido.
- `0`: no se registra como nuevo emisor dentro de ese horizonte.

Las empresas que ya eran emisoras en la fecha de corte correspondiente son excluidas del universo elegible.

---

## 4. Fuentes principales

### 4.1 SCVS — Estados financieros

Fuente principal utilizada para construir las variables financieras predictoras.

Información utilizada:

- cuentas contables;
- identificación de empresas;
- clasificación CIIU;
- información histórica anual.

Ubicación:

`data/raw/scvs/estados_financieros/`

---

### 4.2 SCVS — Registro del Mercado de Valores

Fuente utilizada para construir la variable objetivo.

Información principal:

- RUC del emisor;
- primera fecha de inscripción como emisor.

Ubicación:

`data/raw/scvs/mercado_valores/`

La primera inscripción fue contrastada entre dos fuentes del Registro del Mercado de Valores.

Se identificaron 619 RUC con información disponible en ambas fuentes y no se encontraron diferencias en la primera fecha de inscripción.

---

### 4.3 Bolsa de Valores Quito

La información del Data Warehouse de la BVQ se considera complementaria.

Su utilización actual se orienta a:

- validación;
- contraste;
- potencial enriquecimiento futuro.

No constituye la fuente principal de las variables utilizadas por el Baseline v1.

---

# 5. Variables de identificación y trazabilidad

## 5.1 RUC

**Nombre técnico:** `RUC`

**Descripción:**  
Registro Único de Contribuyentes utilizado para identificar a la empresa.

**Tipo:**  
Texto / identificador.

**Fuente:**  
SCVS.

**Unidad:**  
No aplica.

**Transformación:**  
Normalización como identificador.

**Uso en modelado:**  
No se utiliza como predictor.

**Uso en pipeline:**  
Sí.

**Finalidad:**

- integrar fuentes;
- identificar empresas;
- construir series históricas;
- asociar empresas con eventos de inscripción.

**Consideración:**  
Debe tratarse como identificador y no como variable numérica.

---

## 5.2 EXPEDIENTE

**Nombre técnico:** `EXPEDIENTE`

**Descripción:**  
Identificador administrativo disponible en información de la SCVS.

**Tipo:**  
Identificador.

**Fuente:**  
SCVS.

**Uso en modelado:**  
No.

**Uso:**  
Trazabilidad y validación.

---

## 5.3 NOMBRE

**Nombre técnico:** `NOMBRE`

**Descripción:**  
Nombre o razón social de la empresa.

**Tipo:**  
Texto.

**Fuente:**  
SCVS.

**Uso en modelado:**  
No.

**Uso potencial:**  
Presentación de resultados y validación posterior.

**Consideración:**  
No debe utilizarse como predictor porque podría introducir información no relacionada con la situación financiera de la empresa.

---

## 5.4 ANIO

**Nombre técnico:** `ANIO`

**Descripción:**  
Año correspondiente a la observación financiera.

**Tipo:**  
Entero.

**Fuente:**  
Derivado del período del estado financiero.

**Uso en modelado:**  
No se utiliza directamente como predictor en el Baseline v1.

**Uso en pipeline:**  
Sí.

**Finalidad:**

- construir la unidad empresa-año;
- ordenar temporalmente;
- construir el target;
- definir TRAIN, VALIDATION y TEST.

---

## 5.5 PLAN_CONTABLE

**Nombre técnico:** `PLAN_CONTABLE`

**Descripción:**  
Identifica la estructura contable de origen utilizada en determinado archivo o período.

**Tipo:**  
Categórica.

**Fuente:**  
Proceso de inventario y homologación de SCVS.

**Valores principales utilizados:**

- `PLAN_622`
- `PLAN_639`
- `PLAN_807`
- `PLAN_819`
- `PLAN_830`
- `PLAN_868`
- `PLAN_925`

**Uso en modelado:**  
No.

**Uso:**  
Trazabilidad y control de calidad.

**Justificación de exclusión:**  
El modelo no debe aprender diferencias administrativas o históricas asociadas con cambios de formato contable.

---

## 5.6 SPLIT

**Nombre técnico:** `SPLIT`

**Descripción:**  
Identifica el conjunto temporal al que pertenece cada observación.

**Tipo:**  
Categórica.

**Valores:**

- `TRAIN`
- `VALIDATION`
- `TEST`

**Asignación actual:**

- TRAIN: 2015–2020
- VALIDATION: 2021
- TEST: 2022–2023

**Uso en modelado:**  
No como predictor.

**Uso metodológico:**  
Sí.

---

# 6. Variables financieras base

## 6.1 ACTIVO_TOTAL

**Nombre técnico:** `ACTIVO_TOTAL`

**Descripción:**  
Valor total de los activos de la empresa.

**Tipo:**  
Numérica continua.

**Unidad:**  
Monetaria, según los valores reportados en la fuente.

**Fuente:**  
Estados financieros SCVS.

**Transformación:**  
Homologación entre diferentes planes contables.

**Disponibilidad en dataset armonizado:**  
Completa para las observaciones procesadas.

**Uso directo en Baseline v1:**  
No.

**Variable derivada utilizada:**  
`LOG_ACTIVO_TOTAL`

---

## 6.2 ACTIVO_CORRIENTE

**Nombre técnico:** `ACTIVO_CORRIENTE`

**Descripción:**  
Total de activos clasificados como corrientes.

**Tipo:**  
Numérica continua.

**Fuente:**  
Estados financieros SCVS.

**Transformación:**  
Homologación contable.

**Disponibilidad:**  
Completa en el dataset armonizado.

**Uso directo en Baseline v1:**  
No.

**Variables derivadas:**

- `LOG_ACTIVO_CORRIENTE`
- `LIQUIDEZ_CORRIENTE`

---

## 6.3 EFECTIVO

**Nombre técnico:** `EFECTIVO`

**Descripción:**  
Efectivo y equivalentes de efectivo reportados por la empresa.

**Tipo:**  
Numérica continua.

**Fuente:**  
Estados financieros SCVS.

**Transformación:**  
Homologación contable.

**Disponibilidad:**  
Completa en el dataset armonizado.

**Variables derivadas:**

- `LOG_EFECTIVO`
- `EFECTIVO_ACTIVOS`

---

## 6.4 PASIVO_TOTAL

**Nombre técnico:** `PASIVO_TOTAL`

**Descripción:**  
Valor total de las obligaciones de la empresa.

**Tipo:**  
Numérica continua.

**Fuente:**  
Estados financieros SCVS.

**Transformación:**  
Homologación contable.

**Disponibilidad:**  
Completa en el dataset armonizado.

**Variables derivadas:**

- `LOG_PASIVO_TOTAL`
- `ENDEUDAMIENTO`
- `PASIVO_CORRIENTE_PASIVO`

---

## 6.5 PASIVO_CORRIENTE

**Nombre técnico:** `PASIVO_CORRIENTE`

**Descripción:**  
Obligaciones clasificadas como corrientes.

**Tipo:**  
Numérica continua.

**Fuente:**  
Estados financieros SCVS.

**Transformación:**  
Homologación contable.

**Disponibilidad:**  
Completa en el dataset armonizado.

**Variables derivadas:**

- `LOG_PASIVO_CORRIENTE`
- `LIQUIDEZ_CORRIENTE`
- `PASIVO_CORRIENTE_PASIVO`

---

## 6.6 PASIVO_NO_CORRIENTE

**Nombre técnico:** `PASIVO_NO_CORRIENTE`

**Descripción:**  
Obligaciones clasificadas como no corrientes.

**Tipo:**  
Numérica continua.

**Fuente:**  
Estados financieros SCVS.

**Transformación:**  
Homologación contable.

**Disponibilidad:**  
Completa en el dataset armonizado.

**Variable derivada:**  
`LOG_PASIVO_NO_CORRIENTE`

---

## 6.7 PATRIMONIO

**Nombre técnico:** `PATRIMONIO`

**Descripción:**  
Valor patrimonial reportado por la empresa.

**Tipo:**  
Numérica continua.

**Fuente:**  
Estados financieros SCVS.

**Transformación:**  
Homologación contable.

**Disponibilidad:**  
Completa en el dataset armonizado.

**Variables derivadas:**

- `LOG_PATRIMONIO`
- `AUTONOMIA_FINANCIERA`

---

## 6.8 CAPITAL

**Nombre técnico:** `CAPITAL`

**Descripción:**  
Capital registrado dentro del estado financiero.

**Tipo:**  
Numérica continua.

**Fuente:**  
Estados financieros SCVS.

**Transformación:**  
Homologación contable.

**Disponibilidad:**  
Completa en el dataset armonizado.

**Variables derivadas:**

- `LOG_CAPITAL`
- `CAPITAL_ACTIVOS`

---

## 6.9 UTILIDAD_NETA

**Nombre técnico:** `UTILIDAD_NETA`

**Descripción:**  
Resultado neto del período correspondiente a la empresa.

**Tipo:**  
Numérica continua.

**Fuente:**  
Estados financieros SCVS.

**Transformación:**  
Homologación contable.

**Disponibilidad:**  
Completa en el dataset armonizado.

**Variables derivadas:**

- `LOG_UTILIDAD_NETA`
- `ROA`

**Consideración:**  
Puede presentar valores negativos cuando la empresa registra pérdida.

---

# 7. Variables monetarias transformadas

Las variables financieras de magnitud monetaria utilizan una transformación logarítmica con signo.

Transformación:

`sign(x) × log(1 + |x|)`

Esta transformación permite:

- reducir diferencias extremas de escala;
- conservar valores negativos;
- conservar el cero;
- mantener información sobre la dirección del valor.

---

## 7.1 LOG_ACTIVO_TOTAL

**Origen:**  
`ACTIVO_TOTAL`

**Tipo:**  
Numérica continua.

**Transformación:**  
Logaritmo con signo.

**Uso en Baseline v1:**  
Sí.

**Valores faltantes:**  
No esperados a partir de la variable base armonizada.

---

## 7.2 LOG_ACTIVO_CORRIENTE

**Origen:**  
`ACTIVO_CORRIENTE`

**Tipo:**  
Numérica continua.

**Transformación:**  
Logaritmo con signo.

**Uso en Baseline v1:**  
Sí.

---

## 7.3 LOG_EFECTIVO

**Origen:**  
`EFECTIVO`

**Tipo:**  
Numérica continua.

**Transformación:**  
Logaritmo con signo.

**Uso en Baseline v1:**  
Sí.

---

## 7.4 LOG_PASIVO_TOTAL

**Origen:**  
`PASIVO_TOTAL`

**Tipo:**  
Numérica continua.

**Transformación:**  
Logaritmo con signo.

**Uso en Baseline v1:**  
Sí.

---

## 7.5 LOG_PASIVO_CORRIENTE

**Origen:**  
`PASIVO_CORRIENTE`

**Tipo:**  
Numérica continua.

**Transformación:**  
Logaritmo con signo.

**Uso en Baseline v1:**  
Sí.

---

## 7.6 LOG_PASIVO_NO_CORRIENTE

**Origen:**  
`PASIVO_NO_CORRIENTE`

**Tipo:**  
Numérica continua.

**Transformación:**  
Logaritmo con signo.

**Uso en Baseline v1:**  
Sí.

---

## 7.7 LOG_PATRIMONIO

**Origen:**  
`PATRIMONIO`

**Tipo:**  
Numérica continua.

**Transformación:**  
Logaritmo con signo.

**Uso en Baseline v1:**  
Sí.

---

## 7.8 LOG_CAPITAL

**Origen:**  
`CAPITAL`

**Tipo:**  
Numérica continua.

**Transformación:**  
Logaritmo con signo.

**Uso en Baseline v1:**  
Sí.

---

## 7.9 LOG_UTILIDAD_NETA

**Origen:**  
`UTILIDAD_NETA`

**Tipo:**  
Numérica continua.

**Transformación:**  
Logaritmo con signo.

**Uso en Baseline v1:**  
Sí.

**Consideración:**  
La transformación preserva el signo de pérdidas y utilidades.

---

# 8. Razones financieras

## 8.1 LIQUIDEZ_CORRIENTE

**Nombre técnico:**  
`LIQUIDEZ_CORRIENTE`

**Descripción:**  
Relación entre activo corriente y pasivo corriente.

**Fórmula:**

`ACTIVO_CORRIENTE / PASIVO_CORRIENTE`

**Tipo:**  
Numérica continua.

**Unidad:**  
Razón.

**Disponibilidad aproximada:**  
68,04 %.

**Valores faltantes:**  
Se producen principalmente cuando el denominador no permite calcular una razón válida.

**Tratamiento en modelo:**  
Imputación mediante mediana calculada exclusivamente en TRAIN.

**Uso en Baseline v1:**  
Sí.

---

## 8.2 ENDEUDAMIENTO

**Nombre técnico:**  
`ENDEUDAMIENTO`

**Descripción:**  
Proporción de activos financiada mediante pasivos.

**Fórmula:**

`PASIVO_TOTAL / ACTIVO_TOTAL`

**Tipo:**  
Numérica continua.

**Unidad:**  
Proporción.

**Disponibilidad aproximada:**  
95,81 %.

**Tratamiento de faltantes:**  
Imputación mediante mediana de TRAIN.

**Uso en Baseline v1:**  
Sí.

---

## 8.3 AUTONOMIA_FINANCIERA

**Nombre técnico:**  
`AUTONOMIA_FINANCIERA`

**Descripción:**  
Proporción del activo financiada mediante patrimonio.

**Fórmula:**

`PATRIMONIO / ACTIVO_TOTAL`

**Tipo:**  
Numérica continua.

**Unidad:**  
Proporción.

**Disponibilidad aproximada:**  
95,81 %.

**Tratamiento de faltantes:**  
Mediana de TRAIN.

**Uso en Baseline v1:**  
Sí.

---

## 8.4 ROA

**Nombre técnico:**  
`ROA`

**Descripción:**  
Relación entre utilidad neta y activos.

**Fórmula:**

`UTILIDAD_NETA / ACTIVO_TOTAL`

**Tipo:**  
Numérica continua.

**Unidad:**  
Proporción.

**Disponibilidad aproximada:**  
95,81 %.

**Tratamiento de faltantes:**  
Mediana de TRAIN.

**Uso en Baseline v1:**  
Sí.

**Consideración:**  
Puede tomar valores negativos cuando existe pérdida neta.

---

## 8.5 EFECTIVO_ACTIVOS

**Nombre técnico:**  
`EFECTIVO_ACTIVOS`

**Descripción:**  
Participación del efectivo dentro del total de activos.

**Fórmula:**

`EFECTIVO / ACTIVO_TOTAL`

**Tipo:**  
Numérica continua.

**Disponibilidad aproximada:**  
95,81 %.

**Tratamiento de faltantes:**  
Mediana de TRAIN.

**Uso en Baseline v1:**  
Sí.

---

## 8.6 CAPITAL_ACTIVOS

**Nombre técnico:**  
`CAPITAL_ACTIVOS`

**Descripción:**  
Relación entre capital y activos totales.

**Fórmula:**

`CAPITAL / ACTIVO_TOTAL`

**Tipo:**  
Numérica continua.

**Disponibilidad aproximada:**  
95,81 %.

**Tratamiento de faltantes:**  
Mediana de TRAIN.

**Uso en Baseline v1:**  
Sí.

---

## 8.7 PASIVO_CORRIENTE_PASIVO

**Nombre técnico:**  
`PASIVO_CORRIENTE_PASIVO`

**Descripción:**  
Participación de las obligaciones corrientes dentro del pasivo total.

**Fórmula:**

`PASIVO_CORRIENTE / PASIVO_TOTAL`

**Tipo:**  
Numérica continua.

**Disponibilidad aproximada:**  
71,03 %.

**Tratamiento de faltantes:**  
Mediana de TRAIN.

**Uso en Baseline v1:**  
Sí.

---

# 9. Variable sectorial

## 9.1 SECTOR_CIIU

**Nombre técnico:**  
`SECTOR_CIIU`

**Descripción:**  
Sección principal de la actividad económica de la empresa según clasificación CIIU.

**Origen:**  
Información empresarial SCVS.

**Tipo:**  
Categórica.

**Construcción:**  
Se utiliza la primera sección de la clasificación CIIU.

**Disponibilidad aproximada:**  
99,98 %.

**Tratamiento de faltantes:**  
Imputación mediante la categoría más frecuente calculada en TRAIN.

**Transformación en Baseline v1:**  
One-Hot Encoding.

**Configuración:**  
`handle_unknown="ignore"`

**Uso en Baseline v1:**  
Sí.

**Uso en Baseline v2:**  
No.

**Consideración metodológica:**  
El análisis mostró diferencias importantes en la cantidad de eventos positivos entre sectores.

Por esta razón se evaluó un Baseline v2 eliminando completamente `SECTOR_CIIU`.

El Baseline v2 no mejoró las métricas prioritarias y se mantuvo la variable sectorial dentro del Baseline v1.

---

# 10. Variable objetivo

## 10.1 TARGET_24M

**Nombre técnico:**  
`TARGET_24M`

**Descripción:**  
Indica si una empresa elegible se registra por primera vez como emisor dentro de los siguientes 24 meses.

**Tipo:**  
Binaria.

**Valores:**

- `0`
- `1`

**Fuente:**  
Construida a partir del Registro del Mercado de Valores de la SCVS.

**Evento utilizado:**  
Primera inscripción como emisor.

**Uso en modelado:**  
Variable objetivo.

**Uso como predictor:**  
No.

---

## 11. Regla temporal de TARGET_24M

Para una empresa y año `t`, se considera positiva cuando:

1. la empresa todavía no era emisora al 31 de diciembre de `t`; y
2. su primera inscripción ocurre después de esa fecha y hasta el 31 de diciembre de `t + 2`.

Las empresas que ya eran emisoras son excluidas del universo prospectable.

---

## 12. Distribución de TARGET_24M

Dataset etiquetado:

| Indicador | Valor |
|---|---:|
| Observaciones | 884.072 |
| Positivos | 440 |
| Negativos | 883.632 |
| Prevalencia | 0,0498 % |

La variable objetivo presenta un desbalance extremo.

---

## 13. Distribución anual de positivos

| Año | Positivos |
|---|---:|
| 2015 | 39 |
| 2016 | 58 |
| 2017 | 93 |
| 2018 | 78 |
| 2019 | 39 |
| 2020 | 33 |
| 2021 | 42 |
| 2022 | 36 |
| 2023 | 22 |
| **Total** | **440** |

La frecuencia de nuevos emisores cambia a lo largo del período.

---

# 14. Resumen de variables utilizadas por Baseline v1

El Baseline v1 utiliza 17 variables predictoras.

### Numéricas

1. `LOG_ACTIVO_TOTAL`
2. `LOG_ACTIVO_CORRIENTE`
3. `LOG_EFECTIVO`
4. `LOG_PASIVO_TOTAL`
5. `LOG_PASIVO_CORRIENTE`
6. `LOG_PASIVO_NO_CORRIENTE`
7. `LOG_PATRIMONIO`
8. `LOG_CAPITAL`
9. `LOG_UTILIDAD_NETA`
10. `LIQUIDEZ_CORRIENTE`
11. `ENDEUDAMIENTO`
12. `AUTONOMIA_FINANCIERA`
13. `ROA`
14. `EFECTIVO_ACTIVOS`
15. `CAPITAL_ACTIVOS`
16. `PASIVO_CORRIENTE_PASIVO`

### Categórica

17. `SECTOR_CIIU`

---

# 15. Resumen de tratamiento de faltantes

## Variables monetarias transformadas

Las variables base homologadas presentan cobertura completa dentro del dataset armonizado utilizado.

No se espera ausencia sistemática en sus transformaciones logarítmicas.

---

## Razones financieras

Los valores faltantes se mantienen cuando una razón no puede calcularse adecuadamente, principalmente por condiciones asociadas con el denominador.

No se reemplazan artificialmente durante la etapa de construcción de features.

Durante el modelado se utiliza:

`SimpleImputer(strategy="median")`

El imputador se ajusta exclusivamente con TRAIN.

---

## Variable sectorial

Para `SECTOR_CIIU` se utiliza:

`SimpleImputer(strategy="most_frequent")`

ajustado exclusivamente con TRAIN.

---

# 16. Escalamiento

Las variables numéricas utilizadas por la regresión logística son transformadas mediante:

`StandardScaler`

El escalador se ajusta exclusivamente con TRAIN.

Los parámetros calculados sobre TRAIN se aplican posteriormente a VALIDATION y TEST.

---

# 17. Variables excluidas del modelo

Las siguientes variables no forman parte del vector predictivo del Baseline v1:

- `RUC`
- `EXPEDIENTE`
- `NOMBRE`
- `ANIO`
- `PLAN_CONTABLE`
- `SPLIT`
- `TARGET_24M`
- fechas relacionadas con la inscripción como emisor.

---

# 18. Razones de exclusión

## Identificadores

`RUC`, `EXPEDIENTE` y `NOMBRE` identifican a la empresa, pero no representan características financieras que se desee generalizar.

---

## ANIO

Se utiliza para construir la separación temporal, pero no se incorpora directamente como predictor en el Baseline v1.

---

## PLAN_CONTABLE

Se conserva para trazabilidad, pero se excluye para evitar que el modelo aprenda diferencias derivadas de cambios administrativos o históricos en las estructuras de reporte.

---

## SPLIT

Es una variable metodológica utilizada exclusivamente para controlar la evaluación.

---

## TARGET_24M

Es la variable objetivo y nunca debe utilizarse como predictor.

---

## Fechas futuras

Las fechas utilizadas para determinar el evento futuro no forman parte de las variables predictoras.

---

# 19. Control de data leakage

La selección y tratamiento de variables busca evitar que el modelo acceda a información futura.

Los principales controles son:

- separación temporal;
- preprocesamiento ajustado únicamente con TRAIN;
- exclusión de información posterior al corte;
- exclusión de empresas que ya eran emisoras;
- exclusión del target como predictor;
- exclusión de fechas futuras;
- exclusión de información derivada directamente del resultado.

---

# 20. Limitación temporal pendiente

Actualmente se utiliza el año fiscal como referencia para construir las observaciones.

Existe una diferencia potencial entre:

- fecha de cierre del estado financiero;
- fecha de presentación;
- fecha de publicación;
- fecha real en que la información estuvo disponible.

Esta diferencia deberá investigarse en siguientes etapas para fortalecer el control de leakage temporal.

---

# 21. Variables planificadas

Todavía no forman parte del dataset actual, pero se encuentran priorizadas para siguientes iteraciones.

## Variables de crecimiento

Se evaluarán:

- crecimiento de activos;
- crecimiento de patrimonio;
- crecimiento de capital;
- crecimiento de utilidad;
- crecimiento de efectivo.

---

## Variables de tendencia

Se evaluarán:

- tendencia de activos;
- tendencia de patrimonio;
- tendencia de endeudamiento;
- tendencia de liquidez;
- tendencia de rentabilidad;
- crecimiento acumulado;
- estabilidad de resultados.

---

## Ventanas temporales

Podrán construirse variables correspondientes a:

- un año;
- dos años;
- tres años.

Todas deberán calcularse exclusivamente con información disponible antes de la fecha de corte.

---

# 22. Variables provenientes de nuevas fuentes

En fases posteriores podrán evaluarse variables provenientes de:

- otras fuentes de SCVS;
- información interna de BVQ;
- fuentes empresariales públicas;
- variables sectoriales;
- variables macroeconómicas.

Toda nueva variable deberá documentar:

- fuente;
- fecha de disponibilidad;
- período;
- fórmula;
- cobertura;
- riesgo de leakage;
- condiciones de uso;
- tratamiento de faltantes.

---

# 23. Resumen compacto del dataset de modelado

| Variable | Tipo | Fuente / origen | Uso |
|---|---|---|---|
| `LOG_ACTIVO_TOTAL` | Numérica | `ACTIVO_TOTAL` | Predictor |
| `LOG_ACTIVO_CORRIENTE` | Numérica | `ACTIVO_CORRIENTE` | Predictor |
| `LOG_EFECTIVO` | Numérica | `EFECTIVO` | Predictor |
| `LOG_PASIVO_TOTAL` | Numérica | `PASIVO_TOTAL` | Predictor |
| `LOG_PASIVO_CORRIENTE` | Numérica | `PASIVO_CORRIENTE` | Predictor |
| `LOG_PASIVO_NO_CORRIENTE` | Numérica | `PASIVO_NO_CORRIENTE` | Predictor |
| `LOG_PATRIMONIO` | Numérica | `PATRIMONIO` | Predictor |
| `LOG_CAPITAL` | Numérica | `CAPITAL` | Predictor |
| `LOG_UTILIDAD_NETA` | Numérica | `UTILIDAD_NETA` | Predictor |
| `LIQUIDEZ_CORRIENTE` | Numérica | Razón financiera | Predictor |
| `ENDEUDAMIENTO` | Numérica | Razón financiera | Predictor |
| `AUTONOMIA_FINANCIERA` | Numérica | Razón financiera | Predictor |
| `ROA` | Numérica | Razón financiera | Predictor |
| `EFECTIVO_ACTIVOS` | Numérica | Razón financiera | Predictor |
| `CAPITAL_ACTIVOS` | Numérica | Razón financiera | Predictor |
| `PASIVO_CORRIENTE_PASIVO` | Numérica | Razón financiera | Predictor |
| `SECTOR_CIIU` | Categórica | SCVS / CIIU | Predictor |
| `TARGET_24M` | Binaria | Registro Mercado de Valores | Target |

---

# 24. Disponibilidad resumida

| Variable | Disponibilidad aproximada |
|---|---:|
| Variables financieras base homologadas | 100 % |
| Variables logarítmicas | 100 % |
| `LIQUIDEZ_CORRIENTE` | 68,04 % |
| `ENDEUDAMIENTO` | 95,81 % |
| `AUTONOMIA_FINANCIERA` | 95,81 % |
| `ROA` | 95,81 % |
| `EFECTIVO_ACTIVOS` | 95,81 % |
| `CAPITAL_ACTIVOS` | 95,81 % |
| `PASIVO_CORRIENTE_PASIVO` | 71,03 % |
| `SECTOR_CIIU` | 99,98 % |
| `TARGET_24M` | 100 % en dataset etiquetado |

---

# 25. Archivos relacionados

Dataset armonizado:

`data/interim/scvs_financials_harmonized_2015_2023.csv.gz`

Dataset etiquetado:

`data/processed/mvp_labeled_2015_2023.csv.gz`

Dataset de features:

`data/processed/mvp_features_2015_2023.csv.gz`

Configuración de homologación:

`config/scvs_account_mapping.csv`

Construcción del dataset armonizado:

`src/data/build_scvs_harmonized_dataset.py`

Construcción del dataset etiquetado:

`src/data/build_mvp_labeled_dataset.py`

Ingeniería de variables:

`src/features/build_mvp_features.py`

---

# 26. Mantenimiento del diccionario

Este documento deberá actualizarse cuando:

- se incorpore una nueva variable;
- se elimine una variable;
- cambie una fórmula;
- cambie una fuente;
- cambie el tratamiento de faltantes;
- cambie la disponibilidad;
- se incorporen variables temporales;
- se agreguen nuevas fuentes;
- se modifique la definición del target.

Cada cambio relevante deberá quedar registrado también en la bitácora del proyecto.

---

# 27. Estado actual

El diccionario documenta las variables utilizadas por el MVP y el Baseline v1.

Actualmente se dispone de:

- nueve variables financieras base homologadas;
- nueve transformaciones logarítmicas;
- siete razones financieras;
- una variable sectorial;
- una variable objetivo;
- variables de identificación y trazabilidad.

Las siguientes iteraciones ampliarán este conjunto principalmente con variables temporales y de crecimiento.