# Inventario de fuentes de datos

## Objetivo

Este documento registra las fuentes de información utilizadas en el proyecto Prospect Finder BVQ, con el propósito de mantener trazabilidad sobre su origen, estructura, período disponible y función dentro del pipeline de datos.

## Fuentes disponibles

| ID | Fuente | Archivo / objeto | Formato | Período | Identificador principal | Uso previsto | Estado |
|---|---|---|---|---|---|---|---|
| F01 | DWH BVQ | V_BALANCE_LINEAS_RESUMEN | CSV | 2022-2025 | RUC | Variables de balance: activos, pasivos y patrimonio | Revisada |
| F02 | DWH BVQ | V_RESULTADOS_LINEAS_RESUMEN | CSV | 2022-2025 | RUC | Variables de resultados: ingresos, costos, gastos y utilidades | Revisada |
| F03 | SCVS - Mercado de Valores | listado_entes_65001 | XLSX | Histórico hasta 2026 | IDENTIFICACIÓN | Identificación de emisores y fecha de inscripción | Disponible |
| F04 | SCVS - Mercado de Valores | codigos_fichas_registrales | XLSX | Histórico | IDENTIFICACIÓN | Validación y complemento del histórico registral | Disponible |
| F05 | SCVS - Mercado de Valores | hechos_relevantes | XLSX | Histórico | NO. INSCRIPCIÓN / NOMBRE | Fuente complementaria de eventos del mercado | Disponible |
| F06 | BVQ | emisores_emisiones | XLSX | Por analizar | Por verificar | Validación del histórico de emisores y emisiones | Disponible |

## Fuente F01 - V_BALANCE_LINEAS_RESUMEN

La vista contiene información financiera resumida por empresa, año, grupo y línea contable.

Campos identificados:

- FECHA
- ANIO
- EXPEDIENTE
- RUC
- EMISOR
- RAMA_ACTIVIDAD
- DESCRIPCION_RAMA
- CIIU
- GRUPO
- LINEA
- ORDEN
- VALOR
- VERTICAL_PCT
- VALOR_ANTERIOR
- VAR_ABS
- VAR_PCT

Los grupos identificados son:

- ACTIVO
- PASIVO
- PATRIMONIO

La unidad de registro corresponde a una línea financiera de una empresa en un período determinado.

## Fuente F02 - V_RESULTADOS_LINEAS_RESUMEN

La vista mantiene la misma estructura técnica que la fuente de balances y contiene información del estado de resultados.

El grupo identificado es:

- RESULTADOS

Entre las líneas disponibles se encuentran:

- Ingreso por Actividad
- Costo de Ventas
- Gastos Administrativos
- Gastos Financieros
- Gastos de Venta
- Utilidad Bruta
- Utilidad Operativa
- Utilidad Neta
- Impuestos
- Participación Trabajadores
- Amortizaciones
- Depreciaciones

## Fuentes SCVS - Mercado de Valores

Las fuentes descargadas desde la Superintendencia de Compañías, Valores y Seguros se almacenan sin modificaciones en:

`data/raw/scvs/mercado_valores/`

Los archivos originales son:

- `listado_entes_65001_1789908466941.xlsx`
- `codigos_fichas_registrales_1789908530079.xlsx`
- `hechos_relevantes_1789908501354.xlsx`

Estas fuentes serán utilizadas principalmente para identificar emisores, fechas de inscripción y antecedentes registrales.

## Reglas de almacenamiento

Los archivos originales se conservan en `data/raw` y no serán modificados.

Los datos originales no se almacenan en GitHub. El archivo `.gitignore` excluye el contenido de `data/raw` del control de versiones.

Las transformaciones posteriores se almacenarán en:

- `data/interim`: resultados intermedios.
- `data/processed`: datasets preparados para análisis y modelado.

## Estado

Inventario actualizado con las fuentes disponibles al inicio de la construcción del prototipo.