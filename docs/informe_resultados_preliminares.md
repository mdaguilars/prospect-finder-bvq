# Informe de resultados preliminares

## Sistema inteligente basado en aprendizaje automático y redes neuronales para identificar y priorizar empresas con potencial de convertirse en emisores del mercado de valores ecuatoriano para la Bolsa de Valores Quito

### Integrantes

- Marcelo David Aguilar Salguero
- Francisco Xavier Meneses Játiva
- Luis Miguel Gallardo Dávila

---

# 1. Descripción del prototipo desarrollado

El proyecto busca desarrollar un sistema inteligente que permita identificar y priorizar empresas ecuatorianas con potencial de convertirse en futuros emisores del mercado de valores.

La necesidad parte de un problema organizacional de la Bolsa de Valores Quito (BVQ): existe un universo amplio de empresas que potencialmente podrían acceder al mercado de valores, pero analizarlo manualmente de forma sistemática resulta complejo. Esto dificulta establecer criterios homogéneos de prospección y priorizar de manera objetiva las empresas que podrían representar mejores oportunidades de acercamiento comercial.

Como primera aproximación se desarrolló un modelo de referencia o *baseline* basado en regresión logística. Su propósito no es reemplazar el criterio comercial o financiero de la BVQ, sino comprobar si existe señal predictiva en la información financiera histórica de las empresas y establecer un punto de comparación para modelos posteriores de mayor complejidad.

La unidad de análisis utilizada es:

**empresa-año**.

La variable objetivo definida es:

`TARGET_24M`

Esta variable toma el valor de:

- `1`: cuando una empresa se registra por primera vez como emisor dentro de los 24 meses posteriores al período analizado.
- `0`: cuando no se produce este evento dentro del horizonte definido.

Las empresas que ya habían sido emisoras antes de la fecha de corte correspondiente fueron excluidas del universo elegible.

---

# 2. Fuentes de datos

La fuente principal utilizada para construir las variables predictoras corresponde a información financiera pública de la Superintendencia de Compañías, Valores y Seguros (SCVS).

Para construir la variable objetivo se utilizó la información histórica del Registro del Mercado de Valores de la misma institución.

Se trabajó con estados financieros comprendidos entre 2015 y 2023.

Durante la etapa de preparación se identificaron diferentes estructuras de planes contables, por lo que fue necesario realizar un proceso de homologación de cuentas financieras.

Se utilizaron siete estructuras contables principales:

- PLAN_622
- PLAN_639
- PLAN_807
- PLAN_819
- PLAN_830
- PLAN_868
- PLAN_925

Como resultado de este proceso se obtuvo inicialmente un dataset financiero armonizado con:

**887.469 observaciones empresa-año.**

---

# 3. Variables financieras homologadas

Se homologaron nueve variables financieras principales:

- Activo total
- Activo corriente
- Efectivo
- Pasivo total
- Pasivo corriente
- Pasivo no corriente
- Patrimonio
- Capital
- Utilidad neta

La homologación fue validada mediante ecuaciones contables.

La principal validación utilizada fue:

**Activo = Pasivo + Patrimonio**

El 99,24 % de las observaciones presentó una diferencia relativa menor o igual al 0,01 %.

También se verificó:

**Pasivo total = Pasivo corriente + Pasivo no corriente**

En este caso, el 99,31 % de las observaciones cumplió una diferencia relativa menor o igual al 0,01 %.

Estos resultados permitieron confirmar que la homologación de las principales cuentas financieras era suficientemente consistente para continuar con la construcción del prototipo.

---

# 4. Dataset utilizado para modelado

Después de excluir observaciones correspondientes a empresas que ya eran emisoras al momento del corte, el dataset utilizado para modelado quedó compuesto por:

| Indicador | Resultado |
|---|---:|
| Observaciones empresa-año | 884.072 |
| Empresas únicas | 166.107 |
| Casos positivos | 440 |
| Casos negativos | 883.632 |
| Prevalencia aproximada | 0,0498 % |

