# Prospect Finder BVQ
## Explicabilidad del modelo v10 mediante SHAP y LIME

### 1. Objetivo

El presente documento registra el análisis de explicabilidad realizado sobre el modelo final v10 de Prospect Finder BVQ.

El análisis tiene como objetivo comprender los factores asociados con las predicciones del modelo seleccionado y evaluar técnicas que permitan explicar sus resultados tanto a nivel global como para empresas individuales.

Las técnicas utilizadas fueron:

- Permutation Importance.
- SHAP.
- LIME.

El análisis se realizó después del cierre de la evaluación final de v10.

Por tanto, ninguna de estas técnicas fue utilizada para modificar:

- las variables del modelo;
- la definición del target;
- los hiperparámetros;
- la configuración del modelo;
- la selección del modelo final;
- los resultados obtenidos sobre TEST.

El modelo permanece congelado como:

`v10_hgb_financial_c3`

Configuración:

`C3_CONSERVATIVE`

---

## 2. Modelo analizado

El modelo final corresponde a un clasificador basado en HistGradientBoosting entrenado para generar un score de priorización de empresas con potencial de convertirse en emisores dentro del horizonte definido por el proyecto.

El modelo utiliza 25 variables:

- 17 variables numéricas;
- 7 variables booleanas;
- 1 variable categórica.

La variable categórica utilizada es:

`tipo_compania`

El target es:

`TARGET_24M`

El score generado debe interpretarse como un indicador de priorización y no como una probabilidad calibrada de que una empresa vaya a convertirse en emisor.

---

## 3. Control de integridad

Antes de ejecutar SHAP y LIME se reprodujeron nuevamente las métricas oficiales del conjunto TEST.

Resultados:

| Métrica | Resultado |
|---|---:|
| Observaciones TEST | 260,445 |
| Positivos TEST | 54 |
| PR-AUC | 0.007468801 |
| ROC-AUC | 0.934603901 |

Los resultados coinciden exactamente con la evaluación oficial de v10.

Esto confirma que el análisis de explicabilidad utiliza el mismo modelo, las mismas variables y el mismo universo TEST.

---

## 4. Preparación de datos para explicabilidad

La preparación utilizada para SHAP y LIME replica la lógica empleada durante la evaluación de v10.

Las variables numéricas fueron convertidas a tipo numérico y los valores infinitos fueron tratados como valores faltantes.

Las variables booleanas fueron normalizadas a:

- 0;
- 1;
- valor faltante.

La variable:

`tipo_compania`

fue convertida a variable categórica utilizando exclusivamente las categorías observadas en TRAIN.

TEST no participó en la definición del vocabulario de categorías.

Para las referencias utilizadas por SHAP y LIME se construyó una muestra de 5,000 observaciones proveniente exclusivamente de TRAIN.

De esta manera se evita utilizar información de TEST para definir el comportamiento de referencia de las técnicas de explicabilidad.

---

# 5. SHAP

## 5.1 Metodología

Se utilizó SHAP como técnica principal de explicabilidad.

La implementación se realizó mediante un enfoque model-agnostic con:

`PermutationExplainer`

Este enfoque permite explicar el comportamiento del modelo final sin modificar ni reconstruir internamente el estimador congelado.

Para el análisis se utilizó:

- una muestra de referencia de TRAIN;
- un background SHAP de 75 observaciones;
- una muestra global de 150 observaciones de TEST;
- tres casos individuales para el análisis local.

El propósito de SHAP es estimar la contribución de cada variable al resultado producido por el modelo.

---

## 5.2 Importancia global SHAP

La importancia global se calculó mediante el promedio del valor absoluto de las contribuciones SHAP:

`mean(|SHAP|)`

Los resultados obtenidos fueron:

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

## 5.3 Interpretación global de SHAP

El análisis muestra que las variables con mayor influencia global están asociadas principalmente con:

- tamaño empresarial;
- volumen de actividad;
- patrimonio;
- evolución financiera;
- estructura patrimonial;
- rentabilidad.

La variable con mayor importancia es:

`activos_final`

seguida por:

`bi_ingresos_ventas`

Esto evidencia que la escala empresarial tiene un peso importante dentro del comportamiento aprendido por el modelo.

También aparecen entre las variables relevantes:

- patrimonio del periodo anterior;
- crecimiento de patrimonio;
- relación patrimonio / activos;
- crecimiento de activos;
- patrimonio actual;
- activos del periodo anterior;
- ROA;
- margen neto.

