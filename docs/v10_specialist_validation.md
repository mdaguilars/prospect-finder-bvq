# Validación con especialistas BVQ — Prospect Finder BVQ

## 1. Propósito

Este documento define el protocolo y la evidencia para la validación funcional del prototipo Prospect Finder BVQ con especialistas de la Bolsa de Valores Quito.

La validación busca determinar si el prototipo resulta comprensible y útil como herramienta de apoyo para priorizar empresas con potencial de convertirse en emisores del mercado de valores ecuatoriano.

La actividad corresponde a:

**B36 — Validar con al menos dos especialistas BVQ**

y se relaciona con el objetivo del Capstone de disponer de un prototipo funcional validado por usuarios conocedores del proceso de prospección.

Esta validación no evalúa nuevamente el desempeño estadístico del modelo. El modelo v10 permanece congelado.

---

## 2. Alcance

La validación se concentra en la experiencia de uso y utilidad práctica del prototipo.

Se evaluarán principalmente:

- claridad del ranking;
- utilidad del Índice de Afinidad Bursátil;
- facilidad de búsqueda y filtros;
- comprensión de la ficha empresarial;
- utilidad de los indicadores financieros;
- comprensión de la explicación SHAP;
- utilidad de los emisores históricos comparables;
- claridad de las advertencias y limitaciones;
- facilidad de navegación;
- utilidad general para apoyar la prospección comercial.

No se solicitará a los especialistas modificar:

- el modelo;
- los hiperparámetros;
- las variables;
- el target;
- el protocolo temporal;
- los resultados de TEST.

---

## 3. Participantes requeridos

La validación debe realizarse con al menos:

**2 especialistas de la Bolsa de Valores Quito**

Los participantes deben tener conocimiento relacionado con uno o más de los siguientes ámbitos:

- mercado de valores;
- emisores;
- estructuración;
- prospección comercial;
- análisis financiero;
- gestión comercial;
- conocimiento institucional del proceso de incorporación de emisores.

No es necesario publicar información personal innecesaria.

Para la documentación académica puede utilizarse un código de participante.

Ejemplo:

- `E1`
- `E2`

---

## 4. Registro de participantes

| Código | Nombre | Cargo / función | Área | Fecha de validación | Estado |
|---|---|---|---|---|---|
| E1 | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE |
| E2 | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE |

Si participa una tercera persona puede añadirse:

| Código | Nombre | Cargo / función | Área | Fecha de validación | Estado |
|---|---|---|---|---|---|
| E3 | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE |

---

## 5. Entorno de validación

La sesión se realizará utilizando el prototipo funcional de Prospect Finder BVQ.

Flujo:

`PostgreSQL → FastAPI → React → usuario`

Explicabilidad:

`modelo v10 congelado → SHAP → FastAPI → React → usuario`

Componentes disponibles:

- ranking operacional;
- búsqueda;
- filtros;
- paginación;
- ficha empresarial;
- indicadores financieros;
- Índice de Afinidad Bursátil;
- percentil;
- ranking;
- emisores históricos comparables;
- explicación SHAP.

Fecha de decisión del universo operacional:

`2024-05-01`

Universo:

`137.156 empresas`

---

## 6. Consideraciones antes de iniciar

Antes de cada sesión se debe explicar brevemente al participante que:

1. Prospect Finder BVQ es una herramienta de apoyo para priorización.
2. El Índice de Afinidad Bursátil no representa una probabilidad calibrada.
3. Un score alto no garantiza que una empresa se convierta en emisor.
4. SHAP explica el comportamiento del modelo y no demuestra causalidad.
5. La similitud con emisores representa cercanía del perfil financiero y no probabilidad de emisión.
6. La decisión comercial final permanece bajo criterio humano.
7. El objetivo de la sesión es evaluar el prototipo y no evaluar al participante.

---

# 7. Guion de validación

