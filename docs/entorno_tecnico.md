# Entorno técnico del proyecto

## 1. Entorno de desarrollo

El proyecto Prospect Finder BVQ se desarrolla en un entorno local Windows de 64 bits, utilizando herramientas de desarrollo y control de versiones orientadas a garantizar la trazabilidad y reproducibilidad del trabajo.

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
| Entorno virtual | Python venv | .venv | Aislamiento de las dependencias del proyecto |
| Notebooks | Jupyter | 1.1.1 | Desarrollo y ejecución interactiva de análisis |
| Kernel de notebooks | ipykernel | 7.3.0 | Ejecución de Python dentro de Jupyter |
| Interfaz de notebooks | notebook | 7.6.2 | Gestión y ejecución de notebooks |

## 2. Librerías instaladas

En esta etapa se instalaron las librerías necesarias para la lectura, manipulación, preparación y análisis exploratorio inicial de datos.

| Librería | Versión | Uso dentro del proyecto |
|---|---|---|
| pandas | 3.0.5 | Manipulación, limpieza, integración y transformación de datos tabulares |
| NumPy | 2.5.3 | Operaciones numéricas y manejo de estructuras matriciales |
| openpyxl | 3.1.5 | Lectura y escritura de archivos Microsoft Excel |
| Matplotlib | 3.11.1 | Visualización de datos y análisis exploratorio |

Las versiones exactas de las librerías y de sus dependencias se mantienen registradas en el archivo `requirements.txt`.

## 3. Entorno virtual

El proyecto utiliza un entorno virtual denominado `.venv`, creado mediante el módulo `venv` de Python.

La utilización de un entorno virtual permite aislar las dependencias del proyecto de otras instalaciones de Python existentes en el equipo y facilita la reproducción del entorno de trabajo.

El intérprete utilizado por el proyecto corresponde a:

`prospect-finder-bvq\.venv\Scripts\python.exe`

La ejecución del entorno fue validada utilizando Python 3.13.7.

## 4. Entorno de notebooks

Para el análisis exploratorio y la experimentación se utiliza Jupyter integrado con Visual Studio Code.

Se creó el notebook:

`notebooks/00_validacion_entorno.ipynb`

Este notebook fue utilizado para verificar que el kernel de Jupyter ejecuta el intérprete de Python correspondiente al entorno virtual `.venv`.

La validación confirmó las siguientes versiones:

- Python 3.13.7
- pandas 3.0.5
- NumPy 2.5.3
- openpyxl 3.1.5
- Matplotlib 3.11.1
- Jupyter 1.1.1
- ipykernel 7.3.0
- notebook 7.6.2

## 5. Estructura del proyecto

La estructura inicial del proyecto es la siguiente:

```text
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
├── models/
├── notebooks/
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
└── requirements.txt