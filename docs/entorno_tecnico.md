# Entorno técnico del proyecto

## 1. Entorno de desarrollo

Prospect Finder BVQ se desarrolla en un entorno local Windows de 64 bits utilizando herramientas de ingeniería de datos, aprendizaje automático, desarrollo web, bases de datos, contenerización, pruebas automatizadas y control de versiones.

El entorno está orientado a mantener trazabilidad, reproducibilidad y separación entre las capas de datos, modelado, producto analítico, persistencia, API e interfaz web.

| Componente | Herramienta | Versión / configuración | Uso |
|---|---|---|---|
| Sistema operativo | Windows | 64 bits | Plataforma principal de desarrollo |
| Lenguaje principal | Python | 3.13.7 | Procesamiento, modelado, análisis y backend |
| Entorno de desarrollo | Visual Studio Code | 1.136.1 x64 | Desarrollo y edición del código |
| Terminal | PowerShell | 7.6.5 | Ejecución de comandos |
| Control de versiones | Git | 2.55.0.windows.3 | Trazabilidad de cambios |
| Repositorio remoto | GitHub | rama `main` | Respaldo y sincronización del código |
| Gestor de paquetes Python | pip | 26.2.1 | Administración de dependencias Python |
| Entorno virtual | Python venv | `.venv` | Aislamiento de dependencias |
| Node.js | Node.js | 24.19.0 | Entorno de ejecución del frontend |
| npm | npm | 11.17.0 | Administración de dependencias frontend |
| React | React | 19.3.0 | Construcción de la interfaz web |
| React DOM | React DOM | 19.3.0 | Renderizado del frontend |
| Vite | Vite | 8.3.2 | Desarrollo y construcción del frontend |
| TypeScript | TypeScript | 6.0.3 | Tipado estático del frontend |
| Oxlint | Oxlint | 1.86.0 | Validación estática del código frontend |
| Docker Desktop | Docker Desktop | 4.93.0 | Contenerización y servicios locales |
| Docker Engine / CLI | Docker | 29.8.1 | Ejecución de contenedores |
| WSL | Ubuntu sobre WSL2 | WSL 2 | Backend Linux utilizado por Docker Desktop |
| Base de datos | PostgreSQL | 17 Alpine | Persistencia del producto operacional |

---

## 2. Librerías principales de Python

Las versiones exactas instaladas se encuentran registradas en:

- `requirements.txt`
- `requirements-lock.txt`

Las principales dependencias utilizadas actualmente son:

| Librería | Versión verificada | Uso dentro del proyecto |
|---|---:|---|
| pandas | 3.0.5 | Manipulación, integración y transformación de datos |
| NumPy | 2.5.3 | Operaciones numéricas |
| openpyxl | 3.1.5 | Lectura y escritura de archivos Excel |
| Matplotlib | 3.11.1 | Visualización de resultados |
| scikit-learn | 1.9.1 | Modelado, evaluación y modelo final v10 |
| SciPy | 1.18.1 | Funciones científicas |
| joblib | 1.6.0 | Serialización y carga del modelo final |
| FastAPI | 0.142.2 | API REST del prototipo |
| Uvicorn | 0.54.0 | Servidor ASGI para FastAPI |
| SQLAlchemy | 2.1.3 | Capa ORM y acceso a PostgreSQL |
| psycopg | 3.3.6 | Driver PostgreSQL para Python |
| psycopg-binary | 3.3.6 | Distribución binaria del driver PostgreSQL |
| Alembic | 1.20.0 | Soporte para migraciones de base de datos |
| python-dotenv | 1.2.4 | Variables de configuración del entorno |
| Pydantic | 2.13.5 | Validación y configuración utilizada por FastAPI |
| Starlette | 1.7.0 | Componentes ASGI utilizados por FastAPI |
| pytest | 9.1.1 | Pruebas automáticas |
| SHAP | versión registrada en `requirements-lock.txt` | Interpretabilidad global y local |
| LIME | versión registrada en `requirements-lock.txt` | Interpretabilidad local complementaria |
| Jupyter | 1.1.1 | Experimentación interactiva |
| ipykernel | 7.3.0 | Kernel Python para notebooks |
| notebook | 7.6.2 | Ejecución de notebooks |

Las dependencias transitivas completas también se conservan en `requirements-lock.txt`.

No se deben escribir manualmente versiones de librerías Python no verificadas. El archivo de bloqueo constituye la referencia técnica para reconstruir el entorno.

---

## 3. Dependencias principales del frontend

El frontend dispone de su propio control de dependencias mediante:

- `frontend/package.json`
- `frontend/package-lock.json`

Las versiones efectivamente instaladas y verificadas son:

| Librería / herramienta | Versión instalada | Uso |
|---|---:|---|
| React | 19.3.0 | Construcción de componentes y estado de la interfaz |
| React DOM | 19.3.0 | Renderizado del frontend |
| Lucide React | 1.52.0 | Iconografía de la aplicación |
| React Router DOM | 7.18.4 | Soporte para navegación y crecimiento posterior de rutas |
| Recharts | 3.10.1 | Soporte para visualizaciones gráficas posteriores |
| TypeScript | 6.0.3 | Tipado estático |
| Vite | 8.3.2 | Servidor de desarrollo y build |
| @vitejs/plugin-react | 6.1.1 | Integración de React con Vite |
| Oxlint | 1.86.0 | Validación estática del código |
| @types/node | 24.19.1 | Tipos TypeScript para Node.js |
| @types/react | 19.3.0 | Tipos TypeScript para React |
| @types/react-dom | 19.3.0 | Tipos TypeScript para React DOM |
| Vitest | 5.0.3 | Ejecución de pruebas automatizadas del frontend |
| Testing Library React | 16.3.3 | Pruebas de componentes y comportamiento de la interfaz |
| Testing Library jest-dom | 7.0.1 | Matchers adicionales para validaciones sobre el DOM |
| Testing Library user-event | 14.6.7 | Simulación de interacción de usuario |
| jsdom | 30.1.2 | Entorno DOM para ejecutar pruebas de React fuera del navegador |

