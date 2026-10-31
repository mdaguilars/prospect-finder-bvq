# Índice central de evidencias v10 — Prospect Finder BVQ

Este documento centraliza las principales evidencias técnicas, metodológicas y funcionales de la versión final v10 de Prospect Finder BVQ.

Su objetivo es facilitar la revisión académica y técnica sin duplicar resultados ya documentados en otros artefactos del repositorio.

---

## 1. Modelo final

Modelo seleccionado:

`v10_hgb_financial_c3`

Configuración:

`C3_CONSERVATIVE`

Estado:

**CONGELADO**

Documentación principal:

- `docs/v10_final_candidate_freeze.md`
- `docs/v10_modeling_protocol.md`
- `docs/v10_feature_set_freeze.md`
- `docs/v10_split_freeze.md`

El modelo v10 no fue modificado después de observar el conjunto TEST.

---

## 2. Comparación de familias de modelos

La selección del modelo final consideró Regresión Logística, HistGradientBoosting y MLP bajo validación temporal y backtesting.

Evidencia principal:

- `reports/results/v10/comparison_v10_final_candidates.csv`
- `reports/results/v10/comparison_v10_family_candidates.csv`
- `reports/results/v10/comparison_v10_models.csv`
- `reports/results/v10/comparison_v10_models_backtest_by_fold.csv`
- `reports/results/v10/comparison_v10_models_ranking_by_fold.csv`
- `reports/results/v10/comparison_v10_final_candidates_metadata.json`

El candidato HGB financiero C3 fue seleccionado por su mejor equilibrio entre ranking, desempeño temporal y estabilidad en backtesting.

---

## 3. Evaluación final sobre TEST congelado

Protocolo:

- `docs/v10_final_test_protocol.md`

Resultados:

- `docs/v10_final_test_results.md`
- `reports/results/v10/final_test_v10_metrics.csv`
- `reports/results/v10/final_test_v10_ranking_metrics.csv`
- `reports/results/v10/final_test_v10_year_metrics.csv`
- `reports/results/v10/final_test_v10_year_ranking_metrics.csv`
- `reports/results/v10/final_test_v10_ranking.csv.gz`
- `reports/results/v10/final_test_v10_metadata.json`

Resultados globales principales:

- PR-AUC TEST: `0.007468801`
- ROC-AUC TEST: `0.934603901`
- positivos TEST: `54`
- primer positivo: posición `165`

La interpretación mantiene visible que un ROC-AUC elevado no implica necesariamente recuperación temprana alta en Top-K.

---

## 4. Evaluación Top-K y escenario operativo

La recuperación temprana presenta limitaciones en K pequeños.

Se incorporó una evaluación adicional de capacidad operativa sin modificar ni reentrenar el modelo:

- `reports/results/v10/final_test_v10_operational_k.csv`

Escenario de referencia propuesto:

- K=2.000 empresas/año
- aproximadamente 167 empresas/mes
- Recall 2022: 62,50 %
- Recall 2023: 50,00 %

Escenario ampliado:

- K=5.000 empresas/año
- aproximadamente 417 empresas/mes
- Recall 2022: 81,25 %
- Recall 2023: 77,27 %

K=2.000 es una propuesta de referencia y no constituye todavía un umbral formalmente aprobado por la BVQ.

---

## 5. Pruebas finales P01–P06

Acta principal:

- `reports/live_tests/ACTA_PRUEBAS_V10.md`

Hoja de defensa:

- `reports/live_tests/HOJA_DEFENSA_V10.md`

Resultado consolidado:

| Prueba | Estado |
|---|---|
| P01 — Consistencia y reproducibilidad | CUMPLE |
| P02 — Fuga temporal | CUMPLE |
| P03 — Faltantes y valores atípicos | CUMPLE |
| P04 — Robustez ±5 % | CUMPLE |
| P05 — Utilidad Top-K | CUMPLE CON LIMITACIÓN |
| P06 — Explicabilidad y escala | CUMPLE CON OBSERVACIÓN |

Evidencias:

- `reports/live_tests/P01/`
- `reports/live_tests/P02/`
- `reports/live_tests/P03/`
- `reports/live_tests/P04/`
- `reports/live_tests/P05/`
- `reports/live_tests/P06/`

Conclusión correcta:

**P01–P04 no evidenciaron fallos en los controles evaluados; P05 identificó una limitación en recuperación temprana Top-K y P06 evidenció influencia relevante de variables asociadas a escala.**

No debe resumirse como “6/6 sin observaciones”.

---

## 6. Explicabilidad

Documentación:

- `docs/v10_explainability_shap_lime.md`

Método principal:

`PermutationExplainer`

Método complementario:

`LIME`

P06 evidenció influencia relevante de variables asociadas a escala empresarial en los casos analizados.

Este resultado no constituye por sí solo evidencia de discriminación o inequidad.

---

## 7. Pruebas funcionales del producto

Documento:

- `docs/v10_functional_test_matrix.md`

Resultado:

**10 de 10 pruebas funcionales aprobadas**

Flujo evaluado:

`PostgreSQL → FastAPI → React → usuario`

Explicabilidad:

`modelo v10 congelado → SHAP → FastAPI → React → usuario`

Suites automáticas verificadas:

- backend: `12 passed`
- frontend: `4 passed`

---

## 8. Validación con especialistas BVQ

Documento:

- `docs/v10_specialist_validation.md`

Resultados principales:

- participantes: `4`
- promedio global Q04–Q28: `4,82 / 5`
- experiencia general: `5,00 / 5`
- utilidad para prospección: `4,75 / 5`
- información suficiente para decidir revisión adicional: `100 %`
- revisaría con mayor profundidad una empresa prioritaria: `100 %`
- recomendaría utilizar la herramienta: `100 %`

La validación mide comprensión, utilidad funcional y utilidad comercial percibida.

No constituye medición de impacto comercial real ni prueba estadística generalizable.

---

## 9. Diseño y arquitectura de solución

Documentación:

- `docs/v10_solution_architecture.md`
- `docs/v10_operational_product_design.md`
- `docs/entorno_tecnico.md`

Principio de diseño:

`Modelo → Priorización → Explicación → Especialista → Decisión`

El score representa prioridad relativa y no una probabilidad calibrada, calificación financiera o decisión automatizada.

---

## 10. Demo reproducible para evaluadores

Ruta:

- `evaluator_demo/README.md`

La demo pública permite revisar el flujo funcional sin publicar información institucional privada ni el artefacto final privado del modelo.

Incluye:

- PostgreSQL aislado;
- datos sintéticos;
- API FastAPI;
- frontend React;
- ranking sintético;
- comparables sintéticos;
- explicación local identificada explícitamente como sintética.

La demo no:

- reentrena v10;
- modifica TEST;
- modifica métricas académicas;
- sustituye los resultados reales del modelo.

---

## 11. Reproducibilidad y trazabilidad

Commits relevantes:

- `c6389a0` — demo reproducible para evaluadores sin artefactos privados
- `b6d6c46` — evaluación operativa Top-K sobre TEST congelado

El commit y tag definitivos de cierre se registrarán una vez completada la sincronización final de todas las evidencias.

---

## 12. Regla de integridad metodológica

La versión v10 permanece congelada.

Después de observar TEST no se modificaron retrospectivamente:

- modelo;
- Feature Set;
- target;
- hiperparámetros;
- split temporal;
- ranking TEST;
- resultados TEST.

Cualquier mejora predictiva posterior debe desarrollarse como una nueva versión, por ejemplo v11.

