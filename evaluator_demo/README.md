# Demo reproducible para evaluador — Prospect Finder BVQ

## Propósito

Esta carpeta proporciona una ruta controlada para revisar el flujo funcional de Prospect Finder BVQ sin publicar datos empresariales reales ni artefactos institucionales restringidos.

La demo no reemplaza la evaluación científica de v10 ni genera nuevas métricas del modelo final.

## Versión académica de referencia

- Modelo final: `v10_hgb_financial_c3`
- Configuración: `C3_CONSERVATIVE`
- Algoritmo: `HistGradientBoostingClassifier`
- Variables predictoras: 25
- TRAIN: 2012–2018
- TEST: 2022–2023
- Tag académico de cierre original: `v1.0-thesis`
- Commit asociado al cierre original: `f48793be9313626bb17c6e13bcd611a580718771`
- Commit demo reproducible: `c6389a0`
- Commit evaluación Top-K operativa: `b6d6c46`
- Commit índice central de evidencias: `2bfe28e`
- Estado actual de referencia: rama `main`

## Alcance de reproducibilidad

El repositorio permite revisar la metodología, scripts, configuración, particiones temporales, métricas congeladas, pruebas automatizadas, pruebas funcionales y evidencias P01–P06.

Los datasets empresariales procesados y el artefacto `.joblib` del modelo final no se distribuyen públicamente. Por ello, la reproducción se divide en dos niveles:

1. **Revisión científica:** metodología, configuración, evidencias y resultados oficiales de v10.
2. **Demo funcional sintética:** flujo de aplicación con datos ficticios, sin recalcular ni sustituir las métricas oficiales.

## Resultados oficiales de TEST

- Observaciones: 260.445
- Positivos: 54
- PR-AUC: 0,007468801
- ROC-AUC: 0,934603901
- Top 50: 0 positivos
- Top 100: 0 positivos
- Top 200: 1 positivo
- Primer positivo: posición 165

Estos valores corresponden a la evaluación oficial de v10 y no deben confundirse con resultados de una demo sintética.

## Principio de uso

`Modelo → Priorización → Explicación → Especialista → Decisión`

El score representa prioridad relativa y no una probabilidad calibrada de emisión.

## Integridad metodológica

La demo sintética no implica reentrenamiento, cambio de hiperparámetros, cambio de variables, modificación del target ni reutilización de TEST para seleccionar mejoras.

Cualquier evolución predictiva posterior deberá identificarse como una nueva versión del modelo.


## Ejecución rápida de la demo

La demo utiliza un entorno aislado del ambiente normal.

### Puertos

- PostgreSQL demo: `5434`
- API demo: `8002`
- Frontend demo: `5174`

### Paso 1 — Base demo

Desde la raíz del repositorio ejecutar:

`docker compose -f evaluator_demo/compose.demo.yaml up -d`

### Paso 2 — Cargar datos sintéticos

`python evaluator_demo/load_demo_data.py`

Resultado esperado: 6 prospectos sintéticos y 4 comparables sintéticos.

### Paso 3 — API demo

`$env:DATABASE_URL="postgresql+psycopg://prospect_demo:prospect_demo@localhost:5434/prospect_finder_demo"`
`$env:EVALUATOR_DEMO_MODE="true"`
`python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8002`

Verificar en: `http://127.0.0.1:8002/api/health`

### Paso 4 — Frontend demo

Desde la carpeta `frontend` ejecutar:

`$env:VITE_API_URL="http://127.0.0.1:8002/api"`
`npm run dev -- --port 5174`

Abrir: `http://localhost:5174/`

La pantalla debe mostrar las 6 empresas sintéticas.

### Separación de ambientes

| Componente | Ambiente normal | Demo evaluador |
|---|---:|---:|
| PostgreSQL | 5432 | 5434 |
| API | 8000 | 8002 |
| Frontend | 5173 | 5174 |
| Base | prospect_finder_bvq | prospect_finder_demo |

La demo no modifica datos, modelo, ranking ni resultados académicos del ambiente normal.

### Validaciones ejecutadas

- Backend: 12 pruebas aprobadas.
- Frontend: 4 pruebas aprobadas.
- Build del frontend: completado correctamente.

La explicación local mostrada en modo demo es sintética y no debe interpretarse como un cálculo SHAP real del artefacto privado del modelo.