`Lucide React` se utiliza actualmente en la interfaz.

`React Router DOM` y `Recharts` se encuentran instalados y disponibles para la evolución del prototipo, aunque la primera versión funcional de la pantalla opera actualmente como una vista principal tipo SPA y no requiere todavía navegación compleja ni gráficos construidos con Recharts.

El archivo `package-lock.json` constituye la referencia para reproducir las versiones exactas instaladas del frontend.

---

## 4. Entorno virtual de Python

El proyecto utiliza un entorno virtual denominado:

`.venv`

El intérprete correspondiente es:

`prospect-finder-bvq\.venv\Scripts\python.exe`

La activación desde PowerShell se realiza mediante:

`.\.venv\Scripts\Activate.ps1`

Después de la activación, el prompt debe mostrar:

`(.venv)`

El entorno virtual permite:

- aislar dependencias;
- conservar versiones específicas;
- evitar conflictos con otras instalaciones;
- ejecutar pruebas en un entorno controlado;
- mejorar la reproducibilidad.

---

## 5. Entorno de notebooks

Jupyter se mantiene disponible para análisis exploratorio y validaciones.

El notebook inicial:

`notebooks/00_validacion_entorno.ipynb`

fue utilizado para comprobar el funcionamiento del entorno de Python y las principales librerías.

El desarrollo principal del proyecto se realiza actualmente mediante scripts Python versionados, lo cual facilita la reproducción del pipeline y la trazabilidad de cada etapa.

---

## 6. Estructura actual del proyecto

La estructura técnica principal es:

    prospect-finder-bvq/
    │
    ├── config/
    │
    ├── data/
    │   ├── raw/
    │   ├── interim/
    │   └── processed/
    │
    ├── docs/
    │   ├── v10_functional_test_matrix.md
    │   └── ...
    │
    ├── frontend/
    │   ├── public/
    │   ├── src/
    │   │   ├── assets/
    │   │   ├── components/
    │   │   ├── pages/
    │   │   ├── services/
    │   │   │   └── api.ts
    │   │   ├── test/
    │   │   │   ├── App.test.tsx
    │   │   │   └── setup.ts
    │   │   ├── types/
    │   │   │   ├── catalog.ts
    │   │   │   ├── explainability.ts
    │   │   │   └── prospect.ts
    │   │   ├── App.css
    │   │   ├── App.tsx
    │   │   ├── index.css
    │   │   └── main.tsx
    │   ├── index.html
    │   ├── package.json
    │   ├── package-lock.json
    │   ├── tsconfig.app.json
    │   ├── tsconfig.json
    │   ├── tsconfig.node.json
    │   └── vite.config.ts
    │
    ├── models/
    │   └── v10/
    │
    ├── notebooks/
    │
    ├── reports/
    │   ├── figures/
    │   └── results/
    │       └── v10/
    │
    ├── src/
    │   ├── analysis/
    │   ├── api/
    │   │   ├── core/
    │   │   ├── models/
    │   │   ├── routers/
    │   │   └── services/
    │   ├── data/
    │   ├── evaluation/
    │   ├── features/
    │   ├── models/
    │   └── product/
    │
    ├── tests/
    │   └── api/
    │
    ├── compose.yaml
    ├── requirements.txt
    ├── requirements-lock.txt
    ├── README.md
    └── .gitignore

Las carpetas `frontend/src/components/` y `frontend/src/pages/` se encuentran preparadas para la modularización progresiva de la interfaz.

La primera versión funcional se mantiene principalmente en `App.tsx` mientras se valida la experiencia de usuario antes de dividir la interfaz en componentes adicionales.

---

## 7. Organización de datos

### 7.1 `data/raw`

Contiene las fuentes originales utilizadas durante el proyecto.

Los archivos originales se conservan sin modificaciones.

Los datos sensibles o de gran tamaño no se almacenan directamente en Git.

### 7.2 `data/interim`

Contiene datasets generados durante etapas intermedias de:

- homologación;
- limpieza;
- integración;
- validación;
- preparación temporal.

### 7.3 `data/processed`

Contiene datasets preparados para modelado y producto.

Entre los principales artefactos de la versión v10 se encuentran:

`data/processed/v10_base_integrated_2012_2023.csv.gz`

`data/processed/v10_features_core_2012_2023.csv.gz`

`data/processed/v10_features_financial_2012_2023.csv.gz`

También se generan localmente los datasets operacionales:

`data/processed/v10_operational_ranking_2024_05_01.csv.gz`

`data/processed/v10_issuer_similarity_summary_2024_05_01.csv.gz`

`data/processed/v10_issuer_similarity_matches_2024_05_01.csv.gz`

Los archivos operacionales contienen información empresarial y no se publican como parte del código fuente.

---

## 8. Componentes de código Python

### 8.1 `src/data`

Contiene scripts relacionados con:

- lectura de fuentes;
- homologación;
- integración;
- construcción de datasets;
- validación de calidad;
- construcción de la variable objetivo.

### 8.2 `src/features`

Contiene los procesos de ingeniería de variables.

