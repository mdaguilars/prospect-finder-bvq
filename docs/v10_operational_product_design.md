# Prospect Finder BVQ
## Diseño operativo del producto v10

### 1. Propósito

Prospect Finder BVQ es una herramienta de apoyo analítico para el proceso de prospección de potenciales emisores de la Bolsa de Valores Quito.

Su propósito es permitir que los especialistas analicen un universo amplio de empresas, identifiquen aquellas con mayor afinidad histórica con empresas que posteriormente se convirtieron en emisores y prioricen su revisión comercial.

La herramienta no determina si una empresa debe convertirse en emisor, no constituye una evaluación financiera, legal o regulatoria y no reemplaza el criterio de los especialistas de la Bolsa de Valores Quito.

El modelo funciona como un mecanismo de priorización y exploración.

---

### 2. Usuario principal

El usuario principal del prototipo es un especialista autorizado de la Bolsa de Valores Quito involucrado en actividades de análisis, prospección o desarrollo del mercado.

El sistema está pensado inicialmente como una herramienta interna.

---

### 3. Unidad operativa

Durante el desarrollo del modelo, la unidad de análisis utilizada fue empresa-año.

Para el producto operativo, esta estructura debe transformarse en una vista actual de empresas.

Cada empresa debe aparecer una sola vez utilizando la última observación financiera disponible que cumpla las reglas de elegibilidad.

Por tanto:

| Entorno | Unidad |
|---|---|
| Entrenamiento y evaluación | Empresa-año |
| Producto operativo | Empresa con última información disponible |

Las empresas que ya hayan sido registradas previamente como emisores deben excluirse del universo prospectable.

---

### 4. Ranking principal

La pantalla principal debe presentar las empresas ordenadas según el score generado por el modelo seleccionado:

`v10_hgb_financial_c3`

El score debe interpretarse exclusivamente como un indicador de priorización.

No debe presentarse como probabilidad.

Por ejemplo, un score de:

`0.82`

no significa:

`82 % de probabilidad de convertirse en emisor`.

La interfaz utilizará preferentemente el término:

**Score de priorización**

y podrá acompañarlo de una clasificación relativa:

| Clasificación | Interpretación |
|---|---|
| Muy alta | Empresas ubicadas en la parte superior del ranking |
| Alta | Empresas con score elevado |
| Media | Empresas con afinidad intermedia |
| Baja | Empresas con menor prioridad relativa |

Los límites de estas categorías deberán definirse utilizando percentiles del ranking operativo y no probabilidades.

---

### 5. Pantalla principal

La pantalla inicial del sistema debe ofrecer una visión ejecutiva del universo prospectable.

Debe mostrar como mínimo:

| Indicador | Descripción |
|---|---|
| Empresas analizadas | Total de empresas actualmente elegibles |
| Prioridad muy alta | Empresas ubicadas en el segmento superior |
| Prioridad alta | Empresas ubicadas en el siguiente segmento |
| Información completa | Empresas con alta cobertura de variables |
| Última actualización | Fecha de actualización del universo |

Debajo de los indicadores se mostrará el ranking de empresas.

---

### 6. Tabla de ranking

La tabla principal deberá incluir como mínimo:

| Campo | Descripción |
|---|---|
| Ranking | Posición de la empresa |
| Empresa | Razón social |
| RUC | Identificador |
| Score de priorización | Score generado por el modelo |
| Prioridad | Muy alta, alta, media o baja |
| Activos | Último valor disponible |
| Patrimonio | Último valor disponible |
| Ventas | Último valor disponible |
| ROA | Rentabilidad sobre activos |
| ROE | Rentabilidad sobre patrimonio |
| Provincia | Ubicación registrada |
| Tipo de compañía | Forma societaria |
| Calidad de datos | Nivel de cobertura de información |

La tabla debe permitir ordenar los resultados y acceder al detalle de cada empresa.

---

### 7. Búsqueda

El sistema deberá permitir localizar directamente una empresa mediante:

Razón social.

RUC.

La búsqueda no debe modificar el score de la empresa.

---

### 8. Filtros operativos

Los filtros servirán para explorar el universo sin alterar el score original del modelo.

Se contemplarán filtros por:

| Grupo | Filtros |
|---|---|
| Ranking | Nivel de prioridad |
| Ubicación | Provincia |
| Empresa | Tipo de compañía |
| Tamaño | Activos, patrimonio, ventas y empleados |
| Rentabilidad | ROA, ROE y margen neto |
| Crecimiento | Activos, patrimonio, ventas y empleados |
| Calidad | Disponibilidad de historial y datos faltantes |
| Información | Año de última información disponible |

Los filtros únicamente reducirán el universo visible.

No recalcularán el modelo.

---

### 9. Filtros sugeridos

Además de los filtros manuales, la aplicación podrá incorporar filtros predefinidos para facilitar la exploración.

Ejemplos:

**Mayor prioridad IA**

Empresas ubicadas en la parte superior del ranking.

**Empresas grandes**

Empresas pertenecientes a los rangos superiores de activos.

**Crecimiento positivo**

Empresas con crecimiento positivo en variables financieras relevantes.

**Información completa**

Empresas con alta cobertura de datos.

**Perfil similar a emisores**

Empresas con características financieras cercanas a perfiles históricos de emisores.

Estos filtros son herramientas de exploración y no reglas automáticas de selección.

---

### 10. Ficha de empresa

Al seleccionar una empresa, el sistema deberá abrir una ficha de análisis.

La ficha debe incluir las siguientes secciones:

| Sección | Contenido |
|---|---|
| Identificación | Razón social, RUC, provincia y tipo de compañía |
| Ranking | Posición y score de priorización |
| Información financiera | Activos, patrimonio, ventas y empleados |
| Indicadores | ROA, ROE, margen y rotación |
| Evolución | Comparación con periodos anteriores |
| Explicación | Factores asociados con el score |
| Calidad | Cobertura y disponibilidad de datos |
| Comparables | Empresas con perfiles financieros similares |

---

### 11. Explicabilidad

### 11. Explicabilidad

El sistema deberá permitir que el usuario comprenda por qué una empresa aparece en determinada posición dentro del ranking.

La interfaz utilizará una sección denominada:

**¿Por qué aparece esta empresa en el ranking?**

La técnica principal de explicabilidad seleccionada para Prospect Finder BVQ será **SHAP**, de acuerdo con el análisis realizado sobre el modelo v10.

SHAP fue seleccionado porque permite explicar tanto el comportamiento global del modelo como predicciones individuales y, en los casos evaluados, reprodujo exactamente el score generado por el modelo.

LIME se mantendrá como una técnica complementaria de contraste y validación académica, pero no será utilizada como explicación principal dentro de la interfaz debido a que sus resultados corresponden a aproximaciones locales y no reproducen exactamente el score original.

La aplicación no deberá mostrar directamente valores técnicos de SHAP al usuario de negocio.

Las contribuciones deberán traducirse a explicaciones comprensibles y orientadas al análisis comercial.

Por ejemplo:

**Factores que elevan la prioridad**

- Nivel de activos elevado.
- Ventas relevantes.
- Patrimonio sólido.
- Rentabilidad positiva.
- Crecimiento patrimonial.
- Disponibilidad de información histórica.

**Factores que reducen la prioridad**

- Menor escala empresarial.
- Menor volumen de ventas.
- Reducción de activos.
- Crecimientos negativos.
- Información financiera incompleta.

Las explicaciones deberán generarse a partir de las contribuciones SHAP correspondientes a cada empresa.

El sistema podrá identificar las variables con mayor contribución positiva y negativa para presentar una explicación resumida del resultado.

La explicación no deberá afirmar causalidad.

No se utilizarán expresiones como:

**“La empresa se convertirá en emisor porque posee estas características.”**

La interpretación correcta será:

**“El modelo asigna una mayor prioridad porque el perfil financiero de la empresa presenta características similares a patrones observados históricamente en empresas que posteriormente se convirtieron en emisores.”**

La aplicación deberá diferenciar claramente entre:

| Elemento | Significado |
|---|---|
| Score de priorización | Resultado generado por el modelo v10 |
| SHAP | Explicación de los factores que contribuyeron al score |
| LIME | Técnica complementaria utilizada para contraste académico |
| Calidad de datos | Indicador independiente sobre disponibilidad de información |

La explicación deberá incluir también advertencias cuando corresponda.

Ejemplos:

**Aspectos a revisar**

- Información financiera incompleta.
- Valores extremos.
- Ausencia de información histórica.
- Crecimientos atípicos.
- Variables con contribuciones contradictorias.

