export interface ProspectFilters {
  page?: number
  page_size?: number
  search?: string
  provincia?: string
  tipo_compania?: string
  min_score?: number
  min_similitud?: number
  comparables_disponibles?: boolean
}


export interface ProspectQuality {
  n_features_disponibles: number
  pct_features_disponibles: number
}


export interface ProspectSimilaritySummary {
  comparables_disponibles: boolean
  similitud_top1: number | null
  similitud_top5_promedio: number | null
  estado?: string | null
}


export interface ProspectListItem {
  expediente_key: number
  ruc: string | null
  nombre: string | null
  anio: number
  fecha_decision: string
  tipo_compania: string | null
  provincia: string | null
  ranking: number
  score_afinidad: number
  percentil_ranking: number
  calidad_datos: ProspectQuality
  similitud_emisores: ProspectSimilaritySummary
}


export interface ProspectListMetadata {
  page: number
  page_size: number
  total_records: number
  total_pages: number
  sort: string
  score_note?: string
  similarity_note?: string
}


export interface ProspectListResponse {
  metadata: ProspectListMetadata
  items: ProspectListItem[]
}


export interface ProspectCompany {
  expediente_key: number
  ruc: string | null
  nombre: string | null
  anio: number
  fecha_decision: string
  tipo_compania: string | null
  provincia: string | null
}


export interface ProspectPrioritization {
  ranking: number
  score_afinidad: number
  percentil_ranking: number
  nota?: string
}


export interface ProspectFinancialIndicators {
  activos: number | null
  patrimonio: number | null
  ingresos_ventas: number | null
  numero_empleados: number | null

  ratio_patrimonio_activos: number | null
  roa: number | null
  margen_neto: number | null
  rotacion_activos: number | null
  roe: number | null

  crecimiento_activos: number | null
  crecimiento_patrimonio: number | null
  crecimiento_ventas: number | null
  crecimiento_empleados: number | null
}


/*
 * Perfil financiero histórico del emisor utilizado
 * por el motor de similitud.
 *
 * Estas son las siete variables originales utilizadas
 * para construir la similitud.
 */
export interface IssuerReferenceFinancialProfile {
  activos: number | null
  patrimonio: number | null
  ingresos_ventas: number | null
  numero_empleados: number | null
  ratio_patrimonio_activos: number | null
  roa: number | null
  rotacion_activos: number | null
}


/*
 * Percentiles anuales utilizados por el motor de
 * similitud para calcular la distancia entre perfiles.
 */
export interface IssuerReferencePercentiles {
  activos: number | null
  patrimonio: number | null
  ingresos_ventas: number | null
  numero_empleados: number | null
  ratio_patrimonio_activos: number | null
  roa: number | null
  rotacion_activos: number | null
}


export interface ComparableIssuer {
  expediente_key: number
  ruc: string | null
  nombre: string | null

  anio_perfil: number
  fecha_decision_perfil: string
  fecha_primera_inscripcion: string

  tipo_compania: string | null
  provincia: string | null

  /*
   * Estos tres campos fueron incorporados posteriormente
   * al endpoint de detalle.
   *
   * Se mantienen opcionales para:
   *
   * - compatibilidad con mocks anteriores;
   * - compatibilidad con pruebas existentes;
   * - tolerancia ante respuestas almacenadas/caché antiguas;
   * - evolución progresiva del contrato API.
   */

  perfil_disponible?: boolean

  perfil_financiero?:
    | IssuerReferenceFinancialProfile
    | null

  percentiles_similitud?:
    | IssuerReferencePercentiles
    | null
}


export interface ProspectComparable {
  orden: number
  similitud: number
  distancia_percentiles: number
  mismo_tipo_compania: boolean
  emisor: ComparableIssuer
}


export interface ProspectSimilarityDetail {
  comparables_disponibles: boolean

  similitud_top1: number | null
  similitud_top5_promedio: number | null

  distancia_top1: number | null

  n_emisores_comparados: number | null

  estado: string | null

  metodologia: string | null

  nota?: string

  variables_comparacion?: string[]

  comparables: ProspectComparable[]
}


export interface ProspectModelInfo {
  nombre: string | null
  configuracion: string | null
}


export interface ProspectDetailResponse {
  empresa: ProspectCompany

  priorizacion: ProspectPrioritization

  calidad_datos: ProspectQuality

  indicadores_financieros:
    ProspectFinancialIndicators

  similitud_emisores:
    ProspectSimilarityDetail

  modelo: ProspectModelInfo
}