Cada especialista deberá realizar los siguientes escenarios.

## Tarea V-01 — Revisar el ranking principal

**Instrucción al participante:**

Revise la pantalla principal y observe las primeras empresas del ranking.

**Aspectos a observar:**

- si comprende qué representa el ranking;
- si identifica fácilmente las empresas prioritarias;
- si entiende el Índice de Afinidad Bursátil;
- si la información principal resulta suficiente para una primera revisión.

**Resultado E1:** PENDIENTE

**Resultado E2:** PENDIENTE

**Observaciones:** PENDIENTE

---

## Tarea V-02 — Buscar una empresa

**Instrucción al participante:**

Utilice el buscador para localizar una empresa conocida por nombre o RUC.

**Aspectos a observar:**

- facilidad de uso;
- claridad del resultado;
- utilidad de la búsqueda para el trabajo cotidiano.

**Resultado E1:** PENDIENTE

**Resultado E2:** PENDIENTE

**Observaciones:** PENDIENTE

---

## Tarea V-03 — Utilizar filtros

**Instrucción al participante:**

Filtre el ranking por provincia y posteriormente por tipo de compañía.

**Aspectos a observar:**

- facilidad para encontrar los filtros;
- comprensión de los criterios;
- utilidad comercial del filtrado;
- necesidad de filtros adicionales.

**Resultado E1:** PENDIENTE

**Resultado E2:** PENDIENTE

**Observaciones:** PENDIENTE

---

## Tarea V-04 — Revisar la ficha empresarial

**Instrucción al participante:**

Abra una empresa del ranking y revise su ficha.

**Aspectos a observar:**

- claridad de la identificación empresarial;
- utilidad de activos, patrimonio, ventas y empleados;
- comprensión del ranking y percentil;
- información adicional que el especialista consideraría necesaria.

**Resultado E1:** PENDIENTE

**Resultado E2:** PENDIENTE

**Observaciones:** PENDIENTE

---

## Tarea V-05 — Interpretar el Índice de Afinidad Bursátil

**Instrucción al participante:**

Explique con sus propias palabras qué entiende por Índice de Afinidad Bursátil después de observar la ficha.

**Interpretación esperada conceptualmente:**

El participante debería comprender que se trata de un indicador de priorización relativa producido por el modelo y no de una probabilidad cierta de emisión.

**Resultado E1:** PENDIENTE

**Resultado E2:** PENDIENTE

**Observaciones:** PENDIENTE

---

## Tarea V-06 — Revisar los factores SHAP

**Instrucción al participante:**

Seleccione `Analizar factores` y revise los factores que aumentan o reducen la afinidad.

**Aspectos a observar:**

- comprensión de factores positivos y negativos;
- claridad de las etiquetas;
- utilidad de la explicación;
- riesgo de interpretar los factores como causas;
- necesidad de información adicional.

**Resultado E1:** PENDIENTE

**Resultado E2:** PENDIENTE

**Observaciones:** PENDIENTE

---

## Tarea V-07 — Revisar emisores comparables

**Instrucción al participante:**

Revise la sección de emisores históricos comparables.

**Aspectos a observar:**

- si entiende el significado de similitud;
- si considera útil conocer emisores con perfiles financieros cercanos;
- si la información aporta contexto para la prospección;
- si diferencia similitud de afinidad predictiva.

**Resultado E1:** PENDIENTE

**Resultado E2:** PENDIENTE

**Observaciones:** PENDIENTE

---

## Tarea V-08 — Evaluar utilidad para prospección

**Instrucción al participante:**

Considere cómo utilizaría el prototipo dentro de un proceso real de prospección de potenciales emisores.

**Aspectos a observar:**

- utilidad para priorizar contactos;
- utilidad para preparar análisis preliminar;
- utilidad para reducir revisión manual;
- posibilidad de incorporar el sistema al proceso actual;
- información adicional necesaria antes de contactar una empresa.

