# Validación con especialistas BVQ — Prospect Finder BVQ

## 1. Propósito

Este documento registra el protocolo ejecutado, la evidencia obtenida y los resultados de la validación funcional y comercial del prototipo Prospect Finder BVQ con especialistas vinculados a la Bolsa de Valores de Quito.

La validación busca determinar si el prototipo resulta comprensible, útil y aplicable como herramienta de apoyo para priorizar empresas con potencial de convertirse en emisores del mercado de valores ecuatoriano.

La actividad corresponde a:

**B36 — Validar con al menos dos especialistas BVQ**

y se relaciona con el objetivo del Capstone de disponer de un prototipo funcional validado por usuarios conocedores del proceso comercial, financiero y de prospección.

Esta validación no vuelve a evaluar el desempeño estadístico del modelo. El modelo v10 permanece congelado.

---

## 2. Alcance

La validación se concentra en:

- claridad de la pantalla principal;
- facilidad de navegación;
- utilidad de búsqueda y filtros;
- comprensión del ranking y de los niveles Top;
- utilidad de la información financiera;
- comprensión de las razones que explican la prioridad;
- utilidad de emisores históricos comparables;
- orientación del próximo paso comercial;
- capacidad para reducir el universo de revisión;
- utilidad general para la prospección;
- intención de uso;
- recomendaciones de mejora.

No se solicitó a los participantes modificar:

- el modelo;
- los hiperparámetros;
- las variables predictoras;
- el target;
- el protocolo temporal;
- los resultados de TEST.

Las observaciones obtenidas corresponden a experiencia de uso, presentación de información y evolución funcional del producto.

---

## 3. Fuente de evidencia

La evidencia utilizada para este documento proviene del formulario:

**Validación comercial – Prospect Finder BVQ**

La exportación analizada contiene:

- 4 respuestas;
- fecha y hora de respuesta;
- identificación o nombre del participante;
- cargo o función;
- experiencia;
- 25 afirmaciones principales valoradas en escala de 1 a 5;
- preguntas de decisión y utilidad;
- valoración general;
- recomendación de uso;
- preguntas abiertas de retroalimentación.

La escala utilizada para las afirmaciones cuantitativas es:

| Valor | Interpretación |
|---:|---|
| 1 | Valoración mínima |
| 2 | Valoración baja |
| 3 | Valoración intermedia |
| 4 | Valoración favorable |
| 5 | Valoración máxima |

---

## 4. Participantes

El requisito mínimo era contar con dos especialistas.

La validación fue respondida por cuatro participantes:

| Código | Participante | Cargo / función registrado | Experiencia registrada | Fecha |
|---|---|---|---|---|
| E1 | Gabriela Flores | Jefe de Contabiliad | Entre 1 y 3 años | 22-oct-2026 |
| E2 | Ivanova Correa | Jefe Comercial | Entre 7 y 10 años | 23-oct-2026 |
| E3 | Anahir Salazar | Analista Comercial | Menos de 1 año | 23-oct-2026 |
| E4 | Gerardo Cepeda | Gerente Financiero | Más de 10 años | 27-oct-2026 |

La muestra incluye perfiles comerciales, financieros y contables con distintos niveles de experiencia.

El número de participantes supera el mínimo definido para B36.

---

## 5. Entorno funcional evaluado

La validación se realizó sobre el prototipo funcional de Prospect Finder BVQ.

Flujo general:

`PostgreSQL → FastAPI → React → usuario`

Flujo de explicabilidad:

`modelo v10 congelado → SHAP → FastAPI → React → usuario`

Entre los componentes evaluados se encuentran:

- ranking operacional;
- búsqueda;
- filtros;
- navegación entre secciones;
- ficha empresarial;
- activos;
- patrimonio;
- ventas;
- empleados;
- posición en ranking;
- clasificación Top;
- nivel de afinidad;
- información de completitud;
- razones que explican la prioridad;
- intensidad relativa de las razones;
- emisores históricos comparables;
- orientación de próximo paso comercial.

Fecha de decisión del universo operacional:

`2024-05-01`

Universo operacional:

`137.156 empresas`

---

## 6. Consideraciones de interpretación

Prospect Finder BVQ debe utilizarse como herramienta de apoyo a la priorización.

El score o Índice de Afinidad Bursátil:

- representa una señal relativa de priorización;
- no es una probabilidad calibrada de convertirse en emisor;
- no garantiza que una empresa vaya a emitir valores;
- debe interpretarse junto con información empresarial y criterio humano.

