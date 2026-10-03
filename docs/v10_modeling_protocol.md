# Protocolo de Modelado v10

**Proyecto:** Prospect Finder BVQ  
**Versión:** v10  
**Estado:** CONGELADO  
**Fecha:** octubre de 2026

---

## 1. Propósito

Este documento define el protocolo metodológico que se utilizará para entrenar, comparar y seleccionar los modelos de la versión v10 de Prospect Finder BVQ.

Su objetivo es evitar modificaciones retrospectivas de reglas después de observar resultados de VALIDATION o TEST.

---

## 2. Dataset de entrada

El modelado utilizará exclusivamente:

`data/processed/v10_features_core_2012_2023.csv.gz`

SHA-256 congelado:

`91de8c12e8603d6f2c354f723a7a5e36f30aa8c242edd8ec55d2d8d64f0bcd6c`

El archivo contiene:

- 1.030.671 observaciones empresa-año;
- 568 observaciones positivas;
- 10 variables predictoras conceptuales;
- split temporal congelado;
- variables administrativas y de auditoría separadas de los predictores.

---

## 3. Variable objetivo

La variable objetivo es:

`TARGET_24M`

Representa la ocurrencia de una primera inscripción efectiva como emisor dentro de los 24 meses posteriores a la fecha de decisión definida para cada ejercicio.

El objetivo operacional no es emitir una decisión automática, sino generar un score de afinidad que permita priorizar empresas para análisis humano posterior.

---

## 4. Variables predictoras v10-core

Las únicas variables predictoras del núcleo son:

### Numéricas del ejercicio t

- `activos_final`
- `patrimonio_final`
- `bi_ingresos_ventas`
- `bi_n_empleados`

### Numéricas del ejercicio t-1

- `activos_final_t1`
- `patrimonio_final_t1`
- `bi_ingresos_ventas_t1`
- `bi_n_empleados_t1`

### Categóricas

- `tipo_compania`
- `provincia`

Total:

`10 variables predictoras conceptuales`

---

## 5. Variables excluidas de X

No se utilizarán como predictores:

- `ANIO`;
- `EXPEDIENTE_KEY`;
- `RUC`;
- `NOMBRE`;
- `TARGET_24M`;
- `SPLIT`;
- `TIENE_T_MENOS_1`;
- banderas de calidad;
- variables de fuente o procedencia;
- fechas futuras;
- información asociada al estado de emisor;
- variables utilizadas para construir el target.

Estas variables podrán mantenerse únicamente para identificación, auditoría o evaluación.

---

## 6. División temporal

El split congelado es:

| Conjunto | Periodo | Filas | Positivos |
|---|---|---:|---:|
| TRAIN | 2012-2018 | 470.722 | 407 |
| EMBARGO_1 | 2019 | 91.934 | 34 |
| VALIDATION | 2020 | 98.471 | 34 |
| EMBARGO_2 | 2021 | 109.099 | 39 |
| TEST | 2022-2023 | 260.445 | 54 |

---

## 7. Uso de TRAIN

TRAIN será el único conjunto utilizado para aprender:

- imputaciones;
- escalamiento;
- parámetros del modelo;
- codificaciones aprendidas;
- pesos internos;
- hiperparámetros cuando corresponda mediante procedimientos internos sobre TRAIN.

Toda transformación aprendida deberá ajustarse únicamente con TRAIN.

---

## 8. Uso de VALIDATION

VALIDATION será utilizado para:

- comparar familias de modelos;
- comparar configuraciones previamente justificadas;
- seleccionar hiperparámetros;
- evaluar capacidad de ranking;
- revisar estabilidad;
- seleccionar el modelo candidato final.

VALIDATION no será incorporado al entrenamiento inicial de los modelos durante la fase comparativa.

---

## 9. Uso de los años de embargo

`EMBARGO_1` y `EMBARGO_2` no serán utilizados como observaciones para:

- entrenamiento;
- selección de modelos;
- comparación de modelos;
- evaluación final.

Sus características históricas pueden haber sido utilizadas previamente para construir un lag `t-1` de una observación posterior cuando dicha información estaba disponible temporalmente.

---

## 10. Uso de TEST

TEST corresponde a 2022-2023.

Durante la etapa de desarrollo permanecerá cerrado para evaluación predictiva.

No se utilizará para:

- selección de variables;
- comparación de modelos;
- ajuste de hiperparámetros;
- selección de umbrales;
- calibración;
- análisis SHAP orientado a modificar el modelo;
- selección del modelo final.

TEST podrá abrirse una sola vez después de congelar el modelo final y su pipeline completo.

---

