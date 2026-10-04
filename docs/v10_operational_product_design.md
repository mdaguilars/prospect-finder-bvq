# Prospect Finder BVQ
## Diseño operativo del producto v10

### 1. Propósito

Prospect Finder BVQ es una herramienta de apoyo analítico para el proceso de prospección de potenciales emisores de la Bolsa de Valores Quito.

Su propósito es permitir que los especialistas puedan analizar un universo amplio de empresas, priorizar aquellas que presentan mayor afinidad según el modelo desarrollado, revisar sus principales características financieras, comprender los factores asociados con el score y contrastar su perfil con emisores históricos.

La herramienta busca reducir el universo que requiere revisión manual y proporcionar un proceso de prospección:

- estructurado;
- consistente;
- trazable;
- explicable;
- reproducible.

Prospect Finder BVQ no determina si una empresa debe convertirse en emisor.

Tampoco constituye:

- evaluación financiera formal;
- recomendación de inversión;
- evaluación crediticia;
- evaluación legal;
- evaluación regulatoria;
- aprobación de una empresa como emisor.

La decisión comercial final permanece en los especialistas de la Bolsa de Valores Quito.

---

### 2. Usuario principal

El usuario principal del prototipo es un especialista autorizado de la Bolsa de Valores Quito involucrado en actividades de:

- prospección;
- desarrollo de mercado;
- análisis empresarial;
- identificación de potenciales emisores.

El sistema está diseñado inicialmente como una herramienta interna.

El usuario no necesita conocimientos de programación, ciencia de datos o aprendizaje automático.

---

### 3. Principio de funcionamiento

El flujo general del producto es:

`Datos → Modelo → Ranking → Explicación → Comparación → Análisis humano`

No se implementa:

`Datos → Modelo → Decisión automática`

El sistema funciona como mecanismo de priorización.

---

### 4. Unidad analítica y unidad operativa

Durante entrenamiento y evaluación, la unidad utilizada fue:

`empresa-año`

En el producto operacional la unidad es:

`empresa`

Cada empresa aparece una sola vez dentro del ranking operativo.

Para la versión actual se utiliza:

`ANIO = 2023`

con fecha de decisión:

`2024-05-01`

Por tanto:

| Entorno | Unidad |
|---|---|
| Entrenamiento | Empresa-año |
| Backtesting | Empresa-año |
| Validación | Empresa-año |
| TEST | Empresa-año |
| Producto operativo actual | Empresa con información 2023 |

En futuras actualizaciones podrá utilizarse el último ejercicio financiero disponible, siempre que se mantengan las mismas reglas de construcción temporal y prevención de fuga de información.

---

### 5. Universo operacional

El ranking actual contiene:

`137.156 empresas`

El universo se construye respetando la fecha de decisión.

Las empresas conocidas como emisores antes o hasta la fecha de corte correspondiente no forman parte del universo prospectable.

La construcción no utiliza conocimiento de eventos futuros para modificar retrospectivamente el ranking.

---

### 6. Modelo utilizado

El modelo operativo es:

`v10_hgb_financial_c3`

Configuración:

`C3_CONSERVATIVE`

Algoritmo:

`HistGradientBoostingClassifier`

El modelo se encuentra congelado.

Los resultados obtenidos posteriormente sobre TEST o sobre información operacional no se utilizan para modificar retroactivamente sus parámetros.

---

### 7. Índice de Afinidad Bursátil

El modelo produce técnicamente el campo:

`score_afinidad`

con valores entre 0 y 1.

En la interfaz comercial se utiliza el nombre:

**Índice de Afinidad Bursátil**

Este indicador permite ordenar relativamente las empresas dentro del universo.

No representa una probabilidad calibrada.

Por ejemplo:

`0,90`

no significa:

`90 % de probabilidad de convertirse en emisor`.

La interpretación correcta es:

> La empresa presenta una posición relativa elevada dentro del universo evaluado por el modelo.

---

### 8. Ranking

Cada empresa tiene una posición determinada por su score.

Los principales campos disponibles son:

| Campo | Descripción |
|---|---|
| Ranking | Posición dentro del universo |
| Empresa | Razón social |
| RUC | Identificador empresarial |
| Índice de Afinidad Bursátil | Score del modelo |
| Percentil | Posición relativa dentro del universo |
| Provincia | Ubicación registrada |
| Tipo de compañía | Forma societaria |
| Activos | Información financiera |
| Patrimonio | Información financiera |
| Ventas | Información financiera |
| Empleados | Información empresarial |
| Calidad | Indicadores de disponibilidad y consistencia |
| Similitud | Cercanía con perfiles históricos de emisores |

