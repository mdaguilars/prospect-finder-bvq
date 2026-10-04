# Entorno técnico del proyecto

## 1. Entorno de desarrollo

Prospect Finder BVQ se desarrolla en un entorno local Windows de 64 bits utilizando herramientas de ingeniería de datos, aprendizaje automático, desarrollo web, bases de datos, contenerización, pruebas automatizadas y control de versiones.

El entorno está orientado a mantener trazabilidad, reproducibilidad y separación entre las capas de datos, modelado, API y producto.

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
| Node.js | Node.js LTS | 24.19.0 | Entorno para desarrollo del frontend |
| npm | npm | 11.17.0 | Administración de dependencias frontend |
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

No se deben escribir manualmente versiones de librerías no verificadas. El archivo de bloqueo constituye la referencia técnica para reconstruir el entorno Python.

---

## 3. Entorno virtual de Python

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

## 4. Entorno de notebooks

Jupyter se mantiene disponible para análisis exploratorio y validaciones.

El notebook inicial:

`notebooks/00_validacion_entorno.ipynb`

fue utilizado para comprobar el funcionamiento del entorno de Python y las principales librerías.

El desarrollo principal del proyecto se realiza actualmente mediante scripts Python versionados, lo cual facilita la reproducción del pipeline y la trazabilidad de cada etapa.

---

## 5. Estructura actual del proyecto

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

---

## 6. Organización de datos

### 6.1 `data/raw`

Contiene las fuentes originales utilizadas durante el proyecto.

Los archivos originales se conservan sin modificaciones.

Los datos sensibles o de gran tamaño no se almacenan directamente en Git.

### 6.2 `data/interim`

Contiene datasets generados durante etapas intermedias de:

- homologación;
- limpieza;
- integración;
- validación;
- preparación temporal.

### 6.3 `data/processed`

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

## 7. Componentes de código

### 7.1 `src/data`

Contiene scripts relacionados con:

- lectura de fuentes;
- homologación;
- integración;
- construcción de datasets;
- validación de calidad;
- construcción de la variable objetivo.

### 7.2 `src/features`

Contiene los procesos de ingeniería de variables.

El dataset financiero v10 incorpora variables financieras actuales, rezagos temporales, tasas de crecimiento y banderas de calidad.

### 7.3 `src/models`

Contiene scripts de experimentación, entrenamiento y evaluación de modelos.

Los experimentos iniciales se mantienen como evidencia histórica, mientras que el modelo seleccionado para v10 corresponde a una etapa posterior del proyecto.

### 7.4 `src/evaluation`

Contiene procesos de:

- evaluación temporal;
- métricas;
- análisis de ranking;
- análisis de errores;
- validaciones del modelo.

### 7.5 `src/analysis`

Contiene análisis posteriores al cierre del modelo, entre ellos:

- interpretabilidad;
- SHAP;
- LIME;
- sesgos;
- estabilidad;
- análisis de riesgos.

La explicabilidad es post-test y no modifica el modelo final congelado.

### 7.6 `src/product`

Contiene procesos para convertir el modelo analítico en componentes utilizables por el prototipo.

Actualmente incluye:

- generación del ranking operativo;
- construcción del universo prospectable;
- motor de similitud con emisores históricos.

### 7.7 `src/api`

Contiene el backend del prototipo construido con FastAPI.

Se organiza en:

- `core/`: configuración y conexión a base de datos;
- `models/`: modelos ORM;
- `routers/`: endpoints;
- `services/`: servicios de negocio y explicabilidad.

---

## 8. Modelo final v10

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

---

## 9. División temporal v10

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

## 10. Ranking operacional

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

## 11. Motor de similitud con emisores

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

---

## 12. PostgreSQL

El producto utiliza PostgreSQL como base de datos operacional.

La instancia local se ejecuta mediante Docker utilizando:

`postgres:17-alpine`

Base de datos de desarrollo:

`prospect_finder_bvq`

La base contiene actualmente tres tablas principales:

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

## 13. Docker

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

La dockerización completa de la API se considera una etapa posterior del cierre de MLOps.

---

## 14. FastAPI

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

---

## 15. Explicabilidad SHAP operacional

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

El runtime SHAP se precalienta durante el inicio de FastAPI para evitar que el primer usuario soporte el costo completo de inicialización.

Después del precalentamiento se verificaron respuestas locales cercanas a fracciones de segundo en el entorno de desarrollo.

La importancia global SHAP continúa utilizando los resultados post-test previamente validados.