## 11. Preprocesamiento numérico

Para los modelos que requieran preprocesamiento numérico se utilizará inicialmente:

- imputación por mediana;
- aprendizaje de la mediana exclusivamente con TRAIN.

Para modelos sensibles a escala, como Regresión Logística y red neuronal:

- se aplicará estandarización;
- parámetros de escalamiento aprendidos exclusivamente con TRAIN.

No se calcularán medianas ni escalas utilizando VALIDATION o TEST.

---

## 12. Preprocesamiento categórico

Para modelos scikit-learn que requieran representación numérica explícita:

- imputación de categorías faltantes;
- categoría faltante explícita o estrategia equivalente reproducible;
- One-Hot Encoding;
- manejo de categorías desconocidas.

El codificador se ajustará únicamente con TRAIN.

Para CatBoost se permitirá utilizar directamente variables categóricas mediante su tratamiento nativo.

No se utilizará target encoding calculado con VALIDATION o TEST.

---

## 13. Valores faltantes

No se eliminarán observaciones únicamente por presentar valores faltantes.

Los valores faltantes forman parte esperada del universo histórico.

Su tratamiento deberá realizarse dentro del pipeline correspondiente.

---

## 14. Desbalance

La prevalencia positiva es extremadamente baja.

Para modelos compatibles se evaluará una configuración de ponderación de clases.

En Regresión Logística y Random Forest se utilizará inicialmente:

`class_weight="balanced"`

Para CatBoost se utilizará una estrategia equivalente de ponderación de clases.

Para TensorFlow/Keras se podrán utilizar pesos de clase calculados exclusivamente a partir de TRAIN.

No se utilizará TEST para definir el tratamiento del desbalance.

---

## 15. Interpretación de scores

Los valores generados por los modelos se utilizarán inicialmente como:

- score de afinidad;
- criterio de ordenamiento;
- mecanismo de priorización.

No se presentarán automáticamente como probabilidades reales calibradas.

Cualquier calibración deberá evaluarse como una etapa independiente y únicamente después de seleccionar el modelo candidato.

---

## 16. Modelos v10

Las familias de modelos previstas son:

1. Regresión Logística;
2. Random Forest;
3. CatBoost;
4. Red neuronal TensorFlow/Keras.

La Regresión Logística funcionará como baseline interpretable.

Los modelos más complejos serán comparados contra este baseline utilizando el mismo universo y el mismo protocolo temporal.

---

## 17. Orden de ejecución

El orden inicial será:

1. Regresión Logística;
2. Random Forest;
3. CatBoost;
4. TensorFlow/Keras.

No se utilizarán resultados de TEST para modificar este orden ni para redefinir configuraciones.

---

## 18. Métrica principal

Debido al fuerte desbalance de clases, la métrica principal de discriminación será:

`PR-AUC`

PR-AUC tendrá prioridad sobre Accuracy como medida general de desempeño.

---

## 19. Métricas complementarias

También se calcularán:

- ROC-AUC;
- Precision;
- Recall;
- F1.

Las métricas dependientes de umbral serán interpretadas con cautela debido al fuerte desbalance.

---

## 20. Métricas de ranking

Debido al objetivo operativo de priorizar empresas, se calcularán:

- Precision@K;
- Recall@K;
- Lift@K.

Valores iniciales de K:

- 50;
- 100;
- 200.

Estas métricas deberán utilizar exactamente la misma definición para todos los modelos comparados.

---

## 21. Prioridad operacional

La comparación de modelos no se basará únicamente en ROC-AUC.

Se dará especial atención a:

- PR-AUC;
- Precision@50;
- Precision@100;
- Precision@200;
- Recall@K;
- Lift@K;
- estabilidad temporal;
- interpretabilidad;
- riesgo de sobreajuste.

---

## 22. Accuracy

Accuracy podrá calcularse como referencia técnica, pero no será utilizada como criterio principal de selección debido al fuerte desbalance de clases.

---

## 23. Selección de modelo

La selección no se realizará utilizando un único indicador aislado.

El modelo candidato deberá mostrar un equilibrio entre:

- desempeño;
- capacidad de ranking;
- estabilidad;
- interpretabilidad;
- riesgo de sesgo;
- facilidad de integración;
- capacidad de adaptación.

La comparación formal podrá apoyarse posteriormente en la matriz metodológica definida para el proyecto:

- robustez: 25 %;
- explicabilidad: 25 %;
- sesgo: 15 %;
- integración: 15 %;
- adaptabilidad y drift: 20 %.

Estos pesos no sustituyen las métricas predictivas; constituyen una evaluación complementaria para la selección tecnológica.