---

### 9. Clasificación visual de prioridad

La primera versión funcional no incorpora todavía categorías discretas como:

- Muy alta;
- Alta;
- Media;
- Baja.

Actualmente la interfaz presenta directamente:

- posición del ranking;
- Índice de Afinidad Bursátil;
- percentil.

Una futura clasificación visual deberá calcularse sobre percentiles del ranking.

No deberá interpretarse como probabilidad.

La clasificación visual pertenecería únicamente a la capa de presentación y no modificaría el resultado del modelo.

---

### 10. Pantalla principal

La pantalla principal se encuentra implementada y proporciona una visión ejecutiva del universo prospectable.

Actualmente muestra:

- universo prospectable;
- mayor afinidad visible;
- número de provincias;
- número de tipos de compañía;
- fecha de decisión;
- versión y configuración del modelo;
- ranking de empresas.

El elemento central es la tabla de ranking.

---

### 11. Tabla principal

La tabla implementada permite revisar rápidamente las empresas priorizadas.

Actualmente muestra:

| Campo | Visualización |
|---|---|
| Ranking | Número |
| Empresa | Razón social |
| Provincia | Texto |
| Tipo | Texto |
| Afinidad | Score |
| Percentil | Porcentaje relativo |
| Similitud con emisor | Escala 0–100 |
| Calidad | Indicador visual |

El RUC y los principales indicadores financieros se muestran en la ficha individual.

Esta decisión reduce la densidad de información de la tabla y mantiene el detalle en un segundo nivel.

---

### 12. Paginación

La API soporta paginación y la interfaz ya consume el ranking por páginas.

La vista actual utiliza 25 empresas por página y no carga simultáneamente las 137.156 empresas.

Esto mejora:

- tiempo de respuesta;
- consumo de memoria;
- experiencia del usuario;
- escalabilidad del prototipo.

---

### 13. Búsqueda

La búsqueda se encuentra implementada en la interfaz.

Permite localizar empresas mediante:

- razón social;
- RUC;
- expediente.

La búsqueda:

- no recalcula el modelo;
- no altera el score;
- no modifica el ranking original.

Solamente reduce el conjunto visible.

---

### 14. Filtros implementados

La API dispone de filtros por:

- provincia;
- tipo de compañía;
- score mínimo;
- similitud mínima;
- disponibilidad de comparables.

También permite búsqueda y paginación.

La primera versión funcional de la interfaz expone directamente:

- búsqueda;
- provincia;
- tipo de compañía;
- limpieza de filtros;
- paginación.

Los filtros por score mínimo, similitud mínima y disponibilidad de comparables permanecen disponibles en la API y podrán incorporarse posteriormente a la interfaz sin modificar el modelo.

---

### 15. Catálogos

La API dispone del servicio:

`GET /api/catalogs`

que entrega los valores normalizados utilizados para construir filtros.

Actualmente existen:

`24 provincias`

y:

`9 tipos de compañía`

Los catálogos incluyen además la cantidad de empresas por categoría.

La interfaz consume estos catálogos dinámicamente en lugar de mantener listas estáticas.

---

### 16. Filtros futuros

Posteriormente podrán incorporarse filtros adicionales por:

- activos;
- patrimonio;
- ventas;
- empleados;
- ROA;
- ROE;
- margen;
- crecimiento;
- calidad de datos.

Estos filtros todavía no deben documentarse como funcionalidades implementadas.

Su incorporación no deberá modificar el score original.

---

### 17. Filtros rápidos de interfaz

Los accesos rápidos todavía no forman parte de la primera versión funcional.

En una evolución posterior podrán incorporarse opciones como:

**Mayor afinidad**

Empresas ubicadas en la parte superior del ranking.

**Alta similitud con emisores**

Empresas cuyos perfiles financieros presentan mayor cercanía con emisores históricos.

**Con comparables**

Empresas para las cuales existe información suficiente para calcular similitud.

**Información completa**

Empresas con mayor disponibilidad de información.

Estos accesos representarían combinaciones de filtros.

No constituirían nuevas reglas del modelo.

---

### 18. Ficha de empresa