**Resultado E1:** PENDIENTE

**Resultado E2:** PENDIENTE

**Observaciones:** PENDIENTE

---

# 8. Cuestionario de valoración

Cada participante calificará las siguientes afirmaciones utilizando una escala de 1 a 5.

| Valor | Significado |
|---:|---|
| 1 | Totalmente en desacuerdo |
| 2 | En desacuerdo |
| 3 | Neutral |
| 4 | De acuerdo |
| 5 | Totalmente de acuerdo |

## Preguntas

| ID | Afirmación | E1 | E2 |
|---|---|---:|---:|
| Q01 | El ranking permite identificar fácilmente las empresas prioritarias. | PENDIENTE | PENDIENTE |
| Q02 | El Índice de Afinidad Bursátil es comprensible como indicador de priorización. | PENDIENTE | PENDIENTE |
| Q03 | La búsqueda y los filtros son fáciles de utilizar. | PENDIENTE | PENDIENTE |
| Q04 | La ficha empresarial presenta información financiera útil para una primera revisión. | PENDIENTE | PENDIENTE |
| Q05 | La posición en el ranking y el percentil aportan contexto útil. | PENDIENTE | PENDIENTE |
| Q06 | Los factores SHAP ayudan a comprender por qué una empresa obtiene determinado nivel de afinidad. | PENDIENTE | PENDIENTE |
| Q07 | Los emisores históricos comparables aportan contexto útil para analizar un prospecto. | PENDIENTE | PENDIENTE |
| Q08 | La interfaz resulta clara y fácil de navegar. | PENDIENTE | PENDIENTE |
| Q09 | El prototipo puede apoyar el proceso de prospección de potenciales emisores. | PENDIENTE | PENDIENTE |
| Q10 | Utilizaría una herramienta de este tipo como apoyo para priorizar empresas a analizar. | PENDIENTE | PENDIENTE |

---

# 9. Preguntas abiertas

Cada especialista deberá responder brevemente.

## P1 — Elemento más útil

**Pregunta:**

¿Qué información o funcionalidad del prototipo considera más útil para el proceso de prospección?

**E1:** PENDIENTE

**E2:** PENDIENTE

---

## P2 — Información faltante

**Pregunta:**

¿Qué información adicional debería incorporarse para que la herramienta resulte más útil?

**E1:** PENDIENTE

**E2:** PENDIENTE

---

## P3 — Claridad del Índice de Afinidad

**Pregunta:**

¿El significado del Índice de Afinidad Bursátil resulta claro? ¿Qué cambiaría en su presentación?

**E1:** PENDIENTE

**E2:** PENDIENTE

---

## P4 — Explicabilidad

**Pregunta:**

¿Los factores que aumentan o reducen afinidad ayudan a comprender el resultado del modelo?

**E1:** PENDIENTE

**E2:** PENDIENTE

---

## P5 — Comparables

**Pregunta:**

¿Los emisores históricos comparables aportan información útil? ¿Cómo los utilizaría?

**E1:** PENDIENTE

**E2:** PENDIENTE

---

## P6 — Mejoras

**Pregunta:**

¿Cuál sería la principal mejora que recomendaría antes de utilizar esta herramienta en un proceso real?

**E1:** PENDIENTE

**E2:** PENDIENTE

---

## P7 — Utilidad general

**Pregunta:**

¿Considera que Prospect Finder BVQ puede ayudar a reducir o focalizar el universo de empresas que deben revisarse manualmente? Explique brevemente.

**E1:** PENDIENTE

**E2:** PENDIENTE

---

# 10. Registro de incidencias observadas

| ID | Participante | Escenario | Incidencia | Severidad | Acción propuesta | Estado |
|---|---|---|---|---|---|---|
| I01 | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE |

Si no existen incidencias se deberá registrar explícitamente:

`No se identificaron incidencias durante la sesión.`