El resultado muestra un problema de clasificación extremadamente desbalanceado.

Por esta razón, la exactitud general o *accuracy* no se considera una métrica adecuada como criterio principal de evaluación.

---

# 5. Ingeniería de variables

Además de las variables financieras originales, se generaron transformaciones y razones financieras.

Para reducir el efecto de las diferencias de escala se utilizó una transformación logarítmica con signo:

`sign(x) × log(1 + |x|)`

Se construyeron las siguientes variables:

- LOG_ACTIVO_TOTAL
- LOG_ACTIVO_CORRIENTE
- LOG_EFECTIVO
- LOG_PASIVO_TOTAL
- LOG_PASIVO_CORRIENTE
- LOG_PASIVO_NO_CORRIENTE
- LOG_PATRIMONIO
- LOG_CAPITAL
- LOG_UTILIDAD_NETA

También se calcularon:

- Liquidez corriente
- Endeudamiento
- Autonomía financiera
- ROA
- Efectivo sobre activos
- Capital sobre activos
- Pasivo corriente sobre pasivo total

Adicionalmente se incorporó:

`SECTOR_CIIU`

correspondiente a la primera sección de la clasificación CIIU de la empresa.

La variable `PLAN_CONTABLE` se mantuvo únicamente como elemento de trazabilidad y control de calidad y no se incorporó como predictor.

---

# 6. División temporal de los datos

Para evitar una evaluación basada en una partición aleatoria, se utilizó una separación temporal.

| Conjunto | Período | Observaciones | Positivos |
|---|---|---:|---:|
| TRAIN | 2015–2020 | 514.527 | 340 |
| VALIDATION | 2021 | 109.101 | 42 |
| TEST | 2022–2023 | 260.444 | 58 |

Este enfoque permite evaluar de manera más realista la capacidad del modelo de aprender con información histórica y aplicarse posteriormente sobre períodos futuros.

El preprocesamiento, imputación y escalamiento fueron ajustados exclusivamente utilizando TRAIN.

---

# 7. Modelo de referencia

Como modelo inicial se utilizó una regresión logística regularizada.

La configuración del Baseline v1 fue:

- Regresión logística
- Regularización L2
- `C = 1.0`
- `class_weight = "balanced"`
- `solver = "lbfgs"`
- `max_iter = 2000`
- `random_state = 42`

Las variables numéricas fueron imputadas mediante la mediana y posteriormente estandarizadas.

La variable categórica `SECTOR_CIIU` fue procesada mediante codificación One-Hot.

Este modelo constituye el punto de referencia frente al cual se compararán las siguientes iteraciones.

---

# 8. Métricas seleccionadas

Debido al fuerte desbalance de clases, se utilizaron principalmente:

- PR-AUC
- ROC-AUC
- Precision
- Recall
- F1

Para evaluar específicamente la utilidad del modelo como herramienta de prospección se utilizaron además:

- Precision@K
- Recall@K
- Lift@K

con:

- K = 50
- K = 100
- K = 200

Estas métricas permiten analizar cuántos futuros emisores aparecen dentro de las primeras empresas priorizadas por el modelo.

---

# 9. Resultados preliminares del Baseline v1

## 9.1 Métricas generales

| Conjunto | PR-AUC | ROC-AUC | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|
| TRAIN | 0,099413 | 0,946436 | 0,004494 | 0,894118 | 0,008942 |
| VALIDATION | 0,031095 | 0,940593 | 0,002566 | 0,880952 | 0,005118 |
| TEST | 0,007291 | 0,927740 | 0,000627 | 0,931034 | 0,001254 |

El ROC-AUC permanece por encima de 0,92 en los tres conjuntos, lo que evidencia capacidad general de discriminación.

Sin embargo, debido al desbalance extremo, el PR-AUC y las métricas de ranking son más representativas para evaluar la utilidad del modelo.

Se observa una reducción del PR-AUC a medida que el modelo se aplica sobre períodos temporalmente más alejados:

- TRAIN: 0,099413
- VALIDATION: 0,031095
- TEST: 0,007291