El dataset financiero v10 incorpora variables financieras actuales, rezagos temporales, tasas de crecimiento y banderas de calidad.

### 8.3 `src/models`

Contiene scripts de experimentación, entrenamiento y evaluación de modelos.

Los experimentos iniciales se mantienen como evidencia histórica, mientras que el modelo seleccionado para v10 corresponde a una etapa posterior del proyecto.

### 8.4 `src/evaluation`

Contiene procesos de:

- evaluación temporal;
- métricas;
- análisis de ranking;
- análisis de errores;
- validaciones del modelo.

### 8.5 `src/analysis`

Contiene análisis posteriores al cierre del modelo, entre ellos:

- interpretabilidad;
- SHAP;
- LIME;
- sesgos;
- estabilidad;
- análisis de riesgos.

La explicabilidad es post-test y no modifica el modelo final congelado.

### 8.6 `src/product`

Contiene procesos para convertir el modelo analítico en componentes utilizables por el prototipo.

Actualmente incluye:

- generación del ranking operativo;
- construcción del universo prospectable;
- motor de similitud con emisores históricos.

### 8.7 `src/api`

Contiene el backend del prototipo construido con FastAPI.

Se organiza en:

- `core/`: configuración y conexión a base de datos;
- `models/`: modelos ORM;
- `routers/`: endpoints;
- `services/`: servicios de negocio y explicabilidad.

---

## 9. Componentes del frontend

La interfaz web se encuentra en:

`frontend/`

El frontend utiliza React, TypeScript y Vite.

### 9.1 `frontend/src/App.tsx`

Contiene actualmente la vista principal funcional del prototipo.

La interfaz implementada permite:

- visualizar el ranking operativo;
- consultar el universo total de empresas;
- visualizar el número de provincias y tipos de compañía;
- buscar empresas por nombre, RUC o expediente;
- filtrar por provincia;
- filtrar por tipo de compañía;
- navegar por páginas del ranking;
- seleccionar una empresa;
- consultar su ficha empresarial;
- visualizar su Índice de Afinidad Bursátil;
- visualizar su percentil;
- visualizar su posición en el ranking;
- consultar indicadores financieros;
- visualizar emisores históricos comparables;
- solicitar una explicación SHAP bajo demanda;
- diferenciar factores que aumentan o reducen la afinidad.

### 9.2 `frontend/src/services/api.ts`

Centraliza la comunicación entre React y FastAPI.

Actualmente expone funciones para:

- consultar prospectos;
- consultar el detalle de una empresa;
- obtener catálogos;
- obtener importancia SHAP global;
- obtener explicabilidad SHAP individual.

La URL base predeterminada de desarrollo es:

`http://127.0.0.1:8000/api`

Puede modificarse mediante:

`VITE_API_URL`

### 9.3 `frontend/src/types`

Define contratos TypeScript para las respuestas del backend.

Actualmente incluye:

- `prospect.ts`
- `catalog.ts`
- `explainability.ts`

Esta separación reduce el riesgo de inconsistencias entre el contrato de FastAPI y la interfaz.

### 9.4 Diseño visual

La primera versión funcional utiliza una interfaz orientada a gestión comercial y análisis financiero.

Incluye:

- navegación lateral;
- indicadores principales;
- ranking tabular;
- filtros;
- panel lateral de detalle;
- jerarquía visual para priorización;
- representación diferenciada de impactos SHAP positivos y negativos;
- visualización independiente de comparables históricos.

El diseño evita presentar el sistema como una aplicación puramente técnica de inteligencia artificial.

---

## 10. Modelo final v10

El modelo final seleccionado y congelado es:

`v10_hgb_financial_c3`

Configuración:

`C3_CONSERVATIVE`

El artefacto se encuentra en:

`models/v10/v10_hgb_financial_c3_final.joblib`

El algoritmo utilizado es:

`HistGradientBoostingClassifier`

con configuración:

- `learning_rate = 0.03`
- `max_iter = 250`
- `max_leaf_nodes = 5`
- `max_depth = 2`
- `min_samples_leaf = 200`
- `l2_regularization = 3`
- `early_stopping = False`
- `random_state = 42`
- `class_weight = balanced`
- tratamiento categórico nativo mediante scikit-learn.

El modelo utiliza 25 variables.

El `score_afinidad` generado por el modelo se utiliza como indicador de priorización comercial.

No debe interpretarse como una probabilidad calibrada de convertirse en emisor.

En la interfaz este indicador se presenta como:

`Índice de Afinidad Bursátil`

La denominación busca facilitar su interpretación comercial sin alterar su naturaleza metodológica.

---

## 11. División temporal v10

La división temporal congelada actualmente es:

| Conjunto | Período |
|---|---|
| TRAIN | 2012–2018 |
| EMBARGO 1 | 2019 |
| VALIDATION | 2020 |
| EMBARGO 2 | 2021 |
| TEST | 2022–2023 |

Esta división busca reducir riesgo de fuga temporal y representar un escenario de aplicación sobre períodos futuros.

El modelo final fue seleccionado antes de observar los resultados finales de TEST.

Después de la evaluación final de TEST no se realizó reajuste de hiperparámetros.

---

## 12. Ranking operacional

El producto operacional utiliza información financiera correspondiente a:

`ANIO = 2023`

con fecha de decisión:

`2024-05-01`

El ranking operacional contiene:

`137.156 empresas`

Cada empresa dispone, según disponibilidad de datos, de:

- ranking;
- score de afinidad;
- percentil;
- identificación;
- provincia;
- tipo de compañía;
- indicadores financieros;
- calidad de información;
- similitud con emisores históricos.

