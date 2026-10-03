# Prospect Finder BVQ
## Resultados finales de evaluación TEST v10

**Versión:** v10  
**Modelo evaluado:** `v10_hgb_financial_c3`  
**Configuración:** `C3_CONSERVATIVE`  
**Familia:** `HistGradientBoostingClassifier`  
**TEST:** 2022–2023  
**Estado:** EVALUACIÓN FINAL COMPLETADA  

---

## 1. Propósito

Este documento registra los resultados obtenidos en la evaluación final de generalización de Prospect Finder BVQ v10.

El modelo fue seleccionado, congelado y versionado antes de utilizar TEST.

Los documentos que establecieron previamente esta decisión fueron:

- `docs/v10_final_candidate_freeze.md`
- `docs/v10_final_test_protocol.md`

Los resultados presentados en este documento corresponden a la primera evaluación oficial del candidato congelado sobre TEST 2022–2023.

No se modificó el modelo después de conocer estos resultados.

---

## 2. Modelo evaluado

El único modelo evaluado sobre TEST fue:

`v10_hgb_financial_c3`

| Característica | Configuración |
|---|---|
| Algoritmo | `HistGradientBoostingClassifier` |
| Variante | Financiera |
| Configuración | `C3_CONSERVATIVE` |
| Features físicas | 25 |
| Target | `TARGET_24M` |
| Horizonte | 24 meses |
| Provincia utilizada | No |
| Random state | 42 |

---

## 3. Hiperparámetros utilizados

La evaluación utilizó exactamente la configuración congelada antes de abrir TEST:

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

---

## 4. Conjuntos utilizados

La evaluación final utilizó exclusivamente TRAIN y TEST.

| Conjunto | Periodo | Observaciones | Positivos |
|---|---:|---:|---:|
| TRAIN | 2012–2018 | 470.722 | 407 |
| TEST | 2022–2023 | 260.445 | 54 |

VALIDATION 2020 no fue incorporado al entrenamiento final.

Los años de embargo 2019 y 2021 permanecieron excluidos.

---

## 5. Resultado del entrenamiento final

El modelo fue entrenado utilizando únicamente TRAIN 2012–2018.

| Métrica | Resultado |
|---|---:|
| Observaciones | 470.722 |
| Positivos | 407 |
| PR-AUC | 0.040249 |
| ROC-AUC | 0.952719 |

Estas métricas corresponden al conjunto utilizado para entrenamiento y no representan la capacidad final de generalización del modelo.

La evaluación principal corresponde a TEST.

---

## 6. Resultado oficial de TEST 2022–2023

TEST contiene:

- **260.445 observaciones**
- **54 positivos**
- **Prevalencia: 0.000207337**

Esto equivale aproximadamente a:

**0,0207 % de positivos**

El problema continúa siendo, por tanto, altamente desbalanceado.

### Métricas generales

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0.007469 |
| ROC-AUC | 0.934604 |
| Prevalencia | 0.000207 |

---

## 7. Interpretación de PR-AUC

La PR-AUC obtenida en TEST fue:

**0.007468801**

La prevalencia de positivos en TEST fue:

**0.000207337**

En un problema altamente desbalanceado, una referencia aleatoria para PR-AUC se aproxima a la prevalencia de la clase positiva.

El resultado indica que el modelo conserva una señal predictiva superior a una selección aleatoria.

Sin embargo, esta señal debe analizarse conjuntamente con las métricas de ranking, ya que el objetivo práctico de Prospect Finder es concentrar futuros emisores dentro de listas pequeñas de empresas prioritarias.

---

## 8. Interpretación de ROC-AUC

El modelo obtuvo:

**ROC-AUC = 0.934604**

Este resultado muestra una capacidad general elevada para ordenar observaciones positivas por encima de negativas a través del conjunto completo.

Sin embargo, ROC-AUC no es suficiente para evaluar por sí sola la utilidad comercial del modelo debido al fuerte desbalance existente.

Para Prospect Finder son especialmente importantes los primeros lugares del ranking.

---

## 9. Resultado oficial Top K sobre TEST conjunto

Los resultados obtenidos al ordenar conjuntamente las observaciones de 2022 y 2023 fueron:

| Ranking | Positivos encontrados | Precision | Recall | Lift |
|---|---:|---:|---:|---:|
| Top 50 | 0 | 0,0000 % | 0,0000 % | 0,00 |
| Top 100 | 0 | 0,0000 % | 0,0000 % | 0,00 |
| Top 200 | 1 | 0,5000 % | 1,8519 % | 24,12 |

---

## 10. Lectura del Top 50

Dentro de las 50 empresas con mayor score del TEST conjunto:

**no se encontró ningún futuro emisor.**

Esto implica:

- Positivos: 0
- Precision@50: 0 %
- Recall@50: 0 %
- Lift@50: 0

Por tanto, el modelo no logró concentrar positivos en los primeros 50 lugares del ranking conjunto 2022–2023.

---

## 11. Lectura del Top 100

Dentro de las 100 empresas con mayor score del TEST conjunto:

**no se encontró ningún futuro emisor.**

Esto implica:

- Positivos: 0
- Precision@100: 0 %
- Recall@100: 0 %
- Lift@100: 0

El comportamiento observado históricamente en Top 100 no se reprodujo en el TEST conjunto.

---

## 12. Lectura del Top 200

Dentro de las 200 empresas con mayor score del TEST conjunto:

**se encontró 1 futuro emisor.**

Esto representa:

- Precision@200: **0,5 %**
- Recall@200: **1,85 %**
- Lift@200: **24,12**

El Lift indica que la concentración de positivos dentro del Top 200 fue aproximadamente 24 veces superior a la prevalencia general de TEST.

Sin embargo, en términos absolutos, únicamente uno de los 54 positivos disponibles quedó ubicado dentro de los primeros 200 lugares.

---

## 13. Comparación con resultados anteriores

Antes de abrir TEST, el candidato final había presentado los siguientes resultados históricos.

### Backtest 2015–2018

| Métrica | Resultado |
|---|---:|
| PR-AUC media | 0.029487 |
| PR-AUC mediana | 0.030329 |
| PR-AUC std | 0.002709 |
| Lift@50 medio | 94.299911 |
| Lift@100 medio | 76.102088 |
| Lift@200 medio | 68.267274 |

### VALIDATION 2020

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0.008612 |
| ROC-AUC | 0.949422 |
| Positivos Top 50 | 1 |
| Positivos Top 100 | 2 |
| Positivos Top 200 | 2 |

### TEST 2022–2023

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0.007469 |
| ROC-AUC | 0.934604 |
| Positivos Top 50 | 0 |
| Positivos Top 100 | 0 |
| Positivos Top 200 | 1 |

---

## 14. Principal hallazgo de generalización

El resultado de TEST muestra dos comportamientos simultáneos.

### Señal general

El modelo mantiene:

- PR-AUC superior a la prevalencia;
- ROC-AUC elevado;
- capacidad general de ordenamiento.

### Concentración en primeros puestos

El modelo presenta una reducción importante de efectividad dentro de:

- Top 50;
- Top 100;
- Top 200.

Esto significa que la capacidad general de separar positivos y negativos no se tradujo con la misma intensidad en la concentración de futuros emisores dentro de los primeros lugares del ranking conjunto.

---

## 15. Análisis descriptivo por año

Como análisis complementario previamente autorizado, TEST fue revisado también separando 2022 y 2023.

### Resultados generales

| Año | Observaciones | Positivos | Prevalencia | PR-AUC | ROC-AUC |
|---:|---:|---:|---:|---:|---:|
| 2022 | 123.289 | 32 | 0.000260 | 0.011585 | 0.947530 |
| 2023 | 137.156 | 22 | 0.000160 | 0.004533 | 0.915855 |

Los resultados muestran una diferencia temporal importante entre ambos años.

---

## 16. Ranking de 2022

Cuando 2022 se ordena de manera independiente:

| Ranking | Positivos | Precision | Recall | Lift |
|---|---:|---:|---:|---:|
| Top 50 | 0 | 0,00 % | 0,00 % | 0,00 |
| Top 100 | 1 | 1,00 % | 3,13 % | 38,53 |
| Top 200 | 4 | 2,00 % | 12,50 % | 77,06 |

En 2022 el modelo presentó una concentración significativamente mayor dentro de Top 100 y Top 200 que la observada en el TEST conjunto.

---

## 17. Ranking de 2023

Cuando 2023 se ordena de manera independiente:

| Ranking | Positivos | Precision | Recall | Lift |
|---|---:|---:|---:|---:|
| Top 50 | 0 | 0,00 % | 0,00 % | 0,00 |
| Top 100 | 0 | 0,00 % | 0,00 % | 0,00 |
| Top 200 | 1 | 0,50 % | 4,55 % | 31,17 |

El desempeño de 2023 fue inferior al observado en 2022.

---

## 18. Diferencia entre ranking conjunto y ranking anual

Existe una diferencia importante entre:

- ordenar conjuntamente 2022 y 2023;
- ordenar cada año independientemente.

En el ranking conjunto:

**Top 200 encuentra 1 positivo.**

En rankings independientes:

- Top 200 de 2022 encuentra 4 positivos;
- Top 200 de 2023 encuentra 1 positivo.

Esto no constituye una inconsistencia matemática.

Cuando los años se ordenan separadamente, cada periodo obtiene su propio Top K.

Cuando se ordenan conjuntamente, las empresas de ambos años compiten por las mismas primeras posiciones.

Este comportamiento sugiere que las distribuciones de score pueden variar temporalmente.

El fenómeno deberá estudiarse posteriormente como parte del análisis de estabilidad y drift.

No se utilizará este hallazgo para modificar retrospectivamente el modelo v10.

---

## 19. Comparación 2022 frente a 2023

Los resultados muestran una disminución entre ambos periodos:

### PR-AUC

- 2022: **0.011585**
- 2023: **0.004533**

### ROC-AUC

- 2022: **0.947530**
- 2023: **0.915855**

### Top 200

- 2022: **4 positivos**
- 2023: **1 positivo**

Esta diferencia constituye una señal relevante de posible variación temporal en la relación entre las variables financieras y la probabilidad posterior de emisión.

---

## 20. Qué demostró v10

Los resultados de TEST permiten afirmar que v10 identifica una señal estadística asociada al target.

El modelo:

- obtiene una PR-AUC superior a la prevalencia;
- presenta un ROC-AUC elevado;
- genera rankings con concentración superior a selección aleatoria en determinados cortes y periodos;
- presenta evidencia de variación temporal;
- no mantiene en TEST conjunto la fortaleza de Top K observada durante el backtesting.

---

## 21. Qué no demostró v10

Los resultados no permiten afirmar que:

- el modelo identifica con alta precisión qué empresa será emisora;
- las primeras 50 empresas del ranking contienen necesariamente futuros emisores;
- las primeras 100 empresas contienen necesariamente futuros emisores;
- el rendimiento histórico se mantiene estable en todos los periodos;
- el modelo puede sustituir el análisis especializado;
- el score debe interpretarse como una probabilidad determinística de emisión.

---

## 22. Interpretación de negocio

La interpretación de Prospect Finder debe mantenerse como:

> **Herramienta de priorización y apoyo al análisis comercial.**

No como:

> **Sistema automático para determinar qué empresas se convertirán en emisores.**

La utilidad potencial del modelo se encuentra en combinar:

- señales financieras;
- comportamiento histórico;
- ranking;
- análisis humano especializado.

Los resultados finales muestran que esta utilidad debe ser implementada con controles de estabilidad y seguimiento periódico.

---

## 23. Implicación para el diseño operativo

Los resultados por año sugieren que una implementación productiva debería analizar la conveniencia de generar rankings:

**por periodo de corte**

en lugar de mantener rankings acumulados que mezclen observaciones de diferentes años.

Por ejemplo:

- ranking anual;
- ranking semestral;
- ranking correspondiente a la última información financiera disponible.

Esta hipótesis deberá analizarse en una nueva etapa.

No constituye una modificación de los resultados oficiales de v10.

---

## 24. Posible drift

La diferencia observada entre:

- backtest;
- VALIDATION;
- 2022;
- 2023

justifica realizar posteriormente un análisis específico de:

- cambio en distribución de variables;
- cambio en distribución de scores;
- estabilidad de importancia de variables;
- cambios en prevalencia;
- cobertura de información financiera;
- estabilidad por segmentos;
- posibles cambios estructurales del mercado.

Este análisis tendrá carácter explicativo y no se utilizará para modificar retrospectivamente v10.

---

## 25. Brecha TRAIN–TEST

El modelo obtuvo:

| Conjunto | PR-AUC |
|---|---:|
| TRAIN | 0.040249 |
| TEST | 0.007469 |

La diferencia confirma que el desempeño observado dentro de TRAIN es considerablemente superior al obtenido sobre datos futuros reservados.

Esto refuerza la importancia de haber mantenido TEST completamente separado durante el desarrollo.

---

## 26. Importancia del protocolo utilizado

El resultado obtenido confirma la utilidad metodológica de:

- separar temporalmente TRAIN;
- utilizar años de embargo;
- utilizar VALIDATION para desarrollo;
- realizar backtesting temporal;
- congelar el modelo;
- definir previamente las métricas;
- abrir TEST una única vez.

Sin este protocolo, habría existido el riesgo de continuar modificando el modelo hasta obtener resultados favorables sobre TEST, produciendo una evaluación excesivamente optimista.

---

## 27. Estado de la versión v10

Después de la evaluación final:

**Modelo seleccionado:** `v10_hgb_financial_c3`  
**Modelo congelado:** SÍ  
**TEST abierto:** SÍ  
**TEST evaluado:** SÍ  
**TEST utilizado para selección previa:** NO  
**Resultados finales preservados:** SÍ  
**Reajuste posterior con TEST:** NO  

La versión v10 queda cerrada como experimento de modelado.

---

## 28. Regla posterior a TEST

Los resultados de TEST no serán utilizados para modificar:

- features;
- algoritmo;
- hiperparámetros;
- tratamiento de missing;
- periodo TRAIN;
- Top K;
- configuración C3.

Cualquier nueva investigación deberá identificarse como una versión posterior independiente.

Por ejemplo:

`v11`

---

## 29. Archivos oficiales generados

La evaluación final produjo:

```text
reports/results/v10/final_test_v10_metrics.csv
reports/results/v10/final_test_v10_ranking_metrics.csv
reports/results/v10/final_test_v10_top500.csv
reports/results/v10/final_test_v10_year_metrics.csv
reports/results/v10/final_test_v10_year_ranking_metrics.csv
reports/results/v10/final_test_v10_metadata.json
```

También se generaron localmente:

```text
reports/results/v10/final_test_v10_ranking.csv.gz
models/v10/v10_hgb_financial_c3_final.joblib
```

Estos archivos permanecen sujetos a las reglas de versionamiento definidas en el repositorio.

---

## 30. Commit de preservación de resultados

Los resultados oficiales de TEST fueron preservados en Git antes de iniciar análisis posteriores.

Commit:

`35df876 feat: add v10 final test evaluation`

Esto permite mantener trazabilidad entre:

- congelamiento del candidato;
- protocolo de TEST;
- ejecución;
- resultados finales.

---

## 31. Conclusión de la evaluación final

Prospect Finder BVQ v10 demuestra que existe una señal predictiva capaz de diferenciar empresas con distinta prioridad relativa.

Sin embargo, la evaluación final muestra que la fortaleza observada durante el backtesting no se mantuvo completamente en los primeros lugares del ranking del TEST conjunto 2022–2023.

El resultado oficial fue:

- **PR-AUC: 0.007469**
- **ROC-AUC: 0.934604**
- **Top 50: 0 positivos**
- **Top 100: 0 positivos**
- **Top 200: 1 positivo**
- **Lift@200: 24,12**

El comportamiento por año muestra además una diferencia relevante entre 2022 y 2023.

Por tanto, v10 debe interpretarse como una primera versión técnicamente validada de un motor de priorización, con evidencia de señal predictiva pero también con limitaciones claras de estabilidad temporal y concentración en los primeros lugares del ranking.

La siguiente etapa del proyecto deberá centrarse en comprender el comportamiento del modelo y establecer las condiciones necesarias para su utilización responsable.

---

## 32. Próximas etapas

Después del cierre de v10 se realizarán análisis independientes de:

1. explicabilidad del modelo;
2. importancia de variables;
3. estabilidad temporal;
4. posible concept drift o data drift;
5. comportamiento del score entre años;
6. sesgos y riesgos;
7. criterios operativos de uso;
8. diseño del ranking comercial;
9. monitoreo;
10. documentación académica y presentación final.

Estas actividades no modificarán retrospectivamente los resultados oficiales obtenidos por v10.