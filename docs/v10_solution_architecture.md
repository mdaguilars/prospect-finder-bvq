# Prospect Finder BVQ
# Arquitectura de la solución v10

## 1. Objetivo

Este documento describe la arquitectura técnica y funcional de Prospect Finder BVQ, sistema basado en aprendizaje automático orientado a identificar y priorizar empresas ecuatorianas con potencial de convertirse en emisores del mercado de valores.

La arquitectura mantiene el enfoque cliente-servidor definido en la propuesta del Capstone y separa explícitamente:

- fuentes de información;
- procesamiento;
- datos analíticos;
- modelo de inteligencia artificial;
- generación del producto operacional;
- persistencia;
- servicios API;
- explicabilidad;
- interfaz web;
- supervisión humana.

Esta separación busca facilitar:

- mantenimiento;
- reproducibilidad;
- actualización de datos;
- trazabilidad;
- versionamiento;
- seguridad;
- explicabilidad;
- pruebas;
- evolución futura.

Prospect Finder BVQ es una herramienta de apoyo a la prospección comercial.

No realiza decisiones automáticas de:

- aceptación;
- rechazo;
- aprobación regulatoria;
- evaluación legal;
- evaluación crediticia;
- incorporación de una empresa al mercado de valores.

La decisión final permanece bajo responsabilidad del especialista de la Bolsa de Valores Quito.

---

## 2. Arquitectura general

La arquitectura actual se representa mediante el siguiente flujo:

    Fuentes de información
            │
            ▼
    ETL y preparación
            │
            ▼
    Dataset analítico v10
            │
            ▼
    Modelo v10 congelado
            │
            ├──────────────► Explicabilidad SHAP
            │
            ▼
    Ranking operacional
            │
            ├──────────────► Similitud con emisores históricos
            │
            ▼
    PostgreSQL
            │
            ▼
    FastAPI
            │
            ▼
    Interfaz web
            │
            ▼
    Especialista BVQ

Cada capa mantiene una responsabilidad específica.

---

## 3. Capas de la solución

| Capa | Función |
|---|---|
| Fuentes de información | Proveen información empresarial, financiera e histórica |
| Procesamiento y ETL | Limpia, integra, homologa y valida los datos |
| Datos analíticos | Contienen las variables utilizadas por el modelo |
| Motor analítico | Genera el score de afinidad |
| Producto operacional | Construye ranking y universo prospectable |
| Similitud | Identifica emisores históricos financieramente comparables |
| Persistencia | Almacena resultados operacionales en PostgreSQL |
| Explicabilidad | Explica global y localmente el modelo mediante SHAP |
| API | Expone funcionalidades mediante FastAPI |
| Interfaz web | Presenta resultados al especialista |
| Supervisión humana | Mantiene la decisión comercial fuera de la IA |

---

## 4. Fuentes de información

La primera capa contiene las fuentes utilizadas para construir el universo empresarial y las variables analíticas.

Entre la información utilizada se encuentra:

- identificación empresarial;
- información financiera histórica;
- activos;
- patrimonio;
- ingresos por ventas;
- número de empleados;
- tipo de compañía;
- provincia;
- información histórica de emisores.

La información utilizada corresponde a fuentes públicas o institucionales autorizadas para el proyecto.

El prototipo permanece desacoplado de los sistemas transaccionales de la Bolsa de Valores Quito.

---

## 5. Unidad de análisis

Durante entrenamiento y evaluación la unidad analítica corresponde a:

`empresa-año`

Esto permite analizar la situación de una empresa en un momento determinado y observar si posteriormente se convierte en emisor.

En el producto operacional la unidad corresponde a:

`empresa`

Cada empresa aparece una sola vez en el ranking utilizando la información financiera correspondiente al año operativo definido.

| Entorno | Unidad |
|---|---|
| Entrenamiento | Empresa-año |
| Backtesting | Empresa-año |
| Validación | Empresa-año |
| TEST | Empresa-año |
| Producto operacional | Empresa |