Al seleccionar una empresa, la interfaz abre una ficha individual en un panel lateral.

La información se recupera mediante:

`GET /api/prospects/{expediente_key}`

La ficha se organiza en bloques de:

- identificación;
- priorización;
- perfil financiero;
- explicación;
- emisores comparables;
- advertencias de interpretación.

---

### 19. Identificación

La ficha muestra de forma inmediata:

- razón social;
- RUC;
- provincia;
- tipo de compañía;
- posición en el ranking.

El expediente permanece disponible en los datos del servicio y se utiliza como identificador para recuperar el detalle.

El año operativo y la fecha de decisión forman parte del contexto del producto.

---

### 20. Afinidad bursátil

La ficha muestra claramente:

- posición del ranking;
- Índice de Afinidad Bursátil;
- percentil.

La interfaz mantiene además visible el contexto de versión y configuración del modelo.

Debe conservar una aclaración breve:

> El Índice de Afinidad Bursátil es un indicador de priorización relativa y no una probabilidad de emisión.

---

### 21. Información financiera

La primera versión funcional presenta como perfil financiero principal:

- activos;
- patrimonio;
- ingresos por ventas;
- empleados.

El backend conserva además variables históricas e indicadores adicionales que podrán incorporarse en futuras mejoras de interfaz.

Los valores monetarios se presentan con formato abreviado y legible.

Por ejemplo:

`USD 143,86 millones`

en lugar de mostrar números extensos sin formato.

---

### 22. Indicadores financieros

La API entrega además:

- patrimonio / activos;
- ROA;
- margen neto;
- rotación de activos;
- ROE;
- crecimiento de activos;
- crecimiento de patrimonio;
- crecimiento de ventas;
- crecimiento de empleados.

La primera versión de la interfaz no muestra todos estos indicadores simultáneamente para evitar sobrecargar la ficha.

Podrán incorporarse posteriormente como detalle expandido o sección analítica sin alterar el score.

---

### 23. Calidad de información

La calidad de datos se mantiene visible mediante un indicador resumido.

El sistema contiene diferentes indicadores relacionados con:

- disponibilidad de información histórica;
- activos negativos;
- ventas negativas;
- patrimonio no positivo;
- anomalías de empleados;
- saltos temporales;
- valores consistentes.

La calidad de datos es independiente del score.

Una empresa no debe ser eliminada automáticamente del ranking únicamente por presentar una advertencia de calidad.

---

### 24. Explicabilidad

El sistema implementa explicabilidad mediante SHAP.

En la ficha el usuario puede solicitar el análisis mediante la acción:

**Analizar factores**

La explicación muestra qué variables:

- aumentan la afinidad;
- reducen la afinidad.

La explicación se genera bajo demanda y no se calcula automáticamente para todas las empresas del ranking.

---

### 25. SHAP operacional

La API dispone de:

`GET /api/explainability/prospects/{expediente_key}`

Este servicio calcula una explicación específica para la empresa seleccionada.

La técnica utilizada es:

`SHAP PermutationExplainer`

La explicación se genera con las mismas 25 variables utilizadas por el modelo.

---

### 26. Validación de la explicación

Para cada explicación se verifica que:

`base_value + suma(SHAP) ≈ score del modelo`

En las pruebas funcionales realizadas se obtuvieron diferencias únicamente del orden de precisión numérica.

Esto permite conservar trazabilidad entre:

- score;
- explicación;
- modelo.

---

### 27. Presentación de SHAP al usuario

La interfaz presenta una selección de los factores con mayor contribución local.

Cada factor muestra:

- nombre comprensible;
- magnitud de la contribución SHAP;
- dirección del efecto sobre la afinidad.

Actualmente no se presenta todavía el valor original de cada variable junto al factor.

Esto puede incorporarse como mejora de experiencia, por ejemplo mostrando simultáneamente:

- `Margen neto: 8,4 %`;
- contribución SHAP correspondiente.

Los factores mostrados se construyen siempre con la explicación real de la empresa consultada.

No se utilizan explicaciones genéricas que no correspondan al resultado SHAP.

---

### 28. Sentido de las contribuciones

La interfaz diferencia visualmente:

- contribución positiva;
- contribución negativa.

Una contribución positiva significa que la variable empujó el score hacia arriba respecto del valor base.

Una contribución negativa significa que la variable empujó el score hacia abajo.