La generación operacional reproduce exactamente los scores obtenidos por el modelo congelado para el universo correspondiente.

La salida del producto no expone `TARGET_24M`.

Las empresas que se convirtieron posteriormente en emisores no se excluyen utilizando información futura.

---

## 13. Motor de similitud con emisores

El sistema incorpora un componente adicional de similitud empresarial.

Este componente es independiente del score predictivo.

No existe una fórmula ponderada que combine:

- score de afinidad;
- similitud con emisores.

La similitud utiliza siete variables financieras con cobertura suficiente:

- activos;
- patrimonio;
- ingresos por ventas;
- número de empleados;
- relación patrimonio / activos;
- ROA;
- rotación de activos.

Las variables se transforman a percentiles anuales y posteriormente se calcula distancia euclidiana.

La similitud se expresa en una escala de 0 a 100.

Para cada prospecto pueden presentarse hasta cinco emisores históricos comparables.

El universo de referencia utiliza únicamente emisores conocidos hasta la fecha de decisión correspondiente, evitando utilizar información futura.

En la interfaz la similitud se presenta como información complementaria y nunca como sustituto del score de priorización.

---

## 14. PostgreSQL

El producto utiliza PostgreSQL como base de datos operacional.

La instancia local se ejecuta mediante Docker utilizando:

`postgres:17-alpine`

Base de datos de desarrollo:

`prospect_finder_bvq`

La base contiene actualmente tres tablas principales.

### `operational_prospects`

Contiene una fila por empresa del ranking operacional.

Registros cargados:

`137.156`

### `issuer_similarity_summary`

Contiene el resumen de similitud de cada empresa.

Registros cargados:

`137.156`

### `issuer_similarity_matches`

Contiene los emisores históricos comparables de cada prospecto.

Registros cargados:

`656.600`

Total de registros operacionales cargados y validados:

`930.912`

La carga es realizada mediante:

`src/api/load_operational_data.py`

El proceso valida los conteos esperados después de la carga.

---

## 15. Docker

El archivo:

`compose.yaml`

define actualmente el servicio PostgreSQL local.

La imagen utilizada es:

`postgres:17-alpine`

El servicio expone PostgreSQL en:

`localhost:5432`

Docker Desktop utiliza WSL2 como backend Linux.

Las credenciales incluidas actualmente corresponden exclusivamente al ambiente local de desarrollo.

No deben utilizarse como credenciales de producción.

La dockerización completa de FastAPI se considera una etapa posterior del cierre de MLOps.

El servicio PostgreSQL puede iniciarse mediante:

`docker compose up -d postgres`

---

## 16. FastAPI

La API del producto se encuentra en:

`src/api/`

La aplicación principal es:

`src/api/main.py`

El servidor local se inicia mediante:

`python -m uvicorn src.api.main:app --reload`

Dirección local:

`http://127.0.0.1:8000`

Documentación interactiva:

`http://127.0.0.1:8000/docs`

Los principales endpoints implementados son:

### Salud

`GET /api/health`

Verifica:

- disponibilidad de la API;
- conexión con PostgreSQL;
- entorno;
- versión de aplicación.

### Ranking

`GET /api/prospects`

Permite:

- paginación;
- búsqueda;
- filtro por provincia;
- filtro por tipo de compañía;
- score mínimo;
- similitud mínima;
- disponibilidad de comparables.

El orden predeterminado sigue el ranking operativo ascendente.

### Detalle de empresa

`GET /api/prospects/{expediente_key}`

Devuelve:

- identificación;
- posición en ranking;
- score;
- calidad de datos;
- indicadores financieros;
- similitud;
- cinco comparables históricos;
- información del modelo.

### Catálogos

`GET /api/catalogs`

Devuelve:

- provincias;
- tipos de compañía;
- número de empresas por categoría.

Los textos provenientes de las fuentes se normalizan antes de ser entregados a la interfaz.

### Explicabilidad global

`GET /api/explainability/global`

Devuelve la importancia global SHAP calculada durante el análisis post-test.

### Explicabilidad local

`GET /api/explainability/prospects/{expediente_key}`

Genera una explicación SHAP específica para una empresa.

La explicación se calcula bajo demanda.

---

## 17. Explicabilidad SHAP operacional

La técnica principal de interpretabilidad es SHAP.

La metodología seleccionada es:

`SHAP PermutationExplainer`

El background utilizado para la explicación se construye exclusivamente con observaciones de TRAIN.

La explicación local utiliza las mismas 25 variables del modelo final.

Para cada empresa se valida:

`score_modelo ≈ base_value + suma(valores_SHAP)`

En pruebas funcionales se obtuvo un error numérico del orden de:

`10^-15`

lo que confirma la reconstrucción del score dentro de tolerancia numérica.

TreeExplainer fue evaluado como alternativa de rendimiento, pero fue descartado porque no reconstruyó correctamente el score del modelo al tratar la variable categórica nativa.

Por esta razón se conserva `PermutationExplainer`.

El runtime SHAP se inicializa y reutiliza para reducir el costo de solicitudes posteriores.

Durante la ejecución funcional del 4 de octubre de 2026 se verificó además el precalentamiento de SHAP al iniciar FastAPI. El log de arranque mostró:

`Inicializando explicabilidad SHAP...`

`Precalentando SHAP con expediente 1...`

`SHAP inicializado correctamente.`

Por tanto, el entorno funcional validado inicia el runtime de explicabilidad y ejecuta un calentamiento antes de atender las consultas del usuario.

La importancia global SHAP continúa utilizando los resultados post-test previamente validados.

