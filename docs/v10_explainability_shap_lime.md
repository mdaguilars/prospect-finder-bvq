# Prospect Finder BVQ
## Explicabilidad del modelo v10 mediante SHAP y LIME

### 1. Objetivo

El presente documento registra el análisis de explicabilidad realizado sobre el modelo final v10 de Prospect Finder BVQ y su posterior incorporación como componente operacional del prototipo.

El análisis tiene dos propósitos diferenciados:

1. comprender los factores asociados con las predicciones del modelo seleccionado;
2. proporcionar explicaciones individuales trazables dentro de la aplicación Prospect Finder BVQ.

Las técnicas evaluadas fueron:

- Permutation Importance;
- SHAP;
- LIME.

El análisis metodológico original se realizó después del cierre de la evaluación final de v10.

Por tanto, ninguna de estas técnicas fue utilizada para modificar:

- las variables;
- la definición del target;
- los hiperparámetros;
- la configuración del modelo;
- la selección del modelo final;
- los resultados obtenidos sobre TEST.

El modelo permanece congelado como:

`v10_hgb_financial_c3`

Configuración:

`C3_CONSERVATIVE`

La incorporación posterior de SHAP a la API tampoco modifica el modelo.

---

## 2. Modelo analizado

El modelo final corresponde a:

`HistGradientBoostingClassifier`

Su finalidad es generar un score utilizado para priorizar empresas dentro del universo de potenciales emisores.

El modelo utiliza 25 variables:

- 17 numéricas;
- 7 booleanas;
- 1 categórica.

La variable categórica es:

`tipo_compania`

La variable objetivo utilizada durante entrenamiento y evaluación es:

`TARGET_24M`

El score generado por el modelo debe interpretarse como:

**indicador relativo de priorización**

y no como:

**probabilidad calibrada de convertirse en emisor**.

En el producto este resultado podrá presentarse comercialmente como:

**Índice de Afinidad Bursátil**.

---

## 3. Control de integridad

Antes de ejecutar SHAP y LIME se reprodujeron las métricas oficiales del conjunto TEST.

Resultados:

| Métrica | Resultado |
|---|---:|
| Observaciones TEST | 260.445 |
| Positivos TEST | 54 |
| PR-AUC | 0.007468801 |
| ROC-AUC | 0.934603901 |

Los resultados coincidieron con la evaluación oficial de v10.

Esto confirmó que el análisis de explicabilidad se realizó utilizando:

- el mismo modelo;
- las mismas variables;
- la misma configuración;
- el mismo universo TEST.

La explicabilidad se incorporó después del cierre del modelo y no forma parte del proceso de selección de v10.

---

## 4. Preparación de datos

La preparación utilizada por SHAP y LIME replica la lógica del modelo final.

Las variables numéricas se convierten al tipo correspondiente y los valores infinitos se tratan como faltantes.

Las variables booleanas se normalizan manteniendo:

- 0;
- 1;
- valores faltantes.

La variable:

`tipo_compania`

se convierte a categoría utilizando exclusivamente las categorías observadas en TRAIN.

TEST no participa en la definición del vocabulario categórico.

La referencia inicial para las técnicas de explicabilidad se construyó utilizando información exclusivamente proveniente de TRAIN.

Esto evita utilizar información de TEST para definir el comportamiento de referencia del explicador.

---

# 5. SHAP

## 5.1 Metodología

SHAP fue seleccionado como técnica principal de explicabilidad.

La implementación utilizada es:

`PermutationExplainer`

Se trata de un enfoque model-agnostic que permite explicar el comportamiento del modelo congelado sin reemplazar ni reconstruir el estimador.

Para el análisis metodológico original se utilizaron:

- una muestra de referencia de TRAIN;
- un background SHAP de 75 observaciones;
- una muestra global de 150 observaciones de TEST;
- tres casos individuales de TEST.