Las explicaciones asociadas al modelo describen cómo determinadas variables contribuyen al score.

No demuestran causalidad.

La similitud con emisores históricos representa cercanía de perfil y no probabilidad de emisión.

La decisión comercial final permanece bajo responsabilidad del especialista.

---

## 7. Instrumento cuantitativo principal

Las preguntas 4 a 28 del formulario constituyen 25 afirmaciones valoradas de 1 a 5.

Estas afirmaciones cubren cuatro dimensiones:

1. claridad y usabilidad;
2. priorización y contexto del ranking;
3. análisis empresarial y explicabilidad;
4. utilidad comercial.

El resultado global se calcula como promedio simple de las respuestas válidas.

---

## 8. Resultado general

El promedio global de las 25 afirmaciones principales fue:

**4,82 / 5**

Distribución observada:

- todas las respuestas cuantitativas de Q04 a Q28 fueron 4 o 5;
- no se registraron valoraciones de 1, 2 o 3;
- E1 registró 14 valoraciones de 5 y 11 de 4;
- E2 registró 25 valoraciones de 5;
- E3 registró 25 valoraciones de 5;
- E4 registró 18 valoraciones de 5 y 7 de 4.

Esto evidencia una valoración consistentemente favorable del prototipo dentro del grupo participante.

El resultado debe interpretarse como validación funcional y comercial de una muestra especializada pequeña y no como evidencia estadística generalizable a toda una población.

---

## 9. Resultado por participante

| Participante | Promedio Q04–Q28 |
|---|---:|
| E1 — Gabriela Flores | 4,56 |
| E2 — Ivanova Correa | 5,00 |
| E3 — Anahir Salazar | 5,00 |
| E4 — Gerardo Cepeda | 4,72 |
| **Promedio general** | **4,82** |

Los cuatro participantes presentan una valoración promedio superior a 4,5.

---

## 10. Resultado por dimensión

Para facilitar la interpretación, las 25 afirmaciones se agruparon de la siguiente manera:

| Dimensión | Preguntas | Promedio |
|---|---|---:|
| Claridad y usabilidad | Q04–Q09 | 4,75 |
| Priorización y contexto del ranking | Q10–Q14 | 4,75 |
| Análisis empresarial y explicabilidad | Q15–Q22 | 4,84 |
| Utilidad comercial | Q23–Q28 | 4,92 |
| **Promedio global** | **Q04–Q28** | **4,82** |

La dimensión con mayor valoración fue:

**Utilidad comercial: 4,92 / 5**

Esto es consistente con el propósito principal de Prospect Finder BVQ como herramienta para focalizar el esfuerzo comercial.

---

## 11. Resultado detallado de las afirmaciones Q04–Q28

| ID | Tema evaluado | Promedio |
|---|---|---:|
| Q04 | La pantalla principal permite entender qué empresas revisar primero | 4,75 |
| Q05 | La información presentada es clara y fácil de entender | 4,50 |
| Q06 | Los textos y términos son adecuados para el área comercial | 5,00 |
| Q07 | Tamaño de textos, números y elementos visuales | 4,75 |
| Q08 | Navegación entre Prospectos, Analítica y Cómo interpretar | 4,75 |
| Q09 | Utilidad de filtros por empresa, provincia y tipo de compañía | 4,75 |
| Q10 | La posición asignada ayuda a saber por dónde comenzar | 4,75 |
| Q11 | Comprensión de Top 1 %, Top 5 %, Top 10 % y otros niveles | 5,00 |
| Q12 | Información suficiente en lista principal para profundizar | 4,50 |
| Q13 | Utilidad de conocer qué tan completa está la información | 4,50 |
| Q14 | Valor aportado por empresas similares que ya participaron en el mercado | 5,00 |
| Q15 | Facilidad para identificar por qué una empresa merece revisión | 4,75 |
| Q16 | Utilidad de activos, patrimonio, ventas y empleados | 5,00 |
| Q17 | Comprensión de la sección “¿Qué explica su prioridad?” | 4,75 |
| Q18 | Utilidad de expresiones de favorabilidad | 5,00 |
| Q19 | Utilidad del porcentaje de influencia de cada razón | 4,75 |
| Q20 | Claridad de explicaciones financieras | 4,75 |
| Q21 | Utilidad de emisores similares para preparar conversación comercial | 5,00 |
| Q22 | Utilidad de la sección “Próximo paso comercial” | 4,75 |
| Q23 | Capacidad para reducir el tiempo de identificación de empresas | 5,00 |
| Q24 | Capacidad para concentrar el esfuerzo comercial | 4,75 |
| Q25 | Preparación para primera revisión o conversación | 5,00 |
| Q26 | Intención de utilizar Prospect Finder en actividades habituales | 5,00 |
| Q27 | Complemento de la experiencia y criterio del asesor | 5,00 |
| Q28 | Valor aportado a la gestión comercial de la BVQ | 4,75 |