LIME se conserva como técnica complementaria de análisis y evidencia metodológica, pero no constituye actualmente el método principal de explicación operacional del frontend.

---

## 16. API y separación de responsabilidades

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
           ├──────────────► Explicabilidad
           │
           ▼
    Ranking operacional
           │
           ▼
    PostgreSQL
           │
           ▼
    FastAPI
           │
           ▼
    Interfaz web

Esta separación evita que la interfaz acceda directamente a:

- archivos de entrenamiento;
- modelos;
- fuentes originales;
- bases analíticas.

La API constituye la capa de acceso al producto.

---

## 17. Pruebas automáticas

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

## 18. Frontend

El entorno frontend ya se encuentra preparado con:

- Node.js LTS 24.19.0;
- npm 11.17.0.

La implementación de la interfaz web constituye la siguiente etapa del prototipo.

La interfaz consumirá exclusivamente los endpoints de FastAPI.

No tendrá acceso directo a PostgreSQL ni a los archivos internos de modelado.

---

## 19. Alembic

Alembic 1.20.0 se encuentra instalado como dependencia.

Está previsto utilizarlo para formalizar las migraciones de esquema de PostgreSQL.

La inicialización de migraciones todavía no constituye una etapa cerrada del proyecto.

Por esta razón no debe afirmarse todavía que la base se encuentre administrada mediante migraciones Alembic.

---

## 20. Reproducibilidad

La reproducibilidad se apoya actualmente en:

- `.venv`;
- `requirements.txt`;
- `requirements-lock.txt`;
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
- `random_state = 42` cuando corresponde;
- metadatos de resultados;
- validación de scores operacionales frente al modelo final.

---

## 21. Archivos de dependencias

### `requirements.txt`

Contiene las dependencias instaladas necesarias para reconstruir el entorno Python utilizado actualmente.

### `requirements-lock.txt`

Contiene el conjunto completo de paquetes y versiones instaladas en el ambiente utilizado durante el desarrollo.

Después de incorporar nuevas dependencias, ambos archivos deben actualizarse.

En octubre de 2026 fueron actualizados para incorporar, entre otras dependencias:

- FastAPI;
- Uvicorn;
- SQLAlchemy;
- psycopg;
- Alembic;
- python-dotenv;
- Pydantic;
- pytest.

---

## 22. Control de versiones

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
- pruebas automáticas.

El repositorio no debe utilizarse para publicar información empresarial sensible ni datasets operacionales no autorizados.

---

## 23. Información no versionada

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

---

## 24. Seguridad de configuración

Las credenciales de producción no deben almacenarse en el código.

La configuración de FastAPI permite utilizar variables de entorno mediante `python-dotenv`.

Las credenciales existentes en Docker Compose corresponden al entorno local de desarrollo.

Para despliegues posteriores deberá utilizarse configuración externa segura mediante variables de entorno o mecanismos equivalentes.

---

## 25. Flujo técnico general actualizado

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
21. Pruebas automáticas.
22. Construcción de interfaz web.
23. Formalización MLOps.
24. Validación funcional con especialistas.

---

## 26. Estado técnico actual

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
- ejecución mediante Docker para PostgreSQL.

La API contiene actualmente los componentes necesarios para que el frontend consuma:

- ranking;
- búsqueda;
- filtros;
- detalle empresarial;
- indicadores financieros;
- comparables históricos;
- catálogos;
- explicabilidad.

---

## 27. Componentes pendientes

Los principales componentes técnicos que todavía deben completarse son:

- interfaz web;
- dockerización completa de FastAPI;
- migraciones Alembic;
- integración formal de DVC;
- integración formal de MLflow;
- pruebas funcionales finales del producto;
- validación con al menos dos especialistas de la BVQ;
- documentación final de despliegue y operación.

Estos elementos deben registrarse únicamente cuando hayan sido efectivamente implementados y validados.

---

## 28. Principio de trazabilidad

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

---

## 29. Estado de reproducibilidad

A la fecha de esta documentación se encuentran implementados los siguientes mecanismos:

- entorno Python aislado;
- dependencias congeladas;
- repositorio Git;
- modelo final identificado;
- separación temporal documentada;
- pipeline reproducible;
- scripts de construcción operacional;
- PostgreSQL en Docker;
- API versionada;
- pruebas automáticas;
- documentación técnica;
- explicabilidad reproducible.

La incorporación de DVC, MLflow, migraciones Alembic y contenedor de FastAPI completará la capa de MLOps prevista para el proyecto.