El propósito de SHAP es estimar la contribución de cada variable al resultado producido por el modelo.

---

## 5.2 Importancia global SHAP

La importancia global se calculó mediante:

`mean(|SHAP|)`

Resultados:

| Rank | Variable | Mean Abs SHAP |
|---:|---|---:|
| 1 | activos_final | 0.062030 |
| 2 | bi_ingresos_ventas | 0.033458 |
| 3 | patrimonio_final_t1 | 0.016976 |
| 4 | fin_crecimiento_patrimonio | 0.014514 |
| 5 | fin_ratio_patrimonio_activos | 0.010584 |
| 6 | fin_crecimiento_activos | 0.009977 |
| 7 | patrimonio_final | 0.009283 |
| 8 | activos_final_t1 | 0.008516 |
| 9 | fin_roa | 0.008402 |
| 10 | fin_margen_neto | 0.007309 |
| 11 | tipo_compania | 0.007005 |
| 12 | bi_n_empleados | 0.006461 |
| 13 | fin_rotacion_activos | 0.004432 |
| 14 | fin_crecimiento_ventas | 0.003282 |
| 15 | fin_crecimiento_empleados | 0.002648 |
| 16 | bi_n_empleados_t1 | 0.002137 |
| 17 | bi_ingresos_ventas_t1 | 0.001751 |
| 18 | fin_roe | 0.000849 |
| 19 | TIENE_T_MENOS_1 | 0.000000 |
| 20 | flag_ventas_negativas | 0.000000 |
| 21 | flag_activos_negativos | 0.000000 |
| 22 | flag_empleados_fijo | 0.000000 |
| 23 | flag_empleados_salto_temporal | 0.000000 |
| 24 | flag_empleados_anomalia_total | 0.000000 |
| 25 | flag_patrimonio_no_positivo | 0.000000 |

---

## 5.3 Interpretación global

Las variables con mayor influencia global están relacionadas principalmente con:

- tamaño empresarial;
- volumen de actividad;
- patrimonio;
- evolución financiera;
- estructura patrimonial;
- rentabilidad.

La variable con mayor importancia fue:

`activos_final`

seguida por:

`bi_ingresos_ventas`

Esto indica que la escala empresarial tiene una influencia importante dentro del comportamiento aprendido por el modelo.

También aparecen entre las variables relevantes:

- patrimonio del período anterior;
- crecimiento de patrimonio;
- relación patrimonio / activos;
- crecimiento de activos;
- patrimonio actual;
- activos del período anterior;
- ROA;
- margen neto.

`tipo_compania`

aparece en la posición 11.

Por tanto, participa en el comportamiento del modelo, pero no constituye una de sus variables de mayor importancia global.

Las variables booleanas presentaron importancia SHAP igual a cero dentro de la muestra utilizada para el análisis global.

Esto no significa necesariamente que nunca intervengan en una predicción individual.

---

## 5.4 Limitación de la importancia global

`mean(|SHAP|)`

representa la magnitud promedio de las contribuciones.

No indica directamente si una variable aumenta o reduce el score.

Para analizar dirección es necesario utilizar explicaciones individuales.

La importancia global tampoco demuestra causalidad.

---

# 6. Explicaciones locales SHAP

Durante el análisis metodológico se seleccionaron tres casos completos de TEST.

| Caso | Año | TARGET_24M | Score v10 |
|---|---:|---:|---:|
| Mayor score completo de TEST | 2022 | 0 | 0.975080 |
| Mejor positivo completo de TEST | 2022 | 1 | 0.967644 |
| Caso con score cercano a la mediana | 2023 | 0 | 0.126871 |

La selección se realizó después del cierre del modelo y exclusivamente con fines explicativos.

---

## 6.1 Fidelidad local

En los tres casos analizados, SHAP reconstruyó el score original.

