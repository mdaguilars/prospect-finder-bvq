# Matriz de pruebas funcionales finales — Prospect Finder BVQ

## 1. Propósito

Este documento registra las pruebas funcionales finales del prototipo Prospect Finder BVQ.

El objetivo es verificar que los principales flujos de usuario funcionen correctamente antes de la posterior validación con especialistas de la Bolsa de Valores Quito.

Estas pruebas corresponden al funcionamiento del producto.

No sustituyen:

- las pruebas automáticas del backend;
- las pruebas automatizadas del frontend;
- la evaluación del modelo;
- la validación con especialistas BVQ.

---

## 2. Alcance

Las pruebas cubren el flujo:

`PostgreSQL → FastAPI → React → usuario`

y, para explicabilidad:

`modelo v10 congelado → SHAP → FastAPI → React → usuario`

Se validan principalmente:

- carga del ranking;
- búsqueda;
- filtros;
- paginación;
- ficha empresarial;
- indicadores financieros;
- Índice de Afinidad Bursátil;
- comparables históricos;
- explicación SHAP;
- manejo de casos sin información suficiente;
- manejo de expedientes inexistentes.

---

## 3. Entorno de prueba

### Backend

FastAPI: `0.142.2`

Dirección local: `http://127.0.0.1:8000`

### Frontend

React: `19.3.0`

Vite: `8.3.2`

Dirección local: `http://localhost:5173/`

### Base de datos

PostgreSQL: `17-alpine`

Base: `prospect_finder_bvq`

### Modelo

Modelo: `v10_hgb_financial_c3`

Configuración: `C3_CONSERVATIVE`

Estado: **CONGELADO**

### Fecha operacional

`2024-05-01`

### Universo esperado

`137.156 empresas`

---

## 4. Prerrequisitos

Antes de ejecutar las pruebas se verificó que:

1. PostgreSQL se encontrara activo y saludable.
2. FastAPI se encontrara activo.
3. El frontend se encontrara activo.
4. La API pudiera consultar PostgreSQL.
5. El navegador pudiera acceder al frontend.
6. El modelo v10 congelado estuviera disponible para explicabilidad.
7. No se modificaran el modelo ni sus hiperparámetros durante estas pruebas.

Durante el inicio de FastAPI también se observó en el log:

`Inicializando explicabilidad SHAP...`

`Precalentando SHAP con expediente 1...`

`SHAP inicializado correctamente.`

Esto confirma que el entorno utilizado para las pruebas funcionales ejecutó el precalentamiento de SHAP al iniciar la aplicación.

---

## 5. Criterios de resultado

Cada prueba puede registrar uno de los siguientes estados:

- **APROBADA**
- **NO APROBADA**
- **BLOQUEADA**
- **PENDIENTE**

Una prueba se considera aprobada cuando el resultado obtenido coincide con el comportamiento esperado y no se identifican errores funcionales que impidan completar el flujo.

---

# 6. Matriz de pruebas

## PF-01 — Carga inicial del ranking

**Objetivo:** Verificar que la pantalla principal cargue correctamente el universo operacional.

**Resultado obtenido:**

La pantalla cargó correctamente y mostró:

- universo prospectable: `137.156`;
- mayor afinidad visible: `0.974`;
- provincias: `24`;
- tipos de compañía: `9`;
- fecha de decisión: `01 mayo 2024`;
- ranking visible desde la posición `#1`.

**Estado:** **APROBADA**

**Observaciones:** Sin incidencias.

---

## PF-02 — Búsqueda de empresa

**Objetivo:** Verificar la búsqueda por empresa, RUC o expediente.

**Resultado obtenido:**

Se buscó `EMPRESA PRUEBA A`.

La interfaz devolvió un único resultado correspondiente a `EMPRESA PRUEBA A S.A.` y mantuvo sus datos de ranking, provincia, tipo de compañía, afinidad y similitud.

**Estado:** **APROBADA**

**Observaciones:** El indicador de universo se actualizó a `1`, consistente con el resultado filtrado.

---

## PF-03 — Filtro por provincia

**Objetivo:** Verificar que el filtro geográfico limite correctamente el ranking.

**Resultado obtenido:**

Se seleccionó `PICHINCHA`.

La interfaz mostró `43.487 resultados`.