LIME se conserva como técnica complementaria de análisis y evidencia metodológica, pero no constituye actualmente el método principal de explicación operacional del frontend.

En la interfaz cada factor se clasifica como:

- aumenta afinidad;
- reduce afinidad;
- sin impacto.

El signo del valor SHAP indica la dirección del impacto sobre el score respecto al valor base.

Esta explicación no implica causalidad.

---

## 18. API y separación de responsabilidades

La arquitectura mantiene separadas las siguientes capas:

    Fuentes de datos
           │
           ▼
    Pipeline de procesamiento
           │
           ▼
    Dataset de características
           │
           ▼
    Modelo v10 congelado
           │
           ├──────────────► Explicabilidad SHAP
           │
           ▼
    Ranking operacional
           │
           ├──────────────► Similitud con emisores
           │
           ▼
    PostgreSQL
           │
           ▼
    FastAPI
           │
           ▼
    React + TypeScript
           │
           ▼
    Interfaz Prospect Finder BVQ

Esta separación evita que la interfaz acceda directamente a:

- archivos de entrenamiento;
- modelos;
- fuentes originales;
- bases analíticas;
- PostgreSQL.

La API constituye la única capa de acceso utilizada actualmente por el frontend para consultar información del producto.

---

## 19. Pruebas automáticas del backend

El proyecto utiliza:

`pytest 9.1.1`

Las pruebas se encuentran en:

`tests/api/`

Actualmente existen pruebas para:

- health check;
- ranking;
- filtros;
- detalle de empresa;
- comparables;
- catálogos;
- SHAP global;
- integración del servicio de explicabilidad;
- manejo de errores.

La suite actual fue ejecutada mediante:

`python -m pytest "tests\api" -q`

Resultado validado:

`12 passed`

Las advertencias observadas corresponden a avisos de deprecación internos de SHAP/Matplotlib y no afectan el funcionamiento de las pruebas.

Las pruebas de ranking, detalle y catálogos consultan la base PostgreSQL local cargada.

La prueba del endpoint local SHAP utiliza aislamiento de la ejecución pesada mediante `monkeypatch`, mientras que la reconstrucción SHAP real fue validada mediante pruebas funcionales independientes.

---

## 20. Validación técnica y pruebas automatizadas del frontend

El frontend puede iniciarse desde la raíz del repositorio mediante:

`npm --prefix frontend run dev`

Dirección local:

`http://localhost:5173/`

### 20.1 Pruebas automatizadas

El frontend utiliza:

`Vitest 5.0.3`

junto con:

- `@testing-library/react 16.3.3`;
- `@testing-library/jest-dom 7.0.1`;
- `@testing-library/user-event 14.6.7`;
- `jsdom 30.1.2`.

La configuración de pruebas se encuentra integrada en:

`frontend/vite.config.ts`

El entorno de pruebas utiliza:

`jsdom`

y el archivo de preparación:

`frontend/src/test/setup.ts`

realiza la carga de `jest-dom` y la limpieza del DOM después de cada prueba.

Las pruebas principales se encuentran en:

`frontend/src/test/App.test.tsx`

Actualmente validan cuatro comportamientos funcionales de la interfaz:

- carga inicial del ranking y catálogos;
- aplicación de búsqueda desde el formulario;
- apertura del detalle financiero de una empresa;
- consulta y presentación de factores SHAP positivos y negativos.

La suite se ejecuta mediante:

`npm --prefix frontend run test`

Resultado validado:

`1 test file passed`

`4 tests passed`

Las pruebas del frontend aíslan la interfaz mediante mocks del servicio API. Por tanto, no consultan PostgreSQL ni ejecutan SHAP real durante esta suite. Su objetivo es validar el comportamiento de la capa React de forma rápida, controlada y reproducible.

La integración real con FastAPI, PostgreSQL y SHAP se valida adicionalmente mediante las pruebas del backend y las verificaciones funcionales del prototipo.

### 20.2 Build de producción

La construcción para producción se valida mediante:

`npm --prefix frontend run build`

La compilación validada utilizando Vite 8.3.2 produjo:

`1898 modules transformed`

y finalizó correctamente sin errores de TypeScript ni de construcción.

### 20.3 Validación estática

La validación estática se ejecuta mediante:

`npm --prefix frontend run lint`

Resultado validado:

`0 warnings`

`0 errors`

### 20.4 Validación funcional del flujo integrado

La interfaz fue probada funcionalmente contra la API, PostgreSQL y el servicio real de explicabilidad SHAP.

Documento de evidencia:

`docs/v10_functional_test_matrix.md`

Se ejecutaron diez escenarios:

1. carga inicial del ranking;
2. búsqueda de empresa;
3. filtro por provincia;
4. filtro por tipo de compañía;
5. paginación;
6. ficha empresarial;
7. explicabilidad SHAP;
8. emisores históricos comparables;
9. empresa sin similitud suficiente;
10. expediente inexistente.

### Resultado final

`10 de 10 pruebas funcionales aprobadas`

Entre las evidencias verificadas se encuentran:

- universo prospectable de `137.156` empresas;
- `24` provincias;
- `9` tipos de compañía;
- filtro Pichincha con `43.487` resultados;
- filtro Responsabilidad Limitada con `28.972` resultados;
- navegación a `Página 2 de 5.487`;
- ficha de `CUYABENOPETRO S.A.`;
- factores SHAP positivos y negativos;
- cinco emisores históricos comparables;
- manejo de `INFORMACION_INSUFICIENTE` sin crear comparables artificiales;
- respuesta `404` controlada para un expediente inexistente.