No se deben inventar incidencias para completar la tabla.

---

# 11. Registro de recomendaciones

| ID | Participante | Recomendación | Tipo | Prioridad | Decisión |
|---|---|---|---|---|---|
| R01 | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE |

Tipos sugeridos:

- interfaz;
- información;
- filtros;
- explicabilidad;
- comparables;
- proceso comercial;
- documentación;
- evolución futura.

La decisión podrá registrarse como:

- incorporar antes del cierre;
- incorporar como mejora menor;
- considerar en versión futura;
- no incorporar, con justificación.

---

# 12. Consolidación cuantitativa

Esta sección se completará después de recibir las respuestas reales.

## Resultados por participante

| Participante | Promedio Q01–Q10 | Observación general |
|---|---:|---|
| E1 | PENDIENTE | PENDIENTE |
| E2 | PENDIENTE | PENDIENTE |

## Promedio por dimensión

| Dimensión | Preguntas relacionadas | Resultado |
|---|---|---:|
| Priorización | Q01, Q02, Q05 | PENDIENTE |
| Usabilidad | Q03, Q08 | PENDIENTE |
| Información empresarial | Q04 | PENDIENTE |
| Explicabilidad | Q06 | PENDIENTE |
| Comparables | Q07 | PENDIENTE |
| Utilidad comercial | Q09, Q10 | PENDIENTE |

No deberán completarse promedios hasta disponer de respuestas reales.

---

# 13. Consolidación cualitativa

Después de ambas sesiones se deberá resumir únicamente la evidencia observada.

## Fortalezas identificadas

PENDIENTE

## Debilidades identificadas

PENDIENTE

## Información solicitada por los especialistas

PENDIENTE

## Mejoras recomendadas

PENDIENTE

## Riesgos de interpretación identificados

PENDIENTE

## Cambios realizados después de la validación

PENDIENTE

---

# 14. Criterio interno de cierre de B36

B36 podrá marcarse como **Completado** cuando exista evidencia real de:

1. participación de al menos dos especialistas de la BVQ;
2. ejecución de los escenarios principales;
3. cuestionario completado;
4. observaciones cualitativas registradas;
5. incidencias y recomendaciones documentadas;
6. decisión sobre los cambios derivados de la validación.

No se establece en este documento una calificación mínima artificial para declarar válido el prototipo.

El propósito es obtener evidencia de utilidad, comprensión y oportunidades de mejora.

Si los especialistas identifican problemas importantes, deberán documentarse y resolverse o justificarse antes del cierre final del proyecto.

---

# 15. Evidencia recomendada

Para respaldar académicamente la actividad se recomienda conservar:

- este documento completado;
- capturas de pantalla de la sesión cuando corresponda;
- formulario o registro de respuestas;
- fecha de cada validación;
- identificación funcional del participante;
- observaciones;
- recomendaciones;
- evidencia de cambios implementados como consecuencia de la validación.

No es necesario almacenar información personal que no aporte a la evidencia académica.

---

# 16. Resultado final de B36

**Estado actual:** PENDIENTE

**Número de especialistas requeridos:** 2

**Número de especialistas validados:** 0

**Resultado consolidado:** PENDIENTE

**Decisión final:** PENDIENTE

---

# 17. Regla de integridad de la evidencia

No se deben inventar:

- participantes;
- cargos;
- respuestas;
- puntuaciones;
- observaciones;
- recomendaciones;
- incidencias;
- fechas de validación;
- conclusiones atribuidas a especialistas.

Toda información incorporada en la sección de resultados deberá provenir de una validación efectivamente realizada.

---

# 18. Próximo paso

Realizar la sesión con el primer especialista y registrar sus respuestas como:

`E1`

Después realizar la misma sesión con el segundo especialista y registrar sus respuestas como:

`E2`

Una vez completadas ambas sesiones se consolidarán los resultados y se determinarán los ajustes finales del prototipo.
