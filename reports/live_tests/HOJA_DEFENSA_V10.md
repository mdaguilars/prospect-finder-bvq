# HOJA DE DEFENSA EN VIVO
## Prospect Finder BVQ – v10

**Modelo:** `v10_hgb_financial_c3`
**Configuración:** `C3_CONSERVATIVE`
**TRAIN:** 2012–2018
**TEST:** 2022–2023
**TEST:** 260.445 observaciones / 54 positivos
**Features:** 25
**Principio de uso:** Modelo → Priorización → Especialista → Decisión

---

# Antes de comenzar

Ubicarse en:

`C:\Users\maguilar\OneDrive - Bolsa de Valores de Quito\BVQ\2026\Proyecto IA\prospect-finder-bvq`

Activar el entorno virtual correspondiente y mantener abierta una terminal PowerShell.

No modificar:

- modelo;
- dataset;
- TEST;
- hiperparámetros;
- archivos originales de resultados.

Todas las pruebas generan evidencia únicamente en:

`reports/live_tests/`

---

# P01 – Ranking reproducible

## Ejecutar

`python src\evaluation\evaluate_final_test_v10.py`

La prueba completa de reproducibilidad ya se encuentra documentada en:

`reports/live_tests/P01/`

## Mostrar

`reports/live_tests/P01/ranking_top50.csv`

y, de ser necesario:

- `ranking_run1.csv.gz`
- `ranking_run2.csv.gz`
- `metrics_run1.csv`
- `metrics_run2.csv`

## Resultado obtenido

- Run 1: 260.445 filas
- Run 2: 260.445 filas
- Ranking idéntico: True
- Métricas idénticas: True
- Métricas Top-K idénticas: True

## Qué decir

“Ejecutamos el mismo modelo congelado sobre el mismo conjunto TEST sin modificar datos ni configuración. Las dos ejecuciones produjeron exactamente las mismas 260.445 observaciones, el mismo ranking y las mismas métricas. Esto demuestra reproducibilidad del proceso bajo las mismas condiciones.”

## Estado

**CUMPLE**

---

# P02 – Fuga temporal

## Ejecutar

`python src\evaluation\live_test_p02_temporal_leakage.py`

## Mostrar

`reports/live_tests/P02/p02_temporal_leakage_result.csv`

Opcionalmente:

`reports/live_tests/P02/p02_input_altered.csv`

## Caso

Empresa:

CASO A

Año financiero:

2023

Fecha de decisión:

`2024-05-01`

Dato artificial posterior:

`2024-07-30`

## Resultado obtenido

- Violación temporal detectada: True
- Features congeladas: 25
- Dato futuro pertenece al modelo: False
- Fecha futura pertenece al modelo: False
- Entrada predictora original vs. alterada: idéntica

## Qué decir

“Introdujimos deliberadamente información fechada después del corte de decisión. El ensayo identifica la violación temporal y, al construir la entrada predictora, el modelo continúa recibiendo exclusivamente sus 25 variables congeladas. El dato futuro no modifica la matriz utilizada para generar el score.”

## Si preguntan si esto evita cualquier fuga futura

“No automáticamente. Esta prueba valida el comportamiento del feature set y del control implementado en este ensayo. Si en el futuro se incorporan nuevas fuentes o variables, deberán pasar por las mismas validaciones temporales.”

## Estado

**CUMPLE**

---

# P03 – Datos faltantes y atípicos

## Ejecutar

`python src\evaluation\live_test_p03_missing_outliers.py`

## Mostrar

`reports/live_tests/P03/p03_results.csv`

## Caso faltantes

Score original:

`0.348435641`

Se eliminan 9 variables financieras.

Score resultante:

`0.301758721`

Cambio:

`-13,40 %`

## Caso atípico

Variable:

`fin_ratio_patrimonio_activos`

Valor original:

`0.956894`

P99 TRAIN:

`1.000000`

Valor artificial:

`10.000000`

Score original:

`0.348435641`

Score alterado:

`0.352409192`

Cambio:

`+1,14 %`

## Qué decir

“El objetivo no es que el score permanezca igual, sino verificar que las condiciones anómalas sean identificables y que el modelo no falle silenciosamente. Con nueve variables faltantes el score disminuyó 13,40 %. Ante una razón financiera extrema, el score cambió 1,14 %. En ambos casos obtuvimos una salida finita y documentamos la condición alterada.”

## Precaución

No decir:

“El sistema productivo automáticamente alerta todos los datos atípicos.”

Decir:

“En esta prueba la condición fue detectada y documentada por el procedimiento de validación.”

## Estado

**CUMPLE**

---

# P04 – Robustez ±5 %

## Ejecutar

`python src\evaluation\live_test_p04_small_changes.py`

## Mostrar

`reports/live_tests/P04/p04_results.csv`

## Caso

Empresa:

CASO B

Variable:

`fin_rotacion_activos`

Original:

`6.556447840`

Score original:

`0.122732576`

Ranking:

`73.043`

### -5 %

Score:

`0.122732576`

Ranking:

`73.043`

### +5 %

Score:

`0.122732576`

Ranking:

`73.043`

## Qué decir

“Para esta empresa, modificar ±5 % la rotación de activos no alteró ni el score ni la posición. Esto es compatible con un modelo HistGradientBoosting: una variación pequeña puede permanecer dentro de los mismos umbrales internos de los árboles.”