| Caso | Score modelo | Score reconstruido SHAP | Error |
|---|---:|---:|---:|
| Mayor score completo TEST | 0.975080072 | 0.975080072 | 0.0000000000 |
| Mejor positivo completo TEST | 0.967644384 | 0.967644384 | 0.0000000000 |
| Score mediano completo TEST | 0.126870629 | 0.126870629 | 0.0000000000 |

Esto proporciona evidencia de fidelidad local para la metodología utilizada.

---

# 7. Caso local: mejor positivo real

El mejor positivo real analizado presentó:

`TARGET_24M = 1`

Score:

`0.967644`

Principales contribuciones positivas:

| Variable | Valor | Contribución SHAP |
|---|---:|---:|
| activos_final | 11.590.309,16 | +0.255956 |
| patrimonio_final_t1 | 2.201.209,60 | +0.125590 |
| patrimonio_final | 2.678.111,87 | +0.111640 |
| bi_ingresos_ventas | 10.626.826,73 | +0.072366 |
| fin_ratio_patrimonio_activos | 0.231065 | +0.047199 |
| bi_n_empleados | 80 | +0.038565 |
| fin_roa | 0.041540 | +0.037248 |
| bi_ingresos_ventas_t1 | 8.949.293,41 | +0.020220 |
| fin_margen_neto | 0.045306 | +0.016933 |
| fin_crecimiento_patrimonio | 0.216655 | +0.015696 |

La explicación combina principalmente:

- escala empresarial;
- patrimonio;
- ventas;
- estructura patrimonial;
- rentabilidad;
- crecimiento.

Este perfil fue considerado altamente prioritario por el modelo.

---

# 8. Caso local: mayor score de TEST

El caso con mayor score completo obtuvo:

`0.975080`

pero presentó:

`TARGET_24M = 0`

Principales contribuciones:

| Variable | Valor | Contribución SHAP |
|---|---:|---:|
| activos_final | 65.742.359,13 | +0.328269 |
| patrimonio_final | 17.478.361,28 | +0.124248 |
| bi_ingresos_ventas | 46.354.051,54 | +0.089486 |
| patrimonio_final_t1 | 14.563.703,70 | +0.066427 |
| bi_n_empleados | 349 | +0.045481 |
| fin_roa | 0.044687 | +0.039539 |
| fin_margen_neto | 0.063378 | +0.018794 |
| bi_ingresos_ventas_t1 | 24.050.564,70 | +0.016458 |
| fin_ratio_patrimonio_activos | 0.265861 | +0.012739 |
| fin_crecimiento_patrimonio | 0.200132 | +0.012606 |

La empresa presentaba varias características asociadas con scores elevados.

Sin embargo, no se convirtió en emisor dentro del horizonte utilizado por `TARGET_24M`.

Este caso demuestra un principio fundamental:

**un score elevado no implica que una empresa necesariamente vaya a convertirse en emisor.**

Existen factores:

- empresariales;
- estratégicos;
- comerciales;
- regulatorios;
- financieros;

que no necesariamente están representados por las variables del modelo.

---

# 9. Caso local: score mediano

El caso seleccionado con score cercano a la mediana obtuvo:

`0.126871`

Principales contribuciones:

| Variable | Valor | Contribución SHAP |
|---|---:|---:|
| activos_final | 127.243,44 | -0.040956 |
| bi_ingresos_ventas | 180.822,14 | -0.032432 |
| fin_crecimiento_patrimonio | 0.028265 | +0.023033 |
| tipo_compania | RESPONSABILIDAD LIMITADA | -0.018442 |
| fin_ratio_patrimonio_activos | 0.357974 | +0.015359 |
| fin_margen_neto | 0.051039 | +0.012016 |
| fin_crecimiento_activos | -0.008454 | -0.011666 |
| activos_final_t1 | 128.328,28 | -0.009801 |
| patrimonio_final_t1 | 44.297,75 | +0.005231 |
| bi_n_empleados | 9 | +0.004255 |

