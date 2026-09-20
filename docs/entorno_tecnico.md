# Entorno técnico del proyecto

## 1. Entorno de desarrollo

El proyecto Prospect Finder BVQ se desarrolla en un entorno local Windows de 64 bits, utilizando herramientas de desarrollo, análisis de datos, aprendizaje automático y control de versiones orientadas a garantizar la trazabilidad y reproducibilidad del trabajo.

| Componente | Herramienta | Versión / configuración | Uso |
|---|---|---|---|
| Sistema operativo | Windows | 64 bits | Plataforma principal de desarrollo |
| Lenguaje | Python | 3.13.7 | Lenguaje principal del proyecto |
| Entorno de desarrollo | Visual Studio Code | 1.136.1 x64 | Desarrollo, edición y ejecución del código |
| Terminal | PowerShell | 7.6.5 | Ejecución de comandos y administración del entorno |
| Control de versiones | Git | 2.55.0.windows.3 | Registro y trazabilidad de cambios |
| Repositorio remoto | GitHub | Repositorio privado | Respaldo y sincronización del código |
| Rama principal | Git | main | Rama estable del proyecto |
| Gestor de paquetes | pip | 26.2.1 | Instalación y administración de dependencias |
| Entorno virtual | Python venv | .venv | Aislamiento de dependencias |
| Notebooks | Jupyter | 1.1.1 | Análisis y experimentación interactiva |
| Kernel | ipykernel | 7.3.0 | Ejecución de Python en Jupyter |
| Interfaz de notebooks | notebook | 7.6.2 | Gestión de notebooks |

---

## 2. Librerías principales

El proyecto utiliza librerías para procesamiento de datos, análisis estadístico, modelado, evaluación y visualización.

| Librería | Versión | Uso dentro del proyecto |
|---|---:|---|
| pandas | 3.0.5 | Manipulación, limpieza, integración y transformación de datos |
| NumPy | 2.5.3 | Operaciones numéricas |
| openpyxl | 3.1.5 | Lectura y escritura de archivos Excel |
| Matplotlib | 3.11.1 | Generación de gráficos |
| scikit-learn | 1.9.1 | Preprocesamiento, modelado y métricas |
| SciPy | 1.18.1 | Funciones científicas utilizadas por dependencias del proyecto |
| joblib | 1.6.0 | Serialización local de modelos |
| threadpoolctl | 3.7.0 | Gestión de ejecución de librerías numéricas |
| Jupyter | 1.1.1 | Ejecución interactiva de análisis |

Las versiones completas del entorno se encuentran registradas en:

- `requirements.txt`
- `requirements-lock.txt`

---

## 3. Entorno virtual

El proyecto utiliza un entorno virtual denominado `.venv`, creado mediante el módulo `venv` de Python.

La utilización de un entorno virtual permite:

- aislar las dependencias del proyecto;
- evitar conflictos con otras instalaciones de Python;
- mantener versiones específicas de librerías;
- facilitar la reproducción del entorno;
- reducir diferencias entre ejecuciones.

El intérprete utilizado corresponde a:

`prospect-finder-bvq\.venv\Scripts\python.exe`

La ejecución del entorno fue validada utilizando Python 3.13.7.

---

## 4. Activación del entorno

Desde PowerShell, ubicado en la carpeta raíz del proyecto, el entorno se activa mediante:

`.\.venv\Scripts\Activate.ps1`

Después de la activación, el prompt debe mostrar:

`(.venv)`

antes de la ruta del proyecto.

---

## 5. Entorno de notebooks

Para análisis exploratorio y validaciones iniciales se utiliza Jupyter integrado con Visual Studio Code.

Se creó el notebook:

`notebooks/00_validacion_entorno.ipynb`

Este notebook fue utilizado para verificar que el kernel de Jupyter utiliza el intérprete correspondiente al entorno virtual `.venv`.

La validación inicial confirmó el funcionamiento de:

- Python;
- pandas;
- NumPy;
- openpyxl;
- Matplotlib;
- Jupyter;
- ipykernel.

El desarrollo posterior del pipeline se realiza principalmente mediante scripts Python independientes para mejorar la reproducibilidad.

---

## 6. Estructura del proyecto