---

## 6. Procesamiento y ETL

La preparación de datos se realiza principalmente con Python y pandas.

El flujo general es:

    Extracción
        ↓
    Homologación
        ↓
    Limpieza
        ↓
    Integración
        ↓
    Validación
        ↓
    Construcción de variables
        ↓
    Construcción del target
        ↓
    Dataset analítico

Durante esta etapa se realizan controles relacionados con:

- tipos de datos;
- valores faltantes;
- duplicados;
- inconsistencias;
- valores negativos;
- continuidad temporal;
- información histórica;
- anomalías en empleados;
- consistencia de activos;
- consistencia de ventas;
- consistencia de patrimonio.

---

## 7. Variables del modelo

El modelo v10 utiliza 25 variables.

### Variables de escala

- activos;
- patrimonio;
- ingresos por ventas;
- número de empleados.

### Variables históricas

- activos del período anterior;
- patrimonio del período anterior;
- ventas del período anterior;
- empleados del período anterior.

### Indicadores financieros

- patrimonio / activos;
- ROA;
- margen neto;
- rotación de activos;
- ROE.

### Variables de crecimiento

- crecimiento de activos;
- crecimiento de patrimonio;
- crecimiento de ventas;
- crecimiento de empleados.

### Variables de consistencia y calidad

- disponibilidad de información del período anterior;
- activos negativos;
- ventas negativas;
- empleados con valor fijo;
- salto temporal en empleados;
- anomalía total de empleados;
- patrimonio no positivo.

### Variable categórica

- tipo de compañía.

La provincia no forma parte de las variables predictivas de v10.

Se conserva como atributo descriptivo, de segmentación y auditoría.

---

## 8. Variable objetivo

La variable objetivo es:

`TARGET_24M`

Identifica si una empresa se convierte en emisor dentro de los 24 meses posteriores al punto de observación.

El problema corresponde a clasificación supervisada con fuerte desbalance.

El modelo no intenta predecir:

- la fecha exacta de una emisión;
- el monto de una emisión;
- el instrumento que podría utilizarse;
- la aprobación regulatoria.

Su finalidad es producir una señal de priorización.

---

## 9. Separación temporal

La separación temporal congelada de v10 es:

| Conjunto | Período |
|---|---|
| TRAIN | 2012–2018 |
| EMBARGO 1 | 2019 |
| VALIDATION | 2020 |
| EMBARGO 2 | 2021 |
| TEST | 2022–2023 |

El conjunto TEST permaneció cerrado durante la selección del modelo.

Los períodos de embargo ayudan a reducir riesgo de fuga temporal.

Después de observar TEST no se realizó reajuste del modelo v10.

---

## 10. Dataset analítico

El dataset financiero utilizado por v10 es:

`data/processed/v10_features_financial_2012_2023.csv.gz`

Contiene:

- identificadores;
- año;
- target;
- split temporal;
- información empresarial;
- variables financieras;
- rezagos;
- crecimiento;
- indicadores financieros;
- banderas de calidad.

Los scripts utilizados para construirlo se encuentran versionados.

---

## 11. Modelo final

El modelo congelado corresponde a:

`v10_hgb_financial_c3`

Configuración:

`C3_CONSERVATIVE`

Estimador:

`HistGradientBoostingClassifier`

El artefacto final se encuentra en:

`models/v10/v10_hgb_financial_c3_final.joblib`

La configuración principal incluye:

- `learning_rate = 0.03`
- `max_iter = 250`
- `max_leaf_nodes = 5`
- `max_depth = 2`
- `min_samples_leaf = 200`
- `l2_regularization = 3`
- `early_stopping = False`
- `random_state = 42`
- `class_weight = balanced`

El modelo utiliza tratamiento categórico nativo para `tipo_compania`.

---

## 12. Score de afinidad

