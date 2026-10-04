Prospect Finder BVQ
Arquitectura de la solución v10
1. Objetivo
Este documento describe la arquitectura de Prospect Finder BVQ, sistema basado en aprendizaje automático orientado a identificar y priorizar empresas con potencial de convertirse en emisores del mercado de valores ecuatoriano.
La arquitectura mantiene el enfoque cliente-servidor definido en la propuesta del Capstone y separa claramente los componentes de datos, procesamiento, modelo, servicios e interfaz.
El objetivo de esta separación es facilitar:
mantenimiento;
reproducibilidad;
actualización de datos;
trazabilidad;
versionamiento del modelo;
explicabilidad;
seguridad;
evolución futura de la solución.
Prospect Finder BVQ funciona como una herramienta de apoyo a la prospección comercial.
No realiza decisiones automáticas de aceptación, rechazo, aprobación regulatoria, evaluación legal o evaluación crediticia.
La decisión final permanece bajo responsabilidad del especialista de la Bolsa de Valores Quito.
---
2. Arquitectura general
La arquitectura se organiza en las siguientes capas:
Fuentes de información → ETL y preparación → Dataset analítico → Motor de IA v10 → Explicabilidad y comparables → API → Aplicación web → Especialista BVQ
Estas capas mantienen separadas las responsabilidades del sistema y permiten modificar un componente sin afectar necesariamente al resto.
---
3. Capas de la solución
La arquitectura de Prospect Finder BVQ está compuesta por siete capas principales:
Capa	Función
Fuentes de información	Proveen información empresarial, financiera e histórica
Procesamiento y ETL	Limpia, integra, valida y transforma los datos
Datos analíticos	Almacena las variables utilizadas por el modelo
Motor analítico	Genera el score y ranking
Explicabilidad y comparables	Explica resultados y permite identificar perfiles similares
API	Expone las funcionalidades del sistema
Interfaz web	Permite al especialista explorar y analizar resultados
---
4. Fuentes de información
La primera capa contiene las fuentes utilizadas para construir el universo de empresas y las variables analíticas.
Entre la información utilizada se encuentran:
identificación de empresas;
información financiera histórica;
activos;
patrimonio;
ingresos por ventas;
número de empleados;
tipo de compañía;
provincia;
antecedentes históricos de empresas emisoras.
La información utilizada debe corresponder a fuentes públicas o institucionales autorizadas para el desarrollo del proyecto.
El prototipo se mantiene separado de los sistemas transaccionales de la Bolsa de Valores Quito.
---
5. Unidad de análisis
Durante el entrenamiento y evaluación del modelo la unidad analítica utilizada es:
empresa-año
Esto permite representar la situación de una empresa en un periodo determinado y analizar si posteriormente se convirtió en emisor.
Para la aplicación operativa, la unidad cambia a:
empresa
Cada empresa debe aparecer una sola vez en el ranking utilizando su última información financiera disponible.
Por tanto:
Entorno	Unidad
Entrenamiento	Empresa-año
Backtesting	Empresa-año
Evaluación TEST	Empresa-año
Producto operativo	Empresa con última observación disponible
---
6. Procesamiento y ETL
La preparación de datos se implementa mediante Python y pandas.
El proceso sigue la siguiente secuencia:
Extracción → Homologación → Limpieza → Integración → Validación → Construcción de variables → Construcción del target → Dataset analítico
Durante esta fase se realizan controles sobre:
tipos de datos;
valores faltantes;
duplicados;
inconsistencias;
valores negativos;
valores extremos;
continuidad temporal;
disponibilidad de información histórica;
anomalías en número de empleados;
consistencia de activos;
consistencia de ventas;
consistencia de patrimonio.
---
7. Construcción de variables
El modelo v10 utiliza 25 variables.
Estas variables se agrupan en:
Variables de escala
activos;
patrimonio;
ingresos por ventas;
número de empleados.
Variables históricas
activos del periodo anterior;
patrimonio del periodo anterior;
ventas del periodo anterior;
empleados del periodo anterior.
Indicadores financieros
patrimonio sobre activos;
ROA;
margen neto;
rotación de activos;
ROE.
Variables de crecimiento
crecimiento de activos;
crecimiento de patrimonio;
crecimiento de ventas;
crecimiento de empleados.
Variables de consistencia y calidad
disponibilidad de información del periodo anterior;
activos negativos;
ventas negativas;
anomalías en empleados;
patrimonio no positivo.
Variable categórica
tipo de compañía.
---
8. Variable objetivo
La variable objetivo utilizada es:
`TARGET_24M`
Esta variable identifica si una empresa se convierte en emisor dentro de los 24 meses posteriores al punto de observación.
El problema se aborda como una tarea de clasificación supervisada con fuerte desbalance entre clases.
El modelo no intenta predecir el momento exacto en que una empresa emitirá valores.
Su finalidad es generar una señal de priorización.
---
9. Separación temporal
Para reducir riesgo de fuga de información se definió una separación temporal.
Conjunto	Periodo
TRAIN	2012–2018
EMBARGO 1	2019
VALIDATION	2020
EMBARGO 2	2021
TEST	2022–2023
El conjunto TEST permaneció cerrado hasta finalizar la selección del modelo.
Esta separación permite evaluar el comportamiento del sistema en periodos posteriores al entrenamiento.
---
10. Dataset analítico
El dataset financiero final utilizado por v10 contiene la información preparada para el modelo.
Archivo principal:
`data/processed/v10_features_financial_2012_2023.csv.gz`
Este dataset contiene:
identificadores;
año;
target;
split temporal;
variables empresariales;
variables financieras;
variables históricas;
variables de crecimiento;
indicadores de calidad.
La preparación del dataset es reproducible mediante los scripts almacenados en el repositorio.
---
11. Persistencia de datos
La propuesta original contempla PostgreSQL como base de datos de la aplicación.
Durante la fase experimental, la persistencia se ha realizado mediante:
CSV;
CSV.GZ;
JSON;
Joblib.
Esto permite mantener reproducibilidad durante la construcción y evaluación del modelo.
Para el prototipo web, PostgreSQL constituye la arquitectura objetivo para consultar de forma estructurada:
empresas;
última información disponible;
indicadores;
score;
ranking;
calidad de datos;
explicaciones;
comparables;
información del modelo.
Por tanto, se distinguen dos contextos:
Contexto	Tecnología
Experimentación	CSV / CSV.GZ / JSON
Modelo	Joblib
Aplicación web	PostgreSQL
Documentación	Markdown
Versionamiento	Git
---
12. Motor analítico
Durante el proyecto se evaluaron diferentes alternativas de aprendizaje automático.
Entre los modelos evaluados se encuentran:
Regresión Logística;
HistGradientBoosting;
MLPClassifier.
El modelo seleccionado para v10 es:
`v10_hgb_financial_c3`
Configuración:
`C3_CONSERVATIVE`
El estimador utilizado es:
`HistGradientBoostingClassifier`
---
13. Score de priorización
El modelo recibe las 25 variables de una empresa y genera un valor numérico entre 0 y 1.
Este resultado se utiliza como:
Score de priorización
El score no debe interpretarse como una probabilidad calibrada.
Por ejemplo:
`0.90`
no significa:
`90 % de probabilidad de convertirse en emisor`
El score se utiliza para ordenar empresas de forma relativa dentro del universo analizado.
El flujo es:
Empresa → Variables → Modelo v10 → Score → Ranking
---
14. Evaluación del modelo
Las principales métricas utilizadas fueron:
PR-AUC;
ROC-AUC;
Precision@K;
Recall@K;
Lift@K.
Debido al fuerte desbalance del target, las métricas de ranking adquieren especial relevancia para evaluar la utilidad del sistema.
El conjunto TEST contiene:
260,445 observaciones;
54 positivos.
Resultados oficiales de v10 sobre TEST:
Métrica	Resultado
PR-AUC	0.007468801
ROC-AUC	0.934603901
Las métricas Top-K mostraron que el modelo conserva capacidad de ordenamiento general, aunque la concentración de positivos en los primeros puestos fue inferior a la observada durante el backtesting.
Por esta razón el producto debe utilizar el ranking como mecanismo de apoyo y no como una regla automática de decisión.
---
15. Ranking operativo
En producción no se deben mostrar múltiples observaciones históricas de una misma empresa.
El proceso operativo debe utilizar:
Última información disponible → Construcción de variables → Modelo v10 → Score → Ranking actual
Cada empresa aparecerá una sola vez.
Las empresas que ya hayan sido registradas como emisores deberán excluirse del universo prospectable correspondiente.
---
16. Explicabilidad
La arquitectura incorpora una capa específica de explicabilidad.
Durante el proyecto se utilizaron:
Permutation Importance;
SHAP;
LIME.
Estas técnicas no modifican el modelo.
Su función es ayudar a comprender el comportamiento de las predicciones.
---
17. Permutation Importance
Permutation Importance fue utilizada para analizar la importancia global de las variables.
La técnica permite evaluar cuánto cambia el desempeño del modelo cuando se altera individualmente una variable.
Este análisis complementa la interpretación obtenida mediante SHAP.
---
18. SHAP
SHAP fue seleccionado como la técnica principal de explicabilidad para Prospect Finder BVQ.
Permite realizar:
interpretación global;
explicación individual;
identificación de variables que elevan el score;
identificación de variables que reducen el score.
En los casos analizados, SHAP reconstruyó exactamente el score original del modelo.
Las variables con mayor importancia global observada mediante SHAP incluyen principalmente:
activos;
ventas;
patrimonio;
crecimiento patrimonial;
relación patrimonio sobre activos;
crecimiento de activos;
ROA;
margen neto.
La interfaz web no mostrará necesariamente los valores técnicos de SHAP.
Las contribuciones serán traducidas a explicaciones comprensibles.
Ejemplo:
Factores que elevan la prioridad
nivel de activos elevado;
ventas relevantes;
patrimonio sólido;
rentabilidad positiva;
crecimiento patrimonial.
Factores que reducen la prioridad
menor escala empresarial;
reducción de activos;
menor volumen de ventas;
información incompleta.
---
19. LIME
LIME fue utilizado como técnica complementaria.
Su función dentro del proyecto es:
contrastar explicaciones locales;
evaluar otra técnica de interpretabilidad;
analizar diferencias de fidelidad.
LIME genera una aproximación local del comportamiento del modelo.
En los casos evaluados no reprodujo exactamente el score original, por lo que se mantiene como técnica complementaria y no como explicación principal del producto.
---
20. Flujo de explicabilidad
El flujo de explicación será:
Empresa → Modelo v10 → Score → SHAP → Contribuciones por variable → Traducción a lenguaje de negocio → Especialista
Las explicaciones describen el comportamiento del modelo.
No representan relaciones causales.
Por tanto, no debe afirmarse que una empresa se convertirá en emisor únicamente porque determinadas variables tengan contribuciones positivas.
---
21. Motor de comparables
La arquitectura contempla un componente independiente para identificar empresas financieramente similares.
Su función será responder:
¿Qué empresas presentan un perfil financiero parecido?
El motor utilizará variables como:
activos;
patrimonio;
ventas;
empleados;
ROA;
ROE;
margen;
rotación;
crecimiento.
Antes del cálculo de similitud se aplicarán transformaciones y normalización para evitar que las variables de mayor escala dominen el resultado.
El motor de comparables será independiente del score v10.
---
22. Similitud con emisores históricos
La misma arquitectura permitirá comparar empresas prospectables con perfiles históricos de emisores.
El flujo será:
Empresa prospectable → Perfil financiero → Perfiles históricos de emisores → Cálculo de similitud → Emisores comparables
La similitud será una herramienta exploratoria.
No será interpretada como probabilidad.
---
23. Separación entre score y similitud
El producto manejará dos señales diferentes:
Señal	Significado
Score v10	Prioridad generada por el modelo
Similitud	Cercanía del perfil financiero
Estas señales no se combinarán inicialmente mediante una fórmula ponderada.
Una eventual combinación deberá validarse experimentalmente como una nueva versión.
---
24. Servicios API
La arquitectura propuesta utiliza FastAPI como capa de servicios.
FastAPI permitirá separar:
interfaz;
lógica de negocio;
datos;
modelo;
explicabilidad;
comparables.
La interfaz web no deberá acceder directamente al modelo, archivos CSV o base de datos.
Todas las operaciones deberán realizarse mediante servicios controlados.
---
25. Servicios previstos
Los servicios principales serán:
`GET /api/health`
`GET /api/model`
`GET /api/ranking`
`GET /api/companies/{id}`
`GET /api/companies/{id}/explanation`
`GET /api/companies/{id}/comparables`
`GET /api/companies/{id}/similar-issuers`
`GET /api/filters`
`GET /api/monitoring`
---
26. Servicio de ranking
El servicio:
`GET /api/ranking`
permitirá consultar el universo priorizado.
Entre los filtros previstos se encuentran:
provincia;
tipo de compañía;
prioridad;
activos;
patrimonio;
ventas;
ROA;
ROE;
calidad de datos.
El servicio devolverá información como:
posición;
empresa;
score;
prioridad;
indicadores principales;
calidad de información.
---
27. Servicio de empresa
El servicio:
`GET /api/companies/{id}`
permitirá consultar:
identificación;
información societaria;
score;
posición;
activos;
patrimonio;
ventas;
empleados;
indicadores financieros;
evolución;
calidad de datos.
---
28. Servicio de explicación
El servicio:
`GET /api/companies/{id}/explanation`
proporcionará:
score;
principales factores positivos;
principales factores negativos;
advertencias de calidad.
La explicación deberá mantener trazabilidad hacia las contribuciones SHAP utilizadas.
---
29. Servicio de comparables
El servicio:
`GET /api/companies/{id}/comparables`
permitirá recuperar empresas con perfiles financieros similares.
Los resultados podrán incluir:
empresa;
índice de similitud;
score v10;
activos;
patrimonio;
ventas;
ROA;
tipo de compañía.
---
30. Interfaz web
La aplicación será utilizada desde un navegador.
El objetivo de la interfaz será facilitar:
exploración;
priorización;
filtrado;
comparación;
interpretación;
análisis.
El usuario no requerirá conocimientos de programación ni aprendizaje automático.
---
31. Módulos principales de la interfaz
El prototipo deberá incluir como mínimo:
Módulo	Función

