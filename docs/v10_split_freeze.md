# Congelamiento del split temporal v10

**Proyecto:** Prospect Finder BVQ  
**Versión:** v10  
**Estado:** CONGELADO  
**Fecha:** octubre de 2026

---

## 1. Propósito

Este documento deja formalmente definido el esquema de partición temporal utilizado para el desarrollo, validación y evaluación final de los modelos de la generación v10.

El split se construye sobre el dataset base congelado:

`data/processed/v10_base_integrated_2012_2023.csv.gz`

El dataset contiene 1.030.671 observaciones empresa-año correspondientes al período 2012-2023.

La variable objetivo es:

`TARGET_24M`

que identifica si una empresa elegible obtiene su primera inscripción efectiva como emisor dentro de los 24 meses posteriores a la fecha de decisión correspondiente.

---

## 2. Principio temporal

Para una observación del ejercicio `t`:

- ejercicio financiero: `t`;
- fecha normativa de disponibilidad: 30 de abril de `t+1`;
- fecha de decisión: 1 de mayo de `t+1`;
- ventana objetivo: desde 1 de mayo de `t+1` hasta 30 de abril de `t+3`.

El diseño del split busca evitar que las ventanas objetivo utilizadas para entrenamiento, validación y prueba final se superpongan.

---

## 3. Split congelado

| Conjunto | Ejercicios | Filas | Positivos | Prevalencia |
|---|---:|---:|---:|---:|
| TRAIN | 2012-2018 | 470.722 | 407 | 0,086463 % |
| EMBARGO_1 | 2019 | 91.934 | 34 | 0,036983 % |
| VALIDATION | 2020 | 98.471 | 34 | 0,034528 % |
| EMBARGO_2 | 2021 | 109.099 | 39 | 0,035747 % |
| TEST | 2022-2023 | 260.445 | 54 | 0,020734 % |

Total:

- 1.030.671 observaciones;
- 568 observaciones positivas.

---

## 4. Distribución anual

| Año | Split | Filas | Positivos | Prevalencia |
|---|---|---:|---:|---:|
| 2012 | TRAIN | 42.158 | 55 | 0,130462 % |
| 2013 | TRAIN | 47.140 | 49 | 0,103946 % |
| 2014 | TRAIN | 52.528 | 39 | 0,074246 % |
| 2015 | TRAIN | 76.468 | 43 | 0,056233 % |
| 2016 | TRAIN | 79.503 | 73 | 0,091820 % |
| 2017 | TRAIN | 83.107 | 89 | 0,107091 % |
| 2018 | TRAIN | 89.818 | 59 | 0,065688 % |
| 2019 | EMBARGO_1 | 91.934 | 34 | 0,036983 % |
| 2020 | VALIDATION | 98.471 | 34 | 0,034528 % |
| 2021 | EMBARGO_2 | 109.099 | 39 | 0,035747 % |
| 2022 | TEST | 123.289 | 32 | 0,025955 % |
| 2023 | TEST | 137.156 | 22 | 0,016040 % |

La reducción de prevalencia a lo largo del tiempo se considera una característica observada del problema y no se corrige mediante muestreo temporal artificial.

---

## 5. Verificación de no solapamiento

### TRAIN frente a VALIDATION

Máxima fecha de finalización de la ventana objetivo de TRAIN:

`30/04/2021`

Primera fecha de decisión de VALIDATION:

`01/05/2021`

Resultado:

`30/04/2021 < 01/05/2021`

Por tanto, no existe solapamiento entre las ventanas objetivo utilizadas para TRAIN y la fecha de decisión de VALIDATION.

### VALIDATION frente a TEST

Máxima fecha de finalización de la ventana objetivo de VALIDATION:

`30/04/2023`

Primera fecha de decisión de TEST:

`01/05/2023`

Resultado:

`30/04/2023 < 01/05/2023`

Por tanto, no existe solapamiento entre las ventanas objetivo utilizadas para VALIDATION y la fecha de decisión de TEST.

---

## 6. Función de los años de embargo

Los ejercicios 2019 y 2021 no se utilizarán para ajustar modelos ni para calcular métricas de selección.

Su función principal es separar temporalmente las ventanas objetivo de los conjuntos principales.

Sin embargo, los datos históricos observables de estos ejercicios sí pueden utilizarse para construir características retrospectivas válidas de una observación posterior, por ejemplo:

- una variable `t-1` de una observación de VALIDATION 2020 puede provenir de 2019;
- una variable `t-1` de una observación TEST 2022 puede provenir de 2021.