Esto no implica causalidad.

---

### 29. Variables globalmente importantes

El análisis global SHAP mostró entre las variables de mayor influencia:

- activos;
- ventas;
- patrimonio anterior;
- crecimiento de patrimonio;
- patrimonio / activos;
- crecimiento de activos;
- patrimonio actual;
- activos anteriores;
- ROA;
- margen neto.

Esta información podrá aparecer en una sección metodológica del sistema.

No deberá utilizarse como sustituto de la explicación individual.

---

### 30. LIME

LIME fue evaluado como técnica complementaria.

Se mantiene como evidencia académica y mecanismo de contraste.

No constituye la técnica principal del producto porque sus explicaciones son aproximaciones locales y no reconstruyen exactamente el score original.

La interfaz comercial no necesita mostrar LIME en su primera versión.

---

### 31. Similitud con emisores históricos

El producto incorpora un componente independiente que permite responder:

> ¿Qué emisores históricos presentaban un perfil financiero parecido al de esta empresa?

La similitud no modifica el score del modelo.

---

### 32. Universo de referencia

Para la fecha de decisión:

`2024-05-01`

se identificaron:

`288 emisores conocidos`

Los emisores utilizados para calcular similitud deben haber sido conocidos hasta esa fecha.

Los emisores posteriores no se utilizan como referencia operacional.

De los perfiles disponibles:

`272`

presentaron información completa para las siete variables requeridas por la metodología.

---

### 33. Variables de similitud

El motor utiliza exactamente siete variables:

1. activos;
2. patrimonio;
3. ingresos por ventas;
4. empleados;
5. patrimonio / activos;
6. ROA;
7. rotación de activos.

Estas variables se seleccionaron por su disponibilidad y capacidad para describir perfiles empresariales comparables.

---

### 34. Normalización de similitud

Las variables no se comparan directamente en valores monetarios originales.

Cada variable se transforma a:

`percentil anual`

Esto reduce el efecto de las diferencias de escala.

Posteriormente se calcula:

`distancia euclidiana`

sobre las siete dimensiones.

---

### 35. Índice de similitud

La similitud se expresa mediante una escala:

`0 a 100`

Una mayor puntuación representa mayor cercanía financiera dentro del espacio utilizado.

No representa:

- probabilidad;
- causalidad;
- recomendación automática;
- predicción independiente.

---

### 36. Comparables

Para cada empresa se almacenan hasta:

`5 emisores históricos comparables`

La ficha podrá mostrar para cada uno:

- posición de similitud;
- nombre;
- RUC;
- similitud;
- año del perfil utilizado;
- fecha de primera inscripción;
- tipo de compañía;
- provincia.

---

### 37. Cobertura del motor de similitud

De las:

`137.156`

empresas operacionales,

`131.320`

disponen de similitud calculable.

`5.836`

no cuentan con información suficiente para aplicar las siete variables.

Estas empresas permanecen dentro del ranking predictivo.

La falta de similitud no implica una baja afinidad bursátil.

---

### 38. Separación entre afinidad y similitud

El sistema mantiene dos señales distintas:

| Señal | Significado |
|---|---|
| Índice de Afinidad Bursátil | Prioridad relativa según el modelo v10 |
| Similitud con emisores | Cercanía financiera con perfiles históricos |

No existe una fórmula como:

`50 % afinidad + 50 % similitud`

Las dos señales deben mostrarse separadamente.

Una combinación futura requeriría validación y una nueva versión metodológica.

---

### 39. Interpretación correcta de comparables

La interfaz puede utilizar textos como:

> Esta empresa presenta un perfil financiero similar al observado en determinados emisores históricos.

No debe utilizar:

> Esta empresa probablemente se convertirá en emisor porque se parece a estos emisores.

La similitud tiene finalidad exploratoria.

---

### 40. Evaluación retrospectiva de similitud

Se realizó un análisis retrospectivo sobre empresas que posteriormente se convirtieron en emisores y que no formaban parte del universo de referencia.

El resultado mostró mayor similitud media en este grupo que en el resto del universo analizado.

Este resultado se utiliza únicamente como evidencia exploratoria.

No constituye demostración de capacidad predictiva y no fue utilizado para ajustar el modelo v10.

---

### 41. API del producto

FastAPI constituye la única capa de acceso para el frontend React.

La interfaz no consulta directamente:

- PostgreSQL;
- CSV;
- modelos Joblib;
- datasets de entrenamiento;
- datasets de TEST.

El flujo implementado es:

`React → FastAPI → Servicios / PostgreSQL / Modelo`

---

### 42. Endpoints implementados

Actualmente se encuentran disponibles:

#### Estado

`GET /api/health`

#### Ranking

`GET /api/prospects`

#### Empresa

`GET /api/prospects/{expediente_key}`

#### Catálogos

`GET /api/catalogs`

#### Explicabilidad global

`GET /api/explainability/global`

#### Explicabilidad individual

`GET /api/explainability/prospects/{expediente_key}`

---

### 43. Ranking API

`GET /api/prospects`

soporta actualmente:

- paginación;
- búsqueda;
- provincia;
- tipo de compañía;
- score mínimo;
- similitud mínima;
- filtro por disponibilidad de comparables.

La respuesta se encuentra ordenada por ranking.

---

### 44. Detalle API

`GET /api/prospects/{expediente_key}`

entrega en una misma consulta:

- identificación;
- ranking;
- score;
- percentil;
- indicadores financieros;
- información histórica;
- calidad;
- resumen de similitud;
- cinco comparables;
- modelo utilizado.

Esto permite construir la ficha de empresa sin que el frontend necesite conocer la estructura interna de PostgreSQL.

---

### 45. Catálogos API

`GET /api/catalogs`

entrega valores normalizados de:

- provincias;
- tipos de compañía.

También entrega conteos.

Esto permite construir filtros dinámicos.

---

### 46. Explicabilidad global API

`GET /api/explainability/global`

permite recuperar las variables con mayor importancia global SHAP.

La API permite utilizar esta información en una futura sección:

**Cómo analiza el modelo**

La primera vista funcional todavía no expone la explicación global como módulo independiente.

Cuando se incorpore, deberá mantenerse separada de la explicación individual de una empresa.

---

### 47. Rendimiento de explicabilidad

El cálculo SHAP presenta un costo inicial superior al de las consultas posteriores.

La implementación reutiliza el runtime de explicabilidad una vez inicializado para evitar reconstrucciones innecesarias en cada solicitud.

Las consultas posteriores se verificaron con tiempos adecuados para el prototipo en el entorno local.

La interfaz muestra un estado de carga mientras obtiene la explicación bajo demanda.

La prioridad metodológica es mantener fidelidad con el score del modelo congelado.

---

### 48. Diseño general de interfaz

La interfaz implementada sigue un enfoque:

- profesional;
- ejecutivo;
- sobrio;
- claro;
- orientado a negocio;
- fácil de explorar.

La primera versión utiliza React y TypeScript sobre Vite.

Versiones verificadas:

- Node.js `24.19.0`;
- npm `11.17.0`;
- React `19.3.0`;
- React DOM `19.3.0`;
- TypeScript `6.0.3`;
- Vite `8.3.2`;
- Lucide React `1.52.0`;
- React Router DOM `7.18.4`;
- Recharts `3.10.1`;
- Oxlint `1.86.0`.

React Router DOM y Recharts están disponibles para evolución posterior. La primera vista funcional no depende todavía de navegación compleja ni de gráficos construidos con Recharts.

La interfaz evita una apariencia excesivamente técnica.

El especialista puede comprender la información sin conocimientos de ciencia de datos.

---

### 49. Jerarquía visual

La primera versión prioriza:

1. empresa;
2. ranking;
3. afinidad bursátil;
4. información financiera;
5. factores explicativos;
6. similitud con emisores;
7. calidad de datos;
8. información técnica.

Los elementos técnicos se mantienen en un segundo nivel.

---

### 50. Componentes principales implementados

La primera versión funcional contiene:

| Componente | Función |
|---|---|
| Resumen | Visión general del universo |
| Ranking | Priorización de empresas |
| Búsqueda | Localización de empresas |
| Filtros | Exploración por provincia y tipo |
| Paginación | Navegación del universo |
| Empresa | Ficha individual |
| Afinidad | Score, percentil y posición |
| Explicabilidad | Factores SHAP bajo demanda |
| Emisores comparables | Hasta cinco perfiles históricos similares |
| Calidad | Indicador resumido de disponibilidad |
| Modelo | Versión y configuración v10 |
| Advertencias | Limitaciones de interpretación |

La primera entrega prioriza una vista integrada antes de separar estas funciones en múltiples páginas.