Las empresas visibles correspondieron a Pichincha y conservaron su posición original en el ranking.

**Estado:** **APROBADA**

**Observaciones:** El conteo coincide con el catálogo operacional esperado.

---

## PF-04 — Filtro por tipo de compañía

**Objetivo:** Verificar el filtro por tipo societario.

**Resultado obtenido:**

Se seleccionó `RESPONSABILIDAD LIMITADA`.

La interfaz mostró `28.972 resultados`.

Las empresas visibles correspondieron al tipo seleccionado y conservaron su ranking original.

**Estado:** **APROBADA**

**Observaciones:** El conteo coincide con el catálogo operacional esperado.

---

## PF-05 — Paginación

**Objetivo:** Verificar la navegación entre páginas del ranking.

**Resultado obtenido:**

La navegación avanzó correctamente a `Página 2 de 5.487`.

Se observaron registros desde el ranking `#26` y, al final de la página, hasta `#50`.

Las flechas de navegación anterior y siguiente permanecieron disponibles.

**Estado:** **APROBADA**

**Observaciones:** El ranking conserva numeración global y no se renumera por página.

---

## PF-06 — Ficha empresarial

**Objetivo:** Verificar la apertura del detalle de una empresa.

**Resultado obtenido:**

Se abrió `EMPRESA PRUEBA A S.A.`.

La ficha mostró:

- ranking: `#1`;
- Índice de Afinidad Bursátil: `0.974`;
- percentil: `100,0 %`;
- activos: `USD 143,9 M`;
- patrimonio: `USD 14,2 M`;
- ventas: `USD 47,6 M`;
- empleados: `38`;
- cinco emisores comparables.

**Estado:** **APROBADA**

**Observaciones:** La ficha se abrió sin errores y mantuvo visible la información principal esperada.

---

## PF-07 — Explicabilidad SHAP

**Objetivo:** Verificar que pueda solicitarse una explicación individual del score.

**Resultado obtenido:**

Se verificó la generación de explicación para `EMPRESA PRUEBA A S.A.`.

Posteriormente se seleccionó `EMPRESA PRUEBA B S.A.`, RUC `[RUC ANONIMIZADO]`, ranking `#16.302`.

La interfaz mostró factores en ambas direcciones.

Ejemplos que aumentan afinidad:

- Activos;
- Patrimonio del año anterior;
- Patrimonio.

Ejemplos que reducen afinidad:

- Ingresos por ventas;
- Crecimiento de patrimonio;
- Crecimiento de activos.

**Estado:** **APROBADA**

**Observaciones:** La interfaz diferencia visualmente factores positivos y negativos. SHAP se utiliza como explicación del comportamiento del modelo y no como evidencia causal.

---

## PF-08 — Emisores históricos comparables

**Objetivo:** Verificar la presentación de comparables financieros.

**Resultado obtenido:**

Para `EMPRESA PRUEBA B S.A.` se visualizaron cinco comparables:

1. `HOTEL CASAGANGOTENA S.A.` — `91,5 %`;
2. `BOLSA DE VALORES DE QUITO BVQ SOCIEDAD ANONIMA` — `90,8 %`;
3. `ABSORPELSA PAPELES ABSORVENTES S.A.` — `89,2 %`;
4. `LOGISTICA EMPRESARIAL, LEMPRESA S.A.` — `88,6 %`;
5. `GRUPO GRANDES-ROMAN S.A.` — `88,6 %`.

**Estado:** **APROBADA**

**Observaciones:** La similitud se presenta como información independiente del Índice de Afinidad Bursátil.

---

## PF-09 — Empresa sin similitud suficiente

**Objetivo:** Verificar el comportamiento cuando no existen datos suficientes para calcular comparables.

**Resultado obtenido:**

Mediante la API se identificó `EXPORTQUILSA & PRODUCTORES ASOCIADOS S.A.`, RUC `992708093001`, ranking `#21`, con estado de similitud `INFORMACION_INSUFICIENTE`.

La interfaz mantuvo la ficha disponible y mostró:

`No existen comparables históricos suficientes para esta empresa.`

**Estado:** **APROBADA**

**Observaciones:** No se generaron comparables artificiales. La ausencia de empleados se mostró mediante un guion y el resto de la información permaneció disponible.

---