Los resultados del análisis global de SHAP mostraron que las variables con mayor influencia se encuentran principalmente relacionadas con:

- activos;
- ventas;
- patrimonio;
- crecimiento patrimonial;
- relación patrimonio / activos;
- crecimiento de activos;
- rentabilidad;
- tamaño empresarial.

Estas conclusiones podrán utilizarse para contextualizar las explicaciones, pero las explicaciones individuales deberán basarse en las contribuciones específicas calculadas para cada empresa.

El detalle técnico de SHAP y LIME permanecerá disponible para auditoría, documentación metodológica y análisis del modelo.

La interfaz comercial mostrará únicamente explicaciones simplificadas y comprensibles.

Prospect Finder BVQ utilizará la explicabilidad como mecanismo de transparencia y apoyo al especialista, no como sustituto del análisis humano.

---

### 12. Calidad de datos

La calidad de información será visible dentro del producto.

Esto es necesario porque el análisis de v10 mostró que la disponibilidad de información está asociada con la composición del ranking.

Cada empresa tendrá un indicador de calidad.

Se propone inicialmente:

| Nivel | Interpretación |
|---|---|
| Alta | Información prácticamente completa |
| Media | Existen algunos valores faltantes |
| Baja | Información relevante incompleta |

Este indicador será independiente del score de priorización.

No debe utilizarse para excluir automáticamente empresas.

---

### 13. Motor de empresas comparables

El producto incorporará una funcionalidad de empresas comparables.

Esta funcionalidad será independiente del modelo predictivo v10.

Su objetivo será responder:

**¿Qué empresas presentan un perfil financiero parecido?**

Para cada empresa seleccionada, el sistema podrá mostrar las organizaciones más similares utilizando variables financieras normalizadas.

Las variables candidatas incluyen:

Activos.

Patrimonio.

Ventas.

Número de empleados.

ROA.

ROE.

Margen neto.

Rotación de activos.

Crecimiento de activos.

Crecimiento de patrimonio.

Crecimiento de ventas.

Crecimiento de empleados.

Antes del cálculo de similitud deberán aplicarse transformaciones adecuadas para evitar que las variables de mayor escala dominen el resultado.

La primera implementación podrá utilizar escalamiento robusto y una medida de distancia o similitud.

El resultado se mostrará como:

**Similitud de perfil**

y deberá mantenerse separado del score generado por el modelo v10.

---

### 14. Similitud con emisores históricos

La aplicación permitirá explorar empresas cuyos perfiles financieros sean similares a empresas que históricamente fueron emisores.

El usuario podrá realizar dos tipos de consulta:

**Similares al perfil histórico de emisores**

Busca empresas cercanas al conjunto de perfiles históricos.

**Similares a un emisor específico**

Permite seleccionar un emisor histórico y localizar empresas financieramente comparables.

Esta funcionalidad tiene fines exploratorios.

La similitud no implica que una empresa necesariamente vaya a convertirse en emisor.

---

### 15. Separación entre score y similitud

El producto manejará inicialmente dos señales independientes:

| Señal | Significado |
|---|---|
| Score de priorización | Resultado del modelo v10 |
| Similitud con emisores | Cercanía del perfil financiero |

No se generará inicialmente una fórmula como:

`50 % score + 50 % similitud`

porque esa combinación no ha sido validada experimentalmente.

Una eventual combinación deberá evaluarse como una nueva versión del modelo.

---

### 16. Análisis de sesgos y concentración

La aplicación deberá reconocer que el ranking puede presentar concentraciones asociadas con características del universo empresarial.

El análisis realizado sobre TEST permitió identificar concentración por tamaño de empresa, disponibilidad de información, tipo societario y ubicación.

Estas características deberán utilizarse para monitoreo y exploración.

No deben convertirse automáticamente en reglas de exclusión.

En particular, provincia no forma parte de las variables utilizadas por el modelo final v10 y se utilizará únicamente como atributo descriptivo y de auditoría.

---

### 17. Supervisión humana

Prospect Finder BVQ será una herramienta de apoyo a decisiones.

El flujo recomendado será:

`Modelo → Ranking → Análisis del especialista → Investigación adicional → Decisión comercial`

La decisión final permanecerá siempre en los especialistas de la Bolsa de Valores Quito.