Este resultado evidencia una degradación temporal que deberá ser estudiada en las siguientes fases del proyecto.

![Curvas Precision-Recall](../reports/figures/baseline_02_precision_recall.png)

---

# 10. Desbalance de clases

La siguiente figura muestra la diferencia existente entre la cantidad de observaciones negativas y positivas en los diferentes conjuntos.

![Distribución de clases](../reports/figures/baseline_01_distribucion_clases.png)

La cantidad limitada de nuevos emisores constituye uno de los principales retos del problema.

El modelo debe encontrar patrones útiles a partir de aproximadamente 0,05 % de observaciones positivas dentro del universo disponible.

---

# 11. Análisis del umbral de clasificación

Inicialmente se utilizó un umbral de clasificación de:

`0,50`

En VALIDATION se obtuvo:

| Resultado | Cantidad |
|---|---:|
| Verdaderos positivos | 37 |
| Falsos negativos | 5 |
| Falsos positivos | 14.381 |
| Verdaderos negativos | 94.678 |

![Matriz de confusión Validation](../reports/figures/baseline_03_confusion_matrix_validation.png)

El modelo identifica 37 de los 42 futuros emisores, pero genera 14.381 falsos positivos.

En TEST se obtuvo:

| Resultado | Cantidad |
|---|---:|
| Verdaderos positivos | 54 |
| Falsos negativos | 4 |
| Falsos positivos | 86.032 |
| Verdaderos negativos | 174.354 |

![Matriz de confusión Test](../reports/figures/baseline_04_confusion_matrix_test.png)

Estos resultados muestran que el umbral de 0,50 no es adecuado como regla operativa de prospección comercial.

Por esta razón, consideramos que el problema debe ser tratado principalmente como un problema de **priorización de empresas**, más que como una clasificación binaria convencional.

---

# 12. Resultados de ranking

## 12.1 TRAIN

| K | Futuros emisores encontrados | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 24 | 0,4800 | 0,0706 | 726,39 |
| 100 | 42 | 0,4200 | 0,1235 | 635,59 |
| 200 | 59 | 0,2950 | 0,1735 | 446,43 |

## 12.2 VALIDATION

| K | Futuros emisores encontrados | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 5 | 0,1000 | 0,1190 | 259,76 |
| 100 | 5 | 0,0500 | 0,1190 | 129,88 |
| 200 | 5 | 0,0250 | 0,1190 | 64,94 |

## 12.3 TEST

| K | Futuros emisores encontrados | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| 50 | 1 | 0,0200 | 0,0172 | 89,81 |
| 100 | 2 | 0,0200 | 0,0345 | 89,81 |
| 200 | 3 | 0,0150 | 0,0517 | 67,36 |

![Positivos Top K](../reports/figures/baseline_05_positivos_top_k.png)

![Lift Top K](../reports/figures/baseline_06_lift_top_k.png)

![Precision Top K](../reports/figures/baseline_07_precision_top_k.png)

---

# 13. Interpretación del ranking

Los resultados de ranking muestran que el modelo sí logra concentrar futuros emisores en las primeras posiciones con una frecuencia considerablemente superior a una selección aleatoria.

Por ejemplo, en VALIDATION, dentro de las primeras 50 empresas priorizadas aparecen 5 futuros emisores.

Esto corresponde a:

- Precision@50 = 10 %
- Recall@50 = 11,90 %
- Lift@50 = 259,76

El Lift@50 indica que la concentración de futuros emisores en las primeras posiciones es aproximadamente 260 veces superior a la prevalencia promedio de ese conjunto.

Sin embargo, la capacidad de concentración disminuye en el conjunto TEST.

En TEST:

- Top 50 identifica 1 futuro emisor.
- Top 100 identifica 2.
- Top 200 identifica 3.

Aunque el Lift continúa siendo elevado respecto a una selección aleatoria, la cobertura de futuros emisores todavía resulta insuficiente para considerar el modelo como una herramienta operativa definitiva.