Los resultados más altos, con promedio de 5,00, se observan en:

- adecuación del lenguaje comercial;
- interpretación de niveles Top;
- valor de empresas similares;
- comprensión del tamaño y perfil empresarial;
- expresiones de favorabilidad;
- referencias para conversación comercial;
- reducción del tiempo de identificación;
- preparación para una primera conversación;
- intención de uso;
- complementariedad con el criterio del asesor.

---

## 12. Suficiencia de información para revisión comercial

Pregunta:

**Después de revisar una empresa en Prospect Finder, ¿considera que cuenta con información suficiente para decidir si merece una revisión comercial adicional?**

Resultados:

| Respuesta | Participantes | Porcentaje |
|---|---:|---:|
| Sí | 4 | 100 % |
| No | 0 | 0 % |

Los cuatro participantes consideran que Prospect Finder entrega información suficiente para decidir si una empresa merece una revisión comercial adicional.

Este resultado no significa que la herramienta contenga toda la información necesaria para realizar una gestión comercial completa.

Significa que cumple el propósito de apoyar una primera decisión de priorización y profundización.

---

## 13. Acción frente a empresas prioritarias

Pregunta:

**Luego de utilizar la herramienta, ¿qué acción tomaría normalmente con una empresa ubicada entre las primeras posiciones?**

Los cuatro participantes seleccionaron:

**La revisaría con mayor profundidad.**

Resultado:

| Acción | Participantes | Porcentaje |
|---|---:|---:|
| Revisarla con mayor profundidad | 4 | 100 % |

Este resultado es coherente con el principio:

`Modelo → Priorización → Especialista → Decisión`

La herramienta orienta qué revisar primero, pero no automatiza la decisión comercial.

---

## 14. Elementos considerados más útiles para decidir una revisión

Las selecciones realizadas por los participantes muestran mayor recurrencia en:

| Elemento | Número de menciones |
|---|---:|
| Tamaño financiero | 3 |
| Emisores similares | 3 |
| Posición de la empresa en la lista | 2 |
| Ventas | 2 |
| Nivel de afinidad | 1 |
| Razones que explican su prioridad | 1 |
| Intensidad de cada razón | 1 |
| Número de empleados | 1 |
| Otro | 1 |

Los resultados evidencian que los usuarios no basan su revisión en un único indicador.

La combinación de:

- posición;
- tamaño;
- ventas;
- afinidad;
- explicación;
- comparables;

es percibida como útil para decidir qué empresas merecen mayor atención.

---

## 15. Experiencia general

Pregunta:

**¿Cómo calificaría su experiencia general utilizando Prospect Finder?**

Resultados:

| Participante | Calificación |
|---|---:|
| E1 | 5 |
| E2 | 5 |
| E3 | 5 |
| E4 | 5 |
| **Promedio** | **5,00 / 5** |

Los cuatro participantes asignaron la máxima calificación disponible a su experiencia general.

---

## 16. Utilidad para la prospección comercial

Pregunta:

**¿Qué tan útil considera Prospect Finder para apoyar la prospección comercial de la BVQ?**

Resultados:

| Participante | Calificación |
|---|---:|
| E1 | 5 |
| E2 | 5 |
| E3 | 4 |
| E4 | 5 |
| **Promedio** | **4,75 / 5** |

La utilidad comercial fue evaluada favorablemente por todos los participantes.

---

## 17. Recomendación de uso

Pregunta:

**¿Recomendaría utilizar esta herramienta como apoyo para el equipo comercial?**

Resultados:

| Respuesta | Participantes | Porcentaje |
|---|---:|---:|
| Sí | 2 | 50 % |
| Sí, con algunos ajustes | 2 | 50 % |
| No | 0 | 0 % |

Por tanto:

**100 % de los participantes recomendaría utilizar Prospect Finder como apoyo para el equipo comercial, aunque la mitad identifica ajustes deseables.**