Las pruebas funcionales finales quedaron cerradas técnicamente.

No sustituyen la validación formal con al menos dos especialistas de la BVQ.

---

## 21. Funcionamiento actual del frontend

La pantalla principal presenta cuatro áreas funcionales.

### 21.1 Resumen ejecutivo

Presenta:

- universo prospectable;
- mayor índice de afinidad visible;
- número de provincias;
- número de tipos de compañía;
- fecha de decisión.

### 21.2 Ranking operativo

Presenta:

- posición;
- empresa;
- provincia;
- tipo de compañía;
- Índice de Afinidad Bursátil;
- percentil;
- similitud con emisor;
- calidad de datos.

### 21.3 Ficha individual

Al seleccionar una empresa se presenta un panel lateral con:

- nombre;
- RUC;
- provincia;
- ranking;
- Índice de Afinidad Bursátil;
- percentil;
- activos;
- patrimonio;
- ingresos por ventas;
- número de empleados;
- emisores comparables.

### 21.4 Explicabilidad

La explicación SHAP se solicita expresamente mediante la acción:

`Analizar factores`

La interfaz muestra los factores de mayor impacto y diferencia visualmente entre:

- factores que aumentan afinidad;
- factores que reducen afinidad.

El sistema mantiene visible la advertencia de que el Índice de Afinidad Bursátil es una herramienta de priorización y no una probabilidad calibrada.

---

## 22. Alembic

Alembic 1.20.0 se encuentra instalado como dependencia.

Está previsto utilizarlo para formalizar las migraciones de esquema de PostgreSQL.

La inicialización de migraciones todavía no constituye una etapa cerrada del proyecto.

Por esta razón no debe afirmarse todavía que la base se encuentre administrada mediante migraciones Alembic.

---

## 23. Reproducibilidad

La reproducibilidad se apoya actualmente en:

- `.venv`;
- `requirements.txt`;
- `requirements-lock.txt`;
- `frontend/package.json`;
- `frontend/package-lock.json`;
- Git;
- GitHub;
- scripts independientes por etapa;
- modelo final congelado;
- datasets identificados;
- separación temporal congelada;
- documentación metodológica;
- pruebas automáticas;
- PostgreSQL;
- Docker Compose;
- React y TypeScript;
- build reproducible mediante Vite;
- pruebas automatizadas del frontend mediante Vitest y Testing Library;
- matriz de pruebas funcionales finales;
- `random_state = 42` cuando corresponde;
- metadatos de resultados;
- validación de scores operacionales frente al modelo final.

---

## 24. Archivos de dependencias

### Python

`requirements.txt`

Contiene las dependencias necesarias para reconstruir el entorno Python utilizado actualmente.

`requirements-lock.txt`

Contiene el conjunto completo de paquetes y versiones instaladas en el ambiente Python utilizado durante el desarrollo.

Después de incorporar nuevas dependencias Python, ambos archivos deben actualizarse.

### Frontend

`frontend/package.json`

Define las dependencias y scripts del frontend.

`frontend/package-lock.json`

Conserva las versiones exactas resueltas por npm y permite reconstruir el entorno JavaScript de manera consistente.

La instalación reproducible del frontend debe apoyarse en el archivo de bloqueo.

---

## 25. Scripts npm disponibles

Los scripts actualmente definidos son:

### Desarrollo

`npm --prefix frontend run dev`

Inicia el servidor de desarrollo Vite.

### Construcción

`npm --prefix frontend run build`

Ejecuta:

`tsc -b && vite build`

Por tanto, valida primero TypeScript y posteriormente genera el build de producción.

### Lint

`npm --prefix frontend run lint`

Ejecuta Oxlint.

### Pruebas

`npm --prefix frontend run test`

Ejecuta:

`vitest run`

y valida automáticamente los principales comportamientos de la interfaz React mediante Testing Library y `jsdom`.

### Preview

`npm --prefix frontend run preview`

Permite visualizar localmente el build de producción generado.

---

## 26. Control de versiones

El proyecto utiliza Git.

Rama principal:

`main`

El repositorio remoto se aloja en GitHub.

Los commits registran progresivamente:

- preparación de datos;
- experimentos;
- selección de modelo;
- evaluación final;
- explicabilidad;
- análisis de sesgo;
- estabilidad;
- ranking operacional;
- similitud con emisores;
- arquitectura;
- PostgreSQL;
- FastAPI;
- pruebas automáticas;
- frontend React;
- integración del frontend con FastAPI;
- interfaz de ranking;
- detalle empresarial;
- explicabilidad SHAP en interfaz;
- pruebas automatizadas del frontend.

La primera versión funcional del frontend fue incorporada al repositorio mediante el commit:

`20fb2e4 feat: add Prospect Finder frontend`

Las pruebas automatizadas específicas del frontend fueron incorporadas mediante:

`7a50bf6 test: add frontend automated tests`

Ambos cambios fueron sincronizados con la rama remota `main`.

La matriz de pruebas funcionales finales se encuentra preparada para incorporarse en el siguiente commit documental.

El repositorio no debe utilizarse para publicar información empresarial sensible ni datasets operacionales no autorizados.

---

## 27. Información no versionada

Como principio general, no se publican directamente en Git:

- fuentes originales de gran tamaño;
- datasets sensibles;
- datasets intermedios que puedan reconstruirse;
- datasets operacionales con información empresarial;
- credenciales;
- archivos `.env`;
- información interna sensible de la BVQ.

El repositorio prioriza:

- código;
- configuración no sensible;
- documentación;
- resultados agregados;
- protocolos;
- pruebas;
- metadatos;
- evidencia metodológica.