El caso demuestra que el modelo combina simultáneamente señales positivas y negativas.

La contribución observada para:

`tipo_compania = RESPONSABILIDAD LIMITADA`

corresponde únicamente a esa predicción.

No puede generalizarse como una penalización automática para todas las empresas de esa categoría.

---

# 10. LIME

## 10.1 Propósito

LIME se utilizó como técnica complementaria de explicabilidad local.

Su objetivo fue contrastar las explicaciones obtenidas mediante SHAP y analizar la capacidad de un modelo sustituto local para aproximar el comportamiento del modelo original.

LIME genera observaciones artificiales alrededor del caso analizado y ajusta un modelo simplificado local.

Por esta razón representa una aproximación y no una reconstrucción exacta.

---

## 10.2 Resultados

Mayor score:

| Resultado | Valor |
|---|---:|
| Score v10 | 0.975080 |
| Aproximación LIME | 0.859736 |

Mejor positivo:

| Resultado | Valor |
|---|---:|
| Score v10 | 0.967644 |
| Aproximación LIME | 0.851937 |

Caso mediano:

| Resultado | Valor |
|---|---:|
| Score v10 | 0.126871 |
| Aproximación LIME | 0.051120 |

LIME no reprodujo exactamente las predicciones del modelo.

Esto es consistente con su naturaleza de aproximación local.

---

## 10.3 Factores observados con LIME

En casos de score elevado LIME identificó como relevantes:

- activos;
- patrimonio anterior;
- ventas;
- crecimiento de activos;
- patrimonio;
- empleados;
- crecimiento patrimonial.

Existen coincidencias conceptuales con SHAP.

Sin embargo, también se observaron diferencias de dirección para determinadas variables.

Por esta razón LIME se mantiene como técnica complementaria y no como explicación operacional principal.

---

# 11. Comparación SHAP vs. LIME

| Criterio | SHAP | LIME |
|---|---|---|
| Explicación global | Sí | No es su uso principal |
| Explicación local | Sí | Sí |
| Reconstrucción observada del score | Exacta | Aproximada |
| Dirección de contribuciones | Sí | Sí |
| Modelo sustituto local | No | Sí |
| Fidelidad observada | Mayor | Menor |
| Uso en producto | Principal | No |
| Uso académico | Sí | Sí |

---

# 12. Técnica seleccionada

Se selecciona:

**SHAP como técnica principal de explicabilidad de Prospect Finder BVQ.**

Las razones son:

1. permite análisis global;
2. permite análisis individual;
3. presentó alta fidelidad;
4. permite identificar dirección de contribuciones;
5. permite mantener trazabilidad hacia el score;
6. puede convertirse a lenguaje comprensible para usuarios de negocio.

LIME permanece como:

**técnica complementaria de contraste académico.**

---

# 13. Relación con Permutation Importance

Permutation Importance y SHAP responden preguntas diferentes.

Permutation Importance permite analizar principalmente:

> ¿Cuánto cambia el desempeño cuando se altera una variable?

SHAP permite analizar:

> ¿Cómo contribuyen las variables al score generado por el modelo?

Los rankings de variables no necesitan coincidir.

Las diferencias entre ambas técnicas no constituyen necesariamente una contradicción.

---

# 14. Incorporación de SHAP al producto

Después de completar el análisis metodológico, SHAP fue incorporado al backend de Prospect Finder BVQ.

La implementación operacional se encuentra en:

`src/api/services/explainability.py`

La API expone dos servicios de explicabilidad.

### Explicabilidad global

`GET /api/explainability/global`

### Explicabilidad individual

`GET /api/explainability/prospects/{expediente_key}`

La primera utiliza los resultados globales previamente validados.

La segunda genera una explicación SHAP bajo demanda para la empresa seleccionada.

---

# 15. Explicabilidad global en API

El endpoint global consulta la evidencia previamente calculada y almacenada durante la fase metodológica.

