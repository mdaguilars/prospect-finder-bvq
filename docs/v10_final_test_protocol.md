# Prospect Finder BVQ
## Protocolo de evaluación final TEST v10

**Estado:** DEFINIDO ANTES DE ABRIR TEST  
**Versión:** v10  
**Modelo congelado:** `v10_hgb_financial_c3`  
**Familia:** `HistGradientBoostingClassifier`  
**Configuración:** `C3_CONSERVATIVE`  
**TEST:** 2022–2023  

---

## 1. Propósito

Este documento define el protocolo que se utilizará para realizar la evaluación final de generalización de Prospect Finder BVQ v10.

El protocolo queda establecido y versionado antes de cargar o evaluar el conjunto TEST 2022–2023.

Su propósito es evitar que los resultados obtenidos en TEST influyan en:

- la selección del algoritmo;
- la selección de variables;
- el ajuste de hiperparámetros;
- el diseño del preprocesamiento;
- la elección de métricas;
- la definición del Top K;
- la modificación retrospectiva del modelo.

El modelo que será evaluado ya fue seleccionado y congelado previamente en:

`docs/v10_final_candidate_freeze.md`

---

## 2. Modelo que será evaluado

El único modelo que será evaluado sobre TEST es:

`v10_hgb_financial_c3`

| Característica | Configuración |
|---|---|
| Algoritmo | `HistGradientBoostingClassifier` |
| Variante | Financiera |
| Configuración | `C3_CONSERVATIVE` |
| Variables físicas | 25 |
| Target | `TARGET_24M` |
| Horizonte | 24 meses |
| Provincia utilizada | No |
| Random state | 42 |

No se realizará una comparación de múltiples modelos sobre TEST.

---

## 3. Configuración congelada

El modelo utilizará exactamente la configuración previamente seleccionada:

```python
HistGradientBoostingClassifier(
    loss="log_loss",
    learning_rate=0.03,
    max_iter=250,
    max_leaf_nodes=5,
    max_depth=2,
    min_samples_leaf=200,
    l2_regularization=3.0,
    early_stopping=False,
    random_state=42,
    class_weight="balanced",
    categorical_features="from_dtype",
)
```

Ningún hiperparámetro podrá ser modificado después de observar los resultados de TEST.

---

## 4. Variables congeladas

### 4.1. Variables numéricas core

1. `activos_final`
2. `patrimonio_final`
3. `bi_ingresos_ventas`
4. `bi_n_empleados`
5. `activos_final_t1`
6. `patrimonio_final_t1`
7. `bi_ingresos_ventas_t1`
8. `bi_n_empleados_t1`

### 4.2. Variables booleanas core

1. `TIENE_T_MENOS_1`
2. `flag_activos_negativos`
3. `flag_ventas_negativas`
4. `flag_empleados_fijo`
5. `flag_empleados_salto_temporal`
6. `flag_empleados_anomalia_total`

### 4.3. Variable categórica

1. `tipo_compania`

### 4.4. Variables financieras numéricas

1. `fin_ratio_patrimonio_activos`
2. `fin_roa`
3. `fin_margen_neto`
4. `fin_rotacion_activos`
5. `fin_roe`
6. `fin_crecimiento_activos`
7. `fin_crecimiento_patrimonio`
8. `fin_crecimiento_ventas`
9. `fin_crecimiento_empleados`

### 4.5. Variable financiera booleana

1. `flag_patrimonio_no_positivo`

La variable `provincia` permanece excluida.

---

## 5. Dataset congelado

La evaluación utilizará:

`data/processed/v10_features_financial_2012_2023.csv.gz`

La construcción de las variables financieras ya fue realizada antes de abrir TEST.

Las fórmulas utilizadas para generar dichas variables fueron definidas previamente y no dependen de estadísticas aprendidas desde TEST.

---

## 6. Esquema temporal

El protocolo completo de la versión v10 es:

| Conjunto | Periodo | Observaciones | Positivos | Uso |
|---|---:|---:|---:|---|
| TRAIN | 2012–2018 | 470.722 | 407 | Entrenamiento final |
| EMBARGO 1 | 2019 | 91.934 | 34 | Excluido |
| VALIDATION | 2020 | 98.471 | 34 | Desarrollo y selección previa |
| EMBARGO 2 | 2021 | 109.099 | 39 | Excluido |
| TEST | 2022–2023 | 260.445 | 54 | Evaluación final |

---

## 7. Datos utilizados para el entrenamiento final

El modelo que será evaluado en TEST se entrenará exclusivamente utilizando:

**TRAIN 2012–2018**

Total:

- **470.722 observaciones**
- **407 positivos**

VALIDATION 2020 no será incorporado al entrenamiento final de la versión v10.

Esta decisión mantiene la comparabilidad directa entre el candidato congelado y el modelo que será evaluado en TEST.

Los años de embargo permanecen excluidos:

- 2019;
- 2021.

---

## 8. Tratamiento de VALIDATION

VALIDATION 2020 fue utilizado durante la fase de desarrollo para:

- comparar familias de modelos;
- evaluar variantes;
- apoyar la selección de hiperparámetros;
- analizar comportamiento fuera de TRAIN.

Después del congelamiento del candidato final, VALIDATION no será utilizado para reentrenar el modelo v10.

Esto evita modificar el conjunto de entrenamiento después de haber realizado la selección del candidato.

---

## 9. Tratamiento de TEST

TEST comprende los años:

**2022–2023**

Total:

- **260.445 observaciones**
- **54 positivos**

TEST será utilizado una única vez para obtener la evaluación final de generalización de la versión v10.

El script de evaluación deberá cargar:

- TRAIN;
- TEST.

No deberá cargar VALIDATION ni los conjuntos de embargo para ajustar el modelo.

---

## 10. Preprocesamiento del candidato HGB

El modelo HGB utilizará las variables financieras en su forma derivada original.

No se aplicará:

- `StandardScaler`;
- normalización;
- capping P01–P99;
- imputación por mediana para las variables numéricas.

Los valores faltantes se conservarán para ser manejados por `HistGradientBoostingClassifier` cuando corresponda.

La variable categórica `tipo_compania` deberá mantener el tratamiento compatible con el utilizado durante los experimentos HGB v10.

Las decisiones de preprocesamiento no podrán modificarse después de observar TEST.

---

## 11. Métrica principal

La métrica principal de evaluación será:

**PR-AUC — Area Under the Precision-Recall Curve**

Esta métrica se mantiene como principal debido al fuerte desbalance del problema.

El número de empresas que posteriormente se convierten en emisores representa una proporción extremadamente pequeña respecto del universo total de compañías.

Por esta razón, ROC-AUC será utilizada como métrica complementaria y no como criterio principal.

---

## 12. Métricas de ranking

Además de PR-AUC, se calcularán métricas específicas para el objetivo operativo de Prospect Finder.

Se utilizarán los siguientes cortes previamente definidos:

- Top 50;
- Top 100;
- Top 200.

Para cada Top K se calculará:

- positivos encontrados;
- Precision@K;
- Recall@K;
- Lift@K.

No se agregarán nuevos valores de K después de observar los resultados de TEST con el propósito de presentar un resultado más favorable.

---

## 13. Interpretación de Top K

Las empresas serán ordenadas de mayor a menor según el score generado por el modelo.

### Top 50

Representa las 50 empresas con mayor score.

### Top 100

Representa las 100 empresas con mayor score.

### Top 200

Representa las 200 empresas con mayor score.

El objetivo es medir cuánto logra concentrar el modelo los futuros emisores dentro de listas manejables para un proceso comercial.

---

## 14. Precision@K

Precision@K responde:

> De las empresas que el modelo colocó dentro del Top K, ¿qué proporción terminó convirtiéndose en emisor dentro del horizonte definido?

Por ejemplo, si dentro de un Top 100 existen 5 positivos:

`Precision@100 = 5 / 100 = 5 %`

---

## 15. Recall@K

Recall@K responde:

> De todos los futuros emisores existentes en TEST, ¿qué proporción fue encontrada dentro del Top K?

Por ejemplo, si TEST contiene 54 positivos y el Top 100 encuentra 5:

`Recall@100 = 5 / 54`

---

## 16. Lift@K

Lift@K mide cuánto mejora el modelo frente a una selección aleatoria de empresas.

Conceptualmente:

`Lift@K = Precision@K / prevalencia`

Un Lift@100 de 20 significaría que la concentración de positivos dentro del Top 100 es aproximadamente 20 veces superior a la que se esperaría mediante selección aleatoria.

El Lift es especialmente relevante para Prospect Finder porque permite medir la eficiencia de la priorización comercial.

---

## 17. ROC-AUC

También se calculará:

**ROC-AUC**

Esta métrica se conservará como referencia complementaria para medir la capacidad general de ordenamiento entre clases.

Debido al fuerte desbalance del target, no sustituirá a PR-AUC ni a las métricas Top K como criterios principales de interpretación.

---

## 18. Métricas que se reportarán

La evaluación final deberá generar como mínimo:

| Grupo | Métrica |
|---|---|
| General | PR-AUC |
| General | ROC-AUC |
| Top 50 | Positivos encontrados |
| Top 50 | Precision@50 |
| Top 50 | Recall@50 |
| Top 50 | Lift@50 |
| Top 100 | Positivos encontrados |
| Top 100 | Precision@100 |
| Top 100 | Recall@100 |
| Top 100 | Lift@100 |
| Top 200 | Positivos encontrados |
| Top 200 | Precision@200 |
| Top 200 | Recall@200 |
| Top 200 | Lift@200 |

---

## 19. Resultados históricos de referencia

Los resultados históricos que fueron conocidos antes de abrir TEST quedan registrados únicamente como referencia.

### Backtest del candidato final

| Métrica | Resultado |
|---|---:|
| PR-AUC media | 0.029487 |
| PR-AUC mediana | 0.030329 |
| PR-AUC std | 0.002709 |
| Lift@50 medio | 94.299911 |
| Lift@100 medio | 76.102088 |
| Lift@200 medio | 68.267274 |
| Positivos acumulados Top 50 | 14 |
| Positivos acumulados Top 100 | 23 |
| Positivos acumulados Top 200 | 40 |