El directorio:

`frontend/node_modules/`

no se versiona.

Los artefactos generados durante el build del frontend tampoco deben utilizarse como sustituto del código fuente versionado.

---

## 28. Seguridad de configuración

Las credenciales de producción no deben almacenarse en el código.

La configuración de FastAPI permite utilizar variables de entorno mediante `python-dotenv`.

Las credenciales existentes en Docker Compose corresponden al entorno local de desarrollo.

Para despliegues posteriores deberá utilizarse configuración externa segura mediante variables de entorno o mecanismos equivalentes.

El frontend dispone de la variable:

`VITE_API_URL`

para definir la dirección de la API sin modificar directamente el código fuente.

No deben almacenarse credenciales ni secretos dentro de variables `VITE_*`, ya que su contenido puede quedar expuesto al navegador.

---

## 29. Flujo técnico general actualizado

El flujo técnico actual es:

1. Obtención de fuentes originales.
2. Homologación e integración.
3. Construcción del dataset empresa-año.
4. Construcción de la variable objetivo.
5. Ingeniería de variables.
6. Congelamiento del conjunto de features.
7. División temporal con períodos de embargo.
8. Entrenamiento y comparación de modelos.
9. Backtesting temporal.
10. Selección del candidato final.
11. Evaluación final sobre TEST.
12. Congelamiento del modelo.
13. Interpretabilidad SHAP y LIME.
14. Análisis de sesgo y riesgos.
15. Análisis de estabilidad.
16. Construcción del ranking operacional.
17. Construcción del motor de similitud con emisores.
18. Persistencia operacional en PostgreSQL.
19. Exposición de servicios mediante FastAPI.
20. Explicabilidad operacional bajo demanda.
21. Pruebas automáticas del backend.
22. Construcción del frontend React.
23. Integración frontend–FastAPI.
24. Incorporación de pruebas automatizadas del frontend.
25. Validación de pruebas, build y lint.
26. Ejecución de pruebas funcionales finales del producto.
27. Validación con al menos dos especialistas de la BVQ.
28. Formalización MLOps.
29. Documentación final de operación y despliegue.

---

## 30. Estado técnico actual

El entorno se encuentra operativo para:

- procesamiento de datos;
- construcción de datasets;
- ingeniería de variables;
- entrenamiento;
- evaluación temporal;
- modelo final congelado;
- generación de ranking;
- comparación con emisores históricos;
- interpretabilidad global;
- interpretabilidad local;
- almacenamiento en PostgreSQL;
- exposición mediante API REST;
- consultas filtradas;
- pruebas automáticas;
- ejecución de PostgreSQL mediante Docker;
- frontend React;
- comunicación React–FastAPI;
- ranking interactivo;
- búsqueda de empresas;
- filtros;
- paginación;
- detalle empresarial;
- visualización de indicadores financieros;
- visualización de emisores comparables;
- explicabilidad SHAP bajo demanda;
- representación de factores positivos y negativos;
- build de producción;
- lint del frontend;
- pruebas automatizadas del frontend;
- pruebas funcionales finales con `10 de 10` escenarios aprobados.

El frontend consume actualmente:

- ranking;
- búsqueda;
- filtros;
- detalle empresarial;
- indicadores financieros;
- comparables históricos;
- catálogos;
- explicabilidad.

El prototipo ya permite recorrer funcionalmente el flujo:

`PostgreSQL → FastAPI → React → usuario`

y:

`modelo congelado → SHAP → FastAPI → React → usuario`

---

## 31. Estado de la interfaz web

La interfaz web ya se encuentra implementada en una primera versión funcional.

No debe considerarse todavía una versión productiva definitiva.

La versión actual permite demostrar los componentes principales exigidos para el prototipo:

- ranking de prospectos;
- indicadores de priorización;
- búsqueda;
- filtros;
- detalle de empresa;
- indicadores financieros;
- emisores históricos comparables;
- factores explicativos.

Quedan disponibles mejoras posteriores de experiencia de usuario, entre ellas:

- modularización adicional de componentes;
- uso de rutas específicas cuando resulte necesario;
- visualizaciones analíticas adicionales;
- utilización de Recharts donde aporte valor;
- presentación más explicativa de los valores originales asociados a cada factor SHAP;
- estados de carga más elaborados;
- manejo visual más explícito de errores.

Las pruebas automatizadas específicas del frontend ya se encuentran implementadas y validadas con Vitest y Testing Library.

Las pruebas funcionales finales del producto también se encuentran cerradas con:

`10 de 10 pruebas aprobadas`

según:

`docs/v10_functional_test_matrix.md`

Estas mejoras no afectan el funcionamiento básico actualmente validado.

---

## 32. Componentes pendientes

Los principales componentes técnicos que todavía deben completarse son:

- validación real con al menos dos especialistas de la BVQ;
- registro estructurado de los resultados de dicha validación;
- dockerización completa de FastAPI;
- migraciones formales con Alembic;
- integración formal de DVC;
- integración formal de MLflow;
- monitoreo operacional;
- documentación final de despliegue;
- documentación final de operación.

La interfaz web ya no se considera un componente pendiente.

Las mejoras visuales y de experiencia de usuario pueden continuar de manera incremental, pero la primera versión funcional del frontend ya se encuentra implementada y validada técnicamente.

---

## 33. Principio de trazabilidad

Cada resultado presentado por Prospect Finder BVQ debe poder relacionarse con:

- la fuente de datos utilizada;
- el año de información;
- las variables empleadas;
- el modelo congelado;
- la configuración del modelo;
- la fecha de decisión;
- el ranking producido;
- los comparables utilizados;
- la explicación SHAP correspondiente.