Esto es válido porque se utilizan únicamente datos financieros históricos disponibles antes de la correspondiente fecha de decisión.

Los valores de `TARGET_24M` de los años de embargo no se utilizarán para entrenamiento ni selección de modelos.

---

## 7. Estado del TEST

El conjunto TEST queda definido como los ejercicios:

`2022-2023`

Su horizonte temporal es:

- primera fecha de decisión: 01/05/2023;
- última fecha de decisión: 01/05/2024;
- última fecha de finalización de ventana objetivo: 30/04/2026.

Las fuentes utilizadas para construir el target fueron obtenidas posteriormente a esta última fecha, por lo que el horizonte objetivo de TEST se encuentra completo.

### Regla de cierre

TEST queda reservado exclusivamente para la evaluación final de la generación de modelos seleccionada.

Hasta ese momento no se utilizará para:

- seleccionar variables;
- determinar transformaciones;
- calcular parámetros de imputación;
- determinar límites de winsorización;
- ajustar escaladores;
- seleccionar hiperparámetros;
- comparar modelos;
- seleccionar umbrales;
- decidir configuraciones de ranking.

Las estadísticas descriptivas de estructura, tamaño de muestra, prevalencia y horizonte temporal realizadas durante la construcción del dataset no constituyen una evaluación predictiva del TEST.

No se han calculado métricas de rendimiento de modelos v10 sobre TEST.

---

## 8. Evaluación futura de TEST

Cuando se abra formalmente TEST, los resultados deberán reportarse como mínimo de tres formas:

1. ejercicio 2022;
2. ejercicio 2023;
3. conjunto agregado 2022-2023.

Esta separación es necesaria porque las ventanas objetivo de 24 meses de 2022 y 2023 se superponen temporalmente y una misma empresa puede aparecer en distintos cortes empresa-año.

Las métricas previstas incluyen:

- PR-AUC;
- ROC-AUC como métrica complementaria;
- Precision@K;
- Recall@K;
- Lift@K;
- análisis de estabilidad temporal;
- métricas de interpretabilidad y riesgo definidas para el proyecto.

---

## 9. Datos repetidos entre períodos

Una empresa puede aparecer en varios ejercicios mientras continúe siendo elegible.

Esto no se considera fuga de información, porque el problema está definido como una decisión temporal empresa-año y las características utilizadas en cada observación deben corresponder únicamente a información disponible en su fecha de decisión.

No se utilizará partición aleatoria de observaciones.

---

## 10. Regla de transformación y preprocesamiento

Todos los parámetros derivados de los datos deberán aprenderse exclusivamente en TRAIN.

Esto incluye, entre otros:

- medianas de imputación;
- escalamiento;
- transformaciones;
- límites de winsorización o clipping;
- codificación basada en frecuencias;
- cualquier parámetro aprendido utilizado por el pipeline.

VALIDATION y TEST recibirán exclusivamente transformaciones previamente ajustadas sin recalibrar los parámetros sobre esos conjuntos.

Las reglas determinísticas de calidad de fuente previamente documentadas no se consideran parámetros aprendidos del modelo.

---

## 11. Relación con versiones anteriores

Los resultados v4-v9 utilizaron un universo y período diferentes.

Por tanto:

- los resultados históricos v4-v9 continúan siendo evidencia del desarrollo metodológico;
- el antiguo split 2015-2018 / 2020 / 2022-2023 no debe confundirse con el split v10;
- cualquier modelo entrenado sobre el nuevo universo deberá identificarse explícitamente como generación v10;
- los resultados v8 continúan únicamente como benchmark histórico.

---

## 12. Regla de modificación

A partir de este documento, el split temporal v10 se considera congelado.

Cualquier modificación de:

- años asignados a TRAIN;
- años de embargo;
- año de VALIDATION;
- años de TEST;
- horizonte objetivo;
- reglas de separación temporal;

requerirá una nueva versión documentada y una justificación reproducible.

---

## 13. Estado final

**Split temporal v10: CONGELADO**

Configuración oficial:

`TRAIN 2012-2018 -> EMBARGO 2019 -> VALIDATION 2020 -> EMBARGO 2021 -> TEST 2022-2023`

TEST permanece cerrado para evaluación predictiva hasta que finalicen:

1. construcción del Feature Set v10;
2. definición del pipeline de preprocesamiento;
3. entrenamiento en TRAIN;
4. selección de configuraciones mediante VALIDATION;
5. selección final de la generación de modelo.
