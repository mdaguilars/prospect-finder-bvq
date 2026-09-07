# Entorno técnico del proyecto

## 1. Entorno de desarrollo

El proyecto Prospect Finder BVQ se desarrolla en un entorno local Windows de 64 bits, utilizando herramientas de desarrollo y control de versiones orientadas a garantizar la trazabilidad y reproducibilidad del trabajo.

| Componente | Herramienta | Versión |
|---|---|---|
| Lenguaje | Python | 3.13.7 |
| Entorno de desarrollo | Visual Studio Code | 1.136.1 x64 |
| Terminal | PowerShell | 7.6.5 |
| Control de versiones | Git | 2.55.0.windows.3 |
| Repositorio remoto | GitHub | Repositorio privado |
| Rama principal | Git | main |
| Gestor de paquetes | pip | 26.2.1 |
| Entorno virtual | Python venv | .venv |

## 2. Librerías instaladas

En esta etapa inicial se instalaron únicamente las librerías necesarias para la lectura, manipulación y preparación de datos tabulares.

| Librería | Versión | Uso |
|---|---|---|
| pandas | 3.0.5 | Manipulación, limpieza e integración de datos tabulares |
| NumPy | 2.5.3 | Operaciones numéricas |
| openpyxl | 3.1.5 | Lectura y escritura de archivos Microsoft Excel |

Las versiones exactas del entorno se mantienen registradas en el archivo `requirements.txt`.

## 3. Entorno virtual

El proyecto utiliza un entorno virtual denominado `.venv`, creado mediante el módulo `venv` de Python. Esto permite aislar las dependencias del proyecto de otras instalaciones de Python existentes en el equipo.

## 4. Control de versiones

El código fuente se administra mediante Git y se sincroniza con un repositorio privado en GitHub denominado:

`prospect-finder-bvq`

La rama principal utilizada es:

`main`

Los archivos de datos, credenciales, modelos generados y otros elementos sensibles o derivados están excluidos del repositorio mediante reglas definidas en `.gitignore`.