El modelo produce un valor numérico entre 0 y 1.

Dentro de Prospect Finder BVQ se denomina:

`score_afinidad`

Este valor se utiliza para ordenar empresas.

No corresponde a una probabilidad calibrada.

Por ejemplo:

`score_afinidad = 0.90`

no significa:

`90 % de probabilidad de convertirse en emisor`.

La interpretación correcta es relativa:

una empresa con mayor score obtiene mayor prioridad dentro del universo analizado.

---

## 13. Evaluación final

Las métricas principales utilizadas incluyen:

- PR-AUC;
- ROC-AUC;
- Precision@K;
- Recall@K;
- Lift@K.

TEST contiene:

`260.445 observaciones`

y:

`54 positivos`

Resultados oficiales:

| Métrica | Resultado |
|---|---:|
| PR-AUC | 0.007468801 |
| ROC-AUC | 0.934603901 |

El modelo mostró capacidad de ordenamiento general, aunque la concentración de positivos en Top-K disminuyó respecto de algunos backtests.

Por esta razón el ranking es una herramienta de apoyo y no una regla automática.

---

## 14. Ranking operacional

El producto operacional utiliza:

`ANIO = 2023`

Fecha de decisión:

`2024-05-01`

El universo contiene:

`137.156 empresas`

El proceso es:

    Información 2023
        ↓
    25 variables
        ↓
    Modelo v10 congelado
        ↓
    score_afinidad
        ↓
    ranking
        ↓
    percentil

La generación operacional fue validada contra el scoring correspondiente del modelo congelado.

Se obtuvo coincidencia completa de los scores del universo comparado.

---

## 15. Prevención de fuga futura

El producto operacional se construye respetando la fecha de decisión.

Las empresas cuya inscripción como emisores ocurrió después de:

`2024-05-01`

no se utilizan para modificar retrospectivamente:

- el universo;
- el score;
- el ranking;
- los comparables de referencia.

La información futura puede utilizarse únicamente para análisis retrospectivo posterior.

---

## 16. Persistencia operacional

La aplicación utiliza PostgreSQL como base de datos operacional.

PostgreSQL se ejecuta localmente mediante Docker.

Imagen:

`postgres:17-alpine`

Base:

`prospect_finder_bvq`

Las tablas principales son:

### `operational_prospects`

Registros:

`137.156`

Contiene:

- identificación;
- ranking;
- score;
- percentil;
- indicadores financieros;
- calidad de datos;
- versión del modelo.

### `issuer_similarity_summary`

Registros:

`137.156`

Contiene el resumen del componente de similitud.

### `issuer_similarity_matches`

Registros:

`656.600`

Contiene los emisores históricos comparables.

Total cargado y validado:

`930.912 registros`

---

## 17. Modelo relacional operacional

La relación principal es:

    operational_prospects
            │
            ├── 1 : 0..1 ── issuer_similarity_summary
            │
            └── 1 : 0..5 ── issuer_similarity_matches

`EXPEDIENTE_KEY` funciona como identificador principal de la empresa prospectable.

Los comparables se ordenan mediante:

`orden_comparable`

---

## 18. Motor de similitud

El sistema implementa un motor independiente de similitud con emisores históricos.

Su objetivo es responder:

> ¿Qué emisores históricos tenían un perfil financiero más parecido al de esta empresa?

No intenta responder:

> ¿Cuál es la probabilidad de que esta empresa emita?

El motor utiliza siete variables:

- activos;
- patrimonio;
- ingresos por ventas;
- empleados;
- patrimonio / activos;
- ROA;
- rotación de activos.

---

## 19. Metodología de similitud

Las variables se convierten a percentiles anuales.

Posteriormente se calcula distancia euclidiana sobre los siete percentiles.

La similitud se expresa entre:

`0 y 100`

Para cada empresa se recuperan hasta cinco emisores históricos.

El resultado incluye:

- orden del comparable;
- similitud;
- distancia;
- nombre del emisor;
- RUC;
- año del perfil;
- fecha de decisión del perfil;
- fecha de primera inscripción;
- tipo de compañía;
- provincia.

---

## 20. Referencia temporal de emisores

Los emisores utilizados como referencia deben haber sido conocidos antes o en la fecha de decisión.

Para el corte operativo se identificaron:

`288 emisores conocidos`

De estos, los perfiles con información completa suficiente para la metodología de similitud conforman el universo efectivo de referencia.

Las empresas que se convierten en emisores después del corte no participan como referencia.

---

## 21. Cobertura de similitud

Sobre las 137.156 empresas operativas:

`131.320`

disponen de similitud calculable.

`5.836`

presentan información insuficiente para el cálculo con las siete variables definidas.

La ausencia de similitud no elimina a una empresa del ranking predictivo.

---

## 22. Separación entre score y similitud

El producto mantiene dos señales independientes.

| Señal | Interpretación |
|---|---|
| `score_afinidad` | Prioridad generada por el modelo |
| similitud | Cercanía financiera con emisores históricos |

Actualmente no existe una fórmula ponderada que combine ambas.

Una eventual combinación deberá ser evaluada como una nueva metodología y no incorporarse retroactivamente a v10.

---

## 23. Explicabilidad

La arquitectura incorpora una capa independiente de explicabilidad.

Durante el proyecto se utilizaron:

- Permutation Importance;
- SHAP;
- LIME.

Estas técnicas no modifican:

- variables;
- modelo;
- hiperparámetros;
- score;
- ranking.

---

## 24. SHAP global

SHAP constituye la principal técnica de explicabilidad.

Para análisis global se utilizó:

`PermutationExplainer`

con background obtenido exclusivamente desde TRAIN.

Entre las variables de mayor importancia global se encuentran:

- activos;
- ingresos por ventas;
- patrimonio del período anterior;
- crecimiento de patrimonio;
- patrimonio / activos;
- crecimiento de activos;
- patrimonio;
- activos del período anterior;
- ROA;
- margen neto.

La importancia global describe comportamiento promedio del modelo.

No implica causalidad.

---

## 25. SHAP local

La API permite generar una explicación específica para una empresa.

El flujo es:

    Empresa
        ↓
    25 variables
        ↓
    Modelo v10
        ↓
    score
        ↓
    PermutationExplainer
        ↓
    contribuciones SHAP
        ↓
    factores que aumentan o reducen afinidad

Para cada explicación se valida:

`score_modelo ≈ SHAP_BASE_VALUE + Σ SHAP_VALUE`

Durante las pruebas funcionales se obtuvieron errores numéricos del orden de:

`10^-15`

lo cual confirma la reconstrucción del score dentro de tolerancia numérica.

---

## 26. Rendimiento SHAP

La inicialización inicial de PermutationExplainer puede requerir varios segundos.

Para evitar que este costo recaiga sobre el primer usuario, FastAPI realiza un precalentamiento de SHAP durante el arranque.

Una vez inicializado el runtime, las explicaciones locales fueron verificadas en el entorno de desarrollo con tiempos de respuesta inferiores a aproximadamente dos segundos y, en pruebas posteriores, cercanos a fracciones de segundo.

El tiempo exacto dependerá del equipo y del entorno de ejecución.

---

## 27. TreeExplainer

Se evaluó `TreeExplainer` como posible mecanismo de optimización.

Aunque presentó un tiempo de ejecución significativamente menor, no reconstruyó correctamente el score del modelo final cuando se utilizó la representación numérica necesaria para la variable categórica nativa.

Por esta razón fue descartado para la implementación operacional.

La prioridad metodológica es mantener explicaciones consistentes con el score real del modelo.

---

## 28. LIME

LIME se mantiene como técnica complementaria.

Fue utilizado para:

- contrastar explicaciones locales;
- disponer de una segunda técnica de interpretabilidad;
- analizar fidelidad local.

No reproduce exactamente el score del modelo.

Por tanto, no es actualmente el método principal del producto.

---

## 29. Capa API

FastAPI constituye la capa de servicios entre:

- PostgreSQL;
- modelo;
- servicios analíticos;
- explicabilidad;
- futura interfaz web.

La aplicación principal se encuentra en:

`src/api/main.py`

La arquitectura interna se divide en:

    src/api/
    ├── core/
    ├── models/
    ├── routers/
    └── services/

---

## 30. Configuración y base de datos

`src/api/core/`

contiene:

- configuración;
- conexión a PostgreSQL;
- administración de sesiones SQLAlchemy.

Las credenciales reales de producción no deben almacenarse en el código.

La aplicación admite configuración mediante variables de entorno.

---

## 31. ORM

Los modelos SQLAlchemy se encuentran en:

`src/api/models/`

Representan las tablas:

- `operational_prospects`;
- `issuer_similarity_summary`;
- `issuer_similarity_matches`.

Esta capa separa la lógica de aplicación de la estructura física de PostgreSQL.

---

## 32. Endpoints implementados

### Salud

`GET /api/health`

Permite verificar:

- funcionamiento de la API;
- conexión a PostgreSQL;
- versión;
- entorno.

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

### Detalle

`GET /api/prospects/{expediente_key}`

Devuelve:

- identificación;
- ranking;
- score;
- percentil;
- calidad de datos;
- indicadores financieros;
- resumen de similitud;
- cinco comparables históricos;
- versión del modelo.

### Catálogos

`GET /api/catalogs`

Devuelve:

- provincias;
- tipos de compañía;
- cantidad de empresas por categoría.

### SHAP global

`GET /api/explainability/global`

Devuelve la importancia global previamente validada.

### SHAP local

`GET /api/explainability/prospects/{expediente_key}`

Genera explicación SHAP bajo demanda para una empresa.

---

## 33. Normalización de texto

Las fuentes originales contienen en algunos casos:

- espacios finales;
- espacios internos repetidos.

La API normaliza estos textos antes de entregarlos al frontend.

Esto aplica especialmente a:

- provincia;
- tipo de compañía;
- nombres utilizados en filtros.

La normalización no modifica las variables con las que se entrenó o ejecuta el modelo.

---

## 34. Interfaz web

La interfaz será consumida desde navegador.

El frontend todavía se encuentra pendiente de implementación.

El entorno para su desarrollo ya dispone de:

- Node.js LTS 24.19.0;
- npm 11.17.0.

La interfaz se comunicará únicamente con FastAPI.

No tendrá acceso directo a:

- PostgreSQL;
- archivos CSV;
- modelo Joblib;
- datasets de entrenamiento.

---

## 35. Módulos previstos de interfaz

El prototipo deberá presentar al menos:

| Módulo | Función |
|---|---|
| Resumen | Indicadores generales |
| Ranking | Priorización de empresas |
| Filtros | Segmentación |
| Empresa | Ficha detallada |
| Explicabilidad | Factores asociados con el score |
| Emisores comparables | Perfiles históricos similares |
| Calidad | Cobertura y disponibilidad |
| Modelo | Versión y configuración |
| Riesgos | Limitaciones principales |

El monitoreo puede incorporarse como módulo adicional durante el cierre de MLOps.

---

## 36. Flujo de usuario

El flujo esperado es:

    Inicio
      ↓
    Ranking
      ↓
    Filtros
      ↓
    Selección de empresa
      ↓
    Indicadores
      ↓
    Explicación
      ↓
    Emisores comparables
      ↓
    Análisis
      ↓
    Decisión del especialista

La decisión final no es automatizada.

---

## 37. Pruebas automáticas

La API dispone actualmente de pruebas mediante:

`pytest`

Ubicación:

`tests/api/`

Se validan:

- health check;
- ranking;
- paginación;
- filtros;
- detalle;
- comparables;
- catálogos;
- SHAP global;
- integración de explicabilidad;
- errores 404.

Ejecución:

`python -m pytest "tests\api" -q`

Resultado actual:

`12 passed`

Las advertencias registradas corresponden a deprecaciones internas de dependencias de SHAP/Matplotlib y no afectan las pruebas.

---

## 38. Docker

Docker Desktop se encuentra instalado y operativo utilizando WSL2.

El archivo:

`compose.yaml`

levanta actualmente PostgreSQL.

La API todavía no ha sido contenerizada.

Por tanto:

| Componente | Estado Docker |
|---|---|
| PostgreSQL | Implementado |
| FastAPI | Pendiente |
| Frontend | Pendiente |

---

## 39. Seguridad

La arquitectura considera:

- separación de componentes;
- mínima exposición de datos;
- protección de credenciales;
- variables de entorno;
- no publicación de datasets sensibles;
- API como capa de acceso;
- separación entre entrenamiento y consumo operacional.

La autenticación y autorización de usuarios constituye una etapa posterior del prototipo y deberá formalizarse si la solución avanza hacia un entorno institucional productivo.

---

## 40. Trazabilidad

Cada resultado debe poder relacionarse con:

- versión del modelo;
- configuración;
- año de datos;
- fecha de decisión;
- variables utilizadas;
- calidad de información;
- score;
- ranking;
- comparables;
- explicación SHAP.

Ejemplo:

Modelo:

`v10_hgb_financial_c3`

Configuración:

`C3_CONSERVATIVE`

Año operativo:

`2023`

Fecha de decisión:

`2024-05-01`

---

## 41. Versionamiento

La versión actual del modelo es:

`v10`

Esta versión permanece congelada.

Los resultados de TEST no se utilizan para modificar retroactivamente:

- variables;
- hiperparámetros;
- reglas;
- score;
- arquitectura del modelo.

Cualquier cambio relevante debe corresponder a una nueva versión experimental.

Una eventual versión posterior podrá identificarse como:

`v11`

---

## 42. Monitoreo

La arquitectura contempla monitoreo futuro de:

### Datos

- faltantes;
- cobertura;
- nuevas categorías;
- cambios de distribución.

### Variables

- PSI;
- cambios de distribución;
- missingness;
- estabilidad temporal.

### Score

- media;
- mediana;
- distribución;
- concentración.

### Ranking

- tamaño empresarial;
- tipo de compañía;
- provincia;
- calidad de información.

### Desempeño

Cuando existan labels maduros:

- PR-AUC;
- ROC-AUC;
- Precision@K;
- Recall@K;
- Lift@K.

---

## 43. Sesgos y riesgos

El análisis v10 identificó posibles concentraciones relacionadas con:

- tamaño;
- disponibilidad de información;
- tipo de compañía;
- ubicación geográfica.

Estas concentraciones deben monitorearse.

No se utilizan automáticamente como criterios de exclusión.

La provincia no es variable predictiva de v10.

Debe utilizarse para:

- descripción;
- filtros;
- auditoría;
- análisis de distribución.

---

## 44. MLOps

La arquitectura prevista considera:

    Datos
      ↓
    Versionamiento
      ↓
    Experimentos
      ↓
    Modelo
      ↓
    Registro
      ↓
    Contenedor
      ↓
    Aplicación
      ↓
    Monitoreo

Actualmente están implementados parcialmente los componentes de reproducibilidad mediante:

- Git;
- GitHub;
- requirements;
- modelo congelado;
- scripts reproducibles;
- Docker para PostgreSQL;
- pruebas automáticas;
- documentación;
- metadatos.

Continúan pendientes:

- DVC;
- MLflow;
- dockerización de FastAPI;
- migraciones Alembic;
- formalización de monitoreo operacional.

---

## 45. Estado actual