La variable:

`tipo_compania`

aparece en la posición 11.

Esto indica que participa en el comportamiento del modelo, pero no constituye una de sus principales variables globales.

Las variables booleanas presentan importancia SHAP igual a cero dentro de la muestra utilizada.

Este resultado no implica necesariamente que deban eliminarse o que nunca intervengan en una predicción. Únicamente indica que no mostraron una contribución global apreciable dentro del análisis realizado.

---

## 5.4 Limitación de la importancia global

El valor:

`mean(|SHAP|)`

representa la magnitud promedio de la contribución de una variable.

No permite determinar directamente si una variable incrementa o disminuye el score.

Para analizar la dirección de la contribución es necesario revisar explicaciones locales o análisis adicionales de dependencia.

---

# 6. Explicaciones locales SHAP

Para evaluar el comportamiento individual del modelo se seleccionaron tres casos completos de TEST.

| Caso | Año | TARGET_24M | Score v10 |
|---|---:|---:|---:|
| Mayor score completo de TEST | 2022 | 0 | 0.975080 |
| Mejor positivo completo de TEST | 2022 | 1 | 0.967644 |
| Caso con score cercano a la mediana | 2023 | 0 | 0.126871 |

La selección se realizó exclusivamente con fines de interpretación después del cierre del modelo.

---

## 6.1 Fidelidad de SHAP

En los tres casos analizados, SHAP reconstruyó exactamente el score generado por el modelo.

| Caso | Score modelo | Score reconstruido SHAP | Error |
|---|---:|---:|---:|
| Mayor score completo TEST | 0.975080072 | 0.975080072 | 0.0000000000 |
| Mejor positivo completo TEST | 0.967644384 | 0.967644384 | 0.0000000000 |
| Score mediano completo TEST | 0.126870629 | 0.126870629 | 0.0000000000 |

Esto proporciona evidencia de alta fidelidad para las explicaciones locales generadas.

---

# 7. Caso local: mejor positivo real

El mejor positivo real analizado corresponde a una empresa que presentó:

`TARGET_24M = 1`

y un score de:

`0.967644`

Las principales contribuciones positivas identificadas por SHAP fueron:

| Variable | Valor | Contribución SHAP |
|---|---:|---:|
| activos_final | 11,590,309.16 | +0.255956 |
| patrimonio_final_t1 | 2,201,209.60 | +0.125590 |
| patrimonio_final | 2,678,111.87 | +0.111640 |
| bi_ingresos_ventas | 10,626,826.73 | +0.072366 |
| fin_ratio_patrimonio_activos | 0.231065 | +0.047199 |
| bi_n_empleados | 80 | +0.038565 |
| fin_roa | 0.041540 | +0.037248 |
| bi_ingresos_ventas_t1 | 8,949,293.41 | +0.020220 |
| fin_margen_neto | 0.045306 | +0.016933 |
| fin_crecimiento_patrimonio | 0.216655 | +0.015696 |

La explicación muestra una combinación de:

- escala empresarial;
- patrimonio relevante;
- ventas significativas;
- estructura patrimonial positiva;
- rentabilidad;
- crecimiento.

Este perfil fue considerado por el modelo como altamente prioritario.

---

# 8. Caso local: mayor score de TEST

El caso con mayor score completo obtuvo:

`0.975080`

pero presentó:

`TARGET_24M = 0`

Este caso es especialmente relevante para interpretar correctamente el sistema.

Las principales contribuciones fueron:

| Variable | Valor | Contribución SHAP |
|---|---:|---:|
| activos_final | 65,742,359.13 | +0.328269 |
| patrimonio_final | 17,478,361.28 | +0.124248 |
| bi_ingresos_ventas | 46,354,051.54 | +0.089486 |
| patrimonio_final_t1 | 14,563,703.70 | +0.066427 |
| bi_n_empleados | 349 | +0.045481 |
| fin_roa | 0.044687 | +0.039539 |
| fin_margen_neto | 0.063378 | +0.018794 |
| bi_ingresos_ventas_t1 | 24,050,564.70 | +0.016458 |
| fin_ratio_patrimonio_activos | 0.265861 | +0.012739 |
| fin_crecimiento_patrimonio | 0.200132 | +0.012606 |

Financieramente, la empresa presenta varias características asociadas con scores elevados.

Sin embargo, no se convirtió en emisor dentro del horizonte del target.