---

### 51. Módulo de monitoreo

El monitoreo operacional forma parte de la arquitectura prevista, pero todavía no está implementado como módulo completo de producto.

Posteriormente deberá permitir analizar:

- distribución del score;
- cobertura;
- cambios de variables;
- faltantes;
- categorías nuevas;
- concentración del ranking;
- PSI;
- desempeño cuando existan labels maduros.

No debe mostrarse como funcionalidad terminada hasta completar su implementación.

---

### 52. Flujo principal del usuario

El flujo implementado es:

`Resumen → Ranking → Búsqueda/Filtros → Empresa → Afinidad → Explicación → Comparables → Análisis → Decisión`

El objetivo es permitir pasar progresivamente:

`Universo amplio → empresas priorizadas → análisis individual`

---

### 53. Supervisión humana

Prospect Finder BVQ implementa el principio:

`IA → Priorización → Explicación → Especialista → Decisión`

No implementa:

`IA → Decisión`

El sistema no realiza automáticamente:

- aprobación;
- rechazo;
- contacto;
- recomendación regulatoria;
- evaluación legal;
- evaluación crediticia.

---

### 54. Top-K

Top 50, Top 100 y Top 200 fueron utilizados durante la evaluación metodológica.

En TEST, la concentración de positivos en los primeros puestos fue inferior a la observada en algunos períodos de backtesting.

Por esta razón, el producto no debe limitar al especialista únicamente al Top 200.

La interfaz permitirá explorar todo el universo mediante:

- ranking;
- páginas;
- búsqueda;
- filtros.

---

### 55. Sesgos y concentración

La evaluación de v10 identificó posibles concentraciones relacionadas con:

- tamaño empresarial;
- disponibilidad de información;
- tipo de compañía;
- provincia.

Estas características sirven para monitoreo.

No deben convertirse automáticamente en reglas de exclusión.

Provincia no es una variable predictiva del modelo.

---

### 56. Consideración temporal

Los datos operacionales corresponden al corte establecido.

La interfaz mantiene visible el contexto temporal mediante:

- año de información;
- fecha de decisión.

Esto evita que el usuario interprete los datos como información financiera en tiempo real.

Para la versión actual:

**Información financiera:** 2023

**Fecha de decisión:** 01 de mayo de 2024

---

### 57. Actualización futura

Cuando exista una nueva base financiera suficientemente completa, el proceso esperado será:

`Nuevos datos → Validación → Features → Scoring → Ranking → Similitud → PostgreSQL → Publicación`

Actualizar el ranking no significa reentrenar automáticamente el modelo.

---

### 58. Reentrenamiento

v10 permanece congelado.

Solo deberá considerarse una nueva versión cuando exista evidencia suficiente relacionada con:

- deterioro;
- cambio de distribución;
- nuevas variables;
- nuevos períodos;
- nueva definición de target;
- nueva metodología;
- nueva arquitectura del modelo.

Una modificación significativa deberá registrarse como:

`v11`

o una versión posterior.

---

### 59. Estado actual del producto

| Componente | Estado |
|---|---|
| Modelo v10 | Implementado |
| Ranking operacional | Implementado |
| Universo prospectable | Implementado |
| Percentiles | Implementados |
| Calidad de datos | Implementada |
| Similitud con emisores | Implementada |
| Cinco comparables | Implementados |
| PostgreSQL | Implementado |
| FastAPI | Implementado |
| Búsqueda API | Implementada |
| Paginación API | Implementada |
| Filtro API por provincia | Implementado |
| Filtro API por tipo | Implementado |
| Filtro API por score | Implementado |
| Filtro API por similitud | Implementado |
| Filtro API por comparables | Implementado |
| Catálogos | Implementados |
| SHAP global API | Implementado |
| SHAP individual | Implementado |
| Pruebas automáticas backend | 12 aprobadas |
| Frontend React | Implementado |
| Integración React–FastAPI | Implementada |
| Ranking web | Implementado |
| Búsqueda web | Implementada |
| Filtros web por provincia y tipo | Implementados |
| Paginación web | Implementada |
| Ficha empresarial web | Implementada |
| Comparables web | Implementados |
| SHAP web | Implementado |
| Build frontend | Correcto |
| Lint frontend | 0 warnings / 0 errors |
| Pruebas automatizadas frontend | Pendientes |
| Autenticación institucional | Pendiente |
| Monitoreo operacional completo | Pendiente |
| Validación con especialistas | Pendiente |