| Componente | Estado |
|---|---|
| Integración de datos | Implementado |
| ETL | Implementado |
| Construcción de variables | Implementado |
| Target temporal | Implementado |
| División temporal | Implementado |
| Backtesting | Implementado |
| Modelos clásicos | Implementado |
| MLP | Implementado |
| Selección del modelo | Implementado |
| Evaluación TEST | Implementado |
| Modelo v10 congelado | Implementado |
| Permutation Importance | Implementado |
| SHAP global | Implementado |
| SHAP local | Implementado |
| LIME | Implementado |
| Estabilidad temporal | Implementado |
| Sesgos y riesgos | Implementado |
| Ranking operacional | Implementado |
| Similitud con emisores | Implementado |
| PostgreSQL | Implementado |
| Carga operacional PostgreSQL | Implementado |
| Modelos ORM | Implementado |
| FastAPI | Implementado |
| Health endpoint | Implementado |
| Ranking endpoint | Implementado |
| Detalle endpoint | Implementado |
| Catálogos endpoint | Implementado |
| Explicabilidad API | Implementado |
| Pruebas automáticas API | Implementado |
| Docker PostgreSQL | Implementado |
| Frontend web | Pendiente |
| Docker FastAPI | Pendiente |
| Alembic operativo | Pendiente |
| DVC | Pendiente |
| MLflow | Pendiente |
| Validación con especialistas | Pendiente |

---

## 46. Arquitectura actual del prototipo

La arquitectura implementada actualmente es:

    Fuentes
        ↓
    ETL
        ↓
    Dataset v10
        ↓
    Modelo congelado
        ↓
    Ranking operacional
        ↓
    ┌───────────────────────┐
    │                       │
    ▼                       ▼
    Similitud          Explicabilidad
    con emisores          SHAP
    │                       │
    └───────────┬───────────┘
                ▼
            PostgreSQL
                ↓
             FastAPI
                ↓
          Interfaz web
           [pendiente]
                ↓
        Especialista BVQ

---

## 47. Desacoplamiento

La interfaz web no dependerá de la implementación interna del modelo.

La comunicación será:

`Interfaz → API → Servicios → Datos / Modelo`

Esto permite que una futura versión del modelo pueda sustituir v10 sin reconstruir completamente la aplicación.

---

## 48. Supervisión humana

El principio central del producto es:

`IA → Priorización → Explicación → Especialista → Decisión`

No se implementa:

`IA → Decisión automática`

Esto es particularmente importante por:

- fuerte desbalance;
- variación temporal;
- falsos positivos;
- existencia de factores empresariales no presentes en los datos;
- necesidad de criterio comercial;
- necesidad de supervisión institucional.

---

## 49. Estado del documento

Arquitectura lógica:

`Implementada`

Arquitectura analítica:

`Implementada`

Modelo v10:

`Implementado y congelado`

Ranking operacional:

`Implementado`

Motor de similitud con emisores:

`Implementado`

PostgreSQL:

`Implementado`

FastAPI:

`Implementado`

SHAP operacional:

`Implementado`

Pruebas API:

`Implementadas - 12 pruebas aprobadas`

Interfaz web:

`Pendiente`

Docker FastAPI:

`Pendiente`

Alembic:

`Instalado, implementación de migraciones pendiente`

DVC:

`Pendiente`

MLflow:

`Pendiente`

Validación con especialistas:

`Pendiente`

---

## 50. Resultado esperado final

La arquitectura permitirá disponer de un prototipo funcional que integre:

`Datos + IA + Ranking + Similitud + Explicabilidad + PostgreSQL + API + Interfaz + Supervisión humana`

El especialista podrá seguir un flujo de trabajo:

`Explorar → Filtrar → Priorizar → Comprender → Comparar → Analizar → Decidir`

Prospect Finder BVQ permanecerá como una herramienta de apoyo analítico y comercial, no como un sistema automatizado de decisión.