Este resultado demuestra una característica central del proyecto:

**un score alto no implica que una empresa necesariamente vaya a convertirse en emisor.**

El modelo identifica perfiles que considera prioritarios a partir de patrones históricos, pero existen factores comerciales, estratégicos, regulatorios y empresariales que no necesariamente están contenidos en las variables utilizadas.

Por esta razón Prospect Finder BVQ debe utilizarse como herramienta de apoyo para priorización y no como sistema de decisión automática.

---

# 9. Caso local: score mediano

El caso seleccionado con score cercano a la mediana obtuvo:

`0.126871`

Entre las contribuciones principales se observaron:

| Variable | Valor | Contribución SHAP |
|---|---:|---:|
| activos_final | 127,243.44 | -0.040956 |
| bi_ingresos_ventas | 180,822.14 | -0.032432 |
| fin_crecimiento_patrimonio | 0.028265 | +0.023033 |
| tipo_compania | RESPONSABILIDAD LIMITADA | -0.018442 |
| fin_ratio_patrimonio_activos | 0.357974 | +0.015359 |
| fin_margen_neto | 0.051039 | +0.012016 |
| fin_crecimiento_activos | -0.008454 | -0.011666 |
| activos_final_t1 | 128,328.28 | -0.009801 |
| patrimonio_final_t1 | 44,297.75 | +0.005231 |
| bi_n_empleados | 9 | +0.004255 |

El caso demuestra que el modelo combina señales positivas y negativas.

Aunque la empresa presenta:

- margen positivo;
- estructura patrimonial positiva;
- crecimiento patrimonial;

su menor escala en activos y ventas reduce su score relativo.

La contribución negativa observada para:

`tipo_compania = RESPONSABILIDAD LIMITADA`

corresponde exclusivamente a esta predicción local.

No debe generalizarse como una penalización automática para todas las empresas con esta forma societaria.

El análisis agregado de posibles concentraciones y sesgos se encuentra documentado de manera separada.

---

# 10. LIME

## 10.1 Propósito

LIME fue utilizado como una técnica complementaria de explicabilidad local.

Su objetivo fue contrastar las explicaciones obtenidas mediante SHAP y verificar si un modelo sustituto local identifica patrones semejantes alrededor de las observaciones seleccionadas.

LIME genera observaciones artificiales cercanas al registro analizado y construye un modelo simplificado alrededor de dicha observación.

Por esta razón, su resultado representa una aproximación local al comportamiento del modelo original.

---

## 10.2 Resultados de LIME

Para el caso de mayor score:

| Resultado | Valor |
|---|---:|
| Score v10 | 0.975080 |
| Aproximación local LIME | 0.859736 |

Para el mejor positivo real:

| Resultado | Valor |
|---|---:|
| Score v10 | 0.967644 |
| Aproximación local LIME | 0.851937 |

Para el caso de score mediano:

| Resultado | Valor |
|---|---:|
| Score v10 | 0.126871 |
| Aproximación local LIME | 0.051120 |

LIME no reproduce exactamente la predicción del modelo.

Esto es consistente con su naturaleza de modelo sustituto local.

---

## 10.3 Factores identificados por LIME

En los casos con score elevado, LIME identificó como factores importantes:

- activos elevados;
- patrimonio previo elevado;
- ventas elevadas;
- crecimiento de activos;
- patrimonio elevado;
- número de empleados;
- crecimiento patrimonial.

Estos resultados muestran coincidencias conceptuales con las explicaciones obtenidas mediante SHAP.

Sin embargo, también se observaron diferencias.

Por ejemplo, determinadas condiciones de:

- ROA;
- margen neto;

recibieron pesos negativos dentro de la aproximación local de LIME mientras que SHAP mostró contribuciones positivas en los mismos casos.

Estas diferencias refuerzan la necesidad de no interpretar LIME como una representación exacta del modelo.

---

# 11. Comparación entre SHAP y LIME

| Criterio | SHAP | LIME |
|---|---|---|
| Explicación global | Sí | No es su uso principal |
| Explicación local | Sí | Sí |
| Reconstrucción del score | Exacta en los casos analizados | Aproximada |
| Interpretación individual | Alta | Alta |
| Dependencia de modelo sustituto | No en la explicación obtenida | Sí |
| Consistencia observada | Mayor | Menor |
| Uso recomendado | Principal | Complementario |

---

# 12. Técnica seleccionada para Prospect Finder