Resumen	Indicadores generales del universo
Ranking	Priorización de empresas
Filtros	Segmentación del universo
Empresa	Ficha financiera
Explicabilidad	Factores asociados con el score
Comparables	Empresas financieramente similares
Emisores similares	Comparación con perfiles históricos
Calidad	Estado de disponibilidad de datos
Modelo	Información de versión
Riesgos	Principales limitaciones
Monitoreo	Indicadores de estabilidad
---
32. Flujo del usuario
El flujo principal será:
Inicio → Ranking → Filtros → Selección de empresa → Indicadores → Explicación → Comparables → Análisis → Decisión del especialista
La decisión comercial final no será automatizada.
---
33. Seguridad
La arquitectura deberá contemplar:
autenticación;
autorización;
control de acceso;
separación de componentes;
protección de credenciales;
registro de acciones relevantes;
mínima exposición de información.
Las credenciales no deberán almacenarse directamente en:
código fuente;
repositorio Git;
archivos públicos.
La configuración sensible deberá administrarse mediante variables de entorno o mecanismos equivalentes.
---
34. Separación de responsabilidades
Cada componente tendrá una responsabilidad específica.
Componente	Responsabilidad
Fuentes	Proporcionar información
ETL	Preparar y validar datos
Datos	Almacenar información
Modelo	Generar score
SHAP	Explicar predicción
Comparables	Calcular similitud
API	Exponer servicios
Interfaz	Presentar resultados
Especialista	Tomar decisiones
Esta separación facilita mantenimiento y evolución.
---
35. Trazabilidad
Cada resultado deberá poder relacionarse con:
versión del modelo;
configuración;
fecha de datos;
fecha de scoring;
variables utilizadas;
calidad de información;
versión del proceso de preparación.
Ejemplo:
Modelo: `v10_hgb_financial_c3`
Configuración: `C3_CONSERVATIVE`
Periodo de datos: última información disponible
Versión: `v10`
---
36. Versionamiento
La versión actual del modelo es:
`v10`
Esta versión permanece congelada.
Los resultados obtenidos sobre TEST no se utilizarán para modificar retroactivamente sus parámetros.
Cualquier cambio importante en:
target;
variables;
transformación de datos;
arquitectura del modelo;
hiperparámetros;
reglas de scoring;
deberá registrarse como una nueva versión.
La siguiente versión experimental será:
`v11`
---
37. Monitoreo
La arquitectura incorpora monitoreo sobre datos, features, score y ranking.
Datos
Se revisarán:
valores faltantes;
cobertura;
nuevas categorías;
cambios de distribución.
Variables
Se revisarán:
PSI;
cambios de distribución;
missingness;
estabilidad temporal.
Score
Se revisarán:
media;
mediana;
distribución;
concentración.
Ranking
Se revisará exposición por:
tamaño;
tipo de compañía;
provincia;
calidad de información.
Desempeño
Cuando existan labels maduros se calcularán:
PR-AUC;
ROC-AUC;
Precision@K;
Recall@K;
Lift@K.
---
38. Sesgos y riesgos
El análisis de v10 identificó concentraciones relacionadas con:
tamaño empresarial;
disponibilidad de información;
tipo de compañía;
ubicación geográfica.
Estas concentraciones serán monitoreadas.
No se utilizarán automáticamente como reglas de exclusión.
La provincia no forma parte de las variables del modelo v10 y será utilizada únicamente como atributo descriptivo y de auditoría.
---
39. MLOps y reproducibilidad
La arquitectura incorpora principios de MLOps para garantizar trazabilidad.
El flujo conceptual es:
Código → Git → Datos versionados → Experimentos → Modelo versionado → Contenedor → Aplicación
Los componentes de MLOps deberán permitir identificar:
qué datos fueron utilizados;
qué código fue ejecutado;
qué modelo generó el resultado;
qué métricas fueron obtenidas;
qué versión se encuentra activa.
La implementación específica de DVC, MLflow y Docker se documentará de manera independiente.
---
40. Estado actual del proyecto
El estado de los componentes es:
Componente	Estado
Integración de datos	Implementado
ETL	Implementado
Construcción de variables	Implementado
Target temporal	Implementado
Backtesting	Implementado
Modelos clásicos	Implementado
Red neuronal MLP	Implementado
Selección del modelo	Implementado