## PF-10 — Expediente inexistente

**Objetivo:** Verificar el manejo de una empresa inexistente.

**Resultado obtenido:**

Se consultó:

`GET /api/prospects/999999999999`

La API respondió:

`404`

con el mensaje:

`{"detail":"No se encontró una empresa con el expediente solicitado."}`

**Estado:** **APROBADA**

**Observaciones:** El error se encuentra controlado y no expone información de otra empresa.

---

# 7. Resumen de ejecución

| Prueba | Descripción | Estado |
|---|---|---|
| PF-01 | Carga inicial del ranking | APROBADA |
| PF-02 | Búsqueda de empresa | APROBADA |
| PF-03 | Filtro por provincia | APROBADA |
| PF-04 | Filtro por tipo de compañía | APROBADA |
| PF-05 | Paginación | APROBADA |
| PF-06 | Ficha empresarial | APROBADA |
| PF-07 | Explicabilidad SHAP | APROBADA |
| PF-08 | Emisores comparables | APROBADA |
| PF-09 | Empresa sin similitud suficiente | APROBADA |
| PF-10 | Expediente inexistente | APROBADA |

---

# 8. Resultado general

Estado final:

**10 DE 10 PRUEBAS FUNCIONALES APROBADAS**

Durante la ejecución no se identificaron errores bloqueantes en los principales flujos evaluados.

Se verificó de forma funcional:

- carga del universo operacional;
- búsqueda;
- filtros;
- paginación;
- ficha empresarial;
- indicadores financieros;
- ranking y percentil;
- Índice de Afinidad Bursátil;
- explicación SHAP;
- factores que aumentan y reducen afinidad;
- emisores históricos comparables;
- manejo de empresas sin comparables suficientes;
- manejo controlado de expedientes inexistentes.

Estas pruebas complementan las suites automáticas existentes:

- backend: `12 passed`;
- frontend: `4 passed`.

La validación funcional aquí documentada corresponde al control técnico del producto.

No sustituye la validación real con especialistas de la BVQ.

Dicha validación fue ejecutada posteriormente mediante la actividad B36 y se encuentra documentada en:

`docs/v10_specialist_validation.md`

---

# 9. Cierre de B37

B37 — Pruebas funcionales finales puede marcarse como:

**COMPLETADO**

porque:

1. los principales flujos fueron ejecutados;
2. los resultados quedaron documentados;
3. no se identificaron incidencias críticas pendientes;
4. el producto permitió completar los escenarios principales sin errores bloqueantes.

La aprobación técnica de B37 no sustituye B36 — Validación con especialistas de la BVQ.

B36 fue completada posteriormente con cuatro participantes, superando el mínimo previsto para el proyecto.

---

# 10. Relación con la validación de especialistas

Después de completar las pruebas funcionales B37 se ejecutó:

**B36 — Validación con especialistas de la BVQ**

La validación contó con:

- 4 participantes;
- perfiles comerciales, financieros y contables;
- 25 afirmaciones principales valoradas en escala de 1 a 5;
- preguntas de decisión y utilidad;
- retroalimentación cualitativa;
- recomendaciones de evolución.

Resultados consolidados de B36:

| Indicador | Resultado |
|---|---:|
| Participantes | 4 |
| Promedio global Q04–Q28 | 4,82 / 5 |
| Experiencia general | 5,00 / 5 |
| Utilidad para prospección | 4,75 / 5 |
| Información suficiente para decidir una revisión adicional | 100 % |
| Revisaría con mayor profundidad una empresa prioritaria | 100 % |
| Recomendaría utilizar la herramienta | 100 % |

Por tanto, la secuencia de cierre queda:

`B37 — Pruebas funcionales finales → COMPLETADO`

`B36 — Validación con especialistas → COMPLETADO`

La evidencia completa de B36 se encuentra en:

`docs/v10_specialist_validation.md`

Las recomendaciones obtenidas durante la validación con especialistas se consideran oportunidades de evolución del producto y no modifican retrospectivamente:

- el modelo v10;
- el Feature Set;
- el target;
- los hiperparámetros;
- el split temporal;
- los resultados TEST;
- el ranking operacional.

Con esto, las pruebas funcionales finales y la validación con especialistas quedan documentadas como actividades complementarias y completadas.