Se selecciona:

**SHAP como técnica principal de explicabilidad.**

Las razones son:

1. permite realizar análisis global y local;
2. mostró coherencia con el comportamiento del modelo;
3. reconstruyó exactamente las predicciones de los tres casos analizados;
4. permite identificar la dirección y magnitud de la contribución de cada variable en predicciones individuales;
5. facilita la generación de explicaciones que pueden posteriormente traducirse a lenguaje de negocio.

LIME se mantendrá como:

**técnica complementaria de contraste académico.**

Su utilización permite demostrar que se evaluó más de una alternativa de interpretabilidad y que se analizó la fidelidad de cada técnica antes de seleccionar la más adecuada para el producto.

---

# 13. Relación con Permutation Importance

El análisis previo mediante Permutation Importance y el análisis SHAP deben interpretarse como herramientas complementarias.

Permutation Importance responde principalmente a:

**¿Cuánto se deteriora el desempeño cuando se altera una variable?**

SHAP responde principalmente a:

**¿Cómo contribuyen las variables al score generado para una observación o conjunto de observaciones?**

Por esta razón los rankings obtenidos mediante ambas técnicas no tienen que ser idénticos.

Las diferencias entre ellas no implican necesariamente una contradicción.

Cada técnica evalúa aspectos diferentes del comportamiento del modelo.

---

# 14. Explicabilidad en el producto

En Prospect Finder BVQ no se recomienda mostrar directamente valores técnicos de SHAP al usuario comercial.

La aplicación deberá traducirlos a explicaciones comprensibles.

Ejemplo:

**Factores que elevan la prioridad**

- nivel de activos elevado;
- ventas relevantes;
- patrimonio sólido;
- rentabilidad positiva;
- crecimiento patrimonial.

**Factores que reducen la prioridad**

- menor escala empresarial;
- reducción de activos;
- menor volumen de ventas;
- información incompleta.

El detalle técnico completo permanecerá disponible para auditoría y análisis del modelo.

---

# 15. Uso responsable

Las explicaciones generadas por SHAP y LIME describen el comportamiento del modelo.

No representan relaciones causales.

Por tanto, no debe afirmarse que una empresa obtiene un score alto:

“porque se convertirá en emisor”.

La interpretación correcta es:

“el modelo asigna una mayor prioridad porque el perfil financiero de la empresa presenta características que históricamente han estado asociadas con empresas que posteriormente se convirtieron en emisores”.

La decisión de realizar una gestión comercial continuará correspondiendo a los especialistas de la Bolsa de Valores Quito.

---

# 16. Principales conclusiones

El análisis de explicabilidad permite concluir que:

1. El modelo v10 utiliza principalmente variables asociadas con tamaño, actividad, patrimonio, crecimiento y rentabilidad.

2. Activos y ventas son las variables con mayor influencia global observada mediante SHAP.

3. El modelo no depende exclusivamente de una variable, sino de combinaciones de características.

4. Las explicaciones locales permiten comprender por qué una empresa recibe un score alto, medio o bajo.

5. Un score elevado no garantiza que la empresa se convierta en emisor.

6. El caso con mayor score de TEST y target negativo demuestra la necesidad de supervisión humana.

7. SHAP presentó mayor fidelidad que LIME en los casos evaluados.

8. LIME resulta útil como técnica de contraste, pero sus explicaciones deben interpretarse como aproximaciones locales.

9. SHAP será la técnica principal utilizada para explicar los resultados dentro del prototipo de Prospect Finder BVQ.

10. El modelo continuará funcionando exclusivamente como herramienta de priorización y apoyo al proceso comercial.

---

# 17. Evidencias generadas

El análisis se encuentra implementado en:

`src/analysis/analyze_v10_shap_lime.py`

Los resultados se almacenan en:

`reports/results/v10/explainability/shap_lime/`

Archivos generados:

`v10_shap_global_importance.csv`

`v10_shap_local_explanations.csv`

`v10_shap_global_importance.png`

`v10_lime_local_explanations.csv`

`v10_explainability_local_cases.csv`

`v10_shap_lime_metadata.json`

Adicionalmente se generan archivos HTML con explicaciones locales de LIME para los casos seleccionados.

---

## Estado

**Análisis SHAP: completado.**

**Análisis LIME: completado.**

**Comparación de técnicas: completada.**

**Técnica principal seleccionada: SHAP.**

**Modelo v10: permanece congelado.**