## Si preguntan si siempre ocurrirá

“No. Es una prueba de estabilidad local para esta observación y esta variable. Otra empresa o variable puede producir una modificación diferente.”

## Estado

**CUMPLE**

---

# P05 – Utilidad Top-K

## Ejecutar

`python src\evaluation\live_test_p05_topk_utility.py`

## Mostrar primero

`reports/live_tests/P05/p05_topk_metrics.csv`

Después:

`reports/live_tests/P05/p05_positive_positions.csv`

## Resultado

TEST:

260.445 empresas

Positivos:

54

### Top 20

0 positivos
Precision@20 = 0
Recall@20 = 0

### Top 50

0 positivos
Precision@50 = 0
Recall@50 = 0

### Top 100

0 positivos
Precision@100 = 0
Recall@100 = 0

Primer positivo conocido:

**posición 165**

Empresa:

**ECUAHIELO S.A.**

## Qué decir

“Este es uno de los resultados más importantes de las pruebas. El modelo presenta capacidad general de ordenamiento, pero en TEST la recuperación temprana es limitada: los primeros 100 lugares no contienen positivos conocidos y el primero aparece en la posición 165.”

“Por esta razón no utilizamos solamente el ROC-AUC para afirmar utilidad comercial. Prospect Finder se plantea como una herramienta de priorización que apoya al especialista, no como un mecanismo automático que decide cuáles empresas deben ser contactadas.”

## Si preguntan por qué no corregimos el modelo

“Porque TEST ya fue abierto. Modificar el modelo a partir de este resultado contaminaría la evaluación final. Cualquier mejora debe corresponder a una futura versión v11 y utilizar un nuevo protocolo de entrenamiento y evaluación.”

## Si preguntan si P05 falló

“La ejecución y cálculo de la prueba cumplen. El resultado identifica una limitación real de desempeño Top-K, que está documentada y no se oculta.”

## Estado

**CUMPLE CON LIMITACIÓN**

---

# P06 – Explicabilidad y tamaño

## Ejecutar

`python src\evaluation\live_test_p06_explainability_bias.py`

## Mostrar

Primero:

`reports/live_tests/P06/p06_shap_empresa_grande.png`

Después:

`reports/live_tests/P06/p06_shap_empresa_pequena.png`

Finalmente:

`reports/live_tests/P06/p06_size_analysis.csv`

## Empresa grande

VENPARGLOBAL S.A.

Activos:

USD 3.684.973,43

Score:

`0.894149556`

Principales SHAP:

- Activos: +0.390341
- Ventas: +0.131237
- Patrimonio: +0.046352

Variables de escala:

`86,41 %` de la influencia SHAP absoluta local.

## Empresa pequeña

COMPAÑIA DE TRANSPORTES TRANSCAMPO S.A.

Activos:

USD 7.772,85

Score:

`0.081387026`

Principales SHAP:

- Activos: -0.059736
- Ventas: -0.024907
- Crecimiento patrimonial: +0.017774

Variables de escala:

`67,29 %` de la influencia SHAP absoluta local.

## Qué decir

“Controlamos el año y el tipo de compañía y comparamos una empresa cercana al percentil 90 de activos con otra cercana al percentil 10.”

“Las variables asociadas con escala tienen una influencia relevante en ambos casos. En la empresa grande, activos y ventas incrementan considerablemente el score; en la pequeña generan contribuciones negativas.”

“Esto no demuestra que el tamaño cause una mayor probabilidad de emisión ni demuestra por sí solo discriminación. SHAP explica el comportamiento de la predicción del modelo, no relaciones causales.”

## Si preguntan si existe sesgo hacia empresas grandes

“Existe evidencia de dependencia predictiva respecto de variables de escala en los casos analizados. Eso justifica monitorear el desempeño por segmentos de tamaño. Con dos casos no sería metodológicamente correcto concluir que existe discriminación sistemática.”

## Estado

**CUMPLE CON OBSERVACIÓN**

---

# Resumen final para cerrar la demostración

“Las seis pruebas fueron ejecutadas sobre el modelo v10 congelado. P01 a P04 no evidenciaron fallos en los controles evaluados. P05 identificó una limitación de recuperación temprana y P06 evidenció una influencia importante de variables asociadas con escala empresarial.”

“Estos resultados no fueron utilizados para reajustar retrospectivamente el modelo. Prospect Finder mantiene su función como sistema de priorización para apoyar el análisis de los especialistas de la Bolsa, bajo el principio:

Modelo → Priorización → Especialista → Decisión.”

---

# Mensajes que debemos evitar

No decir:

- “El score es la probabilidad de que la empresa emita.”
- “0,90 significa 90 % de probabilidad.”
- “El modelo garantiza identificar futuros emisores.”
- “SHAP demuestra causalidad.”
- “El modelo no tiene sesgos.”
- “P05 demuestra alta efectividad comercial.”
- “Las empresas grandes necesariamente deben tener mayor score.”

Sí decir:

- “Score relativo de priorización.”
- “Afinidad dentro del universo analizado.”
- “Herramienta de apoyo.”
- “Asociaciones aprendidas históricamente.”
- “Supervisión humana.”
- “Limitaciones documentadas.”
- “Monitoreo por segmentos.”
- “Una futura mejora corresponde a una nueva versión del modelo.”