---

### 60. Pruebas

El backend dispone de pruebas automáticas con pytest.

Estado actual:

`12 pruebas aprobadas`

Las pruebas cubren:

- salud de la API;
- ranking;
- filtros;
- detalle;
- catálogos;
- explicabilidad;
- manejo de errores.

El frontend fue validado mediante:

`npm --prefix frontend run build`

con build correcto y:

`1898 modules transformed`

También mediante:

`npm --prefix frontend run lint`

con:

`0 warnings`

y:

`0 errors`.

Adicionalmente se ejecutaron verificaciones manuales desde navegador sobre:

- ranking;
- búsqueda;
- filtros;
- paginación;
- ficha;
- comparables;
- SHAP positivo y negativo.

Las pruebas automatizadas específicas del frontend todavía están pendientes.

Estas validaciones técnicas no sustituyen la validación funcional con especialistas.

---

### 61. Validación con especialistas

La propuesta del Capstone requiere validación funcional con al menos:

`2 especialistas de la BVQ`

Esta actividad todavía debe realizarse.

La validación deberá revisar aspectos como:

- utilidad del ranking;
- claridad de los indicadores;
- utilidad de los filtros;
- comprensión del score;
- utilidad de SHAP;
- relevancia de comparables;
- claridad de advertencias;
- facilidad de navegación.

Los resultados deberán registrarse como evidencia del proyecto.

---

### 62. Seguridad

El producto mantiene:

- separación entre frontend y base de datos;
- acceso a través de FastAPI;
- configuración mediante variables de entorno;
- ausencia de credenciales reales en Git;
- mínima exposición de datos;
- separación entre datasets de entrenamiento y producto.

Debe añadirse control de acceso si la solución avanza hacia una implementación institucional.

Las credenciales incluidas actualmente en Docker corresponden exclusivamente al entorno local de desarrollo.

La configuración frontend puede utilizar:

`VITE_API_URL`

Las variables con prefijo `VITE_*` son visibles para el navegador y no deben contener:

- contraseñas;
- tokens privados;
- credenciales de base de datos;
- secretos institucionales.

---

### 63. Trazabilidad visible

La interfaz permite identificar directamente o mediante la ficha:

- versión del modelo;
- configuración;
- año de información;
- fecha de decisión;
- ranking;
- score;
- calidad;
- comparables.

La trazabilidad técnica completa permanece disponible en la documentación y backend.

---

### 64. Advertencias de interpretación

La interfaz y la documentación deben mantener claro que:

**El score no es una probabilidad.**

**La similitud no es una predicción.**

**SHAP no demuestra causalidad.**

**Una posición alta no implica que una empresa deba convertirse en emisor.**

**Una posición baja no significa que una empresa no pueda convertirse en emisor.**

**El especialista mantiene la decisión final.**

---

### 65. Lenguaje de negocio

La interfaz evitará, cuando sea posible, términos como:

- vector de features;
- logit;
- SHAP value;
- distancia euclidiana;
- clasificador;
- inferencia.

Estos conceptos permanecerán disponibles en la documentación técnica.

Para el usuario se priorizarán expresiones como:

- afinidad;
- prioridad;
- factores que aumentan la afinidad;
- factores que reducen la afinidad;
- empresas comparables;
- calidad de información.

---

### 66. Resultado actual y cierre esperado

Prospect Finder BVQ ya permite que un especialista explore:

`137.156 empresas`

y reduzca progresivamente el universo de análisis utilizando:

`Ranking + Búsqueda + Filtros + Información financiera + Explicabilidad + Comparables`

El flujo funcional es:

`Explorar → Filtrar → Priorizar → Comprender → Comparar → Analizar → Decidir`

Para completar el cierre del producto permanecen principalmente:

- pruebas automatizadas específicas del frontend;
- pruebas funcionales finales estructuradas;
- validación con al menos dos especialistas de la BVQ;
- componentes pendientes de MLOps;
- monitoreo operacional;
- documentación e informe final.

La finalidad del sistema es mejorar la capacidad de prospección y reducir el esfuerzo requerido para analizar manualmente un universo empresarial amplio.

Prospect Finder BVQ permanece como herramienta de apoyo analítico y comercial, no como sistema automatizado de decisión.