---

## 24. Hiperparámetros

Los hiperparámetros podrán ajustarse utilizando exclusivamente:

- TRAIN;
- VALIDATION.

Se evitarán búsquedas excesivamente amplias que conviertan VALIDATION en un segundo conjunto de entrenamiento.

Cada configuración evaluada deberá quedar registrada.

---

## 25. Reproducibilidad

Los scripts de entrenamiento deberán fijar semillas aleatorias cuando la librería correspondiente lo permita.

Se utilizará inicialmente:

`random_state = 42`

o equivalente.

Las versiones principales del entorno están congeladas en:

- `requirements.txt`;
- `requirements-lock.txt`.

---

## 26. Persistencia de resultados

Cada experimento deberá registrar al menos:

- versión del dataset;
- Feature Set utilizado;
- modelo;
- hiperparámetros;
- fecha de ejecución;
- métricas sobre TRAIN cuando corresponda;
- métricas sobre VALIDATION;
- métricas de ranking;
- tiempo de entrenamiento;
- semilla;
- versión de librerías relevantes.

TEST no aparecerá en los reportes de experimentos de desarrollo.

---

## 27. Sobreajuste

Se revisará explícitamente la diferencia entre TRAIN y VALIDATION.

Un desempeño muy superior en TRAIN frente a VALIDATION será tratado como posible señal de sobreajuste.

La evaluación deberá considerar especialmente esta situación en Random Forest, CatBoost y redes neuronales.

---

## 28. Interpretabilidad

Después de obtener modelos candidatos se utilizarán técnicas de interpretabilidad.

Para modelos compatibles se utilizará principalmente:

- SHAP.

La Regresión Logística permitirá además revisar directamente:

- dirección de coeficientes;
- magnitud relativa de coeficientes estandarizados.

La interpretabilidad no se utilizará sobre TEST para rediseñar el modelo.

---

## 29. Sesgos y equidad

El análisis posterior deberá evaluar si el ranking presenta diferencias relevantes asociadas a variables como:

- provincia;
- tipo de compañía;
- otras agrupaciones justificadas metodológicamente.

El análisis de equidad no implicará que una característica deba eliminarse automáticamente.

Toda modificación deberá ser documentada y evaluada sin utilizar TEST para iteración.

---

## 30. Extensión v10-sector

Después de establecer resultados de `v10-core`, podrá evaluarse una extensión controlada denominada:

`v10-sector`

que incorporará:

- `bi_cod_segmento`;
- `bi_ciiu_n1`.

La extensión deberá compararse contra `v10-core` únicamente utilizando TRAIN y VALIDATION.

No se incorporará automáticamente al modelo final.

---

## 31. Variables enriquecidas

Las variables financieras adicionales y razones oficiales previamente auditadas no forman parte del núcleo inicial.

Podrán estudiarse en versiones posteriores únicamente mediante experimentos explícitamente versionados.

No se agregarán silenciosamente después de observar resultados.

---

## 32. Crecimiento y tendencias

El modelo núcleo inicial no incorpora variables derivadas adicionales de crecimiento o tendencia.

Cualquier extensión de este tipo deberá:

- definirse antes del entrenamiento correspondiente;
- utilizar únicamente información disponible hasta t;
- construirse sin información futura;
- registrarse como experimento separado.

---

## 33. Calibración

La calibración de scores no forma parte del baseline inicial.

Solo se evaluará después de seleccionar un modelo candidato.

Si se implementa, deberá realizarse sin utilizar TEST para ajuste.

Hasta entonces, los resultados deberán denominarse scores y no probabilidades estimadas calibradas.

---

## 34. Evaluación final

Una vez congelados:

- modelo;
- Feature Set;
- pipeline;
- transformaciones;
- hiperparámetros;
- criterio de ranking;
- estrategia de calibración si existiera;

se permitirá una evaluación final sobre TEST.

La evaluación final deberá reportar separadamente:

- ejercicio 2022;
- ejercicio 2023;
- agregado 2022-2023.

---

## 35. Regla de no retroalimentación desde TEST

Una vez abierto TEST, sus resultados no podrán utilizarse para modificar retrospectivamente el modelo v10 evaluado.

Si TEST revela una debilidad que motive cambios, dichos cambios deberán registrarse como una versión posterior y requerir un nuevo esquema de validación.

---

## 36. Estado final

**Protocolo de Modelado v10: CONGELADO**

El siguiente paso será implementar el baseline de Regresión Logística utilizando exclusivamente:

- TRAIN para ajuste;
- VALIDATION para evaluación de desarrollo.

**TEST permanece cerrado.**