El sistema no realizará automáticamente:

Aprobación de emisores.

Rechazo de empresas.

Evaluación regulatoria.

Evaluación legal.

Evaluación crediticia.

Contacto automático con prospectos.

---

### 18. Uso del Top-K

Las métricas Top 50, Top 100 y Top 200 fueron utilizadas para evaluar la capacidad histórica del modelo para concentrar positivos.

En el producto, estas posiciones deben interpretarse como mecanismos de priorización y no como límites absolutos.

El usuario podrá ampliar o reducir el universo analizado.

El modelo v10 mostró capacidad de ordenamiento general, pero el desempeño observado en TEST dentro de los primeros puestos fue inferior al obtenido durante el backtesting.

Por esta razón, el producto no deberá limitarse exclusivamente a mostrar el Top 200.

Debe permitir explorar segmentos más amplios.

---

### 19. Consideración temporal

La aplicación productiva deberá utilizar el último ejercicio financiero disponible para cada empresa.

No se deben mezclar observaciones históricas de una misma empresa en el ranking operativo.

La información histórica permanecerá disponible para gráficos de evolución y cálculo de variables temporales.

---

### 20. Actualización

La actualización del ranking deberá ejecutarse cuando exista nueva información financiera suficientemente completa.

El proceso esperado será:

`Nueva información → validación → construcción de variables → scoring → controles de calidad → publicación del ranking`

La actualización del ranking no significa reentrenar automáticamente el modelo.

El modelo solamente deberá revisarse o reentrenarse cuando los mecanismos de monitoreo indiquen deterioro relevante o exista nueva evidencia suficiente para desarrollar una nueva versión.

---

### 21. Monitoreo

El producto deberá mantener controles sobre:

Desempeño del modelo.

Distribución del score.

Cambios en las variables.

Datos faltantes.

Concentración del ranking.

Desempeño por periodo.

Desempeño Top-K.

Los cambios importantes deberán generar una revisión antes de modificar el modelo.

---

### 22. Versionamiento

La versión actualmente seleccionada para el prototipo es:

`v10_hgb_financial_c3`

La versión v10 se considera cerrada como experimento.

Los resultados obtenidos sobre TEST no deberán utilizarse para modificar retroactivamente sus parámetros.

Cualquier cambio significativo en:

variables,

transformaciones,

modelo,

hiperparámetros,

definición del target,

reglas de ranking,

deberá registrarse como una nueva versión, comenzando por v11.

---

### 23. Funcionalidades del prototipo

El prototipo final de Prospect Finder BVQ deberá demostrar al menos las siguientes capacidades:

| Módulo | Funcionalidad |
|---|---|
| Resumen | Indicadores generales del universo |
| Ranking | Priorización de empresas |
| Filtros | Segmentación del universo |
| Búsqueda | Consulta por empresa o RUC |
| Empresa | Ficha detallada |
| Explicabilidad | Factores asociados con el resultado |
| Comparables | Empresas financieramente similares |
| Emisores similares | Comparación con perfiles históricos |
| Calidad | Estado de información disponible |
| Modelo | Información de la versión utilizada |
| Riesgos | Principales riesgos y limitaciones |
| Monitoreo | Indicadores de estabilidad |

---

### 24. Principios de diseño de la interfaz

La interfaz debe ser profesional, clara y orientada al análisis empresarial.

Debe priorizar:

Lectura rápida.

Jerarquía visual.

Tablas fáciles de explorar.

Indicadores financieros comprensibles.

Filtros visibles.

Explicaciones no técnicas.

Trazabilidad del score.

Advertencias cuando exista información insuficiente.

No debe mostrar términos técnicos innecesarios al usuario comercial.

Los detalles técnicos del modelo deberán estar disponibles en una sección separada.

---

### 25. Resultado esperado

El producto final permitirá transformar el modelo de inteligencia artificial en una herramienta práctica de prospección.

El especialista podrá partir de un universo amplio de empresas y progresivamente:

`Explorar → Filtrar → Priorizar → Comprender → Comparar → Analizar → Decidir`

La principal función de Prospect Finder BVQ será reducir el universo que requiere revisión manual y facilitar una prospección estructurada, consistente y trazable.

El sistema será un mecanismo de apoyo analítico y no un sistema automatizado de decisión.