Este principio permite diferenciar claramente entre:

- datos observados;
- indicadores calculados;
- resultados del modelo;
- explicaciones del modelo;
- criterios comerciales posteriores.

La interfaz no debe ocultar esta separación conceptual.

---

## 34. Principios de presentación del score

El `score_afinidad` no constituye una probabilidad calibrada.

Por este motivo la interfaz evita términos como:

- probabilidad de emisión;
- probabilidad de convertirse en emisor;
- certeza de emisión.

La interfaz utiliza la denominación:

`Índice de Afinidad Bursátil`

y lo presenta como un indicador de priorización.

El percentil y la posición en el ranking sirven como elementos adicionales de interpretación.

La decisión comercial final debe continuar bajo supervisión humana.

---

## 35. Principios de presentación de similitud

La similitud con emisores históricos es independiente del Índice de Afinidad Bursátil.

La interfaz no suma ni pondera ambos indicadores.

La similitud cumple una función explicativa y de referencia comercial.

Su objetivo es permitir responder preguntas como:

- ¿a qué emisores históricos se parece esta empresa?;
- ¿qué empresas ya participantes del mercado presentan perfiles financieros similares?;
- ¿existen comparables suficientes para contextualizar al prospecto?

No debe interpretarse como evidencia causal ni como validación directa de que una empresa llegará a convertirse en emisor.

---

## 36. Principios de explicabilidad

SHAP permite explicar cómo determinadas variables influyen en el score producido por el modelo.

Un valor SHAP positivo significa que una variable aumenta el score respecto al valor base utilizado por el explicador.

Un valor SHAP negativo significa que una variable reduce el score respecto al valor base.

La explicación SHAP:

- describe el comportamiento del modelo;
- no demuestra causalidad;
- no sustituye análisis financiero;
- no sustituye revisión comercial;
- no modifica el modelo;
- no reentrena el modelo.

La explicación operacional se calcula utilizando el modelo final congelado v10.

---

## 37. Validación funcional final realizada

Se ejecutó una matriz estructurada de pruebas funcionales sobre el prototipo integrado.

Documento:

`docs/v10_functional_test_matrix.md`

El flujo validado fue:

`PostgreSQL → FastAPI → React → usuario`

y, para explicabilidad:

`modelo v10 congelado → SHAP → FastAPI → React → usuario`

### Escenarios

- PF-01 — Carga inicial del ranking: **APROBADA**
- PF-02 — Búsqueda de empresa: **APROBADA**
- PF-03 — Filtro por provincia: **APROBADA**
- PF-04 — Filtro por tipo de compañía: **APROBADA**
- PF-05 — Paginación: **APROBADA**
- PF-06 — Ficha empresarial: **APROBADA**
- PF-07 — Explicabilidad SHAP: **APROBADA**
- PF-08 — Emisores históricos comparables: **APROBADA**
- PF-09 — Empresa sin similitud suficiente: **APROBADA**
- PF-10 — Expediente inexistente: **APROBADA**

### Resultado

`10 de 10 pruebas funcionales aprobadas`

No se identificaron errores bloqueantes en los flujos principales evaluados.

Las pruebas verificaron, entre otros aspectos:

- carga del universo operacional;
- búsqueda;
- filtros;
- paginación;
- ficha empresarial;
- indicadores financieros;
- Índice de Afinidad Bursátil;
- ranking y percentil;
- SHAP con factores positivos y negativos;
- comparables históricos;
- comportamiento sin información suficiente para similitud;
- manejo controlado de un expediente inexistente.

Esta validación corresponde al cierre técnico de las pruebas funcionales del producto.

No debe confundirse con la validación formal de utilidad y usabilidad que todavía debe realizarse con al menos dos especialistas de la BVQ.

---

## 38. Estado de reproducibilidad

A la fecha de esta documentación se encuentran implementados los siguientes mecanismos:

- entorno Python aislado;
- dependencias Python congeladas;
- dependencias frontend bloqueadas mediante `package-lock.json`;
- repositorio Git;
- modelo final identificado;
- separación temporal documentada;
- pipeline reproducible;
- scripts de construcción operacional;
- PostgreSQL en Docker;
- API versionada;
- pruebas automáticas del backend;
- pruebas automatizadas del frontend;
- matriz de pruebas funcionales finales;
- frontend versionado;
- build reproducible;
- lint del frontend;
- documentación técnica;
- explicabilidad reproducible.

La incorporación de DVC, MLflow, migraciones Alembic y contenedor de FastAPI completará la capa de MLOps prevista para el proyecto.

---

## 39. Estado global del prototipo

Prospect Finder BVQ dispone actualmente de un flujo técnico funcional compuesto por:

1. datos históricos;
2. pipeline de preparación;
3. modelo predictivo v10 congelado;
4. ranking operacional;
5. motor independiente de similitud;
6. PostgreSQL;
7. FastAPI;
8. explicabilidad SHAP;
9. frontend React;
10. pruebas automatizadas del backend;
11. pruebas automatizadas del frontend;
12. pruebas funcionales finales con `10 de 10` escenarios aprobados;
13. validaciones técnicas del frontend;
14. control de versiones mediante Git y GitHub.

La solución permite actualmente identificar y priorizar empresas, consultar información financiera, revisar emisores históricos comparables y explicar individualmente los principales factores que influyen sobre el Índice de Afinidad Bursátil.

Las etapas restantes se concentran principalmente en validación con especialistas, MLOps y documentación de despliegue.