Esto evita recalcular SHAP global cada vez que un usuario consulta la aplicación.

La API puede limitar el número de variables devueltas mediante:

`limit`

Por ejemplo:

`GET /api/explainability/global?limit=10`

El servicio mantiene como fuente la evidencia post-test ya validada.

---

# 16. Explicabilidad individual en API

La explicación individual se genera sobre el universo operacional.

El endpoint es:

`GET /api/explainability/prospects/{expediente_key}`

y admite:

`top_n`

para limitar el número de factores principales.

El servicio:

1. localiza la empresa;
2. recupera sus 25 variables;
3. aplica exactamente la estructura esperada por el modelo;
4. reproduce el score;
5. genera contribuciones SHAP;
6. reconstruye el score a partir de `base_value + SHAP`;
7. verifica la diferencia;
8. devuelve los principales factores.

---

# 17. Fuente de datos operacional

La implementación operacional utiliza:

`data/processed/v10_features_financial_2012_2023.csv.gz`

El servicio selecciona la observación correspondiente a la empresa y año operacional.

La estructura utiliza exactamente las mismas 25 variables registradas en el artefacto del modelo.

No se agregan nuevas variables a la explicación.

No se elimina ninguna variable del modelo para generar SHAP.

---

# 18. Categorías

La variable:

`tipo_compania`

mantiene las categorías provenientes de TRAIN.

La explicación operacional no aprende categorías utilizando información posterior.

Esto mantiene consistencia con el procedimiento utilizado durante entrenamiento y evaluación.

---

# 19. Background operacional

El `PermutationExplainer` utiliza un background de:

`75 observaciones`

provenientes exclusivamente de TRAIN.

El background no se obtiene del ranking operacional.

Tampoco utiliza TEST para definir la referencia.

Esta decisión mantiene el mismo principio metodológico utilizado en el análisis original.

---

# 20. Evaluaciones del explicador

Para las explicaciones locales se utiliza el número mínimo requerido de evaluaciones para la permutación completa de las 25 variables:

`max_evals = 51`

equivalente a:

`2 × número_de_variables + 1`

para las 25 características utilizadas.

---

# 21. Validación del score operacional

Antes de calcular la explicación se verifica que el modelo congelado reproduzca el score almacenado en el ranking operacional.

En una validación funcional se obtuvo:

`score modelo = 0.9736944399096825`

y:

`score ranking = 0.9736944399096824`

Diferencia:

`1.11 × 10^-16`

La diferencia corresponde únicamente a precisión numérica.

Esto confirma que la explicación se genera sobre la misma predicción presentada en el producto.

---

# 22. Reconstrucción operacional SHAP

Para la misma validación funcional se obtuvo:

`base_value = 0.1783474992099843`

Score reconstruido mediante SHAP:

`0.9736944399096834`

Score del modelo:

`0.9736944399096825`

Error:

`8.88 × 10^-16`

La diferencia es únicamente numérica.

Por tanto:

`base_value + suma(SHAP) ≈ score del modelo`

queda validado también para el servicio operacional.

---

# 23. Reproducibilidad de las contribuciones

`PermutationExplainer` utiliza un procedimiento basado en permutaciones.

Por esta razón, las contribuciones individuales pueden presentar pequeñas variaciones entre ejecuciones en la distribución exacta de aporte entre variables.

Esto significa que:

- el orden de factores cercanos puede cambiar ligeramente;
- determinados valores SHAP pueden variar en pequeña magnitud.

Sin embargo, las validaciones realizadas mantienen la reconstrucción del score dentro de tolerancias numéricas.

Para el usuario, la interpretación debe centrarse en:

- dirección;
- magnitud relativa;
- principales factores.

---

# 24. Evaluación de TreeExplainer

Durante la optimización operacional se evaluó:

`TreeExplainer`

debido a que potencialmente ofrece menor tiempo de cálculo para modelos basados en árboles.