---

# 14. Análisis de la posición de los futuros emisores

Se amplió el análisis hasta las primeras 1.000 empresas del ranking.

## VALIDATION

| Ranking | Positivos encontrados | Recall |
|---:|---:|---:|
| Top 50 | 5 | 11,90 % |
| Top 100 | 5 | 11,90 % |
| Top 200 | 5 | 11,90 % |
| Top 500 | 5 | 11,90 % |
| Top 1.000 | 10 | 23,81 % |

La mejor posición de un futuro emisor fue:

**7**

La mediana de posición fue:

**2.362**

La peor posición fue:

**64.033**

## TEST

| Ranking | Positivos encontrados | Recall |
|---:|---:|---:|
| Top 50 | 1 | 1,72 % |
| Top 100 | 2 | 3,45 % |
| Top 200 | 3 | 5,17 % |
| Top 500 | 4 | 6,90 % |
| Top 1.000 | 10 | 17,24 % |

La mejor posición fue:

**50**

La mediana fue:

**4.317**

La peor posición fue:

**160.698**

Estos resultados refuerzan la evidencia de una reducción temporal en la capacidad del modelo para concentrar futuros emisores en los primeros lugares.

---

# 15. Análisis de errores

Se analizaron de forma agregada los verdaderos positivos, falsos positivos, falsos negativos y verdaderos negativos.

En VALIDATION se identificaron cinco falsos negativos.

Estos casos pertenecieron a los sectores:

- F
- M
- H
- N
- R

En TEST se identificaron cuatro falsos negativos y los cuatro pertenecieron al sector:

**A**

Este resultado fue analizado únicamente como comportamiento observado y no permite concluir que exista un problema general con dicho sector debido al reducido número de casos.

---

# 16. Perfil financiero de falsos negativos

En VALIDATION se observaron diferencias entre los futuros emisores correctamente identificados y aquellos que el modelo no detectó con el umbral inicial.

Por ejemplo:

| Variable | Mediana TP | Mediana FN |
|---|---:|---:|
| LOG_ACTIVO_TOTAL | 16,1125 | 14,7207 |
| LIQUIDEZ_CORRIENTE | 1,1588 | 2,0661 |
| ENDEUDAMIENTO | 0,7749 | 0,6579 |
| AUTONOMIA_FINANCIERA | 0,2251 | 0,3421 |
| PASIVO_CORRIENTE_PASIVO | 0,7657 | 0,5787 |

Los falsos negativos presentan, en términos medianos:

- menor tamaño;
- mayor liquidez;
- menor endeudamiento;
- mayor autonomía financiera.

Estos resultados son descriptivos y no implican causalidad.

En TEST los cuatro falsos negativos presentan además un perfil especialmente diferente al patrón dominante:

- activos reducidos;
- ausencia de pasivos;
- autonomía financiera cercana a 1;
- elevada proporción de efectivo y capital respecto a activos.

Esto sugiere que una regresión logística puede tener dificultades para identificar determinados perfiles financieros atípicos.

---

# 17. Análisis de la variable sectorial

En el Baseline v1 varios coeficientes de mayor magnitud correspondieron a `SECTOR_CIIU`.

Por esta razón se analizó la distribución de eventos positivos por sector.

En TRAIN, los sectores con mayor cantidad de positivos fueron:

- G: 128
- C: 102
- A: 24
- F: 14
- N: 12
- E: 12
- K: 11

Los sectores G y C concentran aproximadamente el 67,6 % de los positivos de TRAIN.

También se identificaron sectores con muy pocos o ningún evento positivo.

Esto podía producir coeficientes sectoriales poco estables.

---

# 18. Experimento v2: eliminación de SECTOR_CIIU

Para comprobar la importancia de esta variable se construyó una segunda regresión logística eliminando completamente `SECTOR_CIIU`.

La comparación en VALIDATION fue:

| Métrica | Baseline v1 | Baseline v2 |
|---|---:|---:|
| PR-AUC | 0,031095 | 0,024402 |
| ROC-AUC | 0,940593 | 0,961619 |
| Precision@50 | 0,1000 | 0,0800 |
| Recall@50 | 0,1190 | 0,0952 |
| Lift@50 | 259,76 | 207,81 |

Aunque ROC-AUC aumentó, las métricas consideradas más importantes para la priorización disminuyeron.

El PR-AUC se redujo aproximadamente un 21,5 %.

Por tanto, decidimos mantener la información sectorial.

El conjunto TEST no fue utilizado para seleccionar entre Baseline v1 y v2.

---

# 19. Experimento v3: regularización

También se evaluó si una mayor regularización podía controlar la inestabilidad observada en algunos coeficientes.

Se probaron:

- C = 0,001
- C = 0,01
- C = 0,1
- C = 1
- C = 10

Los resultados principales en VALIDATION fueron:

| C | PR-AUC | ROC-AUC | Positivos Top 50 |
|---:|---:|---:|---:|
| 0,001 | 0,024217 | 0,955848 | 4 |
| 0,01 | 0,027559 | 0,951061 | 4 |
| 0,1 | 0,030555 | 0,946416 | 5 |
| 1 | 0,031095 | 0,940593 | 5 |
| 10 | 0,031135 | 0,934021 | 5 |

El valor C = 10 obtuvo el PR-AUC numéricamente más alto, pero la diferencia frente a C = 1 fue únicamente:

**0,000040**

Esto representa aproximadamente un 0,13 % de diferencia relativa.

Además, ambos modelos obtuvieron exactamente los mismos resultados en Top 50, Top 100 y Top 200.

Por esta razón, no consideramos que exista evidencia suficiente para sustituir el Baseline v1.

---

# 20. Modelo de referencia actual

Después de los experimentos realizados, se mantiene como referencia:

**Baseline v1**

con:

- Regresión logística
- C = 1
- class_weight = balanced
- SECTOR_CIIU incluido

Los experimentos v2 y v3 permitieron comprobar que ni eliminar completamente la información sectorial ni modificar únicamente la regularización producen una mejora material.

---

# 21. Fortalezas encontradas

Los resultados preliminares permiten identificar varias fortalezas del prototipo.

### Existe señal predictiva

Las características financieras contienen información que permite diferenciar parcialmente empresas con mayor afinidad histórica hacia la emisión de valores.

### El ranking supera ampliamente una selección aleatoria

Los valores de Lift obtenidos muestran que los futuros emisores aparecen concentrados en las primeras posiciones con una frecuencia significativamente superior a la prevalencia general.

### El proceso es temporal

El modelo no fue evaluado mediante una división aleatoria, sino respetando la secuencia cronológica.

### Existe trazabilidad

Los procesos de:

- construcción de datos;
- homologación;
- validación;
- construcción del target;
- ingeniería de variables;
- entrenamiento;
- evaluación;
- análisis de errores;

se encuentran implementados mediante scripts reproducibles y versionados.

---

# 22. Limitaciones encontradas

## 22.1 Desbalance extremo

El número de casos positivos es reducido:

**440 positivos frente a 883.632 negativos.**

Esto limita la capacidad del modelo de aprender diferentes perfiles de futuros emisores.

## 22.2 Degradación temporal

El desempeño disminuye al avanzar hacia períodos posteriores.

Esto puede estar asociado a:

- cambios en las características de los nuevos emisores;
- cambios sectoriales;
- nuevas condiciones económicas;
- variables actualmente no incorporadas;
- relaciones no lineales;
- reducido número de eventos positivos.

Estas posibilidades constituyen hipótesis de trabajo y todavía no conclusiones.

## 22.3 Variables principalmente estáticas

El modelo utiliza una fotografía financiera anual.

Todavía no incorpora variables como:

- crecimiento interanual;
- tendencia del activo;
- tendencia del patrimonio;
- evolución del endeudamiento;
- estabilidad de utilidades;
- crecimiento acumulado;
- volatilidad financiera.