La estructura principal del repositorio es:

    prospect-finder-bvq/
    │
    ├── config/
    │   └── scvs_account_mapping.csv
    │
    ├── data/
    │   ├── raw/
    │   ├── interim/
    │   └── processed/
    │
    ├── docs/
    │   ├── baseline_v1.md
    │   ├── baseline_v2.md
    │   ├── baseline_v3.md
    │   ├── entorno_tecnico.md
    │   ├── informe_resultados_preliminares.md
    │   ├── inventario_fuentes.md
    │   └── pipeline_datos_mvp.md
    │
    ├── models/
    │
    ├── notebooks/
    │   └── 00_validacion_entorno.ipynb
    │
    ├── reports/
    │   ├── figures/
    │   └── results/
    │
    ├── src/
    │   ├── data/
    │   ├── evaluation/
    │   ├── features/
    │   └── models/
    │
    ├── .gitignore
    ├── README.md
    ├── requirements.txt
    └── requirements-lock.txt

---

## 7. Organización por etapas

### 7.1 `data/raw`

Contiene archivos originales obtenidos desde las fuentes utilizadas en el proyecto.

Los archivos originales se conservan sin modificaciones.

Los datos no se almacenan en Git debido a su tamaño y a consideraciones de manejo responsable de información.

---

### 7.2 `data/interim`

Contiene datasets intermedios generados durante las etapas de:

- homologación;
- limpieza;
- integración;
- validación.

Entre los archivos generados se encuentra:

`data/interim/scvs_financials_harmonized_2015_2023.csv.gz`

---

### 7.3 `data/processed`

Contiene datasets preparados para modelado.

Entre los archivos principales se encuentran:

`data/processed/mvp_labeled_2015_2023.csv.gz`

y:

`data/processed/mvp_features_2015_2023.csv.gz`

Estos archivos no se almacenan en Git.

---

### 7.4 `src/data`

Contiene scripts relacionados con:

- lectura de fuentes;
- homologación;
- construcción de datasets;
- validaciones de calidad;
- construcción de la variable objetivo.

---

### 7.5 `src/features`

Contiene los procesos de ingeniería de variables utilizados para construir el dataset destinado al modelado.

---

### 7.6 `src/models`

Contiene los scripts de entrenamiento y experimentación de modelos.

Entre los experimentos desarrollados se encuentran:

- Baseline v1;
- Baseline v2;
- experimento v3 de regularización.

---

### 7.7 `src/evaluation`

Contiene scripts para:

- generación de gráficos;
- análisis de errores;
- matrices de confusión;
- análisis de ranking;
- evaluación de falsos positivos y falsos negativos.

---

### 7.8 `reports/results`

Contiene resultados agregados de los experimentos, por ejemplo:

- métricas;
- ranking;
- coeficientes;
- metadatos;
- análisis de errores.

Los resultados relevantes para reproducibilidad se versionan explícitamente en Git.

---

### 7.9 `reports/figures`

Contiene las visualizaciones utilizadas para analizar y comunicar los resultados del modelo.

---

### 7.10 `docs`

Contiene la documentación metodológica, técnica y de trazabilidad del proyecto.

Actualmente incluye:

- `pipeline_datos_mvp.md`: describe el flujo completo de preparación de datos, etiquetado, ingeniería de variables y modelado;
- `inventario_fuentes.md`: documenta las fuentes utilizadas y su función dentro del proyecto;
- `diccionario_datos.md`: describe variables, tipos, fórmulas, disponibilidad y tratamiento de faltantes;
- `entorno_tecnico.md`: documenta el entorno de desarrollo, dependencias y estructura técnica;
- `baseline_v1.md`: documenta el modelo de referencia;
- `baseline_v2.md`: documenta el experimento de eliminación de `SECTOR_CIIU`;
- `baseline_v3.md`: documenta el experimento de regularización;
- `bitacora.md`: registra cronológicamente decisiones, cambios, resultados y aprendizajes;
- `backlog.md`: mantiene las actividades futuras priorizadas;
- `informe_resultados_preliminares.md`: consolida los resultados, análisis, limitaciones y próximos pasos de la entrega académica.

---
## 8. Reproducibilidad

La reproducibilidad del proyecto se apoya en los siguientes mecanismos:

- entorno virtual `.venv`;
- archivo `requirements.txt`;
- archivo `requirements-lock.txt`;
- control de versiones mediante Git;
- repositorio remoto privado en GitHub;
- scripts independientes por etapa;
- separación entre datos originales, intermedios y procesados;
- registro de configuraciones de experimentos;
- almacenamiento de métricas agregadas;
- documentación metodológica;
- uso de `random_state = 42` en procesos que requieren control de aleatoriedad.

---

## 9. Archivos de dependencias

### `requirements.txt`

Contiene las dependencias necesarias para ejecutar el proyecto.

### `requirements-lock.txt`

Contiene el detalle exacto de las versiones instaladas en el entorno utilizado durante el desarrollo.

El archivo de bloqueo permite reconstruir con mayor precisión el entorno técnico utilizado para los experimentos.

---

## 10. Modelos serializados

Los modelos entrenados pueden generarse localmente en:

`models/`

Por ejemplo:

`models/logistic_baseline.joblib`

Estos archivos no necesitan almacenarse permanentemente en Git mientras puedan reconstruirse mediante:

- código versionado;
- datos correspondientes;
- configuración registrada;
- dependencias documentadas.

---

## 11. Control de versiones

El proyecto utiliza Git como mecanismo de trazabilidad.

La rama principal es:

`main`

El repositorio remoto se encuentra alojado en GitHub y es privado.

Los commits permiten registrar de manera progresiva:

- cambios en el pipeline;
- experimentos;
- resultados;
- documentación;
- decisiones metodológicas.

---

## 12. Información no versionada

No se almacenan directamente en Git:

- archivos originales de gran tamaño;
- datasets intermedios;
- datasets procesados;
- modelos serializados reconstruibles;
- información interna sensible de la BVQ.

El repositorio se concentra en:

- código;
- configuraciones;
- documentación;
- resultados agregados;
- figuras necesarias para reproducibilidad y análisis.

---

## 13. Principio de separación de datos y código

El proyecto mantiene una separación explícita entre:

- datos originales;
- datos transformados;
- código fuente;
- modelos;
- resultados;
- documentación.

Esta estructura permite reconstruir el proceso de manera ordenada y reduce el riesgo de modificar accidentalmente los datos originales.

---

## 14. Flujo técnico general

El flujo implementado es:

1. Carga de datos originales.
2. Inventario de estructuras.
3. Homologación de cuentas contables.
4. Validación contable.
5. Construcción del dataset empresa-año.
6. Construcción de `TARGET_24M`.
7. Ingeniería de variables.
8. División temporal.
9. Preprocesamiento.
10. Entrenamiento.
11. Evaluación.
12. Análisis de ranking.
13. Análisis de errores.
14. Registro de resultados.
15. Documentación del experimento.

---

## 15. División temporal utilizada

La estructura actual de evaluación es:

| Conjunto | Período |
|---|---|
| TRAIN | 2015–2020 |
| VALIDATION | 2021 |
| TEST | 2022–2023 |

Esta división busca aproximar el comportamiento de un escenario real en el que el modelo se entrena con información histórica y posteriormente se utiliza sobre períodos futuros.

---

## 16. Modelo de referencia

El modelo de referencia actual es una regresión logística implementada mediante scikit-learn.

El pipeline integra:

- imputación de datos faltantes;
- estandarización;
- codificación categórica;
- regresión logística;
- ponderación de clases.

El Baseline v1 se mantiene como referencia para comparar las siguientes iteraciones.

---

## 17. Consideraciones sobre reproducibilidad de datos

Aunque el código y las configuraciones se encuentran versionados, la reproducción completa también requiere acceso a las fuentes originales utilizadas.

Por esta razón, la documentación del proyecto debe conservar:

- identificación de la fuente;
- nombre de los archivos;
- período de información;
- ubicación dentro de la estructura local;
- proceso de transformación;
- criterios de exclusión;
- reglas de homologación.

Las fechas exactas de extracción y las condiciones de uso de las fuentes deberán registrarse cuando hayan sido verificadas.

---

## 18. Estado del entorno

El entorno técnico se encuentra operativo para:

- procesamiento de datos;
- construcción de datasets;
- ingeniería de variables;
- entrenamiento de modelos;
- evaluación;
- generación de gráficos;
- análisis de errores;
- experimentación con nuevos algoritmos.

La configuración actual constituye la base reproducible para continuar con las siguientes fases del proyecto Prospect Finder BVQ.