Las observaciones asociadas a esos ajustes se registran como oportunidades de evolución del producto.

---

## 18. Resultados cualitativos por participante

### E1 — Gabriela Flores

**Elemento más útil**

El ranking de empresas y la vista de los principales índices financieros.

**Información o explicación no clara**

Indicó que no identificó información o explicación que resultara confusa.

**Información adicional solicitada**

Índice de liquidez.

**Mejora sugerida**

Personalizar más la solución para la BVQ incorporando variables adicionales, como la última fecha en que una empresa emitió un papel en el mercado de valores y el tipo de papel, con el objetivo de facilitar seguimiento.

**Funcionalidad futura sugerida**

Información adicional, particularmente el indicador de liquidez.

**Comentario general**

Considera que la herramienta resume adecuadamente la información necesaria para realizar seguimiento comercial.

---

### E2 — Ivanova Correa

**Elemento más útil**

La relación con emisores históricos comparables.

La participante destaca el valor de mostrar que empresas de características o sectores similares ya participan en el mercado de valores, porque esto puede ayudar a contextualizar la alternativa de emisión frente a potenciales prospectos.

**Información o explicación no clara**

Ninguna.

**Información adicional solicitada**

Datos de contacto.

**Mejora sugerida**

Permitir registrar notas para conservar información encontrada en otras fuentes.

**Funcionalidades futuras sugeridas**

- componente tipo CRM;
- sección de “balances ajustados”;
- simulación del antes y después financiero de emitir un determinado título en el mercado de valores.

**Comentario general**

Calificó la solución como una excelente herramienta.

---

### E3 — Anahir Salazar

La participante completó las preguntas cuantitativas y de decisión.

Entre los elementos más útiles seleccionó:

- posición de la empresa en la lista;
- nivel de afinidad;
- tamaño financiero;
- emisores similares.

Indicó que:

- cuenta con información suficiente para decidir si una empresa merece revisión comercial adicional;
- revisaría con mayor profundidad una empresa ubicada en primeras posiciones;
- su experiencia general fue 5/5;
- la utilidad para prospección fue 4/5;
- recomendaría utilizar la herramienta.

Las preguntas abiertas finales no registran respuesta.

No se incorporan inferencias adicionales sobre esos campos.

---

### E4 — Gerardo Cepeda

**Elemento más útil**

El ranking y la información desplegada al seleccionar una empresa.

**Información o explicación no clara**

Sugiere que determinados indicadores no se presenten en formato decimal sino como porcentaje.

**Información adicional solicitada**

Solicita mayor segmentación por:

- tamaño de empresa;
- actividad económica, registrada en el formulario como “CIU”;
- tipo de papel emitido por empresas similares;
- valor emitido.

**Mejora sugerida**

Incluir KPI adicionales, particularmente liquidez.

**Funcionalidades futuras sugeridas**

- nivel de impagos de empresas similares;
- calificación de los papeles emitidos por empresas similares.

**Comentario general**

Considera Prospect Finder una herramienta muy útil.

---

## 19. Fortalezas identificadas

A partir de las respuestas cuantitativas y cualitativas se identifican las siguientes fortalezas:

### 19.1 Priorización

El ranking permite reducir un universo muy grande de empresas a una secuencia de revisión manejable.

### 19.2 Utilidad comercial

La dimensión con mayor promedio fue utilidad comercial:

**4,92 / 5**

Los usuarios consideran que la herramienta puede ayudar a reducir tiempo y concentrar el esfuerzo comercial.

### 19.3 Información financiera

Activos, patrimonio, ventas, empleados e indicadores financieros fueron considerados útiles para una primera comprensión empresarial.

### 19.4 Comparables históricos

Los emisores similares fueron uno de los elementos más recurrentemente valorados.

Su utilidad no se limita a la similitud financiera; también puede funcionar como referencia comercial para explicar a un prospecto que existen organizaciones comparables que ya participan en el mercado.

### 19.5 Explicabilidad

Las razones que explican la prioridad y su intensidad fueron valoradas favorablemente.

La explicabilidad ayuda a que el score no se presente como una cifra aislada.

### 19.6 Complemento del criterio humano

La afirmación relacionada con que la herramienta complementa la experiencia y criterio del asesor obtuvo:

**5,00 / 5**

Esto coincide con el enfoque de diseño del proyecto.

---

## 20. Debilidades y oportunidades de mejora

No se identificaron observaciones que invaliden el prototipo.