Estas variables podrían resultar especialmente relevantes porque el interés del proyecto consiste en identificar empresas que estén evolucionando hacia un perfil compatible con el mercado de valores.

## 22.4 Modelo lineal

La regresión logística representa relaciones fundamentalmente lineales entre las características transformadas y la variable objetivo.

Podrían existir combinaciones no lineales entre:

- tamaño;
- liquidez;
- endeudamiento;
- rentabilidad;
- sector;
- crecimiento;

que este modelo no puede representar adecuadamente.

## 22.5 Scores no calibrados

Debido al uso de:

`class_weight="balanced"`

los resultados de `predict_proba()` no deben interpretarse todavía como probabilidades reales.

Por ejemplo, obtener un score de 0,90 no significa que exista un 90 % de probabilidad real de convertirse en emisor.

Por esta razón todavía no utilizamos estos valores directamente como Índice de Afinidad Bursátil.

---

# 23. Consideración sobre disponibilidad temporal de información

En las siguientes etapas también será necesario profundizar el control sobre la disponibilidad real de cada estado financiero.

Aunque la unidad temporal se encuentra definida por año, determinados estados financieros pueden haber sido reportados posteriormente al cierre anual.

Antes de una implementación operativa deberá garantizarse que cada variable utilizada por el modelo habría estado efectivamente disponible en la fecha en que se pretende realizar la predicción.

Esto permitirá reducir el riesgo de incorporar información que no habría estado disponible en un escenario real.

---

# 24. Relación con la necesidad organizacional de la BVQ

El resultado preliminar muestra que la inteligencia artificial puede contribuir al problema de prospección de la BVQ, pero todavía no debe utilizarse como mecanismo automático de decisión.

El uso más adecuado sería como herramienta de apoyo para:

1. analizar un universo amplio de empresas;
2. asignar un nivel de afinidad;
3. generar una lista priorizada;
4. complementar la lista con criterios comerciales y financieros;
5. facilitar el análisis por parte de especialistas de la BVQ.

Por tanto, el objetivo no es que el modelo determine qué empresa debe convertirse en emisor.

Su función sería reducir el universo de análisis y orientar los esfuerzos comerciales hacia empresas con características que justifican un análisis más profundo.

---

# 25. Próximos pasos

A partir de los resultados obtenidos proponemos el siguiente backlog técnico.

## Prioridad 1 — Variables temporales

Construir variables como:

- crecimiento anual de activos;
- crecimiento de patrimonio;
- crecimiento de utilidad;
- variación de endeudamiento;
- variación de liquidez;
- tendencia de dos y tres años;
- estabilidad de resultados;
- crecimiento acumulado.

**Objetivo:** pasar de una fotografía financiera a una representación de la trayectoria empresarial.

---

## Prioridad 2 — Modelos no lineales

Evaluar:

- Random Forest;
- Gradient Boosting;
- CatBoost;
- eventualmente XGBoost.

Estos algoritmos podrían identificar relaciones e interacciones entre variables que la regresión logística no captura.

---

## Prioridad 3 — Redes neuronales

Evaluar una red neuronal multicapa o MLP.

Debido a la limitada cantidad de positivos, será necesario controlar especialmente:

- sobreajuste;
- regularización;
- pesos de clase;
- arquitectura;
- validación temporal.

La red neuronal será comparada con los modelos tabulares y no se asumirá anticipadamente que debe producir el mejor resultado.

---

## Prioridad 4 — Tratamiento del desbalance

Evaluar alternativas como:

- ponderación de clases;
- submuestreo controlado;
- técnicas específicas para eventos poco frecuentes.

Cualquier técnica deberá aplicarse únicamente sobre TRAIN para evitar contaminación entre conjuntos.

---

## Prioridad 5 — Optimización del ranking

El modelo deberá optimizarse considerando principalmente la utilidad comercial.

Las métricas prioritarias serán:

- Precision@50
- Precision@100
- Recall@50
- Recall@100
- Lift@K

Posteriormente podrán analizarse otros valores de K de acuerdo con la capacidad real de gestión comercial de la BVQ.