En una prueba técnica presentó un tiempo aproximado de:

`0,046 segundos`

para la explicación analizada.

Sin embargo, no reprodujo correctamente el score original del modelo cuando fue necesario representar numéricamente la variable categórica utilizada nativamente por `HistGradientBoostingClassifier`.

Resultados de la prueba:

Score del modelo:

`0.973694`

Reconstrucción obtenida mediante TreeExplainer:

`0.476484`

Diferencia aproximada:

`0.49721`

Esta diferencia es metodológicamente inaceptable para el objetivo del producto.

Por esta razón:

**TreeExplainer fue descartado.**

La reducción de tiempo de ejecución no justifica utilizar una explicación que no sea fiel a la predicción real.

---

# 25. Decisión operacional

Prospect Finder BVQ mantiene:

`PermutationExplainer`

como método de explicabilidad individual.

La decisión se tomó priorizando:

- fidelidad;
- trazabilidad;
- consistencia con el modelo;
- reconstrucción del score.

El rendimiento se optimizó mediante inicialización anticipada del runtime y no mediante sustitución por un explicador menos fiel.

---

# 26. Rendimiento inicial

Durante las primeras pruebas, la primera ejecución de SHAP podía requerir aproximadamente:

`70 segundos`

debido principalmente al proceso de inicialización del entorno y del explicador.

Las siguientes explicaciones dentro del mismo proceso eran significativamente más rápidas.

Esto permitió identificar que el problema principal correspondía a:

**cold start**

y no al cálculo individual una vez inicializado el runtime.

---

# 27. Pruebas de reducción del background

Se evaluó reducir el tamaño del background para determinar si esto eliminaba el costo inicial.

Incluso utilizando backgrounds muy pequeños, el primer cálculo continuó requiriendo varios segundos.

Por tanto, reducir el background no resolvió adecuadamente el problema de inicialización.

Además, una reducción extrema podía afectar la calidad de la referencia utilizada por SHAP.

Se mantuvo el background validado de:

`75 observaciones`.

---

# 28. Precalentamiento de SHAP

La solución implementada consiste en inicializar el runtime durante el arranque de FastAPI.

Durante el `lifespan` de la aplicación:

1. se carga el modelo;
2. se prepara la referencia;
3. se inicializa el explicador;
4. se ejecuta una explicación operacional de precalentamiento.

FastAPI no se considera completamente listo hasta terminar este proceso.

De esta manera, el costo inicial se traslada al arranque de la aplicación y no a la primera consulta del especialista.

---

# 29. Rendimiento después del precalentamiento

Después de completar el precalentamiento se verificaron tiempos como:

`≈ 0,25 segundos`

para una primera consulta posterior al inicio.

También se observaron consultas adicionales del orden de:

`≈ 0,20 – 1,5 segundos`

dependiendo del estado del runtime y del caso procesado.

Estos valores corresponden al entorno local de desarrollo.

No constituyen un SLA de producción.

El rendimiento deberá volver a medirse en el ambiente definitivo de despliegue.

---

# 30. Manejo de errores

El servicio operacional debe rechazar o advertir situaciones como:

- empresa inexistente;
- empresa sin observación operacional compatible;
- features incompletas;
- diferencia significativa entre score almacenado y score del modelo;
- error excesivo de reconstrucción SHAP.

La prioridad es evitar presentar al usuario una explicación que no corresponda al score real.

---

# 31. Relación con PostgreSQL

PostgreSQL almacena:

- ranking;
- score;
- identificación;
- indicadores;
- comparables.

Las explicaciones SHAP individuales no necesitan persistirse actualmente en la base.

Se calculan bajo demanda utilizando:

- modelo congelado;
- features;
- background de TRAIN.

Esto evita almacenar explicaciones potencialmente desactualizadas si posteriormente cambia la capa de presentación.

---

# 32. Presentación en frontend

La interfaz deberá traducir las contribuciones técnicas a lenguaje orientado al usuario.