Evaluación TEST	Implementado
Permutation Importance	Implementado
SHAP	Implementado
LIME	Implementado
Estabilidad temporal	Implementado
Sesgos y riesgos	Implementado
Diseño operativo	Implementado
Arquitectura lógica	Documentada
PostgreSQL	Pendiente
FastAPI	Pendiente
Motor de comparables	Pendiente
Interfaz web	Pendiente
MLOps operativo	Pendiente
Validación con especialistas	Pendiente
---
41. Arquitectura objetivo del prototipo
La arquitectura final del prototipo será:
Fuentes de información → ETL y preparación de datos → Datos procesados → Modelo v10 → Score de priorización → SHAP y motor de comparables → PostgreSQL → FastAPI → Aplicación web Prospect Finder BVQ → Especialista BVQ
Esta arquitectura mantiene la separación definida en la propuesta original del proyecto:
Datos → Procesamiento → Motor analítico → Servicios API → Interfaz
---
42. Evolución respecto de la propuesta inicial
La arquitectura conceptual definida al inicio del proyecto se mantiene.
La principal evolución ocurrió dentro del motor analítico.
Inicialmente se contemplaron diferentes alternativas de aprendizaje automático clásico y redes neuronales.
Durante la experimentación se evaluaron modelos bajo condiciones comparables y se seleccionó finalmente:
`HistGradientBoostingClassifier`
como modelo v10.
También se incorporaron componentes adicionales de:
backtesting temporal;
métricas Top-K;
explicabilidad;
SHAP;
LIME;
estabilidad temporal;
análisis de sesgos;
evaluación de riesgos.
La arquitectura se mantiene consistente con el planteamiento original, pero incorpora la evidencia obtenida durante el desarrollo.
---
43. Principio de desacoplamiento
La interfaz web no dependerá directamente de la implementación interna del modelo.
La comunicación será:
Interfaz web → API → Servicio analítico → Modelo
Esto permitirá que una futura versión v11 pueda reemplazar v10 sin necesidad de reconstruir completamente la interfaz.
---
44. Principio de supervisión humana
Prospect Finder BVQ implementa el siguiente principio:
IA → Priorización → Explicación → Especialista → Decisión
No implementa:
IA → Decisión automática
Este principio es especialmente importante debido a:
fuerte desbalance del target;
variación temporal del desempeño;
existencia de falsos positivos;
concentración del ranking;
existencia de factores empresariales no contenidos en los datos.
---
45. Resultado esperado
La arquitectura permitirá convertir el modelo experimental v10 en un prototipo funcional para apoyo a la prospección.
El producto integrará:
Datos + IA + Ranking + Explicabilidad + Comparables + Filtros + Monitoreo
El especialista podrá seguir un flujo de trabajo estructurado:
Explorar → Filtrar → Priorizar → Comprender → Comparar → Analizar → Decidir
Prospect Finder BVQ permanecerá como herramienta de apoyo analítico y no como sistema automatizado de decisión.
---
Estado del documento
Arquitectura lógica: definida.
Arquitectura de datos: definida.
Arquitectura analítica: implementada.
Modelo v10: implementado y congelado.
Explicabilidad SHAP/LIME: implementada.
API FastAPI: pendiente.
PostgreSQL: pendiente.
Motor de comparables: pendiente.
Interfaz web: pendiente.
MLOps operativo: pendiente.
Validación con especialistas: pendiente.