---

## Prioridad 6 — Nuevas fuentes de información

Después de explotar la información histórica disponible se podrá analizar la incorporación incremental de:

- información corporativa adicional de SCVS;
- información histórica interna de BVQ;
- variables sectoriales;
- indicadores macroeconómicos;
- otras fuentes públicas empresariales.

Cada nueva fuente deberá cumplir una condición fundamental:

**la información debe haber estado disponible antes de la fecha en que se realiza la predicción.**

---

## Prioridad 7 — Calibración

Una vez seleccionado el modelo con mejor capacidad predictiva y de ranking, se deberá evaluar:

- calibración de probabilidades;
- curvas de calibración;
- Brier Score;
- Platt Scaling;
- calibración isotónica.

Solo posteriormente se deberá definir formalmente el:

**Índice de Afinidad Bursátil (IAB).**

---

## Prioridad 8 — Interpretabilidad

Sobre el modelo seleccionado se deberán implementar mecanismos de explicación.

Entre las técnicas a evaluar se encuentra:

**SHAP**

El objetivo será explicar por qué una empresa aparece en determinada posición del ranking y cuáles variables contribuyeron a su resultado.

---

# 26. Evidencias de reproducibilidad

El proyecto se encuentra versionado mediante Git y GitHub.

Entre los principales componentes desarrollados se encuentran:

### Construcción de datos

`src/data/build_scvs_harmonized_dataset.py`

`src/data/build_mvp_labeled_dataset.py`

### Ingeniería de variables

`src/features/build_mvp_features.py`

### Baseline

`src/models/train_logistic_baseline.py`

### Análisis sectorial

`src/evaluation/analyze_sector_stability.py`

### Baseline sin sector

`src/models/train_logistic_no_sector_v2.py`

### Experimento de regularización

`src/models/tune_logistic_regularization_v3.py`

### Figuras

`src/evaluation/generate_baseline_figures.py`

### Análisis de errores

`src/evaluation/analyze_baseline_errors.py`

También se encuentran versionados:

- parámetros de los experimentos;
- métricas agregadas;
- resultados de ranking;
- coeficientes;
- figuras;
- documentación metodológica.

Los datasets originales y los modelos binarios no se almacenan directamente en Git.

---

# 27. Conclusiones preliminares

Los resultados obtenidos permiten concluir preliminarmente que existe señal predictiva en la información financiera histórica para priorizar empresas con potencial de convertirse posteriormente en emisores del mercado de valores.

La regresión logística desarrollada como Baseline v1 alcanza valores elevados de ROC-AUC y genera rankings con niveles de Lift significativamente superiores a una selección aleatoria.

Sin embargo, el problema presenta un desbalance extremo y una reducción del desempeño en períodos posteriores.

El análisis muestra además que utilizar un umbral de clasificación convencional genera una cantidad demasiado elevada de falsos positivos, por lo que la formulación más adecuada para el proyecto es la de un sistema de **priorización de prospectos**.

Los experimentos realizados permitieron comprobar que eliminar la información sectorial reduce el desempeño del ranking y que modificar únicamente la intensidad de regularización tampoco produce una mejora material.

El análisis de errores muestra además que algunos futuros emisores presentan perfiles financieros alejados del patrón predominante aprendido por el modelo, especialmente empresas de menor tamaño o con estructuras financieras atípicas.

Por estas razones, consideramos que el siguiente avance relevante deberá provenir principalmente de la incorporación de variables temporales y de la evaluación de modelos capaces de capturar relaciones no lineales.

En esta etapa, el prototipo demuestra la viabilidad técnica del enfoque y proporciona una primera metodología reproducible para transformar un universo amplio de empresas en una lista priorizada.

No obstante, los resultados todavía deben considerarse preliminares y el sistema no debe utilizarse como mecanismo autónomo de decisión.

Su evolución se orientará a convertirse en una herramienta de apoyo para el análisis y la prospección comercial de la Bolsa de Valores Quito.