Puede utilizar una sección denominada:

**Factores que influyen en la afinidad**

dividida en:

**Factores que aumentan la afinidad**

y:

**Factores que reducen la afinidad**

La interfaz no debe generar explicaciones genéricas.

Cada mensaje deberá derivarse de las contribuciones SHAP reales de la empresa consultada.

---

# 33. Información que podrá mostrar la interfaz

Para cada factor se podrá presentar:

| Campo técnico | Presentación de negocio |
|---|---|
| feature | Indicador financiero |
| feature_value | Valor observado |
| shap_value positivo | Aumenta afinidad |
| shap_value negativo | Reduce afinidad |
| abs_shap | Relevancia relativa |
| ranking local | Orden visual |

El valor técnico SHAP puede mantenerse disponible para auditoría sin necesidad de ocupar el primer nivel visual de la interfaz.

---

# 34. Ejemplo de traducción

Un resultado técnico como:

`activos_final → SHAP positivo`

puede presentarse como:

> El nivel de activos de la empresa aumenta su afinidad dentro del modelo.

Un resultado:

`fin_crecimiento_activos → SHAP negativo`

puede presentarse como:

> La evolución de los activos reduce parcialmente la afinidad calculada.

Estas expresiones describen comportamiento del modelo.

No deben presentarse como relaciones causales.

---

# 35. Explicabilidad global en interfaz

El producto podrá disponer de una sección:

**¿Qué considera principalmente el modelo?**

Esta sección podrá utilizar la importancia global SHAP para mostrar que el modelo considera principalmente dimensiones relacionadas con:

- escala;
- ventas;
- patrimonio;
- crecimiento;
- estructura patrimonial;
- rentabilidad.

Esta información representa el comportamiento global.

No sustituye la explicación particular de una empresa.

---

# 36. Uso responsable

SHAP y LIME explican:

**cómo se comporta el modelo**

No explican:

**por qué una empresa realmente se convierte o no en emisor**.

No debe afirmarse:

> La empresa se convertirá en emisor porque estas variables tienen SHAP positivo.

Una formulación adecuada es:

> Estas características contribuyeron positivamente al Índice de Afinidad Bursátil asignado por el modelo.

La decisión de realizar una gestión comercial corresponde al especialista.

---

# 37. Supervisión humana

La explicabilidad forma parte del flujo:

`Modelo → Score → SHAP → Especialista → Análisis`

No reemplaza el criterio humano.

El especialista puede considerar información que no se encuentra en el modelo, como:

- estrategia empresarial;
- necesidades de financiamiento;
- estructura accionaria;
- condiciones de mercado;
- disposición de los administradores;
- proyectos de inversión;
- factores regulatorios;
- contexto sectorial.

---

# 38. Relación con sesgos

SHAP permite observar qué variables contribuyen al score.

Sin embargo, por sí solo no constituye una evaluación completa de equidad.

Los análisis de:

- sesgo;
- concentración;
- estabilidad;
- distribución;

se encuentran documentados separadamente.

La provincia no forma parte del modelo v10.

---

# 39. Pruebas de API

La explicabilidad forma parte de la suite automática de FastAPI.

Las pruebas incluyen:

- disponibilidad del endpoint global;
- respuesta de explicabilidad local;
- manejo de empresa inexistente.

La suite completa de API registra:

`12 pruebas aprobadas`

La explicación SHAP real no se recalcula durante cada ejecución automática de toda la suite debido a su costo computacional.

El endpoint local utiliza aislamiento mediante `monkeypatch` en la prueba correspondiente.

La fidelidad real de SHAP se valida mediante pruebas funcionales independientes.

---

# 40. Separación entre pruebas técnicas y evidencia metodológica

Las pruebas automáticas verifican:

- contratos;
- respuestas;
- integración;
- errores.

La validación metodológica verifica:

- reproducción del score;
- fidelidad SHAP;
- referencia de TRAIN;
- consistencia de variables.

Ambos tipos de prueba son necesarios y responden a objetivos distintos.

---

# 41. Evidencias del análisis metodológico

El análisis original se encuentra implementado en:

`src/analysis/analyze_v10_shap_lime.py`

Los resultados se almacenan en:

`reports/results/v10/explainability/shap_lime/`

Entre los archivos generados se encuentran:

`v10_shap_global_importance.csv`

`v10_shap_local_explanations.csv`

`v10_shap_global_importance.png`

`v10_lime_local_explanations.csv`

`v10_explainability_local_cases.csv`

`v10_shap_lime_metadata.json`

También se generan archivos HTML correspondientes a explicaciones LIME.

---

# 42. Evidencia operacional

La implementación utilizada por la API se encuentra en:

`src/api/services/explainability.py`

Los endpoints se encuentran integrados a FastAPI mediante el router de explicabilidad.

Esta implementación utiliza:

- artefacto v10 congelado;
- lista exacta de 25 features;
- categorías de TRAIN;
- background de TRAIN;
- `PermutationExplainer`;
- validación del score;
- validación de reconstrucción SHAP.

---

# 43. Decisiones descartadas

Durante la construcción operacional se descartaron las siguientes alternativas:

### Recalcular SHAP global en cada consulta

No es necesario debido a que existe evidencia global previamente validada.

### Utilizar TreeExplainer únicamente por velocidad

Fue descartado porque no reprodujo correctamente el score del modelo.

### Reducir agresivamente el background

No resolvió suficientemente el costo de inicialización y podía deteriorar la referencia explicativa.

### Utilizar LIME como explicación principal

Fue descartado debido a su menor fidelidad observada.

La solución adoptada fue mantener la metodología SHAP validada y optimizar la inicialización.

---

# 44. Principales conclusiones

El análisis completo permite concluir que:

1. el modelo v10 utiliza principalmente variables relacionadas con escala, actividad, patrimonio, crecimiento y rentabilidad;
2. activos y ventas son las variables de mayor influencia global observada;
3. ninguna explicación debe interpretarse como causalidad;
4. un score elevado no garantiza que una empresa se convierta en emisor;
5. SHAP presentó mayor fidelidad que LIME;
6. LIME permanece como técnica complementaria académica;
7. `PermutationExplainer` permite reconstruir adecuadamente el score del modelo;
8. TreeExplainer fue descartado al no reproducir correctamente el score;
9. SHAP se encuentra integrado al backend del prototipo;
10. la inicialización anticipada permite disponer de tiempos adecuados para interacción;
11. la explicación individual se valida contra el score operacional;
12. el modelo permanece congelado;
13. la explicabilidad no modifica ranking ni predicciones;
14. la decisión comercial permanece bajo supervisión humana.

---

# 45. Estado actual

| Componente | Estado |
|---|---|
| Permutation Importance | Completado |
| SHAP global | Completado |
| SHAP local TEST | Completado |
| LIME | Completado |
| Comparación SHAP/LIME | Completada |
| Técnica principal | SHAP |
| Modelo v10 | Congelado |
| SHAP operacional | Implementado |
| Validación score operacional | Implementada |
| Validación reconstrucción SHAP | Implementada |
| API SHAP global | Implementada |
| API SHAP local | Implementada |
| Precalentamiento | Implementado |
| Pruebas API | Implementadas |
| Presentación frontend | Pendiente |
| Validación con especialistas | Pendiente |

---

# 46. Principio final

La explicabilidad de Prospect Finder BVQ debe mantener siempre la siguiente separación:

`Predicción ≠ explicación ≠ causalidad ≠ decisión`

El modelo genera una señal de priorización.

SHAP explica cómo las variables contribuyeron a esa señal.

El especialista interpreta la información dentro de un contexto empresarial más amplio.

La decisión final continúa siendo humana.