Las oportunidades de mejora se concentran en enriquecer la información disponible y evolucionar la herramienta hacia un proceso comercial más completo.

Principales oportunidades:

1. incorporar indicador de liquidez;
2. presentar determinados ratios como porcentajes en lugar de decimales;
3. incorporar datos de contacto;
4. incorporar notas comerciales;
5. agregar información histórica de emisiones;
6. mostrar tipo y valor de papeles emitidos por empresas comparables;
7. incorporar segmentación adicional por tamaño y actividad económica;
8. añadir información sobre impagos y calificaciones de emisiones comparables;
9. evolucionar hacia funcionalidades tipo CRM;
10. explorar simulaciones financieras o “balances ajustados” relacionados con una potencial emisión.

---

## 21. Registro de incidencias

No se reportaron incidencias funcionales críticas en las respuestas del formulario.

Se registra una observación de presentación:

| ID | Participante | Observación | Severidad | Acción propuesta | Estado |
|---|---|---|---|---|---|
| I01 | E4 | Presentar determinados indicadores como porcentaje y no como decimal | Baja | Revisar formato visual de ratios | Mejora propuesta |

Esta observación afecta presentación y comprensión visual.

No modifica:

- modelo;
- score;
- ranking;
- target;
- variables predictoras;
- resultados TEST.

---

## 22. Registro consolidado de recomendaciones

| ID | Recomendación | Participantes relacionados | Tipo | Prioridad propuesta | Decisión |
|---|---|---|---|---|---|
| R01 | Incorporar indicador de liquidez | E1, E4 | Información / KPI | Alta | Considerar en siguiente evolución |
| R02 | Incorporar fecha y tipo de emisiones históricas | E1 | Información comercial | Media | Considerar en siguiente evolución |
| R03 | Incorporar datos de contacto | E2 | Información comercial | Alta | Considerar en siguiente evolución |
| R04 | Permitir notas por prospecto | E2 | Proceso comercial | Media | Considerar en siguiente evolución |
| R05 | Incorporar funciones tipo CRM | E2 | Producto | Media | Versión futura |
| R06 | Simular balances ajustados antes/después de una emisión | E2 | Analítica avanzada | Media | Versión futura |
| R07 | Mostrar ratios en porcentaje cuando corresponda | E4 | Interfaz | Media | Mejora visual |
| R08 | Segmentar por tamaño y actividad económica | E4 | Filtros / análisis | Media | Considerar en siguiente evolución |
| R09 | Incluir tipo y valor de emisiones de comparables | E4 | Comparables | Media | Considerar en siguiente evolución |
| R10 | Incluir impagos y calificación de papeles comparables | E4 | Riesgo / comparables | Media | Versión futura |

Las prioridades indicadas corresponden a una organización del backlog a partir de recurrencia y cercanía con el propósito actual del prototipo.

No representan cambios exigidos al modelo v10.

---

## 23. Cambios derivados de la validación

La validación no genera necesidad de modificar retrospectivamente el modelo v10.

Se mantiene congelado:

- Feature Set;
- algoritmo;
- hiperparámetros;
- target;
- split temporal;
- evaluación TEST;
- score;
- metodología de ranking.

Las recomendaciones obtenidas corresponden principalmente a:

- enriquecimiento de datos;
- presentación;
- filtros;
- seguimiento comercial;
- comparables;
- nuevas funcionalidades.

Por integridad metodológica, cualquier evolución predictiva motivada por nueva información deberá desarrollarse como una versión posterior y no como modificación retrospectiva de v10.

---

## 24. Interpretación de la validación

Los resultados permiten afirmar que, dentro del grupo de especialistas participante:

- el prototipo fue comprendido;
- el ranking fue considerado útil;
- la información financiera fue considerada relevante;
- los comparables aportan contexto;
- la explicación de prioridad fue considerada comprensible;
- la herramienta puede reducir el esfuerzo de revisión;
- existe intención de uso;
- existe recomendación favorable para utilizarla como apoyo comercial.

No debe interpretarse esta validación como:

- prueba estadística de desempeño del modelo;
- validación externa sobre todo el mercado;
- garantía de adopción organizacional;
- medición de impacto comercial real;
- demostración de causalidad.

La validación responde específicamente a:

**comprensión, utilidad funcional y utilidad comercial percibida.**

---

## 25. Limitaciones de la validación

La validación presenta las siguientes limitaciones:

1. participaron cuatro personas;
2. la muestra es intencional y especializada;
3. los resultados no son estadísticamente generalizables;
4. la evaluación mide percepción de utilidad y usabilidad;
5. no mide todavía conversión comercial real;
6. no mide incremento real de nuevos emisores;
7. no constituye nueva evaluación predictiva;
8. una participante no completó las preguntas abiertas finales.

Estas limitaciones no invalidan el ejercicio.

Son coherentes con una validación funcional de prototipo dentro de un proyecto Capstone.

---

## 26. Criterio de cierre de B36

El criterio definido requería evidencia de:

1. al menos dos especialistas;
2. ejecución de la validación;
3. cuestionario completado;
4. observaciones registradas;
5. recomendaciones documentadas;
6. decisión sobre el tratamiento de las recomendaciones.

Resultado:

| Criterio | Evidencia | Estado |
|---|---|---|
| Al menos 2 especialistas | 4 participantes | Cumplido |
| Evaluación del prototipo | Formulario de validación comercial | Cumplido |
| Respuestas cuantitativas | 4 respuestas completas Q04–Q28 | Cumplido |
| Evidencia cualitativa | Respuestas abiertas de E1, E2 y E4; E3 sin respuestas abiertas | Cumplido con observación |
| Recomendaciones documentadas | R01–R10 | Cumplido |
| Tratamiento de recomendaciones | Backlog de evolución, sin modificar v10 | Cumplido |

Por tanto:

**B36 — COMPLETADO**

---

## 27. Resultado final de B36

**Estado actual:** COMPLETADO

**Número mínimo de especialistas requerido:** 2

**Número de participantes validados:** 4

**Promedio global Q04–Q28:** 4,82 / 5

**Experiencia general promedio:** 5,00 / 5

**Utilidad para prospección:** 4,75 / 5

**Considera suficiente la información para decidir una revisión adicional:** 100 %

**Revisaría con mayor profundidad una empresa prioritaria:** 100 %

**Recomendaría utilizar la herramienta:** 100 %

**Resultado consolidado:** FAVORABLE

**Decisión final:** Prospect Finder BVQ cumple el objetivo de disponer de un prototipo funcional cuya utilidad, comprensión y aplicabilidad comercial han sido validadas por un grupo de especialistas. Las recomendaciones obtenidas se registran como oportunidades de evolución y no requieren modificar retrospectivamente el modelo v10.

---

## 28. Evidencia conservada

Para trazabilidad académica se recomienda conservar:

- este documento;
- exportación CSV del formulario;
- formulario utilizado;
- fechas de las respuestas;
- identificación funcional de los participantes;
- resultados cuantitativos;
- observaciones cualitativas;
- recomendaciones;
- capturas del prototipo cuando formen parte del informe de defensa.

La evidencia debe conservarse respetando las políticas internas de tratamiento de información y evitando recopilar datos personales innecesarios.

---

## 29. Relación con el modelo

La validación con especialistas no altera el resultado predictivo.

El modelo permanece:

`v10_hgb_financial_c3`

La validación se encuentra aguas abajo del modelo:

`Modelo → Priorización → Explicación → Especialista → Decisión`

La evidencia obtenida refuerza el propósito de Prospect Finder BVQ como sistema de apoyo y no como mecanismo de decisión automatizada.

---

## 30. Conclusión

La validación comercial fue completada con cuatro participantes, superando el mínimo de dos especialistas previsto para B36.

El resultado cuantitativo global fue:

**4,82 / 5**

La experiencia general obtuvo:

**5,00 / 5**

y la utilidad para apoyar la prospección comercial:

**4,75 / 5**

Todos los participantes indicaron que la información disponible permite decidir si una empresa merece una revisión comercial adicional, y todos revisarían con mayor profundidad una empresa ubicada en las primeras posiciones.

Las respuestas cualitativas muestran especial valoración por:

- ranking;
- información financiera;
- comparables históricos;
- explicación de prioridad;
- capacidad de focalizar la gestión comercial.

Las principales recomendaciones se orientan a enriquecer la solución con:

- liquidez;
- datos de contacto;
- información histórica de emisiones;
- segmentación adicional;
- notas;
- funciones tipo CRM;
- indicadores de comparables;
- simulaciones financieras.

Estas mejoras corresponden a la evolución futura del producto y no modifican la integridad metodológica de v10.

Con esta evidencia:

**la actividad B36 queda formalmente cerrada como COMPLETADA.**