### VALIDATION 2020

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0.008612 |
| ROC-AUC | 0.949422 |
| Positivos Top 50 | 1 |
| Positivos Top 100 | 2 |
| Positivos Top 200 | 2 |

Estas cifras no representan umbrales mínimos que TEST deba alcanzar.

Se utilizarán exclusivamente para contextualizar el comportamiento final.

---

## 20. No se establece un resultado mínimo posterior

Antes de abrir TEST no se establecerá una regla del tipo:

> “Si PR-AUC es menor que X, el modelo se modifica.”

El resultado obtenido será aceptado como evidencia final de generalización de la versión v10, independientemente de si resulta:

- superior;
- similar;
- inferior

a los resultados históricos.

Esto evita utilizar TEST como un nuevo conjunto de desarrollo.

---

## 21. Qué ocurrirá si TEST tiene resultados inferiores

Si TEST presenta una reducción importante de rendimiento, el resultado será documentado como una limitación de generalización de v10.

No se utilizará TEST para:

- volver a C1, C2 o C0;
- seleccionar otro algoritmo;
- eliminar variables;
- agregar variables;
- cambiar hiperparámetros;
- seleccionar otro Top K;
- ajustar el modelo para mejorar las cifras observadas.

Cualquier investigación posterior deberá registrarse como una nueva versión experimental, por ejemplo:

`v11`

y no como una modificación retrospectiva de v10.

---

## 22. Qué ocurrirá si TEST tiene resultados favorables

Si TEST mantiene una concentración relevante de positivos en los primeros puestos del ranking, el resultado respaldará el uso del modelo como:

**herramienta de priorización comercial**

y no como una predicción determinística de emisión.

La interpretación seguirá siendo:

> El modelo identifica empresas que presentan mayor prioridad relativa para ser analizadas por el equipo especializado.

No deberá interpretarse como:

> El modelo asegura que una empresa se convertirá en emisor.

---

## 23. Ranking final de TEST

Además de las métricas agregadas, se generará un ranking de TEST ordenado de mayor a menor score.

El archivo podrá contener como mínimo:

- año;
- identificador de empresa;
- RUC;
- nombre;
- target real;
- score;
- posición en el ranking.

Este ranking será utilizado para verificar los Top 50, Top 100 y Top 200.

---

## 24. Separación por año dentro de TEST

TEST contiene:

- 2022;
- 2023.

La métrica principal oficial se calculará sobre el conjunto TEST definido y congelado.

Adicionalmente, podrán reportarse métricas descriptivas por año para analizar estabilidad temporal.

Estas métricas anuales serán consideradas análisis complementarios y no se utilizarán para modificar el modelo v10.

---

## 25. Reproducibilidad

El script de evaluación final deberá dejar registrados:

- dataset utilizado;
- modelo;
- hiperparámetros;
- variables;
- cantidad de observaciones TRAIN;
- cantidad de positivos TRAIN;
- cantidad de observaciones TEST;
- cantidad de positivos TEST;
- métricas generales;
- métricas Top K;
- fecha de ejecución;
- versiones principales del entorno;
- `random_state`.

Los resultados deberán guardarse dentro de:

`reports/results/v10/`

---

## 26. Archivos esperados de la evaluación final

La ejecución final deberá generar archivos separados para:

1. métricas generales de TEST;
2. métricas Top K;
3. ranking de TEST;
4. métricas descriptivas por año;
5. metadata de la evaluación.

El modelo entrenado podrá conservarse localmente dentro de:

`models/v10/`

de acuerdo con las reglas actuales del repositorio.

---

## 27. Regla de ejecución

La secuencia será:

1. versionar este protocolo;
2. verificar que Git quede limpio;
3. crear el script de evaluación final;
4. revisar su sintaxis;
5. revisar que cargue únicamente los conjuntos autorizados;
6. ejecutar el modelo;
7. observar por primera vez los resultados de TEST;
8. guardar los resultados sin modificar el modelo;
9. versionar los resultados;
10. realizar interpretación, explicabilidad y análisis final.

---

## 28. Estado previo a la evaluación

Al momento de versionar este documento:

**Modelo:** `v10_hgb_financial_c3`  
**Modelo congelado:** SÍ  
**Features congeladas:** SÍ  
**Hiperparámetros congelados:** SÍ  
**Métricas definidas:** SÍ  
**Top K definidos:** SÍ  
**TRAIN definido:** SÍ  
**TEST definido:** SÍ  
**TEST utilizado para selección:** NO  
**TEST evaluado:** NO  

---

## 29. Próximo paso

Después de versionar este protocolo se podrá crear el script de evaluación final de:

`v10_hgb_financial_c3`

utilizando:

**TRAIN 2012–2018**

y evaluando una única vez sobre:

**TEST 2022–2023**

El resultado obtenido constituirá la evaluación final de generalización de Prospect Finder BVQ v10.